"""
Elaine v4 — Phase 12 API Routes
Orchestrator: Cross-module intelligence wiring
Almost Magic Tech Lab
"""

from flask import Blueprint, jsonify, request

orchestrator_bp = Blueprint("orchestrator", __name__, url_prefix="/api/orchestrator")


def create_orchestrator_routes(orchestrator):

    @orchestrator_bp.route("/cascade/post-meeting/<meeting_id>", methods=["POST"])
    def post_meeting_cascade(meeting_id):
        """Full cascade after a meeting ends."""
        result = orchestrator.post_meeting_cascade(meeting_id)
        return jsonify(result)

    @orchestrator_bp.route("/cascade/discovery", methods=["POST"])
    def discovery_cascade():
        """Cascade a new discovery across modules."""
        data = request.get_json() or {}
        result = orchestrator.discovery_cascade(
            data.get("title", ""),
            data.get("so_what", ""),
            data.get("territory", ""),
            data.get("actionability", "act"),
        )
        return jsonify(result)

    @orchestrator_bp.route("/cascade/content-review", methods=["POST"])
    def content_review():
        """Send content through Sentinel before publishing."""
        data = request.get_json() or {}
        result = orchestrator.content_to_sentinel_review(
            data.get("content", ""),
            data.get("title", ""),
            data.get("is_public", True),
        )
        return jsonify(result)

    @orchestrator_bp.route("/cascade/analyse", methods=["POST"])
    def analyse():
        """Run Thinking Frameworks on any topic."""
        data = request.get_json() or {}
        result = orchestrator.analyse_decision(
            data.get("topic", ""),
            data.get("domain", "strategy"),
            data.get("stakes", "high"),
        )
        return jsonify(result)

    @orchestrator_bp.route("/log", methods=["GET"])
    def cascade_log():
        limit = request.args.get("limit", 50, type=int)
        return jsonify(orchestrator.get_cascade_log(limit))

    @orchestrator_bp.route("/wiring", methods=["GET"])
    def wiring():
        return jsonify(orchestrator.get_wiring_diagram())

    @orchestrator_bp.route("/status", methods=["GET"])
    def orchestrator_status():
        return jsonify(orchestrator.status())

    return orchestrator_bp
