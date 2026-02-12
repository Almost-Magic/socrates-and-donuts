"""Ripple CRM — Trust Decay API routes."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.trust_decay import compute_trust_decay, get_at_risk, recalculate_all

router = APIRouter(prefix="/trust-decay", tags=["trust-decay"])


@router.get("/at-risk")
async def at_risk_contacts(db: AsyncSession = Depends(get_db)):
    items = await get_at_risk(db)
    return {"items": items, "total": len(items)}


@router.post("/recalculate-all")
async def recalculate_all_decay(db: AsyncSession = Depends(get_db)):
    count = await recalculate_all(db)
    return {"recalculated": count}


# Contact-scoped endpoint
contact_router = APIRouter(prefix="/contacts", tags=["trust-decay"])


@contact_router.get("/{contact_id}/trust-decay")
async def get_trust_decay(contact_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await compute_trust_decay(db, contact_id)
    await db.commit()
    return result
