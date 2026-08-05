"""Tests for the YouTube AI Assistant backend."""

import pytest
from httpx import ASGITransport, AsyncClient
from main import app


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "YouTube AI Assistant"


@pytest.mark.asyncio
async def test_root(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "YouTube AI Assistant"


@pytest.mark.asyncio
async def test_config(client: AsyncClient):
    response = await client.get("/api/config")
    assert response.status_code == 200
    data = response.json()
    assert "channel_language" in data
    assert "ai_provider" in data


@pytest.mark.asyncio
async def test_get_ideas(client: AsyncClient):
    response = await client.get("/api/agents/ideas")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_scripts(client: AsyncClient):
    response = await client.get("/api/agents/scripts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_videos(client: AsyncClient):
    response = await client.get("/api/agents/videos")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_uploads(client: AsyncClient):
    response = await client.get("/api/agents/uploads")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_dashboard_stats(client: AsyncClient):
    response = await client.get("/api/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_ideas" in data


@pytest.mark.asyncio
async def test_dashboard_logs(client: AsyncClient):
    response = await client.get("/api/dashboard/logs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
