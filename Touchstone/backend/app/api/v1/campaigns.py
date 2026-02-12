"""Touchstone — Campaign CRUD endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.campaign import Campaign
from app.models.touchpoint import Touchpoint
from app.schemas.campaign import CampaignCreate, CampaignUpdate, CampaignOut

router = APIRouter(tags=["campaigns"])


@router.post("/campaigns", response_model=CampaignOut, status_code=201)
async def create_campaign(body: CampaignCreate, db: AsyncSession = Depends(get_db)):
    campaign = Campaign(
        name=body.name,
        channel=body.channel,
        start_date=body.start_date,
        end_date=body.end_date,
        budget=body.budget,
        currency=body.currency,
        metadata_=body.metadata or {},
    )
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return CampaignOut(**_campaign_dict(campaign), touchpoint_count=0)


@router.get("/campaigns")
async def list_campaigns(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Campaign).order_by(Campaign.created_at.desc()))
    campaigns = result.scalars().all()
    items = []
    for c in campaigns:
        count_result = await db.execute(
            select(func.count()).where(Touchpoint.campaign_id == c.id)
        )
        count = count_result.scalar() or 0
        items.append(CampaignOut(**_campaign_dict(c), touchpoint_count=count))
    return {"items": items, "total": len(items)}


@router.get("/campaigns/{campaign_id}", response_model=CampaignOut)
async def get_campaign(campaign_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    count_result = await db.execute(
        select(func.count()).where(Touchpoint.campaign_id == campaign.id)
    )
    count = count_result.scalar() or 0
    return CampaignOut(**_campaign_dict(campaign), touchpoint_count=count)


@router.put("/campaigns/{campaign_id}", response_model=CampaignOut)
async def update_campaign(campaign_id: UUID, body: CampaignUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    update_data = body.model_dump(exclude_unset=True)
    if "metadata" in update_data:
        update_data["metadata_"] = update_data.pop("metadata")
    for key, val in update_data.items():
        setattr(campaign, key, val)
    await db.commit()
    await db.refresh(campaign)
    count_result = await db.execute(
        select(func.count()).where(Touchpoint.campaign_id == campaign.id)
    )
    count = count_result.scalar() or 0
    return CampaignOut(**_campaign_dict(campaign), touchpoint_count=count)


@router.delete("/campaigns/{campaign_id}", status_code=204)
async def delete_campaign(campaign_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    await db.delete(campaign)
    await db.commit()


def _campaign_dict(c: Campaign) -> dict:
    return {
        "id": c.id,
        "name": c.name,
        "channel": c.channel,
        "start_date": c.start_date,
        "end_date": c.end_date,
        "budget": c.budget,
        "currency": c.currency,
        "metadata": c.metadata_,
        "created_at": c.created_at,
        "updated_at": c.updated_at,
    }
