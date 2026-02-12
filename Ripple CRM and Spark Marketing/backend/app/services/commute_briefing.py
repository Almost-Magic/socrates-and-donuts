"""Ripple CRM — Commute Briefing Engine (Phase 2.3).

Generates pre-meeting briefings sized to travel time:
  - Quick (≤10 min): key contact info + 3 talking points
  - Standard (10-30 min): + deal status, recent interactions, open items
  - Deep (30+ min): + AI-enriched summary, competitor context, full history

Uses existing data from contacts, deals, interactions, commitments, tasks.
Optional AI enrichment via Supervisor/Ollama.
"""

from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.commitment import Commitment
from app.models.contact import Contact
from app.models.deal import Deal
from app.models.interaction import Interaction
from app.models.meeting import Meeting
from app.models.task import Task


SUPERVISOR_URL = "http://localhost:9000"


def _depth_for_travel(minutes: int) -> str:
    if minutes <= 10:
        return "quick"
    elif minutes <= 30:
        return "standard"
    return "deep"


def _estimated_read_minutes(depth: str, has_ai: bool) -> int:
    base = {"quick": 2, "standard": 5, "deep": 10}
    return base.get(depth, 5) + (2 if has_ai else 0)


def _generate_talking_points(
    contact, deal, interactions, commitments, tasks, depth: str
) -> list[str]:
    """Generate heuristic talking points from available data."""
    points = []

    # Contact basics
    if contact:
        name = f"{contact.first_name} {contact.last_name}"
        if contact.relationship_health_score is not None:
            if contact.relationship_health_score < 40:
                points.append(f"Relationship health is low ({contact.relationship_health_score:.0f}/100) — consider re-engagement strategy")
            elif contact.relationship_health_score >= 80:
                points.append(f"Strong relationship ({contact.relationship_health_score:.0f}/100) — good time for an ask or referral")

        if contact.trust_decay_status in ("at_risk", "dormant"):
            points.append(f"Trust status: {contact.trust_decay_status} — prioritise rebuilding rapport")

        if contact.preferred_channel:
            points.append(f"Preferred channel: {contact.preferred_channel} — follow up via this channel post-meeting")

    # Deal context
    if deal:
        points.append(f"Active deal: {deal.title} ({deal.stage}, ${deal.value:,.0f})" if deal.value else f"Active deal: {deal.title} ({deal.stage})")
        if deal.probability is not None and deal.probability < 50:
            points.append("Deal probability below 50% — identify blockers and next steps")

    # Recent interactions
    if interactions:
        last = interactions[0]
        days_ago = (datetime.now(timezone.utc) - last.occurred_at.replace(tzinfo=timezone.utc if last.occurred_at.tzinfo is None else last.occurred_at.tzinfo)).days
        if days_ago > 30:
            points.append(f"Last interaction was {days_ago} days ago — acknowledge the gap")
        if last.subject:
            points.append(f"Last topic discussed: {last.subject}")

    # Open commitments
    overdue = [c for c in commitments if c.due_date and c.due_date < datetime.now(timezone.utc) and c.status != "completed"]
    if overdue:
        points.append(f"{len(overdue)} overdue commitment(s) — address before making new promises")

    # Open tasks
    pending = [t for t in tasks if t.status in ("pending", "in_progress")]
    if pending and depth != "quick":
        points.append(f"{len(pending)} open task(s) related to this contact")

    # If deep and we still have room, add more context
    if depth == "deep":
        if len(interactions) >= 5:
            sentiments = [i.sentiment_score for i in interactions if i.sentiment_score is not None]
            if sentiments:
                avg = sum(sentiments) / len(sentiments)
                trend = "positive" if avg > 0.5 else "neutral" if avg > 0 else "concerning"
                points.append(f"Overall sentiment trend: {trend} (avg: {avg:.1f})")

    return points[:8]  # Cap at 8 points


async def _try_ai_summary(contact_name: str, talking_points: list[str], depth: str) -> str | None:
    """Try to get AI-enriched summary via Supervisor/Ollama. Returns None if unavailable."""
    if depth == "quick":
        return None

    prompt = (
        f"You are a CRM briefing assistant. Generate a {depth} pre-meeting summary for a meeting with {contact_name}.\n"
        f"Key context:\n" + "\n".join(f"- {p}" for p in talking_points) + "\n\n"
        f"Write a concise {'2-3 sentence' if depth == 'standard' else '4-6 sentence'} briefing paragraph."
    )

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{SUPERVISOR_URL}/api/chat",
                json={
                    "model": "gemma2:27b",
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get("message", {}).get("content") or data.get("choices", [{}])[0].get("message", {}).get("content")
    except Exception:
        pass
    return None


async def generate_commute_briefing(
    db: AsyncSession,
    meeting_id,
    travel_minutes: int = 15,
    format: str = "text",
) -> dict:
    """Generate a commute briefing for a meeting."""

    depth = _depth_for_travel(travel_minutes)
    warnings = []

    # Fetch meeting
    result = await db.execute(select(Meeting).where(Meeting.id == meeting_id))
    meeting = result.scalar_one_or_none()
    if not meeting:
        return None

    contact = None
    deal = None
    interactions = []
    commitments = []
    tasks = []

    # Fetch contact
    if meeting.contact_id:
        result = await db.execute(select(Contact).where(Contact.id == meeting.contact_id))
        contact = result.scalar_one_or_none()

    # Fetch deal
    if meeting.deal_id:
        result = await db.execute(select(Deal).where(Deal.id == meeting.deal_id))
        deal = result.scalar_one_or_none()

    # Fetch recent interactions
    if meeting.contact_id:
        limit = 3 if depth == "quick" else 5 if depth == "standard" else 10
        result = await db.execute(
            select(Interaction)
            .where(Interaction.contact_id == meeting.contact_id)
            .order_by(Interaction.occurred_at.desc())
            .limit(limit)
        )
        interactions = result.scalars().all()

    # Fetch open commitments
    if meeting.contact_id and depth != "quick":
        result = await db.execute(
            select(Commitment)
            .where(
                Commitment.contact_id == meeting.contact_id,
                Commitment.status != "completed",
            )
            .order_by(Commitment.due_date.asc().nullslast())
        )
        commitments = result.scalars().all()

    # Fetch open tasks
    if meeting.contact_id and depth != "quick":
        result = await db.execute(
            select(Task)
            .where(
                Task.contact_id == meeting.contact_id,
                Task.status.in_(["pending", "in_progress"]),
            )
            .order_by(Task.due_date.asc().nullslast())
        )
        tasks = result.scalars().all()

    # Generate talking points
    talking_points = _generate_talking_points(contact, deal, interactions, commitments, tasks, depth)

    # Warnings
    if not contact:
        warnings.append("No contact linked to this meeting — briefing is limited")
    if not interactions:
        warnings.append("No prior interaction history with this contact")

    # Try AI summary for standard/deep
    ai_summary = await _try_ai_summary(
        f"{contact.first_name} {contact.last_name}" if contact else "Unknown",
        talking_points,
        depth,
    )

    # Build contact summary
    contact_summary = None
    if contact:
        last_ix_date = interactions[0].occurred_at if interactions else None
        contact_summary = {
            "name": f"{contact.first_name} {contact.last_name}",
            "role": contact.role,
            "company": contact.company.name if contact.company else None,
            "type": contact.type,
            "relationship_health": contact.relationship_health_score,
            "preferred_channel": contact.preferred_channel,
            "trust_decay_status": contact.trust_decay_status,
            "total_interactions": len(contact.interactions) if contact.interactions else 0,
            "last_interaction_date": last_ix_date.isoformat() if last_ix_date else None,
        }

    # Build deal summary
    deal_summary = None
    if deal:
        days_in_stage = None
        if deal.created_at:
            days_in_stage = (datetime.now(timezone.utc) - deal.created_at.replace(
                tzinfo=timezone.utc if deal.created_at.tzinfo is None else deal.created_at.tzinfo
            )).days
        deal_summary = {
            "title": deal.title,
            "stage": deal.stage,
            "value": deal.value,
            "probability": deal.probability,
            "days_in_stage": days_in_stage,
        }

    # Build recent interactions
    recent_ix = [
        {
            "type": ix.type,
            "channel": ix.channel,
            "subject": ix.subject,
            "occurred_at": ix.occurred_at.isoformat(),
            "sentiment_score": ix.sentiment_score,
        }
        for ix in interactions
    ]

    # Build open items
    open_commitments = [
        {
            "title": c.description or c.type,
            "due_date": c.due_date.isoformat() if c.due_date else None,
            "status": c.status,
            "priority": None,
        }
        for c in commitments[:5]
    ]

    open_tasks = [
        {
            "title": t.title,
            "due_date": t.due_date.isoformat() if t.due_date else None,
            "status": t.status,
            "priority": t.priority,
        }
        for t in tasks[:5]
    ]

    return {
        "meeting_id": str(meeting.id),
        "meeting_title": meeting.title,
        "meeting_time": meeting.scheduled_at.isoformat() if meeting.scheduled_at else None,
        "travel_minutes": travel_minutes,
        "estimated_read_minutes": _estimated_read_minutes(depth, ai_summary is not None),
        "briefing_depth": depth,
        "contact_summary": contact_summary,
        "deal_summary": deal_summary,
        "recent_interactions": recent_ix,
        "open_commitments": open_commitments,
        "open_tasks": open_tasks,
        "talking_points": talking_points,
        "warnings": warnings,
        "ai_summary": ai_summary,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


async def generate_quick_brief(db: AsyncSession, contact_id) -> dict:
    """Generate a quick contact brief (not tied to a meeting)."""

    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()
    if not contact:
        return None

    # Recent interactions
    result = await db.execute(
        select(Interaction)
        .where(Interaction.contact_id == contact_id)
        .order_by(Interaction.occurred_at.desc())
        .limit(5)
    )
    interactions = result.scalars().all()

    # Active deals
    result = await db.execute(
        select(Deal)
        .where(Deal.contact_id == contact_id, Deal.stage != "closed_lost")
    )
    deals = result.scalars().all()

    # Open commitments
    result = await db.execute(
        select(Commitment)
        .where(Commitment.contact_id == contact_id, Commitment.status != "completed")
        .order_by(Commitment.due_date.asc().nullslast())
        .limit(5)
    )
    commitments = result.scalars().all()

    # Talking points
    talking_points = _generate_talking_points(
        contact, deals[0] if deals else None, interactions, commitments, [], "standard"
    )

    last_ix_date = interactions[0].occurred_at if interactions else None

    return {
        "contact_id": str(contact_id),
        "contact_name": f"{contact.first_name} {contact.last_name}",
        "summary": {
            "name": f"{contact.first_name} {contact.last_name}",
            "role": contact.role,
            "company": contact.company.name if contact.company else None,
            "type": contact.type,
            "relationship_health": contact.relationship_health_score,
            "preferred_channel": contact.preferred_channel,
            "trust_decay_status": contact.trust_decay_status,
            "total_interactions": len(contact.interactions) if contact.interactions else 0,
            "last_interaction_date": last_ix_date.isoformat() if last_ix_date else None,
        },
        "active_deals": [
            {
                "title": d.title,
                "stage": d.stage,
                "value": d.value,
                "probability": d.probability,
                "days_in_stage": None,
            }
            for d in deals[:5]
        ],
        "recent_interactions": [
            {
                "type": ix.type,
                "channel": ix.channel,
                "subject": ix.subject,
                "occurred_at": ix.occurred_at.isoformat(),
                "sentiment_score": ix.sentiment_score,
            }
            for ix in interactions
        ],
        "open_commitments": [
            {
                "title": c.description or c.type,
                "due_date": c.due_date.isoformat() if c.due_date else None,
                "status": c.status,
                "priority": None,
            }
            for c in commitments
        ],
        "talking_points": talking_points,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
