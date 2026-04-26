"""OLX scraper implementation."""

import logging
from typing import Optional

from bs4 import BeautifulSoup
from playwright.async_api import Page

from config.scrapers.configs import OLX_CONFIG, ScraperConfig
from services.worker.scrapers.base import RawListing
from services.worker.scrapers.platforms.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class OLXScraper(BaseScraper):
    def __init__(self, config: ScraperConfig = OLX_CONFIG):
        super().__init__(config)

    async def extract_listings(self, page: Page) -> list[RawListing]:
        content = await page.content()
        soup = BeautifulSoup(content, "html.parser")

        listings = []
        cards = soup.select(self.config.listing_selector)

        for card in cards:
            try:
                listing = self.extract_listing(card)
                if listing and listing.listing_url:
                    listings.append(listing)
            except Exception as e:
                logger.warning(f"Failed to extract listing: {str(e)}")
                continue

        return listings

    def extract_listing(self, card) -> Optional[RawListing]:
        title_elem = card.select_one(self.config.title_selector)
        price_elem = card.select_one(self.config.price_selector)
        seller_elem = card.select_one(self.config.seller_selector)
        location_elem = card.select_one(self.config.location_selector)
        image_elem = card.select_one(self.config.image_selector)
        condition_elem = card.select_one(self.config.condition_selector)

        link_elem = card.find("a") or card.select_one('a[href]')
        listing_url = (
            link_elem.get("href", "") if link_elem else ""
        )
        if listing_url and not listing_url.startswith("http"):
            listing_url = f"{self.config.base_url}{listing_url}"

        title = title_elem.get_text(strip=True) if title_elem else ""
        if not title:
            return None

        raw_listing = RawListing(
            platform=self.config.platform,
            listing_url=listing_url,
            title=title,
            price_raw=price_elem.get_text(strip=True) if price_elem else None,
            seller_name=seller_elem.get_text(strip=True) if seller_elem else None,
            location=location_elem.get_text(strip=True) if location_elem else None,
            condition_raw=condition_elem.get_text(strip=True) if condition_elem else None,
        )

        if image_elem:
            img = image_elem.find("img")
            if img:
                raw_listing.image_urls = [img.get("src", "")] if img.get("src") else []

        return raw_listing