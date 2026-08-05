"""Image Agent - Generates images using free Pollinations.ai or local gradients."""

import os
import time
import urllib.request
from typing import Any

from agents.base import BaseAgent
from core.config.settings import get_settings
from utils.logger import get_logger

settings = get_settings()
logger = get_logger()


class ImageAgent(BaseAgent):
    """Generates images using free API or local gradient fallback."""

    async def execute(self, **kwargs) -> dict[str, Any]:
        prompt_text = kwargs.get("prompt", "")
        output_path = kwargs.get("output_path", "storage/images/output.png")
        width = kwargs.get("width", 1080)
        height = kwargs.get("height", 1920)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        logger.info(f"ImageAgent: Generating image: {prompt_text[:80]}...")

        # Try Pollinations.ai (free, no API key)
        result = self._try_pollinations(prompt_text, output_path, width, height)
        if result.get("success"):
            return result

        # Try Gemini if available
        if settings.GEMINI_API_KEY:
            try:
                result = await self._gemini_image(prompt_text, output_path, width, height)
                if result.get("success"):
                    return result
            except Exception as e:
                logger.warning(f"ImageAgent: Gemini failed: {e}")

        # Fallback: create gradient locally
        logger.info("ImageAgent: Using local gradient fallback")
        self._create_gradient(output_path, width, height)
        return {"success": True, "path": output_path, "provider": "local"}

    def _try_pollinations(self, prompt: str, output_path: str, width: int, height: int) -> dict:
        try:
            import urllib.parse
            encoded = urllib.parse.quote(prompt[:200])
            url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&nologo=true"
            urllib.request.urlretrieve(url, output_path)
            time.sleep(0.5)
            if os.path.getsize(output_path) > 1000:
                logger.info(f"ImageAgent: Pollinations saved to {output_path}")
                return {"success": True, "path": output_path, "provider": "pollinations"}
        except Exception as e:
            logger.warning(f"ImageAgent: Pollinations failed: {e}")
        return {"success": False, "path": None}

    async def _gemini_image(self, prompt: str, output_path: str, width: int, height: int) -> dict:
        import google.generativeai as genai

        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            f"Generate an abstract AI/tech themed background image. Description: {prompt}. Dark theme, {width}x{height}."
        )
        if hasattr(response, "text"):
            return {"success": False}

        return {"success": False}

    def _create_gradient(self, output_path: str, width: int, height: int):
        from PIL import Image

        img = Image.new("RGB", (width, height))
        pixels = img.load()

        for y in range(height):
            r = int(15 + (y / height) * 30)
            g = int(10 + (y / height) * 25)
            b = int(40 + (y / height) * 40)
            for x in range(width):
                pixels[x, y] = (min(r, 60), min(g, 50), min(b, 100))

        img.save(output_path, "PNG")
        logger.info(f"ImageAgent: Gradient saved to {output_path}")
