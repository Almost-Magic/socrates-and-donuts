"""Ripple CRM — Pulse API routes.

Sales intelligence endpoints: daily pulse, targets, actions,
easy wins, coaching, wisdom, EOD review, ELAINE briefing.
"""

import json
import uuid
from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.pulse_action import PulseAction
from app.models.pulse_snapshot import PulseSnapshot
from app.models.pulse_wisdom import PulseWisdom
from app.models.sales_target import SalesTarget
from app.schemas.pulse import (
    EodReviewRequest,
    EodReviewResponse,
    ElaineBriefingResponse,
    PulseActionListResponse,
    PulseActionResponse,
    PulseResponse,
    PulseWisdomResponse,
    SalesTargetCreate,
    SalesTargetListResponse,
    SalesTargetResponse,
    StreakResponse,
)
from app.services.pulse_engine import (
    compile_pulse,
    generate_coaching,
    query_target_vs_actual,
    rank_easy_wins,
)

router = APIRouter(prefix="/pulse", tags=["pulse"])


# ── Pulse (daily report) ──────────────────────────────────────────────────


@router.get("", response_model=PulseResponse)
async def get_pulse_today(db: AsyncSession = Depends(get_db)):
    """Get today's full Pulse. Generate if not cached."""
    today = date.today()

    # Check cache
    result = await db.execute(
        select(PulseSnapshot).where(PulseSnapshot.snapshot_date == today)
    )
    snapshot = result.scalar_one_or_none()

    if snapshot:
        return json.loads(snapshot.data_json)

    # Generate fresh
    pulse = await compile_pulse(db, today)
    return pulse


@router.get("/history")
async def get_pulse_history(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    """Pulse history for the last N days."""
    cutoff = date.today()
    from datetime import timedelta

    start = cutoff - timedelta(days=days)
    result = await db.execute(
        select(PulseSnapshot.snapshot_date, PulseSnapshot.created_at)
        .where(PulseSnapshot.snapshot_date >= start)
        .order_by(PulseSnapshot.snapshot_date.desc())
    )
    rows = result.all()
    return {
        "items": [
            {"date": r.snapshot_date.isoformat(), "generated_at": r.created_at.isoformat()}
            for r in rows
        ],
        "total": len(rows),
    }


@router.get("/actions", response_model=PulseActionListResponse)
async def get_pulse_actions(db: AsyncSession = Depends(get_db)):
    """Get today's action items."""
    today = date.today()
    result = await db.execute(
        select(PulseAction)
        .where(PulseAction.snapshot_date == today)
        .order_by(PulseAction.priority.asc())
    )
    actions = result.scalars().all()
    return {"items": actions, "total": len(actions)}


@router.put("/actions/{action_id}/complete", response_model=PulseActionResponse)
async def complete_action(action_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Mark an action as completed."""
    result = await db.execute(
        select(PulseAction).where(PulseAction.id == action_id)
    )
    action = result.scalar_one_or_none()
    if not action:
        raise HTTPException(404, "Action not found")

    action.is_completed = True
    action.completed_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(action)
    return action


@router.get("/targets", response_model=SalesTargetListResponse)
async def list_targets(db: AsyncSession = Depends(get_db)):
    """List all sales targets."""
    result = await db.execute(
        select(SalesTarget).order_by(SalesTarget.period_start.desc())
    )
    targets = result.scalars().all()
    return {"items": targets, "total": len(targets)}


@router.post("/targets", response_model=SalesTargetResponse, status_code=201)
async def create_target(data: SalesTargetCreate, db: AsyncSession = Depends(get_db)):
    """Create a sales target."""
    target = SalesTarget(**data.model_dump())
    db.add(target)
    await db.commit()
    await db.refresh(target)
    return target


@router.get("/targets/current")
async def get_current_target(db: AsyncSession = Depends(get_db)):
    """Current period target vs actual revenue."""
    result = await query_target_vs_actual(db)
    if not result:
        return {"message": "No active target for current period", "target_vs_actual": None}
    return {"target_vs_actual": result}


@router.get("/streak", response_model=StreakResponse)
async def get_streak(db: AsyncSession = Depends(get_db)):
    """Win streak and momentum data."""
    coaching = await generate_coaching(db)
    return {
        "current_streak": coaching["streak_days"],
        "streak_unit": "days",
        "best_streak": coaching["streak_days"],  # Simplified — track best separately in future
        "last_hit_date": date.today() if coaching["streak_days"] > 0 else None,
    }


@router.get("/easy-wins")
async def get_easy_wins(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """AI-ranked easy win opportunities."""
    wins = await rank_easy_wins(db, limit=limit)
    return {"items": wins, "total": len(wins)}


@router.get("/wisdom", response_model=PulseWisdomResponse | None)
async def get_wisdom(db: AsyncSession = Depends(get_db)):
    """Today's wisdom quote. Rotates through available quotes."""
    today = date.today()

    # Find least-recently-shown quote
    result = await db.execute(
        select(PulseWisdom)
        .order_by(PulseWisdom.last_shown.asc().nullsfirst())
        .limit(1)
    )
    wisdom = result.scalar_one_or_none()

    if not wisdom:
        raise HTTPException(404, "No wisdom quotes available")

    # Mark as shown today
    wisdom.last_shown = today
    await db.commit()
    await db.refresh(wisdom)
    return wisdom


@router.get("/eod-review", response_model=EodReviewResponse)
async def get_eod_review(db: AsyncSession = Depends(get_db)):
    """End-of-day review data."""
    today = date.today()

    # Get snapshot
    result = await db.execute(
        select(PulseSnapshot).where(PulseSnapshot.snapshot_date == today)
    )
    snapshot = result.scalar_one_or_none()

    # Count actions
    result = await db.execute(
        select(func.count()).select_from(
            select(PulseAction.id)
            .where(PulseAction.snapshot_date == today)
            .subquery()
        )
    )
    total_actions = result.scalar() or 0

    result = await db.execute(
        select(func.count()).select_from(
            select(PulseAction.id)
            .where(
                PulseAction.snapshot_date == today,
                PulseAction.is_completed == True,  # noqa: E712
            )
            .subquery()
        )
    )
    completed_actions = result.scalar() or 0

    # Target progress
    target_data = await query_target_vs_actual(db, today)
    target_pct = target_data["percentage"] if target_data else None

    return {
        "snapshot_date": today,
        "eod_notes": snapshot.eod_notes if snapshot else None,
        "actions_completed": completed_actions,
        "actions_total": total_actions,
        "target_progress": target_pct,
    }


@router.post("/eod-review", response_model=EodReviewResponse)
async def save_eod_review(data: EodReviewRequest, db: AsyncSession = Depends(get_db)):
    """Save end-of-day reflection notes."""
    today = date.today()

    result = await db.execute(
        select(PulseSnapshot).where(PulseSnapshot.snapshot_date == today)
    )
    snapshot = result.scalar_one_or_none()

    if not snapshot:
        # Create a minimal snapshot to hold the notes
        snapshot = PulseSnapshot(
            snapshot_date=today,
            data_json="{}",
            eod_notes=data.notes,
        )
        db.add(snapshot)
    else:
        snapshot.eod_notes = data.notes

    await db.commit()

    # Get action counts
    result = await db.execute(
        select(func.count()).select_from(
            select(PulseAction.id)
            .where(PulseAction.snapshot_date == today)
            .subquery()
        )
    )
    total_actions = result.scalar() or 0

    result = await db.execute(
        select(func.count()).select_from(
            select(PulseAction.id)
            .where(
                PulseAction.snapshot_date == today,
                PulseAction.is_completed == True,  # noqa: E712
            )
            .subquery()
        )
    )
    completed_actions = result.scalar() or 0

    target_data = await query_target_vs_actual(db, today)
    target_pct = target_data["percentage"] if target_data else None

    return {
        "snapshot_date": today,
        "eod_notes": snapshot.eod_notes,
        "actions_completed": completed_actions,
        "actions_total": total_actions,
        "target_progress": target_pct,
    }


@router.get("/elaine-briefing", response_model=ElaineBriefingResponse)
async def get_elaine_briefing(db: AsyncSession = Depends(get_db)):
    """Condensed Pulse JSON for ELAINE's morning briefing."""
    today = date.today()

    # Try cached snapshot first
    result = await db.execute(
        select(PulseSnapshot).where(PulseSnapshot.snapshot_date == today)
    )
    snapshot = result.scalar_one_or_none()

    if snapshot:
        pulse = json.loads(snapshot.data_json)
    else:
        pulse = await compile_pulse(db, today)

    # Extract condensed briefing
    target = pulse.get("target_vs_actual")
    actions = pulse.get("actions", [])
    pipeline = pulse.get("pipeline", {})
    relationships = pulse.get("relationships", {})
    coaching = pulse.get("coaching", {})
    wisdom = pulse.get("wisdom")

    target_summary = None
    if target:
        target_summary = (
            f"At {target['percentage']}% of {target['period_label']} target "
            f"(${target['actual_value']:,.0f} / ${target['target_value']:,.0f}). "
            f"Pace: {target['pace']}."
        )

    top_action = actions[0]["title"] if actions else None

    stalled = pipeline.get("stalled_deals", [])
    pipeline_alert = None
    if stalled:
        total_val = sum(d.get("value", 0) or 0 for d in stalled)
        pipeline_alert = f"{len(stalled)} stalled deals (${total_val:,.0f} at risk)."

    decaying = relationships.get("decaying", [])
    relationship_alert = None
    if decaying:
        names = ", ".join(d["contact_name"] for d in decaying[:2])
        relationship_alert = f"Relationships decaying: {names}."

    win_celebration = None
    streak = coaching.get("streak_days", 0)
    if streak > 0:
        win_celebration = f"{streak}-day win streak!"

    wisdom_quote = None
    if wisdom:
        wisdom_quote = f"{wisdom['quote']} -- {wisdom['author']}"

    return {
        "snapshot_date": today,
        "target_summary": target_summary,
        "top_action": top_action,
        "pipeline_alert": pipeline_alert,
        "relationship_alert": relationship_alert,
        "win_celebration": win_celebration,
        "wisdom_quote": wisdom_quote,
    }


@router.post("/generate", response_model=PulseResponse)
async def force_generate_pulse(db: AsyncSession = Depends(get_db)):
    """Force regenerate today's Pulse (clears cache)."""
    today = date.today()

    # Delete existing actions for today (they'll be regenerated)
    result = await db.execute(
        select(PulseAction).where(PulseAction.snapshot_date == today)
    )
    for action in result.scalars().all():
        await db.delete(action)
    await db.flush()

    pulse = await compile_pulse(db, today)
    return pulse


@router.get("/{pulse_date}", response_model=PulseResponse)
async def get_pulse_by_date(pulse_date: date, db: AsyncSession = Depends(get_db)):
    """Get historical Pulse for a specific date."""
    result = await db.execute(
        select(PulseSnapshot).where(PulseSnapshot.snapshot_date == pulse_date)
    )
    snapshot = result.scalar_one_or_none()

    if not snapshot:
        raise HTTPException(404, f"No Pulse snapshot for {pulse_date}")

    return json.loads(snapshot.data_json)
