"""
Elaine v4 — Stabilisation Routes
Health, modules, frustration logging, briefing alias, Supervisor integration.

Almost Magic Tech Lab — Week 3
"""

from flask import Blueprint, jsonify, request
import os
import json
import logging
import threading
import urllib.request
from datetime import datetime, timezone

logger = logging.getLogger("elaine.stabilisation")

SUPERVISOR_URL = os.environ.get("SUPERVISOR_URL", "http://localhost:9000")
FRUSTRATION_LOG_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "logs", "friction-log.jsonl"
)

# ── Background Supervisor health cache ──────────────────────────
_supervisor_cache = {"connected": False, "last_check": None}
_supervisor_lock = threading.Lock()


def _check_supervisor_bg():
    """Background thread: ping Supervisor every 30s, cache result."""
    import time
    while True:
        ok = False
        try:
            req = urllib.request.Request(
                f"{SUPERVISOR_URL}/api/health", method="GET"
            )
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status == 200:
                    ok = True
        except Exception:
            pass
        with _supervisor_lock:
            _supervisor_cache["connected"] = ok
            _supervisor_cache["last_check"] = datetime.now(timezone.utc).isoformat()
        time.sleep(30)


# Start background checker once at import time
threading.Thread(target=_check_supervisor_bg, daemon=True).start()


def create_stabilisation_routes(modules_status_fn, morning_briefing_fn):
    """
    Factory for stabilisation blueprint.

    Args:
        modules_status_fn: callable returning dict of active modules with status
        morning_briefing_fn: callable returning Flask response for morning briefing
    """
    bp = Blueprint("stabilisation", __name__)

    # ── GET /api/health ────────────────────────────────────────────
    @bp.route("/api/health", methods=["GET"])
    def health():
        """Health endpoint — returns instantly, never blocks on Supervisor."""
        with _supervisor_lock:
            supervisor_ok = _supervisor_cache["connected"]

        return jsonify({
            "status": "healthy",
            "service": "ELAINE",
            "version": "4.0",
            "supervisor_connected": supervisor_ok,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    # ── GET /api/modules ───────────────────────────────────────────
    @bp.route("/api/modules", methods=["GET"])
    def modules():
        """
        Module manifest — lists only ACTIVE/BUILT modules.
        Foreperson uses expected_contains to check for module names.
        Unbuilt modules (powershell, claude, clipboard, etc.) are
        correctly absent so Foreperson reports them as missing.
        """
        built = modules_status_fn()
        return jsonify({
            "modules": built,
            "total": len(built),
        })

    # ── GET /api/briefing ──────────────────────────────────────────
    @bp.route("/api/briefing", methods=["GET"])
    def briefing_alias():
        """Alias for /api/morning-briefing."""
        return morning_briefing_fn()

    # ── POST /api/frustration ──────────────────────────────────────
    @bp.route("/api/frustration", methods=["POST"])
    def log_frustration():
        """
        Log a frustration / friction event.
        Body: {"text": "...", "source": "api|elaine|manual", "category": "..."}
        Appends to logs/friction-log.jsonl.
        """
        data = request.get_json(silent=True) or {}
        text = data.get("text", "").strip()
        if not text:
            return jsonify({"error": "text is required"}), 400

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "text": text,
            "source": data.get("source", "api"),
            "category": data.get("category", "general"),
        }

        log_dir = os.path.dirname(FRUSTRATION_LOG_PATH)
        os.makedirs(log_dir, exist_ok=True)

        with open(FRUSTRATION_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        logger.info(f"Frustration logged: {text[:80]}")
        return jsonify({"logged": True, "entry": entry})

    # ── GET /api/frustration ───────────────────────────────────────
    @bp.route("/api/frustration", methods=["GET"])
    def get_frustrations():
        """Read recent frustration entries."""
        limit = request.args.get("limit", 20, type=int)
        entries = []
        try:
            with open(FRUSTRATION_LOG_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        entries.append(json.loads(line))
        except FileNotFoundError:
            pass
        return jsonify({"entries": entries[-limit:], "total": len(entries)})

    # ── GET /api/ai/status ─────────────────────────────────────────
    @bp.route("/api/ai/status", methods=["GET"])
    def ai_status():
        """Check whether Claude CLI is available."""
        from utils.ai_engine import check_ai_status
        return jsonify(check_ai_status())

    # ── GET /api/ecosystem ───────────────────────────────────────────
    @bp.route("/api/ecosystem", methods=["GET"])
    def ecosystem():
        """Live health checks for all AMTL apps."""
        from utils.ecosystem import check_ecosystem
        return jsonify(check_ecosystem())

    return bp
