"""
Elaine v4 — Phase 8 API Routes
Cartographer v2, Amplifier v2, Thinking Frameworks Engine
Almost Magic Tech Lab
"""

from flask import Blueprint, jsonify, request


# ── Thinking Frameworks API ──────────────────────────────────────

thinking_bp = Blueprint("thinking", __name__, url_prefix="/api/thinking")


def create_thinking_routes(engine):

    @thinking_bp.route("/status", methods=["GET"])
    def status():
        return jsonify(engine.status())

    @thinking_bp.route("/history", methods=["GET"])
    def history():
        limit = request.args.get("limit", 10, type=int)
        return jsonify(engine.get_history(limit))

    @thinking_bp.route("/analyse", methods=["POST"])
    def analyse():
        """Run thinking frameworks on a topic."""
        data = request.get_json() or {}
        from modules.thinking.engine import DecisionDomain, StakesLevel, FrameworkType
        result = engine.analyse(
            topic=data.get("topic", ""),
            domain=DecisionDomain(data.get("domain", "strategy")),
            stakes=StakesLevel(data.get("stakes", "medium")),
            context=data.get("context"),
            frameworks=[FrameworkType(f) for f in data.get("frameworks", [])] if data.get("frameworks") else None,
        )
        return jsonify({
            "topic": result.topic,
            "domain": result.domain.value,
            "stakes": result.stakes.value,
            "frameworks_applied": [f.value for f in result.frameworks_applied],
            "synthesis": result.synthesis,
            "recommended_action": result.recommended_action,
            "warnings": result.warnings,
        })

    @thinking_bp.route("/matrix", methods=["GET"])
    def framework_matrix():
        """Show which frameworks auto-apply for each domain/stakes combo."""
        from modules.thinking.engine import FRAMEWORK_MATRIX
        return jsonify({
            f"{k[0].value}/{k[1].value}": [f.value for f in v]
            for k, v in FRAMEWORK_MATRIX.items()
        })

    return thinking_bp


# ── Cartographer API ─────────────────────────────────────────────

cartographer_bp = Blueprint("cartographer", __name__, url_prefix="/api/cartographer")


def create_cartographer_routes(territory_map, discovery_engine):

    @cartographer_bp.route("/territory", methods=["GET"])
    def territory():
        return jsonify(territory_map.get_map())

    @cartographer_bp.route("/territory/<territory_id>/debt", methods=["GET"])
    def territory_debt(territory_id):
        from modules.cartographer.models import DepthLevel
        t = territory_map.get_territory(territory_id)
        if not t:
            return jsonify({"error": "Territory not found"}), 404
        return jsonify({
            "territory": t.label,
            "depth": t.depth.value,
            "score": round(t.depth_score, 1),
            "debt_hours": t.knowledge_debt_hours,
            "debt_description": t.knowledge_debt_description,
            "roi": t.knowledge_debt_roi,
        })

    @cartographer_bp.route("/adjacent", methods=["GET"])
    def adjacent():
        return jsonify(territory_map.get_adjacent_territories())

    @cartographer_bp.route("/briefing", methods=["GET"])
    def briefing():
        return jsonify(discovery_engine.get_morning_briefing())

    @cartographer_bp.route("/discoveries", methods=["GET"])
    def discoveries():
        layer = request.args.get("layer")
        territory = request.args.get("territory", "")
        limit = request.args.get("limit", 20, type=int)
        from modules.cartographer.models import DiscoveryLayer
        layer_enum = DiscoveryLayer(layer) if layer else None
        discs = discovery_engine.get_delivered(layer=layer_enum, territory=territory, limit=limit)
        return jsonify([
            {
                "id": d.discovery_id,
                "title": d.title,
                "so_what": d.so_what,
                "layer": d.layer.value,
                "actionability": d.actionability.value,
                "territory": d.territory,
                "source": d.source_name,
                "credibility": round(d.source_credibility, 2),
                "interaction": d.interaction.value if d.interaction else None,
            }
            for d in discs
        ])

    @cartographer_bp.route("/discoveries/<disc_id>/interact", methods=["POST"])
    def interact(disc_id):
        data = request.get_json() or {}
        from modules.cartographer.models import InteractionType
        interaction = InteractionType(data.get("interaction", "read"))
        discovery_engine.record_interaction(disc_id, interaction)
        return jsonify({"status": "recorded", "interaction": interaction.value})

    @cartographer_bp.route("/patterns", methods=["GET"])
    def patterns():
        all_patterns = list(discovery_engine.patterns.values())
        return jsonify([
            {
                "id": p.pattern_id,
                "label": p.label,
                "confidence": round(p.confidence, 2),
                "signal_count": p.signal_count,
                "action": p.action_recommended,
                "territory": p.territory,
            }
            for p in sorted(all_patterns, key=lambda p: p.confidence, reverse=True)
        ])

    @cartographer_bp.route("/sources", methods=["GET"])
    def sources():
        return jsonify(discovery_engine.sources.get_all())

    @cartographer_bp.route("/governor", methods=["GET"])
    def governor():
        return jsonify(discovery_engine.governor.status())

    @cartographer_bp.route("/learning", methods=["GET"])
    def learning():
        return jsonify(discovery_engine.get_learning_report())

    @cartographer_bp.route("/gaps", methods=["GET"])
    def gaps():
        return jsonify([
            {"id": g.gap_id, "title": g.title, "where": g.where_found,
             "causes": g.root_causes, "corrections": g.corrections_applied}
            for g in discovery_engine.gaps
        ])

    @cartographer_bp.route("/status", methods=["GET"])
    def cart_status():
        return jsonify(discovery_engine.status())

    return cartographer_bp


# ── Amplifier API ────────────────────────────────────────────────

amplifier_bp = Blueprint("amplifier", __name__, url_prefix="/api/amplifier")


def create_amplifier_routes(content_engine):

    @amplifier_bp.route("/ideas", methods=["GET"])
    def ideas():
        pillar = request.args.get("pillar")
        from modules.amplifier.models import ContentPillar
        pillar_enum = ContentPillar(pillar) if pillar else None
        items = content_engine.get_ideas(pillar=pillar_enum)
        return jsonify([
            {
                "id": i.content_id,
                "title": i.title,
                "thesis": i.genome.thesis,
                "pillar": i.genome.pillar.value,
                "certainty": i.genome.certainty_level.value,
                "objective": i.genome.objective.value,
            }
            for i in items
        ])

    @amplifier_bp.route("/ideas", methods=["POST"])
    def create_idea():
        data = request.get_json() or {}
        from modules.amplifier.models import ContentPillar, EpistemicLevel, ContentObjective
        item = content_engine.create_idea(
            title=data.get("title", ""),
            thesis=data.get("thesis", ""),
            pillar=ContentPillar(data.get("pillar", "thought_leadership")),
            certainty=EpistemicLevel(data.get("certainty", "conviction")),
            objective=ContentObjective(data.get("objective", "authority")),
        )
        return jsonify({"id": item.content_id, "status": item.status.value})

    @amplifier_bp.route("/quality-gate/<content_id>", methods=["POST"])
    def quality_gate(content_id):
        result = content_engine.run_quality_gate(content_id)
        return jsonify({
            "status": result.gate_status.value,
            "voice_score": result.voice_consistency,
            "epistemic": result.epistemic_alignment,
            "client_sensitivity": result.client_sensitivity,
            "warnings": result.warnings,
            "suggestions": result.suggestions,
            "thinking_frameworks": result.thinking_frameworks_applied,
        })

    @amplifier_bp.route("/restraint/<content_id>", methods=["GET"])
    def check_restraint(content_id):
        red_giants = request.args.get("red_giants", 0, type=int)
        signals = content_engine.check_restraints(content_id, red_giants)
        return jsonify(signals)

    @amplifier_bp.route("/calendar/suggest", methods=["GET"])
    def suggest():
        red_giants = request.args.get("red_giants", 0, type=int)
        return jsonify(content_engine.suggest_next_content(red_giants))

    @amplifier_bp.route("/genome/evolve", methods=["GET"])
    def genome_report():
        return jsonify(content_engine.genome_engine.get_evolution_report())

    @amplifier_bp.route("/graph", methods=["GET"])
    def authority_graph():
        return jsonify(content_engine.get_authority_graph())

    @amplifier_bp.route("/commentary", methods=["GET"])
    def commentary():
        return jsonify(content_engine.get_commentary_queue())

    @amplifier_bp.route("/pipeline-leads", methods=["GET"])
    def pipeline_leads():
        return jsonify([
            {"name": l.name, "company": l.company, "intent": l.intent_score,
             "segment": l.segment, "outreach": l.suggested_outreach}
            for l in content_engine.warm_leads
        ])

    @amplifier_bp.route("/restraint", methods=["GET"])
    def restraint_report():
        return jsonify(content_engine.restraint_engine.get_overexposure_report())

    @amplifier_bp.route("/briefing", methods=["GET"])
    def amp_briefing():
        return jsonify(content_engine.get_morning_briefing_data())

    @amplifier_bp.route("/status", methods=["GET"])
    def amp_status():
        return jsonify(content_engine.status())

    return amplifier_bp
