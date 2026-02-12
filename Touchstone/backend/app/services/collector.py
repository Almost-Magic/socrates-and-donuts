"""Touchstone — Event collection service."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contact import Contact
from app.models.touchpoint import Touchpoint
from app.schemas.collect import CollectEvent


async def process_event(db: AsyncSession, event: CollectEvent) -> None:
    """Process a tracking pixel event. Must be fast (sub-50ms target)."""
    contact_id = None

    # Check if anonymous_id is already linked to a known contact
    result = await db.execute(
        select(Contact.id).where(Contact.anonymous_id == event.anonymous_id).limit(1)
    )
    row = result.scalar_one_or_none()
    if row:
        contact_id = row

    tp = Touchpoint(
        contact_id=contact_id,
        anonymous_id=event.anonymous_id,
        channel=event.channel or _infer_channel(event.source, event.medium),
        source=event.source,
        medium=event.medium,
        utm_campaign=event.utm_campaign,
        utm_content=event.utm_content,
        utm_term=event.utm_term,
        touchpoint_type=event.touchpoint_type,
        page_url=event.page_url,
        referrer_url=event.referrer_url,
        metadata_=event.metadata or {},
        timestamp=event.timestamp or datetime.now(timezone.utc),
    )
    db.add(tp)
    await db.commit()


def _infer_channel(source: str | None, medium: str | None) -> str | None:
    """Infer channel from source/medium if not explicitly set."""
    if not medium:
        return None
    medium_lower = medium.lower()
    if medium_lower in ("cpc", "ppc", "paid"):
        return "paid"
    if medium_lower in ("email",):
        return "email"
    if medium_lower in ("social",):
        return "social"
    if medium_lower in ("organic",):
        return "organic"
    if medium_lower in ("referral",):
        return "referral"
    return None
