"""Fraud Guard API."""
from fastapi import APIRouter
from models.database import get_connection, log_event
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

@router.get("/signals")
async def get_fraud_signals(resolved: bool = False):
    conn = get_connection()
    rows = conn.execute(
        """SELECT fs.*, c.name as contact_name FROM fraud_signals fs
           LEFT JOIN contacts c ON fs.contact_id = c.id
           WHERE fs.is_resolved = ? ORDER BY fs.created_at DESC""", (1 if resolved else 0,)).fetchall()
    conn.close()
    return {"signals": [dict(r) for r in rows]}

@router.get("/score")
async def fraud_prevention_score():
    conn = get_connection()
    total_v = conn.execute("SELECT COUNT(*) FROM contacts WHERE type='vendor' AND is_active=1").fetchone()[0]
    verified_v = conn.execute("SELECT COUNT(*) FROM contacts WHERE type='vendor' AND is_active=1 AND verification_status='verified'").fetchone()[0]
    verification_pct = (verified_v / max(total_v, 1)) * 100
    unresolved = conn.execute("SELECT COUNT(*) FROM fraud_signals WHERE is_resolved=0").fetchone()[0]
    overrides = conn.execute("SELECT COUNT(*) FROM event_log WHERE event_type LIKE '%override%'").fetchone()[0]
    score = min(100, round(verification_pct * 0.3 + (100 if unresolved == 0 else max(0, 100-unresolved*20)) * 0.25 + 100 * 0.2 + 100 * 0.15 + max(0, 100-overrides*10) * 0.1))
    conn.close()
    return {"score": score, "verification_pct": round(verification_pct,1), "unresolved_signals": unresolved, "overrides": overrides, "vendors_total": total_v, "vendors_verified": verified_v}

class ResolveSignal(BaseModel):
    note: str = ""

@router.put("/signals/{signal_id}/resolve")
async def resolve_signal(signal_id: int, data: ResolveSignal):
    conn = get_connection()
    conn.execute("UPDATE fraud_signals SET is_resolved=1, resolved_note=? WHERE id=?", (data.note, signal_id))
    log_event("fraud_signal", signal_id, "resolved", new_data={"note": data.note}, conn=conn)
    conn.commit(); conn.close()
    return {"message": "Signal resolved"}

@router.get("/bank-changes")
async def bank_detail_changes():
    conn = get_connection()
    rows = conn.execute(
        """SELECT bdc.*, c.name as vendor_name FROM bank_detail_changes bdc
           LEFT JOIN contacts c ON bdc.contact_id = c.id ORDER BY bdc.created_at DESC""").fetchall()
    conn.close()
    return {"changes": [dict(r) for r in rows]}
