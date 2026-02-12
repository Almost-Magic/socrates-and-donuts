"""Ripple CRM — Trust Decay Pydantic schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class TrustDecayResponse(BaseModel):
    contact_id: uuid.UUID
    status: str  # healthy, cooling, at_risk, dormant
    days_since_last: int | None = None
    baseline_gap_days: float | None = None
    decay_ratio: float | None = None
    last_interaction_at: datetime | None = None
    interaction_count: int = 0


class AtRiskContact(BaseModel):
    contact_id: uuid.UUID
    contact_name: str
    status: str
    days_since_last: int | None = None
    decay_ratio: float | None = None
    relationship_health_score: float | None = None


class AtRiskListResponse(BaseModel):
    items: list[AtRiskContact]
    total: int
