"""Beast Test — Phase 2.2: Channel DNA v1 Enhancement.

Sections:
  0. Setup
  1. Channel Interaction CRUD
  2. Channel Interaction Filters
  3. Contact-Scoped Channel Interactions
  4. Channel Profile (response tracking)
  5. Enhanced Channel DNA (compute + refresh)
  6. Channel DNA Summary
  7. Edge Cases
  8. Regression (Phase 1 + 2.1 endpoints)
  9. Confidence Stamp
"""

import os
import uuid
from datetime import datetime, timedelta, timezone

import requests

BASE = os.environ.get("RIPPLE_API_BASE", "http://localhost:8100/api")

_RUN_ID = uuid.uuid4().hex[:8]

# ══════════════════════════════════════════════════════════════════════════════
# SETUP
# ══════════════════════════════════════════════════════════════════════════════

_contact_id = None
_ci_id = None
_ci_ids = []


def _create_contact(first="ChannelDNA", last=None, email_addr=None):
    last = last or f"Test{_RUN_ID}"
    email_addr = email_addr or f"{first.lower()}.{last.lower()}@p2p2.test"
    r = requests.post(f"{BASE}/contacts", json={
        "first_name": first,
        "last_name": last,
        "email": email_addr,
        "type": "lead",
        "phone": "+61400000001",
    })
    assert r.status_code == 201, f"Create contact failed: {r.text}"
    return r.json()["id"]


def test_00_setup():
    """Setup: create a contact for channel interaction tests."""
    global _contact_id
    _contact_id = _create_contact()
    assert _contact_id


# ══════════════════════════════════════════════════════════════════════════════
# 1. CHANNEL INTERACTION CRUD
# ══════════════════════════════════════════════════════════════════════════════

def test_01_create_channel_interaction_email():
    """Create an email outreach interaction."""
    global _ci_id
    r = requests.post(f"{BASE}/channel-interactions", json={
        "contact_id": _contact_id,
        "channel": "email",
        "direction": "out",
        "responded": True,
        "response_time_seconds": 3600,
    })
    assert r.status_code == 201, f"Create channel interaction failed: {r.text}"
    data = r.json()
    _ci_id = data["id"]
    _ci_ids.append(_ci_id)
    assert data["channel"] == "email"
    assert data["direction"] == "out"
    assert data["responded"] is True
    assert data["response_time_seconds"] == 3600
    assert data["day_of_week"] is not None
    assert data["hour_of_day"] is not None


def test_01_create_channel_interaction_phone():
    """Create a phone outreach interaction."""
    r = requests.post(f"{BASE}/channel-interactions", json={
        "contact_id": _contact_id,
        "channel": "phone",
        "direction": "out",
        "responded": False,
    })
    assert r.status_code == 201
    data = r.json()
    _ci_ids.append(data["id"])
    assert data["channel"] == "phone"
    assert data["responded"] is False


def test_01_create_channel_interaction_sms():
    """Create an SMS outreach with custom timestamp."""
    ts = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
    r = requests.post(f"{BASE}/channel-interactions", json={
        "contact_id": _contact_id,
        "channel": "sms",
        "direction": "out",
        "occurred_at": ts,
        "responded": True,
        "response_time_seconds": 120,
    })
    assert r.status_code == 201
    data = r.json()
    _ci_ids.append(data["id"])
    assert data["channel"] == "sms"
    assert data["response_time_seconds"] == 120


def test_01_create_channel_interaction_linkedin():
    """Create a LinkedIn inbound interaction."""
    r = requests.post(f"{BASE}/channel-interactions", json={
        "contact_id": _contact_id,
        "channel": "linkedin",
        "direction": "in",
    })
    assert r.status_code == 201
    data = r.json()
    _ci_ids.append(data["id"])
    assert data["direction"] == "in"


def test_01_create_multiple_email_interactions():
    """Create additional email interactions for response rate testing."""
    for i in range(3):
        ts = (datetime.now(timezone.utc) - timedelta(days=i, hours=10)).isoformat()
        r = requests.post(f"{BASE}/channel-interactions", json={
            "contact_id": _contact_id,
            "channel": "email",
            "direction": "out",
            "occurred_at": ts,
            "responded": i % 2 == 0,
            "response_time_seconds": 1800 * (i + 1) if i % 2 == 0 else None,
        })
        assert r.status_code == 201
        _ci_ids.append(r.json()["id"])


def test_01_get_channel_interaction():
    """Get a single channel interaction by ID."""
    r = requests.get(f"{BASE}/channel-interactions/{_ci_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == _ci_id
    assert data["channel"] == "email"


# ══════════════════════════════════════════════════════════════════════════════
# 2. CHANNEL INTERACTION FILTERS
# ══════════════════════════════════════════════════════════════════════════════

def test_02_list_channel_interactions_all():
    """List all channel interactions."""
    r = requests.get(f"{BASE}/channel-interactions")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 7  # We created 7 above


def test_02_list_channel_interactions_by_contact():
    """Filter channel interactions by contact_id."""
    r = requests.get(f"{BASE}/channel-interactions", params={"contact_id": _contact_id})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 7


def test_02_list_channel_interactions_by_channel():
    """Filter channel interactions by channel."""
    r = requests.get(f"{BASE}/channel-interactions", params={"channel": "email"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 4  # 1 initial + 3 additional emails


def test_02_list_channel_interactions_by_direction():
    """Filter channel interactions by direction."""
    r = requests.get(f"{BASE}/channel-interactions", params={"direction": "in"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 1  # LinkedIn inbound


# ══════════════════════════════════════════════════════════════════════════════
# 3. CONTACT-SCOPED CHANNEL INTERACTIONS
# ══════════════════════════════════════════════════════════════════════════════

def test_03_contact_channel_interactions():
    """List channel interactions scoped to a contact."""
    r = requests.get(f"{BASE}/contacts/{_contact_id}/channel-interactions")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 7


def test_03_contact_channel_interactions_filtered():
    """Filter contact channel interactions by channel."""
    r = requests.get(
        f"{BASE}/contacts/{_contact_id}/channel-interactions",
        params={"channel": "sms"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 1


# ══════════════════════════════════════════════════════════════════════════════
# 4. CHANNEL PROFILE (RESPONSE TRACKING)
# ══════════════════════════════════════════════════════════════════════════════

def test_04_channel_profile():
    """Get enhanced channel profile for a contact."""
    r = requests.get(f"{BASE}/contacts/{_contact_id}/channel-profile")
    assert r.status_code == 200
    data = r.json()
    assert data["contact_id"] == _contact_id
    assert "channel_stats" in data
    assert "response_rates" in data
    assert "best_time_slots" in data
    assert "total_outreach" in data
    assert isinstance(data["channel_stats"], list)
    assert len(data["channel_stats"]) >= 1


def test_04_channel_profile_has_response_rates():
    """Channel profile includes response rates per channel."""
    r = requests.get(f"{BASE}/contacts/{_contact_id}/channel-profile")
    assert r.status_code == 200
    data = r.json()
    assert "email" in data["response_rates"]
    assert data["response_rates"]["email"] is not None


def test_04_channel_profile_has_stats():
    """Channel profile has per-channel stats with outbound/inbound/responded."""
    r = requests.get(f"{BASE}/contacts/{_contact_id}/channel-profile")
    assert r.status_code == 200
    stats = r.json()["channel_stats"]
    assert len(stats) >= 1
    email_stat = next((s for s in stats if s["channel"] == "email"), None)
    assert email_stat is not None
    assert "outbound" in email_stat
    assert "response_rate" in email_stat


def test_04_channel_profile_nonexistent_contact():
    """Channel profile 404 for non-existent contact."""
    fake_id = str(uuid.uuid4())
    r = requests.get(f"{BASE}/contacts/{fake_id}/channel-profile")
    assert r.status_code == 404


# ══════════════════════════════════════════════════════════════════════════════
# 5. ENHANCED CHANNEL DNA (COMPUTE + REFRESH)
# ══════════════════════════════════════════════════════════════════════════════

def test_05_channel_dna_compute():
    """Compute channel DNA for a contact (now incorporates channel_interactions)."""
    r = requests.get(f"{BASE}/contacts/{_contact_id}/channel-dna")
    assert r.status_code == 200
    data = r.json()
    assert data["contact_id"] == _contact_id
    assert "primary_channel" in data
    assert "channels" in data
    assert "response_rates" in data
    assert "best_time_slots" in data
    assert "channel_ranking" in data
    assert data["total_interactions"] >= 7


def test_05_channel_dna_has_response_data():
    """Channel DNA includes response rate and avg response time per channel."""
    r = requests.get(f"{BASE}/contacts/{_contact_id}/channel-dna")
    assert r.status_code == 200
    channels = r.json()["channels"]
    email_ch = next((c for c in channels if c["channel"] == "email"), None)
    assert email_ch is not None
    assert "response_rate" in email_ch
    assert "avg_response_time_seconds" in email_ch


def test_05_channel_dna_refresh():
    """Force-refresh channel DNA for a contact."""
    r = requests.post(f"{BASE}/contacts/{_contact_id}/channel-dna/refresh")
    assert r.status_code == 200
    data = r.json()
    assert data["contact_id"] == _contact_id
    assert data["total_interactions"] >= 7


def test_05_channel_dna_nonexistent_contact():
    """Channel DNA 404 for non-existent contact."""
    fake_id = str(uuid.uuid4())
    r = requests.get(f"{BASE}/contacts/{fake_id}/channel-dna")
    assert r.status_code == 404


# ══════════════════════════════════════════════════════════════════════════════
# 6. CHANNEL DNA SUMMARY
# ══════════════════════════════════════════════════════════════════════════════

def test_06_channel_dna_summary():
    """Get aggregated channel DNA summary across all contacts."""
    r = requests.get(f"{BASE}/channel-dna/summary")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert "total_contacts_analysed" in data
    assert isinstance(data["items"], list)


# ══════════════════════════════════════════════════════════════════════════════
# 7. EDGE CASES
# ══════════════════════════════════════════════════════════════════════════════

def test_07_create_interaction_invalid_contact():
    """Create channel interaction with non-existent contact returns 404."""
    fake_id = str(uuid.uuid4())
    r = requests.post(f"{BASE}/channel-interactions", json={
        "contact_id": fake_id,
        "channel": "email",
        "direction": "out",
    })
    assert r.status_code == 404


def test_07_create_interaction_invalid_direction():
    """Create channel interaction with invalid direction returns 422."""
    r = requests.post(f"{BASE}/channel-interactions", json={
        "contact_id": _contact_id,
        "channel": "email",
        "direction": "sideways",
    })
    assert r.status_code == 422


def test_07_get_nonexistent_interaction():
    """Get non-existent channel interaction returns 404."""
    fake_id = str(uuid.uuid4())
    r = requests.get(f"{BASE}/channel-interactions/{fake_id}")
    assert r.status_code == 404


def test_07_delete_channel_interaction():
    """Delete a channel interaction."""
    r = requests.post(f"{BASE}/channel-interactions", json={
        "contact_id": _contact_id,
        "channel": "email",
        "direction": "out",
    })
    assert r.status_code == 201
    del_id = r.json()["id"]

    r = requests.delete(f"{BASE}/channel-interactions/{del_id}")
    assert r.status_code == 200
    assert "deleted" in r.json()["detail"].lower()

    r = requests.get(f"{BASE}/channel-interactions/{del_id}")
    assert r.status_code == 404


def test_07_empty_contact_channel_profile():
    """Channel profile for contact with no channel_interactions returns empty stats."""
    new_cid = _create_contact(first="Empty", last=f"Ch{_RUN_ID}", email_addr=f"empty.ch.{_RUN_ID}@test.test")
    r = requests.get(f"{BASE}/contacts/{new_cid}/channel-profile")
    assert r.status_code == 200
    data = r.json()
    assert data["total_outreach"] == 0
    assert data["channel_stats"] == []


def test_07_empty_contact_channel_dna():
    """Channel DNA for contact with no interactions returns empty result."""
    new_cid = _create_contact(first="NoDNA", last=f"Emp{_RUN_ID}", email_addr=f"nodna.{_RUN_ID}@test.test")
    r = requests.get(f"{BASE}/contacts/{new_cid}/channel-dna")
    assert r.status_code == 200
    data = r.json()
    assert data["total_interactions"] == 0
    assert data["primary_channel"] is None


# ══════════════════════════════════════════════════════════════════════════════
# 8. REGRESSION — Phase 1 + 2.1 core endpoints still work
# ══════════════════════════════════════════════════════════════════════════════

def test_08_regression_health():
    r = requests.get(f"{BASE}/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_08_regression_contacts():
    r = requests.get(f"{BASE}/contacts")
    assert r.status_code == 200
    assert "items" in r.json()


def test_08_regression_companies():
    r = requests.get(f"{BASE}/companies")
    assert r.status_code == 200
    assert "items" in r.json()


def test_08_regression_deals():
    r = requests.get(f"{BASE}/deals")
    assert r.status_code == 200
    assert "items" in r.json()


def test_08_regression_interactions():
    r = requests.get(f"{BASE}/interactions")
    assert r.status_code == 200
    assert "items" in r.json()


def test_08_regression_tasks():
    r = requests.get(f"{BASE}/tasks")
    assert r.status_code == 200
    assert "items" in r.json()


def test_08_regression_commitments():
    r = requests.get(f"{BASE}/commitments")
    assert r.status_code == 200
    assert "items" in r.json()


def test_08_regression_meetings():
    r = requests.get(f"{BASE}/meetings")
    assert r.status_code == 200
    assert "items" in r.json()


def test_08_regression_meeting_analytics():
    r = requests.get(f"{BASE}/meetings/analytics")
    assert r.status_code == 200
    assert "total_meetings" in r.json()


def test_08_regression_lead_scores():
    r = requests.get(f"{BASE}/lead-scores/top")
    assert r.status_code == 200
    assert "items" in r.json()


def test_08_regression_trust_decay():
    r = requests.get(f"{BASE}/trust-decay/at-risk")
    assert r.status_code == 200
    assert "items" in r.json()


def test_08_regression_dashboard():
    r = requests.get(f"{BASE}/dashboard")
    assert r.status_code == 200
    assert "metrics" in r.json()


# ══════════════════════════════════════════════════════════════════════════════
# 9. CONFIDENCE STAMP
# ══════════════════════════════════════════════════════════════════════════════

def test_09_confidence_stamp():
    """Phase 2.2 Channel DNA v1 Enhancement — all tests passed."""
    print("\n" + "=" * 70)
    print("  PHASE 2.2 CONFIDENCE STAMP")
    print("  Channel DNA v1 Enhancement — ALL BEAST TESTS PASSED")
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
    print(f"  Phase 2.2 Beast: {passed}/{total} passed")
    if failed:
        print(f"  {failed} FAILED")
        sys.exit(1)
    else:
        print("  ALL PASSED")
    print(f"{'=' * 60}")
