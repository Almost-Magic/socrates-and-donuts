"""
Costanza Flask API — Beast Tests
Run: python -m pytest tests/ -v  OR  python tests/test_beast.py
"""

import sys
import os
import json

# Add parent to path so we can import app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "AMTL Thinking", "costanza", "src"))

PASS = "\u2705"
FAIL = "\u274c"
results = {"passed": 0, "failed": 0}


def test(name, fn):
    try:
        fn()
        results["passed"] += 1
        _safe_print(f"  {PASS} {name}")
    except Exception as e:
        results["failed"] += 1
        _safe_print(f"  {FAIL} {name}: {e}")


def _safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode("ascii", "replace").decode("ascii"))


# ---------------------------------------------------------------------------
# Flask test client
# ---------------------------------------------------------------------------

from app import app as flask_app

client = flask_app.test_client()


# ---------------------------------------------------------------------------
# Health endpoint tests
# ---------------------------------------------------------------------------

def test_health_returns_200():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "costanza"

def test_health_has_engines():
    resp = client.get("/api/health")
    data = resp.get_json()
    assert "engines" in data
    assert "thinking" in data["engines"]
    assert "communication" in data["engines"]
    assert "strategic" in data["engines"]

def test_health_has_llm_status():
    resp = client.get("/api/health")
    data = resp.get_json()
    assert "llm" in data
    assert "model" in data["llm"]
    assert "supervisor" in data["llm"]

def test_health_has_framework_count():
    resp = client.get("/api/health")
    data = resp.get_json()
    assert data["total_frameworks"] == 22


# ---------------------------------------------------------------------------
# Root endpoint tests
# ---------------------------------------------------------------------------

def test_root_returns_200():
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["app"] == "Costanza"

def test_root_has_correct_version():
    resp = client.get("/")
    data = resp.get_json()
    assert data["version"] == "2.1.0"

def test_root_lists_endpoints():
    resp = client.get("/")
    data = resp.get_json()
    assert "/api/health" in data["endpoints"]
    assert "/api/models" in data["endpoints"]
    assert "/api/analyze" in data["endpoints"]

def test_root_lists_engines():
    resp = client.get("/")
    data = resp.get_json()
    assert "decision_intelligence" in data["engines"]
    assert "communication" in data["engines"]
    assert "strategic" in data["engines"]


# ---------------------------------------------------------------------------
# Models endpoint tests
# ---------------------------------------------------------------------------

def test_models_returns_200():
    resp = client.get("/api/models")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total"] == 22

def test_models_has_three_categories():
    resp = client.get("/api/models")
    data = resp.get_json()
    cats = set(data["categories"])
    assert "decision_intelligence" in cats
    assert "communication" in cats
    assert "strategic" in cats

def test_models_search_filters():
    resp = client.get("/api/models?search=swot")
    data = resp.get_json()
    assert data["total"] >= 1
    assert any("swot" in m["id"].lower() for m in data["models"])

def test_models_category_filters():
    resp = client.get("/api/models?category=strategic")
    data = resp.get_json()
    assert data["total"] == 8
    assert all(m["category"] == "strategic" for m in data["models"])

def test_models_search_no_match():
    resp = client.get("/api/models?search=nonexistent_xyz")
    data = resp.get_json()
    assert data["total"] == 0

def test_models_category_decision():
    resp = client.get("/api/models?category=decision_intelligence")
    data = resp.get_json()
    assert data["total"] == 6

def test_models_category_communication():
    resp = client.get("/api/models?category=communication")
    data = resp.get_json()
    assert data["total"] == 8


# ---------------------------------------------------------------------------
# Analyze endpoint tests
# ---------------------------------------------------------------------------

def test_analyze_returns_200():
    resp = client.post("/api/analyze",
        data=json.dumps({"situation": "Should we expand into a new market?"}),
        content_type="application/json")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["situation"] == "Should we expand into a new market?"
    assert "frameworks_applied" in data
    assert "synthesis" in data

def test_analyze_no_situation_returns_400():
    resp = client.post("/api/analyze",
        data=json.dumps({}),
        content_type="application/json")
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data

def test_analyze_empty_situation_returns_400():
    resp = client.post("/api/analyze",
        data=json.dumps({"situation": "   "}),
        content_type="application/json")
    assert resp.status_code == 400

def test_analyze_respects_domain():
    resp = client.post("/api/analyze",
        data=json.dumps({"situation": "Which tech stack?", "domain": "technology"}),
        content_type="application/json")
    data = resp.get_json()
    assert data["domain"] == "technology"

def test_analyze_respects_stakes():
    resp = client.post("/api/analyze",
        data=json.dumps({"situation": "Mission critical decision", "stakes": "critical"}),
        content_type="application/json")
    data = resp.get_json()
    assert data["stakes"] == "critical"

def test_analyze_high_stakes_multiple_frameworks():
    resp = client.post("/api/analyze",
        data=json.dumps({
            "situation": "Major acquisition decision",
            "domain": "strategy",
            "stakes": "high",
        }),
        content_type="application/json")
    data = resp.get_json()
    assert len(data["frameworks_applied"]) >= 2

def test_analyze_has_ai_fields():
    """Verify AI synthesis fields exist (may be empty if LLM unavailable)."""
    resp = client.post("/api/analyze",
        data=json.dumps({"situation": "Test scenario"}),
        content_type="application/json")
    data = resp.get_json()
    assert "ai_synthesis" in data
    assert "ai_enhanced" in data

def test_analyze_has_confidence():
    resp = client.post("/api/analyze",
        data=json.dumps({"situation": "Test scenario", "stakes": "high"}),
        content_type="application/json")
    data = resp.get_json()
    assert "confidence" in data
    assert isinstance(data["confidence"], (int, float))

def test_analyze_has_recommended_action():
    resp = client.post("/api/analyze",
        data=json.dumps({"situation": "Should we invest?", "stakes": "high"}),
        content_type="application/json")
    data = resp.get_json()
    assert "recommended_action" in data

def test_analyze_default_domain_and_stakes():
    resp = client.post("/api/analyze",
        data=json.dumps({"situation": "A generic situation"}),
        content_type="application/json")
    data = resp.get_json()
    assert data["domain"] == "strategy"
    assert data["stakes"] == "medium"


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys as _sys
    try:
        _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    ALL_TESTS = [
        # Health
        ("GET /api/health returns 200", test_health_returns_200),
        ("GET /api/health has engines", test_health_has_engines),
        ("GET /api/health has LLM status", test_health_has_llm_status),
        ("GET /api/health has framework count (22)", test_health_has_framework_count),
        # Root
        ("GET / returns 200", test_root_returns_200),
        ("GET / has correct version", test_root_has_correct_version),
        ("GET / lists endpoints", test_root_lists_endpoints),
        ("GET / lists engines", test_root_lists_engines),
        # Models
        ("GET /api/models returns 22 frameworks", test_models_returns_200),
        ("GET /api/models has 3 categories", test_models_has_three_categories),
        ("GET /api/models?search=swot filters", test_models_search_filters),
        ("GET /api/models?category=strategic returns 8", test_models_category_filters),
        ("GET /api/models?search=xyz returns 0", test_models_search_no_match),
        ("GET /api/models?category=decision returns 6", test_models_category_decision),
        ("GET /api/models?category=communication returns 8", test_models_category_communication),
        # Analyze
        ("POST /api/analyze returns 200", test_analyze_returns_200),
        ("POST /api/analyze no situation returns 400", test_analyze_no_situation_returns_400),
        ("POST /api/analyze empty situation returns 400", test_analyze_empty_situation_returns_400),
        ("POST /api/analyze respects domain", test_analyze_respects_domain),
        ("POST /api/analyze respects stakes", test_analyze_respects_stakes),
        ("POST /api/analyze high stakes = multiple frameworks", test_analyze_high_stakes_multiple_frameworks),
        ("POST /api/analyze has AI synthesis fields", test_analyze_has_ai_fields),
        ("POST /api/analyze has confidence", test_analyze_has_confidence),
        ("POST /api/analyze has recommended_action", test_analyze_has_recommended_action),
        ("POST /api/analyze default domain/stakes", test_analyze_default_domain_and_stakes),
    ]

    print(f"\n{'='*60}")
    print(f"  COSTANZA BEAST TESTS — {len(ALL_TESTS)} tests")
    print(f"{'='*60}\n")

    for name, fn in ALL_TESTS:
        test(name, fn)

    total = results["passed"] + results["failed"]
    print(f"\n{'='*60}")
    print(f"  Results: {results['passed']}/{total} passed")
    if results["failed"] == 0:
        _safe_print(f"  {PASS} ALL TESTS PASSED")
    else:
        _safe_print(f"  {FAIL} {results['failed']} FAILED")
    print(f"{'='*60}\n")

    _sys.exit(0 if results["failed"] == 0 else 1)
