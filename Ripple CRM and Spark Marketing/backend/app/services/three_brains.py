"""Ripple CRM — Three Brains Lead Scoring Engine (Heuristic v1).

Scores contacts across three dimensions:
  - Fit Brain (40%):     Data completeness + company association + tag richness
  - Intent Brain (35%):  Recent interactions, recency, deal progression, task completion
  - Instinct Brain (25%): Sentiment, relationship health, commitment fulfilment
"""

import json
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.commitment import Commitment
from app.models.contact import Contact
from app.models.deal import Deal
from app.models.interaction import Interaction
from app.models.lead_score import LeadScore
from app.models.tag import contact_tags
from app.models.task import Task


async def calculate_lead_score(db: AsyncSession, contact_id) -> dict:
    """Calculate Three Brains lead score for a single contact."""

    # Fetch contact
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()
    if not contact:
        return None

    now = datetime.now(timezone.utc)
    thirty_days_ago = now - timedelta(days=30)

    # ── Fit Brain (40%) ────────────────────────────────────────
    fit_components = {}

    # Data completeness: check key fields
    fields = ["email", "phone", "role", "title", "linkedin_url"]
    filled = sum(1 for f in fields if getattr(contact, f, None))
    fit_components["data_completeness"] = round((filled / len(fields)) * 100, 1)

    # Company association
    fit_components["has_company"] = 100.0 if contact.company_id else 0.0

    # Tag richness
    tag_count_q = select(func.count()).select_from(contact_tags).where(
        contact_tags.c.contact_id == contact_id
    )
    tag_count = (await db.execute(tag_count_q)).scalar() or 0
    fit_components["tag_richness"] = min(100.0, tag_count * 25.0)  # 4+ tags = 100

    fit_score = round(
        fit_components["data_completeness"] * 0.50
        + fit_components["has_company"] * 0.30
        + fit_components["tag_richness"] * 0.20,
        1,
    )

    # ── Intent Brain (35%) ─────────────────────────────────────
    intent_components = {}

    # Recent interactions (30d)
    result = await db.execute(
        select(func.count()).where(
            Interaction.contact_id == contact_id,
            Interaction.occurred_at >= thirty_days_ago,
        )
    )
    recent_count = result.scalar() or 0
    intent_components["recent_interactions"] = min(100.0, recent_count * 15.0)  # 7+ = 100

    # Interaction recency
    result = await db.execute(
        select(Interaction.occurred_at)
        .where(Interaction.contact_id == contact_id)
        .order_by(Interaction.occurred_at.desc())
        .limit(1)
    )
    last_interaction = result.scalar_one_or_none()
    if last_interaction:
        if last_interaction.tzinfo is None:
            last_interaction = last_interaction.replace(tzinfo=timezone.utc)
        days_since = (now - last_interaction).days
        if days_since <= 7:
            intent_components["recency"] = 100.0
        elif days_since <= 14:
            intent_components["recency"] = 80.0
        elif days_since <= 30:
            intent_components["recency"] = 50.0
        else:
            intent_components["recency"] = max(0, 30 - days_since * 0.3)
    else:
        intent_components["recency"] = 0.0

    # Deal stage progression
    result = await db.execute(
        select(Deal.stage).where(
            Deal.contact_id == contact_id, Deal.is_deleted == False  # noqa: E712
        )
    )
    stages = [r for (r,) in result.all()]
    stage_weights = {"lead": 10, "qualified": 30, "proposal": 50, "negotiation": 70, "closed_won": 100}
    if stages:
        best_stage = max(stage_weights.get(s, 0) for s in stages)
        intent_components["deal_progression"] = float(best_stage)
    else:
        intent_components["deal_progression"] = 0.0

    # Task completion rate
    result = await db.execute(
        select(Task.status).where(Task.contact_id == contact_id)
    )
    task_statuses = [r for (r,) in result.all()]
    if task_statuses:
        done = sum(1 for s in task_statuses if s in ("done", "completed"))
        intent_components["task_completion"] = round((done / len(task_statuses)) * 100, 1)
    else:
        intent_components["task_completion"] = 50.0  # neutral

    intent_score = round(
        intent_components["recent_interactions"] * 0.30
        + intent_components["recency"] * 0.30
        + intent_components["deal_progression"] * 0.25
        + intent_components["task_completion"] * 0.15,
        1,
    )

    # ── Instinct Brain (25%) ───────────────────────────────────
    instinct_components = {}

    # Average sentiment
    result = await db.execute(
        select(Interaction.sentiment_score)
        .where(
            Interaction.contact_id == contact_id,
            Interaction.sentiment_score.isnot(None),
        )
        .order_by(Interaction.occurred_at.desc())
        .limit(10)
    )
    sentiments = [r for (r,) in result.all()]
    if sentiments:
        avg_sent = sum(sentiments) / len(sentiments)
        instinct_components["sentiment"] = round(max(0, min(100, (avg_sent + 1) * 50)), 1)
    else:
        instinct_components["sentiment"] = 50.0

    # Relationship health
    health = contact.relationship_health_score
    instinct_components["relationship_health"] = round(health, 1) if health else 50.0

    # Commitment fulfilment
    result = await db.execute(
        select(Commitment.status).where(Commitment.contact_id == contact_id)
    )
    commitment_statuses = [r for (r,) in result.all()]
    if commitment_statuses:
        fulfilled = sum(1 for s in commitment_statuses if s == "fulfilled")
        instinct_components["commitment_fulfilment"] = round(
            (fulfilled / len(commitment_statuses)) * 100, 1
        )
    else:
        instinct_components["commitment_fulfilment"] = 50.0

    instinct_score = round(
        instinct_components["sentiment"] * 0.40
        + instinct_components["relationship_health"] * 0.35
        + instinct_components["commitment_fulfilment"] * 0.25,
        1,
    )

    # ── Composite ──────────────────────────────────────────────
    composite = round(fit_score * 0.40 + intent_score * 0.35 + instinct_score * 0.25, 1)

    # Upsert lead score
    result = await db.execute(
        select(LeadScore)
        .where(LeadScore.contact_id == contact_id)
        .order_by(LeadScore.calculated_at.desc())
        .limit(1)
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.fit_score = fit_score
        existing.intent_score = intent_score
        existing.instinct_score = instinct_score
        existing.composite_score = composite
        existing.fit_breakdown = json.dumps({"score": fit_score, "components": fit_components})
        existing.intent_breakdown = json.dumps({"score": intent_score, "components": intent_components})
        existing.instinct_breakdown = json.dumps({"score": instinct_score, "components": instinct_components})
        existing.calculated_at = now
        lead_score = existing
    else:
        lead_score = LeadScore(
            contact_id=contact_id,
            fit_score=fit_score,
            intent_score=intent_score,
            instinct_score=instinct_score,
            composite_score=composite,
            fit_breakdown=json.dumps({"score": fit_score, "components": fit_components}),
            intent_breakdown=json.dumps({"score": intent_score, "components": intent_components}),
            instinct_breakdown=json.dumps({"score": instinct_score, "components": instinct_components}),
            calculated_at=now,
        )
        db.add(lead_score)

    await db.flush()
    await db.refresh(lead_score)

    return {
        "id": lead_score.id,
        "contact_id": contact_id,
        "fit_score": fit_score,
        "intent_score": intent_score,
        "instinct_score": instinct_score,
        "composite_score": composite,
        "fit_breakdown": {"score": fit_score, "components": fit_components},
        "intent_breakdown": {"score": intent_score, "components": intent_components},
        "instinct_breakdown": {"score": instinct_score, "components": instinct_components},
        "calculated_at": lead_score.calculated_at,
    }


async def get_leaderboard(db: AsyncSession, limit: int = 20) -> list[dict]:
    """Get top contacts by composite lead score."""
    result = await db.execute(
        select(LeadScore, Contact.first_name, Contact.last_name)
        .join(Contact, LeadScore.contact_id == Contact.id)
        .where(Contact.is_deleted == False)  # noqa: E712
        .order_by(LeadScore.composite_score.desc())
        .limit(limit)
    )
    rows = result.all()
    return [
        {
            "contact_id": ls.contact_id,
            "contact_name": f"{fn} {ln}",
            "composite_score": ls.composite_score,
            "fit_score": ls.fit_score,
            "intent_score": ls.intent_score,
            "instinct_score": ls.instinct_score,
            "calculated_at": ls.calculated_at,
        }
        for ls, fn, ln in rows
    ]


async def recalculate_all(db: AsyncSession) -> int:
    """Recalculate lead scores for all non-deleted contacts."""
    result = await db.execute(
        select(Contact.id).where(Contact.is_deleted == False)  # noqa: E712
    )
    contact_ids = result.scalars().all()
    count = 0
    for cid in contact_ids:
        score = await calculate_lead_score(db, cid)
        if score:
            count += 1
    await db.commit()
    return count
