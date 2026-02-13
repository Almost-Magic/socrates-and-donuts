"""
Peterman V4.1 — The Authority & Presence Engine
Almost Magic Tech Lab

Port: 5008
Database: PostgreSQL + pgvector (Docker, port 5433)
LLMs: Ollama (local, port 11434)
Search: SearXNG (Docker, port 8888)
Queue: Redis (Docker, port 6379)
"""
import os
import logging
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from backend.models import db
from backend.config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")


def create_app(config_name=None):
    """Application factory."""
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="/static")
    app.config.from_object(config[config_name])

    # Extensions
    CORS(app)
    db.init_app(app)

    # Register blueprints — all 10 chambers
    from backend.routes import (
        health_bp, brands_bp, perception_bp, browser_bp,
        semantic_bp, vectormap_bp, authority_bp, survivability_bp,
        machine_bp, amplifier_bp, proof_bp, oracle_bp, forge_bp,
        seo_ask_bp,
    )
    app.register_blueprint(health_bp)
    app.register_blueprint(brands_bp)
    app.register_blueprint(perception_bp)
    app.register_blueprint(browser_bp)
    app.register_blueprint(semantic_bp)        # Chamber 2
    app.register_blueprint(vectormap_bp)       # Chamber 3
    app.register_blueprint(authority_bp)       # Chamber 4
    app.register_blueprint(survivability_bp)   # Chamber 5
    app.register_blueprint(machine_bp)         # Chamber 6
    app.register_blueprint(amplifier_bp)       # Chamber 7
    app.register_blueprint(proof_bp)           # Chamber 8
    app.register_blueprint(oracle_bp)          # Chamber 9
    app.register_blueprint(forge_bp)           # Chamber 10
    app.register_blueprint(seo_ask_bp)         # SEO Ask + ELAINE Briefing

    # Serve frontend
    @app.route("/")
    def serve_index():
        return send_from_directory(STATIC_DIR, "index.html")

    @app.route("/<path:path>")
    def serve_static(path):
        if os.path.exists(os.path.join(STATIC_DIR, path)):
            return send_from_directory(STATIC_DIR, path)
        return jsonify({"error": "Not found", "status": 404}), 404

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found", "status": 404}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error", "status": 500}), 500

    # Create tables (graceful if PostgreSQL is down)
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created/verified")
        except Exception as e:
            logger.warning(f"Database unavailable — Peterman starting in limited mode: {e}")

    logger.info(f"Peterman V{app.config['APP_VERSION']} starting on port {app.config['APP_PORT']}")
    return app


# Entry point
app = create_app()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=app.config["APP_PORT"],
        debug=app.config["DEBUG"],
    )
