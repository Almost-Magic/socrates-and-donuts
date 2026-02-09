"""Cash Flow API."""
from fastapi import APIRouter
from models.database import get_connection
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/forecast")
async def cashflow_forecast(weeks: int = 13):
    """13-week cash flow forecast with 3 scenarios."""
    conn = get_connection()
    cash = conn.execute("SELECT COALESCE(SUM(balance),0) FROM bank_accounts").fetchone()[0]
    # Get average weekly income/expense from last 12 weeks
    avg_income = conn.execute(
        "SELECT COALESCE(AVG(weekly), 0) FROM (SELECT SUM(amount) as weekly FROM transactions WHERE type='income' AND date >= date('now','-84 days') GROUP BY strftime('%W', date))"
    ).fetchone()[0]
    avg_expense = conn.execute(
        "SELECT COALESCE(AVG(weekly), 0) FROM (SELECT SUM(ABS(amount)) as weekly FROM transactions WHERE type='expense' AND date >= date('now','-84 days') GROUP BY strftime('%W', date))"
    ).fetchone()[0]
    # Get scheduled bills
    upcoming_bills = conn.execute(
        "SELECT due_date, total-amount_paid as remaining FROM bills WHERE status IN ('pending','approved','scheduled') ORDER BY due_date"
    ).fetchall()

    forecast = []
    balance = cash
    for w in range(weeks):
        week_start = datetime.now() + timedelta(weeks=w)
        # Three scenarios
        optimistic = balance + avg_income * 1.15 - avg_expense * 0.9
        expected = balance + avg_income - avg_expense
        conservative = balance + avg_income * 0.85 - avg_expense * 1.1
        # Deduct scheduled bills this week
        for bill in upcoming_bills:
            try:
                bd = datetime.strptime(bill["due_date"], "%Y-%m-%d")
                if week_start <= bd < week_start + timedelta(weeks=1):
                    expected -= bill["remaining"]
                    optimistic -= bill["remaining"]
                    conservative -= bill["remaining"]
            except: pass
        forecast.append({
            "week": w + 1,
            "date": week_start.strftime("%Y-%m-%d"),
            "optimistic": round(optimistic, 2),
            "expected": round(expected, 2),
            "conservative": round(conservative, 2),
        })
        balance = expected

    # Fragility
    biz = conn.execute("SELECT min_cash_buffer FROM business WHERE id=1").fetchone()
    buffer = biz["min_cash_buffer"] if biz else 5000
    conn.close()
    return {"current_cash": round(cash, 2), "min_buffer": buffer, "avg_weekly_income": round(avg_income, 2), "avg_weekly_expense": round(avg_expense, 2), "forecast": forecast}

@router.get("/safe-to-spend")
async def safe_to_spend():
    conn = get_connection()
    cash = conn.execute("SELECT COALESCE(SUM(balance),0) FROM bank_accounts").fetchone()[0]
    payables = conn.execute("SELECT COALESCE(SUM(total-amount_paid),0) FROM bills WHERE status IN ('pending','approved','scheduled','overdue')").fetchone()[0]
    gst_net = conn.execute("SELECT COALESCE(SUM(CASE WHEN type='income' THEN gst_amount ELSE -gst_amount END),0) FROM transactions WHERE date >= date('now','start of month','-2 months')").fetchone()[0]
    biz = conn.execute("SELECT min_cash_buffer FROM business WHERE id=1").fetchone()
    buffer = biz["min_cash_buffer"] if biz else 5000
    safe = max(0, cash - abs(payables) - abs(gst_net) - buffer)
    conn.close()
    return {"cash": round(cash,2), "payables": round(abs(payables),2), "gst_liability": round(abs(gst_net),2), "buffer": buffer, "safe_to_spend": round(safe,2),
            "breakdown": [{"label":"Cash Position","amount":round(cash,2)}, {"label":"Payables Due","amount":-round(abs(payables),2)}, {"label":"GST Liability","amount":-round(abs(gst_net),2)}, {"label":"Buffer","amount":-buffer}, {"label":"Safe to Spend","amount":round(safe,2)}]}
