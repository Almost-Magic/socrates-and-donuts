"""Ask Genie — Natural language query interface."""
from fastapi import APIRouter
from pydantic import BaseModel
from models.database import get_connection

router = APIRouter()

class GenieQuery(BaseModel):
    question: str

@router.post("/ask")
async def ask_genie(query: GenieQuery):
    """Answer natural language questions about financial data."""
    q = query.question.lower()
    conn = get_connection()

    # Pattern matching for common questions (Phase 1 - rule-based)
    if any(w in q for w in ["spend", "spent", "spending", "expense"]):
        if "month" in q or "this month" in q:
            result = conn.execute("SELECT COALESCE(SUM(ABS(amount)),0) FROM transactions WHERE type='expense' AND date >= date('now','start of month')").fetchone()[0]
            answer = f"You've spent ${result:,.2f} this month."
        elif "year" in q:
            result = conn.execute("SELECT COALESCE(SUM(ABS(amount)),0) FROM transactions WHERE type='expense' AND date >= date('now','start of year')").fetchone()[0]
            answer = f"Total expenses this year: ${result:,.2f}."
        else:
            # Check for category keywords
            cats = conn.execute("SELECT id, name FROM categories").fetchall()
            matched_cat = None
            for cat in cats:
                if cat["name"].lower() in q:
                    matched_cat = cat; break
            if matched_cat:
                result = conn.execute("SELECT COALESCE(SUM(ABS(amount)),0) FROM transactions WHERE category_id = ?", (matched_cat["id"],)).fetchone()[0]
                answer = f"Total spending on {matched_cat['name']}: ${result:,.2f}."
            else:
                result = conn.execute("SELECT COALESCE(SUM(ABS(amount)),0) FROM transactions WHERE type='expense'").fetchone()[0]
                answer = f"Total expenses: ${result:,.2f}."

    elif any(w in q for w in ["revenue", "income", "earned", "money coming"]):
        result = conn.execute("SELECT COALESCE(SUM(amount),0) FROM transactions WHERE type='income' AND date >= date('now','start of month')").fetchone()[0]
        answer = f"Revenue this month: ${result:,.2f}."

    elif any(w in q for w in ["cash", "balance", "bank"]):
        result = conn.execute("SELECT COALESCE(SUM(balance),0) FROM bank_accounts").fetchone()[0]
        answer = f"Current cash position: ${result:,.2f}."

    elif any(w in q for w in ["overdue", "late", "unpaid"]):
        result = conn.execute("SELECT COUNT(*), COALESCE(SUM(total),0) FROM invoices WHERE status='overdue'").fetchone()
        answer = f"You have {result[0]} overdue invoice(s) totalling ${result[1]:,.2f}."

    elif any(w in q for w in ["vendor", "supplier"]):
        rows = conn.execute("SELECT name, verification_status FROM contacts WHERE type='vendor' AND is_active=1 ORDER BY name LIMIT 10").fetchall()
        answer = "Your vendors: " + ", ".join(f"{r['name']} ({r['verification_status']})" for r in rows)

    elif any(w in q for w in ["uncategorised", "uncategorized", "unclassified"]):
        result = conn.execute("SELECT COUNT(*) FROM transactions WHERE category_id IS NULL").fetchone()[0]
        answer = f"You have {result} uncategorised transaction(s)."

    elif any(w in q for w in ["fragility", "health", "safe"]):
        cash = conn.execute("SELECT COALESCE(SUM(balance),0) FROM bank_accounts").fetchone()[0]
        payables = conn.execute("SELECT COALESCE(SUM(total-amount_paid),0) FROM bills WHERE status IN ('pending','approved','scheduled','overdue')").fetchone()[0]
        fragility = round(cash / max(abs(payables), 1), 2)
        status = "healthy" if fragility > 2 else "caution" if fragility > 1 else "critical"
        answer = f"Financial fragility score: {fragility} ({status}). Cash: ${cash:,.2f}, Obligations: ${abs(payables):,.2f}."

    elif "gst" in q:
        collected = conn.execute("SELECT COALESCE(SUM(gst_amount),0) FROM transactions WHERE type='income'").fetchone()[0]
        paid = conn.execute("SELECT COALESCE(SUM(gst_amount),0) FROM transactions WHERE type='expense'").fetchone()[0]
        answer = f"GST collected: ${collected:,.2f}. GST paid: ${paid:,.2f}. Net position: ${collected-paid:,.2f}."

    else:
        answer = "I'm not sure how to answer that yet. Try asking about spending, revenue, cash position, overdue invoices, GST, or uncategorised transactions."

    conn.close()
    return {"question": query.question, "answer": answer, "source": "rule_engine"}
