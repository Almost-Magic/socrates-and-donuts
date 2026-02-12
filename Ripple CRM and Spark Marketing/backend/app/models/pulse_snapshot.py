"""Ripple CRM — Pulse snapshot model."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class PulseSnapshot(Base):
    __tablename__ = "pulse_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False, unique=True, index=True)
    data_json: Mapped[str] = mapped_column(Text, nullable=False)
    ai_commentary_json: Mapped[str | None] = mapped_column(Text)
    eod_notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
