"""
Elaine v4 — Phase 12+: Complete System with Orchestrator + Morning Brief
Flask application entry point.

16 modules + Orchestrator + Phase 5 Morning Briefing + APScheduler.
Jinja2 templates → Ollama LLM → SQLite storage.
Almost Magic Tech Lab
"""

from flask import Flask, jsonify, request
import json
import logging
import os
import sqlite3
import subprocess
import threading
from datetime import datetime, timedelta
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from config import *

# Load .env file if present (for ELEVENLABS_API_KEY etc.)
_env_path = Path(__file__).parent / ".env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

try:
    import requests as http_requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("elaine.app")


OLLAMA_URL = "http://localhost:9000/api/generate"
OLLAMA_MODEL = "llama3.1:8b"  # Morning Brief only — chat uses qwen3:4b (see api_routes_chat.py)
ELAINE_DIR = Path(__file__).parent.resolve()
BRIEFING_TEMPLATE_DIR = ELAINE_DIR / "templates" / "briefing"
LLM_DB_PATH = Path.home() / ".elaine" / "briefing.db"


def _call_ollama(prompt, model=OLLAMA_MODEL, timeout=300):
    """Send prompt to Ollama and return the response text.
    Returns (text, True) on success, (fallback_text, False) on failure."""
    if not HAS_REQUESTS:
        return prompt, False
    try:
        resp = http_requests.post(
            OLLAMA_URL,
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=timeout,
        )
        resp.raise_for_status()
        return resp.json().get("response", ""), True
    except Exception as exc:
        logger.warning("Ollama call failed (%s) — using raw template as fallback", exc)
        return prompt, False


def _render_template(template_name, **kwargs):
    """Render a Jinja2 template from templates/briefing/."""
    env = Environment(loader=FileSystemLoader(str(BRIEFING_TEMPLATE_DIR)))
    tpl = env.get_template(template_name)
    return tpl.render(**kwargs)


def _init_llm_tables():
    """Ensure the llm_briefings table exists in briefing.db."""
    LLM_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(LLM_DB_PATH))
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS llm_briefings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        briefing_type TEXT NOT NULL,
        raw_data TEXT,
        rendered_prompt TEXT,
        llm_response TEXT,
        ollama_ok INTEGER DEFAULT 0,
        generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.commit()
    conn.close()


_init_llm_tables()


def _store_llm_briefing(briefing_type, raw_data, rendered_prompt, llm_response, ollama_ok):
    """Store an LLM-generated briefing in briefing.db."""
    conn = sqlite3.connect(str(LLM_DB_PATH))
    c = conn.cursor()
    c.execute(
        "INSERT INTO llm_briefings (briefing_type, raw_data, rendered_prompt, llm_response, ollama_ok) VALUES (?, ?, ?, ?, ?)",
        (briefing_type, json.dumps(raw_data, default=str), rendered_prompt, llm_response, int(ollama_ok)),
    )
    conn.commit()
    conn.close()


def _get_latest_llm_briefing(briefing_type):
    """Return the most recent LLM briefing of the given type.
    Prefers Ollama-completed entries from today; falls back to most recent."""
    conn = sqlite3.connect(str(LLM_DB_PATH))
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    # Try Ollama-completed entry from last 24 hours first
    yesterday = (datetime.now() - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
    c.execute(
        "SELECT llm_response, ollama_ok, generated_at, raw_data FROM llm_briefings "
        "WHERE briefing_type = ? AND ollama_ok = 1 AND generated_at >= ? "
        "ORDER BY generated_at DESC LIMIT 1",
        (briefing_type, yesterday),
    )
    row = c.fetchone()
    if not row:
        # Fall back to most recent entry of any kind
        c.execute(
            "SELECT llm_response, ollama_ok, generated_at, raw_data FROM llm_briefings "
            "WHERE briefing_type = ? ORDER BY generated_at DESC LIMIT 1",
            (briefing_type,),
        )
        row = c.fetchone()
    conn.close()
    if row:
        return {
            "briefing": row["llm_response"],
            "ollama_ok": bool(row["ollama_ok"]),
            "generated_at": row["generated_at"],
            "raw_data": json.loads(row["raw_data"]) if row["raw_data"] else {},
        }
    return None


def create_app():
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False

    # ── Initialise All Modules ───────────────────────────────────

    # Phase 8a: Thinking Frameworks (loaded first)
    from modules.thinking.engine import ThinkingFrameworksEngine
    thinking_engine = ThinkingFrameworksEngine()

    # Phase 7: Gravity Engine v2
    from modules.gravity_v2.gravity_field import GravityField
    from modules.gravity_v2.consequence_engine import ConsequenceEngine
    from modules.gravity_v2.learning import LearningEngine
    from modules.gravity_v2.drift_detector import DriftDetector
    gravity_field = GravityField()
    consequence_engine = ConsequenceEngine()
    learning_engine = LearningEngine()
    drift_detector = DriftDetector()

    # Phase 7: Constellation v2
    from modules.constellation.poi_engine import POIEngine
    from modules.constellation.network_intelligence import NetworkIntelligence
    from modules.constellation.reciprocity import ReciprocityEngine
    from modules.constellation.poi_profiles import POIProfile
    poi_engine = POIEngine()
    network_intel = NetworkIntelligence()
    reciprocity_engine = ReciprocityEngine()
    poi_profiles = POIProfile()

    # Phase 8: Cartographer v2
    from modules.cartographer.territory_map import TerritoryMap
    from modules.cartographer.discovery_engine import DiscoveryEngine
    territory_map = TerritoryMap()
    discovery_engine = DiscoveryEngine()

    # Phase 8: Amplifier v2
    from modules.amplifier.content_engine import ContentEngine
    content_engine = ContentEngine(thinking_engine=thinking_engine)

    # Phase 9: Sentinel v2
    from modules.sentinel.trust_engine import TrustEngine
    trust_engine = TrustEngine(thinking_engine=thinking_engine)

    # Phase 10: Chronicle v2
    from modules.chronicle.meeting_engine import MeetingEngine
    meeting_engine = MeetingEngine()

    # Phase 10: Voice
    from modules.chronicle.voice import VoiceBriefingFormatter
    voice_formatter = VoiceBriefingFormatter()

    # Phase 11: Innovator + Beast
    from modules.innovator.engine import InnovationEngine
    innovation_engine = InnovationEngine()

    # Phase 14: Learning Radar
    from modules.learning_radar import LearningRadar
    learning_radar = LearningRadar()

    # Phase 14b: Communication + Strategic Engines
    from modules.communication import CommunicationEngine
    communication_engine = CommunicationEngine()

    from modules.strategic import StrategicEngine
    strategic_engine = StrategicEngine()

    # Phase 15: Compassion Engine
    from modules.compassion import CompassionEngine
    compassion_engine = CompassionEngine()

    # Phase 16: Gatekeeper
    from modules.gatekeeper import Gatekeeper
    gatekeeper = Gatekeeper(
        sentinel=trust_engine,
        compassion=compassion_engine,
        communication=communication_engine,
    )

    # Phase 12: Orchestrator (wires everything together)
    from modules.orchestrator import Orchestrator
    orchestrator = Orchestrator(
        gravity_field=gravity_field,
        poi_engine=poi_engine,
        territory_map=territory_map,
        discovery_engine=discovery_engine,
        content_engine=content_engine,
        trust_engine=trust_engine,
        meeting_engine=meeting_engine,
        innovation_engine=innovation_engine,
        thinking_engine=thinking_engine,
        voice_formatter=voice_formatter,
        learning_radar=learning_radar,
        communication_engine=communication_engine,
        strategic_engine=strategic_engine,
        compassion_engine=compassion_engine,
    )

    # Phase 5: Morning Briefing Engine (news, LinkedIn, POI, deadlines)
    from modules.phase5_briefing.morning_briefing import MorningBriefingEngine
    briefing_engine = MorningBriefingEngine()

    # ── Register All Blueprints ──────────────────────────────────

    # Phase 7
    from api_routes import create_gravity_routes, create_constellation_routes
    app.register_blueprint(create_gravity_routes(gravity_field, consequence_engine, learning_engine, drift_detector))
    app.register_blueprint(create_constellation_routes(poi_engine, network_intel, reciprocity_engine, poi_profiles))

    # Phase 8 + 8a
    from api_routes_phase8 import create_thinking_routes, create_cartographer_routes, create_amplifier_routes
    app.register_blueprint(create_thinking_routes(thinking_engine))
    app.register_blueprint(create_cartographer_routes(territory_map, discovery_engine))
    app.register_blueprint(create_amplifier_routes(content_engine))

    # Phase 9
    from api_routes_phase9 import create_sentinel_routes
    app.register_blueprint(create_sentinel_routes(trust_engine))

    # Phase 10
    from api_routes_phase10 import create_chronicle_routes, create_voice_routes
    app.register_blueprint(create_chronicle_routes(meeting_engine))
    app.register_blueprint(create_voice_routes(voice_formatter))

    # Phase 11
    from api_routes_phase11 import create_innovator_routes
    app.register_blueprint(create_innovator_routes(innovation_engine))

    # Phase 12
    from api_routes_phase12 import create_orchestrator_routes
    app.register_blueprint(create_orchestrator_routes(orchestrator))

    # Phase 14
    from api_routes_phase14 import create_learning_routes
    app.register_blueprint(create_learning_routes(learning_radar))

    # Phase 14b
    from api_routes_phase14b import create_framework_routes
    app.register_blueprint(create_framework_routes(communication_engine, strategic_engine, orchestrator))

    # Phase 14c
    from api_routes_phase14c import create_compassion_routes
    app.register_blueprint(create_compassion_routes(compassion_engine))

    # Phase 16
    from api_routes_phase16 import create_gatekeeper_routes
    app.register_blueprint(create_gatekeeper_routes(gatekeeper))

    # Chat + Tool Registry + Service Health
    from api_routes_chat import create_chat_routes, prewarm_chat_model
    app.register_blueprint(create_chat_routes())
    prewarm_chat_model()  # background thread — loads qwen3:4b into VRAM

    # Phase 5: Briefing, POI, Resilience, Memory routes
    import modules.phase5_routes as _p5
    _p5._briefing = briefing_engine          # share single engine instance
    app.register_blueprint(_p5.phase5_bp)

    # Stabilisation: health, modules, frustration, briefing alias
    from api_routes_stabilisation import create_stabilisation_routes

    def _get_modules_status():
        return {
            "thinking_frameworks": {"status": "active", "analyses": thinking_engine.status()["total_analyses"]},
            "gravity_v2": {"status": "active", "items": gravity_field.active_item_count()},
            "constellation_v2": {"status": "active", "pois": len(poi_engine.pois)},
            "cartographer_v2": {"status": "active", "territories": len(territory_map.territories)},
            "amplifier_v2": {"status": "active", "content_items": len(content_engine.items)},
            "sentinel_v2": {"status": "active", "audits": len(trust_engine.audits)},
            "chronicle_v2": {"status": "active", "meetings": len(meeting_engine.meetings)},
            "voice": {"status": "active", "voice_id": ELEVENLABS_VOICE_ID},
            "innovator": {"status": "active", "opportunities": len(innovation_engine.opportunities)},
            "beast": {"status": "active", "briefs": len(innovation_engine.research_briefs)},
            "orchestrator": {"status": "active", "cascades": len(orchestrator._cascade_log)},
            "learning_radar": {"status": "active", "interests": len(learning_radar.interests)},
            "communication": {"status": "active", "frameworks": 7},
            "strategic": {"status": "active", "frameworks": 8},
            "compassion": {"status": "active", "wellbeing": compassion_engine.wellbeing.level.value},
            "gatekeeper": {"status": "active", "checked": gatekeeper._items_checked},
        }

    def _morning_briefing_data():
        gravity_snap = gravity_field.snapshot()
        constellation_data = poi_engine.get_morning_briefing_data()
        drift = drift_detector.analyse()
        nudges = gravity_field.governors.get_nudges(gravity_field.items)
        rest = gravity_field.governors.should_suggest_rest(gravity_field.items, 8.0)
        cart_briefing = discovery_engine.get_morning_briefing()
        amp_briefing = content_engine.get_morning_briefing_data()
        sentinel_data = trust_engine.get_learning_report()
        chronicle_data = meeting_engine.get_morning_briefing_data()
        innovator_data = innovation_engine.get_morning_briefing_data()
        learning_data = learning_radar.get_morning_briefing_data()
        return jsonify({
            "gravity": {
                "red_giants": gravity_snap.red_giants,
                "top_3": gravity_snap.top_3_ids,
                "trust_debt_aud": gravity_snap.trust_debt_total_aud,
                "collisions": len(gravity_snap.collisions),
            },
            "constellation": constellation_data,
            "cartographer": cart_briefing,
            "amplifier": amp_briefing,
            "sentinel": sentinel_data,
            "chronicle": chronicle_data,
            "innovator": innovator_data,
            "learning_radar": learning_data,
            "drift": {
                "alert": drift.drift_alert,
                "severity": drift.drift_severity,
                "recommendation": drift.recommendation,
            },
            "thinking_frameworks": thinking_engine.status(),
            "orchestrator": {"cascades": len(orchestrator._cascade_log)},
            "governor_nudges": nudges,
            "rest_suggestion": rest,
        })

    app.register_blueprint(
        create_stabilisation_routes(_get_modules_status, _morning_briefing_data)
    )

    # Wisdom & Philosophy routes (proxies to Wisdom Quotes API :3350)
    from api_routes_wisdom import bp as wisdom_bp
    app.register_blueprint(wisdom_bp)

    # ── Combined Briefing Helper (modules + Phase 5) ─────────────

    def _collect_briefing_data():
        """Collect all module + Phase 5 data into a dict (no LLM call)."""
        now = datetime.now()
        hour = now.hour
        greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"

        # Module data
        gravity_snap = gravity_field.snapshot()
        constellation_data = poi_engine.get_morning_briefing_data()
        drift = drift_detector.analyse()
        nudges = gravity_field.governors.get_nudges(gravity_field.items)
        rest = gravity_field.governors.should_suggest_rest(gravity_field.items, 8.0)
        cart_briefing = discovery_engine.get_morning_briefing()
        amp_briefing = content_engine.get_morning_briefing_data()
        sentinel_data = trust_engine.get_learning_report()
        chronicle_data = meeting_engine.get_morning_briefing_data()
        innovator_data = innovation_engine.get_morning_briefing_data()
        learning_data = learning_radar.get_morning_briefing_data()

        # Phase 5 data (news, LinkedIn, POI — skip email/calendar)
        try:
            news = briefing_engine._get_relevant_news()
        except Exception:
            news = {"title": "News", "items": [], "error": "unavailable"}
        try:
            linkedin = briefing_engine._get_linkedin_relevant()
        except Exception:
            linkedin = {"title": "LinkedIn & Industry", "items": [], "error": "unavailable"}
        try:
            poi = briefing_engine._get_poi_briefing()
        except Exception:
            poi = {"title": "People of Interest", "items": []}
        try:
            deadlines = briefing_engine._get_deadlines()
        except Exception:
            deadlines = {"title": "Deadlines & Due Dates", "items": []}
        try:
            actions = briefing_engine._get_pending_actions()
        except Exception:
            actions = {"title": "Pending Action Items", "items": []}

        return {
            "greeting": f"{greeting}, Mani.",
            "generated_at": now.isoformat(),
            "date": now.strftime("%A, %d %B %Y"),
            "gravity": {
                "red_giants": gravity_snap.red_giants,
                "top_3": gravity_snap.top_3_ids,
                "trust_debt_aud": gravity_snap.trust_debt_total_aud,
                "collisions": len(gravity_snap.collisions),
            },
            "constellation": constellation_data,
            "cartographer": cart_briefing,
            "amplifier": amp_briefing,
            "sentinel": sentinel_data,
            "chronicle": chronicle_data,
            "innovator": innovator_data,
            "learning_radar": learning_data,
            "drift": {
                "alert": drift.drift_alert,
                "severity": drift.drift_severity,
                "recommendation": drift.recommendation,
            },
            "thinking_frameworks": thinking_engine.status(),
            "orchestrator": {"cascades": len(orchestrator._cascade_log)},
            "governor_nudges": nudges,
            "rest_suggestion": rest,
            "news": news,
            "linkedin": linkedin,
            "people": poi,
            "deadlines": deadlines,
            "action_items": actions,
        }

    def _render_briefing_prompt(combined, template_name="morning_brief.j2"):
        """Render the Jinja2 template with collected data."""
        now = datetime.now()
        try:
            prompt = _render_template(
                template_name,
                current_date=now.strftime("%d %B %Y"),
                day_of_week=now.strftime("%A"),
                date_formatted=now.strftime("%d %B %Y"),
                **combined,
            )
            return prompt
        except Exception as exc:
            logger.error("Jinja2 render failed for %s: %s", template_name, exc)
            return f"Generate a morning brief for Mani Padisetti on {now.strftime('%A %d %B %Y')}."

    def _ollama_background(briefing_type, combined, prompt):
        """Send prompt to Ollama in a background thread and store the result."""
        try:
            llm_response, ollama_ok = _call_ollama(prompt)
            _store_llm_briefing(briefing_type, combined, prompt, llm_response, ollama_ok)
            logger.info("Background Ollama %s complete (ok=%s, len=%d)", briefing_type, ollama_ok, len(llm_response))
        except Exception as exc:
            logger.error("Background Ollama %s failed: %s", briefing_type, exc)

    def _generate_combined_briefing(sync=False):
        """Collect data, render Jinja2, send to Ollama (async), store result.
        If sync=True, waits for Ollama (used by scheduler). Otherwise returns immediately."""
        combined = _collect_briefing_data()
        now = datetime.now()

        # Store raw data to Phase 5 DB
        try:
            briefing_engine._store_briefing(combined)
        except Exception as exc:
            logger.warning("Failed to store raw briefing: %s", exc)

        prompt = _render_briefing_prompt(combined, "morning_brief.j2")

        if sync:
            # Scheduler path: wait for Ollama (runs in background thread already)
            llm_response, ollama_ok = _call_ollama(prompt)
            _store_llm_briefing("morning_brief", combined, prompt, llm_response, ollama_ok)
            logger.info("Scheduled morning briefing generated (ollama=%s)", ollama_ok)
            return {"briefing": llm_response, "ollama_ok": ollama_ok, "generated_at": now.isoformat(), "raw_data": combined}

        # HTTP path: store the rendered prompt as fallback immediately, fire Ollama in background
        _store_llm_briefing("morning_brief", combined, prompt, prompt, False)
        thread = threading.Thread(target=_ollama_background, args=("morning_brief", combined, prompt), daemon=True)
        thread.start()

        logger.info("Morning briefing dispatched to Ollama (background)")
        return {
            "briefing": prompt,
            "ollama_ok": False,
            "ollama_pending": True,
            "generated_at": now.isoformat(),
            "raw_data": combined,
        }

    def _generate_weekly_prep(sync=False):
        """Collect data, render weekly_prep.j2, send to Ollama, store result."""
        combined = _collect_briefing_data()
        now = datetime.now()
        monday = now - timedelta(days=now.weekday())
        friday = monday + timedelta(days=4)

        try:
            prompt = _render_template(
                "weekly_prep.j2",
                week_start_date=monday.strftime("%d %B %Y"),
                week_end_date=friday.strftime("%d %B %Y"),
                **combined,
            )
        except Exception as exc:
            logger.error("Weekly prep Jinja2 render failed: %s", exc)
            prompt = f"Generate a weekly prep for Mani Padisetti, week of {monday.strftime('%d %B')} to {friday.strftime('%d %B %Y')}."

        if sync:
            llm_response, ollama_ok = _call_ollama(prompt)
            _store_llm_briefing("weekly_prep", combined, prompt, llm_response, ollama_ok)
            logger.info("Scheduled weekly prep generated (ollama=%s)", ollama_ok)
            return {"briefing": llm_response, "ollama_ok": ollama_ok, "generated_at": now.isoformat(), "raw_data": combined}

        _store_llm_briefing("weekly_prep", combined, prompt, prompt, False)
        thread = threading.Thread(target=_ollama_background, args=("weekly_prep", combined, prompt), daemon=True)
        thread.start()

        logger.info("Weekly prep dispatched to Ollama (background)")
        return {
            "briefing": prompt,
            "ollama_ok": False,
            "ollama_pending": True,
            "generated_at": now.isoformat(),
            "raw_data": combined,
        }

    # ── APScheduler — Morning Brief 07:00 + Weekly Prep Mon 06:30 ─

    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger

    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(
        lambda: _generate_combined_briefing(sync=True),
        CronTrigger(hour=7, minute=0, timezone="Australia/Sydney"),
        id="morning_briefing",
        replace_existing=True,
    )
    scheduler.add_job(
        lambda: _generate_weekly_prep(sync=True),
        CronTrigger(day_of_week="mon", hour=6, minute=30, timezone="Australia/Sydney"),
        id="weekly_prep",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("APScheduler started — Morning Brief daily 07:00, Weekly Prep Monday 06:30 (Australia/Sydney)")

    # ── System Status ────────────────────────────────────────────

    @app.route("/api/status", methods=["GET"])
    def status():
        return jsonify({
            "name": ELAINE_NAME,
            "version": f"{ELAINE_VERSION}-phase14",
            "owner": OWNER_NAME,
            "company": COMPANY_NAME,
            "voice_id": ELEVENLABS_VOICE_ID,
            "modules": {
                "thinking_frameworks": {"status": "active", "analyses": thinking_engine.status()["total_analyses"]},
                "gravity_v2": {"status": "active", "items": gravity_field.active_item_count()},
                "constellation_v2": {"status": "active", "pois": len(poi_engine.pois)},
                "cartographer_v2": {"status": "active", "territories": len(territory_map.territories)},
                "amplifier_v2": {"status": "active", "content_items": len(content_engine.items)},
                "sentinel_v2": {"status": "active", "audits": len(trust_engine.audits)},
                "chronicle_v2": {"status": "active", "meetings": len(meeting_engine.meetings)},
                "voice": {"status": "active", "voice_id": ELEVENLABS_VOICE_ID},
                "innovator": {"status": "active", "opportunities": len(innovation_engine.opportunities)},
                "beast": {"status": "active", "briefs": len(innovation_engine.research_briefs)},
                "orchestrator": {"status": "active", "cascades": len(orchestrator._cascade_log)},
                "learning_radar": {"status": "active", "interests": len(learning_radar.interests), "connections": len(learning_radar.connections)},
                "communication": {"status": "active", "frameworks": 7},
                "strategic": {"status": "active", "frameworks": 8},
                "compassion": {"status": "active", "wellbeing": compassion_engine.wellbeing.level.value},
                "gatekeeper": {"status": "active", "checked": gatekeeper._items_checked, "held": gatekeeper._items_held},
            },
            "phase": "14 — Learning Radar",
        })

    # ── Combined Morning Briefing ────────────────────────────────

    @app.route("/api/morning-briefing", methods=["GET"])
    def morning_briefing():
        """Generate and return the full combined briefing (modules + Phase 5 + LLM)."""
        return jsonify(_generate_combined_briefing())

    @app.route("/api/morning-briefing/latest", methods=["GET"])
    def morning_briefing_latest():
        """Return the most recent LLM-generated morning brief without regenerating."""
        result = _get_latest_llm_briefing("morning_brief")
        if result:
            return jsonify(result)
        # Fallback: try the raw Phase 5 store
        try:
            conn = sqlite3.connect(briefing_engine.db_path)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT briefing_data, generated_at FROM briefings ORDER BY generated_at DESC LIMIT 1")
            row = c.fetchone()
            conn.close()
            if row:
                data = json.loads(row["briefing_data"])
                return jsonify({"briefing": data.get("greeting", "No LLM brief yet."), "ollama_ok": False, "generated_at": row["generated_at"], "raw_data": data})
        except Exception:
            pass
        return jsonify({"error": "No briefing stored yet. Hit POST /api/morning-briefing/generate to create one."}), 404

    @app.route("/api/morning-briefing/generate", methods=["POST"])
    def morning_briefing_generate():
        """Trigger a morning briefing now (for testing). Renders Jinja2 → Ollama → stores."""
        result = _generate_combined_briefing()
        return jsonify(result)

    # ── Weekly Prep ────────────────────────────────────────────────

    @app.route("/api/weekly-prep/latest", methods=["GET"])
    def weekly_prep_latest():
        """Return the most recent LLM-generated weekly prep."""
        result = _get_latest_llm_briefing("weekly_prep")
        if result:
            return jsonify(result)
        return jsonify({"error": "No weekly prep stored yet. Hit POST /api/weekly-prep/generate to create one."}), 404

    @app.route("/api/weekly-prep/generate", methods=["POST"])
    def weekly_prep_generate():
        """Trigger weekly prep now (for testing)."""
        result = _generate_weekly_prep()
        return jsonify(result)

    # ── Philosophy Research ────────────────────────────────────────

    @app.route("/api/research/philosophy", methods=["POST"])
    def philosophy_research():
        """Run philosophy corpus search + Ollama synthesis.
        Body: {"question": "...", "filter_category": "optional"}
        """
        data = request.get_json(force=True)
        question = data.get("question", "").strip()
        if not question:
            return jsonify({"error": "question is required"}), 400
        filter_category = data.get("filter_category", "")

        # Try running philosophy_search.py if it exists
        passages = []
        search_script = ELAINE_DIR / "philosophy_search.py"
        if search_script.exists():
            try:
                cmd = ["python", str(search_script), "--query", question]
                if filter_category:
                    cmd.extend(["--category", filter_category])
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=str(ELAINE_DIR))
                if proc.returncode == 0 and proc.stdout.strip():
                    passages = json.loads(proc.stdout)
            except Exception as exc:
                logger.warning("philosophy_search.py failed: %s", exc)

        # Render template
        try:
            prompt = _render_template(
                "philosophy_research.j2",
                question=question,
                filter_category=filter_category,
                passages=passages,
            )
        except Exception as exc:
            logger.error("Philosophy template render failed: %s", exc)
            prompt = f"Answer this philosophy question for Mani Padisetti in Australian English: {question}"

        llm_response, ollama_ok = _call_ollama(prompt, timeout=90)
        return jsonify({
            "question": question,
            "filter_category": filter_category,
            "synthesis": llm_response,
            "ollama_ok": ollama_ok,
            "passages_used": len(passages),
        })

    # ── Voice Morning Briefing ───────────────────────────────────

    @app.route("/api/morning-briefing/voice", methods=["GET"])
    def morning_briefing_voice():
        gravity_snap = gravity_field.snapshot()
        cart_briefing = discovery_engine.get_morning_briefing()
        amp_briefing = content_engine.get_morning_briefing_data()
        chronicle_data = meeting_engine.get_morning_briefing_data()
        rest = gravity_field.governors.should_suggest_rest(gravity_field.items, 8.0)

        briefing_data = {
            "gravity": {"red_giants": gravity_snap.red_giants, "trust_debt_aud": gravity_snap.trust_debt_total_aud},
            "cartographer": cart_briefing,
            "amplifier": amp_briefing,
            "chronicle": chronicle_data,
            "rest_suggestion": rest,
        }
        segments = voice_formatter.format_morning_briefing(briefing_data)
        return jsonify({
            "segments": [{"text": s.text, "emotion": s.emotion.value, "pause_ms": s.pause_before_ms} for s in segments],
            "plain_text": voice_formatter.segments_to_text(segments),
            "ssml": voice_formatter.segments_to_ssml(segments),
        })

    # ── System Info ──────────────────────────────────────────────

    @app.route("/api/system/config", methods=["GET"])
    def system_config():
        return jsonify({
            "name": ELAINE_NAME,
            "version": ELAINE_VERSION,
            "owner": OWNER_NAME,
            "company": COMPANY_NAME,
            "voice_id": ELEVENLABS_VOICE_ID,
            "names": ELAINE_NAMES,
            "modules_enabled": MODULES,
        })

    @app.route("/", methods=["GET"])
    def root():
        from flask import render_template
        return render_template("index.html")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host=HOST, port=PORT, debug=DEBUG)
