"""Transactions API — CRUD, bulk operations, categorisation, notes."""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from models.database import get_connection, log_event
from datetime import datetime
import uuid

router = APIRouter()


class TransactionCreate(BaseModel):
    date: str
    description: str
    amount: float
    type: str = "expense"
    category_id: Optional[int] = None
    contact_id: Optional[int] = None
    bank_account_id: Optional[int] = None
    gst_treatment: str = "10"
    notes: str = ""


class TransactionUpdate(BaseModel):
    category_id: Optional[int] = None
    contact_id: Optional[int] = None
    gst_treatment: Optional[str] = None
    notes: Optional[str] = None
    decision_note: Optional[str] = ""


class BulkReclassify(BaseModel):
    transaction_ids: List[int]
    category_id: int
    teach_genie: bool = True
    decision_note: str = ""


class BulkTag(BaseModel):
    transaction_ids: List[int]
    tag: str


@router.get("/")
async def list_transactions(
    page: int = 1,
    per_page: int = 50,
    category_id: Optional[int] = None,
    contact_id: Optional[int] = None,
    type: Optional[str] = None,
    status: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    search: Optional[str] = None,
    uncategorised_only: bool = False,
    sort_by: str = "date",
    sort_order: str = "desc",
):
    """List transactions with filters, pagination, and sorting."""
    conn = get_connection()
    conditions = []
    params = []

    if category_id:
        conditions.append("t.category_id = ?")
        params.append(category_id)
    if contact_id:
        conditions.append("t.contact_id = ?")
        params.append(contact_id)
    if type:
        conditions.append("t.type = ?")
        params.append(type)
    if status:
        conditions.append("t.reconciliation_status = ?")
        params.append(status)
    if date_from:
        conditions.append("t.date >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("t.date <= ?")
        params.append(date_to)
    if search:
        conditions.append("(t.description LIKE ? OR c2.name LIKE ?)")
        params.extend([f"%{search}%", f"%{search}%"])
    if uncategorised_only:
        conditions.append("t.category_id IS NULL")

    where = " WHERE " + " AND ".join(conditions) if conditions else ""
    allowed_sorts = {"date": "t.date", "amount": "t.amount", "description": "t.description"}
    order_col = allowed_sorts.get(sort_by, "t.date")
    order_dir = "DESC" if sort_order == "desc" else "ASC"

    total = conn.execute(
        f"SELECT COUNT(*) FROM transactions t LEFT JOIN contacts c2 ON t.contact_id = c2.id {where}", params
    ).fetchone()[0]

    offset = (page - 1) * per_page
    rows = conn.execute(
        f"""SELECT t.*, c.name as category_name, c2.name as contact_name
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            LEFT JOIN contacts c2 ON t.contact_id = c2.id
            {where}
            ORDER BY {order_col} {order_dir}
            LIMIT ? OFFSET ?""",
        params + [per_page, offset],
    ).fetchall()

    conn.close()
    return {
        "transactions": [dict(r) for r in rows],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page,
    }


@router.post("/")
async def create_transaction(txn: TransactionCreate):
    """Create a single transaction."""
    conn = get_connection()
    gst_amount = round(txn.amount / 11, 2) if txn.gst_treatment == "10" else 0.0

    cursor = conn.execute(
        """INSERT INTO transactions (date, description, amount, type, category_id, contact_id,
            bank_account_id, gst_treatment, gst_amount, categorization_source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'manual')""",
        (txn.date, txn.description, txn.amount, txn.type, txn.category_id,
         txn.contact_id, txn.bank_account_id, txn.gst_treatment, gst_amount),
    )
    txn_id = cursor.lastrowid
    log_event("transaction", txn_id, "created", new_data=txn.model_dump(), conn=conn)

    if txn.notes:
        conn.execute(
            "INSERT INTO transaction_notes (transaction_id, content) VALUES (?, ?)",
            (txn_id, txn.notes),
        )
    conn.commit()
    conn.close()
    return {"id": txn_id, "message": "Transaction created"}


@router.put("/{txn_id}")
async def update_transaction(txn_id: int, update: TransactionUpdate):
    """Update a transaction. Logs correction events for category changes."""
    conn = get_connection()
    existing = conn.execute("SELECT * FROM transactions WHERE id = ?", (txn_id,)).fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Transaction not found")

    updates = {}
    if update.category_id is not None and update.category_id != existing["category_id"]:
        # Log correction event (regret learning)
        conn.execute(
            "INSERT INTO correction_events (transaction_id, old_category_id, new_category_id, decision_note) VALUES (?, ?, ?, ?)",
            (txn_id, existing["category_id"], update.category_id, update.decision_note or ""),
        )
        updates["category_id"] = update.category_id
        updates["categorization_source"] = "manual"
        updates["categorization_confidence"] = 1.0

    if update.gst_treatment is not None:
        updates["gst_treatment"] = update.gst_treatment
        updates["gst_amount"] = round(existing["amount"] / 11, 2) if update.gst_treatment == "10" else 0.0

    if update.contact_id is not None:
        updates["contact_id"] = update.contact_id

    if updates:
        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
        conn.execute(
            f"UPDATE transactions SET {set_clause}, updated_at = datetime('now') WHERE id = ?",
            list(updates.values()) + [txn_id],
        )
        log_event("transaction", txn_id, "updated",
                  old_data=dict(existing), new_data=updates,
                  decision_note=update.decision_note or "", conn=conn)

    conn.commit()
    conn.close()
    return {"message": "Transaction updated", "corrections_logged": "category_id" in updates}


@router.post("/bulk/reclassify")
async def bulk_reclassify(data: BulkReclassify):
    """Bulk reclassify transactions with optional Genie learning."""
    conn = get_connection()
    batch_id = str(uuid.uuid4())[:8]
    reclassified = 0

    for txn_id in data.transaction_ids:
        existing = conn.execute("SELECT * FROM transactions WHERE id = ?", (txn_id,)).fetchone()
        if existing and existing["category_id"] != data.category_id:
            conn.execute(
                "INSERT INTO correction_events (transaction_id, old_category_id, new_category_id, batch_id, decision_note) VALUES (?, ?, ?, ?, ?)",
                (txn_id, existing["category_id"], data.category_id, batch_id, data.decision_note),
            )
            conn.execute(
                "UPDATE transactions SET category_id = ?, categorization_source = 'manual', updated_at = datetime('now') WHERE id = ?",
                (data.category_id, txn_id),
            )
            reclassified += 1

    if data.teach_genie and reclassified > 0:
        # Extract vendor pattern from first transaction
        first = conn.execute("SELECT description FROM transactions WHERE id = ?", (data.transaction_ids[0],)).fetchone()
        if first:
            vendor = first["description"].split(" ")[0].upper()
            conn.execute(
                "INSERT OR REPLACE INTO categorization_rules (vendor_pattern, category_id, confidence, match_count) VALUES (?, ?, 0.9, ?)",
                (vendor, data.category_id, reclassified),
            )

    log_event("bulk", 0, "bulk_reclassify",
              new_data={"batch_id": batch_id, "count": reclassified, "category_id": data.category_id}, conn=conn)
    conn.commit()
    conn.close()
    return {"batch_id": batch_id, "reclassified": reclassified, "rule_created": data.teach_genie}


@router.post("/bulk/undo/{batch_id}")
async def bulk_undo(batch_id: str):
    """Undo a bulk reclassification by batch ID."""
    conn = get_connection()
    corrections = conn.execute(
        "SELECT * FROM correction_events WHERE batch_id = ?", (batch_id,)
    ).fetchall()

    reverted = 0
    for c in corrections:
        conn.execute(
            "UPDATE transactions SET category_id = ?, updated_at = datetime('now') WHERE id = ?",
            (c["old_category_id"], c["transaction_id"]),
        )
        reverted += 1

    conn.execute("DELETE FROM correction_events WHERE batch_id = ?", (batch_id,))
    log_event("bulk", 0, "bulk_undo", new_data={"batch_id": batch_id, "reverted": reverted}, conn=conn)
    conn.commit()
    conn.close()
    return {"reverted": reverted}


@router.get("/stats")
async def transaction_stats():
    """Transaction statistics for status bar and learning dashboard."""
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    categorised = conn.execute("SELECT COUNT(*) FROM transactions WHERE category_id IS NOT NULL").fetchone()[0]
    auto = conn.execute("SELECT COUNT(*) FROM transactions WHERE categorization_source IN ('rule', 'ai_auto')").fetchone()[0]
    corrections = conn.execute("SELECT COUNT(*) FROM correction_events").fetchone()[0]
    income = conn.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE type = 'income'").fetchone()[0]
    expenses = conn.execute("SELECT COALESCE(SUM(ABS(amount)), 0) FROM transactions WHERE type = 'expense'").fetchone()[0]

    # Time saved calculation
    time_saved_seconds = (auto * 30) + (categorised * 5)  # auto=30s, manual categorised=5s saved on lookup
    biz = conn.execute("SELECT hourly_rate FROM business WHERE id = 1").fetchone()
    hourly_rate = biz["hourly_rate"] if biz else 30.0
    money_saved = round((time_saved_seconds / 3600) * hourly_rate, 2)

    conn.close()
    return {
        "total": total,
        "categorised": categorised,
        "uncategorised": total - categorised,
        "auto_categorised": auto,
        "corrections": corrections,
        "accuracy": round((1 - corrections / max(total, 1)) * 100, 1),
        "correction_rate": round(corrections / max(total, 1) * 100, 1),
        "income_total": round(income, 2),
        "expense_total": round(expenses, 2),
        "time_saved_hours": round(time_saved_seconds / 3600, 1),
        "money_saved": money_saved,
    }
