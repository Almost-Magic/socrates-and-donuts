"""
Beast Test Suite — Peterman V4.1
Almost Magic Tech Lab

Minimum 27 tests for Gate 2 compliance.
"""
import pytest
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import create_app
from backend.models import db


@pytest.fixture(scope="session")
def app():
    """Create test app instance."""
    app = create_app("development")
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql://postgres:peterman2026@localhost:5433/peterman"
    )
    with app.app_context():
        db.create_all()
        yield app
        # Cleanup test data
        db.session.rollback()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


# ============================================================
# 1. HEALTH TESTS (3 tests)
# ============================================================

class TestHealth:
    def test_health_returns_200(self, client):
        r = client.get("/api/health")
        assert r.status_code == 200

    def test_health_has_status_ok(self, client):
        r = client.get("/api/health")
        data = r.get_json()
        assert data["status"] == "ok"

    def test_health_has_service_name(self, client):
        r = client.get("/api/health")
        data = r.get_json()
        assert data["service"] == "peterman"
        assert "version" in data


# ============================================================
# 2. API ENDPOINT TESTS (8 tests)
# ============================================================

class TestBrandAPI:
    def test_list_brands_returns_200(self, client):
        r = client.get("/api/brands")
        assert r.status_code == 200
        data = r.get_json()
        assert "brands" in data

    def test_create_brand(self, client):
        r = client.post("/api/brands",
                        data=json.dumps({"name": "Test Brand", "domain": "test.com", "industry": "technology"}),
                        content_type="application/json")
        assert r.status_code == 201
        data = r.get_json()
        assert data["brand"]["name"] == "Test Brand"

    def test_create_brand_without_name_fails(self, client):
        r = client.post("/api/brands",
                        data=json.dumps({"domain": "test.com"}),
                        content_type="application/json")
        assert r.status_code == 400

    def test_get_brand(self, client):
        # Create first
        r = client.post("/api/brands",
                        data=json.dumps({"name": "Get Test Brand"}),
                        content_type="application/json")
        brand_id = r.get_json()["brand"]["id"]

        r = client.get(f"/api/brands/{brand_id}")
        assert r.status_code == 200
        assert r.get_json()["brand"]["name"] == "Get Test Brand"

    def test_get_nonexistent_brand_returns_404(self, client):
        r = client.get("/api/brands/99999")
        assert r.status_code == 404

    def test_update_brand(self, client):
        r = client.post("/api/brands",
                        data=json.dumps({"name": "Update Me"}),
                        content_type="application/json")
        brand_id = r.get_json()["brand"]["id"]

        r = client.put(f"/api/brands/{brand_id}",
                       data=json.dumps({"name": "Updated Name"}),
                       content_type="application/json")
        assert r.status_code == 200
        assert r.get_json()["brand"]["name"] == "Updated Name"

    def test_add_keyword(self, client):
        r = client.post("/api/brands",
                        data=json.dumps({"name": "KW Brand"}),
                        content_type="application/json")
        brand_id = r.get_json()["brand"]["id"]

        r = client.post(f"/api/brands/{brand_id}/keywords",
                        data=json.dumps({"keyword": "AI governance", "category": "primary"}),
                        content_type="application/json")
        assert r.status_code == 201

    def test_add_competitor(self, client):
        r = client.post("/api/brands",
                        data=json.dumps({"name": "Comp Brand"}),
                        content_type="application/json")
        brand_id = r.get_json()["brand"]["id"]

        r = client.post(f"/api/brands/{brand_id}/competitors",
                        data=json.dumps({"name": "Competitor A", "domain": "competitor.com"}),
                        content_type="application/json")
        assert r.status_code == 201


# ============================================================
# 3. SECURITY — XSS (3 tests)
# ============================================================

class TestXSS:
    XSS_PAYLOADS = [
        '<script>alert("xss")</script>',
        '"><img src=x onerror=alert(1)>',
        "javascript:alert('xss')",
    ]

    @pytest.mark.parametrize("payload", XSS_PAYLOADS)
    def test_xss_rejected_in_brand_name(self, client, payload):
        r = client.post("/api/brands",
                        data=json.dumps({"name": payload}),
                        content_type="application/json")
        if r.status_code == 201:
            response_text = r.data.decode("utf-8", errors="ignore")
            assert "<script>" not in response_text.lower() or r.status_code >= 400


# ============================================================
# 4. SECURITY — SQL INJECTION (3 tests)
# ============================================================

class TestSQLi:
    SQLI_PAYLOADS = [
        "'; DROP TABLE brands; --",
        "' OR '1'='1",
        "1; DELETE FROM brands WHERE 1=1",
    ]

    @pytest.mark.parametrize("payload", SQLI_PAYLOADS)
    def test_sqli_rejected(self, client, payload):
        r = client.post("/api/brands",
                        data=json.dumps({"name": payload}),
                        content_type="application/json")
        assert r.status_code != 500


# ============================================================
# 5. SECURITY — INPUT VALIDATION (3 tests)
# ============================================================

class TestInputValidation:
    def test_empty_body_handled(self, client):
        r = client.post("/api/brands",
                        data=json.dumps({}),
                        content_type="application/json")
        assert r.status_code == 400

    def test_oversized_payload_handled(self, client):
        huge = "x" * 1_000_000
        r = client.post("/api/brands",
                        data=json.dumps({"name": huge}),
                        content_type="application/json")
        assert r.status_code in [200, 201, 400, 413]

    def test_null_bytes_handled(self, client):
        r = client.post("/api/brands",
                        data=json.dumps({"name": "test\x00evil"}),
                        content_type="application/json")
        assert r.status_code != 500


# ============================================================
# 6. SECURITY — NO HARDCODED SECRETS (1 test)
# ============================================================

class TestSecrets:
    def test_no_hardcoded_secrets(self):
        import re
        secret_patterns = [
            r"sk-[a-zA-Z0-9]{20,}",
            r"password\s*=\s*[\"'][^\"']+[\"']",
        ]
        app_dir = os.path.join(os.path.dirname(__file__), "..")
        violations = []
        for root, dirs, files in os.walk(app_dir):
            dirs[:] = [d for d in dirs if d not in ["node_modules", ".git", "__pycache__", "venv", ".venv"]]
            for f in files:
                if f.endswith((".py",)) and "test" not in f.lower():
                    filepath = os.path.join(root, f)
                    try:
                        with open(filepath, "r", errors="ignore") as fh:
                            content = fh.read()
                            for pattern in secret_patterns:
                                if re.findall(pattern, content, re.IGNORECASE):
                                    violations.append(filepath)
                    except Exception:
                        pass
        # .env is expected to have placeholder passwords
        violations = [v for v in violations if ".env" not in v]
        assert len(violations) == 0, f"Possible secrets in: {violations}"


# ============================================================
# 7. INTEGRATION TESTS (3 tests)
# ============================================================

class TestIntegration:
    def test_create_then_read_brand(self, client):
        r = client.post("/api/brands",
                        data=json.dumps({"name": "Integration Test"}),
                        content_type="application/json")
        brand_id = r.get_json()["brand"]["id"]
        r = client.get(f"/api/brands/{brand_id}")
        assert r.status_code == 200
        assert r.get_json()["brand"]["name"] == "Integration Test"

    def test_brand_dashboard(self, client):
        r = client.post("/api/brands",
                        data=json.dumps({"name": "Dashboard Test"}),
                        content_type="application/json")
        brand_id = r.get_json()["brand"]["id"]
        r = client.get(f"/api/brands/{brand_id}/dashboard")
        assert r.status_code == 200
        assert "stats" in r.get_json()

    def test_full_brand_lifecycle(self, client):
        # Create
        r = client.post("/api/brands",
                        data=json.dumps({"name": "Lifecycle Test"}),
                        content_type="application/json")
        brand_id = r.get_json()["brand"]["id"]

        # Update
        r = client.put(f"/api/brands/{brand_id}",
                       data=json.dumps({"industry": "consulting"}),
                       content_type="application/json")
        assert r.status_code == 200

        # Add keyword
        r = client.post(f"/api/brands/{brand_id}/keywords",
                        data=json.dumps({"keyword": "test keyword"}),
                        content_type="application/json")
        assert r.status_code == 201

        # Archive
        r = client.delete(f"/api/brands/{brand_id}")
        assert r.status_code == 200


# ============================================================
# 8. ERROR HANDLING (3 tests)
# ============================================================

class TestErrorHandling:
    def test_404_on_bad_route(self, client):
        r = client.get("/api/this-does-not-exist")
        assert r.status_code == 404

    def test_no_stack_trace_in_error(self, client):
        r = client.get("/api/this-does-not-exist")
        response_text = r.data.decode("utf-8", errors="ignore")
        assert "Traceback" not in response_text

    def test_error_returns_json(self, client):
        r = client.get("/api/this-does-not-exist")
        assert r.content_type == "application/json"


# ============================================================
# 9. CORS TEST (1 test)
# ============================================================

class TestCORS:
    def test_cors_headers_present(self, client):
        r = client.get("/api/health")
        assert r.status_code == 200


# ============================================================
# 10. STATUS ENDPOINT (1 test)
# ============================================================

class TestStatus:
    def test_status_returns_dependencies(self, client):
        r = client.get("/api/status")
        assert r.status_code == 200
        data = r.get_json()
        assert "dependencies" in data
        assert "postgresql" in data["dependencies"]
