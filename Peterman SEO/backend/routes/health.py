"""
Peterman V4.1 — Health & System Routes
Endpoints 1-6
"""
from datetime import datetime, timezone
from flask import Blueprint, jsonify, request, current_app
from ..services import ollama, searxng, snitcher

health_bp = Blueprint("health", __name__)

_start_time = datetime.now(timezone.utc)


@health_bp.route("/api/health", methods=["GET"])
def health_check():
    """Endpoint 1: Health check."""
    return jsonify({
        "status": "ok",
        "service": "peterman",
        "version": current_app.config.get("APP_VERSION", "4.1.0"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


@health_bp.route("/api/status", methods=["GET"])
def system_status():
    """Endpoint 2: Full system status with dependency checks."""
    uptime = (datetime.now(timezone.utc) - _start_time).total_seconds()

    # Check dependencies
    ollama_status = ollama.health_check()
    searxng_status = searxng.health_check()
    snitcher_status = snitcher.health_check()

    # Check PostgreSQL
    try:
        from ..models import db
        db.session.execute(db.text("SELECT 1"))
        pg_status = {"status": "ok"}
    except Exception as e:
        pg_status = {"status": "error", "error": str(e)}

    return jsonify({
        "status": "ok",
        "service": "peterman",
        "version": current_app.config.get("APP_VERSION", "4.1.0"),
        "uptime_seconds": round(uptime, 1),
        "dependencies": {
            "postgresql": pg_status,
            "ollama": ollama_status,
            "searxng": searxng_status,
            "snitcher": snitcher_status,
        },
        "port": current_app.config.get("APP_PORT", 5008),
    })


@health_bp.route("/api/config", methods=["GET"])
def get_config():
    """Endpoint 5: Get configuration (non-sensitive)."""
    return jsonify({
        "app_name": current_app.config.get("APP_NAME"),
        "version": current_app.config.get("APP_VERSION"),
        "port": current_app.config.get("APP_PORT"),
        "ollama_primary_model": current_app.config.get("OLLAMA_PRIMARY_MODEL"),
        "ollama_fast_model": current_app.config.get("OLLAMA_FAST_MODEL"),
        "ollama_embed_model": current_app.config.get("OLLAMA_EMBED_MODEL"),
        "searxng_url": current_app.config.get("SEARXNG_BASE_URL"),
        "scan_cache_days": current_app.config.get("SCAN_CACHE_DAYS"),
        "embed_dimensions": current_app.config.get("EMBED_DIMENSIONS"),
    })
