"""Ripple CRM — Lead Score (Three Brains) Pydantic schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class BrainBreakdown(BaseModel):
    score: float
    components: dict[str, float]


class LeadScoreResponse(BaseModel):
    id: uuid.UUID
    contact_id: uuid.UUID
    fit_score: float
    intent_score: float
    instinct_score: float
    composite_score: float
    fit_breakdown: BrainBreakdown | None = None
    intent_breakdown: BrainBreakdown | None = None
    instinct_breakdown: BrainBreakdown | None = None
    calculated_at: datetime


class LeadScoreListResponse(BaseModel):
    items: list[LeadScoreResponse]
    total: int


class LeadScoreSummary(BaseModel):
    contact_id: uuid.UUID
    contact_name: str
    composite_score: float
    fit_score: float
    intent_score: float
    instinct_score: float
    calculated_at: datetime


class LeaderboardResponse(BaseModel):
    items: list[LeadScoreSummary]
    total: int
