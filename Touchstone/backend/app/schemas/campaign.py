"""Touchstone — Schemas for campaigns."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field


class CampaignCreate(BaseModel):
    name: str = Field(..., max_length=255)
    channel: str | None = Field(default=None, max_length=50)
    start_date: date | None = None
    end_date: date | None = None
    budget: Decimal | None = None
    currency: str = Field(default="AUD", max_length=3)
    metadata: dict | None = None


class CampaignUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    channel: str | None = Field(default=None, max_length=50)
    start_date: date | None = None
    end_date: date | None = None
    budget: Decimal | None = None
    currency: str | None = Field(default=None, max_length=3)
    metadata: dict | None = None


class CampaignOut(BaseModel):
    id: UUID
    name: str
    channel: str | None
    start_date: date | None
    end_date: date | None
    budget: Decimal | None
    currency: str
    metadata: dict | None
    touchpoint_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
