"""Ripple CRM — Deal Analytics & Pipeline Intelligence API routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.deal_analytics import get_pipeline_summary, get_stage_velocity, get_stalled_deals

router = APIRouter(prefix="/deal-analytics", tags=["deal-analytics"])


@router.get("/pipeline")
async def pipeline_summary(db: AsyncSession = Depends(get_db)):
    return await get_pipeline_summary(db)


@router.get("/velocity")
async def stage_velocity(db: AsyncSession = Depends(get_db)):
    return await get_stage_velocity(db)


@router.get("/stalled")
async def stalled_deals(
    threshold_days: int = Query(14, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    return await get_stalled_deals(db, threshold_days=threshold_days)
