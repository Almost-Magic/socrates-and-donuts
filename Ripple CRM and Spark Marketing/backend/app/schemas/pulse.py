"""Ripple CRM — Pulse Pydantic schemas."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from pydantic import BaseModel, Field


# ── Sales Targets ──────────────────────────────────────────────────────────

class SalesTargetCreate(BaseModel):
    period_type: str = Field("monthly", pattern="^(monthly|quarterly|yearly)$")
    period_label: str = Field(..., min_length=1, max_length=50)
    period_start: date
    period_end: date
    target_value: float = Field(..., gt=0)
    currency: str = Field("AUD", max_length=10)
    notes: str | None = None


class SalesTargetResponse(BaseModel):
    id: uuid.UUID
    period_type: str
    period_label: str
    period_start: date
    period_end: date
    target_value: float
    currency: str
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SalesTargetListResponse(BaseModel):
    items: list[SalesTargetResponse]
    total: int


# ── Pulse Actions ──────────────────────────────────────────────────────────

class PulseActionResponse(BaseModel):
    id: uuid.UUID
    snapshot_date: date
    title: str
    description: str | None = None
    reason: str | None = None
    estimated_minutes: int | None = None
    contact_id: uuid.UUID | None = None
    deal_id: uuid.UUID | None = None
    priority: int
    is_completed: bool
    completed_at: datetime | None = None
    contact_name: str | None = None
    deal_title: str | None = None

    model_config = {"from_attributes": True}


class PulseActionListResponse(BaseModel):
    items: list[PulseActionResponse]
    total: int


# ── Pulse Wisdom ───────────────────────────────────────────────────────────

class PulseWisdomResponse(BaseModel):
    id: uuid.UUID
    quote: str
    author: str
    source: str | None = None

    model_config = {"from_attributes": True}


# ── Pulse Snapshot (full Pulse response) ───────────────────────────────────

class TargetVsActual(BaseModel):
    target_id: uuid.UUID | None = None
    period_label: str
    period_type: str
    target_value: float
    actual_value: float
    gap: float
    percentage: float
    pace: str
    commentary: str | None = None


class EasyWin(BaseModel):
    deal_id: uuid.UUID
    deal_title: str
    contact_id: uuid.UUID | None = None
    contact_name: str | None = None
    value: float | None = None
    stage: str
    probability: float | None = None
    days_since_contact: int | None = None
    score: float
    win_type: str
    commentary: str | None = None


class PipelineStage(BaseModel):
    stage: str
    count: int
    value: float


class StalledDeal(BaseModel):
    deal_id: uuid.UUID
    title: str
    stage: str
    value: float | None = None
    days_in_stage: int
    contact_name: str | None = None


class PipelineHealth(BaseModel):
    stages: list[PipelineStage]
    stalled_deals: list[StalledDeal]
    win_rate_30d: float | None = None
    win_rate_60d: float | None = None
    win_rate_90d: float | None = None
    avg_deal_velocity_days: float | None = None
    narrative: str | None = None


class RelationshipChange(BaseModel):
    contact_id: uuid.UUID
    contact_name: str
    health_score: float | None = None
    trust_decay_days: int | None = None
    status: str
    last_interaction_days: int | None = None


class RelationshipIntelligence(BaseModel):
    decaying: list[RelationshipChange]
    champions: list[RelationshipChange]
    no_contact: list[RelationshipChange]


class CoachingInsight(BaseModel):
    streak_days: int
    streak_type: str | None = None
    personal_bests: list[str]
    coaching_tips: list[str]


class PulseResponse(BaseModel):
    snapshot_date: date
    target_vs_actual: TargetVsActual | None = None
    easy_wins: list[EasyWin]
    actions: list[PulseActionResponse]
    pipeline: PipelineHealth
    relationships: RelationshipIntelligence
    coaching: CoachingInsight
    wisdom: PulseWisdomResponse | None = None
    generated_at: datetime | None = None


# ── EOD Review ─────────────────────────────────────────────────────────────

class EodReviewRequest(BaseModel):
    notes: str = Field(..., min_length=1, max_length=5000)


class EodReviewResponse(BaseModel):
    snapshot_date: date
    eod_notes: str | None = None
    actions_completed: int
    actions_total: int
    target_progress: float | None = None


# ── ELAINE Briefing ────────────────────────────────────────────────────────

class ElaineBriefingResponse(BaseModel):
    snapshot_date: date
    target_summary: str | None = None
    top_action: str | None = None
    pipeline_alert: str | None = None
    relationship_alert: str | None = None
    win_celebration: str | None = None
    wisdom_quote: str | None = None


# ── Streak ─────────────────────────────────────────────────────────────────

class StreakResponse(BaseModel):
    current_streak: int
    streak_unit: str
    best_streak: int
    last_hit_date: date | None = None
