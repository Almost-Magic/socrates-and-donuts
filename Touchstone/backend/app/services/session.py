"""Touchstone — Session stitching: anonymous -> known contact."""

from datetime import datetime, timezone

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contact import Contact
from app.models.touchpoint import Touchpoint
from app.schemas.identify import IdentifyRequest, IdentifyResponse


async def identify_contact(db: AsyncSession, req: IdentifyRequest) -> IdentifyResponse:
    """Create or update contact and backfill anonymous touchpoints."""
    is_new = False

    # Check if contact with this email already exists
    result = await db.execute(
        select(Contact).where(Contact.email == req.email).limit(1)
    )
    contact = result.scalar_one_or_none()

    if contact:
        # Update existing contact with new info
        if req.name and not contact.name:
            contact.name = req.name
        if req.company and not contact.company:
            contact.company = req.company
        if req.anonymous_id and not contact.anonymous_id:
            contact.anonymous_id = req.anonymous_id
        if req.metadata:
            existing = contact.metadata_ or {}
            existing.update(req.metadata)
            contact.metadata_ = existing
    else:
        is_new = True
        contact = Contact(
            anonymous_id=req.anonymous_id,
            email=req.email,
            name=req.name,
            company=req.company,
            metadata_=req.metadata or {},
            identified_at=datetime.now(timezone.utc),
        )
        db.add(contact)
        await db.flush()  # Get the ID

    # Backfill: link all anonymous touchpoints to this contact
    backfill_result = await db.execute(
        update(Touchpoint)
        .where(Touchpoint.anonymous_id == req.anonymous_id)
        .where(Touchpoint.contact_id.is_(None))
        .values(contact_id=contact.id)
    )
    touchpoints_linked = backfill_result.rowcount

    await db.commit()

    return IdentifyResponse(
        contact_id=contact.id,
        is_new=is_new,
        touchpoints_linked=touchpoints_linked,
    )
