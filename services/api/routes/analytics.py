"""AI-powered analytics and recommendations."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

from services.api.routes.auth import get_current_user
from config.database.models import User, NegotiationJob
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_db
from services.worker.ml.models import price_predictor, image_analyzer, seller_analyzer

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


class PricePredictionRequest(BaseModel):
    title: str
    condition: str
    market_prices: list[float]
    days_listed: int


class ListingAnalysisRequest(BaseModel):
    image_urls: list[str]
    price: float
    title: str
    seller_name: str
    platform: str


@router.post("/predict-price")
async def predict_optimal_price(
    request: PricePredictionRequest,
    current_user: User = Depends(get_current_user),
):
    """Predict optimal price for a listing."""
    
    prediction = await price_predictor.predict(
        title=request.title,
        condition=request.condition,
        market_prices=request.market_prices,
        days_listed=request.days_listed,
    )
    
    return {
        "recommended_price": prediction.recommended_price,
        "confidence": prediction.confidence,
        "price_trend": prediction.price_trend,
        "market_avg": prediction.market_avg,
        "days_to_buy": prediction.days_to_buy,
    }


@router.post("/analyze-listing")
async def analyze_listing(
    request: ListingAnalysisRequest,
    current_user: User = Depends(get_current_user),
):
    """Analyze a listing for condition and fraud detection."""
    
    image_analysis = await image_analyzer.analyze_condition(
        image_urls=request.image_urls,
        title=request.title,
    )
    
    fraud_detection = await image_analyzer.detect_fake_listings(
        image_urls=request.image_urls,
        price=request.price,
        title=request.title,
    )
    
    return {
        "image_analysis": image_analysis,
        "fraud_detection": fraud_detection,
    }


@router.get("/market-insights")
async def get_market_insights(
    query: str,
    current_user: User = Depends(get_current_user),
):
    """Get market insights for a product query."""
    
    return {
        "query": query,
        "avg_price": 0,
        "price_range": {"min": 0, "max": 0},
        "listings_count": 0,
        "platforms": {},
    }


@router.get("/seller/{seller_id}/analysis")
async def analyze_seller(
    seller_id: str,
    platform: str,
    current_user: User = Depends(get_current_user),
):
    """Get seller trust analysis."""
    
    trust = await seller_analyzer.calculate_trust_score(
        seller_name=seller_id,
        platform=platform,
        response_time_hours=4.5,
        negotiation_count=15,
        acceptance_rate=0.65,
    )
    
    return trust


@router.get("/deal-score")
async def calculate_deal_score(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
):
    """Calculate overall deal score for a job."""
    
    async with async_session_maker() as db:
        result = await db.execute(
            select(NegotiationJob).where(NegotiationJob.id == job_id)
        )
        job = result.scalar_one_or_none()
    
    if not job:
        return {"error": "Job not found"}
    
    deal_score = 0.0
    
    max_discount = ((job.max_price - job.target_price) / job.max_price) * 100
    
    if max_discount > 30:
        deal_score += 40
    elif max_discount > 20:
        deal_score += 30
    elif max_discount > 10:
        deal_score += 20
    else:
        deal_score += 10
    
    if job.status == "completed":
        deal_score += 30
    
    deal_score = min(100, deal_score)
    
    return {
        "job_id": str(job_id),
        "score": deal_score,
        "rating": "Excellent" if deal_score >= 80 else "Good" if deal_score >= 60 else "Fair" if deal_score >= 40 else "Poor",
        "factors": {
            "discount_potential": max_discount,
            "status": job.status,
        },
    }