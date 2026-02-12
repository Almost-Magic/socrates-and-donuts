"""Ripple CRM — Consent Preference model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.contact import Contact


class ConsentPreference(Base):
    __tablename__ = "consent_preferences"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contact_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=False, unique=True, index=True)
    email_marketing: Mapped[bool] = mapped_column(Boolean, default=False)
    data_processing: Mapped[bool] = mapped_column(Boolean, default=True)
    third_party_sharing: Mapped[bool] = mapped_column(Boolean, default=False)
    analytics: Mapped[bool] = mapped_column(Boolean, default=True)
    profiling: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    contact: Mapped[Contact] = relationship("Contact", lazy="selectin")
