"""
Beast Test Harness -- Signal Hunter
Almost Magic Tech Lab

5-section Beast pattern:
  1. Imports & config
  2. Unit tests (DB, helpers)
  3. Integration tests (profile + engagement CRUD)
  4. API smoke tests (health, dashboard, analysis)
  5. Confidence stamp
"""

import json
import os
import sys
import tempfile
import time
import urllib.request
import urllib.error

# ── Section 1: Imports & Config ──────────────────────────────────────

passed = 0
failed = 0
total = 0

BASE_URL = os.environ.get("SIGNAL_TEST_URL", "http://localhost:8420")


def test(name, condition, detail=""):
    global passed, failed, total
    total += 1
    if condition:
        passed += 1
        print(f"  PASS  {name}")
    else:
        failed += 1
        print(f"  FAIL  {name}  {detail}")


def api(path, method="GET", body=None, expect=200, timeout=30):
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode("utf-8") if body else None
    headers = {"Content-Type": "application/json"} if body else {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return resp.status, result
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        try:
            result = json.loads(body_text)
        except Exception:
            result = {"raw": body_text}
        return e.code, result
    except Exception as e:
        return 0, {"error": str(e)}


# Unique run ID to avoid test data collisions
import uuid
RUN_ID = uuid.uuid4().hex[:8]


# ── Section 2: Unit Tests (imports & structure) ──────────────────────

print()
print("=" * 60)
print("  Beast Tests -- Signal Hunter")
print("=" * 60)
print()
print("  Section 2: Unit Tests")
print()

# Test: app.py is importable
test_dir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, test_dir)

try:
    import app as signal_app
    test("import app", True)
except Exception as e:
    test("import app", False, str(e))
    print("\n  FATAL: Cannot import app.py -- aborting\n")
    sys.exit(1)

# Test: Flask app exists
test("Flask app object exists", hasattr(signal_app, "app"))

# Test: key routes registered
rules = [r.rule for r in signal_app.app.url_map.iter_rules()]
test("/api/health route exists", "/api/health" in rules)
test("/ route exists", "/" in rules)
test("/api/profiles route exists", "/api/profiles" in rules)
test("/api/dashboard route exists", "/api/dashboard" in rules)

# Test: config constants
test("PORT is 8420", signal_app.PORT == 8420)
test("SUPERVISOR_URL set", "localhost:9000" in signal_app.SUPERVISOR_URL)
test("OLLAMA_URL set", "localhost:11434" in signal_app.OLLAMA_URL)
test("SIGNAL_MODEL set", bool(signal_app.SIGNAL_MODEL))

# Test: DB init function
test("_init_db callable", callable(signal_app._init_db))
test("_db callable", callable(signal_app._db))

# Test: LLM helper
test("_call_llm callable", callable(signal_app._call_llm))
test("_build_analysis_prompt callable", callable(signal_app._build_analysis_prompt))


# ── Section 3: Integration Tests (API CRUD) ──────────────────────────

print()
print("  Section 3: Integration Tests (API)")
print()

# Health check -- make sure server is running
status, data = api("/api/health")
test("GET /api/health returns 200", status == 200)
test("health status is healthy", data.get("status") == "healthy")
test("health has service=signal", data.get("service") == "signal")
test("health has llm block", "llm" in data)
test("health has profiles count", "profiles" in data)

# Root (web UI)
try:
    req = urllib.request.Request(f"{BASE_URL}/", method="GET")
    with urllib.request.urlopen(req, timeout=5) as resp:
        html = resp.read().decode("utf-8")
        test("GET / returns HTML", "Signal" in html and "<html" in html.lower())
except Exception as e:
    test("GET / returns HTML", False, str(e))

# Create profile
profile_name = f"Beast Test {RUN_ID}"
status, data = api("/api/profiles", "POST", {
    "name": profile_name,
    "headline": "Test headline",
    "company": "AMTL Test Corp",
    "linkedin_url": "https://linkedin.com/in/beasttest",
    "tags": "test, beast",
    "notes": "Created by Beast test harness",
})
test("POST /api/profiles returns 201", status == 201)
test("profile has id", "id" in data)
test("profile name matches", data.get("name") == profile_name)
profile_id = data.get("id")

# Create profile missing name -> 400
status, data = api("/api/profiles", "POST", {"company": "No Name Corp"})
test("POST /api/profiles no name returns 400", status == 400)

# List profiles
status, data = api("/api/profiles")
test("GET /api/profiles returns 200", status == 200)
test("profiles list has items", data.get("total", 0) > 0)

# Search profiles
status, data = api(f"/api/profiles?search={RUN_ID}")
test("search profiles finds test profile", data.get("total", 0) >= 1)

# Get single profile
status, data = api(f"/api/profiles/{profile_id}")
test("GET /api/profiles/:id returns 200", status == 200)
test("profile detail has engagement_count", "engagement_count" in data)

# Update profile
status, data = api(f"/api/profiles/{profile_id}", "PUT", {
    "headline": "Updated Headline",
    "tags": "test, beast, updated",
})
test("PUT /api/profiles/:id returns 200", status == 200)
test("profile headline updated", data.get("headline") == "Updated Headline")

# Get 404 for non-existent profile
status, data = api("/api/profiles/999999")
test("GET non-existent profile returns 404", status == 404)


# ── Section 3b: Engagements ──────────────────────────────────────────

print()
print("  Section 3b: Engagement Tests")
print()

# Create engagement
status, data = api(f"/api/profiles/{profile_id}/engagements", "POST", {
    "engagement_type": "post",
    "post_content": "Wrote about AI governance today",
    "reactions": 42,
    "comments": 7,
    "shares": 3,
    "post_date": "2026-02-13",
    "notes": "Beast test engagement",
})
test("POST engagement returns 201", status == 201)
test("engagement has id", "id" in data)
eng_id = data.get("id")

# List engagements
status, data = api(f"/api/profiles/{profile_id}/engagements")
test("GET engagements returns 200", status == 200)
test("engagements list has items", data.get("total", 0) >= 1)

# Engagement for non-existent profile
status, data = api("/api/profiles/999999/engagements")
test("engagements for missing profile returns 404", status == 404)

# Delete engagement
status, data = api(f"/api/engagements/{eng_id}", "DELETE")
test("DELETE engagement returns 200", status == 200)

# Delete non-existent engagement
status, data = api("/api/engagements/999999", "DELETE")
test("DELETE missing engagement returns 404", status == 404)


# ── Section 4: API Smoke Tests ───────────────────────────────────────

print()
print("  Section 4: Smoke Tests (analysis, dashboard)")
print()

# Analysis (may return offline fallback if Ollama is down -- that's OK)
status, data = api(f"/api/profiles/{profile_id}/analyze", "POST", timeout=45)
test("POST analyze returns 200", status == 200)
test("analyze has analysis text", bool(data.get("analysis")))
test("analyze has model field", "model" in data)
test("analyze has via field", "via" in data)

# Analyses list
status, data = api(f"/api/profiles/{profile_id}/analyses")
test("GET analyses returns 200", status == 200)
test("analyses list populated after analyze", data.get("total", 0) >= 1)

# Dashboard
status, data = api("/api/dashboard")
test("GET /api/dashboard returns 200", status == 200)
test("dashboard has total_profiles", "total_profiles" in data)
test("dashboard has total_engagements", "total_engagements" in data)
test("dashboard has total_analyses", "total_analyses" in data)
test("dashboard has recent_analyses", "recent_analyses" in data)
test("dashboard has top_engaged", "top_engaged" in data)

# Cleanup: delete test profile
status, data = api(f"/api/profiles/{profile_id}", "DELETE")
test("cleanup: delete test profile", status == 200)


# ── Section 5: Confidence Stamp ──────────────────────────────────────

print()
print("=" * 60)
pct = round(100 * passed / total) if total else 0
stamp = f"  Signal Hunter Beast: {passed}/{total} ({pct}%)"
if failed == 0:
    print(f"{stamp} -- ALL PASSING")
else:
    print(f"{stamp} -- {failed} FAILING")
print("=" * 60)
print()

sys.exit(0 if failed == 0 else 1)
