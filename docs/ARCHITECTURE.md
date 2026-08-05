# YouTube AI Assistant - Architecture Documentation

## Entity-Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   ContentIdea   │       │   VideoScript   │       │  GeneratedVideo │
│─────────────────│       │─────────────────│       │─────────────────│
│ id (PK)         │──1:N──│ id (PK)         │──1:N──│ id (PK)         │
│ title_bn        │       │ idea_id (FK)    │       │ script_id (FK)  │
│ title_en        │       │ title           │       │ voice_path      │
│ category        │       │ script_bn       │       │ video_path      │
│ hook            │       │ script_en       │       │ thumbnail_path  │
│ unique_angle    │       │ hooks (JSON)    │       │ subtitle_path   │
│ target_audience │       │ scenes (JSON)   │       │ resolution      │
│ difficulty      │       │ seo_data (JSON) │       │ duration_seconds│
│ expected_ctr    │       │ duration_seconds│       │ file_size_mb    │
│ expected_rpm    │       │ word_count      │       │ status          │
│ expected_views  │       │ status          │       │ error_message   │
│ keyword_data    │       │ created_at      │       │ created_at      │
│ trend_score     │       │ updated_at      │       │ updated_at      │
│ status          │       └─────────────────┘       └────────┬────────┘
│ created_at      │                                          │
│ updated_at      │                                     1:N  │
└─────────────────┘                                          │
                                               ┌─────────────▼──────┐
                                               │   YouTubeUpload    │
                                               │────────────────────│
                                               │ id (PK)            │
                                               │ video_id (FK)      │
                                               │ youtube_video_id   │
                                               │ title              │
                                               │ description        │
                                               │ tags (JSON)        │
                                               │ hashtags (JSON)    │
                                               │ category_id        │
                                               │ visibility         │
                                               │ scheduled_at       │
                                               │ published_at       │
                                               │ view_count         │
                                               │ like_count         │
                                               │ comment_count      │
                                               │ status             │
                                               │ error_message      │
                                               │ created_at         │
                                               │ updated_at         │
                                               └────────────────────┘

┌─────────────────┐       ┌─────────────────┐
│    TaskLog      │       │      User       │
│─────────────────│       │─────────────────│
│ id (PK)         │       │ id (PK)         │
│ task_id         │       │ username        │
│ task_name       │       │ email           │
│ status          │       │ hashed_password │
│ progress        │       │ is_active       │
│ message         │       │ is_admin        │
│ error_trace     │       │ created_at      │
│ metadata (JSON) │       └─────────────────┘
│ started_at      │
│ completed_at    │       ┌─────────────────┐
└─────────────────┘       │   APIConfig     │
                          │─────────────────│
                          │ id (PK)         │
                          │ key_name        │
                          │ key_value       │
                          │ provider        │
                          │ is_active       │
                          │ updated_at      │
                          └─────────────────┘
```

## Data Flow

```
GitHub Actions Cron / Manual Trigger
         │
         ▼
┌─────────────────────────────────────────────────┐
│                  Pipeline                        │
│                                                  │
│  1. IdeaAgent ──► DB: ContentIdea                │
│         │                                        │
│  2. ScriptAgent ──► DB: VideoScript              │
│         │                                        │
│  3. SEOAgent ──► DB: VideoScript.seo_data        │
│         │                                        │
│  4. VoiceAgent ──► File: storage/audio/*.mp3     │
│         │                                        │
│  5. ImageAgent ──► File: storage/images/*.png    │
│         │                                        │
│  6. ThumbnailAgent ──► File: storage/thumbnails/ │
│         │                                        │
│  7. VideoAgent ──► DB: GeneratedVideo            │
│         │           File: storage/videos/*.mp4   │
│         │                                        │
│  8. UploadAgent ──► YouTube API                  │
│         │           DB: YouTubeUpload            │
│         │                                        │
│  9. TelegramAgent ──► Telegram Notification      │
└─────────────────────────────────────────────────┘
```

## AI Provider Routing

```
Request → BaseAgent.generate()
           │
           ├─ provider=gemini  → Gemini 2.0 Flash (free tier)
           ├─ provider=deepseek → DeepSeek API (via OpenAI client)
           └─ provider=grok    → Grok API (via OpenAI client)
           │
           └─ Fallback: Gemini (primary default)
```
