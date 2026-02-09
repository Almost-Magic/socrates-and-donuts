"""
Proof — Real Human User Tests
Tests Genie as a real user would.
Run: python proof_tests.py (with backend running on port 8000)
"""
import sys, json, requests
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_URL = "http://localhost:8000"
RESULTS = {"passed": 0, "failed": 0, "tests": []}

def log_test(name, status, detail=""):
    icon = "+" if status == "pass" else "X"
    RESULTS["tests"].append({"name": name, "status": status, "detail": detail})
    RESULTS["passed" if status == "pass" else "failed"] += 1
    print(f"  [{icon}] {name}" + (f" -- {detail}" if detail else ""))

def check_server():
    try: return requests.get(f"{BACKEND_URL}/api/health", timeout=3).status_code == 200
    except: return False

def test(name, method, url, json_data=None, check_keys=None, check_status=200):
    try:
        r = getattr(requests, method)(f"{BACKEND_URL}{url}", json=json_data, timeout=5)
        ok = r.status_code == check_status
        if ok and check_keys:
            data = r.json()
            ok = all(k in data for k in check_keys)
        log_test(name, "pass" if ok else "fail", f"Status={r.status_code}")
        return r.json() if ok else None
    except Exception as e:
        log_test(name, "fail", str(e))
        return None

def run_all():
    print("=" * 60)
    print("  PROOF -- Real User Tests -- Genie v2.1")
    print(f"  {datetime.now().strftime('%d %b %Y %H:%M:%S')}")
    print("=" * 60)
    if not check_server():
        print("\n  Backend not running! Start: cd backend && python app.py")
        return False
    test("P01 Health check", "get", "/api/health", check_keys=["status", "version"])
    test("P02 Dashboard", "get", "/api/dashboard/", check_keys=["cash_position", "fragility_score", "today_priority"])
    test("P03 Create client", "post", "/api/contacts/", json_data={"type":"client","name":"Test Corp","abn":"12345678901","email":"t@t.com","payment_terms":30}, check_keys=["id"])
    test("P04 Create vendor", "post", "/api/contacts/", json_data={"type":"vendor","name":"Telstra","abn":"33051775556"}, check_keys=["id"])
    test("P05 List contacts", "get", "/api/contacts/", check_keys=["contacts"])
    test("P06 Create transaction", "post", "/api/transactions/", json_data={"date":"2026-02-08","description":"OFFICEWORKS","amount":-247.50,"type":"expense","gst_treatment":"10"}, check_keys=["id"])
    test("P07 List transactions", "get", "/api/transactions/", check_keys=["transactions", "total"])
    test("P08 Transaction stats", "get", "/api/transactions/stats", check_keys=["total", "accuracy", "time_saved_hours", "money_saved"])
    test("P09 Create invoice", "post", "/api/invoices/", json_data={"contact_id":1,"issue_date":"2026-02-08","payment_terms":30,"lines":[{"description":"Consulting","quantity":8,"unit_price":300}]}, check_keys=["invoice_number"])
    test("P10 List invoices", "get", "/api/invoices/", check_keys=["invoices", "total"])
    test("P11 Create bill", "post", "/api/bills/", json_data={"vendor_id":2,"bill_number":"B-001","issue_date":"2026-02-01","due_date":"2026-03-01","lines":[{"description":"Hosting","quantity":1,"unit_price":99}]}, check_keys=["id"])
    test("P12 Ask Genie", "post", "/api/genie/ask", json_data={"question":"How much have I spent?"}, check_keys=["answer"])
    test("P13 Cash flow forecast", "get", "/api/cashflow/forecast", check_keys=["forecast", "current_cash"])
    test("P14 Safe-to-spend", "get", "/api/cashflow/safe-to-spend", check_keys=["safe_to_spend", "breakdown"])
    test("P15 GST position", "get", "/api/gst/position", check_keys=["collected_1a", "paid_1b", "net"])
    test("P16 Fraud score", "get", "/api/fraud/score", check_keys=["score"])
    test("P17 Fraud signals", "get", "/api/fraud/signals", check_keys=["signals"])
    test("P18 Read settings", "get", "/api/settings/", check_keys=["name"])
    test("P19 Update settings", "put", "/api/settings/", json_data={"name":"Test Biz","abn":"12345678901"}, check_keys=["message"])
    test("P20 Categories", "get", "/api/settings/categories", check_keys=["categories"])
    test("P21 Reconciliation score", "get", "/api/reconciliation/score", check_keys=["percentage"])
    test("P22 Unmatched", "get", "/api/reconciliation/unmatched", check_keys=["unmatched"])
    test("P23 Import history", "get", "/api/import/history", check_keys=["imports"])
    test("P24 Bank changes", "get", "/api/fraud/bank-changes", check_keys=["changes"])
    test("P25 GST by category", "get", "/api/gst/by-category", check_keys=["categories"])

    # Costanza-powered reports
    test("P26 Monthly summary (Costanza Pyramid+SCQA)", "get", "/api/reports/monthly-summary", check_keys=["pyramid", "scqa", "abt", "key_three"])
    test("P27 Presentation structure (10-20-30)", "get", "/api/reports/monthly-summary/presentation", check_keys=["slides", "rule_check"])
    test("P28 Risk analysis (Pre-Mortem)", "get", "/api/reports/risk-analysis", check_keys=["risks", "overall_risk", "george_would_say", "costanza_says"])
    test("P29 Cash flow narrative (SCQA)", "get", "/api/reports/cashflow-narrative", check_keys=["situation", "complication", "question", "answer"])

    total = RESULTS["passed"] + RESULTS["failed"]
    print(f"\n{'='*60}")
    pct = round(RESULTS["passed"] / max(total, 1) * 100, 1)
    print(f"  PROOF: {RESULTS['passed']}/{total} passed | {RESULTS['failed']} failed | {pct}%")
    print(f"  STATUS: {'ALL CLEAR' if RESULTS['failed']==0 else 'ISSUES FOUND'}")
    print("="*60)
    rd = PROJECT_ROOT / "tests" / "reports"; rd.mkdir(parents=True, exist_ok=True)
    rp = rd / f"proof_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(rp, "w") as f: json.dump({"timestamp": datetime.now().isoformat(), "results": RESULTS, "score": pct}, f, indent=2)
    print(f"  Report: {rp}")
    return RESULTS["failed"] == 0

if __name__ == "__main__":
    sys.exit(0 if run_all() else 1)
