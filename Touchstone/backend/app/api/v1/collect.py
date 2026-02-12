"""Touchstone — Event collection endpoint (tracking pixel receiver)."""

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.collect import CollectEvent
from app.services.collector import process_event

router = APIRouter(tags=["collect"])


@router.post("/collect", status_code=204)
async def collect(event: CollectEvent, db: AsyncSession = Depends(get_db)):
    """Receive tracking pixel events. Returns 204 No Content for speed."""
    await process_event(db, event)
    return Response(status_code=204)
