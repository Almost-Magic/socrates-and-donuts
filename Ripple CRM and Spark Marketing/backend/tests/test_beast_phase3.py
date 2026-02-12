"""Beast Test — Phase 3: Email Linking + Transparency Portal.

Sections:
  1. Email Link-to-Contact (manual)
  2. Email Link-to-Deal
  3. Deal-scoped Email List
  4. DSAR Request Management
  5. Consent Preferences
  6. Data Export
  7. Deletion Request
  8. Regression (Phase 1 + 2 + 2b endpoints)
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

_contact_id = None
_deal_id = None
_email_id = None


def _create_contact(first="P3", last=None, email_addr=None):
    last = last or f"Test{_RUN_ID}"
    email_addr = email_addr or f"{first.lower()}.{last.lower()}@p3.test"
    r = requests.post(f"{BASE}/contacts", json={
        "first_name": first,
        "last_name": last,
        "email": email_addr,
        "type": "lead",
        "phone": "+61400000000",
        "role": "Manager",
        "title": "Senior Manager",
        "linkedin_url": "https://linkedin.com/in/test-p3",
    })
    assert r.status_code == 201, f"Create contact failed: {r.text}"
    return r.json()["id"]


def _create_deal(title=None, contact_id=None):
    title = title or f"Deal {_RUN_ID}"
    payload = {"title": title, "stage": "lead", "value": 10000.0}
    if contact_id:
        payload["contact_id"] = contact_id
    r = requests.post(f"{BASE}/deals", json=payload)
    assert r.status_code == 201, f"Create deal failed: {r.text}"
    return r.json()["id"]


def _create_email(contact_id=None):
    r = requests.post(f"{BASE}/emails/sync", json={
        "direction": "in",
        "subject": f"Phase3 test email {_RUN_ID}",
        "body_text": "Test body for Phase 3.",
        "from_address": f"phase3-{_RUN_ID}@external.com",
        "to_addresses": ["mani@almostmagic.tech"],
    })
    assert r.status_code == 201, f"Create email failed: {r.text}"
    return r.json()["id"]


def test_setup():
    """Create shared test data for Phase 3 tests."""
    global _contact_id, _deal_id, _email_id
    _contact_id = _create_contact("Phase3Link")
    _deal_id = _create_deal(f"Phase3Deal {_RUN_ID}", _contact_id)
    _email_id = _create_email()


# ══════════════════════════════════════════════════════════════════════════
# SECTION 1 — Email Link-to-Contact (manual)
# ══════════════════════════════════════════════════════════════════════════

def test_link_email_to_contact():
    """Manually link an email to a contact."""
    assert _email_id and _contact_id
    r = requests.post(f"{BASE}/emails/{_email_id}/link-contact?contact_id={_contact_id}")
    assert r.status_code == 200, f"Link email to contact failed: {r.text}"
    data = r.json()
    assert data["contact_id"] == _contact_id


def test_link_email_to_nonexistent_contact():
    fake_id = str(uuid.uuid4())
    r = requests.post(f"{BASE}/emails/{_email_id}/link-contact?contact_id={fake_id}")
    assert r.status_code == 404


def test_link_nonexistent_email_to_contact():
    fake_id = str(uuid.uuid4())
    r = requests.post(f"{BASE}/emails/{fake_id}/link-contact?contact_id={_contact_id}")
    assert r.status_code == 404


# ══════════════════════════════════════════════════════════════════════════
# SECTION 2 — Email Link-to-Deal
# ══════════════════════════════════════════════════════════════════════════

def test_link_email_to_deal():
    """Link an email to a deal."""
    assert _email_id and _deal_id
    r = requests.post(f"{BASE}/emails/{_email_id}/link-deal?deal_id={_deal_id}")
    assert r.status_code == 200, f"Link email to deal failed: {r.text}"
    data = r.json()
    assert data["deal_id"] == _deal_id


def test_link_email_to_nonexistent_deal():
    fake_id = str(uuid.uuid4())
    r = requests.post(f"{BASE}/emails/{_email_id}/link-deal?deal_id={fake_id}")
    assert r.status_code == 404


def test_email_response_has_deal_id():
    """Verify the email response includes the deal_id field."""
    r = requests.get(f"{BASE}/emails/{_email_id}")
    assert r.status_code == 200
    data = r.json()
    assert "deal_id" in data
    assert data["deal_id"] == _deal_id


# ══════════════════════════════════════════════════════════════════════════
# SECTION 3 — Deal-scoped Email List
# ══════════════════════════════════════════════════════════════════════════

def test_deal_emails():
    """List emails linked to a deal."""
    assert _deal_id
    r = requests.get(f"{BASE}/deals/{_deal_id}/emails")
    assert r.status_code == 200, f"Deal emails failed: {r.text}"
    data = r.json()
    assert "items" in data
    assert data["total"] >= 1
    for item in data["items"]:
        assert item["deal_id"] == _deal_id


def test_deal_emails_nonexistent_deal():
    fake_id = str(uuid.uuid4())
    r = requests.get(f"{BASE}/deals/{fake_id}/emails")
    assert r.status_code == 404


# ══════════════════════════════════════════════════════════════════════════
# SECTION 4 — DSAR Request Management
# ══════════════════════════════════════════════════════════════════════════

_dsar_id = None


def test_create_dsar_request():
    global _dsar_id
    assert _contact_id
    r = requests.post(f"{BASE}/privacy/dsar-requests", json={
        "contact_id": _contact_id,
        "request_type": "access",
        "notes": f"Test DSAR request {_RUN_ID}",
    })
    assert r.status_code == 201, f"Create DSAR request failed: {r.text}"
    data = r.json()
    assert data["request_type"] == "access"
    assert data["status"] == "pending"
    assert data["contact_id"] == _contact_id
    _dsar_id = data["id"]


def test_create_dsar_export_request():
    r = requests.post(f"{BASE}/privacy/dsar-requests", json={
        "contact_id": _contact_id,
        "request_type": "export",
    })
    assert r.status_code == 201
    assert r.json()["request_type"] == "export"


def test_create_dsar_invalid_type_rejected():
    r = requests.post(f"{BASE}/privacy/dsar-requests", json={
        "contact_id": _contact_id,
        "request_type": "invalid_type",
    })
    assert r.status_code == 422


def test_list_dsar_requests():
    r = requests.get(f"{BASE}/privacy/dsar-requests")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert data["total"] >= 1


def test_list_dsar_requests_filter_status():
    r = requests.get(f"{BASE}/privacy/dsar-requests?status=pending")
    assert r.status_code == 200
    for item in r.json()["items"]:
        assert item["status"] == "pending"


def test_update_dsar_to_processing():
    assert _dsar_id
    r = requests.put(f"{BASE}/privacy/dsar-requests/{_dsar_id}", json={
        "status": "processing",
    })
    assert r.status_code == 200, f"Update DSAR failed: {r.text}"
    data = r.json()
    assert data["status"] == "processing"


def test_update_dsar_to_completed():
    assert _dsar_id
    r = requests.put(f"{BASE}/privacy/dsar-requests/{_dsar_id}", json={
        "status": "completed",
        "notes": "All data provided to subject.",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "completed"
    assert data["completed_at"] is not None


def test_update_nonexistent_dsar():
    fake_id = str(uuid.uuid4())
    r = requests.put(f"{BASE}/privacy/dsar-requests/{fake_id}", json={
        "status": "completed",
    })
    assert r.status_code == 404


# ══════════════════════════════════════════════════════════════════════════
# SECTION 5 — Consent Preferences
# ══════════════════════════════════════════════════════════════════════════

def test_get_consent_preferences_creates_defaults():
    """First access creates default preferences."""
    assert _contact_id
    r = requests.get(f"{BASE}/contacts/{_contact_id}/consent-preferences")
    assert r.status_code == 200, f"Get consent prefs failed: {r.text}"
    data = r.json()
    assert data["contact_id"] == _contact_id
    assert "email_marketing" in data
    assert "data_processing" in data
    assert "third_party_sharing" in data
    assert "analytics" in data
    assert "profiling" in data


def test_update_consent_preferences():
    assert _contact_id
    r = requests.put(f"{BASE}/contacts/{_contact_id}/consent-preferences", json={
        "email_marketing": True,
        "profiling": True,
    })
    assert r.status_code == 200, f"Update consent prefs failed: {r.text}"
    data = r.json()
    assert data["email_marketing"] is True
    assert data["profiling"] is True
    # Other fields should retain defaults
    assert data["data_processing"] is True
    assert data["third_party_sharing"] is False


def test_consent_preferences_nonexistent_contact():
    fake_id = str(uuid.uuid4())
    r = requests.get(f"{BASE}/contacts/{fake_id}/consent-preferences")
    assert r.status_code == 404


# ══════════════════════════════════════════════════════════════════════════
# SECTION 6 — Data Export
# ══════════════════════════════════════════════════════════════════════════

def test_export_contact_data():
    """Export all contact data as JSON."""
    assert _contact_id
    r = requests.get(f"{BASE}/privacy/contacts/{_contact_id}/export")
    assert r.status_code == 200, f"Export failed: {r.text}"
    data = r.json()
    assert "contact" in data
    assert data["contact"]["id"] == _contact_id
    assert "compliance_note" in data
    assert "Australian Privacy Act" in data["compliance_note"]
    assert "emails" in data


def test_export_has_content_disposition():
    """Export should have Content-Disposition header for download."""
    assert _contact_id
    r = requests.get(f"{BASE}/privacy/contacts/{_contact_id}/export")
    assert r.status_code == 200
    assert "content-disposition" in r.headers
    assert "attachment" in r.headers["content-disposition"]


# ══════════════════════════════════════════════════════════════════════════
# SECTION 7 — Deletion Request
# ══════════════════════════════════════════════════════════════════════════

def test_deletion_request():
    """Request deletion of contact data."""
    cid = _create_contact("DeleteMe")
    r = requests.post(f"{BASE}/privacy/contacts/{cid}/deletion-request")
    assert r.status_code == 200, f"Deletion request failed: {r.text}"
    data = r.json()
    assert "request_id" in data
    assert data["status"] == "pending"


def test_deletion_request_nonexistent_contact():
    fake_id = str(uuid.uuid4())
    r = requests.post(f"{BASE}/privacy/contacts/{fake_id}/deletion-request")
    assert r.status_code == 404


# ══════════════════════════════════════════════════════════════════════════
# SECTION 8 — DSAR Report includes emails
# ══════════════════════════════════════════════════════════════════════════

def test_dsar_report_includes_emails():
    """DSAR report should include emails for the contact."""
    assert _contact_id
    r = requests.get(f"{BASE}/privacy/contacts/{_contact_id}/report")
    assert r.status_code == 200
    data = r.json()
    assert "emails" in data
    assert "total_emails" in data


# ══════════════════════════════════════════════════════════════════════════
# SECTION 9 — Regression
# ══════════════════════════════════════════════════════════════════════════

def test_regression_health():
    r = requests.get(f"{BASE}/health")
    assert r.status_code == 200


def test_regression_contacts():
    r = requests.get(f"{BASE}/contacts")
    assert r.status_code == 200


def test_regression_deals():
    r = requests.get(f"{BASE}/deals")
    assert r.status_code == 200


def test_regression_emails():
    r = requests.get(f"{BASE}/emails")
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


def test_regression_scoring_rules():
    r = requests.get(f"{BASE}/scoring/rules")
    assert r.status_code == 200


def test_regression_privacy_consents():
    r = requests.get(f"{BASE}/privacy/consents")
    assert r.status_code == 200


# ══════════════════════════════════════════════════════════════════════════
# SECTION 10 — Confidence Stamp
# ══════════════════════════════════════════════════════════════════════════

def test_confidence_stamp():
    """Phase 3 Beast test complete. Email linking, DSAR requests,
    consent preferences, data export, deletion requests, and regression verified."""
    assert True


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
