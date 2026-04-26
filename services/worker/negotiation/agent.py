"""Agent state management for negotiation threads."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID


class SellerType(str, Enum):
    RIGID = "rigid"
    FLEXIBLE = "flexible"
    EMOTIONAL = "emotional"
    DATA_DRIVEN = "data_driven"
    UNKNOWN = "unknown"


class NegotiationStatus(str, Enum):
    ACTIVE = "active"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    STALLED = "stalled"
    EXPIRED = "expired"


class NegotiationStrategy(str, Enum):
    LOW_ANCHOR = "low_anchor"
    FAIR_VALUE = "fair_value"
    BUNDLE = "bundle"
    URGENCY = "urgency"
    COMPETITIVE = "competitive"


@dataclass
class AgentState:
    job_id: UUID
    listing_id: UUID
    seller_name: str
    seller_contact: str
    platform: str

    list_price: float
    target_price: float
    max_price: float
    current_offer: Optional[float] = None
    agreed_price: Optional[float] = None

    strategy: NegotiationStrategy = NegotiationStrategy.FAIR_VALUE
    strategy_history: list[str] = field(default_factory=list)
    seller_type: SellerType = SellerType.UNKNOWN

    round_count: int = 0
    max_rounds: int = 5

    status: NegotiationStatus = NegotiationStatus.ACTIVE
    last_action_at: datetime = field(default_factory=datetime.utcnow)
    started_at: datetime = field(default_factory=datetime.utcnow)

    def is_terminal(self) -> bool:
        return self.status in (
            NegotiationStatus.ACCEPTED,
            NegotiationStatus.REJECTED,
            NegotiationStatus.STALLED,
            NegotiationStatus.EXPIRED,
        )

    def get_counter_offer(self) -> float:
        if self.current_offer is None:
            return self._get_initial_offer()

        increment = (self.max_price - self.current_offer) / (self.max_rounds - self.round_count)
        new_offer = self.current_offer + increment

        return min(new_offer, self.max_price)

    def _get_initial_offer(self) -> float:
        if self.strategy == NegotiationStrategy.LOW_ANCHOR:
            return self.target_price * 0.85
        elif self.strategy == NegotiationStrategy.FAIR_VALUE:
            return self.target_price * 0.95
        else:
            return self.target_price

    def to_dict(self) -> dict:
        return {
            "job_id": str(self.job_id),
            "listing_id": str(self.listing_id),
            "seller_name": self.seller_name,
            "seller_contact": self.seller_contact,
            "platform": self.platform,
            "list_price": self.list_price,
            "target_price": self.target_price,
            "max_price": self.max_price,
            "current_offer": self.current_offer,
            "agreed_price": self.agreed_price,
            "strategy": self.strategy.value,
            "seller_type": self.seller_type.value,
            "round_count": self.round_count,
            "max_rounds": self.max_rounds,
            "status": self.status.value,
        }


def classify_seller(
    title: str,
    description: Optional[str],
    price: float,
    target_price: float,
) -> SellerType:
    text = f"{title} {description or ''}".lower()

    if target_price * 0.95 >= price:
        return SellerType.RIGID

    negotiables = ["ono", "or near offer", "negotiable", "serious buyer", "quick sale"]
    if any(kw in text for kw in negotiables):
        return SellerType.FLEXIBLE

    personal_words = ["moving", "upgrading", "first phone", "loving", "sad to let go"]
    if any(kw in text for kw in personal_words):
        return SellerType.EMOTIONAL

    data_indicators = ["k clicks", "km", "box included", "receipt", "warranty"]
    if any(kw in text for kw in data_indicators):
        return SellerType.DATA_DRIVEN

    return SellerType.UNKNOWN


def select_strategy(seller_type: SellerType, urgency: str = "normal") -> NegotiationStrategy:
    if urgency in ("high", "critical"):
        return NegotiationStrategy.FAIR_VALUE

    strategy_map = {
        SellerType.RIGID: NegotiationStrategy.BUNDLE,
        SellerType.FLEXIBLE: NegotiationStrategy.LOW_ANCHOR,
        SellerType.EMOTIONAL: NegotiationStrategy.URGENCY,
        SellerType.DATA_DRIVEN: NegotiationStrategy.FAIR_VALUE,
        SellerType.UNKNOWN: NegotiationStrategy.FAIR_VALUE,
    }

    return strategy_map.get(seller_type, NegotiationStrategy.FAIR_VALUE)