"""Reconciliation API."""
from fastapi import APIRouter
from models.database import get_connection, log_event
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class ReconcileAction(BaseModel):
    transaction_id: int
    invoice_id: Optional[int] = None
    bill_id: Optional[int] = None
    action: str = "accept"  # accept, reject, one_off, reviewed
    decision_note: str = ""

@router.get("/unmatched")
async def get_unmatched():
    conn = get_connection()
    rows = conn.execute(
        """SELECT t.*, c.name as category_name, ct.name as contact_name
           FROM transactions t
           LEFT JOIN categories c ON t.category_id = c.id
           LEFT JOIN contacts ct ON t.contact_id = ct.id
           WHERE t.reconciliation_status IN ('unmatched', 'suggested')
           ORDER BY t.date DESC""").fetchall()
    conn.close()
    return {"unmatched": [dict(r) for r in rows], "count": len(rows)}

@router.get("/score")
async def reconciliation_score():
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    matched = conn.execute("SELECT COUNT(*) FROM transactions WHERE reconciliation_status IN ('matched', 'one_off', 'reviewed')").fetchone()[0]
    suggested = conn.execute("SELECT COUNT(*) FROM transactions WHERE reconciliation_status = 'suggested'").fetchone()[0]
    conn.close()
    pct = round(matched / max(total, 1) * 100, 1)
    return {"total": total, "matched": matched, "suggested": suggested, "unmatched": total - matched - suggested, "percentage": pct}

@router.post("/action")
async def reconcile(action: ReconcileAction):
    conn = get_connection()
    status_map = {"accept": "matched", "reject": "unmatched", "one_off": "one_off", "reviewed": "reviewed"}
    new_status = status_map.get(action.action, "unmatched")
    conn.execute("UPDATE transactions SET reconciliation_status = ?, reconciled_with_id = ?, updated_at = datetime('now') WHERE id = ?",
                 (new_status, action.invoice_id or action.bill_id, action.transaction_id))
    log_event("transaction", action.transaction_id, f"reconciled_{action.action}", new_data={"status": new_status}, decision_note=action.decision_note, conn=conn)
    conn.commit(); conn.close()
    return {"message": f"Transaction {action.transaction_id} → {new_status}"}

@router.post("/bulk-accept")
async def bulk_accept(min_confidence: float = 0.95):
    conn = get_connection()
    rows = conn.execute("SELECT id FROM transactions WHERE reconciliation_status = 'suggested' AND categorization_confidence >= ?", (min_confidence,)).fetchall()
    for r in rows:
        conn.execute("UPDATE transactions SET reconciliation_status = 'matched', updated_at = datetime('now') WHERE id = ?", (r["id"],))
    conn.commit(); conn.close()
    return {"accepted": len(rows)}
