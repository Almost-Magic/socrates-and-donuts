"""Touchstone — Schemas for CRM webhook."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field


class CRMWebhookRequest(BaseModel):
    crm_source: str = Field(..., max_length=50)
    crm_deal_id: str = Field(..., max_length=255)
    contact_email: str = Field(..., max_length=255)
    deal_name: str | None = Field(default=None, max_length=255)
    amount: Decimal | None = None
    currency: str = Field(default="AUD", max_length=3)
    stage: str = Field(default="open", max_length=50)
    closed_at: datetime | None = None
    metadata: dict | None = None


class CRMWebhookResponse(BaseModel):
    deal_id: UUID
    contact_id: UUID | None
    is_new: bool
