"""
Elaine v4 — Phase 7 API Routes
Flask API endpoints for Gravity Engine v2 and Constellation v2.
Almost Magic Tech Lab
"""

from flask import Blueprint, jsonify, request
from datetime import datetime
from typing import Optional

# ── Gravity API ──────────────────────────────────────────────────

gravity_bp = Blueprint("gravity", __name__, url_prefix="/api/gravity")


def create_gravity_routes(gravity_field, consequence_engine, learning_engine, drift_detector):
    """Register gravity routes with injected dependencies."""

    @gravity_bp.route("/field", methods=["GET"])
    def get_field():
        """Current gravity field with all items, consequences, and balance."""
        snapshot = gravity_field.snapshot()
        return jsonify({
            "total_items": snapshot.total_items,
            "red_giants": snapshot.red_giants,
            "approaching": snapshot.approaching,
            "stable": snapshot.stable,
            "peripheral": snapshot.peripheral,
            "top_3": snapshot.top_3_ids,
            "collisions": len(snapshot.collisions),
            "trust_debt_aud": snapshot.trust_debt_total_aud,
            "consequence_exposure": snapshot.consequence_exposure,
            "governor_status": snapshot.governor_status,
            "ungraviton_count": snapshot.ungraviton_count,
            "ungraviton_pattern": snapshot.ungraviton_pattern,
        })

    @gravity_bp.route("/top", methods=["GET"])
    def get_top():
        """Top N items by gravity score with full breakdowns."""
        n = request.args.get("n", 5, type=int)
        items = gravity_field.get_top_items(n)
        return jsonify([
            {
                "id": item.id,
                "title": item.title,
                "gravity_score": item.gravity_score,
                "alert_level": item.alert_level.value,
                "trajectory": item.trajectory.value,
                "due": item.proximity_date.isoformat() if item.proximity_date else None,
                "consequence_severity": item.consequence.trust_erosion,
                "revenue_at_risk": item.consequence.revenue_at_risk,
                "people": item.charge.people,
                "explanation": item.breakdown.explanation if item.breakdown else "",
            }
            for item in items
        ])

    @gravity_bp.route("/item/<item_id>/explain", methods=["GET"])
    def explain_item(item_id):
        """Full gravity breakdown for an item."""
        item = gravity_field.get_item(item_id)
        if not item:
            return jsonify({"error": "Item not found"}), 404
        if not item.breakdown:
            gravity_field.recalculate()
        bd = item.breakdown
        return jsonify({
            "id": item.id,
            "title": item.title,
            "score": item.gravity_score,
            "breakdown": {
                "mass": bd.mass_component,
                "proximity": bd.proximity_multiplier,
                "charge": bd.charge_multiplier,
                "consequence_kq": bd.consequence_multiplier,
                "momentum": bd.momentum_adjustment,
                "burst": bd.burst_component,
                "energy_fit": bd.energy_fit_modifier,
                "raw": bd.raw_score,
                "normalised": bd.normalised_score,
                "governors_applied": bd.governor_caps_applied,
                "inertia_active": bd.inertia_active,
            },
            "explanation": bd.explanation,
        })

    @gravity_bp.route("/item/<item_id>/whatif", methods=["GET"])
    def whatif_item(item_id):
        """Consequence cascade — what happens if skipped."""
        item = gravity_field.get_item(item_id)
        if not item:
            return jsonify({"error": "Item not found"}), 404
        chain = consequence_engine.analyse(item, gravity_field.items)
        return jsonify({
            "item": item.title,
            "severity": chain.severity,
            "revenue_at_risk": chain.revenue_at_risk,
            "trust_erosion": chain.trust_erosion_description,
            "trust_recovery": chain.trust_recovery_cost,
            "blocked_items": chain.blocked_items,
            "strategic_setback": chain.strategic_setback,
            "recovery_if_today": chain.recovery_cost_if_today,
            "recovery_if_week": chain.recovery_cost_if_week,
            "upside_if_done": chain.upside,
        })

    @gravity_bp.route("/collisions", methods=["GET"])
    def get_collisions():
        """Current collisions with resolution options."""
        collisions = gravity_field.detect_collisions()
        return jsonify([
            {
                "item_a": c.item_a_id,
                "item_b": c.item_b_id,
                "options": [
                    {
                        "label": o.label,
                        "gains": o.gains,
                        "costs": o.costs,
                        "net": o.net_impact,
                        "recommended": o.recommended,
                    }
                    for o in c.options
                ],
            }
            for c in collisions
        ])

    @gravity_bp.route("/drift", methods=["GET"])
    def get_drift():
        """Strategic drift analysis."""
        days = request.args.get("days", 7, type=int)
        analysis = drift_detector.analyse(days)
        return jsonify({
            "tactical_pct": analysis.urgent_tactical_pct,
            "strategic_pct": analysis.important_strategic_pct,
            "admin_pct": analysis.administrative_pct,
            "drift_alert": analysis.drift_alert,
            "drift_severity": analysis.drift_severity,
            "okrs_at_risk": analysis.okrs_at_risk,
            "okr_status": analysis.okr_status,
            "recommendation": analysis.recommendation,
        })

    @gravity_bp.route("/ungraviton", methods=["GET"])
    def get_ungraviton():
        """Deprioritised items with pattern analysis."""
        items = gravity_field.get_ungraviton()
        return jsonify([
            {
                "id": item.id,
                "title": item.title,
                "deprioritised_since": item.deprioritised_since.isoformat() if item.deprioritised_since else None,
                "tags": item.tags,
                "consequence_severity": item.consequence.trust_erosion,
            }
            for item in items
        ])

    @gravity_bp.route("/learning", methods=["GET"])
    def get_learning():
        """Learning system status."""
        return jsonify(learning_engine.status())

    @gravity_bp.route("/archaeology", methods=["GET"])
    def get_archaeology():
        """Failure post-mortems and prevention rules."""
        days = request.args.get("days", 30, type=int)
        return jsonify(learning_engine.get_failure_report(days))

    @gravity_bp.route("/governors", methods=["GET"])
    def get_governors():
        """Current governor states."""
        return jsonify(gravity_field.governors.status())

    @gravity_bp.route("/recalculate", methods=["POST"])
    def recalculate():
        """Force full recalculation."""
        gravity_field.recalculate()
        return jsonify({"status": "recalculated", "items": gravity_field.active_item_count()})

    return gravity_bp


# ── Constellation API ────────────────────────────────────────────

constellation_bp = Blueprint("constellation", __name__, url_prefix="/api/constellation")


def create_constellation_routes(poi_engine, network_intel, reciprocity_engine, poi_profiles):
    """Register constellation routes with injected dependencies."""

    @constellation_bp.route("/pois", methods=["GET"])
    def list_pois():
        """List POIs with tier/trust filters."""
        tier = request.args.get("tier")
        company = request.args.get("company", "")
        min_trust = request.args.get("min_trust", type=float)
        query = request.args.get("q", "")

        from modules.constellation.models import POITier
        tier_enum = None
        if tier:
            try:
                tier_enum = POITier[tier.upper()]
            except KeyError:
                pass

        pois = poi_engine.search_pois(query=query, tier=tier_enum,
                                       company=company, min_trust=min_trust)
        return jsonify([
            {
                "poi_id": p.poi_id,
                "name": p.name,
                "company": p.company,
                "tier": p.tier.name,
                "trust_balance": round(p.trust_account.balance, 1),
                "trust_health": p.trust_account.health,
                "days_since_interaction": round(p.days_since_interaction, 0),
            }
            for p in pois
        ])

    @constellation_bp.route("/pois/<poi_id>", methods=["GET"])
    def get_poi(poi_id):
        """Full POI profile with trust account."""
        poi = poi_engine.get_poi(poi_id)
        if not poi:
            return jsonify({"error": "POI not found"}), 404
        return jsonify(poi_profiles.build_profile_summary(poi))

    @constellation_bp.route("/pois/<poi_id>/meeting-prep", methods=["GET"])
    def meeting_prep(poi_id):
        """Pre-meeting intelligence brief."""
        poi = poi_engine.get_poi(poi_id)
        if not poi:
            return jsonify({"error": "POI not found"}), 404
        return jsonify(poi_profiles.build_meeting_prep(poi))

    @constellation_bp.route("/trust/alerts", methods=["GET"])
    def trust_alerts():
        """Current trust alerts."""
        alerts = poi_engine.trust_ledger.get_trust_alerts(poi_engine.pois)
        return jsonify(alerts)

    @constellation_bp.route("/trust/portfolio", methods=["GET"])
    def trust_portfolio():
        """Portfolio analysis."""
        return jsonify(poi_engine.trust_ledger.get_portfolio_summary(poi_engine.pois))

    @constellation_bp.route("/network/opportunities", methods=["GET"])
    def network_opportunities():
        """Second-order relationship opportunities."""
        opps = network_intel.find_opportunities(poi_engine.pois)
        return jsonify([
            {
                "source": o.source_poi_name,
                "target": o.target_name,
                "probability": o.warm_intro_probability,
                "value": o.estimated_value,
                "action": o.action,
                "prerequisites": o.prerequisites,
            }
            for o in opps
        ])

    @constellation_bp.route("/reciprocity", methods=["GET"])
    def reciprocity():
        """Reciprocity analysis across all tiers."""
        return jsonify(reciprocity_engine.analyse_all(poi_engine.pois))

    @constellation_bp.route("/briefing", methods=["GET"])
    def morning_briefing():
        """Morning briefing data for constellation."""
        return jsonify(poi_engine.get_morning_briefing_data())

    @constellation_bp.route("/counts", methods=["GET"])
    def poi_counts():
        """POI counts by tier."""
        return jsonify(poi_engine.get_poi_count())

    return constellation_bp
