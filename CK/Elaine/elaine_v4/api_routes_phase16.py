"""
Elaine v4 — Phase 16 API Routes
Gatekeeper: Pre-transmission quality assurance
Almost Magic Tech Lab
"""

from flask import Blueprint, jsonify, request

gatekeeper_bp = Blueprint("gatekeeper", __name__, url_prefix="/api/gatekeeper")


def create_gatekeeper_routes(gatekeeper):

    @gatekeeper_bp.route("/check", methods=["POST"])
    def check():
        """Full gatekeeper check on outbound content."""
        data = request.get_json() or {}
        from modules.gatekeeper import ContentChannel, ContentPriority
        channel = ContentChannel(data.get("channel", "email"))
        priority = None
        if data.get("priority"):
            priority = ContentPriority(data["priority"])
        r = gatekeeper.check(
            content=data.get("content", ""),
            title=data.get("title", ""),
            recipient=data.get("recipient", ""),
            channel=channel,
            priority=priority,
        )
        return jsonify({
            "item_id": r.item_id,
            "verdict": r.verdict.value,
            "priority": r.priority.value,
            "score": r.overall_score,
            "summary": r.summary,
            "checks": [
                {"gate": c.gate_name, "passed": c.passed, "issues": c.issues, "suggestions": c.suggestions, "score": c.score}
                for c in r.checks
            ],
        })

    @gatekeeper_bp.route("/override", methods=["POST"])
    def override():
        """Override a HOLD or REVIEW verdict."""
        data = request.get_json() or {}
        r = gatekeeper.override(data.get("item_id", ""), data.get("reason", ""))
        if r:
            return jsonify({"overridden": True, "item_id": r.item_id})
        return jsonify({"overridden": False, "error": "Item not found"}), 404

    @gatekeeper_bp.route("/folders", methods=["GET"])
    def folders():
        return jsonify({"folders": gatekeeper.get_watched_folders()})

    @gatekeeper_bp.route("/outlook-rules", methods=["GET"])
    def outlook_rules():
        return jsonify({"rules": gatekeeper.get_outlook_rules()})

    @gatekeeper_bp.route("/scripts/outlook", methods=["GET"])
    def outlook_script():
        return gatekeeper.get_outlook_hook_script(), 200, {"Content-Type": "text/plain"}

    @gatekeeper_bp.route("/scripts/watcher", methods=["GET"])
    def watcher_script():
        return gatekeeper.get_file_watcher_script(), 200, {"Content-Type": "text/plain"}

    @gatekeeper_bp.route("/history", methods=["GET"])
    def history():
        limit = request.args.get("limit", 20, type=int)
        return jsonify({"history": gatekeeper.get_history(limit)})

    @gatekeeper_bp.route("/status", methods=["GET"])
    def status():
        return jsonify(gatekeeper.status())

    return gatekeeper_bp
