"""Ripple CRM — Contact model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.commitment import Commitment
    from app.models.deal import Deal
    from app.models.interaction import Interaction
    from app.models.note import Note
    from app.models.privacy_consent import PrivacyConsent
    from app.models.relationship import Relationship
    from app.models.tag import Tag
    from app.models.task import Task


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), index=True)
    phone: Mapped[str | None] = mapped_column(String(50))
    company_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True, index=True)
    role: Mapped[str | None] = mapped_column(String(100))
    title: Mapped[str | None] = mapped_column(String(150))
    type: Mapped[str] = mapped_column(String(20), default="lead")
    source: Mapped[str | None] = mapped_column(String(100))
    notes: Mapped[str | None] = mapped_column(Text)
    timezone: Mapped[str | None] = mapped_column(String(50))
    linkedin_url: Mapped[str | None] = mapped_column(String(500))
    preferred_channel: Mapped[str | None] = mapped_column(String(50))
    relationship_health_score: Mapped[float | None] = mapped_column(Float)
    trust_decay_days: Mapped[int | None] = mapped_column(Integer)
    channel_dna_json: Mapped[str | None] = mapped_column(Text)
    preferred_times_json: Mapped[str | None] = mapped_column(Text)
    trust_decay_status: Mapped[str | None] = mapped_column(String(20))
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    company: Mapped["Company"] = relationship("Company", lazy="selectin")
    interactions: Mapped[list[Interaction]] = relationship("Interaction", back_populates="contact", lazy="selectin")
    relationships: Mapped[list[Relationship]] = relationship("Relationship", back_populates="contact", lazy="selectin")
    deals: Mapped[list[Deal]] = relationship("Deal", back_populates="contact", foreign_keys="Deal.contact_id", lazy="selectin")
    commitments: Mapped[list[Commitment]] = relationship("Commitment", back_populates="contact", lazy="selectin")
    tasks: Mapped[list[Task]] = relationship("Task", back_populates="contact", lazy="selectin")
    notes_list: Mapped[list[Note]] = relationship("Note", back_populates="contact", lazy="selectin")
    privacy_consents: Mapped[list[PrivacyConsent]] = relationship("PrivacyConsent", back_populates="contact", lazy="selectin")
    tags: Mapped[list[Tag]] = relationship("Tag", secondary="contact_tags", back_populates="contacts", lazy="selectin")


from app.models.company import Company  # noqa: E402, F811
