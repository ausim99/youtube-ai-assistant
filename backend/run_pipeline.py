#!/usr/bin/env python3
"""Pipeline runner for GitHub Actions. Prints step-by-step progress to console."""

import asyncio
import os
import sys
import time
import traceback

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def log(step: str, msg: str = ""):
    """Print progress with flush so GitHub Actions shows it immediately."""
    ts = time.strftime("%H:%M:%S")
    line = f"[{ts}] {step}: {msg}" if msg else f"[{ts}] {step}"
    print(line, flush=True)


def check_prerequisites():
    """Check if minimum required API keys are set."""
    keys = {
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", ""),
        "YOUTUBE_CLIENT_ID": os.getenv("YOUTUBE_CLIENT_ID", ""),
        "YOUTUBE_REFRESH_TOKEN": os.getenv("YOUTUBE_REFRESH_TOKEN", ""),
    }
    missing = [k for k, v in keys.items() if not v]
    if missing:
        log("WARNING", f"Missing API keys: {', '.join(missing)}")
        log("WARNING", "Set these in GitHub Secrets for full pipeline functionality")
    return {k: v for k, v in keys.items() if v}


async def send_telegram_alert(text: str):
    """Send Telegram alert using direct HTTP (no imports needed beyond stdlib)."""
    bot = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat = os.getenv("TELEGRAM_CHAT_ID", "")
    if not bot or not chat:
        return
    import urllib.request, json
    try:
        url = f"https://api.telegram.org/bot{bot}/sendMessage"
        data = json.dumps({"chat_id": chat, "text": text[:4096]}).encode()
        req = urllib.request.Request(url, data, {"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"Telegram alert failed: {e}", flush=True)


async def run():
    category = os.getenv("PIPELINE_CATEGORY", "ai-tools")
    resolution = os.getenv("PIPELINE_RESOLUTION", "1080x1920")
    visibility = os.getenv("PIPELINE_VISIBILITY", "private")

    log("START", f"Pipeline: category={category}, resolution={resolution}, visibility={visibility}")
    keys = check_prerequisites()

    if not keys.get("GEMINI_API_KEY"):
        log("SKIP", "No AI API key set. Set GEMINI_API_KEY in GitHub Secrets.")
        log("SKIP", "Pipeline cannot generate content without an AI provider.")
        await send_telegram_alert(
            f"Pipeline skipped - No AI API key configured.\n"
            f"Add GEMINI_API_KEY to GitHub Secrets → Settings → Secrets and variables → Actions"
        )
        return

    await send_telegram_alert(f"Pipeline started: {category} ({resolution})")

    log("STEP 1/8", "Generating content ideas...")
    try:
        from services.agent_service import AgentService
        from database.session import async_session

        async with async_session() as db:
            service = AgentService(db)

            log("STEP 2/8", "Writing script...")
            results = await service.run_full_pipeline(category, resolution, visibility)

            if results.get("success"):
                vid = results.get("youtube_video_id", "N/A")
                log("DONE", f"Pipeline complete! Video ID: {vid}")
                await send_telegram_alert(f"Pipeline complete!\nVideo ID: {vid}\nCategory: {category}")
            else:
                err = results.get("error", "Unknown")
                log("FAIL", err)
                await send_telegram_alert(f"Pipeline failed: {err}")
                sys.exit(1)

    except Exception as e:
        log("CRASH", str(e))
        traceback.print_exc()
        await send_telegram_alert(f"Pipeline crashed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(run())
