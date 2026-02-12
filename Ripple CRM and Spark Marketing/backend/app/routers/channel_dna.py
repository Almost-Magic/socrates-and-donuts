"""Ripple CRM — Channel DNA API routes (enhanced Phase 2.2)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.contact import Contact
from app.services.channel_dna import compute_channel_dna, get_summary

router = APIRouter(prefix="/channel-dna", tags=["channel-dna"])


@router.get("/summary")
async def channel_dna_summary(db: AsyncSession = Depends(get_db)):
    return await get_summary(db)


# Contact-scoped endpoints
contact_router = APIRouter(prefix="/contacts", tags=["channel-dna"])


@contact_router.get("/{contact_id}/channel-dna")
async def get_channel_dna(contact_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    # Verify contact exists
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id, Contact.is_deleted == False)  # noqa: E712
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Contact not found")
    dna = await compute_channel_dna(db, contact_id)
    await db.commit()
    return dna


@contact_router.post("/{contact_id}/channel-dna/refresh")
async def refresh_channel_dna(contact_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    # Verify contact exists
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id, Contact.is_deleted == False)  # noqa: E712
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Contact not found")
    dna = await compute_channel_dna(db, contact_id)
    await db.commit()
    return dna
