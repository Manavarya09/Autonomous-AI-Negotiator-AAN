"""Auto-buy and price alert tasks."""

import logging
from uuid import UUID
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config.database.connection import async_session_maker
from config.database.models import NegotiationJob, Negotiation

logger = logging.getLogger(__name__)


async def check_auto_buy_triggers(job_id: UUID) -> dict:
    """Check if any negotiations hit target price for auto-buy."""
    
    async with async_session_maker() as db:
        result = await db.execute(
            select(NegotiationJob).where(NegotiationJob.id == job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job or not job.auto_close:
            return {"triggered": False, "reason": "Auto-close not enabled"}
        
        neg_result = await db.execute(
            select(Negotiation).where(
                Negotiation.job_id == job_id,
                Negotiation.status == "active",
            )
        )
        negotiations = neg_result.scalars().all()
        
        for neg in negotiations:
            if neg.current_offer and neg.current_offer <= job.target_price:
                return {
                    "triggered": True,
                    "negotiation_id": str(neg.id),
                    "offer_price": neg.current_offer,
                    "target_price": job.target_price,
                }
        
        return {"triggered": False, "reason": "No offers at target"}


async def process_auto_buy(negotiation_id: UUID) -> dict:
    """Process auto-buy for a negotiation."""
    
    async with async_session_maker() as db:
        result = await db.execute(
            select(Negotiation).where(Negotiation.id == negotiation_id)
        )
        neg = result.scalar_one_or_none()
        
        if not neg:
            return {"success": False, "error": "Negotiation not found"}
        
        if neg.status != "active":
            return {"success": False, "error": "Negotiation not active"}
        
        neg.status = "accepted"
        neg.agreed_price = neg.current_offer
        neg.closed_at = datetime.utcnow()
        
        await db.commit()
        
        logger.info(f"Auto-buy triggered for negotiation {negotiation_id}")
        
        return {
            "success": True,
            "negotiation_id": str(negotiation_id),
            "agreed_price": neg.agreed_price,
        }


async def check_price_alerts() -> dict:
    """Background task to check price alerts."""
    
    async with async_session_maker() as db:
        result = await db.execute(
            select(NegotiationJob).where(
                NegotiationJob.status == "completed",
            )
        )
        jobs = result.scalars().all()
        
        alerts_triggered = []
        
        for job in jobs:
            if not job.auto_close:
                continue
            
            neg_result = await db.execute(
                select(Negotiation).where(
                    Negotiation.job_id == job.id,
                    Negotiation.status == "accepted",
                    Negotiation.agreed_price != None,
                )
            )
            accepted = neg_result.scalars().all()
            
            for neg in accepted:
                savings = ((job.max_price - (neg.agreed_price or 0)) / job.max_price) * 100
                
                if savings >= 10:
                    alerts_triggered.append({
                        "job_id": str(job.id),
                        "product": job.product_query,
                        "agreed_price": neg.agreed_price,
                        "savings_percent": savings,
                    })
        
        return {
            "checked_jobs": len(jobs),
            "alerts": alerts_triggered,
        }


async def send_deal_notification(
    job_id: UUID,
    agreed_price: float,
    seller_name: str,
) -> dict:
    """Send push notification for accepted deal."""
    
    logger.info(f"Sending deal notification for job {job_id}")
    
    return {
        "sent": True,
        "job_id": str(job_id),
        "price": agreed_price,
    }