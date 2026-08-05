"""Celery task definitions for the pipeline.

Imported by Celery beat for scheduled execution.
"""

from tasks.celery_app import run_custom_pipeline, run_daily_pipeline

__all__ = ["run_daily_pipeline", "run_custom_pipeline"]
