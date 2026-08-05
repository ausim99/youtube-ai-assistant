"""Utility helpers."""

import hashlib
import os
from datetime import datetime


def generate_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:12]


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def format_duration(seconds: int) -> str:
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}:{secs:02d}"


def timestamp() -> str:
    return datetime.utcnow().isoformat()
