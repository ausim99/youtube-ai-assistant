"""Service layer - orchestrates agents and database operations."""

import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from agents.idea_agent import IdeaAgent
from agents.script_agent import ScriptAgent
from agents.seo_agent import SEOAgent
from agents.voice_agent import VoiceAgent
from agents.image_agent import ImageAgent
from agents.thumbnail_agent import ThumbnailAgent
from agents.video_agent import VideoAgent
from agents.upload_agent import UploadAgent
from agents.telegram_agent import TelegramAgent
from database.models.models import ContentIdea, GeneratedVideo, TaskLog, VideoScript, YouTubeUpload
from utils.logger import get_logger

logger = get_logger()


class AgentService:
    """Orchestrates all agents and manages the content pipeline."""

    def __init__(self, db: Optional[AsyncSession] = None):
        self.db = db

    async def generate_ideas(self, category: str = "ai-tools", count: int = 5) -> list[dict]:
        agent = IdeaAgent()
        ideas = await agent.execute(category=category, count=count)
        saved = []

        if self.db:
            for idea in ideas:
                db_idea = ContentIdea(
                    id=str(uuid.uuid4()),
                    title_bn=idea.get("title_bn", idea.get("title", "")),
                    title_en=idea.get("title_en", ""),
                    category=idea.get("category", category),
                    hook=idea.get("hook", ""),
                    unique_angle=idea.get("unique_angle", ""),
                    target_audience=idea.get("target_audience", ""),
                    difficulty=idea.get("difficulty", "medium"),
                    expected_ctr=idea.get("expected_ctr", 50.0),
                    expected_rpm=idea.get("expected_rpm", 2.0),
                    expected_views=idea.get("expected_views", 1000),
                    trend_score=idea.get("trend_score", 0.5),
                    status="generated",
                )
                self.db.add(db_idea)
                saved.append(db_idea)
            await self.db.commit()

        logger.info(f"AgentService: Generated and saved {len(saved)} ideas")
        return ideas

    async def generate_script(self, idea_id: str, duration_seconds: int = 60) -> Optional[dict]:
        duration_seconds = min(duration_seconds, 60)  # cap at 60s for shorts
        if not self.db:
            return None

        result = await self.db.execute(select(ContentIdea).where(ContentIdea.id == idea_id))
        idea = result.scalar_one_or_none()
        if not idea:
            logger.error(f"AgentService: Idea {idea_id} not found")
            return None

        agent = ScriptAgent()
        script_data = await agent.execute(
            idea_title=idea.title_bn,
            category=idea.category,
            duration_seconds=duration_seconds,
        )

        db_script = VideoScript(
            id=str(uuid.uuid4()),
            idea_id=idea_id,
            title=script_data.get("title", idea.title_bn),
            script_bn=script_data.get("script_bn", ""),
            script_en=script_data.get("script_en", ""),
            hooks=script_data.get("hooks", []),
            duration_seconds=script_data.get("duration_seconds", duration_seconds),
            word_count=script_data.get("word_count", 0),
            scenes=script_data.get("scenes", []),
            status="draft",
        )
        self.db.add(db_script)

        seo_agent = SEOAgent()
        seo_data = await seo_agent.execute(
            title=db_script.title,
            script=db_script.script_bn,
            category=idea.category,
        )
        db_script.seo_data = seo_data
        db_script.title = seo_data.get("titles", [db_script.title])[0] if seo_data.get("titles") else db_script.title

        await self.db.commit()
        logger.info(f"AgentService: Generated script {db_script.id}")
        return {"id": db_script.id, "title": db_script.title, "script_bn": db_script.script_bn}

    async def generate_video(self, script_id: str, resolution: str = "1080x1920", add_music: bool = False) -> Optional[dict]:
        if not self.db:
            return None

        result = await self.db.execute(select(VideoScript).where(VideoScript.id == script_id))
        script = result.scalar_one_or_none()
        if not script:
            return None

        video_id = str(uuid.uuid4())
        db_video = GeneratedVideo(
            id=video_id,
            script_id=script_id,
            resolution=resolution,
            status="processing",
        )
        self.db.add(db_video)
        await self.db.commit()

        voice_agent = VoiceAgent()
        voice_result = await voice_agent.execute(
            text=script.script_bn,
            output_path=f"storage/audio/{video_id}.mp3",
        )

        if voice_result.get("success"):
            db_video.voice_path = voice_result["path"]

        image_agent = ImageAgent()
        w, h = (1080, 1920) if resolution == "1080x1920" else (1920, 1080)
        image_result = await image_agent.execute(
            prompt=f"Abstract tech background, AI theme, gradient blue purple, {w}x{h}",
            output_path=f"storage/images/{video_id}_bg.png",
            width=w,
            height=h,
        )
        image_paths = [image_result["path"]] if image_result.get("success") else []

        video_agent = VideoAgent()
        video_result = await video_agent.execute(
            audio_path=voice_result.get("path", ""),
            image_paths=image_paths,
            output_path=f"storage/videos/{video_id}.mp4",
            resolution=resolution,
            add_music=add_music,
        )
        if video_result.get("success"):
            db_video.video_path = video_result["path"]
            db_video.duration_seconds = video_result.get("duration_seconds")
            db_video.file_size_mb = video_result.get("file_size_mb")

        thumbnail_agent = ThumbnailAgent()
        thumb_result = await thumbnail_agent.execute(
            title=script.title,
            thumbnail_text=script.seo_data.get("thumbnail_text", script.title) if script.seo_data else script.title,
            output_path=f"storage/thumbnails/{video_id}.jpg",
        )
        if thumb_result.get("success"):
            db_video.thumbnail_path = thumb_result["path"]

        db_video.status = "completed"
        await self.db.commit()

        telegram = TelegramAgent()
        await telegram.send_notification(
            "Video Generation Complete",
            f"Title: {script.title}\nResolution: {resolution}",
        )

        return {
            "id": db_video.id,
            "video_path": db_video.video_path,
            "thumbnail_path": db_video.thumbnail_path,
            "status": db_video.status,
        }

    async def upload_to_youtube(self, video_id: str, **kwargs) -> Optional[dict]:
        if not self.db:
            return None

        result = await self.db.execute(select(GeneratedVideo).where(GeneratedVideo.id == video_id))
        video = result.scalar_one_or_none()
        if not video:
            return None

        script_result = await self.db.execute(select(VideoScript).where(VideoScript.id == video.script_id))
        script = script_result.scalar_one_or_none()

        seo_data = script.seo_data if script else {}
        tags = seo_data.get("tags", kwargs.get("tags", []))
        hashtags = seo_data.get("hashtags", kwargs.get("hashtags", []))
        description = kwargs.get("description") or seo_data.get("description", script.script_bn[:2000] if script else "")
        if hashtags:
            description += "\n\n" + " ".join(hashtags)

        agent = UploadAgent()
        upload_result = await agent.execute(
            video_path=video.video_path,
            title=kwargs.get("title") or (script.title if script else "AI Bangla"),
            description=description,
            tags=tags,
            thumbnail_path=video.thumbnail_path,
            category_id=kwargs.get("category_id", "28"),
            visibility=kwargs.get("visibility", "private"),
            scheduled_at=kwargs.get("scheduled_at"),
        )

        db_upload = YouTubeUpload(
            id=str(uuid.uuid4()),
            video_id=video_id,
            youtube_video_id=upload_result.get("youtube_video_id"),
            title=kwargs.get("title") or (script.title if script else ""),
            description=description,
            tags=tags,
            hashtags=hashtags,
            visibility=kwargs.get("visibility", "private"),
            scheduled_at=kwargs.get("scheduled_at"),
            published_at=datetime.utcnow() if upload_result.get("success") and kwargs.get("visibility") == "public" else None,
            status="published" if upload_result.get("success") else "failed",
            error_message=upload_result.get("error"),
        )
        self.db.add(db_upload)
        await self.db.commit()

        telegram = TelegramAgent()
        if upload_result.get("success"):
            await telegram.send_video_link(
                db_upload.title or "New Video",
                upload_result["youtube_video_id"],
            )
        else:
            await telegram.send_notification(
                "Upload Failed",
                f"Error: {upload_result.get('error')}",
                is_error=True,
            )

        return {"success": upload_result.get("success"), "youtube_video_id": upload_result.get("youtube_video_id")}

    async def run_full_pipeline(self, category: str = "ai-tools", resolution: str = "1080x1920", visibility: str = "private") -> dict:
        logger.info(f"AgentService: Starting full pipeline for {category}")
        results = {}

        print("[PIPELINE] Step 2/7: Generating content ideas...", flush=True)
        ideas = await self.generate_ideas(category=category, count=1)
        if not ideas:
            return {"success": False, "error": "No ideas generated"}
        results["ideas"] = len(ideas)
        print(f"[PIPELINE] Step 2/7: Done - {len(ideas)} idea(s)", flush=True)

        idea_id = ideas[0].id if hasattr(ideas[0], "id") else ""
        print("[PIPELINE] Step 3/7: Writing Bangla script...", flush=True)
        script = await self.generate_script(idea_id, duration_seconds=min(60, int(settings.VIDEO_DURATION)))
        if not script:
            return {"success": False, "error": "Script generation failed"}
        results["script_id"] = script["id"]
        print(f"[PIPELINE] Step 3/7: Done - Script: {script.get('title', 'N/A')[:60]}", flush=True)

        print("[PIPELINE] Step 4/7: Generating voice + images...", flush=True)
        print("[PIPELINE] Step 5/7: Creating thumbnail...", flush=True)
        print("[PIPELINE] Step 6/7: Assembling video...", flush=True)
        video = await self.generate_video(script["id"], resolution=resolution)
        if not video or video.get("status") != "completed":
            return {"success": False, "error": "Video generation failed", "results": results}
        results["video_id"] = video["id"]
        print(f"[PIPELINE] Step 6/7: Done - Video assembled", flush=True)

        print("[PIPELINE] Step 7/7: Uploading to YouTube...", flush=True)
        upload = await self.upload_to_youtube(video["id"], visibility=visibility)
        results["upload_success"] = upload.get("success", False)
        results["youtube_video_id"] = upload.get("youtube_video_id")
        results["success"] = upload.get("success", False)
        print(f"[PIPELINE] Step 7/7: Done - Upload success: {upload.get('success')}", flush=True)

        logger.info(f"AgentService: Pipeline complete - {results}")
        return results

    async def get_dashboard_stats(self) -> dict:
        if not self.db:
            return {}

        stats = {}
        for model, key in [
            (ContentIdea, "total_ideas"),
            (VideoScript, "total_scripts"),
            (GeneratedVideo, "total_videos"),
            (YouTubeUpload, "total_uploads"),
        ]:
            result = await self.db.execute(select(func.count(model.id)))
            stats[key] = result.scalar() or 0

        result = await self.db.execute(
            select(func.count(YouTubeUpload.id)).where(YouTubeUpload.status == "published")
        )
        stats["published_videos"] = result.scalar() or 0

        result = await self.db.execute(
            select(func.count(YouTubeUpload.id)).where(
                YouTubeUpload.scheduled_at != None,
                YouTubeUpload.status == "pending",
            )
        )
        stats["scheduled_videos"] = result.scalar() or 0

        result = await self.db.execute(
            select(func.count(TaskLog.id)).where(TaskLog.status == "failed")
        )
        stats["failed_tasks"] = result.scalar() or 0

        stats["pipeline_status"] = "ready"
        return stats
