"""Core configuration for YouTube AI Assistant."""

import os
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_NAME: str = "YouTube AI Assistant"
    APP_ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./storage/youtube_ai.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # AI Providers
    GEMINI_API_KEY: str = ""
    DEEPSEEK_API_KEY: str = ""
    GROK_API_KEY: str = ""
    DEFAULT_AI_PROVIDER: Literal["gemini", "deepseek", "grok"] = "gemini"

    # Google / YouTube
    GOOGLE_API_KEY: str = ""
    YOUTUBE_CLIENT_ID: str = ""
    YOUTUBE_CLIENT_SECRET: str = ""
    YOUTUBE_REFRESH_TOKEN: str = ""
    YOUTUBE_REFRESH_TOKEN_UPLOAD: str = ""
    YOUTUBE_CHANNEL_ID: str = ""

    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""

    # TTS
    ELEVENLABS_API_KEY: str = ""
    AZURE_SPEECH_KEY: str = ""
    AZURE_SPEECH_REGION: str = "eastus"
    DEFAULT_TTS_PROVIDER: Literal["google", "elevenlabs", "azure"] = "google"

    # Stock Footage & Music
    PEXELS_API_KEY: str = ""
    PIXABAY_API_KEY: str = ""

    # Cloud Storage (R2)
    R2_ACCESS_KEY: str = ""
    R2_SECRET_KEY: str = ""
    R2_BUCKET: str = "youtube-ai-assets"
    R2_ENDPOINT: str = ""

    # Channel
    CHANNEL_LANGUAGE: str = "bn"
    CHANNEL_NAME: str = "AI Bangla"
    DEFAULT_CATEGORY: str = "ai-tools"
    UPLOAD_TIME: str = "18:00"
    TIMEZONE: str = "Asia/Dhaka"
    VOICE_NAME: str = "bn-IN-Wavenet-A"
    VIDEO_DURATION: int = 60
    SHORTS_ENABLED: bool = True
    LONG_VIDEO_ENABLED: bool = False

    # Vercel
    VERCEL_TOKEN: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
