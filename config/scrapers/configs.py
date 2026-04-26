"""Scraper configurations for each platform."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ScraperConfig:
    platform: str
    base_url: str
    search_url_template: str
    listing_selector: str
    price_selector: str
    title_selector: str
    seller_selector: str
    seller_contact_selector: Optional[str] = None
    seller_profile_selector: Optional[str] = None
    image_selector: Optional[str] = None
    condition_selector: Optional[str] = None
    location_selector: Optional[str] = None
    posted_date_selector: Optional[str] = None
    description_selector: Optional[str] = None
    pagination_selector: Optional[str] = None
    max_pages: int = 3
    retry_limit: int = 3
    timeout_ms: int = 10000
    use_proxy: bool = True
    headless: bool = True


DUBIZZLE_CONFIG = ScraperConfig(
    platform="dubizzle",
    base_url="https://www.dubizzle.com.ae",
    search_url_template="https://www.dubizzle.com.ae/en/{query}/?query={query}&sort_by=date&sort_order=desc",
    listing_selector='[data-testid="listing-card"]',
    price_selector='[data-testid="price"]',
    title_selector='[data-testid="title"]',
    seller_selector='[data-testid="seller-name"]',
    seller_contact_selector='[data-testid="seller-contact"]',
    seller_profile_selector='[data-testid="seller-profile"]',
    image_selector='[data-testid="image"]',
    condition_selector='[data-testid="condition"]',
    location_selector='[data-testid="location"]',
    pagination_selector='[data-testid="pagination-next"]',
    max_pages=3,
    timeout_ms=10000,
    use_proxy=True,
    headless=True,
)

OLX_CONFIG = ScraperConfig(
    platform="olx",
    base_url="https://www.olx.com.ae",
    search_url_template="https://www.olx.com.ae/ae/{query}/q/{query}/",
    listing_selector='[data-testid="listing-card"]',
    price_selector='[data-testid="price"]',
    title_selector='[data-testid="title"]',
    seller_selector='[data-testid="user-name"]',
    seller_contact_selector='[data-testid="contact-button"]',
    seller_profile_selector='[data-testid="user-link"]',
    image_selector='[data-testid="image"]',
    condition_selector='[data-testid="condition"]',
    location_selector='[data-testid="location"]',
    pagination_selector='[data-testid="pagination-next"]',
    max_pages=3,
    timeout_ms=10000,
    use_proxy=True,
    headless=True,
)

FACEBOOK_CONFIG = ScraperConfig(
    platform="facebook_marketplace",
    base_url="https://www.facebook.com/marketplace",
    search_url_template="https://www.facebook.com/marketplace/{location}/search/?query={query}",
    listing_selector='[data-testid="marketplace-card"]',
    price_selector='[data-testid="price"]',
    title_selector='[data-testid="title"]',
    seller_selector='[data-testid="seller"]',
    seller_profile_selector='[data-testid="seller-link"]',
    image_selector='[data-testid="image"]',
    location_selector='[data-testid="location"]',
    max_pages=2,
    timeout_ms=15000,
    use_proxy=True,
    headless=True,
)

NOON_CONFIG = ScraperConfig(
    platform="noon",
    base_url="https://www.noon.com",
    search_url_template="https://www.noon.com/ae-en/search/?q={query}",
    listing_selector='[data-testid="product-card"]',
    price_selector='[data-testid="price"]',
    title_selector='[data-testid="product-title"]',
    seller_selector='[data-testid="seller"]',
    image_selector='[data-testid="product-image"]',
    condition_selector='[data-testid="condition"]',
    max_pages=3,
    timeout_ms=10000,
    use_proxy=False,
    headless=True,
)

AMAZON_CONFIG = ScraperConfig(
    platform="amazon_ae",
    base_url="https://www.amazon.ae",
    search_url_template="https://www.amazon.ae/s?k={query}",
    listing_selector='[data-component-type="s-search-result"]',
    price_selector='.a-price-whole',
    title_selector='.a-text-normal',
    seller_selector='#MerchantInfoInputIDTextarea',
    image_selector='.s-image',
    max_pages=2,
    timeout_ms=10000,
    use_proxy=False,
    headless=True,
)

PLATFORM_CONFIGS = {
    "dubizzle": DUBIZZLE_CONFIG,
    "olx": OLX_CONFIG,
    "facebook_marketplace": FACEBOOK_CONFIG,
    "noon": NOON_CONFIG,
    "amazon_ae": AMAZON_CONFIG,
}