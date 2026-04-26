"""Scraper tasks for Celery."""

import asyncio
import logging
from typing import Optional

from services.worker.scrapers.platforms.dubizzle import DubizzleScraper
from services.worker.scrapers.platforms.olx import OLXScraper

logger = logging.getLogger(__name__)


async def run_dubizzle_scraper(query: str, location: Optional[str] = None):
    async with DubizzleScraper() as scraper:
        listings = await scraper.scrape(query, location)
        return [l.to_dict() for l in listings]


async def run_olx_scraper(query: str, location: Optional[str] = None):
    async with OLXScraper() as scraper:
        listings = await scraper.scrape(query, location)
        return [l.to_dict() for l in listings]


async def scrape_platform(platform: str, query: str, location: Optional[str] = None):
    if platform == "dubizzle":
        return await run_dubizzle_scraper(query, location)
    elif platform == "olx":
        return await run_olx_scraper(query, location)
    else:
        raise ValueError(f"Unsupported platform: {platform}")


async def scrape_all_platforms(
    query: str,
    platforms: Optional[list[str]] = None,
    location: Optional[str] = None,
):
    if platforms is None:
        platforms = ["dubizzle", "olx"]

    all_listings = []
    tasks = [scrape_platform(p, query, location) for p in platforms]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for platform, result in zip(platforms, results):
        if isinstance(result, Exception):
            logger.error(f"Failed to scrape {platform}: {result}")
        elif isinstance(result, list):
            all_listings.extend(result)

    return all_listings