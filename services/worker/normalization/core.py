"""Main normalization orchestrator."""

import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from services.worker.normalization.condition import (
    extract_negotiability,
    normalize_condition,
    normalize_listing_condition,
)
from services.worker.normalization.deduplication import deduplicate_listings
from services.worker.normalization.price import normalize_price
from services.worker.normalization.scoring import calculate_listing_score
from services.worker.scrapers.base import RawListing

logger = logging.getLogger(__name__)


class NormalizedListing:
    def __init__(
        self,
        raw_listing: RawListing,
        job_id: Optional[UUID] = None,
    ):
        self.job_id = job_id
        self.raw_listing = raw_listing
        self.platform = raw_listing.platform
        self.listing_url = raw_listing.listing_url
        self.title = raw_listing.title
        self.product_name = self._extract_product_name()
        self.price = None
        self.currency = "AED"
        self.seller_name = raw_listing.seller_name
        self.seller_contact = raw_listing.seller_contact
        self.condition = None
        self.condition_score = 0.5
        self.location_city = self._extract_location()
        self.location_distance = None
        self.posted_days_ago = self._parse_posted_date()
        self.is_negotiable = False
        self.listing_score = 0.0

        self._normalize()

    def _extract_product_name(self) -> str:
        return self.title

    def _extract_location(self) -> Optional[str]:
        location = self.raw_listing.location
        if not location:
            return None

        location_lower = location.lower()
        uae_cities = ["dubai", "abu dhabi", "sharjah", "ajman", "ras al khaimah"]
        for city in uae_cities:
            if city in location_lower:
                return city.title()

        return location

    def _parse_posted_date(self) -> Optional[int]:
        posted = self.raw_listing.posted_date
        if not posted:
            return None

        import re

        days_match = re.search(r"(\d+)\s*day", posted.lower())
        if days_match:
            return int(days_match.group(1))

        hours_match = re.search(r"(\d+)\s*hour", posted.lower())
        if hours_match:
            hours = int(hours_match.group(1))
            return 0 if hours < 24 else 1

        if "today" in posted.lower():
            return 0

        if "yesterday" in posted.lower():
            return 1

        return None

    def _normalize(self):
        price, currency = normalize_price(self.raw_listing.price_raw)
        self.price = price
        self.currency = currency or "AED"

        condition, score = normalize_listing_condition(self.raw_listing)
        self.condition = condition
        self.condition_score = score

        self.is_negotiable = extract_negotiability(
            self.raw_listing.title,
            self.raw_listing.description,
        )

    def calculate_score(
        self,
        target_price: float,
        max_price: float,
        radius_km: float = 30.0,
    ) -> float:
        self.listing_score = calculate_listing_score(
            price=self.price or 0,
            min_price=target_price,
            max_price=max_price,
            condition_score=self.condition_score,
            posted_days_ago=self.posted_days_ago,
            is_negotiable=self.is_negotiable,
            distance_km=self.location_distance,
            radius_km=radius_km,
        )
        return self.listing_score

    def to_dict(self) -> dict:
        return {
            "job_id": str(self.job_id) if self.job_id else None,
            "product_name": self.product_name,
            "price": self.price,
            "currency": self.currency,
            "platform": self.platform,
            "listing_url": self.listing_url,
            "seller_name": self.seller_name,
            "seller_contact": self.seller_contact,
            "condition": self.condition,
            "condition_score": self.condition_score,
            "location_city": self.location_city,
            "location_distance": self.location_distance,
            "posted_days_ago": self.posted_days_ago,
            "is_negotiable": self.is_negotiable,
            "listing_score": self.listing_score,
        }


async def normalize_raw_listings(
    raw_listings: list[RawListing],
    target_price: float,
    max_price: float,
    job_id: Optional[UUID] = None,
    radius_km: float = 30.0,
    top_n: int = 10,
) -> list[NormalizedListing]:
    logger.info(f"Normalizing {len(raw_listings)} raw listings")

    unique_listings = deduplicate_listings(raw_listings)
    logger.info(f"After deduplication: {len(unique_listings)} unique listings")

    normalized = []
    for raw in unique_listings:
        try:
            norm_listing = NormalizedListing(raw, job_id=job_id)
            norm_listing.calculate_score(target_price, max_price, radius_km)
            normalized.append(norm_listing)
        except Exception as e:
            logger.warning(f"Failed to normalize listing {raw.listing_url}: {e}")
            continue

    normalized.sort(key=lambda x: x.listing_score, reverse=True)

    top_listings = normalized[:top_n]
    logger.info(f"Selected top {len(top_listings)} listings by score")

    return top_listings