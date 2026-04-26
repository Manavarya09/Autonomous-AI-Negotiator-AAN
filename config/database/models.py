"""Database models for AAN."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(200))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    jobs: Mapped[list["NegotiationJob"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (Index("ix_users_email", "email"),)


class NegotiationJob(Base):
    __tablename__ = "negotiation_jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    product_query: Mapped[str] = mapped_column(String(500), nullable=False)
    target_price: Mapped[float] = mapped_column(Float, nullable=False)
    max_price: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="AED")
    location_city: Mapped[Optional[str]] = mapped_column(String(100))
    location_radius: Mapped[Optional[int]] = mapped_column(Integer)
    urgency: Mapped[str] = mapped_column(String(20), default="normal")
    status: Mapped[str] = mapped_column(String(30), default="queued")
    auto_close: Mapped[bool] = mapped_column(Boolean, default=False)
    config: Mapped[Optional[dict]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    raw_listings: Mapped[list["RawListing"]] = relationship(back_populates="job", cascade="all, delete-orphan")
    normalized_listings: Mapped[list["NormalizedListing"]] = relationship(back_populates="job", cascade="all, delete-orphan")
    negotiations: Mapped[list["Negotiation"]] = relationship(back_populates="job", cascade="all, delete-orphan")

    user: Mapped["User"] = relationship(back_populates="jobs")


class RawListing(Base):
    __tablename__ = "raw_listings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("negotiation_jobs.id"), nullable=True)
    platform: Mapped[str] = mapped_column(String(50))
    listing_url: Mapped[str] = mapped_column(Text, unique=True)
    title: Mapped[str] = mapped_column(Text)
    price_raw: Mapped[Optional[str]] = mapped_column(String(100))
    price: Mapped[Optional[float]] = mapped_column(Float)
    currency: Mapped[Optional[str]] = mapped_column(String(3))
    seller_name: Mapped[Optional[str]] = mapped_column(String(200))
    seller_contact: Mapped[Optional[str]] = mapped_column(Text)
    seller_profile_url: Mapped[Optional[str]] = mapped_column(Text)
    condition_raw: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    location: Mapped[Optional[str]] = mapped_column(String(200))
    posted_date: Mapped[Optional[str]] = mapped_column(String(50))
    image_urls: Mapped[list[str]] = mapped_column(ARRAY(Text))
    listing_id: Mapped[Optional[str]] = mapped_column(String(100))
    scraped_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    job: Mapped["NegotiationJob"] = relationship(back_populates="raw_listings")

    __table_args__ = (Index("ix_raw_listings_job_id", "job_id"),)


class NormalizedListing(Base):
    __tablename__ = "normalized_listings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    raw_listing_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("raw_listings.id"), nullable=True)
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("negotiation_jobs.id"), nullable=True)
    product_name: Mapped[str] = mapped_column(String(500))
    canonical_title: Mapped[Optional[str]] = mapped_column(String(500))
    price: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(3), default="AED")
    platform: Mapped[str] = mapped_column(String(50))
    listing_url: Mapped[str] = mapped_column(Text)
    seller_name: Mapped[Optional[str]] = mapped_column(String(200))
    seller_contact: Mapped[Optional[str]] = mapped_column(Text)
    condition: Mapped[Optional[str]] = mapped_column(String(30))
    condition_score: Mapped[float] = mapped_column(Float)
    location_city: Mapped[Optional[str]] = mapped_column(String(100))
    location_distance: Mapped[Optional[float]] = mapped_column(Float)
    posted_days_ago: Mapped[Optional[int]] = mapped_column(Integer)
    is_negotiable: Mapped[bool] = mapped_column(Boolean, default=True)
    listing_score: Mapped[float] = mapped_column(Float)
    normalized_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    job: Mapped["NegotiationJob"] = relationship(back_populates="normalized_listings")
    negotiations: Mapped[list["Negotiation"]] = relationship(back_populates="listing")

    __table_args__ = (Index("ix_normalized_listings_job_id", "job_id"),)


class Negotiation(Base):
    __tablename__ = "negotiations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("negotiation_jobs.id"))
    listing_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("normalized_listings.id"))
    seller_name: Mapped[Optional[str]] = mapped_column(String(200))
    seller_contact: Mapped[Optional[str]] = mapped_column(Text)
    platform: Mapped[str] = mapped_column(String(50))
    strategy: Mapped[Optional[str]] = mapped_column(String(50))
    seller_type: Mapped[Optional[str]] = mapped_column(String(30))
    list_price: Mapped[float] = mapped_column(Float)
    target_price: Mapped[float] = mapped_column(Float)
    max_price: Mapped[float] = mapped_column(Float)
    current_offer: Mapped[Optional[float]] = mapped_column(Float)
    agreed_price: Mapped[Optional[float]] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(30), default="active")
    round_count: Mapped[int] = mapped_column(Integer, default=0)
    max_rounds: Mapped[int] = mapped_column(Integer, default=5)
    deal_score: Mapped[Optional[float]] = mapped_column(Float)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    job: Mapped["NegotiationJob"] = relationship(back_populates="negotiations")
    listing: Mapped["NormalizedListing"] = relationship(back_populates="negotiations")
    messages: Mapped[list["Message"]] = relationship(back_populates="negotiation", cascade="all, delete-orphan")

    __table_args__ = (Index("ix_negotiations_job_id", "job_id"),)


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    negotiation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("negotiations.id"))
    direction: Mapped[str] = mapped_column(String(10))
    channel: Mapped[str] = mapped_column(String(30))
    raw_content: Mapped[Optional[str]] = mapped_column(Text)
    parsed_content: Mapped[Optional[str]] = mapped_column(Text)
    intent: Mapped[Optional[str]] = mapped_column(String(30))
    extracted_price: Mapped[Optional[float]] = mapped_column(Float)
    confidence: Mapped[Optional[float]] = mapped_column(Float)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    received_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    negotiation: Mapped["Negotiation"] = relationship(back_populates="messages")

    __table_args__ = (Index("ix_messages_negotiation_id", "negotiation_id"),)


class SellerProfile(Base):
    __tablename__ = "seller_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform: Mapped[str] = mapped_column(String(50))
    platform_user_id: Mapped[Optional[str]] = mapped_column(Text)
    name: Mapped[Optional[str]] = mapped_column(String(200))
    seller_type: Mapped[Optional[str]] = mapped_column(String(30))
    trust_score: Mapped[Optional[float]] = mapped_column(Float)
    avg_response_hours: Mapped[Optional[float]] = mapped_column(Float)
    negotiations_count: Mapped[int] = mapped_column(Integer, default=0)
    acceptance_rate: Mapped[Optional[float]] = mapped_column(Float)
    last_seen: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("platform", "platform_user_id", name="uq_seller_platform_user"),
    )


class StrategyOutcome(Base):
    __tablename__ = "strategy_outcomes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    negotiation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("negotiations.id"), nullable=True)
    strategy_used: Mapped[str] = mapped_column(String(50))
    seller_type: Mapped[Optional[str]] = mapped_column(String(30))
    product_category: Mapped[Optional[str]] = mapped_column(String(100))
    list_price: Mapped[float] = mapped_column(Float)
    agreed_price: Mapped[Optional[float]] = mapped_column(Float)
    savings_pct: Mapped[Optional[float]] = mapped_column(Float)
    rounds_taken: Mapped[Optional[int]] = mapped_column(Integer)
    result: Mapped[Optional[str]] = mapped_column(String(20))
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)