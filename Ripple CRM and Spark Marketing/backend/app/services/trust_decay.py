"""Ripple CRM — Trust Decay Engine.

Computes baseline-relative decay for contacts:
  - healthy:  gap < 1.5x baseline
  - cooling:  1.5x - 3x baseline
  - at_risk:  3x - 5x baseline
  - dormant:  > 5x baseline (or no interactions)
"""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contact import Contact
from app.models.interaction import Interaction


async def compute_trust_decay(db: AsyncSession, contact_id) -> dict:
    """Compute trust decay for a single contact."""

    result = await db.execute(
        select(Interaction.occurred_at)
        .where(Interaction.contact_id == contact_id)
        .order_by(Interaction.occurred_at.desc())
    )
    timestamps = [r for (r,) in result.all()]

    now = datetime.now(timezone.utc)

    if not timestamps:
        status = "dormant"
        return {
            "contact_id": contact_id,
            "status": status,
            "days_since_last": None,
            "baseline_gap_days": None,
            "decay_ratio": None,
            "last_interaction_at": None,
            "interaction_count": 0,
        }

    # Ensure timezone awareness
    clean_ts = []
    for ts in timestamps:
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        clean_ts.append(ts)

    last = clean_ts[0]
    days_since = (now - last).days

    # Compute baseline gap (average gap between consecutive interactions)
    if len(clean_ts) >= 2:
        gaps = []
        for i in range(len(clean_ts) - 1):
            gap = (clean_ts[i] - clean_ts[i + 1]).days
            if gap > 0:
                gaps.append(gap)
        baseline_gap = sum(gaps) / len(gaps) if gaps else 30.0
    else:
        baseline_gap = 30.0  # default if only one interaction

    # Compute decay ratio
    if baseline_gap > 0:
        decay_ratio = round(days_since / baseline_gap, 2)
    else:
        decay_ratio = 0.0

    # Determine status
    if decay_ratio < 1.5:
        status = "healthy"
    elif decay_ratio < 3.0:
        status = "cooling"
    elif decay_ratio < 5.0:
        status = "at_risk"
    else:
        status = "dormant"

    # Update contact
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()
    if contact:
        contact.trust_decay_status = status
        contact.trust_decay_days = days_since

    return {
        "contact_id": contact_id,
        "status": status,
        "days_since_last": days_since,
        "baseline_gap_days": round(baseline_gap, 1),
        "decay_ratio": decay_ratio,
        "last_interaction_at": last,
        "interaction_count": len(clean_ts),
    }


async def get_at_risk(db: AsyncSession) -> list[dict]:
    """Get all contacts with at_risk or dormant trust decay status."""
    result = await db.execute(
        select(Contact)
        .where(
            Contact.is_deleted == False,  # noqa: E712
            Contact.trust_decay_status.in_(["at_risk", "dormant", "cooling"]),
        )
        .order_by(Contact.trust_decay_days.desc().nullslast())
    )
    contacts = result.scalars().all()
    return [
        {
            "contact_id": c.id,
            "contact_name": f"{c.first_name} {c.last_name}",
            "status": c.trust_decay_status or "unknown",
            "days_since_last": c.trust_decay_days,
            "decay_ratio": None,
            "relationship_health_score": c.relationship_health_score,
        }
        for c in contacts
    ]


async def recalculate_all(db: AsyncSession) -> int:
    """Recalculate trust decay for all non-deleted contacts."""
    result = await db.execute(
        select(Contact.id).where(Contact.is_deleted == False)  # noqa: E712
    )
    contact_ids = result.scalars().all()
    count = 0
    for cid in contact_ids:
        await compute_trust_decay(db, cid)
        count += 1
    await db.commit()
    return count
