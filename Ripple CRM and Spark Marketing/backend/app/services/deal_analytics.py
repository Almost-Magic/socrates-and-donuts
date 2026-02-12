"""Ripple CRM — Deal Analytics & Pipeline Intelligence.

Provides:
  - Pipeline summary (deals by stage, values)
  - Stage velocity (avg days per stage from audit log)
  - Stall detection (deals with no activity in N days)
  - Win/loss metrics
"""

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.contact import Contact
from app.models.deal import Deal


STAGE_ORDER = ["lead", "qualified", "proposal", "negotiation", "closed_won", "closed_lost"]


async def get_pipeline_summary(db: AsyncSession) -> dict:
    """Pipeline summary: deals by stage, total values, win/loss metrics."""
    result = await db.execute(
        select(
            Deal.stage,
            func.count(Deal.id).label("count"),
            func.coalesce(func.sum(Deal.value), 0).label("total_value"),
            func.coalesce(func.avg(Deal.value), 0).label("avg_value"),
        )
        .where(Deal.is_deleted == False)  # noqa: E712
        .group_by(Deal.stage)
    )
    rows = result.all()

    stages = []
    total_deals = 0
    total_value = 0.0
    win_count = 0
    loss_count = 0

    for stage, count, total_val, avg_val in rows:
        stages.append({
            "stage": stage,
            "count": count,
            "total_value": round(float(total_val), 2),
            "avg_value": round(float(avg_val), 2),
        })
        total_deals += count
        total_value += float(total_val)
        if stage == "closed_won":
            win_count = count
        elif stage == "closed_lost":
            loss_count = count

    # Sort by stage order
    stage_idx = {s: i for i, s in enumerate(STAGE_ORDER)}
    stages.sort(key=lambda x: stage_idx.get(x["stage"], 99))

    decided = win_count + loss_count
    win_rate = round((win_count / decided) * 100, 1) if decided > 0 else None
    avg_deal = round(total_value / total_deals, 2) if total_deals > 0 else None

    return {
        "stages": stages,
        "total_deals": total_deals,
        "total_pipeline_value": round(total_value, 2),
        "win_count": win_count,
        "loss_count": loss_count,
        "win_rate": win_rate,
        "avg_deal_value": avg_deal,
    }


async def get_stage_velocity(db: AsyncSession) -> dict:
    """Average days spent in each stage, computed from audit log stage_change entries."""

    # Get all stage_change audit entries for deals
    result = await db.execute(
        select(AuditLog)
        .where(
            AuditLog.entity_type == "deal",
            AuditLog.action == "stage_change",
        )
        .order_by(AuditLog.changed_at.asc())
    )
    stage_changes = result.scalars().all()

    # Group by deal_id, compute time in each stage
    from collections import defaultdict
    deal_stages = defaultdict(list)
    for sc in stage_changes:
        deal_stages[sc.entity_id].append({
            "from": sc.old_value,
            "to": sc.new_value,
            "at": sc.changed_at,
        })

    stage_durations = defaultdict(list)

    for _deal_id, changes in deal_stages.items():
        for i, change in enumerate(changes):
            old_stage = change["from"]
            ts = change["at"]
            if ts and ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)

            if i == 0:
                # Can't compute duration for the first known stage without deal creation time
                continue

            prev_ts = changes[i - 1]["at"]
            if prev_ts and prev_ts.tzinfo is None:
                prev_ts = prev_ts.replace(tzinfo=timezone.utc)

            if prev_ts and ts:
                days = (ts - prev_ts).days
                prev_stage = changes[i - 1]["to"]
                if prev_stage:
                    stage_durations[prev_stage].append(days)

    velocity = []
    for stage in STAGE_ORDER:
        if stage in ("closed_won", "closed_lost"):
            continue
        durations = stage_durations.get(stage, [])
        if durations:
            velocity.append({
                "stage": stage,
                "avg_days": round(sum(durations) / len(durations), 1),
                "deal_count": len(durations),
            })
        else:
            velocity.append({"stage": stage, "avg_days": 0, "deal_count": 0})

    # Average full cycle (from first stage change to closed)
    cycle_times = []
    for _deal_id, changes in deal_stages.items():
        if changes:
            last = changes[-1]
            if last["to"] in ("closed_won", "closed_lost"):
                first_ts = changes[0]["at"]
                last_ts = last["at"]
                if first_ts and last_ts:
                    if first_ts.tzinfo is None:
                        first_ts = first_ts.replace(tzinfo=timezone.utc)
                    if last_ts.tzinfo is None:
                        last_ts = last_ts.replace(tzinfo=timezone.utc)
                    cycle_times.append((last_ts - first_ts).days)

    avg_cycle = round(sum(cycle_times) / len(cycle_times), 1) if cycle_times else None

    return {
        "stages": velocity,
        "avg_cycle_days": avg_cycle,
    }


async def get_stalled_deals(db: AsyncSession, threshold_days: int = 14) -> dict:
    """Find deals that haven't been updated in threshold_days."""
    now = datetime.now(timezone.utc)

    result = await db.execute(
        select(Deal)
        .where(
            Deal.is_deleted == False,  # noqa: E712
            Deal.stage.notin_(["closed_won", "closed_lost"]),
        )
        .order_by(Deal.updated_at.asc())
    )
    deals = result.scalars().all()

    stalled = []
    for deal in deals:
        updated = deal.updated_at
        if updated and updated.tzinfo is None:
            updated = updated.replace(tzinfo=timezone.utc)

        days_since = (now - updated).days if updated else 999

        if days_since >= threshold_days:
            # Get contact name
            contact_name = None
            if deal.contact_id:
                c_result = await db.execute(
                    select(Contact.first_name, Contact.last_name)
                    .where(Contact.id == deal.contact_id)
                )
                row = c_result.first()
                if row:
                    contact_name = f"{row[0]} {row[1]}"

            stalled.append({
                "id": deal.id,
                "title": deal.title,
                "stage": deal.stage,
                "value": deal.value,
                "contact_name": contact_name,
                "days_stalled": days_since,
                "last_activity_at": updated,
            })

    stalled.sort(key=lambda x: -x["days_stalled"])

    return {
        "items": stalled,
        "total": len(stalled),
        "stall_threshold_days": threshold_days,
    }
