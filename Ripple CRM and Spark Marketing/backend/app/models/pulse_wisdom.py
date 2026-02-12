"""Ripple CRM — Pulse wisdom quote model."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class PulseWisdom(Base):
    __tablename__ = "pulse_wisdom"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quote: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(200), nullable=False)
    source: Mapped[str | None] = mapped_column(String(300))
    last_shown: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
