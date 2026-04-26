"""Condition normalization from raw text."""

from typing import Optional

from services.worker.scrapers.base import RawListing

CONDITION_MAP = {
    "new": ("new", 1.0),
    "brand new": ("new", 1.0),
    "sealed": ("new", 1.0),
    "sealed box": ("new", 1.0),
    "unopened": ("new", 1.0),
    "like new": ("like_new", 0.9),
    "like_new": ("like_new", 0.9),
    "used once": ("like_new", 0.9),
    "excellent": ("excellent", 0.8),
    "excellent condition": ("excellent", 0.8),
    "mint": ("excellent", 0.8),
    "very good": ("good", 0.75),
    "good": ("good", 0.7),
    "good condition": ("good", 0.7),
    "working": ("used", 0.6),
    "used": ("used", 0.6),
    "fair": ("used", 0.5),
    "poor": ("parts", 0.2),
    "for parts": ("parts", 0.2),
    "parts": ("parts", 0.2),
    "not working": ("parts", 0.1),
    "damaged": ("parts", 0.1),
    "for repair": ("parts", 0.1),
}


def normalize_condition(condition_raw: Optional[str]) -> tuple[Optional[str], float]:
    if not condition_raw:
        return None, 0.5

    condition_lower = condition_raw.lower().strip()

    if condition_lower in CONDITION_MAP:
        return CONDITION_MAP[condition_lower]

    for key, (label, score) in CONDITION_MAP.items():
        if key in condition_lower:
            return label, score

    return None, 0.5


def extract_negotiability(title: str, description: Optional[str]) -> bool:
    text = f"{title} {description or ''}".lower()

    negotiability_keywords = [
        "ono",
        "or near offer",
        "negotiable",
        "firm",
        "best price",
        "serious buyer",
        "quick sale",
        "flexible",
    ]

    for keyword in negotiability_keywords:
        if keyword in text:
            return True

    return False


def normalize_listing_condition(listing: RawListing) -> tuple[Optional[str], float]:
    condition_source = listing.condition_raw or listing.description or ""

    return normalize_condition(condition_source)