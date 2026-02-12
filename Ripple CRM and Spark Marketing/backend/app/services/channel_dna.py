"""Ripple CRM — Channel DNA Engine.

Analyses interaction history to determine communication preferences:
  - Primary channel (most used)
  - Preferred time window (morning/afternoon/evening)
  - Per-channel sentiment
  - Distribution percentages
"""

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contact import Contact
from app.models.interaction import Interaction


async def compute_channel_dna(db: AsyncSession, contact_id) -> dict:
    """Compute channel DNA for a single contact."""

    result = await db.execute(
        select(Interaction)
        .where(Interaction.contact_id == contact_id)
        .order_by(Interaction.occurred_at.desc())
    )
    interactions = result.scalars().all()

    if not interactions:
        return {
            "contact_id": contact_id,
            "primary_channel": None,
            "preferred_time": None,
            "channels": [],
            "total_interactions": 0,
        }

    total = len(interactions)
    channel_counter = Counter()
    channel_sentiments = defaultdict(list)
    time_counter = Counter()

    for ix in interactions:
        ch = ix.channel or ix.type or "unknown"
        channel_counter[ch] += 1

        if ix.sentiment_score is not None:
            channel_sentiments[ch].append(ix.sentiment_score)

        # Determine time window
        ts = ix.occurred_at
        if ts:
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            hour = ts.hour
            if 5 <= hour < 12:
                time_counter["morning"] += 1
            elif 12 <= hour < 17:
                time_counter["afternoon"] += 1
            else:
                time_counter["evening"] += 1

    # Build channel stats
    channels = []
    for ch, count in channel_counter.most_common():
        avg_sent = None
        if channel_sentiments[ch]:
            avg_sent = round(sum(channel_sentiments[ch]) / len(channel_sentiments[ch]), 2)
        channels.append({
            "channel": ch,
            "count": count,
            "percentage": round((count / total) * 100, 1),
            "avg_sentiment": avg_sent,
        })

    primary = channels[0]["channel"] if channels else None
    preferred_time = time_counter.most_common(1)[0][0] if time_counter else None

    # Store in contact
    dna_json = json.dumps({
        "primary_channel": primary,
        "preferred_time": preferred_time,
        "channels": channels,
    })
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()
    if contact:
        contact.channel_dna_json = dna_json

    return {
        "contact_id": contact_id,
        "primary_channel": primary,
        "preferred_time": preferred_time,
        "channels": channels,
        "total_interactions": total,
    }


async def get_summary(db: AsyncSession) -> dict:
    """Aggregate channel DNA across all contacts."""
    result = await db.execute(
        select(Contact.id, Contact.channel_dna_json)
        .where(Contact.is_deleted == False, Contact.channel_dna_json.isnot(None))  # noqa: E712
    )
    rows = result.all()

    channel_agg = defaultdict(lambda: {"contact_count": 0, "total_interactions": 0, "sentiments": []})

    for _cid, dna_str in rows:
        try:
            dna = json.loads(dna_str)
        except (json.JSONDecodeError, TypeError):
            continue
        for ch_stat in dna.get("channels", []):
            ch = ch_stat["channel"]
            channel_agg[ch]["contact_count"] += 1
            channel_agg[ch]["total_interactions"] += ch_stat["count"]
            if ch_stat.get("avg_sentiment") is not None:
                channel_agg[ch]["sentiments"].append(ch_stat["avg_sentiment"])

    items = []
    for ch, data in sorted(channel_agg.items(), key=lambda x: -x[1]["total_interactions"]):
        avg_sent = None
        if data["sentiments"]:
            avg_sent = round(sum(data["sentiments"]) / len(data["sentiments"]), 2)
        items.append({
            "channel": ch,
            "contact_count": data["contact_count"],
            "total_interactions": data["total_interactions"],
            "avg_sentiment": avg_sent,
        })

    return {
        "items": items,
        "total_contacts_analysed": len(rows),
    }
