"""Facebook Marketplace scraper implementation."""

import logging
from typing import Optional

from bs4 import BeautifulSoup
from playwright.async_api import Page

from config.scrapers.configs import FACEBOOK_CONFIG, ScraperConfig
from services.worker.scrapers.base import RawListing
from services.worker.scrapers.platforms.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class FacebookMarketplaceScraper(BaseScraper):
    """Scraper for Facebook Marketplace."""

    def __init__(self, config: ScraperConfig = FACEBOOK_CONFIG):
        super().__init__(config)

    async def extract_listings(self, page: Page) -> list[RawListing]:
        """Extract listings from Facebook Marketplace search results."""
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
        """Extract listing data from a card element."""
        title_elem = card.select_one(self.config.title_selector)
        price_elem = card.select_one(self.config.price_selector)
        seller_elem = card.select_one(self.config.seller_selector)
        location_elem = card.select_one(self.config.location_selector)
        image_elem = card.select_one(self.config.image_selector)

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
            price_raw=price_elem.get_text(strip=True) if price_elem else "",
            seller_name=seller_elem.get_text(strip=True) if seller_elem else None,
            location=location_elem.get_text(strip=True) if location_elem else None,
        )

        if image_elem:
            img = image_elem.find("img")
            if img and img.get("src"):
                raw_listing.image_urls = [img.get("src")]

        return raw_listing

    async def scrape_page(
        self, query: str, page_num: int, location: Optional[str] = None
    ) -> list[RawListing]:
        """Scrape a single page of results."""
        params = self.config.search_params.copy()
        params["q"] = query
        params["start"] = (page_num - 1) * self.config.page_size

        search_url = f"{self.config.search_url}"
        
        url = f"{self.config.base_url}/marketplace/?{params['q']}"
        
        logger.info(f"Scraping Facebook Marketplace: {url}")

        try:
            page = await self.context.new_page()
            await page.goto(url, timeout=30000)
            
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(2000)

            listings = await self.extract_listings(page)
            await page.close()

            logger.info(f"Found {len(listings)} listings on page {page_num}")
            return listings

        except Exception as e:
            logger.error(f"Failed to scrape page {page_num}: {str(e)}")
            return []