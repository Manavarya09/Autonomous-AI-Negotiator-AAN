"""Proxy rotation and BrightData integration for scrapers."""

import logging
import os
from typing import Optional

import httpx
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ProxyConfig:
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    session_id: Optional[str] = None
    country: Optional[str] = None


class ProxyManager:
    """Manages proxy rotation for scrapers."""
    
    def __init__(self):
        self.brightdata_username = os.getenv("BRIGHTDATA_USERNAME")
        self.brightdata_password = os.getenv("BRIGHTDATA_PASSWORD")
        self.current_session = None
        
    def get_brightdata_proxy(self, country: str = "ae") -> Optional[ProxyConfig]:
        """Get BrightData residential proxy."""
        if not self.brightdata_username or not self.brightdata_password:
            logger.warning("BrightData credentials not configured")
            return None
            
        session = f"session-{country}-{os.urandom(4).hex()}"
        
        return ProxyConfig(
            host="brd.superproxy.io",
            port=33335,
            username=self.brightdata_username,
            password=self.brightdata_password,
            session_id=session,
            country=country,
        )
    
    def get_proxy_url(self, config: ProxyConfig) -> str:
        """Get formatted proxy URL."""
        if config.username and config.password:
            return f"http://{config.username}:{config.password}@{config.host}:{config.port}"
        return f"http://{config.host}:{config.port}"
    
    async def test_proxy(self, config: ProxyConfig) -> bool:
        """Test if proxy is working."""
        try:
            proxy_url = self.get_proxy_url(config)
            async with httpx.AsyncClient(proxies=proxy_url, timeout=10) as client:
                response = await client.get("https://httpbin.org/ip")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Proxy test failed: {e}")
            return False
    
    def should_use_proxy(self, platform: str) -> bool:
        """Determine if proxy should be used for platform."""
        no_proxy_platforms = ["noon", "amazon_ae"]
        return platform not in no_proxy_platforms


proxy_manager = ProxyManager()


def get_proxy_for_platform(platform: str, country: str = "ae") -> Optional[ProxyConfig]:
    """Get configured proxy for platform."""
    if proxy_manager.should_use_proxy(platform):
        return proxy_manager.get_brightdata_proxy(country)
    return None