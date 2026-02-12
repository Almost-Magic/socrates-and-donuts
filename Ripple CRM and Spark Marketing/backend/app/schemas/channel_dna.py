"""Ripple CRM — Channel DNA Pydantic schemas."""

from __future__ import annotations

import uuid

from pydantic import BaseModel


class ChannelStats(BaseModel):
    channel: str
    count: int
    percentage: float
    avg_sentiment: float | None = None


class ChannelDNAResponse(BaseModel):
    contact_id: uuid.UUID
    primary_channel: str | None = None
    preferred_time: str | None = None
    channels: list[ChannelStats]
    total_interactions: int


class ChannelDNASummary(BaseModel):
    channel: str
    contact_count: int
    total_interactions: int
    avg_sentiment: float | None = None


class ChannelDNASummaryResponse(BaseModel):
    items: list[ChannelDNASummary]
    total_contacts_analysed: int
