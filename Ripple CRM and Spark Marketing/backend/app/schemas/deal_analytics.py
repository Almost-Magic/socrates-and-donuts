"""Ripple CRM — Deal Analytics Pydantic schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class StageMetric(BaseModel):
    stage: str
    count: int
    total_value: float
    avg_value: float


class PipelineResponse(BaseModel):
    stages: list[StageMetric]
    total_deals: int
    total_pipeline_value: float
    win_count: int
    loss_count: int
    win_rate: float | None = None
    avg_deal_value: float | None = None


class VelocityMetric(BaseModel):
    stage: str
    avg_days: float
    deal_count: int


class VelocityResponse(BaseModel):
    stages: list[VelocityMetric]
    avg_cycle_days: float | None = None


class StalledDeal(BaseModel):
    id: uuid.UUID
    title: str
    stage: str
    value: float | None = None
    contact_name: str | None = None
    days_stalled: int
    last_activity_at: datetime | None = None


class StalledDealsResponse(BaseModel):
    items: list[StalledDeal]
    total: int
    stall_threshold_days: int
