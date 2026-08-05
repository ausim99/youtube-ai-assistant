#!/usr/bin/env python3
"""Telegram Bot - Listens for commands and controls the AI pipeline."""

import asyncio
import os
import sys
import uuid
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import nest_asyncio
nest_asyncio.apply()

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from core.config.settings import get_settings
from services.agent_service import AgentService
from database.session import async_session
from utils.logger import get_logger

settings = get_settings()
logger = get_logger()

BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
ALLOWED_CHAT_ID = settings.TELEGRAM_CHAT_ID


async def is_authorized(update: Update) -> bool:
    chat_id = str(update.effective_chat.id)
    if ALLOWED_CHAT_ID and chat_id != ALLOWED_CHAT_ID:
        await update.message.reply_text("⛔ Unauthorized")
        return False
    return True


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 <b>YouTube AI Assistant বট</b>\n\n"
        "স্বাগতম! এই বট দিয়ে আপনি AI কন্টেন্ট তৈরি করতে পারবেন।\n\n"
        "কমান্ড:\n"
        "/run - ফুল পাইপলাইন চালান\n"
        "/create - নতুন আইডিয়া জেনারেট\n"
        "/status - স্ট্যাটাস দেখুন\n"
        "/history - শেষ ৫টি কাজ\n"
        "/help - সব কমান্ড",
        parse_mode="HTML",
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 <b>কমান্ড লিস্ট:</b>\n\n"
        "/run [category] - পাইপলাইন চালান (public upload)\n"
        "/run_private [category] - পাইপলাইন চালান (private)\n"
        "/create [category] - শুধু আইডিয়া জেনারেট\n"
        "/status - সিস্টেম স্ট্যাটাস\n"
        "/history - শেষ কাজ দেখুন\n"
        "/help - এই মেসেজ",
        parse_mode="HTML",
    )


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update):
        return

    msg = await update.message.reply_text("⏳ Checking...", parse_mode="HTML")

    try:
        async with async_session() as db:
            service = AgentService(db)
            stats = await service.get_dashboard_stats()

        text = (
            "📊 <b>System Status</b>\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"📝 Ideas: {stats.get('total_ideas', 0)}\n"
            f"📜 Scripts: {stats.get('total_scripts', 0)}\n"
            f"🎥 Videos: {stats.get('total_videos', 0)}\n"
            f"📤 Uploads: {stats.get('total_uploads', 0)}\n"
            f"✅ Published: {stats.get('published_videos', 0)}\n"
            f"⏰ Scheduled: {stats.get('scheduled_videos', 0)}\n"
            f"❌ Failed: {stats.get('failed_tasks', 0)}\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"🟢 Pipeline: {stats.get('pipeline_status', 'ready')}"
        )
        await msg.edit_text(text, parse_mode="HTML")
    except Exception as e:
        await msg.edit_text(f"❌ Error: {e}")


async def cmd_create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update):
        return

    category = " ".join(context.args) if context.args else "ai-tools"
    msg = await update.message.reply_text(f"⏳ Generating ideas for: {category}...")

    try:
        async with async_session() as db:
            service = AgentService(db)
            ideas = await service.generate_ideas(category=category, count=3)

        if ideas:
            text = f"💡 <b>Generated Ideas</b> ({category}):\n\n"
            for i, idea in enumerate(ideas, 1):
                title = getattr(idea, "title_bn", str(idea))
                text += f"{i}. {title[:80]}\n"
            await msg.edit_text(text, parse_mode="HTML")
        else:
            await msg.edit_text("❌ No ideas generated. Check AI API keys.")
    except Exception as e:
        await msg.edit_text(f"❌ Error: {e}")


async def cmd_run(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update):
        return

    category = " ".join(context.args) if context.args else "ai-tools"
    is_private = update.message.text.startswith("/run_private")
    visibility = "private" if is_private else "public"

    msg = await update.message.reply_text(
        f"🚀 <b>Pipeline Started</b>\n\n"
        f"Category: {category}\n"
        f"Visibility: {visibility}\n\n"
        f"⏳ This takes 5-8 minutes...",
        parse_mode="HTML",
    )

    try:
        async with async_session() as db:
            service = AgentService(db)
            results = await service.run_full_pipeline(category, "1080x1920", visibility)

        vid = results.get("youtube_video_id", "N/A")
        if results.get("success"):
            await msg.edit_text(
                f"✅ <b>Pipeline Complete!</b>\n\n"
                f"📹 Video ID: {vid}\n"
                f"🔗 https://youtube.com/watch?v={vid}",
                parse_mode="HTML",
            )
        else:
            err = results.get("error", "Unknown")
            await msg.edit_text(
                f"⚠️ <b>Partial Success</b>\n\n"
                f"Video generated but upload had issues.\n"
                f"Error: {err}",
                parse_mode="HTML",
            )
    except Exception as e:
        await msg.edit_text(f"❌ <b>Pipeline Failed</b>\n\n{e}", parse_mode="HTML")


async def cmd_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update):
        return

    try:
        from sqlalchemy import select
        from database.models.models import YouTubeUpload

        async with async_session() as db:
            result = await db.execute(
                select(YouTubeUpload).order_by(YouTubeUpload.created_at.desc()).limit(5)
            )
            uploads = result.scalars().all()

        if not uploads:
            await update.message.reply_text("📭 No uploads yet.")
            return

        text = "📋 <b>Last 5 Uploads:</b>\n\n"
        for u in uploads:
            status_emoji = "✅" if u.status == "published" else "❌" if u.status == "failed" else "⏳"
            yt_id = u.youtube_video_id or "N/A"
            title = (u.title or "No title")[:50]
            text += f"{status_emoji} {title}\n   {yt_id}\n\n"

        await update.message.reply_text(text, parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


def main():
    if not BOT_TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN not set in .env")
        sys.exit(1)

    print(f"Starting Telegram bot... (allowed chat: {ALLOWED_CHAT_ID or 'ANY'})")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("create", cmd_create))
    app.add_handler(CommandHandler("run", cmd_run))
    app.add_handler(CommandHandler("run_private", cmd_run))
    app.add_handler(CommandHandler("history", cmd_history))

    print("Bot polling started. Send /start to your bot on Telegram.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
