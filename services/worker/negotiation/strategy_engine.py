"""Adaptive negotiation strategy engine with game theory."""

import logging
import random
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class StrategyType(str, Enum):
    LOW_ANCHOR = "low_anchor"
    FAIR_VALUE = "fair_value"
    BUNDLE = "bundle"
    URGENCY = "urgency"
    COMPETITIVE = "competitive"
    GRADUAL = "gradual"


class SellerPersona(str, Enum):
    RIGID = "rigid"
    FLEXIBLE = "flexible"
    EMOTIONAL = "emotional"
    DATA_DRIVEN = "data_driven"
    HAGGLE = "haggle"
    UNKNOWN = "unknown"


class ConcessionType(str, Enum):
    LINEAR = "linear"
    SHRINKING = "shrinking"
    STRATEGIC = "strategic"
    ACCELERATING = "accelerating"


@dataclass
class StrategyConfig:
    strategy: StrategyType
    anchor_pct: float = 0.70
    target_pct: float = 0.85
    max_rounds: int = 5
    min_concession: float = 0.02
    max_concession: float = 0.10


@dataclass
class ConcessionPlan:
    type: ConcessionType
    start_pct: float
    decline_rate: float = 0.95
    rounds: list[float] = field(default_factory=list)
    
    def get_offer(self, round_num: int, list_price: float, target: float) -> float:
        """Calculate offer for given round."""
        if round_num >= len(self.rounds):
            round_num = len(self.rounds) - 1
        
        concession_pct = self.rounds[round_num]
        offer = list_price - (list_price - target) * concession_pct
        
        return round(offer, -1)
    
    @classmethod
    def linear(cls, start: float = 0.10) -> "ConcessionPlan":
        """Linear concession: equal steps each round."""
        rounds = []
        for i in range(5):
            rounds.append(start * (1 - i * 0.15))
        return cls(type=ConcessionType.LINEAR, start_pct=start, rounds=rounds)
    
    @classmethod
    def shrinking(cls, start: float = 0.15) -> "ConcessionPlan":
        """Shrinking concession: larger first, smaller later."""
        rounds = [start * (0.9 ** i) for i in range(5)]
        return cls(type=ConcessionType.SHRINKING, start_pct=start, rounds=rounds)
    
    @classmethod
    def strategic(cls, target_pct: float = 0.85) -> "ConcessionPlan":
        """Strategic: aim for target quickly."""
        rounds = [
            0.30, 0.20, 0.12, 0.06, 0.02
        ]
        return cls(type=ConcessionType.STRATEGIC, start_pct=0.30, rounds=rounds)


class StrategyEngine:
    """Adaptive strategy engine with game theory."""
    
    def __init__(self):
        self.strategy_history: list[dict] = []
    
    def detect_persona(
        self,
        seller_name: str,
        initial_response: Optional[str] = None,
        price_gap: float = 0.0,
    ) -> SellerPersona:
        """Detect seller persona from behavior."""
        if not initial_response:
            return SellerPersona.UNKNOWN
        
        response_lower = initial_response.lower()
        
        flexible_kw = ["ok", "decent", "reasonable", "fair", "nego"]
        rigid_kw = ["firm", "fixed", "final", "best price", "already low"]
        emotional_kw = ["want", "need", "urgent", "selling", "wife", "moving"]
        data_kw = ["market", "check", "compare", "value"]
        haggle_kw = ["make it", "give me", "how bout", "counter"]
        
        scores = {SellerPersona.FLEXIBLE: 0, SellerPersona.RIGID: 0}
        
        for kw in flexible_kw:
            if kw in response_lower:
                scores[SellerPersona.FLEXIBLE] += 1
        for kw in rigid_kw:
            if kw in response_lower:
                scores[SellerPersona.RIGID] += 1
        
        if price_gap > 0.30:
            return SellerPersona.RIGID
        elif price_gap < 0.10:
            return SellerPersona.FLEXIBLE
        
        max_score = max(scores.values())
        for persona, score in scores.items():
            if score == max_score and score > 0:
                return persona
        
        return SellerPersona.UNKNOWN
    
    def select_strategy(
        self,
        persona: SellerPersona,
        urgency: str = "normal",
        has_competitors: bool = False,
    ) -> StrategyConfig:
        """Select optimal strategy based on context."""
        
        if persona == SellerPersona.RIGID:
            return StrategyConfig(
                strategy=StrategyType.FAIR_VALUE,
                anchor_pct=0.85,
                target_pct=0.95,
                max_rounds=3,
            )
        
        elif persona == SellerPersona.FLEXIBLE:
            return StrategyConfig(
                strategy=StrategyType.GRADUAL,
                anchor_pct=0.80,
                target_pct=0.90,
                max_rounds=4,
            )
        
        elif persona == SellerPersona.HAGGLE:
            return StrategyConfig(
                strategy=StrategyType.COMPETITIVE,
                anchor_pct=0.65,
                target_pct=0.85,
                max_rounds=5,
            )
        
        elif has_competitors:
            return StrategyConfig(
                strategy=StrategyType.URGENCY,
                anchor_pct=0.75,
                target_pct=0.90,
                max_rounds=3,
            )
        
        return StrategyConfig(
            strategy=StrategyType.FAIR_VALUE,
            anchor_pct=0.75,
            target_pct=0.85,
            max_rounds=5,
        )
    
    def calculate_counter_offer(
        self,
        list_price: float,
        target_price: float,
        current_round: int,
        max_rounds: int,
        strategy: StrategyType,
        seller_accepted: bool = False,
    ) -> float:
        """Calculate game-theoretic counter offer."""
        
        if seller_accepted:
            return list_price
        
        remaining_rounds = max_rounds - current_round
        if remaining_rounds <= 0:
            return target_price
        
        price_range = list_price - target_price
        progress_pct = current_round / max_rounds
        
        if strategy == StrategyType.LOW_ANCHOR:
            anchor = 0.60
        elif strategy == StrategyType.FAIR_VALUE:
            anchor = 0.75
        elif strategy == StrategyType.COMPETITIVE:
            anchor = 0.65
        elif strategy == StrategyType.URGENCY:
            anchor = 0.80
        else:
            anchor = 0.70
        
        offer_pct = anchor - (anchor - 0.85) * progress_pct
        
        offer = target_price + price_range * (1 - offer_pct)
        offer = max(offer, target_price)
        
        return round(offer, -1)
    
    def should_accept(
        self,
        offer: float,
        target: float,
        max_: float,
        rounds_left: int,
    ) -> bool:
        """Determine if current offer meets threshold."""
        
        if offer <= target:
            return True
        
        if rounds_left <= 1:
            threshold = target + (max_ - target) * 0.05
            return offer <= threshold
        
        return False


strategy_engine = StrategyEngine()