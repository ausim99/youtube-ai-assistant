"""System API routes - health, auth, config."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import TokenResponse, UserCreate, UserLogin
from database.models.models import User
from database.session import get_db
from core.config.settings import get_settings
from utils.logger import get_logger

router = APIRouter()
settings = get_settings()
logger = get_logger()


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "YouTube AI Assistant", "version": "1.0.0"}


@router.get("/config")
async def get_config():
    return {
        "channel_language": settings.CHANNEL_LANGUAGE,
        "channel_name": settings.CHANNEL_NAME,
        "shorts_enabled": settings.SHORTS_ENABLED,
        "long_video_enabled": settings.LONG_VIDEO_ENABLED,
        "ai_provider": settings.DEFAULT_AI_PROVIDER,
        "tts_provider": settings.DEFAULT_TTS_PROVIDER,
    }


@router.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == credentials.username))
    user = result.scalar_one_or_none()
    if not user or credentials.password != "admin":
        return TokenResponse(access_token="demo-token", token_type="bearer")
    return TokenResponse(access_token="demo-token", token_type="bearer")


@router.post("/auth/register")
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=user_data.password,
    )
    db.add(user)
    await db.commit()
    return {"success": True, "message": "User created"}
