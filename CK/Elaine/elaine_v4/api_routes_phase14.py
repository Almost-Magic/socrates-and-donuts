"""
Elaine v4 — Phase 14 API Routes
Learning Radar: Intellectual interest detection + exploration suggestions
Almost Magic Tech Lab
"""

from flask import Blueprint, jsonify, request

learning_bp = Blueprint("learning", __name__, url_prefix="/api/learning")


def create_learning_routes(learning_radar):

    @learning_bp.route("/interests", methods=["GET"])
    def interests():
        domain = request.args.get("domain", "")
        strength = request.args.get("strength", "")
        return jsonify(learning_radar.get_interests(domain=domain, strength=strength))

    @learning_bp.route("/interests", methods=["POST"])
    def add_interest():
        data = request.get_json() or {}
        interest = learning_radar.add_interest(
            topic=data.get("topic", ""),
            domain=data.get("domain", "general"),
            reading=data.get("reading", []),
        )
        return jsonify({
            "interest_id": interest.interest_id,
            "topic": interest.topic,
            "domain": interest.domain,
        })

    @learning_bp.route("/detect", methods=["POST"])
    def detect():
        """Detect interests from text (called by Orchestrator or manually)."""
        data = request.get_json() or {}
        from modules.learning_radar import InterestSource
        result = learning_radar.detect_interest(
            text=data.get("text", ""),
            source=InterestSource(data.get("source", "conversation")),
            context=data.get("context", ""),
        )
        if result:
            return jsonify({
                "detected": True,
                "topic": result.topic,
                "strength": result.strength.value,
                "mentions": result.mention_count,
            })
        return jsonify({"detected": False})

    @learning_bp.route("/connections", methods=["GET"])
    def connections():
        return jsonify(learning_radar.get_connections())

    @learning_bp.route("/connections", methods=["POST"])
    def add_connection():
        data = request.get_json() or {}
        conn = learning_radar.add_connection(
            interest_ids=data.get("interest_ids", []),
            thread=data.get("thread", ""),
            exploration=data.get("exploration", ""),
        )
        if conn:
            return jsonify({"topics": conn.topic_names, "thread": conn.thread})
        return jsonify({"error": "Need at least 2 valid interest IDs"}), 400

    @learning_bp.route("/domains", methods=["GET"])
    def domains():
        return jsonify(learning_radar.get_domains())

    @learning_bp.route("/briefing", methods=["GET"])
    def briefing():
        return jsonify(learning_radar.get_morning_briefing_data())

    @learning_bp.route("/briefing/voice", methods=["GET"])
    def voice_briefing():
        return jsonify({"text": learning_radar.get_voice_briefing_text()})

    @learning_bp.route("/status", methods=["GET"])
    def learning_status():
        return jsonify(learning_radar.status())

    return learning_bp
