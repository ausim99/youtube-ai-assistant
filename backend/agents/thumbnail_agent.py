"""Thumbnail Agent - Creates high-CTR YouTube thumbnails with Bangla text."""

import os
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from agents.base import BaseAgent
from agents.image_agent import ImageAgent
from utils.logger import get_logger

logger = get_logger()


class ThumbnailAgent(BaseAgent):
    """Creates professional YouTube thumbnails with AI-generated imagery and Bangla text overlay."""

    async def execute(self, **kwargs) -> dict[str, Any]:
        title = kwargs.get("title", "")
        thumbnail_text = kwargs.get("thumbnail_text", title[:30])
        output_path = kwargs.get("output_path", "storage/thumbnails/thumbnail.jpg")
        template = kwargs.get("template", "default")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        logger.info(f"ThumbnailAgent: Creating thumbnail for '{title[:50]}'")

        try:
            bg_prompt = f"YouTube thumbnail background, tech/AI theme, vibrant colors, high contrast, professional, {template} style"

            image_agent = ImageAgent()
            bg_result = await image_agent.execute(
                prompt=bg_prompt,
                output_path="storage/thumbnails/temp_bg.png",
                width=1280,
                height=720,
            )

            if bg_result.get("success") and os.path.exists(bg_result["path"]):
                await self._add_text_overlay(bg_result["path"], thumbnail_text, output_path)
            else:
                await self._create_simple_thumbnail(thumbnail_text, output_path)

            logger.info(f"ThumbnailAgent: Saved to {output_path}")
            return {"success": True, "path": output_path}
        except Exception as e:
            logger.error(f"ThumbnailAgent: Failed: {e}")
            await self._create_simple_thumbnail(thumbnail_text, output_path)
            return {"success": True, "path": output_path, "fallback": True}

    async def _add_text_overlay(self, bg_path: str, text: str, output_path: str):
        img = Image.open(bg_path).convert("RGB")
        img = img.resize((1280, 720), Image.LANCZOS)
        draw = ImageDraw.Draw(img)

        try:
            font_large = ImageFont.truetype("C:/Windows/Fonts/Nirmala.ttf", 80)
            font_small = ImageFont.truetype("C:/Windows/Fonts/Nirmala.ttf", 40)
        except Exception:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()

        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle([(0, 420), (1280, 720)], fill=(0, 0, 0, 160))
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)

        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test = f"{current_line} {word}".strip()
            bbox = draw.textbbox((0, 0), test, font=font_large)
            if bbox[2] - bbox[0] < 1200:
                current_line = test
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        y_offset = 470
        for line in lines[:3]:
            bbox = draw.textbbox((0, 0), line, font=font_large)
            x = (1280 - (bbox[2] - bbox[0])) // 2
            draw.text((x + 4, y_offset + 4), line, font=font_large, fill=(0, 0, 0))
            draw.text((x, y_offset), line, font=font_large, fill=(255, 255, 0))
            y_offset += 75

        img.save(output_path, "JPEG", quality=95)

    async def _create_simple_thumbnail(self, text: str, output_path: str):
        img = Image.new("RGB", (1280, 720), (18, 18, 36))
        draw = ImageDraw.Draw(img)

        for i in range(720):
            r = 18 + (i // 3)
            g = 18 + (i // 5)
            b = 36 + (i // 2)
            draw.line([(0, i), (1280, i)], fill=(min(r, 255), min(g, 255), min(b, 255)))

        try:
            font = ImageFont.truetype("C:/Windows/Fonts/Nirmala.ttf", 70)
        except Exception:
            font = ImageFont.load_default()

        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test = f"{current_line} {word}".strip()
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] < 1200:
                current_line = test
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        y = 200
        for line in lines[:4]:
            bbox = draw.textbbox((0, 0), line, font=font)
            x = (1280 - (bbox[2] - bbox[0])) // 2
            draw.text((x + 3, y + 3), line, font=font, fill=(0, 0, 0))
            draw.text((x, y), line, font=font, fill=(0, 255, 255))
            y += 85

        img.save(output_path, "JPEG", quality=95)
