"""Learning system for strategy optimization."""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config.database.connection import async_session_maker
from config.database.models import StrategyOutcome, SellerProfile

logger = logging.getLogger(__name__)


@dataclass
class StrategyResult:
    negotiation_id: UUID
    strategy_used: str
    seller_type: str
    list_price: float
    agreed_price: float
    saved_pct: float
    rounds: int
    result: str


@dataclass
class StrategyStats:
    strategy: str
    total_attempts: int
    successes: int
    success_rate: float
    avg_savings: float
    avg_rounds: float


class LearningSystem:
    """Track and optimize negotiation strategies."""
    
    def __init__(self):
        self.min_samples = 3
    
    async def record_outcome(
        self,
        result: StrategyResult,
        db: AsyncSession,
    ) -> None:
        """Record negotiation outcome for learning."""
        
        savings_pct = ((result.list_price - result.agreed_price) / result.list_price) * 100
        
        outcome = StrategyOutcome(
            negotiation_id=result.negotiation_id,
            strategy_used=result.strategy_used,
            seller_type=result.seller_type,
            list_price=result.list_price,
            agreed_price=result.agreed_price,
            savings_pct=savings_pct,
            rounds_taken=result.rounds,
            result=result.result,
        )
        
        db.add(outcome)
        await db.commit()
        
        logger.info(f"Recorded outcome: {result.strategy_used} -> {result.result}")
    
    async def get_strategy_stats(
        self,
        strategy: str,
        db: AsyncSession,
    ) -> Optional[StrategyStats]:
        """Get stats for a specific strategy."""
        
        result = await db.execute(
            select(StrategyOutcome).where(
                StrategyOutcome.strategy_used == strategy
            )
        )
        outcomes = result.scalars().all()
        
        if len(outcomes) < self.min_samples:
            return None
        
        successes = [o for o in outcomes if o.result == "accepted"]
        total_savings = sum(o.savings_pct or 0 for o in outcomes)
        total_rounds = sum(o.rounds_taken or 0 for o in outcomes)
        
        return StrategyStats(
            strategy=strategy,
            total_attempts=len(outcomes),
            successes=len(successes),
            success_rate=len(successes) / len(outcomes),
            avg_savings=total_savings / len(outcomes),
            avg_rounds=total_rounds / len(outcomes),
        )
    
    async def recommend_strategy(
        self,
        seller_type: str,
        db: AsyncSession,
    ) -> str:
        """Recommend best strategy based on history."""
        
        strategies = ["low_anchor", "fair_value", "competitive", "gradual"]
        best_strategy = "fair_value"
        best_rate = 0.0
        
        for strategy in strategies:
            result = await db.execute(
                select(StrategyOutcome).where(
                    StrategyOutcome.strategy_used == strategy,
                    StrategyOutcome.seller_type == seller_type,
                )
            )
            outcomes = result.scalars().all()
            
            if len(outcomes) < self.min_samples:
                continue
            
            successes = [o for o in outcomes if o.result == "accepted"]
            rate = len(successes) / len(outcomes)
            
            if rate > best_rate:
                best_rate = rate
                best_strategy = strategy
        
        logger.info(f"Recommended strategy: {best_strategy} ({best_rate*100:.0f}% success)")
        return best_strategy
    
    async def update_seller_profile(
        self,
        platform: str,
        platform_user_id: str,
        acceptance_rate: float,
        avg_response_hours: float,
        db: AsyncSession,
    ) -> None:
        """Update seller profile with new data."""
        
        result = await db.execute(
            select(SellerProfile).where(
                SellerProfile.platform == platform,
                SellerProfile.platform_user_id == platform_user_id,
            )
        )
        profile = result.scalar_one_or_none()
        
        if profile:
            profile.negotiations_count += 1
            
            if profile.acceptance_rate:
                profile.acceptance_rate = (
                    profile.acceptance_rate * 0.7 + acceptance_rate * 0.3
                )
            else:
                profile.acceptance_rate = acceptance_rate
            
            if profile.avg_response_hours:
                profile.avg_response_hours = (
                    profile.avg_response_hours * 0.7 + avg_response_hours * 0.3
                )
            else:
                profile.avg_response_hours = avg_response_hours
        else:
            profile = SellerProfile(
                platform=platform,
                platform_user_id=platform_user_id,
                trust_score=0.5,
                avg_response_hours=avg_response_hours,
                negotiations_count=1,
                acceptance_rate=acceptance_rate,
            )
            db.add(profile)
        
        profile.last_seen = datetime.utcnow()
        await db.commit()


learning_system = LearningSystem()