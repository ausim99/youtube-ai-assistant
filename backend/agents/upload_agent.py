"""YouTube Upload Agent - Handles video uploads, thumbnails, and metadata to YouTube."""

import os
from datetime import datetime, timedelta, timezone
from typing import Any

import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from agents.base import BaseAgent
from core.config.settings import get_settings
from utils.logger import get_logger

settings = get_settings()
logger = get_logger()

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]


class UploadAgent(BaseAgent):
    """Uploads videos, thumbnails, and metadata to YouTube."""

    async def execute(self, **kwargs) -> dict[str, Any]:
        video_path = kwargs.get("video_path", "")
        title = kwargs.get("title", "AI Bangla Video")
        description = kwargs.get("description", "")
        tags = kwargs.get("tags", [])
        thumbnail_path = kwargs.get("thumbnail_path", "")
        category_id = kwargs.get("category_id", "28")
        visibility = kwargs.get("visibility", "private")
        scheduled_at = kwargs.get("scheduled_at")

        if not video_path or not os.path.exists(video_path):
            return {"success": False, "error": "Video file not found", "youtube_video_id": None}

        logger.info(f"UploadAgent: Uploading '{title}' ({visibility})")

        try:
            youtube = self._get_youtube_service()

            body = {
                "snippet": {
                    "title": title[:100],
                    "description": description[:5000],
                    "tags": tags[:30],
                    "categoryId": category_id,
                },
                "status": {
                    "privacyStatus": visibility,
                    "selfDeclaredMadeForKids": False,
                },
            }

            media = MediaFileUpload(
                video_path,
                mimetype="video/*",
                resumable=True,
                chunksize=1024 * 1024 * 5,
            )

            request = youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media,
            )

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    logger.info(f"UploadAgent: Uploaded {int(status.progress() * 100)}%")

            video_id = response["id"]
            logger.info(f"UploadAgent: Uploaded video ID: {video_id}")

            if thumbnail_path and os.path.exists(thumbnail_path):
                youtube.thumbnails().set(
                    videoId=video_id,
                    media_body=MediaFileUpload(thumbnail_path),
                ).execute()
                logger.info(f"UploadAgent: Thumbnail set for {video_id}")

            if scheduled_at and visibility == "private":
                if isinstance(scheduled_at, str):
                    scheduled_at = datetime.fromisoformat(scheduled_at)
                youtube.videos().update(
                    part="status",
                    body={
                        "id": video_id,
                        "status": {
                            "privacyStatus": "private",
                            "publishAt": scheduled_at.isoformat(),
                        },
                    },
                ).execute()
                logger.info(f"UploadAgent: Scheduled for {scheduled_at}")

            return {
                "success": True,
                "youtube_video_id": video_id,
                "url": f"https://youtube.com/watch?v={video_id}",
            }

        except Exception as e:
            logger.error(f"UploadAgent: Upload failed: {e}")
            return {"success": False, "error": str(e), "youtube_video_id": None}

    def _get_youtube_service(self):
        credentials = None
        upload_token = settings.YOUTUBE_REFRESH_TOKEN_UPLOAD or settings.YOUTUBE_REFRESH_TOKEN
        youtube_token = settings.YOUTUBE_REFRESH_TOKEN or upload_token

        if upload_token:
            try:
                credentials = Credentials(
                    token=None,
                    refresh_token=upload_token,
                    client_id=settings.YOUTUBE_CLIENT_ID,
                    client_secret=settings.YOUTUBE_CLIENT_SECRET,
                    token_uri="https://oauth2.googleapis.com/token",
                    scopes=SCOPES,
                )
                credentials.refresh(Request())
            except Exception as e:
                logger.warning(f"Upload token failed: {e}, trying youtube token...")
                credentials = None

        if not credentials and youtube_token and youtube_token != upload_token:
            credentials = Credentials(
                token=None,
                refresh_token=youtube_token,
                client_id=settings.YOUTUBE_CLIENT_ID,
                client_secret=settings.YOUTUBE_CLIENT_SECRET,
                token_uri="https://oauth2.googleapis.com/token",
                scopes=SCOPES,
            )
            credentials.refresh(Request())

        if not credentials:
            credentials, _ = google.auth.default(scopes=SCOPES)

        return build("youtube", "v3", credentials=credentials)
