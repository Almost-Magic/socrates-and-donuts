"""Touchstone — Schemas for contact identification."""

from uuid import UUID
from pydantic import BaseModel, Field


class IdentifyRequest(BaseModel):
    anonymous_id: str = Field(..., max_length=64)
    email: str = Field(..., max_length=255)
    name: str | None = Field(default=None, max_length=255)
    company: str | None = Field(default=None, max_length=255)
    metadata: dict | None = None


class IdentifyResponse(BaseModel):
    contact_id: UUID
    is_new: bool
    touchpoints_linked: int
