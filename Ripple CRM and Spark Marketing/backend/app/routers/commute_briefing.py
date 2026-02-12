"""Ripple CRM — Commute Briefing API routes (Phase 2.3).

Pre-meeting briefings sized to travel time.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.commute_briefing import generate_commute_briefing, generate_quick_brief

router = APIRouter(prefix="/briefings", tags=["briefings"])
meeting_router = APIRouter(prefix="/meetings", tags=["briefings"])
contact_router = APIRouter(prefix="/contacts", tags=["briefings"])


@meeting_router.post("/{meeting_id}/commute-briefing")
async def commute_briefing(
    meeting_id: uuid.UUID,
    travel_minutes: int = Query(15, ge=1, le=180),
    format: str = Query("text", pattern="^(text|bullet|detailed)$"),
    db: AsyncSession = Depends(get_db),
):
    """Generate a commute briefing for a meeting, sized to travel time."""
    result = await generate_commute_briefing(db, meeting_id, travel_minutes, format)
    if result is None:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return result


@contact_router.get("/{contact_id}/quick-brief")
async def quick_brief(
    contact_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Generate a quick contact brief (not tied to a meeting)."""
    result = await generate_quick_brief(db, contact_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return result


@router.get("/depths")
async def briefing_depths():
    """Return the briefing depth thresholds."""
    return {
        "depths": [
            {"name": "quick", "travel_minutes_max": 10, "description": "Key contact info + 3 talking points"},
            {"name": "standard", "travel_minutes_max": 30, "description": "Deal status, recent interactions, open items"},
            {"name": "deep", "travel_minutes_max": 180, "description": "Full history, AI-enriched summary, sentiment trends"},
        ]
    }
