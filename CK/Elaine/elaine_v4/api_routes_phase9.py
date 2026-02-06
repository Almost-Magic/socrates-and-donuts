"""
Elaine v4 — Phase 9 API Routes
Sentinel v2: Quality Governance & Trust Intelligence Engine
Almost Magic Tech Lab
"""

from flask import Blueprint, jsonify, request

sentinel_bp = Blueprint("sentinel", __name__, url_prefix="/api/sentinel")


def create_sentinel_routes(trust_engine):

    @sentinel_bp.route("/review", methods=["POST"])
    def review():
        """Submit content for quality review. Auto-detects profile and intent."""
        data = request.get_json() or {}
        audit = trust_engine.review(
            content=data.get("content", ""),
            title=data.get("title", ""),
            document_type=data.get("document_type", ""),
            recipient=data.get("recipient", ""),
            audience_context=data.get("audience_context"),
            has_pricing=data.get("has_pricing", False),
            is_public=data.get("is_public", False),
        )
        return jsonify({
            "audit_id": audit.audit_id,
            "profile": audit.governance_profile.value,
            "intent": audit.strategic_intent.value,
            "trust_surface": audit.trust_surface.to_dict(),
            "weighted_score": audit.weighted_trust_score,
            "verdict": audit.verdict.value,
            "summary": audit.summary,
            "risk_items": [
                {"issue": r.issue, "severity": r.severity.value,
                 "downside": r.expected_downside, "fix": r.suggested_fix}
                for r in audit.risk_items
            ],
            "position_conflicts": [
                {"claim": c.claim_in_document, "conflicts_with": c.conflicts_with,
                 "description": c.conflict_description, "options": c.resolution_options}
                for c in audit.position_conflicts
            ],
            "perspectives": [
                {"persona": p.persona, "flags": p.flags, "count": p.flag_count}
                for p in audit.perspective_reviews
            ],
            "credibility_present": audit.credibility_present,
            "credibility_missing": audit.credibility_missing,
            "credibility_suggestions": [
                {"type": s.signal_type, "suggestion": s.suggestion, "impact": s.expected_trust_impact}
                for s in audit.credibility_suggestions
            ],
            "staleness": [
                {"type": s.item_type, "content": s.content, "action": s.action_needed}
                for s in audit.staleness_items
            ],
            "resilience_score": audit.resilience_score,
            "thinking_frameworks": audit.thinking_frameworks_applied,
            "suggestions": audit.suggestions,
            "facts_checked": audit.facts_checked,
            "compliance_checked": audit.compliance_rules_checked,
        })

    @sentinel_bp.route("/quick-scan", methods=["POST"])
    def quick_scan():
        """Gate 1: Fast lightweight scan."""
        data = request.get_json() or {}
        result = trust_engine.quick_scan(data.get("content", ""))
        return jsonify(result)

    @sentinel_bp.route("/audit/<audit_id>", methods=["GET"])
    def get_audit(audit_id):
        audit = trust_engine.audits.get(audit_id)
        if not audit:
            return jsonify({"error": "Audit not found"}), 404
        return jsonify({
            "audit_id": audit.audit_id,
            "title": audit.document_title,
            "profile": audit.governance_profile.value,
            "intent": audit.strategic_intent.value,
            "trust_surface": audit.trust_surface.to_dict(),
            "weighted_score": audit.weighted_trust_score,
            "verdict": audit.verdict.value,
            "summary": audit.summary,
        })

    @sentinel_bp.route("/history", methods=["GET"])
    def history():
        limit = request.args.get("limit", 20, type=int)
        audits = sorted(trust_engine.audits.values(), key=lambda a: a.reviewed_at, reverse=True)[:limit]
        return jsonify([
            {
                "audit_id": a.audit_id,
                "title": a.document_title,
                "profile": a.governance_profile.value,
                "verdict": a.verdict.value,
                "weighted_score": a.weighted_trust_score,
                "date": a.reviewed_at.isoformat(),
            }
            for a in audits
        ])

    @sentinel_bp.route("/positions", methods=["GET"])
    def positions():
        return jsonify(trust_engine.get_positions())

    @sentinel_bp.route("/positions/conflicts", methods=["POST"])
    def check_conflicts():
        """Check a piece of content against position graph."""
        data = request.get_json() or {}
        conflicts = trust_engine._check_position_integrity(data.get("content", ""))
        return jsonify([
            {"claim": c.claim_in_document, "conflicts_with": c.conflicts_with,
             "description": c.conflict_description}
            for c in conflicts
        ])

    @sentinel_bp.route("/override", methods=["POST"])
    def record_override():
        data = request.get_json() or {}
        ovr = trust_engine.record_override(
            audit_id=data.get("audit_id", ""),
            issue=data.get("issue", ""),
            reason=data.get("reason", ""),
        )
        return jsonify({"override_id": ovr.override_id, "recorded": True})

    @sentinel_bp.route("/override/<override_id>/outcome", methods=["POST"])
    def record_outcome(override_id):
        data = request.get_json() or {}
        from modules.sentinel.models import OverrideOutcome
        trust_engine.record_override_outcome(
            override_id,
            OverrideOutcome(data.get("outcome", "neutral")),
            data.get("detail", ""),
        )
        return jsonify({"recorded": True})

    @sentinel_bp.route("/overrides", methods=["GET"])
    def overrides():
        return jsonify([
            {
                "id": o.override_id, "audit": o.audit_id,
                "issue": o.issue_overridden, "reason": o.reason,
                "outcome": o.outcome.value if o.outcome else None,
            }
            for o in trust_engine.overrides[-20:]
        ])

    @sentinel_bp.route("/incidents", methods=["GET"])
    def incidents():
        return jsonify([
            {"id": i.incident_id, "description": i.description,
             "root_cause": i.root_cause, "correction": i.self_correction,
             "new_rule": i.new_rule}
            for i in trust_engine.incidents
        ])

    @sentinel_bp.route("/incidents", methods=["POST"])
    def record_incident():
        data = request.get_json() or {}
        inc = trust_engine.record_incident(
            description=data.get("description", ""),
            root_cause=data.get("root_cause", ""),
            self_correction=data.get("self_correction", ""),
            new_rule=data.get("new_rule", ""),
        )
        return jsonify({"incident_id": inc.incident_id})

    @sentinel_bp.route("/exceptions", methods=["GET"])
    def exceptions():
        return jsonify([
            {"id": e.exception_id, "rule": e.rule_broken, "intent": e.intent,
             "ratio": e.risk_ratio, "granted": e.granted, "reasoning": e.reasoning}
            for e in trust_engine.exceptions
        ])

    @sentinel_bp.route("/exceptions", methods=["POST"])
    def grant_exception():
        data = request.get_json() or {}
        exc = trust_engine.grant_exception(
            rule_broken=data.get("rule_broken", ""),
            intent=data.get("intent", ""),
            risk_ratio=data.get("risk_ratio", 0.0),
            reasoning=data.get("reasoning", ""),
            conditions=data.get("conditions", []),
        )
        return jsonify({"exception_id": exc.exception_id, "granted": exc.granted})

    @sentinel_bp.route("/credibility/<audit_id>", methods=["GET"])
    def credibility(audit_id):
        audit = trust_engine.audits.get(audit_id)
        if not audit:
            return jsonify({"error": "Audit not found"}), 404
        return jsonify({
            "present": audit.credibility_present,
            "missing": audit.credibility_missing,
            "suggestions": [
                {"type": s.signal_type, "suggestion": s.suggestion, "impact": s.expected_trust_impact}
                for s in audit.credibility_suggestions
            ],
        })

    @sentinel_bp.route("/staleness", methods=["POST"])
    def check_staleness():
        data = request.get_json() or {}
        items = data.get("items", [])
        stale = trust_engine.check_staleness(items)
        return jsonify([
            {"type": s.item_type, "content": s.content, "age_days": s.age_days,
             "freshness": s.freshness_pct, "action": s.action_needed}
            for s in stale
        ])

    @sentinel_bp.route("/patterns", methods=["GET"])
    def patterns():
        return jsonify(trust_engine._error_patterns)

    @sentinel_bp.route("/learning", methods=["GET"])
    def learning():
        return jsonify(trust_engine.get_learning_report())

    @sentinel_bp.route("/status", methods=["GET"])
    def sentinel_status():
        return jsonify(trust_engine.status())

    return sentinel_bp
