"""Touchstone — CRM webhook endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.contact import Contact
from app.models.deal import Deal
from app.schemas.webhook import CRMWebhookRequest, CRMWebhookResponse

router = APIRouter(tags=["webhooks"])


@router.post("/webhooks/crm", response_model=CRMWebhookResponse)
async def crm_webhook(req: CRMWebhookRequest, db: AsyncSession = Depends(get_db)):
    """Receive deal outcome from CRM. Matches contact by email."""
    is_new = False

    # Match contact by email
    result = await db.execute(
        select(Contact).where(Contact.email == req.contact_email).limit(1)
    )
    contact = result.scalar_one_or_none()
    contact_id = contact.id if contact else None

    # Check for existing deal by crm_deal_id
    existing = await db.execute(
        select(Deal).where(Deal.crm_deal_id == req.crm_deal_id).limit(1)
    )
    deal = existing.scalar_one_or_none()

    if deal:
        # Update existing deal
        deal.deal_name = req.deal_name or deal.deal_name
        deal.amount = req.amount if req.amount is not None else deal.amount
        deal.currency = req.currency
        deal.stage = req.stage
        deal.closed_at = req.closed_at
        deal.crm_source = req.crm_source
        if contact_id:
            deal.contact_id = contact_id
        if req.metadata:
            existing_meta = deal.metadata_ or {}
            existing_meta.update(req.metadata)
            deal.metadata_ = existing_meta
    else:
        is_new = True
        deal = Deal(
            contact_id=contact_id,
            crm_deal_id=req.crm_deal_id,
            deal_name=req.deal_name,
            amount=req.amount,
            currency=req.currency,
            stage=req.stage,
            closed_at=req.closed_at,
            crm_source=req.crm_source,
            metadata_=req.metadata or {},
        )
        db.add(deal)

    await db.commit()
    await db.refresh(deal)

    return CRMWebhookResponse(
        deal_id=deal.id,
        contact_id=contact_id,
        is_new=is_new,
    )
