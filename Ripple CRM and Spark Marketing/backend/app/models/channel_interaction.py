"""ChannelInteraction model — granular response tracking per channel."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.contact import Contact


class ChannelInteraction(Base):
    __tablename__ = "channel_interactions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contact_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=False, index=True)
    channel: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    direction: Mapped[str] = mapped_column(String(10), nullable=False, server_default="out")
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    response_time_seconds: Mapped[int | None] = mapped_column(Integer)
    responded: Mapped[bool] = mapped_column(Boolean, server_default="false")
    day_of_week: Mapped[int | None] = mapped_column(Integer)
    hour_of_day: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    contact: Mapped[Contact] = relationship("Contact", lazy="selectin")
