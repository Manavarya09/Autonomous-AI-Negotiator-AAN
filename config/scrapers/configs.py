"""Scraper configurations with multiple fallback selectors."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ScraperConfig:
    platform: str
    base_url: str
    search_url_template: str
    search_url: str = ""
    search_params: dict = field(default_factory=dict)
    listing_selector: str = ""
    title_selector: str = ""
    price_selector: str = ""
    seller_selector: str = ""
    image_selector: str = ""
    location_selector: str = ""
    condition_selector: str = ""
    listing_selectors: list[str] = field(default_factory=list)
    price_selectors: list[str] = field(default_factory=list)
    title_selectors: list[str] = field(default_factory=list)
    seller_selectors: list[str] = field(default_factory=list)
    image_selectors: list[str] = field(default_factory=list)
    location_selectors: list[str] = field(default_factory=list)
    condition_selectors: list[str] = field(default_factory=list)
    max_pages: int = 3
    page_size: int = 24
    timeout_ms: int = 15000
    use_proxy: bool = False
    headless: bool = True
    requires_auth: bool = False


DUBIZZLE_CONFIG = ScraperConfig(
    platform="dubizzle",
    base_url="https://www.dubizzle.com.ae",
    search_url_template="https://www.dubizzle.com.ae/en/{query}/",
    listing_selectors=[
        '[data-testid="listing-card"]',
        '.listing-card',
        '.css-1app33f',
        'article.listing-item',
    ],
    price_selectors=[
        '[data-testid="price"]',
        '.price',
        '[itemprop="price"]',
    ],
    title_selectors=[
        '[data-testid="title"]',
        '.title',
        '[itemprop="name"]',
    ],
    seller_selectors=[
        '[data-testid="seller-name"]',
        '.seller-name',
    ],
    image_selectors=[
        '[data-testid="image"]',
        'img.listing-image',
    ],
    location_selectors=[
        '[data-testid="location"]',
        '.location',
    ],
    max_pages=3,
    timeout_ms=15000,
    use_proxy=True,
)

OLX_CONFIG = ScraperConfig(
    platform="olx",
    base_url="https://www.olx.com.ae",
    search_url_template="https://www.olx.com.ae/ae/{query}/q/{query}/",
    listing_selectors=[
        '[data-testid="listing-card"]',
        '.listing-card',
        'li.css-1app33f',
    ],
    price_selectors=[
        '[data-testid="price"]',
        '.price',
    ],
    title_selectors=[
        '[data-testid="title"]',
        '.title',
    ],
    seller_selectors=[
        '[data-testid="user-name"]',
        '.user-name',
    ],
    image_selectors=[
        '[data-testid="image"]',
        'img',
    ],
    location_selectors=[
        '[data-testid="location"]',
        '.location',
    ],
    max_pages=3,
    timeout_ms=15000,
    use_proxy=True,
)

NOON_CONFIG = ScraperConfig(
    platform="noon",
    base_url="https://www.noon.com",
    search_url_template="https://www.noon.com/ae-en/search/?q={query}",
    listing_selectors=[
        '.productCard-3BkNyu',
        '[data-testid="product-card"]',
        '.css-1app33f',
    ],
    price_selectors=[
        '.priceNOW-3he4lz',
        '[data-testid="price"]',
    ],
    title_selectors=[
        '.productTitle-2k4Lqx',
        '[data-testid="product-title"]',
    ],
    image_selectors=[
        'img.product-image',
    ],
    max_pages=2,
    timeout_ms=15000,
    use_proxy=False,
)

AMAZON_CONFIG = ScraperConfig(
    platform="amazon_ae",
    base_url="https://www.amazon.ae",
    search_url_template="https://www.amazon.ae/s?k={query}",
    listing_selectors=[
        '[data-component-type="s-search-result"]',
        '.s-result-item',
    ],
    price_selectors=[
        '.a-price-whole',
        '.a-offscreen-display',
    ],
    title_selectors=[
        '.a-text-normal',
        'h2 a',
    ],
    image_selectors=[
        '.s-image',
    ],
    max_pages=2,
    timeout_ms=15000,
    use_proxy=False,
)

FACEBOOK_CONFIG = ScraperConfig(
    platform="facebook",
    base_url="https://www.facebook.com",
    search_url="https://www.facebook.com/marketplace/",
    search_url_template="https://www.facebook.com/marketplace/?",
    listing_selector=".x1n2kcrq",
    title_selector=".x1lliihq",
    price_selector=".x1ux0k5l",
    seller_selector=".x78jz5m",
    image_selector="img.x1n2ekr",
    location_selector=".x1e56ztr",
    max_pages=3,
    timeout_ms=20000,
    use_proxy=True,
    headless=True,
    requires_auth=True,
)

PLATFORM_CONFIGS = {
    "dubizzle": DUBIZZLE_CONFIG,
    "olx": OLX_CONFIG,
    "noon": NOON_CONFIG,
    "amazon_ae": AMAZON_CONFIG,
    "facebook": FACEBOOK_CONFIG,
}