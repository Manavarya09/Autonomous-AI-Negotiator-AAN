"""Jobs API router."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_db
from config.database.models import NegotiationJob
from config.database.schemas import (
    NegotiationJobCreate,
    NegotiationJobResponse,
    NegotiationJobStatusResponse,
)

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


@router.post("", response_model=NegotiationJobResponse, status_code=201)
async def create_job(
    job_data: NegotiationJobCreate,
    db: AsyncSession = Depends(get_db),
):
    job = NegotiationJob(
        product_query=job_data.product_query,
        target_price=job_data.target_price,
        max_price=job_data.max_price,
        currency=job_data.currency,
        location_city=job_data.location_city,
        location_radius=job_data.location_radius,
        urgency=job_data.urgency,
        auto_close=job_data.auto_close,
        status="queued",
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


@router.get("/{job_id}", response_model=NegotiationJobResponse)
async def get_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(NegotiationJob).where(NegotiationJob.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job


@router.get("/{job_id}/status", response_model=NegotiationJobStatusResponse)
async def get_job_status(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(NegotiationJob).where(NegotiationJob.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    from config.database.models import RawListing, NormalizedListing, Negotiation

    raw_result = await db.execute(
        select(RawListing).where(RawListing.job_id == job_id)
    )
    raw_count = len(raw_result.scalars().all())

    norm_result = await db.execute(
        select(NormalizedListing).where(NormalizedListing.job_id == job_id)
    )
    norm_count = len(norm_result.scalars().all())

    neg_result = await db.execute(
        select(Negotiation).where(Negotiation.job_id == job_id)
    )
    negotiations = neg_result.scalars().all()
    active_count = sum(1 for n in negotiations if n.status == "active")
    completed_count = sum(1 for n in negotiations if n.status in ("accepted", "rejected", "stalled"))

    return NegotiationJobStatusResponse(
        id=job.id,
        status=job.status,
        listings_found=norm_count,
        active_negotiations=active_count,
        completed_negotiations=completed_count,
    )


@router.delete("/{job_id}")
async def cancel_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(NegotiationJob).where(NegotiationJob.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.status = "cancelled"
    await db.commit()

    return {"message": "Job cancelled", "job_id": str(job_id)}