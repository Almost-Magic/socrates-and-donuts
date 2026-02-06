"""
Elaine v4 — Phase 12: Complete System with Orchestrator
Flask application entry point.

10 modules + Orchestrator cross-wiring.
Almost Magic Tech Lab
"""

from flask import Flask, jsonify
import logging
from config import *

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)


def create_app():
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False

    # ── Initialise All Modules ───────────────────────────────────

    # Phase 8a: Thinking Frameworks (loaded first)
    from modules.thinking.engine import ThinkingFrameworksEngine
    thinking_engine = ThinkingFrameworksEngine()

    # Phase 7: Gravity Engine v2
    from modules.gravity_v2.gravity_field import GravityField
    from modules.gravity_v2.consequence_engine import ConsequenceEngine
    from modules.gravity_v2.learning import LearningEngine
    from modules.gravity_v2.drift_detector import DriftDetector
    gravity_field = GravityField()
    consequence_engine = ConsequenceEngine()
    learning_engine = LearningEngine()
    drift_detector = DriftDetector()

    # Phase 7: Constellation v2
    from modules.constellation.poi_engine import POIEngine
    from modules.constellation.network_intelligence import NetworkIntelligence
    from modules.constellation.reciprocity import ReciprocityEngine
    from modules.constellation.poi_profiles import POIProfile
    poi_engine = POIEngine()
    network_intel = NetworkIntelligence()
    reciprocity_engine = ReciprocityEngine()
    poi_profiles = POIProfile()

    # Phase 8: Cartographer v2
    from modules.cartographer.territory_map import TerritoryMap
    from modules.cartographer.discovery_engine import DiscoveryEngine
    territory_map = TerritoryMap()
    discovery_engine = DiscoveryEngine()

    # Phase 8: Amplifier v2
    from modules.amplifier.content_engine import ContentEngine
    content_engine = ContentEngine(thinking_engine=thinking_engine)

    # Phase 9: Sentinel v2
    from modules.sentinel.trust_engine import TrustEngine
    trust_engine = TrustEngine(thinking_engine=thinking_engine)

    # Phase 10: Chronicle v2
    from modules.chronicle.meeting_engine import MeetingEngine
    meeting_engine = MeetingEngine()

    # Phase 10: Voice
    from modules.chronicle.voice import VoiceBriefingFormatter
    voice_formatter = VoiceBriefingFormatter()

    # Phase 11: Innovator + Beast
    from modules.innovator.engine import InnovationEngine
    innovation_engine = InnovationEngine()

    # Phase 14: Learning Radar
    from modules.learning_radar import LearningRadar
    learning_radar = LearningRadar()

    # Phase 14b: Communication + Strategic Engines
    from modules.communication import CommunicationEngine
    communication_engine = CommunicationEngine()

    from modules.strategic import StrategicEngine
    strategic_engine = StrategicEngine()

    # Phase 15: Compassion Engine
    from modules.compassion import CompassionEngine
    compassion_engine = CompassionEngine()

    # Phase 12: Orchestrator (wires everything together)
    from modules.orchestrator import Orchestrator
    orchestrator = Orchestrator(
        gravity_field=gravity_field,
        poi_engine=poi_engine,
        territory_map=territory_map,
        discovery_engine=discovery_engine,
        content_engine=content_engine,
        trust_engine=trust_engine,
        meeting_engine=meeting_engine,
        innovation_engine=innovation_engine,
        thinking_engine=thinking_engine,
        voice_formatter=voice_formatter,
        learning_radar=learning_radar,
        communication_engine=communication_engine,
        strategic_engine=strategic_engine,
        compassion_engine=compassion_engine,
    )

    # ── Register All Blueprints ──────────────────────────────────

    # Phase 7
    from api_routes import create_gravity_routes, create_constellation_routes
    app.register_blueprint(create_gravity_routes(gravity_field, consequence_engine, learning_engine, drift_detector))
    app.register_blueprint(create_constellation_routes(poi_engine, network_intel, reciprocity_engine, poi_profiles))

    # Phase 8 + 8a
    from api_routes_phase8 import create_thinking_routes, create_cartographer_routes, create_amplifier_routes
    app.register_blueprint(create_thinking_routes(thinking_engine))
    app.register_blueprint(create_cartographer_routes(territory_map, discovery_engine))
    app.register_blueprint(create_amplifier_routes(content_engine))

    # Phase 9
    from api_routes_phase9 import create_sentinel_routes
    app.register_blueprint(create_sentinel_routes(trust_engine))

    # Phase 10
    from api_routes_phase10 import create_chronicle_routes, create_voice_routes
    app.register_blueprint(create_chronicle_routes(meeting_engine))
    app.register_blueprint(create_voice_routes(voice_formatter))

    # Phase 11
    from api_routes_phase11 import create_innovator_routes
    app.register_blueprint(create_innovator_routes(innovation_engine))

    # Phase 12
    from api_routes_phase12 import create_orchestrator_routes
    app.register_blueprint(create_orchestrator_routes(orchestrator))

    # Phase 14
    from api_routes_phase14 import create_learning_routes
    app.register_blueprint(create_learning_routes(learning_radar))

    # Phase 14b
    from api_routes_phase14b import create_framework_routes
    app.register_blueprint(create_framework_routes(communication_engine, strategic_engine, orchestrator))

    # Phase 14c
    from api_routes_phase14c import create_compassion_routes
    app.register_blueprint(create_compassion_routes(compassion_engine))

    # ── System Status ────────────────────────────────────────────

    @app.route("/api/status", methods=["GET"])
    def status():
        return jsonify({
            "name": ELAINE_NAME,
            "version": f"{ELAINE_VERSION}-phase14",
            "owner": OWNER_NAME,
            "company": COMPANY_NAME,
            "voice_id": ELEVENLABS_VOICE_ID,
            "modules": {
                "thinking_frameworks": {"status": "active", "analyses": thinking_engine.status()["total_analyses"]},
                "gravity_v2": {"status": "active", "items": gravity_field.active_item_count()},
                "constellation_v2": {"status": "active", "pois": len(poi_engine.pois)},
                "cartographer_v2": {"status": "active", "territories": len(territory_map.territories)},
                "amplifier_v2": {"status": "active", "content_items": len(content_engine.items)},
                "sentinel_v2": {"status": "active", "audits": len(trust_engine.audits)},
                "chronicle_v2": {"status": "active", "meetings": len(meeting_engine.meetings)},
                "voice": {"status": "active", "voice_id": ELEVENLABS_VOICE_ID},
                "innovator": {"status": "active", "opportunities": len(innovation_engine.opportunities)},
                "beast": {"status": "active", "briefs": len(innovation_engine.research_briefs)},
                "orchestrator": {"status": "active", "cascades": len(orchestrator._cascade_log)},
                "learning_radar": {"status": "active", "interests": len(learning_radar.interests), "connections": len(learning_radar.connections)},
                "communication": {"status": "active", "frameworks": 7},
                "strategic": {"status": "active", "frameworks": 8},
                "compassion": {"status": "active", "wellbeing": compassion_engine.wellbeing.level.value},
            },
            "phase": "14 — Learning Radar",
        })

    # ── Combined Morning Briefing ────────────────────────────────

    @app.route("/api/morning-briefing", methods=["GET"])
    def morning_briefing():
        gravity_snap = gravity_field.snapshot()
        constellation_data = poi_engine.get_morning_briefing_data()
        drift = drift_detector.analyse()
        nudges = gravity_field.governors.get_nudges(gravity_field.items)
        rest = gravity_field.governors.should_suggest_rest(gravity_field.items, 8.0)
        cart_briefing = discovery_engine.get_morning_briefing()
        amp_briefing = content_engine.get_morning_briefing_data()
        sentinel_data = trust_engine.get_learning_report()
        chronicle_data = meeting_engine.get_morning_briefing_data()
        innovator_data = innovation_engine.get_morning_briefing_data()
        learning_data = learning_radar.get_morning_briefing_data()

        return jsonify({
            "gravity": {
                "red_giants": gravity_snap.red_giants,
                "top_3": gravity_snap.top_3_ids,
                "trust_debt_aud": gravity_snap.trust_debt_total_aud,
                "collisions": len(gravity_snap.collisions),
            },
            "constellation": constellation_data,
            "cartographer": cart_briefing,
            "amplifier": amp_briefing,
            "sentinel": sentinel_data,
            "chronicle": chronicle_data,
            "innovator": innovator_data,
            "learning_radar": learning_data,
            "drift": {
                "alert": drift.drift_alert,
                "severity": drift.drift_severity,
                "recommendation": drift.recommendation,
            },
            "thinking_frameworks": thinking_engine.status(),
            "orchestrator": {"cascades": len(orchestrator._cascade_log)},
            "governor_nudges": nudges,
            "rest_suggestion": rest,
        })

    # ── Voice Morning Briefing ───────────────────────────────────

    @app.route("/api/morning-briefing/voice", methods=["GET"])
    def morning_briefing_voice():
        gravity_snap = gravity_field.snapshot()
        cart_briefing = discovery_engine.get_morning_briefing()
        amp_briefing = content_engine.get_morning_briefing_data()
        chronicle_data = meeting_engine.get_morning_briefing_data()
        rest = gravity_field.governors.should_suggest_rest(gravity_field.items, 8.0)

        briefing_data = {
            "gravity": {"red_giants": gravity_snap.red_giants, "trust_debt_aud": gravity_snap.trust_debt_total_aud},
            "cartographer": cart_briefing,
            "amplifier": amp_briefing,
            "chronicle": chronicle_data,
            "rest_suggestion": rest,
        }
        segments = voice_formatter.format_morning_briefing(briefing_data)
        return jsonify({
            "segments": [{"text": s.text, "emotion": s.emotion.value, "pause_ms": s.pause_before_ms} for s in segments],
            "plain_text": voice_formatter.segments_to_text(segments),
            "ssml": voice_formatter.segments_to_ssml(segments),
        })

    # ── System Info ──────────────────────────────────────────────

    @app.route("/api/system/config", methods=["GET"])
    def system_config():
        return jsonify({
            "name": ELAINE_NAME,
            "version": ELAINE_VERSION,
            "owner": OWNER_NAME,
            "company": COMPANY_NAME,
            "voice_id": ELEVENLABS_VOICE_ID,
            "names": ELAINE_NAMES,
            "modules_enabled": MODULES,
        })

    @app.route("/", methods=["GET"])
    def root():
        return jsonify({
            "message": f"{ELAINE_NAME} is running.",
            "status": "/api/status",
            "briefing": "/api/morning-briefing",
            "voice": "/api/morning-briefing/voice",
        })

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host=HOST, port=PORT, debug=DEBUG)
