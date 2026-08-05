"""Image/Thumbnail Agent - Professional AI thumbnails using text + Pillow."""

import os
from typing import Any
from PIL import Image, ImageDraw, ImageFont

from agents.base import BaseAgent
from core.config.settings import get_settings
from utils.logger import get_logger

settings = get_settings()
logger = get_logger()


class ImageAgent(BaseAgent):
    """Generates professional AI-themed images and thumbnails."""

    async def execute(self, **kwargs) -> dict[str, Any]:
        prompt_text = kwargs.get("prompt", "")
        output_path = kwargs.get("output_path", "storage/images/output.png")
        width = kwargs.get("width", 1080)
        height = kwargs.get("height", 1920)
        style = kwargs.get("style", "tech")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        self._create_ai_gradient(output_path, width, height, style)
        return {"success": True, "path": output_path, "provider": "ai"}

    def _create_ai_gradient(self, output_path: str, width: int, height: int, style: str = "tech"):
        """Create AI-themed gradient with geometric shapes and glow effects."""
        img = Image.new("RGB", (width, height))
        pixels = img.load()

        styles = {
            "tech": (
                (13, 17, 38), (25, 20, 55), (18, 15, 70), (30, 10, 50),
            ),
            "warm": (
                (40, 10, 10), (50, 20, 5), (60, 15, 10), (45, 5, 20),
            ),
            "cool": (
                (10, 15, 40), (5, 25, 50), (15, 10, 60), (8, 30, 45),
            ),
        }

        colors = styles.get(style, styles["tech"])
        bands = len(colors)

        for y in range(height):
            band = (y * bands) // height
            next_band = min(band + 1, bands - 1)
            t = ((y * bands) % (height // bands)) / (height // bands)

            c1, c2 = colors[band], colors[next_band]
            r = int(c1[0] + (c2[0] - c1[0]) * t)
            g = int(c1[1] + (c2[1] - c1[1]) * t)
            b = int(c1[2] + (c2[2] - c1[2]) * t)

            for x in range(width):
                nx = x / width - 0.5
                dr = int(10 * abs(nx))
                pixels[x, y] = (
                    min(max(r + dr, 0), 255),
                    min(max(g + dr, 0), 255),
                    min(max(b + dr * 2, 0), 255),
                )

        draw = ImageDraw.Draw(img)

        # Glow circles
        for cx, cy, radius, opacity in [
            (width // 2, height // 3, 300, 20),
            (width - 100, height // 4, 150, 15),
            (80, height // 2, 200, 10),
            (width // 3, height - 200, 250, 15),
        ]:
            for r in range(radius, 0, -5):
                alpha = int(opacity * (r / radius))
                draw.ellipse(
                    [(cx - r, cy - r), (cx + r, cy + r)],
                    outline=(60, 80, 255, alpha),
                    width=1,
                )

        # Accent lines
        for y_pos in [height // 4, height // 2, (height * 3) // 4]:
            draw.line([(width * 0.1, y_pos), (width * 0.9, y_pos)], fill=(40, 80, 255, 8), width=2)

        img.save(output_path, "PNG")
        logger.info(f"ImageAgent: AI gradient saved to {output_path}")


class ThumbnailAgent(BaseAgent):
    """Creates high-CTR YouTube thumbnails with AI styling."""

    async def execute(self, **kwargs) -> dict[str, Any]:
        title = kwargs.get("title", "")
        thumbnail_text = kwargs.get("thumbnail_text", title[:30])
        output_path = kwargs.get("output_path", "storage/thumbnails/thumbnail.jpg")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        print(f"  Creating AI thumbnail: {thumbnail_text[:40]}...", flush=True)

        img = Image.new("RGB", (1280, 720))
        pixels = img.load()

        # Professional gradient background
        for y in range(720):
            t = y / 720
            r = int(10 + t * 30 + (1 - t) * 10)
            g = int(5 + t * 25 + (1 - t) * 15)
            b = int(30 + t * 60 + (1 - t) * 20)
            for x in range(1280):
                nx = (x - 640) / 640
                shade = int(10 * abs(nx))
                pixels[x, y] = (
                    min(r + shade, 80),
                    min(g + shade, 60),
                    min(b + shade, 140),
                )

        draw = ImageDraw.Draw(img)

        # Glow center
        for radius in range(350, 50, -10):
            alpha = int(10 * (radius / 350))
            draw.ellipse(
                [(640 - radius, 260 - radius), (640 + radius, 260 + radius)],
                outline=(60, 120, 255, alpha),
                width=2,
            )

        # Bottom dark overlay
        overlay = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
        odraw = ImageDraw.Draw(overlay)
        for y in range(400, 720):
            alpha = int(180 * ((y - 400) / 320))
            odraw.rectangle([(0, y), (1280, y)], fill=(0, 0, 0, alpha))
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)

        # Title text
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 70)
            sub_font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 35)
        except Exception:
            try:
                font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 70)
                sub_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 35)
            except Exception:
                font = ImageFont.load_default()
                sub_font = ImageFont.load_default()

        # Word wrap
        words = thumbnail_text.split()[:6]
        lines = []
        current = ""
        for word in words:
            test = f"{current} {word}".strip()
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] < 1150:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)

        # Draw title
        y = 430
        for line in lines[:3]:
            bbox = draw.textbbox((0, 0), line, font=font)
            x = (1280 - (bbox[2] - bbox[0])) // 2
            # Shadow
            draw.text((x + 4, y + 4), line, font=font, fill=(0, 0, 0))
            # Main text - bright yellow/white
            draw.text((x, y), line, font=font, fill=(255, 255, 50))
            y += 85

        # Channel name
        channel = settings.CHANNEL_NAME or "AI Bangla"
        draw.text((50, 650), channel, font=sub_font, fill=(200, 200, 255))

        # AI badge
        draw.rounded_rectangle([(1120, 645), (1240, 685)], radius=10, fill=(59, 130, 246))
        draw.text((1135, 650), "AI", font=sub_font, fill=(255, 255, 255))

        img.save(output_path, "JPEG", quality=95)
        return {"success": True, "path": output_path}
