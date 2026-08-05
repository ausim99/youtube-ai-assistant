"""Database models for YouTube AI Assistant."""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import relationship

from database.session import Base


def generate_uuid():
    return str(uuid.uuid4())


def utcnow():
    return datetime.utcnow()


class ContentIdea(Base):
    __tablename__ = "content_ideas"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title_bn = Column(String(500), nullable=False)
    title_en = Column(String(500))
    category = Column(String(100), nullable=False)
    hook = Column(Text)
    unique_angle = Column(Text)
    target_audience = Column(String(255))
    difficulty = Column(String(50))
    expected_ctr = Column(Float)
    expected_rpm = Column(Float)
    expected_views = Column(Integer)
    keyword_data = Column(JSON)
    trend_score = Column(Float)
    competitor_analysis = Column(JSON)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    scripts = relationship("VideoScript", back_populates="idea", cascade="all, delete-orphan")


class VideoScript(Base):
    __tablename__ = "video_scripts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    idea_id = Column(String(36), ForeignKey("content_ideas.id", ondelete="CASCADE"))
    title = Column(String(500), nullable=False)
    script_bn = Column(Text, nullable=False)
    script_en = Column(Text)
    hooks = Column(JSON)
    duration_seconds = Column(Integer)
    word_count = Column(Integer)
    scenes = Column(JSON)
    seo_data = Column(JSON)
    status = Column(String(50), default="draft")
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    idea = relationship("ContentIdea", back_populates="scripts")
    videos = relationship("GeneratedVideo", back_populates="script", cascade="all, delete-orphan")


class GeneratedVideo(Base):
    __tablename__ = "generated_videos"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    script_id = Column(String(36), ForeignKey("video_scripts.id", ondelete="CASCADE"))
    voice_path = Column(String(500))
    background_music_path = Column(String(500))
    video_path = Column(String(500))
    thumbnail_path = Column(String(500))
    subtitle_path = Column(String(500))
    resolution = Column(String(50), default="1080x1920")
    duration_seconds = Column(Integer)
    file_size_mb = Column(Float)
    status = Column(String(50), default="processing")
    error_message = Column(Text)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    script = relationship("VideoScript", back_populates="videos")
    uploads = relationship("YouTubeUpload", back_populates="video", cascade="all, delete-orphan")


class YouTubeUpload(Base):
    __tablename__ = "youtube_uploads"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    video_id = Column(String(36), ForeignKey("generated_videos.id", ondelete="CASCADE"))
    youtube_video_id = Column(String(100))
    title = Column(String(500))
    description = Column(Text)
    tags = Column(JSON)
    hashtags = Column(JSON)
    category_id = Column(String(10))
    visibility = Column(String(50), default="private")
    scheduled_at = Column(DateTime)
    published_at = Column(DateTime)
    playlist_id = Column(String(100))
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    status = Column(String(50), default="pending")
    error_message = Column(Text)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    video = relationship("GeneratedVideo", back_populates="uploads")


class TaskLog(Base):
    __tablename__ = "task_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    task_id = Column(String(100))
    task_name = Column(String(255))
    status = Column(String(50), default="running")
    progress = Column(Integer, default=0)
    message = Column(Text)
    error_trace = Column(Text)
    extra_data = Column(JSON)
    started_at = Column(DateTime, default=utcnow)
    completed_at = Column(DateTime)


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)


class APIConfig(Base):
    __tablename__ = "api_configs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    key_name = Column(String(100), unique=True, nullable=False)
    key_value = Column(Text)
    provider = Column(String(50))
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
