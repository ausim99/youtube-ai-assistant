#!/usr/bin/env python3
"""Pipeline runner for GitHub Actions. Called from the workflow YAML."""

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.agent_service import AgentService
from database.session import async_session
from agents.telegram_agent import TelegramAgent


async def run():
    category = os.getenv("PIPELINE_CATEGORY", "ai-tools")
    resolution = os.getenv("PIPELINE_RESOLUTION", "1080x1920")
    visibility = os.getenv("PIPELINE_VISIBILITY", "private")

    telegram = TelegramAgent()

    try:
        await telegram.send_notification("Pipeline Started", f"Category: {category}\nResolution: {resolution}")

        async with async_session() as db:
            service = AgentService(db)
            results = await service.run_full_pipeline(category, resolution, visibility)

            if results.get("success"):
                await telegram.send_notification(
                    "Pipeline Complete",
                    f"Video ID: {results.get('youtube_video_id', 'N/A')}\nCategory: {category}",
                )
                print(f"SUCCESS: {results}")
            else:
                error_msg = results.get("error", "Unknown error")
                await telegram.send_notification("Pipeline Failed", error_msg, is_error=True)
                print(f"FAILED: {error_msg}")
                sys.exit(1)

    except Exception as e:
        await telegram.send_notification("Pipeline Crashed", str(e), is_error=True)
        print(f"CRASHED: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(run())
