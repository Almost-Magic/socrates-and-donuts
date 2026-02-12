"""Ripple CRM — Email model."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Email(Base):
    __tablename__ = "emails"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contact_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=True, index=True)
    deal_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("deals.id"), nullable=True, index=True)
    direction: Mapped[str] = mapped_column(String(10), nullable=False)  # "in" or "out"
    subject: Mapped[str | None] = mapped_column(String(500))
    body_text: Mapped[str | None] = mapped_column(Text)
    body_html: Mapped[str | None] = mapped_column(Text)
    from_address: Mapped[str] = mapped_column(String(255), nullable=False)
    to_addresses: Mapped[dict | None] = mapped_column(JSONB, default=list)
    cc_addresses: Mapped[dict | None] = mapped_column(JSONB, default=list)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    thread_id: Mapped[str | None] = mapped_column(String(255), index=True)
    message_id: Mapped[str | None] = mapped_column(String(255), unique=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(20), default="synced")  # synced, pending, sent, failed
    metadata_json: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    contact: Mapped["Contact"] = relationship("Contact", lazy="selectin")
    deal: Mapped["Deal"] = relationship("Deal", lazy="selectin")


from app.models.contact import Contact  # noqa: E402, F811
from app.models.deal import Deal  # noqa: E402, F811
