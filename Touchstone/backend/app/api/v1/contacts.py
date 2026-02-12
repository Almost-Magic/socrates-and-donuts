"""Touchstone — Contact listing and journey endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.contact import Contact
from app.models.touchpoint import Touchpoint
from app.schemas.contact import ContactOut, TouchpointOut, JourneyResponse

router = APIRouter(tags=["contacts"])


@router.get("/contacts")
async def list_contacts(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Contact).order_by(Contact.created_at.desc()).limit(limit).offset(offset)
    )
    contacts = result.scalars().all()
    items = []
    for c in contacts:
        count_result = await db.execute(
            select(func.count()).where(Touchpoint.contact_id == c.id)
        )
        count = count_result.scalar() or 0
        items.append(ContactOut(
            id=c.id,
            anonymous_id=c.anonymous_id,
            email=c.email,
            name=c.name,
            company=c.company,
            metadata=c.metadata_,
            identified_at=c.identified_at,
            touchpoint_count=count,
            created_at=c.created_at,
            updated_at=c.updated_at,
        ))
    total_result = await db.execute(select(func.count()).select_from(Contact))
    total = total_result.scalar() or 0
    return {"items": items, "total": total}


@router.get("/contacts/{contact_id}/journey", response_model=JourneyResponse)
async def contact_journey(contact_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    tp_result = await db.execute(
        select(Touchpoint)
        .where(Touchpoint.contact_id == contact_id)
        .order_by(Touchpoint.timestamp.asc())
    )
    touchpoints = tp_result.scalars().all()

    count_result = await db.execute(
        select(func.count()).where(Touchpoint.contact_id == contact_id)
    )
    total = count_result.scalar() or 0

    return JourneyResponse(
        contact=ContactOut(
            id=contact.id,
            anonymous_id=contact.anonymous_id,
            email=contact.email,
            name=contact.name,
            company=contact.company,
            metadata=contact.metadata_,
            identified_at=contact.identified_at,
            touchpoint_count=total,
            created_at=contact.created_at,
            updated_at=contact.updated_at,
        ),
        touchpoints=[
            TouchpointOut(
                id=tp.id,
                contact_id=tp.contact_id,
                anonymous_id=tp.anonymous_id,
                campaign_id=tp.campaign_id,
                channel=tp.channel,
                source=tp.source,
                medium=tp.medium,
                utm_campaign=tp.utm_campaign,
                utm_content=tp.utm_content,
                utm_term=tp.utm_term,
                touchpoint_type=tp.touchpoint_type,
                page_url=tp.page_url,
                referrer_url=tp.referrer_url,
                metadata=tp.metadata_,
                timestamp=tp.timestamp,
                created_at=tp.created_at,
            )
            for tp in touchpoints
        ],
        total_touchpoints=total,
    )
