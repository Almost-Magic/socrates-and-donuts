"""Ripple CRM — Privacy / Transparency Portal API routes.

DSAR report generation, consent tracking, privacy management,
consent preferences, and DSAR request workflow.
Australian Privacy Act compliant.
"""

import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.commitment import Commitment
from app.models.consent_preference import ConsentPreference
from app.models.contact import Contact
from app.models.dsar_request import DsarRequest
from app.models.email import Email
from app.models.interaction import Interaction
from app.models.note import Note
from app.models.privacy_consent import PrivacyConsent
from app.schemas.consent_preference import ConsentPreferenceResponse, ConsentPreferenceUpdate
from app.schemas.dsar_request import (
    DsarRequestCreate,
    DsarRequestListResponse,
    DsarRequestResponse,
    DsarRequestUpdate,
)

router = APIRouter(prefix="/privacy", tags=["privacy"])

# Contact-scoped consent preferences
contact_router = APIRouter(prefix="/contacts", tags=["privacy"])


@router.get("/contacts/{contact_id}/report")
async def generate_dsar_report(
    contact_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    """Generate a DSAR (Data Subject Access Request) report for a contact.
    Returns all data held about the contact. Australian Privacy Act compliant."""
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id)
    )
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    # Interactions
    result = await db.execute(
        select(Interaction).where(Interaction.contact_id == contact_id)
        .order_by(Interaction.occurred_at.desc())
    )
    interactions = result.scalars().all()

    # Notes
    result = await db.execute(
        select(Note).where(Note.contact_id == contact_id)
        .order_by(Note.created_at.desc())
    )
    notes = result.scalars().all()

    # Commitments
    result = await db.execute(
        select(Commitment).where(Commitment.contact_id == contact_id)
    )
    commitments = result.scalars().all()

    # Consents
    result = await db.execute(
        select(PrivacyConsent).where(PrivacyConsent.contact_id == contact_id)
        .order_by(PrivacyConsent.created_at.desc())
    )
    consents = result.scalars().all()

    # Emails
    result = await db.execute(
        select(Email).where(Email.contact_id == contact_id)
        .order_by(Email.created_at.desc())
    )
    emails = result.scalars().all()

    return {
        "report_generated_at": datetime.now(timezone.utc).isoformat(),
        "compliance_note": "Generated under the Australian Privacy Act 1988 — APP 12 (Access to personal information)",
        "contact": {
            "id": str(contact.id),
            "first_name": contact.first_name,
            "last_name": contact.last_name,
            "email": contact.email,
            "phone": contact.phone,
            "role": contact.role,
            "type": contact.type,
            "source": contact.source,
            "created_at": contact.created_at.isoformat() if contact.created_at else None,
        },
        "interactions": [
            {
                "id": str(i.id),
                "type": i.type,
                "subject": i.subject,
                "content": i.content,
                "occurred_at": i.occurred_at.isoformat() if i.occurred_at else None,
            }
            for i in interactions
        ],
        "notes": [
            {
                "id": str(n.id),
                "content": n.content,
                "created_at": n.created_at.isoformat() if n.created_at else None,
            }
            for n in notes
        ],
        "commitments": [
            {
                "id": str(c.id),
                "description": c.description,
                "committed_by": c.committed_by,
                "status": c.status,
                "due_date": c.due_date.isoformat() if c.due_date else None,
            }
            for c in commitments
        ],
        "emails": [
            {
                "id": str(e.id),
                "direction": e.direction,
                "subject": e.subject,
                "from_address": e.from_address,
                "to_addresses": e.to_addresses,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in emails
        ],
        "consents": [
            {
                "id": str(c.id),
                "consent_type": c.consent_type,
                "granted": c.granted,
                "granted_at": c.granted_at.isoformat() if c.granted_at else None,
                "revoked_at": c.revoked_at.isoformat() if c.revoked_at else None,
                "source": c.source,
            }
            for c in consents
        ],
        "total_interactions": len(interactions),
        "total_notes": len(notes),
        "total_commitments": len(commitments),
        "total_emails": len(emails),
    }


@router.get("/contacts/{contact_id}/export")
async def export_contact_data(
    contact_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    """Export all contact data as downloadable JSON. APP 12 compliant."""
    report = await generate_dsar_report(contact_id, db)
    return JSONResponse(
        content=report,
        headers={
            "Content-Disposition": f'attachment; filename="contact_{str(contact_id)[:8]}_export.json"',
        },
    )


@router.post("/contacts/{contact_id}/deletion-request")
async def request_contact_deletion(
    contact_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    """Request deletion of contact data. Creates a DSAR request with type 'deletion'.
    Under the Australian Privacy Act, APP 13 provides the right to correction/deletion."""
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id, Contact.is_deleted == False)  # noqa: E712
    )
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    dsar = DsarRequest(
        contact_id=contact_id,
        request_type="deletion",
        status="pending",
        notes="Automated deletion request via Transparency Portal",
    )
    db.add(dsar)
    await db.commit()
    await db.refresh(dsar)
    return {
        "detail": "Deletion request created. Will be reviewed and processed.",
        "request_id": str(dsar.id),
        "status": dsar.status,
    }


@router.get("/consents")
async def list_consents(
    contact_id: uuid.UUID | None = Query(None),
    consent_type: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List privacy consents with optional filtering."""
    q = select(PrivacyConsent)
    if contact_id:
        q = q.where(PrivacyConsent.contact_id == contact_id)
    if consent_type:
        q = q.where(PrivacyConsent.consent_type == consent_type)

    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    q = q.order_by(PrivacyConsent.created_at.desc())
    q = q.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(q)
    consents = result.scalars().all()

    return {
        "items": [
            {
                "id": str(c.id),
                "contact_id": str(c.contact_id),
                "consent_type": c.consent_type,
                "granted": c.granted,
                "granted_at": c.granted_at.isoformat() if c.granted_at else None,
                "revoked_at": c.revoked_at.isoformat() if c.revoked_at else None,
                "source": c.source,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in consents
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("/consents")
async def create_consent(
    data: dict,
    db: AsyncSession = Depends(get_db),
):
    """Record a privacy consent for a contact."""
    required = ["contact_id", "consent_type", "granted"]
    for field in required:
        if field not in data:
            raise HTTPException(status_code=422, detail=f"Missing required field: {field}")

    consent = PrivacyConsent(
        contact_id=uuid.UUID(data["contact_id"]),
        consent_type=data["consent_type"],
        granted=data["granted"],
        granted_at=datetime.now(timezone.utc) if data["granted"] else None,
        source=data.get("source"),
    )
    db.add(consent)
    await db.commit()
    await db.refresh(consent)
    return {
        "id": str(consent.id),
        "contact_id": str(consent.contact_id),
        "consent_type": consent.consent_type,
        "granted": consent.granted,
        "created_at": consent.created_at.isoformat() if consent.created_at else None,
    }


# Phase 3: DSAR Request Management
@router.post("/dsar-requests", response_model=DsarRequestResponse, status_code=201)
async def create_dsar_request(data: DsarRequestCreate, db: AsyncSession = Depends(get_db)):
    """Create a formal DSAR request."""
    result = await db.execute(
        select(Contact).where(Contact.id == data.contact_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Contact not found")

    dsar = DsarRequest(
        contact_id=data.contact_id,
        request_type=data.request_type,
        status="pending",
        notes=data.notes,
    )
    db.add(dsar)
    await db.commit()
    await db.refresh(dsar)
    return dsar


@router.get("/dsar-requests", response_model=DsarRequestListResponse)
async def list_dsar_requests(
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List DSAR requests with optional status filter."""
    q = select(DsarRequest)
    if status:
        q = q.where(DsarRequest.status == status)

    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    q = q.order_by(DsarRequest.created_at.desc())
    q = q.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(q)
    requests = result.scalars().all()
    return DsarRequestListResponse(items=requests, total=total, page=page, page_size=page_size)


@router.put("/dsar-requests/{request_id}", response_model=DsarRequestResponse)
async def update_dsar_request(
    request_id: uuid.UUID,
    data: DsarRequestUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update DSAR request status."""
    result = await db.execute(select(DsarRequest).where(DsarRequest.id == request_id))
    dsar = result.scalar_one_or_none()
    if not dsar:
        raise HTTPException(status_code=404, detail="DSAR request not found")

    dsar.status = data.status
    if data.notes is not None:
        dsar.notes = data.notes
    if data.status == "completed":
        dsar.completed_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(dsar)
    return dsar


# Phase 3: Consent Preferences per contact
@contact_router.get("/{contact_id}/consent-preferences", response_model=ConsentPreferenceResponse)
async def get_consent_preferences(
    contact_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    """Get consent preferences for a contact. Creates defaults if none exist."""
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Contact not found")

    result = await db.execute(
        select(ConsentPreference).where(ConsentPreference.contact_id == contact_id)
    )
    pref = result.scalar_one_or_none()

    if not pref:
        pref = ConsentPreference(contact_id=contact_id)
        db.add(pref)
        await db.commit()
        await db.refresh(pref)

    return pref


@contact_router.put("/{contact_id}/consent-preferences", response_model=ConsentPreferenceResponse)
async def update_consent_preferences(
    contact_id: uuid.UUID,
    data: ConsentPreferenceUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update consent preferences for a contact."""
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Contact not found")

    result = await db.execute(
        select(ConsentPreference).where(ConsentPreference.contact_id == contact_id)
    )
    pref = result.scalar_one_or_none()

    if not pref:
        pref = ConsentPreference(contact_id=contact_id)
        db.add(pref)
        await db.flush()

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(pref, key, value)

    await db.commit()
    await db.refresh(pref)
    return pref
