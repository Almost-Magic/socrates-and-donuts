"""Bills (AP) API."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from models.database import get_connection, log_event

router = APIRouter()

class BillLineCreate(BaseModel):
    description: str
    quantity: float = 1.0
    unit_price: float
    gst_treatment: str = "10"
    category_id: Optional[int] = None

class BillCreate(BaseModel):
    vendor_id: int
    bill_number: str = ""
    issue_date: str
    due_date: str
    lines: List[BillLineCreate]
    notes: str = ""

@router.get("/")
async def list_bills(status: Optional[str] = None, page: int = 1, per_page: int = 50):
    conn = get_connection()
    where = "WHERE b.status = ?" if status else ""
    params = [status] if status else []
    rows = conn.execute(
        f"""SELECT b.*, c.name as vendor_name, c.verification_status FROM bills b
            LEFT JOIN contacts c ON b.vendor_id = c.id {where}
            ORDER BY b.due_date ASC LIMIT ? OFFSET ?""",
        params + [per_page, (page-1)*per_page]).fetchall()
    total = conn.execute(f"SELECT COUNT(*) FROM bills b {where}", params).fetchone()[0]
    conn.close()
    return {"bills": [dict(r) for r in rows], "total": total}

@router.post("/")
async def create_bill(bill: BillCreate):
    conn = get_connection()
    # Check vendor verification
    vendor = conn.execute("SELECT verification_status FROM contacts WHERE id = ?", (bill.vendor_id,)).fetchone()
    if not vendor: raise HTTPException(404, "Vendor not found")

    subtotal = sum(l.quantity * l.unit_price for l in bill.lines)
    gst_total = sum(round(l.quantity * l.unit_price / 11, 2) if l.gst_treatment == "10" else 0 for l in bill.lines)

    cursor = conn.execute(
        """INSERT INTO bills (vendor_id, bill_number, status, issue_date, due_date,
            subtotal, gst_total, total, notes) VALUES (?,?,?,?,?,?,?,?,?)""",
        (bill.vendor_id, bill.bill_number, "pending", bill.issue_date, bill.due_date,
         subtotal, gst_total, subtotal, bill.notes))
    bid = cursor.lastrowid
    for i, line in enumerate(bill.lines):
        gst = round(line.quantity * line.unit_price / 11, 2) if line.gst_treatment == "10" else 0
        conn.execute(
            "INSERT INTO bill_lines (bill_id, description, quantity, unit_price, gst_treatment, gst_amount, total, category_id, display_order) VALUES (?,?,?,?,?,?,?,?,?)",
            (bid, line.description, line.quantity, line.unit_price, line.gst_treatment, gst, line.quantity * line.unit_price, line.category_id, i))

    # Fraud check: unverified vendor warning
    if vendor["verification_status"] != "verified":
        conn.execute(
            "INSERT INTO fraud_signals (severity, signal_type, description, contact_id, bill_id) VALUES (?,?,?,?,?)",
            ("medium", "unverified_vendor", f"Bill created for unverified vendor", bill.vendor_id, bid))

    log_event("bill", bid, "created", new_data={"total": subtotal, "vendor_id": bill.vendor_id}, conn=conn)
    conn.commit(); conn.close()
    return {"id": bid, "total": subtotal, "vendor_verified": vendor["verification_status"] == "verified"}
