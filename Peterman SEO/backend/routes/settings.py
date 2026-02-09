"""Settings API."""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from models.database import get_connection

router = APIRouter()

class BusinessSettings(BaseModel):
    name: Optional[str] = None
    abn: Optional[str] = None
    gst_registered: Optional[bool] = None
    financial_year_start: Optional[str] = None
    bas_frequency: Optional[str] = None
    state: Optional[str] = None
    accountant_mode: Optional[str] = None
    confidence_threshold: Optional[float] = None
    min_cash_buffer: Optional[float] = None
    hourly_rate: Optional[float] = None
    theme: Optional[str] = None
    font_size: Optional[str] = None
    reduce_animations: Optional[bool] = None
    sidebar_collapsed: Optional[bool] = None

@router.get("/")
async def get_settings():
    conn = get_connection()
    biz = conn.execute("SELECT * FROM business WHERE id = 1").fetchone()
    conn.close()
    return dict(biz) if biz else {}

@router.put("/")
async def update_settings(settings: BusinessSettings):
    conn = get_connection()
    updates = {k: v for k, v in settings.model_dump().items() if v is not None}
    if updates:
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        conn.execute(f"UPDATE business SET {set_clause}, updated_at = datetime('now') WHERE id = 1", list(updates.values()))
    conn.commit(); conn.close()
    return {"message": "Settings updated", "updated": list(updates.keys())}

@router.post("/onboarding/complete")
async def complete_onboarding():
    conn = get_connection()
    conn.execute("UPDATE business SET onboarding_complete = 1 WHERE id = 1")
    conn.commit(); conn.close()
    return {"message": "Onboarding complete"}

@router.get("/categories")
async def list_categories():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM categories ORDER BY type, display_order").fetchall()
    conn.close()
    return {"categories": [dict(r) for r in rows]}
