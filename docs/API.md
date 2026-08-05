# API Documentation

Base URL: `http://localhost:8000/api`

## System Endpoints

### Health Check
```
GET /api/health
Response: { "status": "healthy", "service": "YouTube AI Assistant", "version": "1.0.0" }
```

### Get Configuration
```
GET /api/config
Response: { "channel_language": "bn", "channel_name": "AI Bangla", ... }
```

### Login
```
POST /api/auth/login
Body: { "username": "admin", "password": "admin" }
Response: { "access_token": "...", "token_type": "bearer" }
```

## Agent Endpoints

### List Content Ideas
```
GET /api/agents/ideas
Query: ?limit=50
Response: ContentIdea[]
```

### Generate Content Ideas
```
POST /api/agents/ideas
Body: { "category": "ai-tools", "count": 5 }
Response: ContentIdea[]
```

### Generate Script
```
POST /api/agents/scripts
Body: {
  "idea_id": "uuid",
  "language": "bn",
  "tone": "professional",
  "duration_seconds": 60
}
Response: VideoScript
```

### Generate Video
```
POST /api/agents/videos
Body: {
  "script_id": "uuid",
  "resolution": "1080x1920",
  "add_music": false,
  "add_subtitles": true
}
Response: GeneratedVideo
```

### Upload to YouTube
```
POST /api/agents/uploads
Body: {
  "video_id": "uuid",
  "title": "My Video",
  "description": "...",
  "tags": ["AI", "Tech"],
  "visibility": "private",
  "scheduled_at": "2024-12-25T18:00:00Z"
}
Response: YouTubeUpload
```

### Run Full Pipeline
```
POST /api/agents/pipeline
Body: {
  "category": "ai-tools",
  "resolution": "1080x1920",
  "visibility": "private"
}
Response: { "status": "started", "message": "Pipeline running in background" }
```

## Dashboard Endpoints

### Get Stats
```
GET /api/dashboard/stats
Response: {
  "total_ideas": 50,
  "total_scripts": 30,
  "total_videos": 20,
  "total_uploads": 15,
  "published_videos": 10,
  "scheduled_videos": 5,
  "failed_tasks": 2,
  "pipeline_status": "ready"
}
```

### Get Logs
```
GET /api/dashboard/logs?limit=50&offset=0
Response: TaskLog[]
```

## Category IDs (YouTube)
```
1  - Film & Animation
2  - Autos & Vehicles
10 - Music
15 - Pets & Animals
17 - Sports
19 - Travel & Events
20 - Gaming
22 - People & Blogs
23 - Comedy
24 - Entertainment
25 - News & Politics
26 - Howto & Style
27 - Education
28 - Science & Technology
29 - Nonprofits & Activism
```

## Error Responses
```json
{
  "detail": "Error message description"
}
```

All errors return appropriate HTTP status codes:
- 200: Success
- 400: Bad request / Validation error
- 404: Resource not found
- 500: Internal server error
