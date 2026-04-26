"""Decision Engine for scoring and closing deals."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


OFFSET_PRICE = 0.45
OFFSET_TRUST = 0.25
OFFSET_TIME = 0.15
OFFSET_ROUNDS = 0.15


def calculate_deal_score(
    agreed_price: float,
    target_price: float,
    max_price: float,
    trust_score: float,
    time_to_close_hours: float,
    rounds_taken: int,
    max_rounds: int,
) -> float:
    if max_price <= target_price:
        price_score = 1.0
    else:
        price_score = 1 - ((agreed_price - target_price) / (max_price - target_price))

    time_score = max(0, 1 - min(1, time_to_close_hours / 72))

    rounds_score = 1 - (rounds_taken / max_rounds) if max_rounds > 0 else 0.5

    score = (
        OFFSET_PRICE * price_score
        + OFFSET_TRUST * trust_score
        + OFFSET_TIME * time_score
        + OFFSET_ROUNDS * rounds_score
    )

    return round(score, 3)


def should_auto_close(
    deal_score: float,
    min_score_threshold: float = 0.75,
) -> bool:
    return deal_score >= min_score_threshold


def calculate_time_to_close(started_at: datetime, closed_at: Optional[datetime] = None) -> float:
    if closed_at is None:
        closed_at = datetime.utcnow()
    
    delta = closed_at - started_at
    return delta.total_value / 3600


@dataclass
class DealResult:
    listing_id: UUID
    product_name: str
    agreed_price: float
    currency: str
    seller_name: str
    platform: str
    condition: str
    score: float
    negotiation_rounds: int
    time_to_close_hours: float

    def to_dict(self) -> dict:
        return {
            "listing_id": str(self.listing_id),
            "product_name": self.product_name,
            "agreed_price": self.agreed_price,
            "currency": self.currency,
            "seller_name": self.seller_name,
            "platform": self.platform,
            "condition": self.condition,
            "score": self.score,
            "negotiation_rounds": self.negotiation_rounds,
            "time_to_close_hours": round(self.time_to_close_hours, 1),
        }


def rank_deals(
    deals: list[DealResult],
) -> list[DealResult]:
    return sorted(deals, key=lambda x: x.score, reverse=True)


def select_best_deal(
    deals: list[DealResult],
    min_threshold: float = 0.50,
) -> Optional[DealResult]:
    valid_deals = [d for d in deals if d.score >= min_threshold]
    
    if not valid_deals:
        return None
    
    return max(valid_deals, key=lambda x: x.score)