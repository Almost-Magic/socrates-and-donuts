"""Touchstone — Deal model (CRM outcomes via webhook)."""

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import String, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Deal(Base):
    __tablename__ = "touchstone_deals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contact_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("touchstone_contacts.id"), index=True
    )
    crm_deal_id: Mapped[str | None] = mapped_column(String(255), unique=True)
    deal_name: Mapped[str | None] = mapped_column(String(255))
    amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3), default="AUD")
    stage: Mapped[str] = mapped_column(String(50), default="open")
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    crm_source: Mapped[str | None] = mapped_column(String(50))
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
