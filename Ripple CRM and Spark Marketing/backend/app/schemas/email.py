"""Ripple CRM — Email Pydantic schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class EmailSync(BaseModel):
    """Webhook-ready schema for receiving email data from Gmail/Outlook."""
    direction: str = Field(..., pattern="^(in|out)$")
    subject: str | None = None
    body_text: str | None = None
    body_html: str | None = None
    from_address: str = Field(..., max_length=255)
    to_addresses: list[str] = Field(default_factory=list)
    cc_addresses: list[str] = Field(default_factory=list)
    sent_at: datetime | None = None
    received_at: datetime | None = None
    thread_id: str | None = None
    message_id: str | None = None
    is_read: bool = False
    metadata: dict | None = None


class EmailSend(BaseModel):
    """Queue an outgoing email (stores locally, doesn't actually send yet)."""
    contact_id: uuid.UUID | None = None
    to_addresses: list[str] = Field(..., min_length=1)
    cc_addresses: list[str] = Field(default_factory=list)
    subject: str = Field(..., min_length=1, max_length=500)
    body_text: str | None = None
    body_html: str | None = None
    thread_id: str | None = None


class EmailResponse(BaseModel):
    id: uuid.UUID
    contact_id: uuid.UUID | None = None
    deal_id: uuid.UUID | None = None
    direction: str
    subject: str | None = None
    body_text: str | None = None
    body_html: str | None = None
    from_address: str
    to_addresses: list | None = None
    cc_addresses: list | None = None
    sent_at: datetime | None = None
    received_at: datetime | None = None
    thread_id: str | None = None
    message_id: str | None = None
    is_read: bool = False
    status: str = "synced"
    created_at: datetime

    model_config = {"from_attributes": True}


class EmailListResponse(BaseModel):
    items: list[EmailResponse]
    total: int
    page: int
    page_size: int
