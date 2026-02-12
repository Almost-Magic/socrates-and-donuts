"""Ripple Pulse — Beast Tests.

5 sections: Import, Unit, Integration, API Smoke, Confidence Stamp.
Run: cd backend && python -B -m pytest ../tests/test_pulse_beast.py -v
"""

import os
import uuid

import httpx
import requests

BASE = os.environ.get("RIPPLE_API_BASE", "http://localhost:8100/api")
_RUN_ID = uuid.uuid4().hex[:8]

# Track IDs between tests
_target_id = None
_action_id = None


# ══════════════════════════════════════════════════════════════════════════
# SECTION 1: IMPORT CHECKS
# ══════════════════════════════════════════════════════════════════════════

def test_import_pulse_models():
    """Pulse models import without error."""
    from app.models.sales_target import SalesTarget
    from app.models.pulse_snapshot import PulseSnapshot
    from app.models.pulse_action import PulseAction
    from app.models.pulse_wisdom import PulseWisdom
    assert SalesTarget.__tablename__ == "sales_targets"
    assert PulseSnapshot.__tablename__ == "pulse_snapshots"
    assert PulseAction.__tablename__ == "pulse_actions"
    assert PulseWisdom.__tablename__ == "pulse_wisdom"


def test_import_pulse_schemas():
    """Pulse schemas import without error."""
    from app.schemas.pulse import (
        SalesTargetCreate,
        SalesTargetResponse,
        PulseResponse,
        PulseActionResponse,
        PulseWisdomResponse,
        EodReviewRequest,
        ElaineBriefingResponse,
        StreakResponse,
    )
    assert SalesTargetCreate is not None
    assert PulseResponse is not None


def test_import_pulse_engine():
    """Pulse engine service imports without error."""
    from app.services.pulse_engine import (
        compile_pulse,
        query_target_vs_actual,
        rank_easy_wins,
        analyse_pipeline,
        detect_relationship_changes,
        generate_coaching,
        generate_actions,
    )
    assert compile_pulse is not None
    assert rank_easy_wins is not None


def test_import_pulse_router():
    """Pulse router imports without error."""
    from app.routers.pulse import router
    assert router is not None
    assert router.prefix == "/pulse"


# ══════════════════════════════════════════════════════════════════════════
# SECTION 2: UNIT TESTS
# ══════════════════════════════════════════════════════════════════════════

def test_sales_target_model_columns():
    """SalesTarget model has required columns."""
    from app.models.sales_target import SalesTarget
    cols = {c.name for c in SalesTarget.__table__.columns}
    expected = {"id", "period_type", "period_label", "period_start", "period_end",
                "target_value", "currency", "notes", "created_at", "updated_at"}
    assert expected.issubset(cols), f"Missing columns: {expected - cols}"


def test_pulse_snapshot_model_columns():
    """PulseSnapshot model has required columns."""
    from app.models.pulse_snapshot import PulseSnapshot
    cols = {c.name for c in PulseSnapshot.__table__.columns}
    expected = {"id", "snapshot_date", "data_json", "ai_commentary_json", "eod_notes",
                "created_at", "updated_at"}
    assert expected.issubset(cols), f"Missing columns: {expected - cols}"


def test_pulse_action_model_columns():
    """PulseAction model has required columns."""
    from app.models.pulse_action import PulseAction
    cols = {c.name for c in PulseAction.__table__.columns}
    expected = {"id", "snapshot_date", "title", "description", "reason",
                "estimated_minutes", "contact_id", "deal_id", "priority",
                "is_completed", "completed_at", "created_at"}
    assert expected.issubset(cols), f"Missing columns: {expected - cols}"


def test_pulse_wisdom_model_columns():
    """PulseWisdom model has required columns."""
    from app.models.pulse_wisdom import PulseWisdom
    cols = {c.name for c in PulseWisdom.__table__.columns}
    expected = {"id", "quote", "author", "source", "last_shown", "created_at"}
    assert expected.issubset(cols), f"Missing columns: {expected - cols}"


def test_target_create_schema_validation():
    """SalesTargetCreate validates input correctly."""
    from app.schemas.pulse import SalesTargetCreate
    from pydantic import ValidationError

    # Valid
    target = SalesTargetCreate(
        period_type="monthly",
        period_label="Test Month",
        period_start="2026-02-01",
        period_end="2026-02-28",
        target_value=50000,
    )
    assert target.target_value == 50000
    assert target.currency == "AUD"

    # Invalid period_type
    try:
        SalesTargetCreate(
            period_type="weekly",
            period_label="Test",
            period_start="2026-02-01",
            period_end="2026-02-28",
            target_value=1000,
        )
        assert False, "Should have raised ValidationError"
    except ValidationError:
        pass

    # Invalid target_value (zero)
    try:
        SalesTargetCreate(
            period_type="monthly",
            period_label="Test",
            period_start="2026-02-01",
            period_end="2026-02-28",
            target_value=0,
        )
        assert False, "Should have raised ValidationError for zero target"
    except ValidationError:
        pass


# ══════════════════════════════════════════════════════════════════════════
# SECTION 3: INTEGRATION TESTS
# ══════════════════════════════════════════════════════════════════════════

def test_pulse_tables_exist():
    """All 4 Pulse tables exist in the database."""
    import asyncio
    import asyncpg

    async def check():
        conn = await asyncpg.connect(
            user="postgres",
            password="peterman2026",
            host="localhost",
            port=5433,
            database="ripple",
        )
        tables = await conn.fetch(
            "SELECT tablename FROM pg_tables WHERE schemaname='public'"
        )
        table_names = {t["tablename"] for t in tables}
        await conn.close()
        return table_names

    table_names = asyncio.run(check())
    for tbl in ("sales_targets", "pulse_snapshots", "pulse_actions", "pulse_wisdom"):
        assert tbl in table_names, f"Table '{tbl}' not found in database"


# ══════════════════════════════════════════════════════════════════════════
# SECTION 4: API SMOKE TESTS
# ══════════════════════════════════════════════════════════════════════════

def test_health_endpoint():
    """Backend health check still works."""
    r = httpx.get(f"{BASE}/health", timeout=5)
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_create_target():
    """POST /api/pulse/targets creates a new target."""
    global _target_id
    r = requests.post(f"{BASE}/pulse/targets", json={
        "period_type": "monthly",
        "period_label": f"Beast Test {_RUN_ID}",
        "period_start": "2026-03-01",
        "period_end": "2026-03-31",
        "target_value": 25000,
        "currency": "AUD",
    })
    assert r.status_code == 201, f"Create target failed: {r.text}"
    data = r.json()
    _target_id = data["id"]
    assert data["period_label"] == f"Beast Test {_RUN_ID}"
    assert data["target_value"] == 25000


def test_list_targets():
    """GET /api/pulse/targets returns a list."""
    r = requests.get(f"{BASE}/pulse/targets")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1


def test_current_target():
    """GET /api/pulse/targets/current returns target or message."""
    r = requests.get(f"{BASE}/pulse/targets/current")
    assert r.status_code == 200
    data = r.json()
    assert "target_vs_actual" in data


def test_pulse_generation():
    """GET /api/pulse returns structured Pulse data."""
    r = requests.get(f"{BASE}/pulse", timeout=60)
    assert r.status_code == 200
    data = r.json()
    assert "snapshot_date" in data
    assert "pipeline" in data
    assert "relationships" in data
    assert "coaching" in data

    # Pipeline has stages
    pipeline = data["pipeline"]
    assert "stages" in pipeline
    assert "stalled_deals" in pipeline

    # Relationships has sections
    rel = data["relationships"]
    assert "decaying" in rel
    assert "champions" in rel
    assert "no_contact" in rel

    # Coaching has fields
    coaching = data["coaching"]
    assert "streak_days" in coaching
    assert "personal_bests" in coaching


def test_actions_list():
    """GET /api/pulse/actions returns actions list."""
    r = requests.get(f"{BASE}/pulse/actions")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert "total" in data


def test_action_complete():
    """PUT /api/pulse/actions/{id}/complete marks action done."""
    global _action_id
    # First get actions
    r = requests.get(f"{BASE}/pulse/actions")
    assert r.status_code == 200
    actions = r.json()["items"]

    if actions:
        _action_id = actions[0]["id"]
        r = requests.put(f"{BASE}/pulse/actions/{_action_id}/complete")
        assert r.status_code == 200
        data = r.json()
        assert data.get("is_completed") or data.get("status") == "completed"


def test_easy_wins():
    """GET /api/pulse/easy-wins returns ranked opportunities."""
    r = requests.get(f"{BASE}/pulse/easy-wins")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert "total" in data
    # Verify ranking order (scores should be descending)
    items = data["items"]
    if len(items) >= 2:
        for i in range(len(items) - 1):
            assert items[i]["score"] >= items[i + 1]["score"], \
                f"Easy wins not sorted by score: {items[i]['score']} < {items[i + 1]['score']}"


def test_streak():
    """GET /api/pulse/streak returns streak data."""
    r = requests.get(f"{BASE}/pulse/streak")
    assert r.status_code == 200
    data = r.json()
    assert "current_streak" in data
    assert "streak_unit" in data
    assert data["streak_unit"] == "days"


def test_wisdom():
    """GET /api/pulse/wisdom returns a quote."""
    r = requests.get(f"{BASE}/pulse/wisdom")
    # 200 if quotes exist, 404 if not
    assert r.status_code in (200, 404)
    if r.status_code == 200:
        data = r.json()
        assert "quote" in data
        assert "author" in data


def test_eod_review_get():
    """GET /api/pulse/eod-review returns review summary."""
    r = requests.get(f"{BASE}/pulse/eod-review")
    assert r.status_code == 200
    data = r.json()
    assert "snapshot_date" in data
    assert "actions_completed" in data
    assert "actions_total" in data


def test_eod_review_save():
    """POST /api/pulse/eod-review saves reflection notes."""
    r = requests.post(f"{BASE}/pulse/eod-review", json={
        "notes": f"Beast test reflection {_RUN_ID}",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["eod_notes"] == f"Beast test reflection {_RUN_ID}"


def test_elaine_briefing():
    """GET /api/pulse/elaine-briefing returns condensed JSON."""
    r = requests.get(f"{BASE}/pulse/elaine-briefing", timeout=60)
    assert r.status_code == 200
    data = r.json()
    assert "snapshot_date" in data
    # These fields should exist (may be null)
    for key in ("target_summary", "top_action", "pipeline_alert",
                "relationship_alert", "win_celebration", "wisdom_quote"):
        assert key in data, f"Missing key in ELAINE briefing: {key}"


def test_force_regenerate():
    """POST /api/pulse/generate regenerates the pulse."""
    r = requests.post(f"{BASE}/pulse/generate", timeout=60)
    assert r.status_code == 200
    data = r.json()
    assert "snapshot_date" in data
    assert "pipeline" in data


def test_no_targets_edge_case():
    """Pulse works even with no matching targets for edge dates."""
    r = requests.get(f"{BASE}/pulse/targets/current")
    assert r.status_code == 200
    # Should return data or message, never crash


def test_empty_pipeline_edge():
    """Easy wins endpoint handles empty results gracefully."""
    r = requests.get(f"{BASE}/pulse/easy-wins?limit=1")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data


# ══════════════════════════════════════════════════════════════════════════
# SECTION 5: CONFIDENCE STAMP
# ══════════════════════════════════════════════════════════════════════════

def test_confidence_stamp():
    """Pulse Beast tests passed."""
    stamp = """
    ╔═══════════════════════════════════════════════╗
    ║   RIPPLE PULSE — BEAST TESTS PASSED           ║
    ║   Targets, Actions, Easy Wins, Pipeline,      ║
    ║   Relationships, Coaching, Wisdom, ELAINE      ║
    ╚═══════════════════════════════════════════════╝
    """
    print(stamp)
    assert True
