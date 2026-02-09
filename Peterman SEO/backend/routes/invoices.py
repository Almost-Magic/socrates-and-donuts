"""Invoices API."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from models.database import get_connection, log_event
from datetime import datetime, timedelta

router = APIRouter()

class InvoiceLineCreate(BaseModel):
    description: str
    quantity: float = 1.0
    unit_price: float
    gst_treatment: str = "10"
    category_id: Optional[int] = None

class InvoiceCreate(BaseModel):
    contact_id: int
    issue_date: str
    payment_terms: int = 30
    lines: List[InvoiceLineCreate]
    notes: str = ""
    template_name: str = ""

@router.get("/")
async def list_invoices(status: Optional[str] = None, page: int = 1, per_page: int = 50):
    conn = get_connection()
    where = "WHERE i.status = ?" if status else ""
    params = [status] if status else []
    total = conn.execute(f"SELECT COUNT(*) FROM invoices i {where}", params).fetchone()[0]
    rows = conn.execute(
        f"""SELECT i.*, c.name as client_name FROM invoices i
            LEFT JOIN contacts c ON i.contact_id = c.id {where}
            ORDER BY i.issue_date DESC LIMIT ? OFFSET ?""",
        params + [per_page, (page - 1) * per_page]).fetchall()
    conn.close()
    return {"invoices": [dict(r) for r in rows], "total": total, "page": page}

@router.post("/")
async def create_invoice(inv: InvoiceCreate):
    conn = get_connection()
    # Generate invoice number
    count = conn.execute("SELECT COUNT(*) FROM invoices").fetchone()[0]
    inv_num = f"INV-{count + 1:04d}"
    due = (datetime.strptime(inv.issue_date, "%Y-%m-%d") + timedelta(days=inv.payment_terms)).strftime("%Y-%m-%d")

    subtotal = sum(l.quantity * l.unit_price for l in inv.lines)
    gst_total = sum(round(l.quantity * l.unit_price / 11, 2) if l.gst_treatment == "10" else 0 for l in inv.lines)
    total = subtotal

    cursor = conn.execute(
        """INSERT INTO invoices (invoice_number, contact_id, status, issue_date, due_date,
            subtotal, gst_total, total, notes, template_name) VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (inv_num, inv.contact_id, "draft", inv.issue_date, due, subtotal, gst_total, total, inv.notes, inv.template_name))
    inv_id = cursor.lastrowid

    for i, line in enumerate(inv.lines):
        line_gst = round(line.quantity * line.unit_price / 11, 2) if line.gst_treatment == "10" else 0
        line_total = line.quantity * line.unit_price
        conn.execute(
            "INSERT INTO invoice_lines (invoice_id, description, quantity, unit_price, gst_treatment, gst_amount, total, category_id, display_order) VALUES (?,?,?,?,?,?,?,?,?)",
            (inv_id, line.description, line.quantity, line.unit_price, line.gst_treatment, line_gst, line_total, line.category_id, i))

    log_event("invoice", inv_id, "created", new_data={"number": inv_num, "total": total}, conn=conn)
    conn.commit()
    conn.close()
    return {"id": inv_id, "invoice_number": inv_num, "total": total}

@router.put("/{inv_id}/status/{new_status}")
async def update_invoice_status(inv_id: int, new_status: str):
    conn = get_connection()
    existing = conn.execute("SELECT * FROM invoices WHERE id = ?", (inv_id,)).fetchone()
    if not existing:
        conn.close()
        raise HTTPException(404, "Invoice not found")
    extras = {}
    if new_status == "sent":
        extras["sent_at"] = datetime.now().isoformat()
    elif new_status == "paid":
        extras["paid_at"] = datetime.now().isoformat()
    set_parts = ["status = ?", "updated_at = datetime('now')"] + [f"{k} = ?" for k in extras]
    conn.execute(f"UPDATE invoices SET {', '.join(set_parts)} WHERE id = ?",
                 [new_status] + list(extras.values()) + [inv_id])
    log_event("invoice", inv_id, "status_changed", old_data={"status": existing["status"]}, new_data={"status": new_status}, conn=conn)
    conn.commit()
    conn.close()
    return {"message": f"Invoice {existing['invoice_number']} → {new_status}"}
