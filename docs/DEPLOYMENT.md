# Deployment Guide

## Vercel Dashboard Deployment

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy dashboard
cd dashboard
vercel --prod

# Set environment variables in Vercel dashboard
NEXT_PUBLIC_API_URL=https://your-backend-url.com/api
```

## Backend Deployment (Docker)

```bash
# Build and start all services
docker compose up -d --build

# Check logs
docker compose logs -f backend
docker compose logs -f celery_worker

# Scale workers
docker compose up -d --scale celery_worker=3
```

## Production Checklist

- [ ] Set all API keys in `.env` or GitHub Secrets
- [ ] Change `JWT_SECRET_KEY` to a strong random value
- [ ] Set `APP_ENV=production`
- [ ] Set `DEBUG=false`
- [ ] Use PostgreSQL instead of SQLite for production
- [ ] Configure Redis with authentication
- [ ] Set up CloudFlare R2 for asset storage
- [ ] Configure YouTube OAuth and refresh token
- [ ] Enable Telegram bot with webhook mode
- [ ] Set up monitoring (Sentry, Grafana, etc.)
- [ ] Configure proper CORS origins
- [ ] Run database migrations
- [ ] Test the full pipeline end-to-end

## GitHub Secrets Setup

```
Settings → Secrets and variables → Actions → New repository secret

Required secrets:
- GEMINI_API_KEY
- YOUTUBE_CLIENT_ID
- YOUTUBE_CLIENT_SECRET
- YOUTUBE_REFRESH_TOKEN
- TELEGRAM_BOT_TOKEN
- TELEGRAM_CHAT_ID
- VERCEL_TOKEN

Variables:
- CHANNEL_LANGUAGE
- CHANNEL_NAME
- DEFAULT_CATEGORY
```

## YouTube OAuth Setup

1. Go to Google Cloud Console
2. Create a project or select existing
3. Enable YouTube Data API v3
4. Create OAuth 2.0 credentials (Desktop application)
5. Download credentials as JSON
6. Use the refresh token flow:

```python
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
credentials = flow.run_local_server(port=0)
print(f"Refresh Token: {credentials.refresh_token}")
```

7. Copy the refresh token to `YOUTUBE_REFRESH_TOKEN`
8. Copy Client ID and Secret to `YOUTUBE_CLIENT_ID` and `YOUTUBE_CLIENT_SECRET`

## Database Migration

```bash
# Using Alembic for migrations
cd backend

# Initialize
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head
```
