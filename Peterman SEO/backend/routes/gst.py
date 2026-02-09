"""GST API."""
from fastapi import APIRouter
from models.database import get_connection

router = APIRouter()

@router.get("/position")
async def gst_position():
    conn = get_connection()
    collected = conn.execute("SELECT COALESCE(SUM(gst_amount),0) FROM transactions WHERE type='income' AND date >= date('now','start of month','-2 months')").fetchone()[0]
    paid = conn.execute("SELECT COALESCE(SUM(gst_amount),0) FROM transactions WHERE type='expense' AND date >= date('now','start of month','-2 months')").fetchone()[0]
    needs_review = conn.execute("SELECT COUNT(*) FROM transactions WHERE gst_treatment IS NULL OR gst_treatment = ''").fetchone()[0]
    conn.close()
    return {"collected_1a": round(collected,2), "paid_1b": round(paid,2), "net": round(collected-paid,2), "position": "refund" if collected < paid else "payable", "needs_review": needs_review}

@router.get("/by-category")
async def gst_by_category():
    conn = get_connection()
    rows = conn.execute(
        """SELECT c.name, c.type, SUM(t.gst_amount) as gst_total, COUNT(*) as count
           FROM transactions t JOIN categories c ON t.category_id = c.id
           WHERE t.gst_amount > 0 GROUP BY c.id ORDER BY gst_total DESC""").fetchall()
    conn.close()
    return {"categories": [dict(r) for r in rows]}
