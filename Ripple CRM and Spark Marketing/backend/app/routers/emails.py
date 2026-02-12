"""Ripple CRM — Email API routes."""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.contact import Contact
from app.models.deal import Deal
from app.models.email import Email
from app.schemas.email import (
    EmailListResponse,
    EmailResponse,
    EmailSend,
    EmailSync,
)

router = APIRouter(prefix="/emails", tags=["emails"])

# Contact-scoped email endpoints
contact_router = APIRouter(prefix="/contacts", tags=["emails"])

# Deal-scoped email endpoints
deal_router = APIRouter(prefix="/deals", tags=["emails"])


async def _auto_link_contact(db: AsyncSession, email_obj: Email) -> None:
    """Try to match email to a contact by from/to addresses."""
    if email_obj.contact_id:
        return

    addresses = []
    if email_obj.direction == "in":
        addresses.append(email_obj.from_address)
    else:
        addresses.extend(email_obj.to_addresses or [])

    for addr in addresses:
        result = await db.execute(
            select(Contact).where(
                Contact.email == addr,
                Contact.is_deleted == False,  # noqa: E712
            ).limit(1)
        )
        contact = result.scalar_one_or_none()
        if contact:
            email_obj.contact_id = contact.id
            return


@router.post("/sync", response_model=EmailResponse, status_code=201)
async def sync_email(data: EmailSync, db: AsyncSession = Depends(get_db)):
    """Receive email data (webhook-ready for future Gmail/Outlook integration)."""
    email = Email(
        direction=data.direction,
        subject=data.subject,
        body_text=data.body_text,
        body_html=data.body_html,
        from_address=data.from_address,
        to_addresses=data.to_addresses,
        cc_addresses=data.cc_addresses,
        sent_at=data.sent_at,
        received_at=data.received_at or (datetime.now(timezone.utc) if data.direction == "in" else None),
        thread_id=data.thread_id,
        message_id=data.message_id,
        is_read=data.is_read,
        status="synced",
        metadata_json=data.metadata or {},
    )
    await _auto_link_contact(db, email)
    db.add(email)
    await db.commit()
    await db.refresh(email)
    return email


@router.get("", response_model=EmailListResponse)
async def list_emails(
    contact_id: uuid.UUID | None = Query(None),
    direction: str | None = Query(None),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(Email)
    if contact_id:
        q = q.where(Email.contact_id == contact_id)
    if direction:
        q = q.where(Email.direction == direction)
    if start_date:
        q = q.where(Email.created_at >= start_date)
    if end_date:
        q = q.where(Email.created_at <= end_date)
    if search:
        term = f"%{search}%"
        q = q.where(Email.subject.ilike(term))

    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    q = q.order_by(Email.created_at.desc())
    q = q.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(q)
    emails = result.scalars().all()
    return EmailListResponse(items=emails, total=total, page=page, page_size=page_size)


@router.get("/{email_id}", response_model=EmailResponse)
async def get_email(email_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Email).where(Email.id == email_id))
    email = result.scalar_one_or_none()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email


@router.post("/send", response_model=EmailResponse, status_code=201)
async def send_email(data: EmailSend, db: AsyncSession = Depends(get_db)):
    """Queue an outgoing email (stores in DB, marks as pending)."""
    email = Email(
        contact_id=data.contact_id,
        direction="out",
        subject=data.subject,
        body_text=data.body_text,
        body_html=data.body_html,
        from_address="mani@almostmagic.tech",
        to_addresses=data.to_addresses,
        cc_addresses=data.cc_addresses,
        thread_id=data.thread_id,
        status="pending",
    )
    if not email.contact_id:
        await _auto_link_contact(db, email)
    db.add(email)
    await db.commit()
    await db.refresh(email)
    return email


# Contact-scoped: GET /contacts/{id}/emails
@contact_router.get("/{contact_id}/emails", response_model=EmailListResponse)
async def get_contact_emails(
    contact_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    # Verify contact exists
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id, Contact.is_deleted == False)  # noqa: E712
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Contact not found")

    q = select(Email).where(Email.contact_id == contact_id)
    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    q = q.order_by(Email.created_at.desc())
    q = q.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(q)
    emails = result.scalars().all()
    return EmailListResponse(items=emails, total=total, page=page, page_size=page_size)


# Phase 3: Link email to contact manually
@router.post("/{email_id}/link-contact", response_model=EmailResponse)
async def link_email_to_contact(
    email_id: uuid.UUID,
    contact_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Manually link an email to a contact."""
    result = await db.execute(select(Email).where(Email.id == email_id))
    email = result.scalar_one_or_none()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    result = await db.execute(
        select(Contact).where(Contact.id == contact_id, Contact.is_deleted == False)  # noqa: E712
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Contact not found")

    email.contact_id = contact_id
    await db.commit()
    await db.refresh(email)
    return email


# Phase 3: Link email to deal
@router.post("/{email_id}/link-deal", response_model=EmailResponse)
async def link_email_to_deal(
    email_id: uuid.UUID,
    deal_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Link an email to a deal."""
    result = await db.execute(select(Email).where(Email.id == email_id))
    email = result.scalar_one_or_none()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    result = await db.execute(
        select(Deal).where(Deal.id == deal_id, Deal.is_deleted == False)  # noqa: E712
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Deal not found")

    email.deal_id = deal_id
    await db.commit()
    await db.refresh(email)
    return email


# Deal-scoped: GET /deals/{id}/emails
@deal_router.get("/{deal_id}/emails", response_model=EmailListResponse)
async def get_deal_emails(
    deal_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List emails linked to a deal."""
    result = await db.execute(
        select(Deal).where(Deal.id == deal_id, Deal.is_deleted == False)  # noqa: E712
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Deal not found")

    q = select(Email).where(Email.deal_id == deal_id)
    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    q = q.order_by(Email.created_at.desc())
    q = q.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(q)
    emails = result.scalars().all()
    return EmailListResponse(items=emails, total=total, page=page, page_size=page_size)
