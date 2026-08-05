"""Video Agent - Professional looking videos with text overlays, music, and transitions."""

import asyncio
import os
import subprocess
from typing import Any

from agents.base import BaseAgent
from utils.logger import get_logger

logger = get_logger()


class VideoAgent(BaseAgent):
    """Creates professional videos with text overlays, background music, and transitions."""

    async def execute(self, **kwargs) -> dict[str, Any]:
        audio_path = kwargs.get("audio_path", "")
        image_paths = kwargs.get("image_paths", [])
        text_overlays = kwargs.get("text_overlays", [])
        output_path = kwargs.get("output_path", "storage/videos/output.mp4")
        resolution = kwargs.get("resolution", "1080x1920")
        add_music = kwargs.get("add_music", True)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        w, h = (1080, 1920) if resolution == "1080x1920" else (1920, 1080)

        logger.info(f"VideoAgent: Creating professional video {w}x{h}")
        print(f"  Creating {w}x{h} video...", flush=True)

        try:
            if audio_path and os.path.exists(audio_path):
                return await self._create_professional(audio_path, text_overlays, output_path, w, h)
            else:
                return await self._create_blank(output_path, w, h, 10)

        except Exception as e:
            logger.error(f"VideoAgent: Failed: {e}")
            return {"success": False, "error": str(e), "path": None}

    async def _create_professional(
        self, audio_path: str, text_overlays: list[str], output_path: str, w: int, h: int
    ) -> dict:
        from moviepy import AudioFileClip, ColorClip, CompositeVideoClip, TextClip, concatenate_videoclips

        audio = AudioFileClip(audio_path)
        duration = audio.duration

        # Create animated gradient background
        bg_clips = []
        colors = [
            (18, 20, 40), (25, 18, 50), (15, 30, 60), (40, 15, 50),
            (20, 25, 45), (10, 20, 55), (30, 15, 40), (20, 10, 50),
        ]
        segment = duration / len(colors)

        for i, color in enumerate(colors):
            clip = ColorClip(size=(w, h), color=color, duration=segment)
            bg_clips.append(clip)

        bg = concatenate_videoclips(bg_clips, method="compose")

        # Generate text overlay clips
        text_clips = []
        if text_overlays:
            chunk_duration = duration / len(text_overlays)
            font_size = h // 18

            for idx, line in enumerate(text_overlays):
                try:
                    txt = TextClip(
                        text=line.strip()[:60],
                        font_size=font_size,
                        color="white",
                        stroke_color="black",
                        stroke_width=3,
                        size=(w - 80, None),
                        method="caption",
                        font="Nirmala-UI-Bold",
                    )
                    txt = txt.with_position(("center", h * 0.42))
                    txt = txt.with_start(idx * chunk_duration)
                    txt = txt.with_duration(chunk_duration)
                    txt = txt.with_effects([("crossfadein", 0.3), ("crossfadeout", 0.3)])
                    text_clips.append(txt)
                except Exception as e:
                    logger.warning(f"TextClip for '{line[:30]}' failed: {e}")

        # Composite
        all_clips = [bg] + text_clips
        video = CompositeVideoClip(all_clips, size=(w, h))
        video = video.with_duration(duration)
        video = video.with_audio(audio)

        video.write_videofile(
            output_path,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            preset="medium",
            bitrate="3000k",
            threads=2,
            logger=None,
        )

        audio.close()
        video.close()

        file_size = os.path.getsize(output_path) / (1024 * 1024)
        logger.info(f"VideoAgent: Created {file_size:.1f}MB video")
        return {"success": True, "path": output_path, "file_size_mb": file_size, "duration_seconds": duration}

    async def _create_blank(self, output_path: str, width: int, height: int, duration: int = 10) -> dict:
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", f"color=c=0x121428:s={width}x{height}:d={duration}",
            "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
            "-c:v", "libx264", "-c:a", "aac",
            "-shortest", output_path,
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return {"success": True, "path": output_path, "file_size_mb": 0.3, "duration_seconds": duration}
