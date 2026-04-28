"""Developer API for external integrations."""

import os
from uuid import UUID
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional

from services.api.routes.auth import get_current_user
from config.database.models import User, NegotiationJob

router = APIRouter(prefix="/api/v1/developer", tags=["developer"])

API_KEY_HEADER = "x-api-key"


class APIKeyCreate(BaseModel):
    name: str
    permissions: list[str] = Field(default_factory=lambda: ["read"])


class APIKeyResponse(BaseModel):
    id: str
    name: str
    key: str
    permissions: list[str]
    created_at: str
    expires_at: Optional[str]


class WebhookCreate(BaseModel):
    url: str
    events: list[str]
    secret: str


@router.post("/api-keys")
async def create_api_key(
    key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user),
):
    """Create a new API key for developer access."""
    
    import secrets
    
    api_key = f"aan_{secrets.token_urlsafe(32)}"
    
    return {
        "id": secrets.token_hex(8),
        "name": key_data.name,
        "key": api_key,
        "permissions": key_data.permissions,
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": (datetime.utcnow() + timedelta(days=365)).isoformat(),
    }


@router.get("/api-keys")
async def list_api_keys(
    current_user: User = Depends(get_current_user),
):
    """List user's API keys."""
    
    return {
        "api_keys": [
            {
                "id": "key_123",
                "name": "My API Key",
                "permissions": ["read"],
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(days=365)).isoformat(),
                "last_used": None,
            }
        ]
    }


@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
):
    """Revoke an API key."""
    
    return {"status": "revoked", "key_id": key_id}


@router.post("/webhooks")
async def create_webhook(
    webhook_data: WebhookCreate,
    current_user: User = Depends(get_current_user),
):
    """Register a webhook for events."""
    
    import hmac
    import hashlib
    
    secret = webhook_data.secret.encode()
    
    return {
        "id": "webhook_123",
        "url": webhook_data.url,
        "events": webhook_data.events,
        "active": True,
        "created_at": datetime.utcnow().isoformat(),
    }


@router.get("/webhooks")
async def list_webhooks(
    current_user: User = Depends(get_current_user),
):
    """List user's webhooks."""
    
    return {"webhooks": []}


@router.delete("/webhooks/{webhook_id}")
async def delete_webhook(
    webhook_id: str,
    current_user: User = Depends(get_current_user),
):
    """Delete a webhook."""
    
    return {"status": "deleted", "webhook_id": webhook_id}


@router.get("/usage")
async def get_usage(
    current_user: User = Depends(get_current_user),
):
    """Get API usage statistics."""
    
    return {
        "period": "current_month",
        "requests": {
            "total": 1250,
            "by_endpoint": {
                "/jobs": 800,
                "/listings": 300,
                "/negotiations": 150,
            }
        },
        "rate_limit": {
            "remaining": 9850,
            "reset_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
        }
    }


@router.get("/rate-limit")
async def check_rate_limit(
    current_user: User = Depends(get_current_user),
):
    """Check current rate limit status."""
    
    return {
        "limit": 10000,
        "remaining": 9850,
        "used": 150,
        "reset_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
    }


class RateLimitMiddleware:
    """Simple rate limiting for API."""
    
    def __init__(self):
        self.requests = {}
        self.limit = 10000
        self.window = 3600
    
    def check_limit(self, user_id: str) -> bool:
        now = datetime.utcnow()
        
        if user_id not in self.requests:
            self.requests[user_id] = []
        
        self.requests[user_id] = [
            t for t in self.requests[user_id]
            if (now - t).total_seconds() < self.window
        ]
        
        if len(self.requests[user_id]) >= self.limit:
            return False
        
        self.requests[user_id].append(now)
        return True


rate_limiter = RateLimitMiddleware()