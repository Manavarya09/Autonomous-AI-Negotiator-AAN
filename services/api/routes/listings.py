"""Listings API router."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_db
from config.database.models import NormalizedListing
from config.database.schemas import NormalizedListingResponse

router = APIRouter(prefix="/api/v1/listings", tags=["listings"])


@router.get("", response_model=list[NormalizedListingResponse])
async def get_listings(
    product: Optional[str] = Query(None, description="Filter by product name"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    max_price: Optional[float] = Query(None, description="Maximum price filter"),
    condition: Optional[str] = Query(None, description="Filter by condition"),
    city: Optional[str] = Query(None, description="Filter by city"),
    sort: str = Query("score", description="Sort by: score, price, date"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    query = select(NormalizedListing)

    if product:
        query = query.where(NormalizedListing.product_name.ilike(f"%{product}%"))
    if platform:
        query = query.where(NormalizedListing.platform == platform)
    if max_price:
        query = query.where(NormalizedListing.price <= max_price)
    if condition:
        query = query.where(NormalizedListing.condition == condition)
    if city:
        query = query.where(NormalizedListing.location_city == city)

    if sort == "price":
        query = query.order_by(NormalizedListing.price.asc())
    elif sort == "date":
        query = query.order_by(NormalizedListing.normalized_at.desc())
    else:
        query = query.order_by(NormalizedListing.listing_score.desc())

    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    listings = result.scalars().all()

    return listings


@router.get("/{listing_id}", response_model=NormalizedListingResponse)
async def get_listing(
    listing_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(NormalizedListing).where(NormalizedListing.id == listing_id)
    )
    listing = result.scalar_one_or_none()

    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    return listing