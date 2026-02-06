"""
Elaine v4 — Phase 14c API Routes
Compassion Engine: emotional intelligence and wellbeing
Almost Magic Tech Lab
"""

from flask import Blueprint, jsonify, request

compassion_bp = Blueprint("compassion", __name__, url_prefix="/api/compassion")


def create_compassion_routes(compassion_engine):

    @compassion_bp.route("/detect", methods=["POST"])
    def detect():
        """Detect emotional context from text."""
        data = request.get_json() or {}
        context = compassion_engine.detect_context(
            data.get("text", ""), data.get("metadata", {}),
        )
        response = compassion_engine.frame_response(context, data.get("topic", ""))
        return jsonify({
            "context": context.value,
            "tone": response.tone.value,
            "opening": response.opening,
            "closing": response.closing,
            "framing_notes": response.framing_notes,
            "should_push": response.should_push,
            "should_celebrate": response.should_celebrate,
            "breathing_room": response.breathing_room,
            "voice_emotion": response.voice_emotion,
        })

    @compassion_bp.route("/wellbeing", methods=["GET"])
    def wellbeing():
        """Get current wellbeing state."""
        return jsonify(compassion_engine.get_morning_compassion())

    @compassion_bp.route("/wellbeing/signal", methods=["POST"])
    def log_signal():
        """Log a wellbeing observation."""
        data = request.get_json() or {}
        signal = compassion_engine.log_signal(
            data.get("type", ""), data.get("detail", ""),
            data.get("weight", 1.0),
        )
        return jsonify({
            "logged": signal.signal_type,
            "wellbeing_level": compassion_engine.wellbeing.level.value,
            "recommendation": compassion_engine.wellbeing.recommendation,
        })

    @compassion_bp.route("/briefing/voice", methods=["GET"])
    def voice_compassion():
        """Voice-ready compassion text for morning briefing."""
        return jsonify({"text": compassion_engine.get_voice_compassion_text()})

    @compassion_bp.route("/status", methods=["GET"])
    def status():
        return jsonify(compassion_engine.status())

    return compassion_bp
