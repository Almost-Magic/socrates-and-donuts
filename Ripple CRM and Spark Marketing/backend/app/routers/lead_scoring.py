"""Ripple CRM — Lead Scoring (Three Brains) API routes."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.three_brains import calculate_lead_score, get_leaderboard, recalculate_all

router = APIRouter(prefix="/lead-scores", tags=["lead-scoring"])


@router.get("/top")
async def leaderboard(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    items = await get_leaderboard(db, limit=limit)
    return {"items": items, "total": len(items)}


@router.post("/recalculate-all")
async def recalculate_all_scores(db: AsyncSession = Depends(get_db)):
    count = await recalculate_all(db)
    return {"recalculated": count}


# Contact-scoped endpoints (mounted separately)
contact_router = APIRouter(prefix="/contacts", tags=["lead-scoring"])


@contact_router.get("/{contact_id}/lead-score")
async def get_lead_score(contact_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await calculate_lead_score(db, contact_id)
    if not result:
        raise HTTPException(status_code=404, detail="Contact not found")
    await db.commit()
    return result


@contact_router.post("/{contact_id}/lead-score/recalculate")
async def recalculate_lead_score(contact_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await calculate_lead_score(db, contact_id)
    if not result:
        raise HTTPException(status_code=404, detail="Contact not found")
    await db.commit()
    return result
