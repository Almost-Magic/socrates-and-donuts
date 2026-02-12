"""Ripple CRM — DSAR Request Pydantic schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class DsarRequestCreate(BaseModel):
    contact_id: uuid.UUID
    request_type: str = Field(..., pattern="^(access|export|deletion|rectification)$")
    notes: str | None = None


class DsarRequestUpdate(BaseModel):
    status: str = Field(..., pattern="^(pending|processing|completed|rejected)$")
    notes: str | None = None


class DsarRequestResponse(BaseModel):
    id: uuid.UUID
    contact_id: uuid.UUID
    request_type: str
    status: str
    notes: str | None = None
    requested_at: datetime
    completed_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class DsarRequestListResponse(BaseModel):
    items: list[DsarRequestResponse]
    total: int
    page: int
    page_size: int
