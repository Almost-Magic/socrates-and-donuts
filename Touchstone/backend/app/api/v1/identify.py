"""Touchstone — Contact identification endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.identify import IdentifyRequest, IdentifyResponse
from app.services.session import identify_contact

router = APIRouter(tags=["identify"])


@router.post("/identify", response_model=IdentifyResponse)
async def identify(req: IdentifyRequest, db: AsyncSession = Depends(get_db)):
    """Identify an anonymous visitor by email. Backfills touchpoints."""
    return await identify_contact(db, req)
