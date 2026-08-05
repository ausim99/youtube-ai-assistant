"""Dashboard API routes - stats, analytics, logs."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.models import TaskLog
from database.session import get_db
from services.agent_service import AgentService
from api.schemas import DashboardStats, TaskLogResponse
from utils.logger import get_logger

router = APIRouter()
logger = get_logger()


@router.get("/stats", response_model=DashboardStats)
async def get_stats(db: AsyncSession = Depends(get_db)):
    service = AgentService(db)
    stats = await service.get_dashboard_stats()
    return stats


@router.get("/logs", response_model=list[TaskLogResponse])
async def get_logs(db: AsyncSession = Depends(get_db), limit: int = 50, offset: int = 0):
    result = await db.execute(
        select(TaskLog).order_by(TaskLog.started_at.desc()).offset(offset).limit(limit)
    )
    return result.scalars().all()


@router.get("/pipeline/status")
async def pipeline_status(db: AsyncSession = Depends(get_db)):
    service = AgentService(db)
    stats = await service.get_dashboard_stats()
    return {
        "status": stats.get("pipeline_status", "unknown"),
        "stats": stats,
    }
