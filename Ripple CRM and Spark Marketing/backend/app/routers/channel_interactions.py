"""Ripple CRM — Channel Interactions API routes (Phase 2.2).

Granular outreach event logging with response tracking.
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.channel_interaction import ChannelInteraction
from app.models.contact import Contact
from app.schemas.channel_interaction import (
    ChannelInteractionCreate,
    ChannelInteractionListResponse,
    ChannelInteractionResponse,
    ChannelProfileResponse,
)
from app.services.audit import log_action
from app.services.channel_dna import get_channel_profile

router = APIRouter(prefix="/channel-interactions", tags=["channel-interactions"])
contact_router = APIRouter(prefix="/contacts", tags=["channel-interactions"])


@router.post("", response_model=ChannelInteractionResponse, status_code=201)
async def create_channel_interaction(
    data: ChannelInteractionCreate, db: AsyncSession = Depends(get_db)
):
    """Log a channel interaction (outreach event)."""
    # Verify contact exists
    result = await db.execute(
        select(Contact).where(Contact.id == data.contact_id, Contact.is_deleted == False)  # noqa: E712
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Contact not found")

    occurred = data.occurred_at or datetime.now(timezone.utc)
    if occurred.tzinfo is None:
        occurred = occurred.replace(tzinfo=timezone.utc)

    ci = ChannelInteraction(
        contact_id=data.contact_id,
        channel=data.channel,
        direction=data.direction,
        occurred_at=occurred,
        response_time_seconds=data.response_time_seconds,
        responded=data.responded,
        day_of_week=occurred.weekday(),
        hour_of_day=occurred.hour,
    )
    db.add(ci)
    await db.flush()
    await log_action(db, "channel_interaction", str(ci.id), "create")
    await db.commit()
    await db.refresh(ci)
    return ci


@router.get("", response_model=ChannelInteractionListResponse)
async def list_channel_interactions(
    contact_id: uuid.UUID | None = Query(None),
    channel: str | None = Query(None),
    direction: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List channel interactions with optional filters."""
    q = select(ChannelInteraction).order_by(ChannelInteraction.occurred_at.desc())

    if contact_id:
        q = q.where(ChannelInteraction.contact_id == contact_id)
    if channel:
        q = q.where(ChannelInteraction.channel == channel)
    if direction:
        q = q.where(ChannelInteraction.direction == direction)

    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    q = q.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(q)
    items = result.scalars().all()

    return ChannelInteractionListResponse(items=items, total=total)


@router.get("/{interaction_id}", response_model=ChannelInteractionResponse)
async def get_channel_interaction(
    interaction_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ChannelInteraction).where(ChannelInteraction.id == interaction_id)
    )
    ci = result.scalar_one_or_none()
    if not ci:
        raise HTTPException(status_code=404, detail="Channel interaction not found")
    return ci


@router.delete("/{interaction_id}")
async def delete_channel_interaction(
    interaction_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ChannelInteraction).where(ChannelInteraction.id == interaction_id)
    )
    ci = result.scalar_one_or_none()
    if not ci:
        raise HTTPException(status_code=404, detail="Channel interaction not found")

    await db.delete(ci)
    await log_action(db, "channel_interaction", str(interaction_id), "delete")
    await db.commit()
    return {"detail": "Channel interaction deleted"}


# Contact-scoped: channel profile
@contact_router.get("/{contact_id}/channel-profile", response_model=ChannelProfileResponse)
async def contact_channel_profile(
    contact_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    """Get enhanced channel profile for a contact from channel_interactions."""
    # Verify contact exists
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id, Contact.is_deleted == False)  # noqa: E712
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Contact not found")

    profile = await get_channel_profile(db, contact_id)
    return profile


@contact_router.get("/{contact_id}/channel-interactions", response_model=ChannelInteractionListResponse)
async def contact_channel_interactions(
    contact_id: uuid.UUID,
    channel: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List channel interactions for a specific contact."""
    q = (
        select(ChannelInteraction)
        .where(ChannelInteraction.contact_id == contact_id)
        .order_by(ChannelInteraction.occurred_at.desc())
    )
    if channel:
        q = q.where(ChannelInteraction.channel == channel)

    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    q = q.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(q)
    items = result.scalars().all()

    return ChannelInteractionListResponse(items=items, total=total)
