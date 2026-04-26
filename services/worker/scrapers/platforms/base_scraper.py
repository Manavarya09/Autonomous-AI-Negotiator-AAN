"""Base scraper abstract class."""

import logging
from abc import ABC, abstractmethod
from typing import Optional

from playwright.async_api import Browser, BrowserContext, Page

from config.scrapers.configs import ScraperConfig
from services.worker.scrapers.anti_detection import (
    create_stealth_context,
    launch_browser,
    random_delay,
)
from services.worker.scrapers.base import RawListing

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    def __init__(self, config: ScraperConfig):
        self.config = config
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def start(self):
        self.browser = await launch_browser(
            headless=self.config.headless,
            proxy=None,
        )

    async def close(self):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()

    async def scrape(self, query: str, location: Optional[str] = None) -> list[RawListing]:
        listings = []

        for page_num in range(1, self.config.max_pages + 1):
            try:
                page_listings = await self.scrape_page(query, page_num, location)
                listings.extend(page_listings)
                logger.info(
                    f"{self.config.platform}: scraped {len(page_listings)} listings from page {page_num}"
                )
            except Exception as e:
                logger.error(
                    f"{self.config.platform}: failed to scrape page {page_num}: {str(e)}"
                )

            if page_num < self.config.max_pages:
                await random_delay()

        return listings

    async def scrape_page(
        self,
        query: str,
        page_num: int,
        location: Optional[str] = None,
    ) -> list[RawListing]:
        url = self.build_url(query, page_num, location)

        self.context = await create_stealth_context(
            self.browser,
            headless=self.config.headless,
        )

        page = await self.context.new_page()
        page.set_default_timeout(self.config.timeout_ms)

        try:
            await page.goto(url, wait_until="networkidle")
            await random_delay(min_seconds=1.0, max_seconds=2.0)

            return await self.extract_listings(page)
        finally:
            await page.close()

    def build_url(
        self,
        query: str,
        page_num: int,
        location: Optional[str] = None,
    ) -> str:
        base_url = self.config.search_url_template.format(query=query, location=location or "")
        if page_num > 1:
            if "?" in base_url:
                return f"{base_url}&page={page_num}"
            else:
                return f"{base_url}?page={page_num}"
        return base_url

    @abstractmethod
    async def extract_listings(self, page: Page) -> list[RawListing]:
        pass