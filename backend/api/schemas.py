"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ContentIdeaCreate(BaseModel):
    category: str = Field(default="ai-tools")
    language: str = Field(default="bn")
    count: int = Field(default=5, ge=1, le=10)


class ContentIdeaResponse(BaseModel):
    id: str
    title_bn: str
    title_en: Optional[str] = None
    category: str
    hook: Optional[str] = None
    unique_angle: Optional[str] = None
    target_audience: Optional[str] = None
    difficulty: Optional[str] = None
    expected_ctr: Optional[float] = None
    expected_rpm: Optional[float] = None
    expected_views: Optional[int] = None
    trend_score: Optional[float] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ScriptCreate(BaseModel):
    idea_id: str
    language: str = Field(default="bn")
    tone: str = Field(default="professional")
    duration_seconds: int = Field(default=60)
    include_hooks: bool = True


class ScriptResponse(BaseModel):
    id: str
    idea_id: Optional[str] = None
    title: str
    script_bn: str
    script_en: Optional[str] = None
    hooks: Optional[list[str]] = None
    duration_seconds: Optional[int] = None
    word_count: Optional[int] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class VideoGenerateRequest(BaseModel):
    script_id: str
    resolution: str = Field(default="1080x1920")
    add_music: bool = True
    add_subtitles: bool = True


class VideoResponse(BaseModel):
    id: str
    script_id: Optional[str] = None
    voice_path: Optional[str] = None
    video_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    subtitle_path: Optional[str] = None
    resolution: Optional[str] = None
    duration_seconds: Optional[int] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class YouTubeUploadRequest(BaseModel):
    video_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[list[str]] = None
    hashtags: Optional[list[str]] = None
    category_id: Optional[str] = Field(default="28")
    visibility: str = Field(default="private")
    scheduled_at: Optional[datetime] = None


class YouTubeUploadResponse(BaseModel):
    id: str
    video_id: Optional[str] = None
    youtube_video_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    visibility: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    view_count: Optional[int] = 0
    like_count: Optional[int] = 0
    status: str
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TaskLogResponse(BaseModel):
    id: str
    task_id: str
    task_name: str
    status: str
    progress: int
    message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class DashboardStats(BaseModel):
    total_ideas: int
    total_scripts: int
    total_videos: int
    total_uploads: int
    published_videos: int
    scheduled_videos: int
    failed_tasks: int
    pipeline_status: str


class PipelineRequest(BaseModel):
    category: Optional[str] = Field(default="ai-tools")
    resolution: Optional[str] = Field(default="1080x1920")
    visibility: Optional[str] = Field(default="private")
