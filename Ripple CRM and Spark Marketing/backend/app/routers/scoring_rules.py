"""Ripple CRM — Scoring Rules CRUD API routes."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.scoring_rule import ScoringRule
from app.schemas.scoring_rule import (
    ScoringRuleCreate,
    ScoringRuleListResponse,
    ScoringRuleResponse,
    ScoringRuleUpdate,
)

router = APIRouter(prefix="/scoring/rules", tags=["scoring-rules"])


@router.post("", response_model=ScoringRuleResponse, status_code=201)
async def create_rule(data: ScoringRuleCreate, db: AsyncSession = Depends(get_db)):
    rule = ScoringRule(**data.model_dump())
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule


@router.get("", response_model=ScoringRuleListResponse)
async def list_rules(
    brain: str | None = Query(None),
    is_active: bool | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    q = select(ScoringRule)
    if brain:
        q = q.where(ScoringRule.brain == brain)
    if is_active is not None:
        q = q.where(ScoringRule.is_active == is_active)

    q = q.order_by(ScoringRule.brain, ScoringRule.sort_order)
    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    result = await db.execute(q)
    rules = result.scalars().all()
    return ScoringRuleListResponse(items=rules, total=total)


@router.get("/{rule_id}", response_model=ScoringRuleResponse)
async def get_rule(rule_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ScoringRule).where(ScoringRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Scoring rule not found")
    return rule


@router.put("/{rule_id}", response_model=ScoringRuleResponse)
async def update_rule(rule_id: uuid.UUID, data: ScoringRuleUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ScoringRule).where(ScoringRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Scoring rule not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(rule, key, value)

    await db.commit()
    await db.refresh(rule)
    return rule


@router.delete("/{rule_id}")
async def delete_rule(rule_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ScoringRule).where(ScoringRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Scoring rule not found")

    await db.delete(rule)
    await db.commit()
    return {"detail": "Scoring rule deleted"}
