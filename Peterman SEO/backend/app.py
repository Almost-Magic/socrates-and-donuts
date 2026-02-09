"""
Genie v2.1 — The AI Bookkeeper
Almost Magic Finance Suite — Agent 01

Backend API server (FastAPI + SQLite + SQLCipher)
"""

import os
import sys
import uvicorn
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from routes.transactions import router as transactions_router
from routes.invoices import router as invoices_router
from routes.contacts import router as contacts_router
from routes.reconciliation import router as reconciliation_router
from routes.dashboard import router as dashboard_router
from routes.import_export import router as import_router
from routes.settings import router as settings_router
from routes.genie_ai import router as genie_ai_router
from routes.fraud_guard import router as fraud_router
from routes.cashflow import router as cashflow_router
from routes.gst import router as gst_router
from routes.bills import router as bills_router
from routes.reports import router as reports_router
from models.database import init_db, get_db_path

# ── App Setup ──────────────────────────────────────────────
app = FastAPI(
    title="Genie — The AI Bookkeeper",
    description="Almost Magic Finance Suite Agent 01. Local-first AI bookkeeping.",
    version="2.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "file://"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount Routes ───────────────────────────────────────────
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(transactions_router, prefix="/api/transactions", tags=["Transactions"])
app.include_router(invoices_router, prefix="/api/invoices", tags=["Invoices"])
app.include_router(bills_router, prefix="/api/bills", tags=["Bills"])
app.include_router(contacts_router, prefix="/api/contacts", tags=["Contacts"])
app.include_router(reconciliation_router, prefix="/api/reconciliation", tags=["Reconciliation"])
app.include_router(import_router, prefix="/api/import", tags=["Import/Export"])
app.include_router(settings_router, prefix="/api/settings", tags=["Settings"])
app.include_router(genie_ai_router, prefix="/api/genie", tags=["Ask Genie"])
app.include_router(fraud_router, prefix="/api/fraud", tags=["Fraud Guard"])
app.include_router(cashflow_router, prefix="/api/cashflow", tags=["Cash Flow"])
app.include_router(gst_router, prefix="/api/gst", tags=["GST"])
app.include_router(reports_router, prefix="/api/reports", tags=["Reports (Costanza-Powered)"])


# ── Health Check ───────────────────────────────────────────
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "agent": "Genie",
        "version": "2.1.0",
        "suite": "Almost Magic Finance Suite",
        "database": str(get_db_path()),
        "ai_engine": "local",
    }


@app.get("/api/status")
async def status():
    """Full status including AI availability."""
    ai_available = False
    try:
        import httpx
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get("http://localhost:11434/api/tags")
            ai_available = resp.status_code == 200
    except Exception:
        pass

    return {
        "status": "operational",
        "ai_available": ai_available,
        "database": "connected",
        "version": "2.1.0",
    }


# ── Startup ────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    """Initialise database on startup."""
    init_db()
    print("🧞 Genie v2.1 — The AI Bookkeeper")
    print(f"   Database: {get_db_path()}")
    print(f"   API docs: http://localhost:8000/api/docs")


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
