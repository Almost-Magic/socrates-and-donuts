"""Channel Interaction schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ChannelInteractionCreate(BaseModel):
    contact_id: uuid.UUID
    channel: str = Field(..., min_length=1, max_length=50)
    direction: str = Field("out", pattern="^(in|out)$")
    occurred_at: datetime | None = None
    response_time_seconds: int | None = Field(None, ge=0)
    responded: bool = False


class ChannelInteractionResponse(BaseModel):
    id: uuid.UUID
    contact_id: uuid.UUID
    channel: str
    direction: str
    occurred_at: datetime
    response_time_seconds: int | None = None
    responded: bool
    day_of_week: int | None = None
    hour_of_day: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChannelInteractionListResponse(BaseModel):
    items: list[ChannelInteractionResponse]
    total: int


class ChannelProfileResponse(BaseModel):
    contact_id: str
    preferred_channel: str | None = None
    preferred_times: dict | None = None
    channel_stats: list[dict]
    response_rates: dict
    best_time_slots: list[dict]
    total_outreach: int
    overall_response_rate: float | None = None
