"""Touchstone — Touchpoint model (the Campaign Participation Ledger)."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Touchpoint(Base):
    __tablename__ = "touchstone_touchpoints"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contact_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("touchstone_contacts.id"), index=True
    )
    anonymous_id: Mapped[str | None] = mapped_column(String(64), index=True)
    campaign_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("touchstone_campaigns.id")
    )
    channel: Mapped[str | None] = mapped_column(String(50))
    source: Mapped[str | None] = mapped_column(String(100))
    medium: Mapped[str | None] = mapped_column(String(100))
    utm_campaign: Mapped[str | None] = mapped_column(String(255))
    utm_content: Mapped[str | None] = mapped_column(String(255))
    utm_term: Mapped[str | None] = mapped_column(String(255))
    touchpoint_type: Mapped[str] = mapped_column(String(50), default="page_view")
    page_url: Mapped[str | None] = mapped_column(Text)
    referrer_url: Mapped[str | None] = mapped_column(Text)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, default=dict)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
