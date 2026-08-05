"""Image Agent - Generates AI images using Gemini/Flux/Stable Diffusion."""

import os
import base64
from typing import Any

from agents.base import BaseAgent
from core.config.settings import get_settings
from utils.logger import get_logger

settings = get_settings()
logger = get_logger()


class ImageAgent(BaseAgent):
    """Generates AI images for video backgrounds and scenes."""

    async def execute(self, **kwargs) -> dict[str, Any]:
        prompt_text = kwargs.get("prompt", "")
        output_path = kwargs.get("output_path", "storage/images/output.png")
        width = kwargs.get("width", 1080)
        height = kwargs.get("height", 1920)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        logger.info(f"ImageAgent: Generating image: {prompt_text[:80]}...")

        try:
            if self.provider == "gemini":
                return await self._gemini_image(prompt_text, output_path, width, height)
            else:
                return await self._gemini_image(prompt_text, output_path, width, height)
        except Exception as e:
            logger.error(f"ImageAgent: Generation failed: {e}")
            return {"success": False, "error": str(e), "path": None}

    async def _gemini_image(self, prompt: str, output_path: str, width: int, height: int) -> dict:
        import google.generativeai as genai

        genai.configure(api_key=settings.GEMINI_API_KEY)

        model = genai.GenerativeModel("gemini-2.0-flash-exp-image-generation")
        response = model.generate_content([
            f"Generate an image: {prompt}. Style: Modern, high-quality YouTube thumbnail/video style. Resolution: {width}x{height}.",
        ])

        if response.candidates and response.candidates[0].content:
            for part in response.candidates[0].content.parts:
                if hasattr(part, "inline_data") and part.inline_data:
                    image_data = base64.b64decode(part.inline_data.data)
                    with open(output_path, "wb") as f:
                        f.write(image_data)
                    logger.info(f"ImageAgent: Saved to {output_path}")
                    return {"success": True, "path": output_path, "provider": "gemini"}

        raise Exception("No image data in response")
