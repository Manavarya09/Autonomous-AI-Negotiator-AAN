"""Amazon.ae scraper with price tracking."""

import logging
from typing import Optional
import re

from bs4 import BeautifulSoup
from playwright.async_api import Page
from playwright_stealth import stealth_async

from config.scrapers.configs import AMAZON_CONFIG, ScraperConfig
from services.worker.scrapers.base import RawListing
from services.worker.scrapers.platforms.base_scraper import BaseScraper
from services.worker.scrapers.anti_detection import random_delay

logger = logging.getLogger(__name__)


class AmazonScraper(BaseScraper):
    def __init__(self, config: ScraperConfig = AMAZON_CONFIG):
        super().__init__(config)

    async def scrape_page(
        self, query: str, page_num: int, location: Optional[str] = None
    ) -> list[RawListing]:
        search_url = self.config.search_url_template.format(
            query=query.replace(" ", "+")
        )
        
        if page_num > 1:
            search_url += f"&page={page_num}"

        logger.info(f"Scraping Amazon: {search_url}")

        try:
            page = await self.context.new_page()
            
            await stealth_async(page)
            await page.goto(search_url, timeout=30000)
            
            await random_delay(1000, 2000)
            
            await page.wait_for_selector(".s-result-item", timeout=10000)

            content = await page.content()
            await page.close()

            return await self.extract_listings_from_html(content)

        except Exception as e:
            logger.error(f"Failed to scrape Amazon page {page_num}: {str(e)}")
            return []

    async def extract_listings_from_html(self, html: str) -> list[RawListing]:
        soup = BeautifulSoup(html, "html.parser")
        
        listings = []
        items = soup.select(".s-result-item") or soup.select("[data-component-type='s-search-result']")

        for item in items:
            try:
                listing = self.extract_listing(item)
                if listing:
                    listings.append(listing)
            except Exception as e:
                logger.warning(f"Failed to extract listing: {str(e)}")
                continue

        logger.info(f"Found {len(listings)} listings")
        return listings

    def extract_listing(self, item) -> Optional[RawListing]:
        title_elem = item.select_one("h2 a span") or item.select_one(".a-text-normal")
        price_elem = item.select_one(".a-price-whole") or item.select_one("[data-a-color='price'] .a-offscreen")
        image_elem = item.select_one("img.s-image")
        rating_elem = item.select_one(".a-icon-alt")
        
        link_elem = item.select_one("h2 a") or item.select_one("a.a-link-normal")
        
        title = title_elem.get_text(strip=True) if title_elem else ""
        if not title:
            return None

        listing_url = ""
        if link_elem:
            listing_url = link_elem.get("href", "")
            if listing_url and not listing_url.startswith("http"):
                listing_url = f"https://www.amazon.ae{listing_url}"

        price_text = ""
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            price_text = re.sub(r"[^\d.]", "", price_text)

        raw_listing = RawListing(
            platform=self.config.platform,
            listing_url=listing_url,
            title=title,
            price_raw=price_text or None,
        )

        if image_elem:
            img_src = image_elem.get("src") or image_elem.get("data-old-hi") or image_elem.get("data-a-dynamic-image")
            if img_src and isinstance(img_src, str) and img_src.startswith("http"):
                raw_listing.image_urls = [img_src]
            elif isinstance(img_src, dict):
                raw_listing.image_urls = list(img_src.keys())[:3] if img_src else []

        if rating_elem:
            rating_text = rating_elem.get_text(strip=True)
            match = re.search(r"([\d.]+)\s*out", rating_text)
            if match:
                raw_listing.condition_raw = f"Rating: {match.group(1)} stars"

        return raw_listing