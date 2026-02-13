"""Beast Tests — ELAINE Integration Test Suite (10+ tests)

Beast tests verify that ELAINE's modules work together correctly.
They exercise the full Flask app via the test client — no live server needed.

Almost Magic Tech Lab
"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

# client fixture provided by conftest.py (session-scoped)


# ── Beast 1: System Health ────────────────────────────────────────

def test_beast_health_endpoint(client):
    """ELAINE health endpoint returns healthy status."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "ELAINE"


# ── Beast 2: All 16 Modules Active ───────────────────────────────

def test_beast_all_modules_active(client):
    """All 16 intelligence modules are loaded and active."""
    resp = client.get("/api/status")
    assert resp.status_code == 200
    data = resp.get_json()
    modules = data["modules"]
    assert len(modules) >= 16, f"Expected 16+ modules, got {len(modules)}"
    for name, info in modules.items():
        assert info["status"] == "active", f"Module {name} is not active"


# ── Beast 3: Tool Registry ───────────────────────────────────────

def test_beast_tool_registry(client):
    """AMTL tool registry returns all registered services."""
    resp = client.get("/api/tools")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total"] >= 16
    ids = [t["id"] for t in data["tools"]]
    for expected in ["workshop", "supervisor", "elaine", "ollama", "genie", "writer", "costanza", "junk-drawer"]:
        assert expected in ids, f"Missing tool: {expected}"


# ── Beast 4: TTS Fallback Chain ──────────────────────────────────

def test_beast_tts_status(client):
    """TTS status reports the correct fallback chain."""
    resp = client.get("/api/tts/status")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "fallback_chain" in data
    assert data["fallback_chain"] == ["elevenlabs", "kokoro", "browser-tts"]
    assert data["active"] in ["elevenlabs", "kokoro", "browser-tts"]


def test_beast_tts_synthesis(client):
    """TTS endpoint returns audio or browser-tts fallback."""
    resp = client.post("/api/tts",
                       data=json.dumps({"text": "Testing voice output."}),
                       content_type="application/json")
    assert resp.status_code == 200
    ct = resp.content_type
    # Should be audio (kokoro/elevenlabs) or JSON (browser fallback)
    assert "audio/" in ct or "application/json" in ct
    if "application/json" in ct:
        data = resp.get_json()
        assert data.get("fallback") == "browser-tts"


# ── Beast 5: Orchestrator Wiring ─────────────────────────────────

def test_beast_orchestrator_wiring(client):
    """Orchestrator has all module connections wired."""
    resp = client.get("/api/orchestrator/wiring")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "chronicle_to" in data
    assert "gravity" in data["chronicle_to"]
    assert "sentinel_to" in data


def test_beast_orchestrator_status(client):
    """Orchestrator reports connected module count."""
    resp = client.get("/api/orchestrator/status")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["modules_connected"] >= 13


# ── Beast 6: External App Delegation ─────────────────────────────

def test_beast_delegation_apps_endpoint(client):
    """External apps endpoint returns all 6 registered apps."""
    resp = client.get("/api/orchestrator/apps")
    assert resp.status_code == 200
    data = resp.get_json()
    for app_id in ["writer", "learning", "peterman", "costanza", "genie", "junk-drawer"]:
        assert app_id in data, f"Missing app: {app_id}"
        assert "port" in data[app_id]
        assert "name" in data[app_id]


def test_beast_delegation_unknown_app(client):
    """Delegation to unknown app returns 400 with known apps list."""
    resp = client.post("/api/orchestrator/delegate",
                       data=json.dumps({"app": "nonexistent", "task_type": "test"}),
                       content_type="application/json")
    assert resp.status_code == 400
    data = resp.get_json()
    assert "known_apps" in data


# ── Beast 7: Wisdom Knowledge Base ───────────────────────────────

def test_beast_wisdom_daily(client):
    """Wisdom daily quote returns a quote with author."""
    resp = client.get("/api/wisdom")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "text" in data
    assert "author" in data


def test_beast_wisdom_categories(client):
    """Wisdom KB has all 4 categories with sufficient quotes."""
    resp = client.get("/api/wisdom/stats")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total_quotes"] >= 80
    cats = data["categories"]
    assert cats.get("sitcom", 0) >= 25
    assert cats.get("one-liner", 0) >= 15
    assert cats.get("idiom", 0) >= 15
    assert cats.get("philosophy", 0) >= 10


def test_beast_wisdom_search(client):
    """Wisdom search finds quotes by keyword."""
    resp = client.get("/api/wisdom/search?q=Ron+Swanson")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data["results"]) >= 3
    for r in data["results"]:
        assert "Ron Swanson" in r["author"]


def test_beast_wisdom_sitcom_filter(client):
    """Sitcom quotes endpoint filters by source."""
    resp = client.get("/api/wisdom/sitcom?source=Seinfeld")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["count"] >= 8
    for q in data["quotes"]:
        assert q["source"] == "Seinfeld"


# ── Beast 8: Morning Briefing ────────────────────────────────────

def test_beast_morning_briefing_generate(client):
    """Morning briefing generates without errors."""
    resp = client.post("/api/morning-briefing/generate")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "briefing" in data
    assert "generated_at" in data
    assert len(data["briefing"]) > 100


# ── Beast 9: Gravity Field ───────────────────────────────────────

def test_beast_gravity_top(client):
    """Gravity top items endpoint returns structured data."""
    resp = client.get("/api/gravity/top?limit=5")
    assert resp.status_code == 200
    data = resp.get_json()
    # Endpoint returns {"items": [...]} or a list directly
    assert isinstance(data, (dict, list))


# ── Beast 10: Gatekeeper Check ───────────────────────────────────

def test_beast_gatekeeper_check(client):
    """Gatekeeper checks content and returns verdict."""
    resp = client.post("/api/gatekeeper/check",
                       data=json.dumps({"content": "This is a test email about AI governance.", "title": "Test"}),
                       content_type="application/json")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "verdict" in data
    assert data["verdict"] in ["clear", "review", "hold"]


# ── Beast 11: Chat Endpoint Structure ────────────────────────────

def test_beast_chat_requires_message(client):
    """Chat endpoint rejects empty messages."""
    resp = client.post("/api/chat",
                       data=json.dumps({"message": ""}),
                       content_type="application/json")
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data


# ── Beast 12: Compassion Wellbeing ───────────────────────────────

def test_beast_compassion_wellbeing(client):
    """Compassion engine returns wellbeing status."""
    resp = client.get("/api/compassion/wellbeing")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "wellbeing_level" in data
    assert data["wellbeing_level"] in ["thriving", "steady", "stretched", "strained", "depleted"]
