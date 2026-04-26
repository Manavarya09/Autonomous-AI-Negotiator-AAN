"""Raw listing data structure."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class RawListing:
    platform: str
    listing_url: str
    title: str
    price_raw: Optional[str] = None
    currency_raw: Optional[str] = None
    seller_name: Optional[str] = None
    seller_contact: Optional[str] = None
    seller_profile_url: Optional[str] = None
    condition_raw: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    posted_date: Optional[str] = None
    image_urls: list[str] = field(default_factory=list)
    listing_id: Optional[str] = None
    scraped_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "platform": self.platform,
            "listing_url": self.listing_url,
            "title": self.title,
            "price_raw": self.price_raw,
            "currency_raw": self.currency_raw,
            "seller_name": self.seller_name,
            "seller_contact": self.seller_contact,
            "seller_profile_url": self.seller_profile_url,
            "condition_raw": self.condition_raw,
            "description": self.description,
            "location": self.location,
            "posted_date": self.posted_date,
            "image_urls": self.image_urls,
            "listing_id": self.listing_id,
            "scraped_at": self.scraped_at.isoformat(),
        }