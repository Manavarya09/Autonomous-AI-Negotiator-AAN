"""Pytest fixtures for testing."""

import asyncio
import pytest
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from config.database.models import Base


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
    
    await engine.dispose()


@pytest.fixture
def sample_listing_data() -> dict:
    """Sample listing data for tests."""
    return {
        "platform": "dubizzle",
        "listing_url": "https://dubizzle.com/item/123",
        "title": "Nikon D750 Camera Body",
        "price_raw": "AED 3,500",
        "seller_name": "Ahmed",
        "seller_contact": "ahmed@email.com",
        "condition_raw": "Used - Good",
        "location": "Dubai",
        "posted_date": "2 days ago",
        "image_urls": ["https://example.com/img1.jpg"],
    }


@pytest.fixture
def sample_job_data() -> dict:
    """Sample job data for tests."""
    return {
        "product_query": "Nikon D750",
        "target_price": 3000,
        "max_price": 4000,
        "currency": "AED",
        "location_city": "Dubai",
        "urgency": "normal",
    }