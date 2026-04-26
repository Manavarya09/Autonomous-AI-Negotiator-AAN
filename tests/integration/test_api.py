"""API endpoint tests."""

import pytest
from httpx import AsyncClient, ASGITransport


@pytest.mark.asyncio
async def test_health_check():
    """Test health endpoint."""
    from services.api.main import app
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint."""
    from services.api.main import app
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        assert "Autonomous AI Negotiator" in response.json()["message"]


@pytest.mark.asyncio
async def test_create_job_validation():
    """Test job creation validation."""
    from services.api.main import app
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/jobs", json={})
        assert response.status_code == 422