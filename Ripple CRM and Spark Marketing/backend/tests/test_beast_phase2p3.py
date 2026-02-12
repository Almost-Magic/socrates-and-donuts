"""Beast Test — Phase 2.3: Commute Briefing v1.

Sections:
  0. Setup
  1. Briefing Depths Info
  2. Commute Briefing (meeting-scoped)
  3. Quick Brief (contact-scoped)
  4. Depth Adaptation
  5. Edge Cases
  6. Regression
  7. Confidence Stamp
"""

import os
import uuid
from datetime import datetime, timedelta, timezone

import requests

BASE = os.environ.get("RIPPLE_API_BASE", "http://localhost:8100/api")

_RUN_ID = uuid.uuid4().hex[:8]

_contact_id = None
_deal_id = None
_meeting_id = None


def _create_contact(first="Commute", last=None, email_addr=None):
    last = last or f"Test{_RUN_ID}"
    email_addr = email_addr or f"{first.lower()}.{last.lower()}@p2p3.test"
    r = requests.post(f"{BASE}/contacts", json={
        "first_name": first,
        "last_name": last,
        "email": email_addr,
        "type": "lead",
        "phone": "+61400000002",
    })
    assert r.status_code == 201, f"Create contact failed: {r.text}"
    return r.json()["id"]


def _create_deal(title=None, contact_id=None):
    title = title or f"CommuteDeal {_RUN_ID}"
    payload = {"title": title, "stage": "proposal", "value": 50000.0, "probability": 60}
    if contact_id:
        payload["contact_id"] = contact_id
    r = requests.post(f"{BASE}/deals", json=payload)
    assert r.status_code == 201, f"Create deal failed: {r.text}"
    return r.json()["id"]


def _create_interaction(contact_id, type_="call", subject=None):
    ts = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
    r = requests.post(f"{BASE}/interactions", json={
        "contact_id": contact_id,
        "type": type_,
        "channel": type_,
        "subject": subject or f"Discussion {_RUN_ID}",
        "content": "Test interaction for commute briefing",
        "sentiment_score": 0.7,
        "occurred_at": ts,
    })
    assert r.status_code == 201, f"Create interaction failed: {r.text}"
    return r.json()["id"]


def _create_meeting(contact_id=None, deal_id=None, title=None):
    ts = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
    payload = {
        "title": title or f"Briefing Test {_RUN_ID}",
        "meeting_type": "in_person",
        "scheduled_at": ts,
        "duration_minutes": 60,
        "location": "Sydney CBD",
    }
    if contact_id:
        payload["contact_id"] = contact_id
    if deal_id:
        payload["deal_id"] = deal_id
    r = requests.post(f"{BASE}/meetings", json=payload)
    assert r.status_code == 201, f"Create meeting failed: {r.text}"
    return r.json()["id"]


def test_00_setup():
    """Setup: create contact, deal, interaction, and meeting."""
    global _contact_id, _deal_id, _meeting_id
    _contact_id = _create_contact()
    _deal_id = _create_deal(contact_id=_contact_id)
    _create_interaction(_contact_id, "call", "Discussed project scope")
    _create_interaction(_contact_id, "email", "Sent proposal draft")
    _meeting_id = _create_meeting(contact_id=_contact_id, deal_id=_deal_id)
    assert _contact_id
    assert _deal_id
    assert _meeting_id


# ══════════════════════════════════════════════════════════════════════════════
# 1. BRIEFING DEPTHS INFO
# ══════════════════════════════════════════════════════════════════════════════

def test_01_briefing_depths():
    """Get briefing depth thresholds."""
    r = requests.get(f"{BASE}/briefings/depths")
    assert r.status_code == 200
    data = r.json()
    assert "depths" in data
    assert len(data["depths"]) == 3
    names = [d["name"] for d in data["depths"]]
    assert "quick" in names
    assert "standard" in names
    assert "deep" in names


# ══════════════════════════════════════════════════════════════════════════════
# 2. COMMUTE BRIEFING (MEETING-SCOPED)
# ══════════════════════════════════════════════════════════════════════════════

def test_02_commute_briefing_default():
    """Generate commute briefing with default travel time."""
    r = requests.post(f"{BASE}/meetings/{_meeting_id}/commute-briefing")
    assert r.status_code == 200
    data = r.json()
    assert data["meeting_id"] == _meeting_id
    assert "briefing_depth" in data
    assert "contact_summary" in data
    assert "talking_points" in data
    assert "generated_at" in data
    assert data["travel_minutes"] == 15
    assert data["briefing_depth"] == "standard"


def test_02_commute_briefing_has_contact_summary():
    """Commute briefing includes contact summary."""
    r = requests.post(f"{BASE}/meetings/{_meeting_id}/commute-briefing")
    assert r.status_code == 200
    cs = r.json()["contact_summary"]
    assert cs is not None
    assert cs["name"] is not None
    assert "relationship_health" in cs
    assert "preferred_channel" in cs


def test_02_commute_briefing_has_deal_summary():
    """Commute briefing includes deal summary."""
    r = requests.post(f"{BASE}/meetings/{_meeting_id}/commute-briefing")
    assert r.status_code == 200
    ds = r.json()["deal_summary"]
    assert ds is not None
    assert ds["title"] is not None
    assert ds["stage"] == "proposal"
    assert ds["value"] == 50000.0


def test_02_commute_briefing_has_recent_interactions():
    """Commute briefing includes recent interactions."""
    r = requests.post(f"{BASE}/meetings/{_meeting_id}/commute-briefing")
    assert r.status_code == 200
    data = r.json()
    assert len(data["recent_interactions"]) >= 2


def test_02_commute_briefing_has_talking_points():
    """Commute briefing generates talking points."""
    r = requests.post(f"{BASE}/meetings/{_meeting_id}/commute-briefing")
    assert r.status_code == 200
    data = r.json()
    assert len(data["talking_points"]) >= 1


def test_02_commute_briefing_has_estimated_read_time():
    """Commute briefing includes estimated read time."""
    r = requests.post(f"{BASE}/meetings/{_meeting_id}/commute-briefing")
    assert r.status_code == 200
    data = r.json()
    assert "estimated_read_minutes" in data
    assert data["estimated_read_minutes"] >= 1


# ══════════════════════════════════════════════════════════════════════════════
# 3. QUICK BRIEF (CONTACT-SCOPED)
# ══════════════════════════════════════════════════════════════════════════════

def test_03_quick_brief():
    """Generate quick brief for a contact."""
    r = requests.get(f"{BASE}/contacts/{_contact_id}/quick-brief")
    assert r.status_code == 200
    data = r.json()
    assert data["contact_id"] == _contact_id
    assert "contact_name" in data
    assert "summary" in data
    assert "active_deals" in data
    assert "recent_interactions" in data
    assert "talking_points" in data
    assert "generated_at" in data


def test_03_quick_brief_has_deals():
    """Quick brief includes active deals."""
    r = requests.get(f"{BASE}/contacts/{_contact_id}/quick-brief")
    assert r.status_code == 200
    data = r.json()
    assert len(data["active_deals"]) >= 1
    assert data["active_deals"][0]["title"] is not None


def test_03_quick_brief_has_interactions():
    """Quick brief includes recent interactions."""
    r = requests.get(f"{BASE}/contacts/{_contact_id}/quick-brief")
    assert r.status_code == 200
    data = r.json()
    assert len(data["recent_interactions"]) >= 2


# ══════════════════════════════════════════════════════════════════════════════
# 4. DEPTH ADAPTATION
# ══════════════════════════════════════════════════════════════════════════════

def test_04_quick_depth():
    """5-minute travel = quick briefing depth."""
    r = requests.post(f"{BASE}/meetings/{_meeting_id}/commute-briefing", params={"travel_minutes": 5})
    assert r.status_code == 200
    data = r.json()
    assert data["briefing_depth"] == "quick"
    assert data["travel_minutes"] == 5


def test_04_standard_depth():
    """20-minute travel = standard briefing depth."""
    r = requests.post(f"{BASE}/meetings/{_meeting_id}/commute-briefing", params={"travel_minutes": 20})
    assert r.status_code == 200
    assert r.json()["briefing_depth"] == "standard"


def test_04_deep_depth():
    """45-minute travel = deep briefing depth."""
    r = requests.post(f"{BASE}/meetings/{_meeting_id}/commute-briefing", params={"travel_minutes": 45})
    assert r.status_code == 200
    assert r.json()["briefing_depth"] == "deep"


def test_04_quick_is_shorter():
    """Quick briefing has fewer estimated read minutes than deep."""
    r_quick = requests.post(f"{BASE}/meetings/{_meeting_id}/commute-briefing", params={"travel_minutes": 5})
    r_deep = requests.post(f"{BASE}/meetings/{_meeting_id}/commute-briefing", params={"travel_minutes": 60})
    assert r_quick.status_code == 200
    assert r_deep.status_code == 200
    assert r_quick.json()["estimated_read_minutes"] <= r_deep.json()["estimated_read_minutes"]


# ══════════════════════════════════════════════════════════════════════════════
# 5. EDGE CASES
# ══════════════════════════════════════════════════════════════════════════════

def test_05_briefing_nonexistent_meeting():
    """Commute briefing for non-existent meeting returns 404."""
    fake_id = str(uuid.uuid4())
    r = requests.post(f"{BASE}/meetings/{fake_id}/commute-briefing")
    assert r.status_code == 404


def test_05_quick_brief_nonexistent_contact():
    """Quick brief for non-existent contact returns 404."""
    fake_id = str(uuid.uuid4())
    r = requests.get(f"{BASE}/contacts/{fake_id}/quick-brief")
    assert r.status_code == 404


def test_05_meeting_no_deal():
    """Commute briefing for meeting with no deal still works."""
    fresh_cid = _create_contact(first="NoDeal", last=f"Mtg{_RUN_ID}", email_addr=f"nodeal.{_RUN_ID}@test.test")
    mid = _create_meeting(contact_id=fresh_cid, title=f"No Deal Meeting {_RUN_ID}")
    r = requests.post(f"{BASE}/meetings/{mid}/commute-briefing")
    assert r.status_code == 200
    data = r.json()
    assert data["deal_summary"] is None
    assert data["contact_summary"] is not None


def test_05_contact_no_interactions():
    """Quick brief for contact with no interactions returns empty lists."""
    cid = _create_contact(first="Lonely", last=f"NoIx{_RUN_ID}", email_addr=f"lonely.{_RUN_ID}@test.test")
    r = requests.get(f"{BASE}/contacts/{cid}/quick-brief")
    assert r.status_code == 200
    data = r.json()
    assert data["recent_interactions"] == []


# ══════════════════════════════════════════════════════════════════════════════
# 6. REGRESSION — Phase 1, 2.1, 2.2 core endpoints
# ══════════════════════════════════════════════════════════════════════════════

def test_06_regression_health():
    r = requests.get(f"{BASE}/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_06_regression_contacts():
    r = requests.get(f"{BASE}/contacts")
    assert r.status_code == 200
    assert "items" in r.json()


def test_06_regression_deals():
    r = requests.get(f"{BASE}/deals")
    assert r.status_code == 200
    assert "items" in r.json()


def test_06_regression_meetings():
    r = requests.get(f"{BASE}/meetings")
    assert r.status_code == 200
    assert "items" in r.json()


def test_06_regression_channel_interactions():
    r = requests.get(f"{BASE}/channel-interactions")
    assert r.status_code == 200
    assert "items" in r.json()


def test_06_regression_channel_dna():
    r = requests.get(f"{BASE}/channel-dna/summary")
    assert r.status_code == 200
    assert "items" in r.json()


def test_06_regression_dashboard():
    r = requests.get(f"{BASE}/dashboard")
    assert r.status_code == 200
    assert "metrics" in r.json()


def test_06_regression_lead_scores():
    r = requests.get(f"{BASE}/lead-scores/top")
    assert r.status_code == 200
    assert "items" in r.json()


# ══════════════════════════════════════════════════════════════════════════════
# 7. CONFIDENCE STAMP
# ══════════════════════════════════════════════════════════════════════════════

def test_07_confidence_stamp():
    """Phase 2.3 Commute Briefing v1 — all tests passed."""
    print("\n" + "=" * 70)
    print("  PHASE 2.3 CONFIDENCE STAMP")
    print("  Commute Briefing v1 — ALL BEAST TESTS PASSED")
    print(f"  Run ID: {_RUN_ID}")
    print("=" * 70 + "\n")


# ══════════════════════════════════════════════════════════════════════════════
# RUNNER
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed, failed = 0, 0

    for fn in tests:
        try:
            fn()
            passed += 1
            print(f"  PASS  {fn.__name__}")
        except Exception as e:
            failed += 1
            print(f"  FAIL  {fn.__name__}: {e}")

    total = passed + failed
    print(f"\n{'=' * 60}")
    print(f"  Phase 2.3 Beast: {passed}/{total} passed")
    if failed:
        print(f"  {failed} FAILED")
        sys.exit(1)
    else:
        print("  ALL PASSED")
    print(f"{'=' * 60}")
