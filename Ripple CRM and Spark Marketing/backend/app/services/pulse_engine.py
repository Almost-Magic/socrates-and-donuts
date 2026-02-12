"""Ripple CRM — Pulse intelligence engine.

Generates daily sales intelligence briefings by analysing CRM data:
targets vs actual, easy wins, pipeline health, relationship changes,
coaching insights, and AI commentary via the Supervisor.
"""

import json
import logging
from datetime import date, datetime, timedelta, timezone

import httpx
from sqlalchemy import Date, and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.contact import Contact
from app.models.deal import Deal
from app.models.interaction import Interaction
from app.models.pulse_action import PulseAction
from app.models.pulse_snapshot import PulseSnapshot
from app.models.pulse_wisdom import PulseWisdom
from app.models.sales_target import SalesTarget

log = logging.getLogger(__name__)

SUPERVISOR_URL = settings.supervisor_url

AI_SYSTEM_PROMPT = (
    "You are a senior sales coach for an Australian business. "
    "Analyse the CRM data provided and generate SPECIFIC, ACTIONABLE insights. "
    "Rules: 1) Reference actual contact names, deal names, and dollar amounts. "
    "2) Never give generic advice like 'try to close more deals' or 'consider reaching out'. "
    "3) Explain WHY each action matters using data. "
    "4) Australian English. "
    "5) Max 2-3 sentences per insight. "
    "6) Be encouraging but honest."
)


# ── Target vs Actual ───────────────────────────────────────────────────────

async def query_target_vs_actual(db: AsyncSession, for_date: date | None = None) -> dict | None:
    """Compare sales target vs sum of closed_won deals in current period."""
    today = for_date or date.today()

    # Find current target (monthly first, then quarterly)
    for period_type in ("monthly", "quarterly"):
        result = await db.execute(
            select(SalesTarget)
            .where(
                SalesTarget.period_type == period_type,
                SalesTarget.period_start <= today,
                SalesTarget.period_end >= today,
            )
            .order_by(SalesTarget.created_at.desc())
            .limit(1)
        )
        target = result.scalar_one_or_none()
        if target:
            break

    if not target:
        return None

    # Sum of closed_won deals in the target period
    actual = (await db.execute(
        select(func.coalesce(func.sum(Deal.value), 0)).where(
            Deal.is_deleted == False,  # noqa: E712
            Deal.stage == "closed_won",
            Deal.actual_close_date >= target.period_start,
            Deal.actual_close_date <= target.period_end,
        )
    )).scalar() or 0.0

    gap = target.target_value - actual
    percentage = (actual / target.target_value * 100) if target.target_value > 0 else 0

    # Calculate pace
    days_elapsed = (today - target.period_start).days + 1
    total_days = (target.period_end - target.period_start).days + 1
    time_pct = (days_elapsed / total_days * 100) if total_days > 0 else 0

    if percentage >= time_pct + 10:
        pace = "ahead"
    elif percentage >= time_pct - 10:
        pace = "on_track"
    else:
        pace = "behind"

    return {
        "target_id": str(target.id),
        "period_label": target.period_label,
        "period_type": target.period_type,
        "target_value": target.target_value,
        "actual_value": round(actual, 2),
        "gap": round(gap, 2),
        "percentage": round(percentage, 1),
        "pace": pace,
    }


# ── Easy Wins ──────────────────────────────────────────────────────────────

async def rank_easy_wins(db: AsyncSession, limit: int = 10) -> list[dict]:
    """Score and rank deals by opportunity value.

    Score = (value * probability) / (days_since_last_interaction + 1)

    Also detects: renewals, stale proposals, cross-sell opportunities.
    """
    today = date.today()
    wins: list[dict] = []

    # Active deals with contact info
    result = await db.execute(
        select(Deal)
        .where(
            Deal.is_deleted == False,  # noqa: E712
            Deal.stage.notin_(["closed_won", "closed_lost"]),
        )
        .order_by(Deal.value.desc().nullslast())
        .limit(50)
    )
    deals = result.scalars().all()

    for deal in deals:
        # Get days since last interaction
        last_interaction = (await db.execute(
            select(func.max(Interaction.occurred_at))
            .where(Interaction.contact_id == deal.contact_id)
        )).scalar()

        days_since = (today - last_interaction.date()).days if last_interaction else 30

        value = deal.value or 0
        prob = (deal.probability or 50) / 100
        score = (value * prob) / (days_since + 1)

        # Determine win type
        win_type = "standard"
        if deal.stage in ("proposal", "negotiation"):
            if days_since > 14:
                win_type = "stale_proposal"
                score *= 1.5  # Boost stale proposals
            else:
                win_type = "final_stage"
                score *= 1.3
        elif deal.stage == "qualified":
            win_type = "warm_lead"

        # Get contact name
        contact_name = None
        if deal.contact_id:
            contact = (await db.execute(
                select(Contact.first_name, Contact.last_name)
                .where(Contact.id == deal.contact_id)
            )).first()
            if contact:
                contact_name = f"{contact.first_name} {contact.last_name}"

        wins.append({
            "deal_id": str(deal.id),
            "deal_title": deal.title,
            "contact_id": str(deal.contact_id) if deal.contact_id else None,
            "contact_name": contact_name,
            "value": value,
            "stage": deal.stage,
            "probability": deal.probability,
            "days_since_contact": days_since,
            "score": round(score, 2),
            "win_type": win_type,
        })

    # Detect renewal opportunities (customers with no active deal)
    result = await db.execute(
        select(Contact)
        .where(
            Contact.is_deleted == False,  # noqa: E712
            Contact.type == "customer",
        )
        .limit(20)
    )
    customers = result.scalars().all()

    for cust in customers:
        has_active = (await db.execute(
            select(func.count()).select_from(
                select(Deal.id).where(
                    Deal.contact_id == cust.id,
                    Deal.is_deleted == False,  # noqa: E712
                    Deal.stage.notin_(["closed_won", "closed_lost"]),
                ).subquery()
            )
        )).scalar() or 0

        if has_active == 0:
            # Get their last won deal value as estimate
            last_won = (await db.execute(
                select(Deal.value)
                .where(
                    Deal.contact_id == cust.id,
                    Deal.stage == "closed_won",
                )
                .order_by(Deal.actual_close_date.desc().nullslast())
                .limit(1)
            )).scalar()

            if last_won and last_won > 0:
                wins.append({
                    "deal_id": None,
                    "deal_title": f"Renewal: {cust.first_name} {cust.last_name}",
                    "contact_id": str(cust.id),
                    "contact_name": f"{cust.first_name} {cust.last_name}",
                    "value": last_won,
                    "stage": "renewal",
                    "probability": None,
                    "days_since_contact": None,
                    "score": last_won * 0.7,
                    "win_type": "renewal",
                })

    # Sort by score descending and limit
    wins.sort(key=lambda w: w["score"], reverse=True)
    return wins[:limit]


# ── Pipeline Analysis ──────────────────────────────────────────────────────

async def analyse_pipeline(db: AsyncSession) -> dict:
    """Analyse deal pipeline: stages, stalled deals, win/loss rates, velocity."""
    today = date.today()

    # Deals by stage
    result = await db.execute(
        select(Deal.stage, func.count(), func.coalesce(func.sum(Deal.value), 0))
        .where(Deal.is_deleted == False)  # noqa: E712
        .group_by(Deal.stage)
    )
    stage_rows = result.all()
    stages = [
        {"stage": row[0], "count": row[1], "value": round(float(row[2]), 2)}
        for row in stage_rows
    ]

    # Stalled deals (>14 days same stage, not closed)
    stale_cutoff = today - timedelta(days=14)
    result = await db.execute(
        select(Deal)
        .where(
            Deal.is_deleted == False,  # noqa: E712
            Deal.stage.notin_(["closed_won", "closed_lost"]),
            Deal.updated_at < datetime(stale_cutoff.year, stale_cutoff.month, stale_cutoff.day, tzinfo=timezone.utc),
        )
        .order_by(Deal.updated_at.asc())
        .limit(10)
    )
    stalled_deals_raw = result.scalars().all()

    stalled = []
    for d in stalled_deals_raw:
        days_in_stage = (today - d.updated_at.date()).days if d.updated_at else 0
        contact_name = None
        if d.contact_id:
            c = (await db.execute(
                select(Contact.first_name, Contact.last_name)
                .where(Contact.id == d.contact_id)
            )).first()
            if c:
                contact_name = f"{c.first_name} {c.last_name}"

        stalled.append({
            "deal_id": str(d.id),
            "title": d.title,
            "stage": d.stage,
            "value": d.value,
            "days_in_stage": days_in_stage,
            "contact_name": contact_name,
        })

    # Win/loss rates for 30/60/90 days
    rates = {}
    for days in (30, 60, 90):
        cutoff = today - timedelta(days=days)
        won = (await db.execute(
            select(func.count()).select_from(
                select(Deal.id).where(
                    Deal.stage == "closed_won",
                    Deal.actual_close_date >= cutoff,
                ).subquery()
            )
        )).scalar() or 0

        lost = (await db.execute(
            select(func.count()).select_from(
                select(Deal.id).where(
                    Deal.stage == "closed_lost",
                    Deal.actual_close_date >= cutoff,
                ).subquery()
            )
        )).scalar() or 0

        total = won + lost
        rates[f"win_rate_{days}d"] = round(won / total * 100, 1) if total > 0 else None

    # Average deal velocity (days from created to closed_won)
    result = await db.execute(
        select(
            func.avg(
                func.extract("epoch", Deal.actual_close_date) -
                func.extract("epoch", func.cast(Deal.created_at, Date))
            )
        ).where(
            Deal.stage == "closed_won",
            Deal.actual_close_date.isnot(None),
        )
    )
    avg_velocity_seconds = result.scalar()
    avg_velocity_days = round(avg_velocity_seconds, 0) if avg_velocity_seconds else None

    return {
        "stages": stages,
        "stalled_deals": stalled,
        "win_rate_30d": rates.get("win_rate_30d"),
        "win_rate_60d": rates.get("win_rate_60d"),
        "win_rate_90d": rates.get("win_rate_90d"),
        "avg_deal_velocity_days": avg_velocity_days,
    }


# ── Relationship Changes ──────────────────────────────────────────────────

async def detect_relationship_changes(
    db: AsyncSession, no_contact_days: int = 14
) -> dict:
    """Find decaying, champion, and silent contacts."""
    today = date.today()

    # Decaying: health score below 40 or trust_decay_status in warning/critical
    result = await db.execute(
        select(Contact)
        .where(
            Contact.is_deleted == False,  # noqa: E712
            or_(
                Contact.relationship_health_score < 40,
                Contact.trust_decay_status.in_(["warning", "critical"]),
            ),
        )
        .order_by(Contact.relationship_health_score.asc().nullslast())
        .limit(10)
    )
    decaying_raw = result.scalars().all()
    decaying = []
    for c in decaying_raw:
        last = (await db.execute(
            select(func.max(Interaction.occurred_at))
            .where(Interaction.contact_id == c.id)
        )).scalar()
        last_days = (today - last.date()).days if last else None

        decaying.append({
            "contact_id": str(c.id),
            "contact_name": f"{c.first_name} {c.last_name}",
            "health_score": c.relationship_health_score,
            "trust_decay_days": c.trust_decay_days,
            "status": c.trust_decay_status or "warning",
            "last_interaction_days": last_days,
        })

    # Champions: highest health scores
    result = await db.execute(
        select(Contact)
        .where(
            Contact.is_deleted == False,  # noqa: E712
            Contact.relationship_health_score.isnot(None),
            Contact.relationship_health_score >= 70,
        )
        .order_by(Contact.relationship_health_score.desc())
        .limit(5)
    )
    champ_raw = result.scalars().all()
    champions = [
        {
            "contact_id": str(c.id),
            "contact_name": f"{c.first_name} {c.last_name}",
            "health_score": c.relationship_health_score,
            "trust_decay_days": c.trust_decay_days,
            "status": "champion",
            "last_interaction_days": None,
        }
        for c in champ_raw
    ]

    # No contact: no interaction in X days
    cutoff = today - timedelta(days=no_contact_days)
    cutoff_dt = datetime(cutoff.year, cutoff.month, cutoff.day, tzinfo=timezone.utc)

    # Contacts whose most recent interaction is before the cutoff
    subq = (
        select(Interaction.contact_id, func.max(Interaction.occurred_at).label("latest"))
        .group_by(Interaction.contact_id)
    ).subquery()

    result = await db.execute(
        select(Contact)
        .join(subq, Contact.id == subq.c.contact_id)
        .where(
            Contact.is_deleted == False,  # noqa: E712
            subq.c.latest < cutoff_dt,
        )
        .order_by(subq.c.latest.asc())
        .limit(10)
    )
    silent_raw = result.scalars().all()
    no_contact_list = [
        {
            "contact_id": str(c.id),
            "contact_name": f"{c.first_name} {c.last_name}",
            "health_score": c.relationship_health_score,
            "trust_decay_days": c.trust_decay_days,
            "status": "silent",
            "last_interaction_days": None,
        }
        for c in silent_raw
    ]

    return {
        "decaying": decaying,
        "champions": champions,
        "no_contact": no_contact_list,
    }


# ── Coaching ───────────────────────────────────────────────────────────────

async def generate_coaching(db: AsyncSession) -> dict:
    """Win streaks, personal bests, pattern detection."""
    today = date.today()

    # Count consecutive days with closed_won deals (streak)
    streak = 0
    check_date = today
    while True:
        won_today = (await db.execute(
            select(func.count()).select_from(
                select(Deal.id).where(
                    Deal.stage == "closed_won",
                    Deal.actual_close_date == check_date,
                ).subquery()
            )
        )).scalar() or 0

        if won_today > 0:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break

        if streak > 365:
            break

    # Personal bests
    bests: list[str] = []

    # Largest single deal this month
    month_start = today.replace(day=1)
    biggest = (await db.execute(
        select(Deal.title, Deal.value)
        .where(
            Deal.stage == "closed_won",
            Deal.actual_close_date >= month_start,
        )
        .order_by(Deal.value.desc().nullslast())
        .limit(1)
    )).first()

    if biggest and biggest.value:
        bests.append(f"Biggest win this month: {biggest.title} (${biggest.value:,.0f})")

    # Total closed this month
    month_total = (await db.execute(
        select(func.coalesce(func.sum(Deal.value), 0)).where(
            Deal.stage == "closed_won",
            Deal.actual_close_date >= month_start,
        )
    )).scalar() or 0

    if month_total > 0:
        bests.append(f"Total closed this month: ${month_total:,.0f}")

    # Count of deals won this month
    month_count = (await db.execute(
        select(func.count()).select_from(
            select(Deal.id).where(
                Deal.stage == "closed_won",
                Deal.actual_close_date >= month_start,
            ).subquery()
        )
    )).scalar() or 0
    if month_count > 0:
        bests.append(f"Deals closed this month: {month_count}")

    return {
        "streak_days": streak,
        "streak_type": "win" if streak > 0 else None,
        "personal_bests": bests,
        "coaching_tips": [],
    }


# ── Action Generation ──────────────────────────────────────────────────────

async def generate_actions(
    db: AsyncSession, easy_wins: list[dict], pipeline: dict, relationships: dict
) -> list[dict]:
    """Pick top 5 highest-impact actions from various signals."""
    candidates: list[dict] = []

    # From easy wins
    for win in easy_wins[:5]:
        if win["win_type"] == "stale_proposal":
            candidates.append({
                "title": f"Follow up on stale proposal: {win['deal_title']}",
                "description": f"This proposal has been untouched for {win['days_since_contact']} days.",
                "reason": f"${win['value']:,.0f} deal at {win['stage']} stage with no recent contact.",
                "estimated_minutes": 15,
                "contact_id": win["contact_id"],
                "deal_id": win["deal_id"],
                "priority": 1,
                "score": win["score"] * 2,
            })
        elif win["win_type"] == "final_stage":
            candidates.append({
                "title": f"Push to close: {win['deal_title']}",
                "description": f"Deal in {win['stage']} stage ready for final push.",
                "reason": f"${win['value']:,.0f} deal with {win.get('contact_name', 'unknown')} at {win['stage']}.",
                "estimated_minutes": 20,
                "contact_id": win["contact_id"],
                "deal_id": win["deal_id"],
                "priority": 1,
                "score": win["score"] * 1.5,
            })
        elif win["win_type"] == "renewal":
            candidates.append({
                "title": f"Explore renewal with {win.get('contact_name', 'customer')}",
                "description": "Existing customer with no active deal - renewal opportunity.",
                "reason": f"Previous deal worth ${win['value']:,.0f}. Renewals close faster.",
                "estimated_minutes": 10,
                "contact_id": win["contact_id"],
                "deal_id": None,
                "priority": 2,
                "score": win["score"],
            })
        else:
            candidates.append({
                "title": f"Advance deal: {win['deal_title']}",
                "description": f"Move this {win['stage']} deal forward.",
                "reason": f"${win['value']:,.0f} opportunity with good momentum.",
                "estimated_minutes": 15,
                "contact_id": win["contact_id"],
                "deal_id": win["deal_id"],
                "priority": 2,
                "score": win["score"],
            })

    # From stalled deals
    for stalled in pipeline.get("stalled_deals", [])[:3]:
        candidates.append({
            "title": f"Unblock stalled deal: {stalled['title']}",
            "description": f"Stuck in {stalled['stage']} for {stalled['days_in_stage']} days.",
            "reason": f"${stalled['value']:,.0f} at risk of going cold." if stalled.get("value") else f"Deal stalled for {stalled['days_in_stage']} days.",
            "estimated_minutes": 20,
            "contact_id": None,
            "deal_id": stalled["deal_id"],
            "priority": 1,
            "score": (stalled.get("value") or 1000) / (stalled["days_in_stage"] + 1),
        })

    # From decaying relationships
    for decay in relationships.get("decaying", [])[:3]:
        candidates.append({
            "title": f"Re-engage {decay['contact_name']}",
            "description": f"Relationship health at {decay.get('health_score', 'unknown')}.",
            "reason": f"Trust decaying for {decay.get('trust_decay_days', '?')} days - needs attention.",
            "estimated_minutes": 10,
            "contact_id": decay["contact_id"],
            "deal_id": None,
            "priority": 3,
            "score": 100 - (decay.get("health_score") or 50),
        })

    # Sort by score descending, take top 5
    candidates.sort(key=lambda c: c.get("score", 0), reverse=True)
    return candidates[:5]


# ── AI Commentary ──────────────────────────────────────────────────────────

async def get_ai_commentary(data_bundle: dict) -> dict | None:
    """Send structured data to Supervisor for AI analysis.

    Returns commentary dict or None if Supervisor/Ollama unavailable.
    Graceful degradation - Pulse works without AI.
    """
    try:
        prompt = json.dumps(data_bundle, default=str, indent=2)
        user_message = (
            "Analyse this CRM data and provide commentary in JSON format with these keys:\n"
            '- "target_commentary": 2-3 sentences on target progress\n'
            '- "pipeline_narrative": 2-3 sentences on pipeline health\n'
            '- "coaching_tips": list of 2-3 specific coaching tips\n'
            '- "action_descriptions": dict mapping action titles to AI-enhanced descriptions\n\n'
            f"CRM Data:\n{prompt}"
        )

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{SUPERVISOR_URL}/api/chat",
                json={
                    "model": "default",
                    "system": AI_SYSTEM_PROMPT,
                    "messages": [{"role": "user", "content": user_message}],
                },
                timeout=30.0,
            )

            if resp.status_code != 200:
                log.warning("Supervisor returned %d for AI commentary", resp.status_code)
                return None

            body = resp.json()
            content = body.get("message", {}).get("content", "")

            # Try to parse JSON from response
            try:
                # Strip markdown code fences if present
                cleaned = content.strip()
                if cleaned.startswith("```"):
                    lines = cleaned.split("\n")
                    lines = [l for l in lines if not l.strip().startswith("```")]
                    cleaned = "\n".join(lines)
                return json.loads(cleaned)
            except json.JSONDecodeError:
                # Return raw text as target commentary
                return {"target_commentary": content, "pipeline_narrative": None, "coaching_tips": [], "action_descriptions": {}}

    except Exception as e:
        log.warning("AI commentary unavailable: %s", e)
        return None


# ── Compile Pulse ──────────────────────────────────────────────────────────

async def compile_pulse(db: AsyncSession, for_date: date | None = None) -> dict:
    """Orchestrate all Pulse components into a single briefing."""
    today = for_date or date.today()

    # Gather data
    target = await query_target_vs_actual(db, today)
    easy_wins = await rank_easy_wins(db)
    pipeline = await analyse_pipeline(db)
    relationships = await detect_relationship_changes(db)
    coaching = await generate_coaching(db)
    actions_raw = await generate_actions(db, easy_wins, pipeline, relationships)

    # Get wisdom quote
    wisdom = None
    result = await db.execute(
        select(PulseWisdom)
        .order_by(PulseWisdom.last_shown.asc().nullsfirst())
        .limit(1)
    )
    wisdom_row = result.scalar_one_or_none()
    if wisdom_row:
        wisdom = {
            "id": str(wisdom_row.id),
            "quote": wisdom_row.quote,
            "author": wisdom_row.author,
            "source": wisdom_row.source,
        }
        wisdom_row.last_shown = today
        await db.flush()

    # AI commentary (best effort)
    ai_data = {
        "target": target,
        "top_deals": easy_wins[:5],
        "pipeline_stages": pipeline["stages"],
        "stalled_deals": pipeline["stalled_deals"],
        "decaying_contacts": relationships["decaying"][:3],
        "win_rates": {
            "30d": pipeline.get("win_rate_30d"),
            "60d": pipeline.get("win_rate_60d"),
        },
    }
    commentary = await get_ai_commentary(ai_data)

    # Apply AI commentary
    if commentary:
        if target:
            target["commentary"] = commentary.get("target_commentary")
        pipeline["narrative"] = commentary.get("pipeline_narrative")
        coaching["coaching_tips"] = commentary.get("coaching_tips", [])

        # Enhance action descriptions
        action_descs = commentary.get("action_descriptions", {})
        for action in actions_raw:
            enhanced = action_descs.get(action["title"])
            if enhanced:
                action["description"] = enhanced

    # Save actions to DB
    saved_actions = []
    for i, a in enumerate(actions_raw):
        action = PulseAction(
            snapshot_date=today,
            title=a["title"],
            description=a.get("description"),
            reason=a.get("reason"),
            estimated_minutes=a.get("estimated_minutes"),
            contact_id=a.get("contact_id"),
            deal_id=a.get("deal_id"),
            priority=i + 1,
        )
        db.add(action)
        await db.flush()
        saved_actions.append({
            "id": str(action.id),
            "snapshot_date": today.isoformat(),
            "title": action.title,
            "description": action.description,
            "reason": action.reason,
            "estimated_minutes": action.estimated_minutes,
            "contact_id": str(action.contact_id) if action.contact_id else None,
            "deal_id": str(action.deal_id) if action.deal_id else None,
            "priority": action.priority,
            "is_completed": False,
            "completed_at": None,
            "contact_name": a.get("contact_name"),
            "deal_title": a.get("deal_title"),
        })

    pulse = {
        "snapshot_date": today.isoformat(),
        "target_vs_actual": target,
        "easy_wins": easy_wins,
        "actions": saved_actions,
        "pipeline": pipeline,
        "relationships": relationships,
        "coaching": coaching,
        "wisdom": wisdom,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    # Cache in pulse_snapshots
    existing = (await db.execute(
        select(PulseSnapshot).where(PulseSnapshot.snapshot_date == today)
    )).scalar_one_or_none()

    data_str = json.dumps(pulse, default=str)
    commentary_str = json.dumps(commentary, default=str) if commentary else None

    if existing:
        existing.data_json = data_str
        existing.ai_commentary_json = commentary_str
    else:
        snapshot = PulseSnapshot(
            snapshot_date=today,
            data_json=data_str,
            ai_commentary_json=commentary_str,
        )
        db.add(snapshot)

    await db.commit()
    return pulse
