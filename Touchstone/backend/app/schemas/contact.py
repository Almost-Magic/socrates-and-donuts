"""Touchstone — Schemas for contacts and journeys."""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class ContactOut(BaseModel):
    id: UUID
    anonymous_id: str | None
    email: str | None
    name: str | None
    company: str | None
    metadata: dict | None
    identified_at: datetime | None
    touchpoint_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TouchpointOut(BaseModel):
    id: UUID
    contact_id: UUID | None
    anonymous_id: str | None
    campaign_id: UUID | None
    channel: str | None
    source: str | None
    medium: str | None
    utm_campaign: str | None
    utm_content: str | None
    utm_term: str | None
    touchpoint_type: str
    page_url: str | None
    referrer_url: str | None
    metadata: dict | None
    timestamp: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class JourneyResponse(BaseModel):
    contact: ContactOut
    touchpoints: list[TouchpointOut]
    total_touchpoints: int
