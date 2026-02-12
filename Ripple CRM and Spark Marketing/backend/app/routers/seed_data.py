"""Ripple CRM — Seed data API endpoints.

POST /api/seed-data/load       Load Australian demo data
POST /api/seed-data/clear      Clear seed data (dry run by default)
GET  /api/seed-data/status     Count seed vs real records
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.seeds.crm_seed import clear_seed_data, get_seed_counts, load_seed_data

router = APIRouter(prefix="/seed-data", tags=["seed-data"])


@router.post("/load")
async def load_seed(db: AsyncSession = Depends(get_db)):
    """Load 15 companies, 30 contacts, 20 deals, 15 interactions, 5 tasks."""
    result = await load_seed_data(db)
    if "error" in result:
        return {"status": "error", "message": result["error"]}
    return {"status": "ok", "created": result}


@router.post("/clear")
async def clear_seed(
    confirm: bool = Query(False, description="Set to true to actually delete"),
    db: AsyncSession = Depends(get_db),
):
    """Delete only seed records. Dry run by default; pass ?confirm=true to delete."""
    result = await clear_seed_data(db, confirm=confirm)
    return result


@router.get("/status")
async def seed_status(db: AsyncSession = Depends(get_db)):
    """Show count of seed vs real records."""
    counts = await get_seed_counts(db)
    return counts
