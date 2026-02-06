"""
Elaine v4 — Phase 14b API Routes
Communication + Strategic Frameworks: auto-applied and directly accessible
Almost Magic Tech Lab
"""

from flask import Blueprint, jsonify, request

frameworks_bp = Blueprint("frameworks", __name__, url_prefix="/api/frameworks")


def create_framework_routes(communication_engine, strategic_engine, orchestrator):

    # ── Communication ────────────────────────────────────────

    @frameworks_bp.route("/communication/pyramid", methods=["POST"])
    def pyramid():
        data = request.get_json() or {}
        r = communication_engine.pyramid(
            answer=data.get("answer", ""),
            supporting_arguments=data.get("arguments", []),
            situation=data.get("situation", ""),
            complication=data.get("complication", ""),
            question=data.get("question", ""),
        )
        return jsonify({
            "answer": r.answer,
            "arguments": r.supporting_arguments,
            "is_mece": r.is_mece,
            "gaps": r.mece_gaps,
            "overlaps": r.mece_overlaps,
            "scqa": r.scqa,
        })

    @frameworks_bp.route("/communication/scqa", methods=["POST"])
    def scqa():
        data = request.get_json() or {}
        r = communication_engine.scqa(
            data.get("situation", ""), data.get("complication", ""),
            data.get("question", ""), data.get("answer", ""),
        )
        return jsonify({"narrative": r.narrative, "situation": r.situation,
                         "complication": r.complication, "question": r.question, "answer": r.answer})

    @frameworks_bp.route("/communication/abt", methods=["POST"])
    def abt():
        data = request.get_json() or {}
        r = communication_engine.abt(
            data.get("and", ""), data.get("but", ""), data.get("therefore", ""),
        )
        return jsonify({"narrative": r.narrative})

    @frameworks_bp.route("/communication/presentation-check", methods=["POST"])
    def presentation_check():
        data = request.get_json() or {}
        r = communication_engine.presentation_check(
            slides_count=data.get("slides", 10),
            timing_minutes=data.get("minutes", 20),
            min_font_size=data.get("font_size", 30),
        )
        return jsonify({
            "passes_10_20_30": r.passes_10_20_30,
            "recommendations": r.recommendations,
            "signposts": r.signposts,
            "power_pauses": r.power_pauses,
        })

    @frameworks_bp.route("/communication/suggest", methods=["GET"])
    def suggest_comm():
        from modules.communication import CommunicationType, AudienceLevel
        ct = request.args.get("type", "email")
        al = request.args.get("audience", "c_suite")
        fws = communication_engine.suggest_frameworks(CommunicationType(ct), AudienceLevel(al))
        return jsonify({"type": ct, "audience": al, "suggested_frameworks": fws})

    @frameworks_bp.route("/communication/status", methods=["GET"])
    def comm_status():
        return jsonify(communication_engine.status())

    # ── Strategic ────────────────────────────────────────────

    @frameworks_bp.route("/strategic/swot", methods=["POST"])
    def swot():
        data = request.get_json() or {}
        r = strategic_engine.swot(
            data.get("topic", ""),
            strengths=data.get("strengths", []),
            weaknesses=data.get("weaknesses", []),
            opportunities=data.get("opportunities", []),
            threats=data.get("threats", []),
        )
        return jsonify({
            "topic": r.topic, "strengths": r.strengths, "weaknesses": r.weaknesses,
            "opportunities": r.opportunities, "threats": r.threats,
            "key_insight": r.key_insight, "priority_action": r.priority_action,
        })

    @frameworks_bp.route("/strategic/mece", methods=["POST"])
    def mece():
        data = request.get_json() or {}
        r = strategic_engine.mece_check(data.get("problem", ""), data.get("categories", []))
        return jsonify({
            "is_mece": r.is_mece, "gaps": r.gaps, "overlaps": r.overlaps,
            "recommendations": r.recommendations,
        })

    @frameworks_bp.route("/strategic/pestle", methods=["POST"])
    def pestle():
        data = request.get_json() or {}
        r = strategic_engine.pestle(data.get("topic", ""),
            political=data.get("political", []),
            economic=data.get("economic", []),
            social=data.get("social", []),
            technological=data.get("technological", []),
            legal=data.get("legal", []),
            environmental=data.get("environmental", []),
        )
        return jsonify({
            "topic": r.topic, "highest_impact": r.highest_impact_factor,
            "recommendations": r.recommendations,
        })

    @frameworks_bp.route("/strategic/bcg", methods=["POST"])
    def bcg():
        data = request.get_json() or {}
        r = strategic_engine.bcg_matrix(data.get("topic", ""), data.get("items", []))
        return jsonify({
            "portfolio_balance": r.portfolio_balance,
            "items": [{"name": i.name, "quadrant": i.quadrant.value, "recommendation": i.recommendation} for i in r.items],
        })

    @frameworks_bp.route("/strategic/seven-s", methods=["POST"])
    def seven_s():
        data = request.get_json() or {}
        r = strategic_engine.seven_s(data.get("topic", ""), **{
            k: data.get(k, "") for k in
            ["strategy", "structure", "systems", "shared_values", "style", "staff", "skills"]
        })
        return jsonify({
            "alignment_score": r.alignment_score,
            "misalignments": r.misalignments,
            "recommendations": r.recommendations,
        })

    @frameworks_bp.route("/strategic/status", methods=["GET"])
    def strategic_status():
        return jsonify(strategic_engine.status())

    # ── Auto-Apply (via Orchestrator) ────────────────────────

    @frameworks_bp.route("/auto/structure", methods=["POST"])
    def auto_structure():
        """Auto-apply communication frameworks to content."""
        data = request.get_json() or {}
        r = orchestrator.auto_structure_communication(
            content=data.get("content", ""),
            title=data.get("title", ""),
            comm_type=data.get("type", "email"),
            audience=data.get("audience", "c_suite"),
        )
        return jsonify(r)

    @frameworks_bp.route("/auto/strategic", methods=["POST"])
    def auto_strategic():
        """Auto-apply strategic framework to a topic."""
        data = request.get_json() or {}
        r = orchestrator.auto_strategic_analysis(
            topic=data.get("topic", ""),
            analysis_type=data.get("framework", "swot"),
            context=data.get("context", {}),
        )
        return jsonify(r)

    return frameworks_bp
