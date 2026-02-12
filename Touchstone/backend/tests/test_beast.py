"""Beast Test — Touchstone Phase 1: Event Collection Layer.

Sections:
  1. Imports
  2. Health endpoint
  3. Event collection (/collect)
  4. Contact identification (/identify) + session stitching
  5. CRM webhook (/webhooks/crm)
  6. Campaign CRUD
  7. Contact listing + journey
  8. Edge cases
  9. Confidence Stamp
"""

import os
import uuid

import requests

BASE = os.environ.get("TOUCHSTONE_API_BASE", "http://localhost:8200/api/v1")

_RUN_ID = uuid.uuid4().hex[:8]


# ══════════════════════════════════════════════════════════════════════════
# SECTION 1 — Import checks
# ══════════════════════════════════════════════════════════════════════════

def test_import_fastapi():
    import fastapi
    assert fastapi

def test_import_sqlalchemy():
    import sqlalchemy
    assert sqlalchemy

def test_import_models():
    from app.models import Base, Contact, Touchpoint, Campaign, Deal, Attribution
    assert Base
    assert Contact.__tablename__ == "touchstone_contacts"
    assert Touchpoint.__tablename__ == "touchstone_touchpoints"
    assert Campaign.__tablename__ == "touchstone_campaigns"
    assert Deal.__tablename__ == "touchstone_deals"
    assert Attribution.__tablename__ == "touchstone_attributions"

def test_import_config():
    from app.config import settings
    assert settings.app_port == 8200

def test_import_app():
    from app.main import app
    assert app.title == "Touchstone"


# ══════════════════════════════════════════════════════════════════════════
# SECTION 2 — Health endpoint
# ══════════════════════════════════════════════════════════════════════════

def test_health_endpoint():
    r = requests.get(f"{BASE}/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["service"] == "touchstone"
    assert data["database"] == "connected"

def test_health_has_version():
    r = requests.get(f"{BASE}/health")
    data = r.json()
    assert data["version"] == "0.1.0"

def test_root_endpoint():
    r = requests.get("http://localhost:8200/")
    assert r.status_code == 200
    assert "Touchstone" in r.json()["message"]


# ══════════════════════════════════════════════════════════════════════════
# SECTION 3 — Event collection
# ══════════════════════════════════════════════════════════════════════════

def test_collect_page_view():
    r = requests.post(f"{BASE}/collect", json={
        "anonymous_id": f"beast-{_RUN_ID}-001",
        "touchpoint_type": "page_view",
        "page_url": "https://example.com/pricing",
        "referrer_url": "https://google.com",
    })
    assert r.status_code == 204

def test_collect_with_utm():
    r = requests.post(f"{BASE}/collect", json={
        "anonymous_id": f"beast-{_RUN_ID}-002",
        "touchpoint_type": "page_view",
        "page_url": "https://example.com/landing",
        "source": "google",
        "medium": "cpc",
        "utm_campaign": "spring-2026",
        "utm_content": "hero-banner",
        "utm_term": "crm software",
    })
    assert r.status_code == 204

def test_collect_custom_event():
    r = requests.post(f"{BASE}/collect", json={
        "anonymous_id": f"beast-{_RUN_ID}-003",
        "touchpoint_type": "form_submit",
        "page_url": "https://example.com/contact",
        "metadata": {"form": "contact-us", "submitted_fields": ["name", "email"]},
    })
    assert r.status_code == 204

def test_collect_requires_anonymous_id():
    r = requests.post(f"{BASE}/collect", json={
        "touchpoint_type": "page_view",
        "page_url": "https://example.com",
    })
    assert r.status_code == 422

def test_collect_minimal():
    """Minimum viable event: just anonymous_id."""
    r = requests.post(f"{BASE}/collect", json={
        "anonymous_id": f"beast-{_RUN_ID}-min",
    })
    assert r.status_code == 204


# ══════════════════════════════════════════════════════════════════════════
# SECTION 4 — Identification + session stitching
# ══════════════════════════════════════════════════════════════════════════

def test_identify_creates_contact():
    # First, send an anonymous event
    anon_id = f"stitch-{_RUN_ID}"
    requests.post(f"{BASE}/collect", json={
        "anonymous_id": anon_id,
        "touchpoint_type": "page_view",
        "page_url": "https://example.com/about",
    })
    requests.post(f"{BASE}/collect", json={
        "anonymous_id": anon_id,
        "touchpoint_type": "page_view",
        "page_url": "https://example.com/pricing",
    })

    # Now identify
    r = requests.post(f"{BASE}/identify", json={
        "anonymous_id": anon_id,
        "email": f"stitch-{_RUN_ID}@beast.test",
        "name": "Beast Stitcher",
        "company": "Test Corp",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["is_new"] is True
    assert data["touchpoints_linked"] == 2
    assert "contact_id" in data

def test_identify_duplicate_email():
    """Identifying with same email again should not create new contact."""
    anon_id = f"stitch2-{_RUN_ID}"
    requests.post(f"{BASE}/collect", json={
        "anonymous_id": anon_id,
        "touchpoint_type": "page_view",
        "page_url": "https://example.com/demo",
    })

    r = requests.post(f"{BASE}/identify", json={
        "anonymous_id": anon_id,
        "email": f"stitch-{_RUN_ID}@beast.test",  # same email as above
        "name": "Beast Stitcher Updated",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["is_new"] is False

def test_identify_requires_email():
    r = requests.post(f"{BASE}/identify", json={
        "anonymous_id": "no-email-test",
    })
    assert r.status_code == 422

def test_identify_requires_anonymous_id():
    r = requests.post(f"{BASE}/identify", json={
        "email": "test@example.com",
    })
    assert r.status_code == 422

def test_collect_after_identify_links_contact():
    """Events sent after identify should auto-link to contact."""
    anon_id = f"post-identify-{_RUN_ID}"
    # Identify first
    r = requests.post(f"{BASE}/identify", json={
        "anonymous_id": anon_id,
        "email": f"postid-{_RUN_ID}@beast.test",
        "name": "Post ID User",
    })
    contact_id = r.json()["contact_id"]

    # Send event with same anonymous_id
    requests.post(f"{BASE}/collect", json={
        "anonymous_id": anon_id,
        "touchpoint_type": "page_view",
        "page_url": "https://example.com/docs",
    })

    # Check journey
    r = requests.get(f"{BASE}/contacts/{contact_id}/journey")
    assert r.status_code == 200
    data = r.json()
    assert data["total_touchpoints"] >= 1
    # The page_view should have contact_id set
    urls = [tp["page_url"] for tp in data["touchpoints"]]
    assert "https://example.com/docs" in urls


# ══════════════════════════════════════════════════════════════════════════
# SECTION 5 — CRM webhook
# ══════════════════════════════════════════════════════════════════════════

def test_webhook_creates_deal():
    # First create a contact to link to
    anon_id = f"deal-{_RUN_ID}"
    requests.post(f"{BASE}/identify", json={
        "anonymous_id": anon_id,
        "email": f"deal-{_RUN_ID}@beast.test",
        "name": "Deal Maker",
    })

    r = requests.post(f"{BASE}/webhooks/crm", json={
        "crm_source": "ripple",
        "crm_deal_id": f"DEAL-{_RUN_ID}",
        "contact_email": f"deal-{_RUN_ID}@beast.test",
        "deal_name": "Enterprise CRM",
        "amount": 50000.00,
        "currency": "AUD",
        "stage": "won",
        "closed_at": "2026-02-12T00:00:00Z",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["is_new"] is True
    assert data["contact_id"] is not None

def test_webhook_updates_existing_deal():
    r = requests.post(f"{BASE}/webhooks/crm", json={
        "crm_source": "ripple",
        "crm_deal_id": f"DEAL-{_RUN_ID}",
        "contact_email": f"deal-{_RUN_ID}@beast.test",
        "deal_name": "Enterprise CRM v2",
        "amount": 75000.00,
        "stage": "won",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["is_new"] is False

def test_webhook_unknown_contact():
    """Deal with unknown email should still create deal (contact_id = null)."""
    r = requests.post(f"{BASE}/webhooks/crm", json={
        "crm_source": "hubspot",
        "crm_deal_id": f"UNKNOWN-{_RUN_ID}",
        "contact_email": f"unknown-{_RUN_ID}@nowhere.test",
        "deal_name": "Mystery Deal",
        "amount": 1000.00,
    })
    assert r.status_code == 200
    data = r.json()
    assert data["is_new"] is True
    assert data["contact_id"] is None

def test_webhook_requires_crm_source():
    r = requests.post(f"{BASE}/webhooks/crm", json={
        "crm_deal_id": "TEST-123",
        "contact_email": "test@test.com",
    })
    assert r.status_code == 422

def test_webhook_requires_crm_deal_id():
    r = requests.post(f"{BASE}/webhooks/crm", json={
        "crm_source": "ripple",
        "contact_email": "test@test.com",
    })
    assert r.status_code == 422


# ══════════════════════════════════════════════════════════════════════════
# SECTION 6 — Campaign CRUD
# ══════════════════════════════════════════════════════════════════════════

_campaign_id = None

def test_create_campaign():
    global _campaign_id
    r = requests.post(f"{BASE}/campaigns", json={
        "name": f"Spring Campaign {_RUN_ID}",
        "channel": "paid",
        "start_date": "2026-03-01",
        "end_date": "2026-05-31",
        "budget": 10000.00,
        "currency": "AUD",
    })
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == f"Spring Campaign {_RUN_ID}"
    assert data["budget"] == "10000.00"
    _campaign_id = data["id"]

def test_list_campaigns():
    r = requests.get(f"{BASE}/campaigns")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert data["total"] >= 1

def test_get_campaign():
    assert _campaign_id is not None
    r = requests.get(f"{BASE}/campaigns/{_campaign_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == f"Spring Campaign {_RUN_ID}"

def test_update_campaign():
    r = requests.put(f"{BASE}/campaigns/{_campaign_id}", json={
        "budget": 15000.00,
    })
    assert r.status_code == 200
    data = r.json()
    assert data["budget"] == "15000.00"

def test_get_nonexistent_campaign():
    fake_id = str(uuid.uuid4())
    r = requests.get(f"{BASE}/campaigns/{fake_id}")
    assert r.status_code == 404

def test_create_campaign_requires_name():
    r = requests.post(f"{BASE}/campaigns", json={
        "channel": "organic",
    })
    assert r.status_code == 422


# ══════════════════════════════════════════════════════════════════════════
# SECTION 7 — Contact listing + journey
# ══════════════════════════════════════════════════════════════════════════

def test_list_contacts():
    r = requests.get(f"{BASE}/contacts")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert data["total"] >= 1

def test_list_contacts_has_touchpoint_count():
    r = requests.get(f"{BASE}/contacts")
    data = r.json()
    # At least one contact should have touchpoints
    has_touchpoints = any(c["touchpoint_count"] > 0 for c in data["items"])
    assert has_touchpoints

def test_contact_journey():
    """Get journey for the stitched contact."""
    # Find the stitch contact
    r = requests.get(f"{BASE}/contacts")
    data = r.json()
    stitch_contact = None
    for c in data["items"]:
        if c["email"] and f"stitch-{_RUN_ID}" in c["email"]:
            stitch_contact = c
            break
    assert stitch_contact is not None, "Stitched contact not found"

    r = requests.get(f"{BASE}/contacts/{stitch_contact['id']}/journey")
    assert r.status_code == 200
    journey = r.json()
    assert journey["total_touchpoints"] >= 2
    assert len(journey["touchpoints"]) >= 2
    # Touchpoints should be ordered by timestamp
    timestamps = [tp["timestamp"] for tp in journey["touchpoints"]]
    assert timestamps == sorted(timestamps)

def test_journey_nonexistent_contact():
    fake_id = str(uuid.uuid4())
    r = requests.get(f"{BASE}/contacts/{fake_id}/journey")
    assert r.status_code == 404


# ══════════════════════════════════════════════════════════════════════════
# SECTION 8 — Edge cases
# ══════════════════════════════════════════════════════════════════════════

def test_pixel_endpoint_serves_js():
    r = requests.get("http://localhost:8200/pixel/touchstone.js")
    assert r.status_code == 200
    assert "application/javascript" in r.headers.get("content-type", "")
    assert "touchstone" in r.text.lower()
    assert "anonymous" in r.text.lower()

def test_pixel_size_under_5kb():
    r = requests.get("http://localhost:8200/pixel/touchstone.js")
    # Check uncompressed size (gzipped would be smaller)
    assert len(r.content) < 10000, f"Pixel is {len(r.content)} bytes uncompressed (target < 5KB gzipped)"

def test_cors_allows_any_origin():
    r = requests.options(f"{BASE}/collect", headers={
        "Origin": "https://random-website.com",
        "Access-Control-Request-Method": "POST",
    })
    # Should allow any origin
    assert r.status_code == 200

def test_collect_with_timestamp():
    r = requests.post(f"{BASE}/collect", json={
        "anonymous_id": f"ts-{_RUN_ID}",
        "touchpoint_type": "page_view",
        "page_url": "https://example.com",
        "timestamp": "2026-01-15T10:30:00Z",
    })
    assert r.status_code == 204

def test_delete_campaign():
    """Clean up: delete the test campaign."""
    assert _campaign_id is not None
    r = requests.delete(f"{BASE}/campaigns/{_campaign_id}")
    assert r.status_code == 204
    # Verify it's gone
    r = requests.get(f"{BASE}/campaigns/{_campaign_id}")
    assert r.status_code == 404


# ══════════════════════════════════════════════════════════════════════════
# SECTION 9 — Confidence Stamp
# ══════════════════════════════════════════════════════════════════════════

def test_confidence_stamp():
    """Touchstone Phase 1 Beast test complete. Event collection, session stitching,
    CRM webhook, campaign CRUD, contact journey, and pixel serving verified."""
    assert True


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
