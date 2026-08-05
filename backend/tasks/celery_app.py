"""Celery tasks for async pipeline execution."""

import uuid
from datetime import datetime

from celery import Celery

from core.config.settings import get_settings
from utils.logger import get_logger

settings = get_settings()
logger = get_logger()

celery_app = Celery(
    "youtube_ai",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone=settings.TIMEZONE,
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    task_soft_time_limit=3000,
    worker_max_tasks_per_child=50,
    broker_connection_retry_on_startup=True,
    imports=["tasks.pipeline"],
)

celery_app.conf.beat_schedule = {
    "daily-pipeline": {
        "task": "tasks.pipeline.run_daily_pipeline",
        "schedule": 86400.0,
        "options": {"queue": "youtube_ai"},
    },
}


@celery_app.task(bind=True, name="tasks.pipeline.run_daily_pipeline", queue="youtube_ai")
def run_daily_pipeline(self):
    """Scheduled daily pipeline execution."""
    from services.agent_service import AgentService
    from database.models.models import TaskLog
    from database.session import async_session as session_factory

    import asyncio
    import nest_asyncio

    nest_asyncio.apply()

    task_log = None

    async def _run():
        nonlocal task_log
        async with session_factory() as db:
            service = AgentService(db)
            task_log = TaskLog(
                id=str(uuid.uuid4()),
                task_id=self.request.id,
                task_name="daily_pipeline",
                status="running",
                progress=0,
                message="Starting daily pipeline",
            )
            db.add(task_log)
            await db.commit()

            results = await service.run_full_pipeline(
                category=settings.DEFAULT_CATEGORY,
                resolution="1080x1920" if settings.SHORTS_ENABLED else "1920x1080",
            )

            task_log.status = "completed" if results.get("success") else "failed"
            task_log.progress = 100
            task_log.message = str(results)
            task_log.completed_at = datetime.utcnow()
            await db.commit()

            return results

    return asyncio.run(_run())


@celery_app.task(bind=True, name="tasks.pipeline.run_custom_pipeline", queue="youtube_ai")
def run_custom_pipeline(self, category: str = "ai-tools", resolution: str = "1080x1920", visibility: str = "private"):
    """Manual pipeline execution with custom parameters."""
    from services.agent_service import AgentService
    from database.models.models import TaskLog
    from database.session import async_session as session_factory

    import asyncio
    import nest_asyncio

    nest_asyncio.apply()

    async def _run():
        async with session_factory() as db:
            service = AgentService(db)
            task_log = TaskLog(
                id=str(uuid.uuid4()),
                task_id=self.request.id,
                task_name="custom_pipeline",
                status="running",
                progress=0,
                message=f"Running pipeline: {category}",
            )
            db.add(task_log)
            await db.commit()

            results = await service.run_full_pipeline(category, resolution, visibility)

            task_log.status = "completed" if results.get("success") else "failed"
            task_log.progress = 100
            task_log.message = str(results)
            task_log.completed_at = datetime.utcnow()
            await db.commit()

            return results

    return asyncio.run(_run())
