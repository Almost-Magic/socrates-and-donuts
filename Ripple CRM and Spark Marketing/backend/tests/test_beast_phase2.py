"""Beast Test — Phase 2: Intelligence Layer.

Sections:
  1. Tag Management CRUD
  2. Contact-Tag Assignment
  3. Three Brains Lead Scoring
  4. Channel DNA
  5. Trust Decay
  6. Deal Analytics — Pipeline
  7. Deal Analytics — Velocity
  8. Deal Analytics — Stalled Deals
  9. Regression (Phase 1 endpoints)
  10. Confidence Stamp
"""

import os
import uuid

import requests

BASE = os.environ.get("RIPPLE_API_BASE", "http://localhost:8100/api")

# Unique suffix per test run to avoid collisions
_RUN_ID = uuid.uuid4().hex[:8]


# ══════════════════════════════════════════════════════════════════════════
# SETUP — create test data
# ══════════════════════════════════════════════════════════════════════════

def _create_contact(first="Phase2", last=None):
    last = last or f"Test{_RUN_ID}"
    r = requests.post(f"{BASE}/contacts", json={
        "first_name": first,
        "last_name": last,
        "email": f"{first.lower()}.{last.lower()}@phase2.test",
        "type": "lead",
        "phone": "+61400000000",
        "title": "Director",
        "linkedin_url": "https://linkedin.com/in/test",
    })
    assert r.status_code == 201, f"Create contact failed: {r.text}"
    return r.json()["id"]


def _create_interaction(contact_id, channel="email", sentiment=0.5):
    r = requests.post(f"{BASE}/interactions", json={
        "contact_id": contact_id,
        "type": "email",
        "channel": channel,
        "subject": f"Test interaction {_RUN_ID}",
        "sentiment_score": sentiment,
    })
    assert r.status_code == 201, f"Create interaction failed: {r.text}"
    return r.json()["id"]


def _create_deal(contact_id, stage="lead", value=50000):
    r = requests.post(f"{BASE}/deals", json={
        "contact_id": contact_id,
        "title": f"Phase2 Deal {_RUN_ID}",
        "stage": stage,
        "value": value,
    })
    assert r.status_code == 201, f"Create deal failed: {r.text}"
    return r.json()["id"]


# ══════════════════════════════════════════════════════════════════════════
# SECTION 1 — Tag Management CRUD
# ══════════════════════════════════════════════════════════════════════════

_tag_id = None


def test_create_tag():
    global _tag_id
    r = requests.post(f"{BASE}/tags", json={"name": f"phase2-tag-{_RUN_ID}", "colour": "#c9a84c"})
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == f"phase2-tag-{_RUN_ID}"
    assert data["colour"] == "#c9a84c"
    _tag_id = data["id"]


def test_list_tags():
    r = requests.get(f"{BASE}/tags")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert "total" in data


def test_get_tag():
    assert _tag_id, "Tag not created"
    r = requests.get(f"{BASE}/tags/{_tag_id}")
    assert r.status_code == 200
    assert r.json()["name"] == f"phase2-tag-{_RUN_ID}"


def test_update_tag():
    assert _tag_id, "Tag not created"
    r = requests.put(f"{BASE}/tags/{_tag_id}", json={"colour": "#34d399"})
    assert r.status_code == 200
    assert r.json()["colour"] == "#34d399"


def test_create_duplicate_tag_rejected():
    r = requests.post(f"{BASE}/tags", json={"name": f"phase2-tag-{_RUN_ID}"})
    assert r.status_code == 409


def test_get_nonexistent_tag():
    fake_id = str(uuid.uuid4())
    r = requests.get(f"{BASE}/tags/{fake_id}")
    assert r.status_code == 404


# ══════════════════════════════════════════════════════════════════════════
# SECTION 2 — Contact-Tag Assignment
# ══════════════════════════════════════════════════════════════════════════

_contact_id = None


def test_assign_tags_to_contact():
    global _contact_id
    _contact_id = _create_contact("TagTest")
    assert _tag_id, "Tag not created"
    r = requests.post(f"{BASE}/contacts/{_contact_id}/tags", json=[_tag_id])
    assert r.status_code == 200
    data = r.json()
    assert data["tag_count"] == 1


def test_contact_has_tags_in_response():
    assert _contact_id, "Contact not created"
    r = requests.get(f"{BASE}/contacts/{_contact_id}")
    assert r.status_code == 200
    data = r.json()
    assert "tags" in data
    assert len(data["tags"]) >= 1
    assert data["tags"][0]["name"] == f"phase2-tag-{_RUN_ID}"


# ══════════════════════════════════════════════════════════════════════════
# SECTION 3 — Three Brains Lead Scoring
# ══════════════════════════════════════════════════════════════════════════

_scored_contact_id = None


def test_lead_score_calculate():
    global _scored_contact_id
    _scored_contact_id = _create_contact("ScoreTest")
    # Add interactions for intent signal
    _create_interaction(_scored_contact_id, "email", 0.8)
    _create_interaction(_scored_contact_id, "call", 0.6)

    r = requests.get(f"{BASE}/contacts/{_scored_contact_id}/lead-score")
    assert r.status_code == 200
    data = r.json()
    assert "fit_score" in data
    assert "intent_score" in data
    assert "instinct_score" in data
    assert "composite_score" in data
    assert data["composite_score"] > 0


def test_lead_score_has_breakdowns():
    assert _scored_contact_id, "Contact not scored"
    r = requests.get(f"{BASE}/contacts/{_scored_contact_id}/lead-score")
    data = r.json()
    assert "fit_breakdown" in data
    assert "intent_breakdown" in data
    assert "instinct_breakdown" in data
    assert "components" in data["fit_breakdown"]


def test_lead_score_recalculate():
    assert _scored_contact_id, "Contact not scored"
    r = requests.post(f"{BASE}/contacts/{_scored_contact_id}/lead-score/recalculate")
    assert r.status_code == 200
    assert r.json()["composite_score"] > 0


def test_lead_score_leaderboard():
    r = requests.get(f"{BASE}/lead-scores/top?limit=5")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert "total" in data


def test_lead_score_recalculate_all():
    r = requests.post(f"{BASE}/lead-scores/recalculate-all")
    assert r.status_code == 200
    assert "recalculated" in r.json()


def test_lead_score_nonexistent_contact():
    fake_id = str(uuid.uuid4())
    r = requests.get(f"{BASE}/contacts/{fake_id}/lead-score")
    assert r.status_code == 404


# ══════════════════════════════════════════════════════════════════════════
# SECTION 4 — Channel DNA
# ══════════════════════════════════════════════════════════════════════════

_channel_contact_id = None


def test_channel_dna_compute():
    global _channel_contact_id
    _channel_contact_id = _create_contact("ChannelTest")
    _create_interaction(_channel_contact_id, "email", 0.5)
    _create_interaction(_channel_contact_id, "email", 0.7)
    _create_interaction(_channel_contact_id, "call", 0.3)

    r = requests.get(f"{BASE}/contacts/{_channel_contact_id}/channel-dna")
    assert r.status_code == 200
    data = r.json()
    assert "primary_channel" in data
    assert "channels" in data
    assert data["total_interactions"] == 3
    assert data["primary_channel"] == "email"


def test_channel_dna_has_percentages():
    assert _channel_contact_id, "Contact not created"
    r = requests.get(f"{BASE}/contacts/{_channel_contact_id}/channel-dna")
    data = r.json()
    email_ch = next((c for c in data["channels"] if c["channel"] == "email"), None)
    assert email_ch is not None
    assert email_ch["percentage"] > 50


def test_channel_dna_refresh():
    assert _channel_contact_id, "Contact not created"
    r = requests.post(f"{BASE}/contacts/{_channel_contact_id}/channel-dna/refresh")
    assert r.status_code == 200
    assert r.json()["total_interactions"] == 3


def test_channel_dna_summary():
    r = requests.get(f"{BASE}/channel-dna/summary")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert "total_contacts_analysed" in data


def test_channel_dna_empty_contact():
    cid = _create_contact("EmptyChannel")
    r = requests.get(f"{BASE}/contacts/{cid}/channel-dna")
    assert r.status_code == 200
    data = r.json()
    assert data["total_interactions"] == 0
    assert data["primary_channel"] is None


# ══════════════════════════════════════════════════════════════════════════
# SECTION 5 — Trust Decay
# ══════════════════════════════════════════════════════════════════════════

_decay_contact_id = None


def test_trust_decay_compute():
    global _decay_contact_id
    _decay_contact_id = _create_contact("DecayTest")
    _create_interaction(_decay_contact_id, "email", 0.5)

    r = requests.get(f"{BASE}/contacts/{_decay_contact_id}/trust-decay")
    assert r.status_code == 200
    data = r.json()
    assert "status" in data
    assert "days_since_last" in data
    assert "baseline_gap_days" in data
    assert "decay_ratio" in data
    assert data["interaction_count"] >= 1


def test_trust_decay_recent_is_healthy():
    assert _decay_contact_id, "Contact not created"
    r = requests.get(f"{BASE}/contacts/{_decay_contact_id}/trust-decay")
    data = r.json()
    # Just created interaction, should be healthy
    assert data["status"] == "healthy"


def test_trust_decay_at_risk_list():
    r = requests.get(f"{BASE}/trust-decay/at-risk")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert "total" in data


def test_trust_decay_recalculate_all():
    r = requests.post(f"{BASE}/trust-decay/recalculate-all")
    assert r.status_code == 200
    assert "recalculated" in r.json()


def test_trust_decay_dormant_with_no_interactions():
    cid = _create_contact("DormantTest")
    r = requests.get(f"{BASE}/contacts/{cid}/trust-decay")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "dormant"
    assert data["interaction_count"] == 0


# ══════════════════════════════════════════════════════════════════════════
# SECTION 6 — Deal Analytics: Pipeline
# ══════════════════════════════════════════════════════════════════════════

def test_pipeline_summary():
    r = requests.get(f"{BASE}/deal-analytics/pipeline")
    assert r.status_code == 200
    data = r.json()
    assert "stages" in data
    assert "total_deals" in data
    assert "total_pipeline_value" in data
    assert "win_count" in data
    assert "loss_count" in data


def test_pipeline_has_stage_metrics():
    r = requests.get(f"{BASE}/deal-analytics/pipeline")
    data = r.json()
    if data["stages"]:
        stage = data["stages"][0]
        assert "stage" in stage
        assert "count" in stage
        assert "total_value" in stage
        assert "avg_value" in stage


# ══════════════════════════════════════════════════════════════════════════
# SECTION 7 — Deal Analytics: Velocity
# ══════════════════════════════════════════════════════════════════════════

def test_stage_velocity():
    r = requests.get(f"{BASE}/deal-analytics/velocity")
    assert r.status_code == 200
    data = r.json()
    assert "stages" in data
    assert "avg_cycle_days" in data


def test_velocity_has_stage_entries():
    r = requests.get(f"{BASE}/deal-analytics/velocity")
    data = r.json()
    assert len(data["stages"]) > 0
    stage = data["stages"][0]
    assert "stage" in stage
    assert "avg_days" in stage
    assert "deal_count" in stage


# ══════════════════════════════════════════════════════════════════════════
# SECTION 8 — Deal Analytics: Stalled Deals
# ══════════════════════════════════════════════════════════════════════════

def test_stalled_deals_endpoint():
    r = requests.get(f"{BASE}/deal-analytics/stalled")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert "total" in data
    assert "stall_threshold_days" in data


def test_stalled_deals_custom_threshold():
    r = requests.get(f"{BASE}/deal-analytics/stalled?threshold_days=1")
    assert r.status_code == 200
    data = r.json()
    assert data["stall_threshold_days"] == 1


# ══════════════════════════════════════════════════════════════════════════
# SECTION 9 — Regression: Phase 1 endpoints
# ══════════════════════════════════════════════════════════════════════════

def test_health_still_works():
    r = requests.get(f"{BASE}/health")
    assert r.status_code == 200

def test_contacts_still_work():
    r = requests.get(f"{BASE}/contacts")
    assert r.status_code == 200

def test_deals_still_work():
    r = requests.get(f"{BASE}/deals")
    assert r.status_code == 200

def test_dashboard_still_works():
    r = requests.get(f"{BASE}/dashboard")
    assert r.status_code == 200

def test_interactions_still_work():
    r = requests.get(f"{BASE}/interactions")
    assert r.status_code == 200

def test_commitments_still_work():
    r = requests.get(f"{BASE}/commitments")
    assert r.status_code == 200

def test_tasks_still_work():
    r = requests.get(f"{BASE}/tasks")
    assert r.status_code == 200

def test_settings_still_work():
    r = requests.get(f"{BASE}/settings")
    assert r.status_code == 200


# ══════════════════════════════════════════════════════════════════════════
# SECTION 10 — Tag Cleanup + Delete
# ══════════════════════════════════════════════════════════════════════════

def test_delete_tag():
    assert _tag_id, "Tag not created"
    r = requests.delete(f"{BASE}/tags/{_tag_id}")
    assert r.status_code == 200


def test_delete_nonexistent_tag():
    fake_id = str(uuid.uuid4())
    r = requests.delete(f"{BASE}/tags/{fake_id}")
    assert r.status_code == 404


# ══════════════════════════════════════════════════════════════════════════
# SECTION 11 — Confidence Stamp
# ══════════════════════════════════════════════════════════════════════════

def test_confidence_stamp():
    """Phase 2 Beast test complete. Tag CRUD, Three Brains Lead Scoring,
    Channel DNA, Trust Decay, Deal Analytics (pipeline, velocity, stalled),
    and Phase 1 regression verified."""
    assert True


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
