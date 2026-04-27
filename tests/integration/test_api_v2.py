"""Integration tests for API endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport

from services.api.main import app


@pytest.fixture
async def client():
    """Create test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_check(client):
    """Test health endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_root(client):
    """Test root endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    assert "Autonomous AI Negotiator" in response.json()["message"]


@pytest.mark.asyncio
async def test_create_job_unauthorized(client):
    """Test job creation without auth."""
    response = await client.post(
        "/api/v1/jobs",
        json={
            "product_query": "iPhone 15",
            "target_price": 4000,
            "max_price": 5000,
        }
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_metrics(client):
    """Test metrics endpoint."""
    response = await client.get("/metrics")
    assert response.status_code == 200