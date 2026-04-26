"""Main negotiation loop - orchestrates full autonomous negotiation."""

import asyncio
import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from config.database.connection import async_session_maker
from config.database.models import NegotiationJob, NormalizedListing, Negotiation as NegotiationModel
from sqlalchemy import select

from services.worker.negotiation.agent import (
    AgentState,
    classify_seller,
    select_strategy,
    NegotiationStatus,
    NegotiationStrategy,
)
from services.worker.negotiation.decision import (
    calculate_deal_score,
    should_auto_close,
    select_best_deal,
    DealResult,
)
from services.worker.negotiation.email import send_negotiation_email
from services.worker.negotiation.intent_parser import parse_message
from services.worker.negotiation.llm_messages import (
    generate_intro_message,
    generate_counter_message,
    generate_accept_message,
    generate_reject_message,
)
from services.worker.tasks.scraper import scrape_all_platforms
from services.worker.normalization.core import normalize_raw_listings
from services.worker.scrapers.base import RawListing

logger = logging.getLogger(__name__)


async def run_full_negotiation_cycle(
    job_id: UUID,
    auto_close: bool = False,
    max_parallel: int = 10,
):
    """Complete autonomous negotiation cycle from discovery to decision."""
    
    logger.info(f"Starting negotiation cycle for job: {job_id}")
    
    async with async_session_maker() as db:
        result = await db.execute(
            select(NegotiationJob).where(NegotiationJob.id == job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            logger.error(f"Job not found: {job_id}")
            return {"error": "Job not found"}
        
        job.status = "running"
        await db.commit()
        
        platforms = job.config.get("platforms", ["dubizzle", "olx"]) if job.config else ["dubizzle", "olx"]
        
        raw_listings_data = await scrape_all_platforms(
            query=job.product_query,
            platforms=platforms,
            location=job.location_city,
        )
        
        for listing_data in raw_listings_data:
            raw = RawListing(**listing_data)
            from config.database.models import RawListing
            db_listing = RawListing(
                job_id=job_id,
                platform=raw.platform,
                listing_url=raw.listing_url,
                title=raw.title,
                price_raw=raw.price_raw,
                seller_name=raw.seller_name,
                seller_contact=raw.seller_contact,
                condition_raw=raw.condition_raw,
            )
            db.add(db_listing)
        
        await db.commit()
        
        from sqlalchemy import select as sql_select
        result = await db.execute(sql_select(NormalizedListing).where(NormalizedListing.job_id == job_id))
        all_normals = result.scalars().all()
        
        raw_objs = [
            RawListing(
                platform=r.platform,
                listing_url=r.listing_url,
                title=r.title or "",
                price_raw=str(r.price) if r.price else "",
                seller_name=r.seller_name,
                seller_contact=r.seller_contact,
                condition_raw=r.condition,
            )
            for r in all_normals
        ]
        
        normalized = await normalize_raw_listings(
            raw_listings=raw_objs,
            target_price=job.target_price,
            max_price=job.max_price,
            job_id=job_id,
            top_n=max_parallel,
        )
        
        for norm in normalized:
            if not norm.listing_url:
                continue
            
            agent = await start_negotiation_thread(
                db=db,
                job_id=job_id,
                listing=norm,
                target_price=job.target_price,
                max_price=job.max_price,
            )
            
            if agent:
                await asyncio.sleep(2)
        
        await db.commit()
        
        job.status = "completed"
        await db.commit()
        
        return {
            "job_id": str(job_id),
            "status": "completed",
            "negotiations_started": len(normalized),
        }


async def start_negotiation_thread(
    db,
    job_id: UUID,
    listing,
    target_price: float,
    max_price: float,
) -> Optional[AgentState]:
    """Start a single negotiation thread with a seller."""
    
    from services.worker.negotiation.email import send_negotiation_email
    from services.worker.normalization.price import normalize_price
    
    title = listing.title or "Item"
    price, _ = normalize_price(listing.price_raw if hasattr(listing, 'price_raw') else str(listing.price))
    
    if not price:
        return None
    
    seller_name = listing.seller_name or "Seller"
    seller_contact = listing.seller_contact
    
    if not seller_contact:
        return None
    
    seller_type = classify_seller(
        title=title,
        description=listing.description if hasattr(listing, 'description') else None,
        price=price,
        target_price=target_price,
    )
    
    strategy = select_strategy(seller_type, urgency="normal")
    
    agent = AgentState(
        job_id=job_id,
        listing_id=listing.id,
        seller_name=seller_name,
        seller_contact=seller_contact,
        platform=listing.platform,
        list_price=price,
        target_price=target_price,
        max_price=max_price,
        strategy=strategy,
        seller_type=seller_type,
    )
    
    intro_msg = await generate_intro_message(
        product=title,
        seller_name=seller_name,
        target_price=target_price,
        max_price=max_price,
        strategy=strategy.value,
    )
    
    sent = await send_negotiation_email(
        to=seller_contact,
        subject=f"Re: {title}",
        message=intro_msg,
    )
    
    if sent:
        agent.current_offer = agent.get_counter_offer()
        agent.round_count = 1
        
        neg_model = NegotiationModel(
            job_id=job_id,
            listing_id=listing.id,
            seller_name=seller_name,
            seller_contact=seller_contact,
            platform=listing.platform,
            strategy=strategy.value,
            seller_type=seller_type.value,
            list_price=price,
            target_price=target_price,
            max_price=max_price,
            current_offer=agent.current_offer,
            status="active",
            round_count=agent.round_count,
        )
        db.add(neg_model)
        
        logger.info(f"Started negotiation with {seller_name} for {title}")
        
    return agent


async def process_seller_reply(
    db,
    negotiation_id: UUID,
    seller_message: str,
) -> dict:
    """Process an incoming seller reply and generate response."""
    
    result = await db.execute(
        select(NegotiationModel).where(NegotiationModel.id == negotiation_id)
    )
    neg = result.scalar_one_or_none()
    
    if not neg:
        return {"error": "Negotiation not found"}
    
    parsed = await parse_message(seller_message)
    
    intent = parsed.get("intent")
    extracted_price = parsed.get("extracted_price")
    
    if intent == "accept":
        neg.agreed_price = extracted_price or neg.current_offer
        neg.status = "accepted"
        neg.closed_at = datetime.utcnow()
        
        accept_msg = await generate_accept_message(
            product="Item",
            agreed_price=neg.agreed_price,
            seller_name=neg.seller_name,
        )
        
        await send_negotiation_email(
            to=neg.seller_contact,
            subject="Confirmed - Purchase",
            message=accept_msg,
        )
        
        await db.commit()
        return {"status": "accepted", "agreed_price": neg.agreed_price}
    
    elif intent == "reject":
        neg.status = "rejected"
        neg.closed_at = datetime.utcnow()
        
        reject_msg = await generate_reject_message(
            product="Item",
            max_price=neg.max_price,
            seller_price=extracted_price or neg.list_price,
            seller_name=neg.seller_name,
        )
        
        await send_negotiation_email(
            to=neg.seller_contact,
            subject="Thanks",
            message=reject_msg,
        )
        
        await db.commit()
        return {"status": "rejected"}
    
    elif intent == "counter" or extracted_price:
        counter_offer = extracted_price if extracted_price else neg.target_price * 0.95
        
        counter_msg = await generate_counter_message(
            product="Item",
            list_price=neg.list_price,
            target_price=neg.target_price,
            max_price=neg.max_price,
            current_offer=neg.current_offer or 0,
            seller_price=extracted_price or counter_offer,
            strategy=neg.strategy or "fair_value",
            round_num=neg.round_count + 1,
            max_rounds=neg.max_rounds,
        )
        
        neg.current_offer = counter_offer
        neg.round_count += 1
        
        if neg.round_count >= neg.max_rounds:
            neg.status = "max_rounds"
            neg.closed_at = datetime.utcnow()
        
        await send_negotiation_email(
            to=neg.seller_contact,
            subject=f"Re: Item - Offer of AED {counter_offer}",
            message=counter_msg,
        )
        
        await db.commit()
        return {"status": "counter", "offer": counter_offer}
    
    else:
        return {"status": "unknown", "message": "Could not understand seller response"}


async def evaluate_all_negotiations(
    db,
    job_id: UUID,
    auto_close: bool = False,
) -> dict:
    """Evaluate all completed negotiations and select best deal."""
    
    result = await db.execute(
        select(NegotiationModel).where(
            NegotiationModel.job_id == job_id,
            NegotiationModel.status.in_(["accepted", "rejected", "max_rounds", "stalled"]),
        )
    )
    negotiations = result.scalars().all()
    
    completed_deals = []
    
    for neg in negotiations:
        if neg.status == "accepted" and neg.agreed_price:
            deal_score = calculate_deal_score(
                agreed_price=neg.agreed_price,
                target_price=neg.target_price,
                max_price=neg.max_price,
                trust_score=0.7,
                time_to_close_hours=18,
                rounds_taken=neg.round_count,
                max_rounds=neg.max_rounds,
            )
            
            deal = DealResult(
                listing_id=neg.listing_id,
                product_name="Item",
                agreed_price=neg.agreed_price,
                currency="AED",
                seller_name=neg.seller_name or "Unknown",
                platform=neg.platform,
                condition="used",
                score=deal_score,
                negotiation_rounds=neg.round_count,
                time_to_close_hours=18,
            )
            
            completed_deals.append(deal)
    
    best = select_best_deal(completed_deals, min_threshold=0.50)
    
    result_data = {
        "job_id": str(job_id),
        "total_negotiations": len(completed_deals),
        "accepted": len([d for d in completed_deals if d.score >= 0.50]),
    }
    
    if best:
        result_data["best_deal"] = best.to_dict()
        result_data["recommended"] = True
        
        if auto_close and best.score >= 0.75:
            accept_msg = await generate_accept_message(
                product=best.product_name,
                agreed_price=best.agreed_price,
                seller_name=best.seller_name,
            )
            
            for neg in negotiations:
                if neg.listing_id == best.listing_id:
                    await send_negotiation_email(
                        to=neg.seller_contact,
                        subject="Confirmed - I'll take it",
                        message=accept_msg,
                    )
                    break
            
            result_data["auto_closed"] = True
    else:
        result_data["recommended"] = False
        result_data["best_deal"] = None
    
    return result_data