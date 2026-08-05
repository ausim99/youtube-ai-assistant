"""Telegram Agent - Bot that serves as the AI assistant interface via Telegram."""

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
        payload = {
            "chat_id": self.chat_id,
            "text": text[:4096],
            "parse_mode": parse_mode,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as resp:
                    return await resp.json()
        except Exception as e:
            logger.error(f"Telegram send failed: {e}")
            return None

    async def send_notification(self, title: str, message: str, is_error: bool = False):
        emoji = "❌" if is_error else "✅"
        text = f"{emoji} <b>{title}</b>\n\n{message}\n\n<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
        return await self._send_message(text)

    async def send_progress(self, step: str, progress: int, details: str = ""):
        bar_length = 10
        filled = int(bar_length * progress / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        text = (
            f"🔄 <b>Pipeline Progress</b>\n\n"
            f"<b>Current Step:</b> {step}\n"
            f"<b>Progress:</b> [{bar}] {progress}%\n"
            f"{details}"
        )
        return await self._send_message(text)

    async def send_video_link(self, title: str, video_id: str, thumbnail_url: str = ""):
        url = f"https://youtube.com/watch?v={video_id}"
        text = (
            f"🎬 <b>New Video Published!</b>\n\n"
            f"<b>Title:</b> {title}\n"
            f"<b>Link:</b> {url}\n\n"
            f"#YouTubeAI #BanglaTech"
        )
        return await self._send_message(text)

    async def send_daily_report(self, stats: dict):
        text = (
            f"📊 <b>Daily Report</b>\n"
            f"{'─' * 30}\n"
            f"📝 Ideas: {stats.get('total_ideas', 0)}\n"
            f"📜 Scripts: {stats.get('total_scripts', 0)}\n"
            f"🎥 Videos: {stats.get('total_videos', 0)}\n"
            f"📤 Uploads: {stats.get('total_uploads', 0)}\n"
            f"✅ Published: {stats.get('published_videos', 0)}\n"
            f"⏰ Scheduled: {stats.get('scheduled_videos', 0)}\n"
            f"❌ Failed: {stats.get('failed_tasks', 0)}\n"
        )
        return await self._send_message(text)

    async def handle_telegram_command(self, command: str, args: list[str]) -> str:
        commands = {
            "start": "স্বাগতম! YouTube AI Assistant বটে আপনাকে স্বাগতম।\n/help - সব কমান্ড দেখুন\n/status - বর্তমান স্ট্যাটাস\n/run - পাইপলাইন চালু করুন\n/history - পূর্বের ভিডিও দেখুন",
            "help": "কমান্ডসমূহ:\n/start - শুরু\n/status - স্ট্যাটাস\n/run - পাইপলাইন চালান\n/create - নতুন ভিডিও তৈরি\n/upload - আপলোড\n/publish - পাবলিশ\n/history - ইতিহাস\n/analytics - এনালিটিক্স\n/settings - সেটিংস",
            "status": "✅ সিস্টেম চলমান আছে। সব সার্ভিস OK।\nChannel: AI Bangla\nLanguage: Bengali",
        }

        return commands.get(command.lstrip("/"), f"অজানা কমান্ড: {command}")
