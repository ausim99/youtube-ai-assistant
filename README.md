# YouTube AI Assistant

A production-ready, autonomous AI-powered YouTube automation platform for generating Bangla content.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Vercel Dashboard                      │
│              Next.js + Tailwind + Recharts               │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP/REST
┌────────────────────────▼────────────────────────────────┐
│                    FastAPI Backend                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │  Idea    │ │  Script  │ │   SEO    │ │  Voice   │  │
│  │  Agent   │ │  Agent   │ │  Agent   │ │  Agent   │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │  Image   │ │ Thumbnail│ │  Video   │ │  Upload  │  │
│  │  Agent   │ │  Agent   │ │  Agent   │ │  Agent   │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
│  ┌──────────┐ ┌──────────┐                              │
│  │ Telegram │ │ Analytics│                              │
│  │  Agent   │ │  Agent   │                              │
│  └──────────┘ └──────────┘                              │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                  Celery + Redis                           │
│            Task Queue & Scheduled Jobs                    │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│              Database (SQLite / PostgreSQL)               │
└─────────────────────────────────────────────────────────┘
```

## AI Agents

| Agent | Function | AI Provider |
|-------|----------|-------------|
| IdeaAgent | Generate Bangla content ideas | Gemini / DeepSeek / Grok |
| ScriptAgent | Write video scripts in Bengali | Gemini / DeepSeek / Grok |
| SEOAgent | Generate SEO metadata | Gemini / DeepSeek / Grok |
| VoiceAgent | Text-to-speech (Bangla female voice) | Google TTS / ElevenLabs / Azure |
| ImageAgent | Generate AI images | Gemini / Stable Diffusion |
| ThumbnailAgent | Create YouTube thumbnails | Pillow + AI images |
| VideoAgent | Assemble final videos | MoviePy + FFmpeg |
| UploadAgent | Upload to YouTube | YouTube Data API v3 |
| TelegramAgent | Bot notifications & commands | Telegram Bot API |

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 20+
- FFmpeg
- Redis (for production)
- Docker (optional)

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/youtube-ai-assistant.git
cd youtube-ai-assistant

# Run setup
python scripts/setup.py

# Install backend dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start backend
cd backend
uvicorn main:app --reload --port 8000

# Start dashboard (new terminal)
cd dashboard
npm install
npm run dev
```

### Docker

```bash
docker compose up
```

Services:
- Backend API: http://localhost:8000
- Dashboard: http://localhost:3000
- API Docs: http://localhost:8000/api/docs

## Configuration

### Required Secrets

| Secret | Purpose |
|--------|---------|
| GEMINI_API_KEY | AI content generation |
| YOUTUBE_CLIENT_ID | YouTube OAuth |
| YOUTUBE_CLIENT_SECRET | YouTube OAuth |
| YOUTUBE_REFRESH_TOKEN | YouTube API access |
| TELEGRAM_BOT_TOKEN | Telegram bot |
| TELEGRAM_CHAT_ID | Telegram chat |

### GitHub Variables

| Variable | Default | Description |
|----------|---------|-------------|
| CHANNEL_LANGUAGE | bn | Content language |
| CHANNEL_NAME | AI Bangla | Channel name |
| DEFAULT_CATEGORY | ai-tools | Default category |
| SHORTS_ENABLED | true | Enable Shorts |
| LONG_VIDEO_ENABLED | false | Enable long videos |
| VOICE_NAME | bn-IN-Wavenet-A | TTS voice |

## API Endpoints

### System
- `GET /api/health` - Health check
- `GET /api/config` - Get configuration
- `POST /api/auth/login` - Login

### Agents
- `GET /api/agents/ideas` - List ideas
- `POST /api/agents/ideas` - Generate ideas
- `GET /api/agents/scripts` - List scripts
- `POST /api/agents/scripts` - Generate script
- `GET /api/agents/videos` - List videos
- `POST /api/agents/videos` - Generate video
- `GET /api/agents/uploads` - List uploads
- `POST /api/agents/uploads` - Upload to YouTube
- `POST /api/agents/pipeline` - Run full pipeline

### Dashboard
- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/dashboard/logs` - Task logs

## Telegram Commands

| Command | Description |
|---------|-------------|
| /start | Welcome message |
| /help | List commands |
| /status | System status |
| /run | Start pipeline |
| /history | View history |
| /analytics | Channel analytics |

## GitHub Actions CI/CD

```yaml
Pipeline:
  1. Generate Ideas → 2. Write Script → 3. Generate Voice
  → 4. Create Images → 5. Assemble Video → 6. Create Thumbnail
  → 7. SEO Optimization → 8. Upload YouTube → 9. Notify Telegram
```

- Scheduled daily at 12:00 UTC
- Manual trigger via workflow_dispatch
- Artifact upload for logs
- Automatic Vercel deployment

## Project Structure

```
youtube-ai-assistant/
├── backend/
│   ├── agents/          # AI agents
│   ├── api/             # FastAPI routes
│   │   └── routes/      # Route modules
│   ├── core/            # Core config
│   │   └── config/      # Settings
│   ├── database/        # Database
│   │   └── models/      # SQLAlchemy models
│   ├── prompts/         # LLM prompts library
│   ├── services/        # Business logic
│   ├── tasks/           # Celery tasks
│   ├── tests/           # Unit tests
│   ├── utils/           # Utilities
│   └── storage/         # File storage
├── dashboard/           # Next.js frontend
│   └── src/
│       ├── app/         # Pages
│       ├── components/  # UI components
│       ├── lib/         # API client
│       └── types/       # TypeScript types
├── .github/
│   └── workflows/       # GitHub Actions
├── scripts/             # CLI tools
├── docs/                # Documentation
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Testing

```bash
cd backend
pytest tests/ -v

# With coverage
pytest tests/ --cov=. --cov-report=html
```

## License

MIT
