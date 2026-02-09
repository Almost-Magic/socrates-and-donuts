"""Dashboard API — Today's Priority, metrics, health summary."""

from fastapi import APIRouter
from models.database import get_connection
from datetime import datetime, timedelta

router = APIRouter()


@router.get("/")
async def get_dashboard():
    """Get full dashboard data."""
    conn = get_connection()
    now = datetime.now()

    # Cash position
    cash = conn.execute(
        "SELECT COALESCE(SUM(balance), 0) as total FROM bank_accounts"
    ).fetchone()["total"]

    # Receivables
    receivables = conn.execute(
        "SELECT COALESCE(SUM(total), 0) as total, "
        "COUNT(*) as count FROM invoices WHERE status IN ('sent', 'overdue')"
    ).fetchone()
    overdue_invoices = conn.execute(
        "SELECT COUNT(*) as count FROM invoices WHERE status = 'overdue'"
    ).fetchone()["count"]

    # Payables
    payables = conn.execute(
        "SELECT COALESCE(SUM(total - amount_paid), 0) as total, "
        "COUNT(*) as count FROM bills WHERE status IN ('pending', 'approved', 'scheduled', 'overdue')"
    ).fetchone()
    overdue_bills = conn.execute(
        "SELECT COUNT(*) as count FROM bills WHERE status = 'overdue'"
    ).fetchone()["count"]

    # Uncategorised
    uncategorised = conn.execute(
        "SELECT COUNT(*) as count FROM transactions WHERE category_id IS NULL"
    ).fetchone()["count"]

    # Unmatched reconciliation
    unmatched = conn.execute(
        "SELECT COUNT(*) as count FROM transactions WHERE reconciliation_status = 'unmatched'"
    ).fetchone()["count"]

    # GST position (current quarter)
    gst_collected = conn.execute(
        "SELECT COALESCE(SUM(gst_amount), 0) FROM transactions WHERE type = 'income' AND date >= date('now', 'start of month', '-2 months')"
    ).fetchone()[0]
    gst_paid = conn.execute(
        "SELECT COALESCE(SUM(gst_amount), 0) FROM transactions WHERE type = 'expense' AND date >= date('now', 'start of month', '-2 months')"
    ).fetchone()[0]

    # Transaction stats
    total_txn = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    auto_categorised = conn.execute(
        "SELECT COUNT(*) FROM transactions WHERE categorization_source IN ('rule', 'ai_auto')"
    ).fetchone()[0]

    # Fraud signals
    active_fraud = conn.execute(
        "SELECT COUNT(*) as count FROM fraud_signals WHERE is_resolved = 0"
    ).fetchone()["count"]
    high_fraud = conn.execute(
        "SELECT COUNT(*) as count FROM fraud_signals WHERE is_resolved = 0 AND severity = 'high'"
    ).fetchone()["count"]

    # Vendor verification
    total_vendors = conn.execute(
        "SELECT COUNT(*) FROM contacts WHERE type = 'vendor' AND is_active = 1"
    ).fetchone()[0]
    verified_vendors = conn.execute(
        "SELECT COUNT(*) FROM contacts WHERE type = 'vendor' AND is_active = 1 AND verification_status = 'verified'"
    ).fetchone()[0]

    # Learning metrics
    rules_count = conn.execute("SELECT COUNT(*) FROM categorization_rules").fetchone()[0]
    corrections = conn.execute("SELECT COUNT(*) FROM correction_events").fetchone()[0]
    accuracy = round((1 - (corrections / max(total_txn, 1))) * 100, 1) if total_txn > 0 else 0

    # Settings
    biz = conn.execute("SELECT * FROM business WHERE id = 1").fetchone()

    conn.close()

    # Calculate fragility
    obligations = abs(payables["total"]) + abs(gst_collected - gst_paid)
    fragility = round(cash / max(obligations, 1), 2)
    safe_to_spend = max(0, cash - abs(payables["total"]) - abs(gst_collected - gst_paid) - (biz["min_cash_buffer"] or 5000))

    # Audit readiness
    categorised_pct = round((total_txn - uncategorised) / max(total_txn, 1) * 100, 1)
    reconciled = conn.execute if False else 0  # placeholder
    audit_readiness = min(100, categorised_pct)

    # Today's Priority
    priority = _calculate_priority(high_fraud, active_fraud, fragility, overdue_invoices, uncategorised, overdue_bills)

    return {
        "cash_position": round(cash, 2),
        "safe_to_spend": round(safe_to_spend, 2),
        "fragility_score": fragility,
        "fragility_status": "healthy" if fragility > 2.0 else "caution" if fragility > 1.0 else "critical",
        "receivables": {"total": round(receivables["total"], 2), "count": receivables["count"], "overdue": overdue_invoices},
        "payables": {"total": round(abs(payables["total"]), 2), "count": payables["count"], "overdue": overdue_bills},
        "gst_position": {"collected": round(gst_collected, 2), "paid": round(gst_paid, 2), "net": round(gst_collected - gst_paid, 2)},
        "uncategorised": uncategorised,
        "unmatched": unmatched,
        "fraud": {"active_signals": active_fraud, "high_severity": high_fraud},
        "vendors": {"total": total_vendors, "verified": verified_vendors},
        "audit_readiness": round(audit_readiness, 1),
        "learning": {
            "phase": _determine_phase(total_txn, accuracy),
            "accuracy": accuracy,
            "rules": rules_count,
            "corrections": corrections,
            "auto_categorised": auto_categorised,
            "total_transactions": total_txn,
        },
        "today_priority": priority,
        "business_health": "strong" if fragility > 2.0 and audit_readiness > 85 and high_fraud == 0 else "attention" if fragility > 1.0 else "critical",
    }


@router.get("/priority")
async def get_priority():
    """Get today's single highest priority action."""
    dashboard = await get_dashboard()
    return dashboard["today_priority"]


def _calculate_priority(high_fraud, active_fraud, fragility, overdue_invoices, uncategorised, overdue_bills):
    """Calculate single highest priority action."""
    if high_fraud > 0:
        return {"type": "fraud", "severity": "critical", "message": f"🔴 {high_fraud} high-severity fraud signal(s) — review immediately", "action": "fraud_guard"}
    if fragility < 1.0:
        return {"type": "cash_crisis", "severity": "critical", "message": "🔴 Cash position critical — obligations exceed available cash", "action": "cashflow"}
    if overdue_invoices > 0:
        return {"type": "overdue_invoices", "severity": "high", "message": f"⚠️ {overdue_invoices} overdue invoice(s) — chase payments", "action": "invoices"}
    if uncategorised > 5:
        return {"type": "uncategorised", "severity": "medium", "message": f"📋 {uncategorised} uncategorised transactions — audit readiness drops ~{uncategorised}%", "action": "transactions"}
    if overdue_bills > 0:
        return {"type": "overdue_bills", "severity": "medium", "message": f"📋 {overdue_bills} overdue bill(s) — review payments", "action": "bills"}
    return {"type": "all_clear", "severity": "none", "message": "✅ All caught up! Nothing urgent.", "action": "dashboard"}


def _determine_phase(total_txn, accuracy):
    """Determine Genie's current learning phase."""
    if total_txn < 50:
        return "observation"
    if accuracy < 90:
        return "suggestion"
    if accuracy < 98:
        return "automation"
    return "autonomous"
