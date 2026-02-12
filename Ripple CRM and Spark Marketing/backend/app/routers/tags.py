"""Ripple CRM — Tags API routes."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.contact import Contact
from app.models.tag import Tag, contact_tags
from app.schemas.tag import (
    TagCreate,
    TagListResponse,
    TagResponse,
    TagUpdate,
    TagWithCountResponse,
)
from app.services.audit import log_action

router = APIRouter(prefix="/tags", tags=["tags"])


@router.post("", response_model=TagResponse, status_code=201)
async def create_tag(data: TagCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Tag).where(Tag.name == data.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Tag already exists")
    tag = Tag(**data.model_dump())
    db.add(tag)
    await db.flush()
    await log_action(db, "tag", str(tag.id), "create")
    await db.commit()
    await db.refresh(tag)
    return tag


@router.get("", response_model=TagListResponse)
async def list_tags(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tag).order_by(Tag.name))
    tags = result.scalars().all()
    items = []
    for tag in tags:
        count_q = select(func.count()).select_from(contact_tags).where(contact_tags.c.tag_id == tag.id)
        count = (await db.execute(count_q)).scalar() or 0
        items.append(TagWithCountResponse(
            id=tag.id, name=tag.name, colour=tag.colour,
            created_at=tag.created_at, contact_count=count,
        ))
    return TagListResponse(items=items, total=len(items))


@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(tag_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(tag_id: uuid.UUID, data: TagUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(tag, key, value)
    await log_action(db, "tag", str(tag_id), "update")
    await db.commit()
    await db.refresh(tag)
    return tag


@router.delete("/{tag_id}")
async def delete_tag(tag_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    await db.delete(tag)
    await log_action(db, "tag", str(tag_id), "delete")
    await db.commit()
    return {"detail": "Tag deleted"}
