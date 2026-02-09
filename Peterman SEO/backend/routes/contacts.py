"""Contacts API."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from models.database import get_connection, log_event

router = APIRouter()

class ContactCreate(BaseModel):
    type: str = "client"
    name: str
    abn: str = ""
    email: str = ""
    phone: str = ""
    address: str = ""
    payment_terms: int = 30
    bsb: str = ""
    account_number: str = ""
    account_name: str = ""
    notes: str = ""

@router.get("/")
async def list_contacts(type: Optional[str] = None, search: Optional[str] = None):
    conn = get_connection()
    conditions, params = ["is_active = 1"], []
    if type:
        conditions.append("type = ?"); params.append(type)
    if search:
        conditions.append("(name LIKE ? OR email LIKE ?)"); params.extend([f"%{search}%"]*2)
    where = " WHERE " + " AND ".join(conditions)
    rows = conn.execute(f"SELECT * FROM contacts {where} ORDER BY name", params).fetchall()
    conn.close()
    return {"contacts": [dict(r) for r in rows]}

@router.post("/")
async def create_contact(c: ContactCreate):
    conn = get_connection()
    cursor = conn.execute(
        """INSERT INTO contacts (type, name, abn, email, phone, address, payment_terms,
            bsb, account_number, account_name, notes) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (c.type, c.name, c.abn, c.email, c.phone, c.address, c.payment_terms,
         c.bsb, c.account_number, c.account_name, c.notes))
    cid = cursor.lastrowid
    log_event("contact", cid, "created", new_data=c.model_dump(), conn=conn)
    conn.commit(); conn.close()
    return {"id": cid}

@router.put("/{cid}/verify")
async def verify_contact(cid: int, step: str, verified: bool = True):
    conn = get_connection()
    contact = conn.execute("SELECT * FROM contacts WHERE id = ?", (cid,)).fetchone()
    if not contact: raise HTTPException(404)
    field_map = {"abn": "verification_abn", "bsb": "verification_bsb", "phone": "verification_phone", "email": "verification_email"}
    if step not in field_map: raise HTTPException(400, "Invalid step")
    conn.execute(f"UPDATE contacts SET {field_map[step]} = ?, updated_at = datetime('now') WHERE id = ?", (1 if verified else 0, cid))
    # Check if all 4 steps done
    updated = conn.execute("SELECT * FROM contacts WHERE id = ?", (cid,)).fetchone()
    all_verified = all(updated[f"verification_{s}"] for s in ["abn", "bsb", "phone", "email"])
    if all_verified:
        conn.execute("UPDATE contacts SET verification_status = 'verified' WHERE id = ?", (cid,))
    elif any(updated[f"verification_{s}"] for s in ["abn", "bsb", "phone", "email"]):
        conn.execute("UPDATE contacts SET verification_status = 'partial' WHERE id = ?", (cid,))
    log_event("contact", cid, f"verification_{step}", new_data={"verified": verified}, conn=conn)
    conn.commit(); conn.close()
    return {"message": f"Step {step} verified", "fully_verified": all_verified}

@router.get("/{cid}/hover")
async def contact_hover(cid: int):
    conn = get_connection()
    c = conn.execute("SELECT * FROM contacts WHERE id = ?", (cid,)).fetchone()
    if not c: raise HTTPException(404)
    if c["type"] == "client":
        revenue = conn.execute("SELECT COALESCE(SUM(total),0) FROM invoices WHERE contact_id = ?", (cid,)).fetchone()[0]
        outstanding = conn.execute("SELECT COALESCE(SUM(total),0) FROM invoices WHERE contact_id = ? AND status IN ('sent','overdue')", (cid,)).fetchone()[0]
        avg_days = conn.execute("SELECT AVG(julianday(paid_at)-julianday(issue_date)) FROM invoices WHERE contact_id = ? AND paid_at IS NOT NULL", (cid,)).fetchone()[0]
        conn.close()
        return {**dict(c), "revenue_12mo": round(revenue, 2), "outstanding": round(outstanding, 2), "avg_payment_days": round(avg_days or 0, 0)}
    else:
        spend = conn.execute("SELECT COALESCE(SUM(total),0) FROM bills WHERE vendor_id = ?", (cid,)).fetchone()[0]
        conn.close()
        return {**dict(c), "spend_12mo": round(spend, 2)}
