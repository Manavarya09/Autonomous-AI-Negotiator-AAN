"""Deduplication utilities for listings."""

import difflib
from typing import Optional

from services.worker.normalization.price import normalize_price
from services.worker.scrapers.base import RawListing

LEVENSHTEIN_THRESHOLD = 0.9


def levenshtein_similarity(s1: str, s2: str) -> float:
    if not s1 or not s2:
        return 0.0

    if s1 == s2:
        return 1.0

    ratio = difflib.SequenceMatcher(None, s1.lower(), s2.lower()).ratio()
    return ratio


def is_duplicate_title(title1: str, title2: str) -> bool:
    similarity = levenshtein_similarity(title1, title2)
    return similarity >= LEVENSHTEIN_THRESHOLD


def is_duplicate_price(price1: Optional[float], price2: Optional[float]) -> bool:
    if price1 is None or price2 is None:
        return False

    return abs(price1 - price2) < 1


def is_duplicate_seller(seller1: Optional[str], seller2: Optional[str]) -> bool:
    if not seller1 or not seller2:
        return False

    similarity = levenshtein_similarity(seller1, seller2)
    return similarity >= 0.8


def is_duplicate_listing(
    listing1: RawListing,
    listing2: RawListing,
    same_platform: bool = True,
) -> bool:
    if same_platform:
        if listing1.listing_url and listing2.listing_url:
            if listing1.listing_url == listing2.listing_url:
                return True

    if is_duplicate_title(listing1.title, listing2.title):
        price1, _ = normalize_price(listing1.price_raw)
        price2, _ = normalize_price(listing2.price_raw)
        if price1 and price2:
            if is_duplicate_price(price1, price2):
                if is_duplicate_seller(listing1.seller_name, listing2.seller_name):
                    return True

        if listing1.seller_name and listing2.seller_name:
            if is_duplicate_seller(listing1.seller_name, listing2.seller_name):
                return True

    return False


def deduplicate_listings(listings: list[RawListing]) -> list[RawListing]:
    if not listings:
        return []

    unique_listings = []
    seen_signatures = set()

    for listing in listings:
        signature = f"{listing.title.lower().strip()}|{listing.price_raw or ''}|{listing.seller_name or ''}"

        if signature in seen_signatures:
            continue

        is_dup = False
        for existing in unique_listings:
            if is_duplicate_listing(listing, existing, same_platform=False):
                is_dup = True
                break

        if not is_dup:
            unique_listings.append(listing)
            seen_signatures.add(signature)

    return unique_listings