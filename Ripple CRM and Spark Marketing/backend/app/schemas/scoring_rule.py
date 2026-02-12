"""Ripple CRM — Scoring Rule Pydantic schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ScoringRuleCreate(BaseModel):
    brain: str = Field(..., pattern="^(fit|intent|instinct)$")
    attribute: str = Field(..., min_length=1, max_length=100)
    label: str = Field(..., min_length=1, max_length=200)
    points: float = 0
    max_points: float = 100
    description: str | None = None
    is_active: bool = True
    sort_order: int = 0


class ScoringRuleUpdate(BaseModel):
    brain: str | None = Field(None, pattern="^(fit|intent|instinct)$")
    attribute: str | None = Field(None, max_length=100)
    label: str | None = Field(None, max_length=200)
    points: float | None = None
    max_points: float | None = None
    description: str | None = None
    is_active: bool | None = None
    sort_order: int | None = None


class ScoringRuleResponse(BaseModel):
    id: uuid.UUID
    brain: str
    attribute: str
    label: str
    points: float
    max_points: float
    description: str | None = None
    is_active: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ScoringRuleListResponse(BaseModel):
    items: list[ScoringRuleResponse]
    total: int
