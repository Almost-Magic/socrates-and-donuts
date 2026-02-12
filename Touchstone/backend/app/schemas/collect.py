"""Touchstone — Schemas for event collection."""

from datetime import datetime
from pydantic import BaseModel, Field


class CollectEvent(BaseModel):
    anonymous_id: str = Field(..., max_length=64)
    touchpoint_type: str = Field(default="page_view", max_length=50)
    page_url: str | None = None
    referrer_url: str | None = None
    channel: str | None = Field(default=None, max_length=50)
    source: str | None = Field(default=None, max_length=100)
    medium: str | None = Field(default=None, max_length=100)
    utm_campaign: str | None = Field(default=None, max_length=255)
    utm_content: str | None = Field(default=None, max_length=255)
    utm_term: str | None = Field(default=None, max_length=255)
    metadata: dict | None = None
    timestamp: datetime | None = None
