"""Ripple CRM — Channel DNA Engine v2 (Phase 2.2).

Enhanced with granular channel_interactions table:
  - Response latency by channel
  - Response rates by time-of-day and day-of-week
  - Per-contact profile: "Best channel: SMS > Email > Phone. Best time: Tue/Thu 10-12"
  - Preferred times stored in contact.preferred_times_json
"""

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.channel_interaction import ChannelInteraction
from app.models.contact import Contact
from app.models.interaction import Interaction


DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _time_slot(hour: int) -> str:
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    else:
        return "evening"


async def compute_channel_dna(db: AsyncSession, contact_id) -> dict:
    """Compute channel DNA for a single contact using both tables."""

    # --- Pull from legacy interactions table ---
    result = await db.execute(
        select(Interaction)
        .where(Interaction.contact_id == contact_id)
        .order_by(Interaction.occurred_at.desc())
    )
    interactions = result.scalars().all()

    # --- Pull from new channel_interactions table ---
    result2 = await db.execute(
        select(ChannelInteraction)
        .where(ChannelInteraction.contact_id == contact_id)
        .order_by(ChannelInteraction.occurred_at.desc())
    )
    channel_ixs = result2.scalars().all()

    total_legacy = len(interactions)
    total_granular = len(channel_ixs)

    if total_legacy == 0 and total_granular == 0:
        return {
            "contact_id": str(contact_id),
            "primary_channel": None,
            "preferred_time": None,
            "channels": [],
            "total_interactions": 0,
            "response_rates": {},
            "best_time_slots": [],
            "channel_ranking": [],
        }

    channel_counter = Counter()
    channel_sentiments = defaultdict(list)
    time_counter = Counter()

    # Process legacy interactions
    for ix in interactions:
        ch = ix.channel or ix.type or "unknown"
        channel_counter[ch] += 1
        if ix.sentiment_score is not None:
            channel_sentiments[ch].append(ix.sentiment_score)
        ts = ix.occurred_at
        if ts:
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            time_counter[_time_slot(ts.hour)] += 1

    # Process granular channel interactions — response tracking
    channel_response_times = defaultdict(list)
    channel_responded = defaultdict(lambda: {"total": 0, "responded": 0})
    day_response = defaultdict(lambda: {"total": 0, "responded": 0})
    hour_response = defaultdict(lambda: {"total": 0, "responded": 0})
    day_of_week_counter = Counter()
    hour_of_day_counter = Counter()

    for ci in channel_ixs:
        ch = ci.channel
        channel_counter[ch] += 1

        # Response tracking (outbound only)
        if ci.direction == "out":
            channel_responded[ch]["total"] += 1
            if ci.responded:
                channel_responded[ch]["responded"] += 1
                if ci.response_time_seconds is not None:
                    channel_response_times[ch].append(ci.response_time_seconds)

        # Time-of-day / day-of-week tracking
        ts = ci.occurred_at
        if ts:
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            time_counter[_time_slot(ts.hour)] += 1

        dow = ci.day_of_week
        hod = ci.hour_of_day
        if dow is not None:
            day_of_week_counter[dow] += 1
            day_response[dow]["total"] += 1
            if ci.responded:
                day_response[dow]["responded"] += 1
        if hod is not None:
            hour_of_day_counter[hod] += 1
            hour_response[hod]["total"] += 1
            if ci.responded:
                hour_response[hod]["responded"] += 1

    # Build channel stats
    total = sum(channel_counter.values())
    channels = []
    for ch, count in channel_counter.most_common():
        avg_sent = None
        if channel_sentiments[ch]:
            avg_sent = round(sum(channel_sentiments[ch]) / len(channel_sentiments[ch]), 2)
        avg_resp_time = None
        if channel_response_times[ch]:
            avg_resp_time = round(sum(channel_response_times[ch]) / len(channel_response_times[ch]))
        resp_rate = None
        if channel_responded[ch]["total"] > 0:
            resp_rate = round(
                channel_responded[ch]["responded"] / channel_responded[ch]["total"] * 100, 1
            )
        channels.append({
            "channel": ch,
            "count": count,
            "percentage": round((count / total) * 100, 1) if total else 0,
            "avg_sentiment": avg_sent,
            "avg_response_time_seconds": avg_resp_time,
            "response_rate": resp_rate,
        })

    # Channel ranking by response rate (best first)
    ranked = sorted(
        [c for c in channels if c.get("response_rate") is not None],
        key=lambda x: (-x["response_rate"], x.get("avg_response_time_seconds") or 999999),
    )
    channel_ranking = [c["channel"] for c in ranked]

    # Response rates by channel
    response_rates = {}
    for ch, data in channel_responded.items():
        if data["total"] > 0:
            response_rates[ch] = round(data["responded"] / data["total"] * 100, 1)

    # Best time slots — day/hour combos with best response rates
    best_time_slots = []
    for dow in sorted(day_response.keys()):
        data = day_response[dow]
        if data["total"] >= 1:
            rate = round(data["responded"] / data["total"] * 100, 1) if data["total"] else 0
            best_time_slots.append({
                "day": DAY_NAMES[dow] if 0 <= dow < 7 else str(dow),
                "day_of_week": dow,
                "outreach_count": data["total"],
                "response_rate": rate,
            })
    best_time_slots.sort(key=lambda x: -x["response_rate"])

    primary = channels[0]["channel"] if channels else None
    preferred_time = time_counter.most_common(1)[0][0] if time_counter else None

    # Preferred times data
    preferred_times = {
        "preferred_time_slot": preferred_time,
        "best_days": [s["day"] for s in best_time_slots[:3]],
        "best_hours": [
            h for h, _ in sorted(hour_response.items(),
                                  key=lambda x: -(x[1]["responded"] / x[1]["total"] if x[1]["total"] else 0))
            if hour_response[h]["total"] >= 1
        ][:3],
    }

    # Store in contact
    dna_json = json.dumps({
        "primary_channel": primary,
        "preferred_time": preferred_time,
        "channels": channels,
        "channel_ranking": channel_ranking,
        "response_rates": response_rates,
    })
    preferred_times_json = json.dumps(preferred_times)

    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()
    if contact:
        contact.channel_dna_json = dna_json
        contact.preferred_channel = primary
        contact.preferred_times_json = preferred_times_json

    return {
        "contact_id": str(contact_id),
        "primary_channel": primary,
        "preferred_time": preferred_time,
        "channels": channels,
        "total_interactions": total,
        "response_rates": response_rates,
        "best_time_slots": best_time_slots,
        "channel_ranking": channel_ranking,
    }


async def get_channel_profile(db: AsyncSession, contact_id) -> dict:
    """Get enhanced channel profile for a contact."""
    # Pull channel_interactions for this contact
    result = await db.execute(
        select(ChannelInteraction)
        .where(ChannelInteraction.contact_id == contact_id)
        .order_by(ChannelInteraction.occurred_at.desc())
    )
    channel_ixs = result.scalars().all()

    channel_stats = defaultdict(lambda: {
        "total_out": 0, "total_in": 0, "responded": 0,
        "response_times": [], "hours": [], "days": [],
    })

    for ci in channel_ixs:
        ch = ci.channel
        if ci.direction == "out":
            channel_stats[ch]["total_out"] += 1
            if ci.responded:
                channel_stats[ch]["responded"] += 1
                if ci.response_time_seconds is not None:
                    channel_stats[ch]["response_times"].append(ci.response_time_seconds)
        else:
            channel_stats[ch]["total_in"] += 1
        if ci.hour_of_day is not None:
            channel_stats[ch]["hours"].append(ci.hour_of_day)
        if ci.day_of_week is not None:
            channel_stats[ch]["days"].append(ci.day_of_week)

    stats_list = []
    response_rates = {}
    total_outreach = 0
    total_responded = 0

    for ch, data in sorted(channel_stats.items(), key=lambda x: -(x[1]["total_out"] + x[1]["total_in"])):
        total_out = data["total_out"]
        total_outreach += total_out
        responded = data["responded"]
        total_responded += responded
        rate = round(responded / total_out * 100, 1) if total_out > 0 else None
        response_rates[ch] = rate

        avg_resp = None
        if data["response_times"]:
            avg_resp = round(sum(data["response_times"]) / len(data["response_times"]))

        stats_list.append({
            "channel": ch,
            "outbound": total_out,
            "inbound": data["total_in"],
            "responded": responded,
            "response_rate": rate,
            "avg_response_time_seconds": avg_resp,
        })

    # Best time slots
    day_hour_combos = defaultdict(lambda: {"total": 0, "responded": 0})
    for ci in channel_ixs:
        if ci.direction == "out" and ci.day_of_week is not None and ci.hour_of_day is not None:
            key = (ci.day_of_week, ci.hour_of_day)
            day_hour_combos[key]["total"] += 1
            if ci.responded:
                day_hour_combos[key]["responded"] += 1

    best_slots = []
    for (dow, hod), data in sorted(
        day_hour_combos.items(),
        key=lambda x: -(x[1]["responded"] / x[1]["total"] if x[1]["total"] else 0),
    ):
        if data["total"] >= 1:
            best_slots.append({
                "day": DAY_NAMES[dow] if 0 <= dow < 7 else str(dow),
                "hour": hod,
                "outreach_count": data["total"],
                "response_rate": round(data["responded"] / data["total"] * 100, 1),
            })
    best_slots = best_slots[:10]

    preferred = stats_list[0]["channel"] if stats_list else None
    overall_rate = round(total_responded / total_outreach * 100, 1) if total_outreach > 0 else None

    return {
        "contact_id": str(contact_id),
        "preferred_channel": preferred,
        "preferred_times": None,
        "channel_stats": stats_list,
        "response_rates": response_rates,
        "best_time_slots": best_slots,
        "total_outreach": total_outreach,
        "overall_response_rate": overall_rate,
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
