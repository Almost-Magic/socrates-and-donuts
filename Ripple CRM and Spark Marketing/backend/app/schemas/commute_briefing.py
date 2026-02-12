"""Commute Briefing schemas (Phase 2.3)."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class CommuteBriefingRequest(BaseModel):
    travel_minutes: int = Field(15, ge=1, le=180, description="Estimated travel time in minutes")
    format: str = Field("text", pattern="^(text|bullet|detailed)$")


class ContactSummary(BaseModel):
    name: str
    role: str | None = None
    company: str | None = None
    type: str | None = None
    relationship_health: float | None = None
    preferred_channel: str | None = None
    trust_decay_status: str | None = None
    total_interactions: int = 0
    last_interaction_date: datetime | None = None


class DealSummary(BaseModel):
    title: str
    stage: str
    value: float | None = None
    probability: int | None = None
    days_in_stage: int | None = None


class RecentInteraction(BaseModel):
    type: str
    channel: str | None = None
    subject: str | None = None
    occurred_at: datetime
    sentiment_score: float | None = None


class OpenItem(BaseModel):
    title: str
    due_date: datetime | None = None
    status: str | None = None
    priority: str | None = None


class CommuteBriefingResponse(BaseModel):
    meeting_id: str
    meeting_title: str
    meeting_time: datetime | None = None
    travel_minutes: int
    estimated_read_minutes: int
    briefing_depth: str  # "quick", "standard", "deep"
    contact_summary: ContactSummary | None = None
    deal_summary: DealSummary | None = None
    recent_interactions: list[RecentInteraction] = []
    open_commitments: list[OpenItem] = []
    open_tasks: list[OpenItem] = []
    talking_points: list[str] = []
    warnings: list[str] = []
    ai_summary: str | None = None
    generated_at: datetime


class QuickBriefResponse(BaseModel):
    contact_id: str
    contact_name: str
    summary: ContactSummary
    active_deals: list[DealSummary] = []
    recent_interactions: list[RecentInteraction] = []
    open_commitments: list[OpenItem] = []
    talking_points: list[str] = []
    generated_at: datetime
