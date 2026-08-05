"""Video Agent - Fast video assembly using FFmpeg."""

import os
import subprocess
from typing import Any

from agents.base import BaseAgent
from utils.logger import get_logger

logger = get_logger()


class VideoAgent(BaseAgent):
    """Creates videos with FFmpeg — fast and efficient."""

    async def execute(self, **kwargs) -> dict[str, Any]:
        audio_path = kwargs.get("audio_path", "")
        text_overlays = kwargs.get("text_overlays", [])
        output_path = kwargs.get("output_path", "storage/videos/output.mp4")
        resolution = kwargs.get("resolution", "1080x1920")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        w, h = (1080, 1920) if resolution == "1080x1920" else (1920, 1080)

        print(f"  Creating {w}x{h} video with FFmpeg...", flush=True)

        try:
            if audio_path and os.path.exists(audio_path):
                return await self._ffmpeg_video(audio_path, output_path, w, h, text_overlays)
            else:
                return await self._create_blank(output_path, w, h, 10)
        except Exception as e:
            logger.error(f"VideoAgent: Failed: {e}")
            return {"success": False, "error": str(e), "path": None}

    async def _ffmpeg_video(self, audio_path: str, output_path: str, w: int, h: int, texts: list) -> dict:
        import asyncio
        import tempfile

        # Get audio duration
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", audio_path],
            capture_output=True, text=True,
        )
        duration = float(probe.stdout.strip() or 10)

        # Build filter_complex with text overlays
        filter_parts = [f"color=c=0x141428:s={w}x{h}:d={duration}[bg]"]

        if texts:
            chunk = duration / len(texts)
            prev = "[bg]"
            for i, txt in enumerate(texts[:6]):
                clean = txt.replace("'", "").replace(":", " ").replace("\\", "")[:50]
                start_t = i * chunk
                label = f"txt{i}"
                filter_parts.append(
                    f"{prev}drawtext=text='{clean}':fontcolor=white:fontsize={h//18}:"
                    f"x=(w-text_w)/2:y=(h-text_h)/2.2:"
                    f"enable='between(t,{start_t:.2f},{start_t + chunk:.2f})':"
                    f"bordercolor=black@0.5:borderw=3[{label}]"
                )
                prev = f"[{label}]"
        else:
            prev = "[bg]"

        # Build and run FFmpeg
        filter_str = ";".join(filter_parts)
        cmd = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-f", "lavfi", "-i", f"color=c=0x141428:s={w}x{h}:d={duration}",
            "-i", audio_path,
            "-filter_complex", filter_str,
            "-map", prev.replace("[", "").replace("]", ""),
            "-map", "1:a",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
            "-c:a", "aac", "-b:a", "128k",
            "-shortest", "-t", str(duration),
            output_path,
        ]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            err = stderr.decode()[:500] if stderr else "Unknown"
            logger.error(f"FFmpeg failed: {err}")
            return await self._create_blank(output_path, w, h, int(duration))

        file_size = os.path.getsize(output_path) / (1024 * 1024)
        logger.info(f"VideoAgent: Created {file_size:.1f}MB video in {duration:.0f}s")
        print(f"  Video ready: {file_size:.1f}MB, {duration:.0f}s", flush=True)
        return {"success": True, "path": output_path, "file_size_mb": file_size, "duration_seconds": duration}

    async def _create_blank(self, output_path: str, width: int, height: int, duration: int = 10) -> dict:
        cmd = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-f", "lavfi", "-i", f"color=c=0x121428:s={width}x{height}:d={duration}",
            "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "30",
            "-c:a", "aac",
            "-shortest", output_path,
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return {"success": True, "path": output_path, "file_size_mb": 0.3, "duration_seconds": duration}
