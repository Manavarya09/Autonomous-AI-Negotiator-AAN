"""Rate limiter for API endpoints."""

import time
from dataclasses import dataclass, field
from typing import Callable, Optional
import asyncio

from fastapi import HTTPException, Request, status


@dataclass
class RateLimitConfig:
    requests: int = 100
    window_seconds: int = 60
    burst: int = 10


@dataclass 
class RateLimitState:
    requests: list[float] = field(default_factory=list)
    burst_used: int = 0


class RateLimiter:
    """Token bucket rate limiter."""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.state = RateLimitState()
        self._lock = asyncio.Lock()
    
    async def check(self) -> bool:
        """Check if request is allowed."""
        async with self._lock:
            now = time.time()
            window = self.config.window_seconds
            
            self.state.requests = [
                t for t in self.state.requests 
                if now - t < window
            ]
            
            if len(self.state.requests) >= self.config.requests:
                return False
            
            self.state.requests.append(now)
            
            if self.state.burst_used >= self.config.burst:
                return False
            
            self.state.burst_used += 1
            return True
    
    async def reset_burst(self):
        """Reset burst counter."""
        async with self._lock:
            self.state.burst_used = 0


async def rate_limit_check(request: Request, config: RateLimitConfig = None):
    """FastAPI dependency for rate limiting."""
    if config is None:
        config = RateLimitConfig()
    
    rate_limiter = getattr(request.app.state, "rate_limiter", None)
    if rate_limiter is None:
        rate_limiter = RateLimiter(config)
        request.app.state.rate_limiter = rate_limiter
    
    allowed = await rate_limiter.check()
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )


USER_RATE_LIMIT = RateLimitConfig(
    requests=100,
    window_seconds=60,
    burst=10
)

ADMIN_RATE_LIMIT = RateLimitConfig(
    requests=1000,
    window_seconds=60,
    burst=50
)