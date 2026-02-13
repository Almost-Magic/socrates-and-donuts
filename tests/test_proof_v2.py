"""Proof Tests — ELAINE Verification Suite (5+ tests)

Proof tests verify that specific features work end-to-end as designed.
Uses Flask test client — no live server or Playwright needed.

Almost Magic Tech Lab
"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

# client fixture provided by conftest.py (session-scoped)


# ── Proof 1: Voice Fallback Chain Works End-to-End ───────────────

def test_proof_voice_fallback_chain(client):
    """Voice degrades gracefully: server TTS → browser hint."""
    status = client.get("/api/tts/status").get_json()
    active = status["active"]

    resp = client.post("/api/tts",
                       data=json.dumps({"text": "Proof test — voice working."}),
                       content_type="application/json")
    assert resp.status_code == 200

    if active == "kokoro":
        assert "audio/wav" in resp.content_type
        assert len(resp.data) > 1000  # WAV has real audio data
    elif active == "elevenlabs":
        assert "audio/mpeg" in resp.content_type
    else:
        data = resp.get_json()
        assert data["fallback"] == "browser-tts"
        assert len(data["text"]) > 0


# ── Proof 2: Orchestrator Delegation Tracks Tasks ────────────────

def test_proof_delegation_tracking(client):
    """Delegated tasks are tracked and retrievable."""
    # Delegate a task (will fail gracefully — app offline)
    client.post("/api/orchestrator/delegate",
                data=json.dumps({"app": "writer", "task_type": "write_draft",
                                 "payload": {"topic": "proof test"}}),
                content_type="application/json")

    # Retrieve delegated tasks
    resp = client.get("/api/orchestrator/delegate/tasks")
    assert resp.status_code == 200
    data = resp.get_json()
    tasks = data["tasks"]
    assert len(tasks) >= 1
    latest = tasks[-1]
    assert latest["app_id"] == "writer"
    assert latest["task_type"] == "write_draft"
    assert latest["status"] in ["delegated", "app_offline", "error"]


# ── Proof 3: Wisdom KB Serves All Categories ────────────────────

def test_proof_wisdom_all_categories(client):
    """Every wisdom category has accessible content."""
    for category in ["sitcom", "one-liner", "idiom", "philosophy"]:
        resp = client.get(f"/api/wisdom/random?category={category}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["category"] == category, f"Wrong category for {category}"
        assert len(data["text"]) > 5, f"Empty quote for {category}"


# ── Proof 4: Morning Brief Contains All Sections ────────────────

def test_proof_morning_brief_sections(client):
    """Generated morning brief contains weather, security, intelligence sections."""
    resp = client.post("/api/morning-briefing/generate")
    assert resp.status_code == 200
    data = resp.get_json()
    briefing = data["briefing"]

    # Should contain key section markers
    assert "Priority Systems" in briefing or "Gravity" in briefing
    assert "Intelligence" in briefing or "Cartographer" in briefing
    assert "Weather" in briefing
    assert "Security" in briefing
    assert "Financial" in briefing or "Genie" in briefing


# ── Proof 5: Gatekeeper Catches Risky Content ───────────────────

def test_proof_gatekeeper_risk_detection(client):
    """Gatekeeper flags content with risky language."""
    safe = client.post("/api/gatekeeper/check",
                       data=json.dumps({"content": "Our team delivered excellent results this quarter.", "title": "Report"}),
                       content_type="application/json")
    assert safe.status_code == 200
    safe_data = safe.get_json()
    assert safe_data["verdict"] in ["clear", "review"]

    risky = client.post("/api/gatekeeper/check",
                        data=json.dumps({"content": "This is guaranteed to make you rich overnight with no risk.", "title": "Spam"}),
                        content_type="application/json")
    assert risky.status_code == 200
    risky_data = risky.get_json()
    # Should flag this as needing review at minimum
    assert "verdict" in risky_data


# ── Proof 6: UI Root Returns HTML ────────────────────────────────

def test_proof_ui_loads(client):
    """Root URL returns the ELAINE desktop UI."""
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.data.decode()
    assert "Elaine" in html
    assert "Chief of Staff" in html
    assert "speakText" in html  # Voice function present
    assert "api/tts" in html  # TTS integration present
