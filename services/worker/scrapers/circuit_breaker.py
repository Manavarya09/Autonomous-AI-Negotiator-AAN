"""Circuit breaker implementation for reliable scraper handling."""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    success_threshold: int = 2
    timeout_seconds: float = 30.0
    excluded_exceptions: tuple = ()


@dataclass
class CircuitBreakerStats:
    failures: int = 0
    successes: int = 0
    last_failure_time: Optional[float] = None
    state: CircuitState = CircuitState.CLOSED


class CircuitBreaker:
    """Circuit breaker pattern for handling failing scrapers."""

    def __init__(self, name: str, config: CircuitBreakerConfig = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.stats = CircuitBreakerStats()
        self._lock = asyncio.Lock()

    async def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        async with self._lock:
            if self.stats.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.stats.state = CircuitState.HALF_OPEN
                    logger.info(f"Circuit '{self.name}' entering HALF_OPEN state")
                else:
                    raise CircuitOpenError(f"Circuit '{self.name}' is OPEN")

        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except Exception as e:
            await self._on_failure(e)
            raise

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.stats.last_failure_time is None:
            return True
        return (time.time() - self.stats.last_failure_time) >= self.config.timeout_seconds

    async def _on_success(self):
        """Handle successful call."""
        async with self._lock:
            self.stats.failures = 0
            self.stats.last_failure_time = None
            
            if self.stats.state == CircuitState.HALF_OPEN:
                self.stats.successes += 1
                if self.stats.successes >= self.config.success_threshold:
                    self.stats.state = CircuitState.CLOSED
                    self.stats.successes = 0
                    logger.info(f"Circuit '{self.name}' CLOSED after successful calls")

    async def _on_failure(self, error: Exception):
        """Handle failed call."""
        async with self._lock:
            self.stats.failures += 1
            self.stats.last_failure_time = time.time()
            
            if self.stats.state == CircuitState.HALF_OPEN:
                self.stats.state = CircuitState.OPEN
                self.stats.successes = 0
                logger.warning(f"Circuit '{self.name}' reopened after HALF_OPEN failure")
            elif self.stats.failures >= self.config.failure_threshold:
                self.stats.state = CircuitState.OPEN
                logger.warning(f"Circuit '{self.name}' OPEN after {self.stats.failures} failures")

    def get_state(self) -> dict:
        """Get current circuit state."""
        return {
            "name": self.name,
            "state": self.stats.state.value,
            "failures": self.stats.failures,
            "successes": self.stats.successes,
        }


class CircuitOpenError(Exception):
    """Raised when circuit is open."""
    pass


SCRAPER_CIRCUITS: dict[str, CircuitBreaker] = {}


def get_scraper_circuit(platform: str) -> CircuitBreaker:
    """Get or create circuit breaker for a platform."""
    if platform not in SCRAPER_CIRCUITS:
        SCRAPER_CIRCUITS[platform] = CircuitBreaker(
            name=f"scraper_{platform}",
            config=CircuitBreakerConfig(
                failure_threshold=5,
                timeout_seconds=30.0,
            )
        )
    return SCRAPER_CIRCUITS[platform]


def get_all_circuit_states() -> list[dict]:
    """Get state of all circuit breakers."""
    return [cb.get_state() for cb in SCRAPER_CIRCUITS.values()]