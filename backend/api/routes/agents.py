"""Agent API routes - trigger agents, run pipeline."""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import (
    ContentIdeaCreate,
    ContentIdeaResponse,
    PipelineRequest,
    ScriptCreate,
    ScriptResponse,
    VideoGenerateRequest,
    VideoResponse,
    YouTubeUploadRequest,
    YouTubeUploadResponse,
)
from database.models.models import ContentIdea, GeneratedVideo, VideoScript, YouTubeUpload
from database.session import get_db
from services.agent_service import AgentService
from utils.logger import get_logger

router = APIRouter()
logger = get_logger()


def get_service(db: AsyncSession = Depends(get_db)) -> AgentService:
    return AgentService(db)


@router.post("/ideas", response_model=list[ContentIdeaResponse])
async def generate_ideas(request: ContentIdeaCreate, service: AgentService = Depends(get_service)):
    ideas = await service.generate_ideas(category=request.category, count=request.count)
    return ideas


@router.get("/ideas", response_model=list[ContentIdeaResponse])
async def list_ideas(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ContentIdea).order_by(ContentIdea.created_at.desc()).limit(50))
    return result.scalars().all()


@router.get("/ideas/{idea_id}", response_model=ContentIdeaResponse)
async def get_idea(idea_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ContentIdea).where(ContentIdea.id == idea_id))
    idea = result.scalar_one_or_none()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    return idea


@router.post("/scripts", response_model=ScriptResponse)
async def generate_script(request: ScriptCreate, service: AgentService = Depends(get_service)):
    result = await service.generate_script(idea_id=request.idea_id, duration_seconds=request.duration_seconds)
    if not result:
        raise HTTPException(status_code=400, detail="Script generation failed")
    return result


@router.get("/scripts", response_model=list[ScriptResponse])
async def list_scripts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(VideoScript).order_by(VideoScript.created_at.desc()).limit(50))
    return result.scalars().all()


@router.get("/scripts/{script_id}", response_model=ScriptResponse)
async def get_script(script_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(VideoScript).where(VideoScript.id == script_id))
    script = result.scalar_one_or_none()
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    return script


@router.post("/videos", response_model=VideoResponse)
async def generate_video(request: VideoGenerateRequest, service: AgentService = Depends(get_service)):
    result = await service.generate_video(
        script_id=request.script_id,
        resolution=request.resolution,
        add_music=request.add_music,
    )
    if not result:
        raise HTTPException(status_code=400, detail="Video generation failed")
    return result


@router.get("/videos", response_model=list[VideoResponse])
async def list_videos(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(GeneratedVideo).order_by(GeneratedVideo.created_at.desc()).limit(50))
    return result.scalars().all()


@router.get("/videos/{video_id}", response_model=VideoResponse)
async def get_video(video_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(GeneratedVideo).where(GeneratedVideo.id == video_id))
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video


@router.post("/uploads", response_model=YouTubeUploadResponse)
async def upload_video(request: YouTubeUploadRequest, service: AgentService = Depends(get_service)):
    result = await service.upload_to_youtube(**request.model_dump())
    if not result or not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Upload failed") if result else "Upload failed")
    return result


@router.get("/uploads", response_model=list[YouTubeUploadResponse])
async def list_uploads(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(YouTubeUpload).order_by(YouTubeUpload.created_at.desc()).limit(50))
    return result.scalars().all()


@router.post("/pipeline")
async def run_pipeline(
    request: PipelineRequest,
    background_tasks: BackgroundTasks,
    service: AgentService = Depends(get_service),
):
    background_tasks.add_task(
        service.run_full_pipeline,
        category=request.category or "ai-tools",
        resolution=request.resolution or "1080x1920",
        visibility=request.visibility or "private",
    )
    return {"status": "started", "message": "Pipeline running in background"}
