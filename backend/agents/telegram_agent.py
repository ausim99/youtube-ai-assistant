"""Telegram Agent - Professional notification formatting."""

import asyncio
from datetime import datetime
from typing import Any

from agents.base import BaseAgent
from core.config.settings import get_settings
from utils.logger import get_logger

settings = get_settings()
logger = get_logger()


class TelegramAgent(BaseAgent):
    """Manages Telegram bot communication and notifications."""

    def __init__(self):
        super().__init__()
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID

    async def execute(self, **kwargs) -> Any:
        pass

    async def _send_message(self, text: str, parse_mode: str = "HTML"):
        import aiohttp
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram not configured")
            return None
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": text[:4096], "parse_mode": parse_mode}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as resp:
                    return await resp.json()
        except Exception as e:
            logger.error(f"Telegram send failed: {e}")
            return None

    async def send_pipeline_start(self, category: str, resolution: str):
        text = (
            f"🎬 <b>Pipeline Started</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🏷️  Category: <b>{category}</b>\n"
            f"📐 Resolution: {resolution}\n"
            f"🕐 {datetime.now().strftime('%H:%M:%S')}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"<i>Generating content...</i>"
        )
        return await self._send_message(text)

    async def send_step(self, step_num: int, total: int, name: str, status: str = "✅"):
        text = (
            f"{status} <b>Step {step_num}/{total}</b>: {name}"
        )
        return await self._send_message(text)

    async def send_idea_generated(self, title: str, category: str):
        text = (
            f"💡 <b>Content Idea Generated</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📝 {title[:100]}\n"
            f"🏷️  {category}\n"
        )
        return await self._send_message(text)

    async def send_script_ready(self, title: str, words: int):
        text = (
            f"📜 <b>Script Ready</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📝 {title[:100]}\n"
            f"📊 {words} words\n"
        )
        return await self._send_message(text)

    async def send_video_complete(self, title: str, resolution: str, duration: int = 60):
        text = (
            f"🎥 <b>Video Generated</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📝 {title[:80]}\n"
            f"📐 {resolution}\n"
            f"⏱️  {duration}s\n"
        )
        return await self._send_message(text)

    async def send_upload_success(self, title: str, video_id: str):
        url = f"https://youtube.com/watch?v={video_id}"
        text = (
            f"📤 <b>Uploaded to YouTube</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📝 {title[:80]}\n"
            f"🔗 <a href='{url}'>Watch Video</a>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📊 <a href='https://dashboard-jade-pi-57.vercel.app'>View Dashboard</a>"
        )
        return await self._send_message(text)

    async def send_upload_failed(self, title: str, error: str):
        text = (
            f"⚠️ <b>Upload Failed</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📝 {title[:80]}\n"
            f"❌ {error[:200]}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"<a href='https://github.com/ausim99/youtube-ai-assistant/actions'>Check Logs</a>"
        )
        return await self._send_message(text)

    async def send_pipeline_complete(self, success: bool, video_id: str = "", category: str = ""):
        if success:
            text = (
                f"✅ <b>Pipeline Complete</b>\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🏷️  {category}\n"
                f"🔗 <a href='https://youtube.com/watch?v={video_id}'>Watch on YouTube</a>\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"📊 <a href='https://dashboard-jade-pi-57.vercel.app'>Dashboard</a>"
            )
        else:
            text = (
                f"⚠️ <b>Pipeline Finished (Issues)</b>\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🏷️  {category}\n"
                f"Video generated but upload had issues.\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"<a href='https://github.com/ausim99/youtube-ai-assistant/actions'>View Logs</a>"
            )
        return await self._send_message(text)

    async def send_error(self, step: str, error: str):
        text = (
            f"❌ <b>Error</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📍 Step: {step}\n"
            f"💬 {error[:300]}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"<a href='https://github.com/ausim99/youtube-ai-assistant/actions'>View Logs</a>"
        )
        return await self._send_message(text)

    # Legacy methods for backward compatibility
    async def send_notification(self, title: str, message: str, is_error: bool = False):
        emoji = "❌" if is_error else "✅"
        text = f"{emoji} <b>{title}</b>\n\n{message}"
        return await self._send_message(text)

    async def send_video_link(self, title: str, video_id: str, thumbnail_url: str = ""):
        return await self.send_upload_success(title, video_id)
