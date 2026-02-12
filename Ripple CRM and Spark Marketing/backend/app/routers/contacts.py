"""Ripple CRM — Contacts API routes."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.contact import Contact
from app.models.tag import Tag
from app.schemas.contact import (
    ContactCreate,
    ContactListResponse,
    ContactResponse,
    ContactUpdate,
)
from app.services.audit import log_action, log_changes

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.post("", response_model=ContactResponse, status_code=201)
async def create_contact(data: ContactCreate, db: AsyncSession = Depends(get_db)):
    contact = Contact(**data.model_dump())
    db.add(contact)
    await db.flush()
    await log_action(db, "contact", str(contact.id), "create")
    await db.commit()
    await db.refresh(contact)
    return contact


@router.get("", response_model=ContactListResponse)
async def list_contacts(
    search: str | None = Query(None),
    type: str | None = Query(None),
    source: str | None = Query(None),
    health: str | None = Query(None),
    sort_by: str = Query("created_at"),
    sort_dir: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(Contact).where(Contact.is_deleted == False)

    if search:
        term = f"%{search}%"
        q = q.where(
            or_(
                Contact.first_name.ilike(term),
                Contact.last_name.ilike(term),
                Contact.email.ilike(term),
                Contact.phone.ilike(term),
            )
        )
    if type:
        q = q.where(Contact.type == type)
    if source:
        q = q.where(Contact.source == source)
    if health:
        if health == "healthy":
            q = q.where(Contact.relationship_health_score >= 70)
        elif health == "warning":
            q = q.where(Contact.relationship_health_score.between(40, 69))
        elif health == "critical":
            q = q.where(Contact.relationship_health_score < 40)

    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    sort_col = getattr(Contact, sort_by, Contact.created_at)
    q = q.order_by(sort_col.desc() if sort_dir == "desc" else sort_col.asc())
    q = q.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(q)
    contacts = result.scalars().all()

    return ContactListResponse(items=contacts, total=total, page=page, page_size=page_size)


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id, Contact.is_deleted == False)
    )
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: uuid.UUID, data: ContactUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id, Contact.is_deleted == False)
    )
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    old_data = {k: getattr(contact, k) for k in data.model_dump(exclude_unset=True)}
    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(contact, key, value)

    await log_changes(db, "contact", str(contact_id), old_data, update_data)
    await db.commit()
    await db.refresh(contact)
    return contact


@router.delete("/{contact_id}")
async def delete_contact(contact_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id, Contact.is_deleted == False)
    )
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    contact.is_deleted = True
    await log_action(db, "contact", str(contact_id), "delete")
    await db.commit()
    return {"detail": "Contact deleted"}


@router.post("/{contact_id}/tags")
async def assign_tags(
    contact_id: uuid.UUID,
    tag_ids: list[uuid.UUID],
    db: AsyncSession = Depends(get_db),
):
    """Set tags on a contact (replaces existing tags)."""
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id, Contact.is_deleted == False)
    )
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    # Fetch requested tags
    tags = []
    for tid in tag_ids:
        r = await db.execute(select(Tag).where(Tag.id == tid))
        tag = r.scalar_one_or_none()
        if tag:
            tags.append(tag)

    contact.tags = tags
    await log_action(db, "contact", str(contact_id), "tags_updated")
    await db.commit()
    await db.refresh(contact)
    return {"detail": f"Set {len(tags)} tags on contact", "tag_count": len(tags)}
