"""Ripple CRM — Consent Preference Pydantic schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class ConsentPreferenceUpdate(BaseModel):
    email_marketing: bool | None = None
    data_processing: bool | None = None
    third_party_sharing: bool | None = None
    analytics: bool | None = None
    profiling: bool | None = None


class ConsentPreferenceResponse(BaseModel):
    id: uuid.UUID
    contact_id: uuid.UUID
    email_marketing: bool
    data_processing: bool
    third_party_sharing: bool
    analytics: bool
    profiling: bool
    updated_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}
