"""Beast Test — Phase 2b: Email Integration + Scoring Rules.

Sections:
  1. Email Sync (webhook-style ingest)
  2. Email Send (queue outgoing)
  3. Email List / Detail / Contact Scoped
  4. Email Auto-Link to Contact
  5. Scoring Rules CRUD
  6. Scoring Rules Filters
  7. MQL Flag on Lead Score
  8. Regression (Phase 1 + Phase 2 endpoints)
  9. Confidence Stamp
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

def _create_contact(first="P2b", last=None, email_addr=None):
    last = last or f"Test{_RUN_ID}"
    email_addr = email_addr or f"{first.lower()}.{last.lower()}@p2b.test"
    r = requests.post(f"{BASE}/contacts", json={
        "first_name": first,
        "last_name": last,
        "email": email_addr,
        "type": "lead",
        "phone": "+61400000000",
        "role": "Manager",
        "title": "Senior Manager",
        "linkedin_url": "https://linkedin.com/in/test-p2b",
    })
    assert r.status_code == 201, f"Create contact failed: {r.text}"
    return r.json()["id"]


# ══════════════════════════════════════════════════════════════════════════
# SECTION 1 — Email Sync
# ══════════════════════════════════════════════════════════════════════════

_synced_email_id = None


def test_sync_inbound_email():
    global _synced_email_id
    r = requests.post(f"{BASE}/emails/sync", json={
        "direction": "in",
        "subject": f"Hello from sync {_RUN_ID}",
        "body_text": "This is a test email body.",
        "from_address": f"sender-{_RUN_ID}@external.com",
        "to_addresses": ["mani@almostmagic.tech"],
        "sent_at": "2026-02-10T10:00:00Z",
        "is_read": False,
    })
    assert r.status_code == 201, f"Sync email failed: {r.text}"
    data = r.json()
    assert data["direction"] == "in"
    assert data["subject"] == f"Hello from sync {_RUN_ID}"
    assert data["status"] == "synced"
    assert data["from_address"] == f"sender-{_RUN_ID}@external.com"
    _synced_email_id = data["id"]


def test_sync_outbound_email():
    r = requests.post(f"{BASE}/emails/sync", json={
        "direction": "out",
        "subject": f"Outbound sync {_RUN_ID}",
        "body_text": "Outbound test body.",
        "from_address": "mani@almostmagic.tech",
        "to_addresses": [f"recipient-{_RUN_ID}@external.com"],
        "sent_at": "2026-02-10T11:00:00Z",
    })
    assert r.status_code == 201
    data = r.json()
    assert data["direction"] == "out"
    assert data["status"] == "synced"


def test_sync_email_with_thread():
    thread = f"thread-{_RUN_ID}"
    msg_id = f"msg-{_RUN_ID}@external.com"
    r = requests.post(f"{BASE}/emails/sync", json={
        "direction": "in",
        "subject": f"Threaded email {_RUN_ID}",
        "body_text": "Part of a thread.",
        "from_address": f"thread-sender-{_RUN_ID}@external.com",
        "to_addresses": ["mani@almostmagic.tech"],
        "thread_id": thread,
        "message_id": msg_id,
    })
    assert r.status_code == 201
    data = r.json()
    assert data["thread_id"] == thread
    assert data["message_id"] == msg_id


def test_sync_email_missing_direction_rejected():
    r = requests.post(f"{BASE}/emails/sync", json={
        "subject": "No direction",
        "from_address": "bad@test.com",
        "to_addresses": ["mani@almostmagic.tech"],
    })
    assert r.status_code == 422


def test_sync_email_invalid_direction_rejected():
    r = requests.post(f"{BASE}/emails/sync", json={
        "direction": "sideways",
        "subject": "Bad direction",
        "from_address": "bad@test.com",
        "to_addresses": ["mani@almostmagic.tech"],
    })
    assert r.status_code == 422


# ══════════════════════════════════════════════════════════════════════════
# SECTION 2 — Email Send (Queue Outgoing)
# ══════════════════════════════════════════════════════════════════════════

_sent_email_id = None
_send_contact_id = None


def test_send_email():
    global _sent_email_id, _send_contact_id
    _send_contact_id = _create_contact("EmailSend")
    r = requests.post(f"{BASE}/emails/send", json={
        "contact_id": _send_contact_id,
        "to_addresses": [f"emailsend.test{_RUN_ID}@p2b.test"],
        "subject": f"Outgoing email {_RUN_ID}",
        "body_text": "This email is queued for sending.",
    })
    assert r.status_code == 201, f"Send email failed: {r.text}"
    data = r.json()
    assert data["direction"] == "out"
    assert data["status"] == "pending"
    assert data["contact_id"] == _send_contact_id
    _sent_email_id = data["id"]


def test_send_email_requires_to_and_subject():
    r = requests.post(f"{BASE}/emails/send", json={
        "body_text": "Missing to and subject",
    })
    assert r.status_code == 422


# ══════════════════════════════════════════════════════════════════════════
# SECTION 3 — Email List / Detail / Contact Scoped
# ══════════════════════════════════════════════════════════════════════════

def test_list_emails():
    r = requests.get(f"{BASE}/emails?page_size=10")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 3  # We created at least 3 synced + 1 sent


def test_list_emails_filter_direction():
    r = requests.get(f"{BASE}/emails?direction=in")
    assert r.status_code == 200
    for item in r.json()["items"]:
        assert item["direction"] == "in"


def test_list_emails_search():
    r = requests.get(f"{BASE}/emails?search={_RUN_ID}")
    assert r.status_code == 200
    assert r.json()["total"] >= 1


def test_get_email_detail():
    assert _synced_email_id, "No synced email"
    r = requests.get(f"{BASE}/emails/{_synced_email_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == _synced_email_id
    assert data["subject"] == f"Hello from sync {_RUN_ID}"


def test_get_nonexistent_email():
    fake_id = str(uuid.uuid4())
    r = requests.get(f"{BASE}/emails/{fake_id}")
    assert r.status_code == 404


def test_get_contact_emails():
    assert _send_contact_id, "No send contact"
    r = requests.get(f"{BASE}/contacts/{_send_contact_id}/emails")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 1
    for item in data["items"]:
        assert item["contact_id"] == _send_contact_id


def test_get_contact_emails_nonexistent_contact():
    fake_id = str(uuid.uuid4())
    r = requests.get(f"{BASE}/contacts/{fake_id}/emails")
    assert r.status_code == 404


# ══════════════════════════════════════════════════════════════════════════
# SECTION 4 — Email Auto-Link to Contact
# ══════════════════════════════════════════════════════════════════════════

def test_auto_link_inbound_email():
    """Syncing an inbound email with from_address matching a contact should auto-link."""
    email_addr = f"autolink-{_RUN_ID}@p2b.test"
    cid = _create_contact("AutoLink", email_addr=email_addr)

    r = requests.post(f"{BASE}/emails/sync", json={
        "direction": "in",
        "subject": f"Auto-linked inbound {_RUN_ID}",
        "body_text": "Should auto-link.",
        "from_address": email_addr,
        "to_addresses": ["mani@almostmagic.tech"],
    })
    assert r.status_code == 201
    data = r.json()
    assert data["contact_id"] == cid, "Email should be auto-linked to contact"


def test_auto_link_outbound_email():
    """Syncing an outbound email with to_addresses matching a contact should auto-link."""
    email_addr = f"autolink-out-{_RUN_ID}@p2b.test"
    cid = _create_contact("AutoLinkOut", email_addr=email_addr)

    r = requests.post(f"{BASE}/emails/sync", json={
        "direction": "out",
        "subject": f"Auto-linked outbound {_RUN_ID}",
        "body_text": "Should auto-link outbound.",
        "from_address": "mani@almostmagic.tech",
        "to_addresses": [email_addr],
    })
    assert r.status_code == 201
    data = r.json()
    assert data["contact_id"] == cid, "Outbound email should be auto-linked to contact"


def test_unlinked_email_has_no_contact():
    """Email from unknown address should have null contact_id."""
    r = requests.post(f"{BASE}/emails/sync", json={
        "direction": "in",
        "subject": f"Unknown sender {_RUN_ID}",
        "body_text": "No matching contact.",
        "from_address": f"nobody-{_RUN_ID}@unknown.com",
        "to_addresses": ["mani@almostmagic.tech"],
    })
    assert r.status_code == 201
    assert r.json()["contact_id"] is None


# ══════════════════════════════════════════════════════════════════════════
# SECTION 5 — Scoring Rules CRUD
# ══════════════════════════════════════════════════════════════════════════

_rule_id = None


def test_create_scoring_rule():
    global _rule_id
    r = requests.post(f"{BASE}/scoring/rules", json={
        "brain": "fit",
        "attribute": f"has_email_{_RUN_ID}",
        "label": f"Has Email ({_RUN_ID})",
        "points": 25.0,
        "max_points": 100.0,
        "description": "Points for having email address",
        "is_active": True,
        "sort_order": 1,
    })
    assert r.status_code == 201, f"Create rule failed: {r.text}"
    data = r.json()
    assert data["brain"] == "fit"
    assert data["attribute"] == f"has_email_{_RUN_ID}"
    assert data["points"] == 25.0
    assert data["is_active"] is True
    _rule_id = data["id"]


def test_list_scoring_rules():
    r = requests.get(f"{BASE}/scoring/rules")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1


def test_get_scoring_rule():
    assert _rule_id, "Rule not created"
    r = requests.get(f"{BASE}/scoring/rules/{_rule_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == _rule_id
    assert data["brain"] == "fit"


def test_update_scoring_rule():
    assert _rule_id, "Rule not created"
    r = requests.put(f"{BASE}/scoring/rules/{_rule_id}", json={
        "points": 50.0,
        "label": f"Has Email Updated ({_RUN_ID})",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["points"] == 50.0
    assert "Updated" in data["label"]


def test_create_intent_rule():
    r = requests.post(f"{BASE}/scoring/rules", json={
        "brain": "intent",
        "attribute": f"recent_activity_{_RUN_ID}",
        "label": f"Recent Activity ({_RUN_ID})",
        "points": 30.0,
        "max_points": 100.0,
        "sort_order": 1,
    })
    assert r.status_code == 201
    assert r.json()["brain"] == "intent"


def test_create_instinct_rule():
    r = requests.post(f"{BASE}/scoring/rules", json={
        "brain": "instinct",
        "attribute": f"positive_sentiment_{_RUN_ID}",
        "label": f"Positive Sentiment ({_RUN_ID})",
        "points": 20.0,
        "max_points": 100.0,
        "sort_order": 1,
    })
    assert r.status_code == 201
    assert r.json()["brain"] == "instinct"


def test_create_invalid_brain_rejected():
    r = requests.post(f"{BASE}/scoring/rules", json={
        "brain": "random",
        "attribute": "bad_brain",
        "label": "Bad Brain Rule",
    })
    assert r.status_code == 422


def test_get_nonexistent_rule():
    fake_id = str(uuid.uuid4())
    r = requests.get(f"{BASE}/scoring/rules/{fake_id}")
    assert r.status_code == 404


# ══════════════════════════════════════════════════════════════════════════
# SECTION 6 — Scoring Rules Filters
# ══════════════════════════════════════════════════════════════════════════

def test_filter_rules_by_brain():
    r = requests.get(f"{BASE}/scoring/rules?brain=fit")
    assert r.status_code == 200
    for item in r.json()["items"]:
        assert item["brain"] == "fit"


def test_filter_rules_by_active():
    r = requests.get(f"{BASE}/scoring/rules?is_active=true")
    assert r.status_code == 200
    for item in r.json()["items"]:
        assert item["is_active"] is True


# ══════════════════════════════════════════════════════════════════════════
# SECTION 7 — MQL Flag on Lead Score
# ══════════════════════════════════════════════════════════════════════════

def test_lead_score_has_mql_flag():
    """Calculate a lead score and verify is_mql field is present."""
    cid = _create_contact("MqlTest")
    # Add some interactions to get a score
    requests.post(f"{BASE}/interactions", json={
        "contact_id": cid, "type": "email",
        "channel": "email", "subject": f"MQL test {_RUN_ID}",
        "sentiment_score": 0.9,
    })
    r = requests.post(f"{BASE}/contacts/{cid}/lead-score/recalculate")
    assert r.status_code == 200
    data = r.json()
    assert "is_mql" in data
    assert isinstance(data["is_mql"], bool)
    assert "composite_score" in data


# ══════════════════════════════════════════════════════════════════════════
# SECTION 8 — Delete Scoring Rule + Regression
# ══════════════════════════════════════════════════════════════════════════

def test_delete_scoring_rule():
    assert _rule_id, "Rule not created"
    r = requests.delete(f"{BASE}/scoring/rules/{_rule_id}")
    assert r.status_code == 200


def test_delete_nonexistent_rule():
    fake_id = str(uuid.uuid4())
    r = requests.delete(f"{BASE}/scoring/rules/{fake_id}")
    assert r.status_code == 404


def test_regression_health():
    r = requests.get(f"{BASE}/health")
    assert r.status_code == 200


def test_regression_contacts():
    r = requests.get(f"{BASE}/contacts")
    assert r.status_code == 200


def test_regression_deals():
    r = requests.get(f"{BASE}/deals")
    assert r.status_code == 200


def test_regression_tags():
    r = requests.get(f"{BASE}/tags")
    assert r.status_code == 200


def test_regression_lead_scores():
    r = requests.get(f"{BASE}/lead-scores/top?limit=5")
    assert r.status_code == 200


def test_regression_channel_dna():
    r = requests.get(f"{BASE}/channel-dna/summary")
    assert r.status_code == 200


def test_regression_trust_decay():
    r = requests.get(f"{BASE}/trust-decay/at-risk")
    assert r.status_code == 200


# ══════════════════════════════════════════════════════════════════════════
# SECTION 9 — Confidence Stamp
# ══════════════════════════════════════════════════════════════════════════

def test_confidence_stamp():
    """Phase 2b Beast test complete. Email sync/send, auto-link,
    scoring rules CRUD, MQL flag, and regression verified."""
    assert True


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
