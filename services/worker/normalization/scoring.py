"""Listing score calculation based on PRD formula."""

from typing import Optional


OFFSET_MIN_PRICE = 0.4
OFFSET_CONDITION = 0.2
OFFSET_RECENCY = 0.15
OFFSET_NEGOTIABILITY = 0.15
OFFSET_LOCATION = 0.1


def calculate_price_score(
    price: float,
    min_price: float,
    max_price: float,
) -> float:
    if max_price <= min_price:
        return 0.5

    if price <= min_price:
        return 1.0

    if price >= max_price:
        return 0.0

    return 1 - ((price - min_price) / (max_price - min_price))


def calculate_recency_score(posted_days_ago: Optional[int]) -> float:
    if posted_days_ago is None:
        return 0.5

    if posted_days_ago <= 0:
        return 1.0

    if posted_days_ago >= 30:
        return 0.0

    return max(0, 1 - (posted_days_ago / 30))


def calculate_location_score(
    distance_km: Optional[float],
    radius_km: float,
) -> float:
    if distance_km is None or radius_km <= 0:
        return 0.5

    if distance_km <= 0:
        return 1.0

    if distance_km >= radius_km:
        return 0.0

    return max(0, 1 - (distance_km / radius_km))


def calculate_listing_score(
    price: float,
    min_price: float,
    max_price: float,
    condition_score: float,
    posted_days_ago: Optional[int],
    is_negotiable: bool,
    distance_km: Optional[float],
    radius_km: float = 30.0,
) -> float:
    price_score = calculate_price_score(price, min_price, max_price)

    recency_score = calculate_recency_score(posted_days_ago)

    negotiability_score = 1.0 if is_negotiable else 0.5

    location_score = calculate_location_score(distance_km, radius_km)

    score = (
        OFFSET_MIN_PRICE * price_score
        + OFFSET_CONDITION * condition_score
        + OFFSET_RECENCY * recency_score
        + OFFSET_NEGOTIABILITY * negotiability_score
        + OFFSET_LOCATION * location_score
    )

    return round(score, 3)


def rank_listings(
    listings: list[dict],
    target_price: float,
    max_price: float,
    limit: int = 10,
) -> list[dict]:
    for listing in listings:
        listing["listing_score"] = calculate_listing_score(
            price=listing.get("price", 0),
            min_price=target_price,
            max_price=max_price,
            condition_score=listing.get("condition_score", 0.5),
            posted_days_ago=listing.get("posted_days_ago"),
            is_negotiable=listing.get("is_negotiable", True),
            distance_km=listing.get("location_distance"),
            radius_km=listing.get("location_radius", 30),
        )

    sorted_listings = sorted(
        listings,
        key=lambda x: x.get("listing_score", 0),
        reverse=True,
    )

    return sorted_listings[:limit]