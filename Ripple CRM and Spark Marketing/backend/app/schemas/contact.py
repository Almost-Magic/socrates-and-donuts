"""Ripple CRM — Contact Pydantic schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.tag import TagResponse


class ContactCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: str | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=50)
    company_id: uuid.UUID | None = None
    role: str | None = Field(None, max_length=100)
    title: str | None = Field(None, max_length=150)
    type: str = Field("lead", pattern="^(lead|contact|customer)$")
    source: str | None = Field(None, max_length=100)
    notes: str | None = None
    timezone: str | None = Field(None, max_length=50)
    linkedin_url: str | None = Field(None, max_length=500)
    preferred_channel: str | None = Field(None, max_length=50)


class ContactUpdate(BaseModel):
    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    email: str | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=50)
    company_id: uuid.UUID | None = None
    role: str | None = Field(None, max_length=100)
    title: str | None = Field(None, max_length=150)
    type: str | None = Field(None, pattern="^(lead|contact|customer)$")
    source: str | None = Field(None, max_length=100)
    notes: str | None = None
    timezone: str | None = Field(None, max_length=50)
    linkedin_url: str | None = Field(None, max_length=500)
    preferred_channel: str | None = Field(None, max_length=50)


class ContactResponse(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    email: str | None = None
    phone: str | None = None
    company_id: uuid.UUID | None = None
    role: str | None = None
    title: str | None = None
    type: str
    source: str | None = None
    notes: str | None = None
    timezone: str | None = None
    linkedin_url: str | None = None
    preferred_channel: str | None = None
    relationship_health_score: float | None = None
    trust_decay_days: int | None = None
    trust_decay_status: str | None = None
    tags: list[TagResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ContactListResponse(BaseModel):
    items: list[ContactResponse]
    total: int
    page: int
    page_size: int
