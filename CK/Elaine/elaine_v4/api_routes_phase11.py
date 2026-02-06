"""
Elaine v4 — Phase 11 API Routes
App Innovator + Beast Research Delegation
Almost Magic Tech Lab
"""

from flask import Blueprint, jsonify, request

innovator_bp = Blueprint("innovator", __name__, url_prefix="/api/innovator")


def create_innovator_routes(innovation_engine):

    @innovator_bp.route("/opportunities", methods=["GET"])
    def opportunities():
        status = request.args.get("status", "")
        return jsonify(innovation_engine.get_ranked_opportunities(status=status))

    @innovator_bp.route("/opportunities", methods=["POST"])
    def create_opportunity():
        data = request.get_json() or {}
        from modules.innovator.models import InnovationType
        opp = innovation_engine.create_opportunity(
            title=data.get("title", ""),
            innovation_type=InnovationType(data.get("type", "customer_product")),
            description=data.get("description", ""),
            signals=data.get("signals", []),
            estimated_revenue=data.get("estimated_revenue", ""),
        )
        return jsonify({
            "opportunity_id": opp.opportunity_id,
            "title": opp.title,
            "confidence": round(opp.composite_confidence, 2),
        })

    @innovator_bp.route("/opportunities/<opp_id>/signal", methods=["POST"])
    def add_signal(opp_id):
        data = request.get_json() or {}
        from modules.innovator.models import SignalSource
        innovation_engine.add_signal(
            opp_id,
            source=SignalSource(data.get("source", "chronicle")),
            evidence=data.get("evidence", ""),
            strength=data.get("strength", 0.5),
        )
        opp = innovation_engine.opportunities.get(opp_id)
        return jsonify({
            "confidence": round(opp.composite_confidence, 2) if opp else 0,
            "signal_count": opp.signal_count if opp else 0,
        })

    @innovator_bp.route("/opportunities/<opp_id>/decide", methods=["POST"])
    def decide(opp_id):
        data = request.get_json() or {}
        innovation_engine.decide(opp_id, data.get("decision", ""), data.get("notes", ""))
        opp = innovation_engine.opportunities.get(opp_id)
        return jsonify({
            "status": opp.status.value if opp else "unknown",
            "decision": opp.mani_decision if opp else None,
        })

    @innovator_bp.route("/detect", methods=["POST"])
    def detect():
        """Run cross-module detection with provided module data."""
        data = request.get_json() or {}
        new = innovation_engine.detect_from_modules(data)
        return jsonify([
            {"id": o.opportunity_id, "title": o.title, "confidence": round(o.composite_confidence, 2)}
            for o in new
        ])

    # ── Beast Research ──

    @innovator_bp.route("/beast/brief/<opp_id>", methods=["POST"])
    def create_brief(opp_id):
        """Create a research brief for Beast (manual questions)."""
        data = request.get_json() or {}
        brief = innovation_engine.create_research_brief(
            opp_id, data.get("questions", []), data.get("deadline_days", 5),
        )
        return jsonify({
            "brief_id": brief.brief_id,
            "title": brief.title,
            "questions": len(brief.questions),
            "deadline_days": brief.deadline_days,
        })

    @innovator_bp.route("/beast/auto-brief/<opp_id>", methods=["POST"])
    def auto_brief(opp_id):
        """Auto-generate a research brief based on opportunity type."""
        brief = innovation_engine.auto_generate_brief(opp_id)
        return jsonify({
            "brief_id": brief.brief_id,
            "title": brief.title,
            "questions": [
                {"question": q.question, "type": q.research_type.value, "priority": q.priority}
                for q in brief.questions
            ],
            "deadline_days": brief.deadline_days,
        })

    @innovator_bp.route("/beast/briefs", methods=["GET"])
    def list_briefs():
        return jsonify([
            {
                "id": b.brief_id, "title": b.title,
                "opportunity": b.opportunity_id, "status": b.status.value,
                "questions": len(b.questions),
                "created": b.created_at.isoformat(),
            }
            for b in innovation_engine.research_briefs.values()
        ])

    @innovator_bp.route("/beast/result/<brief_id>", methods=["POST"])
    def submit_result(brief_id):
        """Submit Beast research results."""
        data = request.get_json() or {}
        result = innovation_engine.submit_research_result(
            brief_id,
            findings=data.get("findings", []),
            recommendation=data.get("recommendation", "investigate"),
            summary=data.get("summary", ""),
            risks=data.get("risks", []),
        )
        return jsonify({
            "brief_id": result.brief_id,
            "recommendation": result.recommendation.value,
            "findings_count": len(result.findings),
        })

    @innovator_bp.route("/beast/result/<brief_id>", methods=["GET"])
    def get_result(brief_id):
        result = innovation_engine.research_results.get(brief_id)
        if not result:
            return jsonify({"error": "No results yet"}), 404
        return jsonify({
            "brief_id": result.brief_id,
            "recommendation": result.recommendation.value,
            "summary": result.executive_summary,
            "risks": result.risks,
            "findings": [
                {"question": f.question_answered, "finding": f.finding,
                 "confidence": round(f.confidence, 2)}
                for f in result.findings
            ],
        })

    # ── Reports ──

    @innovator_bp.route("/report", methods=["GET"])
    def report():
        return jsonify(innovation_engine.get_monthly_report())

    @innovator_bp.route("/briefing", methods=["GET"])
    def briefing():
        return jsonify(innovation_engine.get_morning_briefing_data())

    @innovator_bp.route("/status", methods=["GET"])
    def innovator_status():
        return jsonify(innovation_engine.status())

    return innovator_bp
