"""Stock Footage Agent - Downloads free clips from Pexels/ Pixabay."""

import os
import random
import urllib.request
import json
from typing import Any

from agents.base import BaseAgent
from core.config.settings import get_settings
from utils.logger import get_logger

settings = get_settings()
logger = get_logger()

PEXELS_HEADERS = {}
if settings.PEXELS_API_KEY:
    PEXELS_HEADERS = {"Authorization": settings.PEXELS_API_KEY}


class StockFootageAgent(BaseAgent):
    """Downloads free stock footage matching the video topic."""

    async def execute(self, **kwargs) -> list[str]:
        topic = kwargs.get("topic", "technology AI")
        count = kwargs.get("count", 4)
        output_dir = kwargs.get("output_dir", "storage/footage")

        os.makedirs(output_dir, exist_ok=True)
        downloaded = []

        # Try Pexels video API
        if settings.PEXELS_API_KEY:
            clips = await self._pexels_videos(topic, count)
            for i, clip in enumerate(clips):
                path = os.path.join(output_dir, f"clip_{i}.mp4")
                if self._download(clip, path):
                    downloaded.append(path)
                    logger.info(f"Downloaded: {path}")

        # Fallback to Pixabay
        if not downloaded:
            clips = await self._pixabay_videos(topic, count)
            for i, clip in enumerate(clips):
                path = os.path.join(output_dir, f"clip_{i}.mp4")
                if self._download(clip, path):
                    downloaded.append(path)

        if downloaded:
            print(f"  Downloaded {len(downloaded)} stock clips", flush=True)
        else:
            print(f"  No stock clips found, will use gradient background", flush=True)

        return downloaded

    async def _pexels_videos(self, query: str, count: int) -> list[str]:
        try:
            encoded = urllib.parse.quote(query[:100])
            url = f"https://api.pexels.com/videos/search?query={encoded}&per_page={min(count + 5, 20)}&orientation=portrait&size=medium"
            req = urllib.request.Request(url, headers=PEXELS_HEADERS)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
            videos = data.get("videos", [])
            urls = []
            for v in videos[:count]:
                files = v.get("video_files", [])
                portrait = [f for f in files if f.get("width", 0) < 1000]
                best = portrait[0] if portrait else (files[0] if files else None)
                if best:
                    urls.append(best["link"])
            return urls
        except Exception as e:
            logger.warning(f"Pexels API failed: {e}")
            return []

    async def _pixabay_videos(self, query: str, count: int) -> list[str]:
        try:
            key = settings.PIXABAY_API_KEY or ""
            encoded = urllib.parse.quote(query[:100])
            url = f"https://pixabay.com/api/videos/?key={key}&q={encoded}&per_page={count}&orientation=vertical"
            with urllib.request.urlopen(url, timeout=15) as resp:
                data = json.loads(resp.read())
            hits = data.get("hits", [])
            urls = []
            for h in hits[:count]:
                videos = h.get("videos", {})
                medium = videos.get("medium") or videos.get("small") or videos.get("large")
                if medium:
                    urls.append(medium.get("url", ""))
            return [u for u in urls if u]
        except Exception as e:
            logger.warning(f"Pixabay API failed: {e}")
            return []

    def _download(self, url: str, path: str) -> bool:
        try:
            if not url:
                return False
            urllib.request.urlretrieve(url, path)
            return os.path.getsize(path) > 5000
        except Exception as e:
            logger.warning(f"Download failed: {e}")
            return False
