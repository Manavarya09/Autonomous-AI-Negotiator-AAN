"""Pydantic schemas for AAN API."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class NegotiationJobBase(BaseModel):
    product_query: str = Field(..., max_length=500)
    target_price: float = Field(..., gt=0)
    max_price: float = Field(..., gt=0)
    currency: str = Field(default="AED", max_length=3)
    location_city: Optional[str] = Field(None, max_length=100)
    location_radius: Optional[int] = Field(None, ge=0)
    urgency: str = Field(default="normal")
    auto_close: bool = Field(default=False)


class NegotiationJobCreate(NegotiationJobBase):
    pass


class NegotiationJobResponse(NegotiationJobBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: Optional[UUID]
    status: str
    created_at: datetime
    updated_at: datetime


class NegotiationJobStatusResponse(BaseModel):
    id: UUID
    status: str
    listings_found: int = 0
    active_negotiations: int = 0
    completed_negotiations: int = 0


class RawListingBase(BaseModel):
    platform: str
    listing_url: str
    title: str
    price_raw: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    seller_name: Optional[str] = None
    seller_contact: Optional[str] = None
    condition_raw: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    posted_date: Optional[str] = None
    image_urls: list[str] = []


class RawListingResponse(RawListingBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_id: Optional[UUID]
    scraped_at: datetime


class NormalizedListingBase(BaseModel):
    product_name: str
    price: float
    currency: str = "AED"
    platform: str
    listing_url: str
    seller_name: Optional[str] = None
    seller_contact: Optional[str] = None
    condition: Optional[str] = None
    condition_score: float
    location_city: Optional[str] = None
    location_distance: Optional[float] = None
    posted_days_ago: Optional[int] = None
    is_negotiable: bool = True
    listing_score: float


class NormalizedListingResponse(NormalizedListingBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_id: Optional[UUID]
    normalized_at: datetime


class NegotiationBase(BaseModel):
    seller_name: Optional[str] = None
    seller_contact: Optional[str] = None
    platform: str
    strategy: Optional[str] = None
    seller_type: Optional[str] = None
    list_price: float
    target_price: float
    max_price: float
    current_offer: Optional[float] = None
    agreed_price: Optional[float] = None
    status: str = "active"
    round_count: int = 0
    max_rounds: int = 5


class NegotiationResponse(NegotiationBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_id: UUID
    listing_id: UUID
    deal_score: Optional[float]
    started_at: datetime
    closed_at: Optional[datetime]


class MessageBase(BaseModel):
    direction: str
    channel: str
    raw_content: Optional[str] = None
    parsed_content: Optional[str] = None
    intent: Optional[str] = None
    extracted_price: Optional[float] = None
    confidence: Optional[float] = None


class MessageResponse(MessageBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    negotiation_id: UUID
    sent_at: Optional[datetime]
    received_at: Optional[datetime]


class DealScoringResult(BaseModel):
    listing_id: UUID
    product_name: str
    agreed_price: float
    currency: str = "AED"
    seller_name: Optional[str]
    platform: str
    condition: Optional[str]
    score: float
    negotiation_rounds: int
    time_to_close_hours: float


class JobCompletedResponse(BaseModel):
    job_id: UUID
    status: str = "completed"
    recommended_deal: Optional[DealScoringResult] = None
    all_deals: list[DealScoringResult] = []