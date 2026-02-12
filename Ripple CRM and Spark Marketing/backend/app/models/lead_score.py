"""Ripple CRM — Lead Score model (Three Brains)."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class LeadScore(Base):
    __tablename__ = "lead_scores"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contact_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=False, index=True)
    fit_score: Mapped[float] = mapped_column(Float, default=0)
    intent_score: Mapped[float] = mapped_column(Float, default=0)
    instinct_score: Mapped[float] = mapped_column(Float, default=0)
    composite_score: Mapped[float] = mapped_column(Float, default=0)
    fit_breakdown: Mapped[str | None] = mapped_column(Text)
    intent_breakdown: Mapped[str | None] = mapped_column(Text)
    instinct_breakdown: Mapped[str | None] = mapped_column(Text)
    is_mql: Mapped[bool] = mapped_column(Boolean, default=False)
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
