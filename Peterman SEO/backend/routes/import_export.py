"""Import/Export API."""
from fastapi import APIRouter, UploadFile, File, HTTPException
from models.database import get_connection, log_event
from typing import Optional
import csv, io, uuid, json
from datetime import datetime

router = APIRouter()

@router.post("/upload")
async def import_file(file: UploadFile = File(...)):
    """Import transactions from CSV/Excel file."""
    if not file.filename:
        raise HTTPException(400, "No file provided")

    content = await file.read()
    batch_id = str(uuid.uuid4())[:8]
    ext = file.filename.rsplit(".", 1)[-1].lower()

    if ext == "csv":
        rows = _parse_csv(content.decode("utf-8-sig"))
    else:
        raise HTTPException(400, f"Unsupported format: {ext}. Use CSV for now.")

    conn = get_connection()
    imported, duplicates, errors = 0, 0, 0

    for row in rows:
        try:
            # Duplicate check
            existing = conn.execute(
                "SELECT id FROM transactions WHERE date = ? AND amount = ? AND description = ?",
                (row["date"], row["amount"], row["description"])).fetchone()
            if existing:
                duplicates += 1; continue

            conn.execute(
                """INSERT INTO transactions (date, description, amount, type, import_batch_id,
                    categorization_source) VALUES (?, ?, ?, ?, ?, 'imported')""",
                (row["date"], row["description"], row["amount"],
                 "income" if row["amount"] > 0 else "expense", batch_id))
            imported += 1
        except Exception as e:
            errors += 1

    conn.execute(
        "INSERT INTO import_batches (id, filename, format, row_count, imported_count, duplicate_count, error_count) VALUES (?,?,?,?,?,?,?)",
        (batch_id, file.filename, ext, len(rows), imported, duplicates, errors))
    conn.commit(); conn.close()

    return {
        "batch_id": batch_id,
        "filename": file.filename,
        "total_rows": len(rows),
        "imported": imported,
        "duplicates": duplicates,
        "errors": errors,
        "message": f"{imported} imported. {duplicates} duplicates skipped. {errors} errors."
    }

@router.post("/rollback/{batch_id}")
async def rollback_import(batch_id: str):
    conn = get_connection()
    deleted = conn.execute("DELETE FROM transactions WHERE import_batch_id = ?", (batch_id,)).rowcount
    conn.execute("UPDATE import_batches SET status = 'rolled_back' WHERE id = ?", (batch_id,))
    conn.commit(); conn.close()
    return {"message": f"Rolled back {deleted} transactions", "batch_id": batch_id}

@router.get("/history")
async def import_history():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM import_batches ORDER BY created_at DESC LIMIT 20").fetchall()
    conn.close()
    return {"imports": [dict(r) for r in rows]}

def _parse_csv(text: str):
    reader = csv.DictReader(io.StringIO(text))
    rows = []
    for r in reader:
        # Try common column names
        date = r.get("Date") or r.get("date") or r.get("Transaction Date") or ""
        desc = r.get("Description") or r.get("description") or r.get("Narrative") or r.get("Details") or ""
        amount = r.get("Amount") or r.get("amount") or ""
        # Handle debit/credit columns
        if not amount:
            debit = float(r.get("Debit", 0) or 0)
            credit = float(r.get("Credit", 0) or 0)
            amount = credit - debit if credit else -debit

        try:
            amount = float(str(amount).replace(",", "").replace("$", "").strip())
        except (ValueError, TypeError):
            continue

        if date and desc:
            rows.append({"date": date.strip(), "description": desc.strip(), "amount": amount})
    return rows
