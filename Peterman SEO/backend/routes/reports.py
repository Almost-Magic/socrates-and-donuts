"""
Reports API — Costanza-powered structured intelligence.

Every report uses Costanza frameworks:
- Pyramid Principle: answer first, MECE structure
- SCQA: narrative arc (Situation, Complication, Question, Answer)
- ABT: financial storytelling (And, But, Therefore)
- Rule of Three: memorable key actions
- Pre-Mortem: risk analysis ("Assume this failed. Why?")
- 10-20-30: presentation structure

"George led with the bad news and buried the recommendation.
 Costanza leads with the answer and structures the evidence."
"""

from fastapi import APIRouter
from models.database import get_connection
from services.costanza_integration import (
    CostanzaReportEngine, CostanzaRiskEngine,
    ReportType, AudienceLevel, StructuredReport,
    PyramidStructure, SCQAStructure, ABTStructure, RuleOfThree,
)
from typing import Optional
from dataclasses import asdict

router = APIRouter()
report_engine = CostanzaReportEngine()
risk_engine = CostanzaRiskEngine()


@router.get("/monthly-summary")
async def monthly_summary(audience: str = "owner"):
    """
    Monthly summary powered by Costanza Pyramid + SCQA + Rule of Three.
    Answer first. Then why. Then what to do.
    """
    conn = get_connection()

    # Gather data
    cash = conn.execute("SELECT COALESCE(SUM(balance),0) FROM bank_accounts").fetchone()[0]
    revenue = conn.execute("SELECT COALESCE(SUM(amount),0) FROM transactions WHERE type='income' AND date >= date('now','start of month')").fetchone()[0]
    expenses = conn.execute("SELECT COALESCE(SUM(ABS(amount)),0) FROM transactions WHERE type='expense' AND date >= date('now','start of month')").fetchone()[0]
    overdue = conn.execute("SELECT COUNT(*) FROM invoices WHERE status='overdue'").fetchone()[0]
    overdue_amount = conn.execute("SELECT COALESCE(SUM(total),0) FROM invoices WHERE status='overdue'").fetchone()[0]
    uncategorised = conn.execute("SELECT COUNT(*) FROM transactions WHERE category_id IS NULL").fetchone()[0]
    total_txn = conn.execute("SELECT COUNT(*) FROM transactions WHERE date >= date('now','start of month')").fetchone()[0]
    auto_txn = conn.execute("SELECT COUNT(*) FROM transactions WHERE categorization_source IN ('rule','ai_auto') AND date >= date('now','start of month')").fetchone()[0]
    receivables = conn.execute("SELECT COALESCE(SUM(total),0) FROM invoices WHERE status IN ('sent','overdue')").fetchone()[0]
    payables = conn.execute("SELECT COALESCE(SUM(total-amount_paid),0) FROM bills WHERE status IN ('pending','approved','scheduled','overdue')").fetchone()[0]
    payables_week = conn.execute("SELECT COALESCE(SUM(total-amount_paid),0) FROM bills WHERE due_date <= date('now','+7 days') AND status IN ('pending','approved','scheduled')").fetchone()[0]
    zombie = conn.execute("SELECT COUNT(DISTINCT contact_id) FROM transactions WHERE type='expense' AND category_id IN (SELECT id FROM categories WHERE name LIKE '%Subscription%') AND date >= date('now','-6 months')").fetchone()[0]
    unverified = conn.execute("SELECT COUNT(*) FROM contacts WHERE type='vendor' AND verification_status != 'verified' AND is_active=1").fetchone()[0]
    corrections = conn.execute("SELECT COUNT(*) FROM correction_events WHERE created_at >= date('now','start of month')").fetchone()[0]

    biz = conn.execute("SELECT * FROM business WHERE id=1").fetchone()
    hourly_rate = biz["hourly_rate"] if biz else 30.0

    # Calculate derived
    obligations = abs(payables) + abs(conn.execute("SELECT COALESCE(SUM(CASE WHEN type='income' THEN gst_amount ELSE -gst_amount END),0) FROM transactions WHERE date >= date('now','start of month','-2 months')").fetchone()[0])
    fragility = round(cash / max(obligations, 1), 2)
    safe_to_spend = max(0, cash - abs(payables) - (biz["min_cash_buffer"] if biz else 5000))
    auto_pct = round(auto_txn / max(total_txn, 1) * 100, 1)
    accuracy = round((1 - corrections / max(total_txn, 1)) * 100, 1) if total_txn > 0 else 100
    time_saved_hrs = round((auto_txn * 30) / 3600, 1)
    money_saved = round(time_saved_hrs * hourly_rate, 2)
    audit_readiness = min(100, round((total_txn - uncategorised) / max(total_txn, 1) * 100, 1))

    conn.close()

    # Build Costanza-structured report
    audience_level = AudienceLevel(audience) if audience in [a.value for a in AudienceLevel] else AudienceLevel.OWNER
    report = report_engine.monthly_summary({
        "cash_position": cash, "revenue": revenue, "expenses": expenses,
        "fragility_score": fragility, "safe_to_spend": safe_to_spend,
        "overdue_invoices": overdue, "overdue_amount": overdue_amount,
        "uncategorised": uncategorised, "total_transactions": total_txn,
        "receivables": receivables, "payables": payables, "payables_due_week": payables_week,
        "audit_readiness": audit_readiness, "accuracy": accuracy, "auto_pct": auto_pct,
        "time_saved": time_saved_hrs, "money_saved": money_saved,
        "zombie_expenses": zombie, "unverified_vendors": unverified,
        "month": "This Month",
    }, audience_level)

    return asdict(report)


@router.get("/monthly-summary/presentation")
async def monthly_presentation(audience: str = "owner"):
    """
    Convert monthly summary into a slide deck structure.
    Uses 10-20-30 rule: ≤10 slides, ≤20 min, ≥30pt font.
    """
    report_data = await monthly_summary(audience)

    # Reconstruct dataclasses from dict
    pyramid = PyramidStructure(**report_data["pyramid"]) if report_data.get("pyramid") else None
    scqa = SCQAStructure(**report_data["scqa"]) if report_data.get("scqa") else None
    abt = ABTStructure(**report_data["abt"]) if report_data.get("abt") else None
    key_three = RuleOfThree(**report_data["key_three"]) if report_data.get("key_three") else None

    report = StructuredReport(
        title=report_data["title"],
        report_type=ReportType(report_data["report_type"]),
        audience=AudienceLevel(report_data["audience"]),
        date=report_data["date"],
        pyramid=pyramid, scqa=scqa, abt=abt, key_three=key_three,
        sections=report_data.get("sections", []),
        recommendations=report_data.get("recommendations", []),
    )
    slides = report_engine.presentation_structure(report)
    return {
        "title": report.title,
        "slide_count": len(slides),
        "rule_check": {"slides_ok": len(slides) <= 10, "target_minutes": 20, "min_font": 30},
        "slides": slides,
    }


@router.get("/risk-analysis")
async def risk_analysis():
    """
    Pre-Mortem risk analysis.
    "Assume the business fails in 90 days. Why?"
    """
    conn = get_connection()
    cash = conn.execute("SELECT COALESCE(SUM(balance),0) FROM bank_accounts").fetchone()[0]
    payables = conn.execute("SELECT COALESCE(SUM(total-amount_paid),0) FROM bills WHERE status IN ('pending','approved','scheduled','overdue')").fetchone()[0]
    fragility = round(cash / max(abs(payables), 1), 2)
    overdue = conn.execute("SELECT COUNT(*) FROM invoices WHERE status='overdue'").fetchone()[0]
    unverified = conn.execute("SELECT COUNT(*) FROM contacts WHERE type='vendor' AND verification_status != 'verified' AND is_active=1").fetchone()[0]

    # Client concentration (top client % of revenue)
    top_client = conn.execute(
        "SELECT COALESCE(MAX(client_total), 0) * 100.0 / NULLIF((SELECT SUM(total) FROM invoices), 0) FROM (SELECT contact_id, SUM(total) as client_total FROM invoices GROUP BY contact_id)"
    ).fetchone()[0] or 0

    conn.close()

    return risk_engine.pre_mortem(
        "Business viability over next 90 days",
        {
            "fragility_score": fragility,
            "overdue_invoices": overdue,
            "unverified_vendors": unverified,
            "client_concentration": round(top_client, 1),
        },
    )


@router.get("/cashflow-narrative")
async def cashflow_narrative():
    """SCQA narrative for cash flow — used in reports and Accountant Pack."""
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://localhost:8000/api/cashflow/forecast")
            forecast_data = resp.json()
    except Exception:
        forecast_data = {"current_cash": 0, "min_buffer": 5000, "forecast": []}

    narrative = report_engine.cash_flow_narrative(forecast_data)
    return {
        "situation": narrative.situation,
        "complication": narrative.complication,
        "question": narrative.question,
        "answer": narrative.answer,
    }
