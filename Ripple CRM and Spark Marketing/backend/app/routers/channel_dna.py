"""Ripple CRM — Channel DNA API routes."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.channel_dna import compute_channel_dna, get_summary

router = APIRouter(prefix="/channel-dna", tags=["channel-dna"])


@router.get("/summary")
async def channel_dna_summary(db: AsyncSession = Depends(get_db)):
    return await get_summary(db)


# Contact-scoped endpoints
contact_router = APIRouter(prefix="/contacts", tags=["channel-dna"])


@contact_router.get("/{contact_id}/channel-dna")
async def get_channel_dna(contact_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await compute_channel_dna(db, contact_id)
    await db.commit()
    return result


@contact_router.post("/{contact_id}/channel-dna/refresh")
async def refresh_channel_dna(contact_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await compute_channel_dna(db, contact_id)
    await db.commit()
    return result
