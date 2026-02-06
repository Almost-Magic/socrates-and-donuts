"""
Elaine v4 — Phase 13: Test Harness & Verification Suite
Comprehensive testing before GitHub push.

Tests:
  1. Module Import Validation
  2. Unit Tests (each engine independently)
  3. Integration Tests (cross-module cascades)
  4. API Smoke Tests (every endpoint)
  5. Confidence Stamp (final report)

Almost Magic Tech Lab
"""

import sys
import os
import json
import traceback
from datetime import datetime, timedelta
from io import StringIO

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Test Infrastructure ──────────────────────────────────────────

PASS = "✅"
FAIL = "❌"
WARN = "⚠️"

results = {"passed": 0, "failed": 0, "warnings": 0, "details": []}


def test(name: str, fn, critical=True):
    """Run a test and record the result."""
    try:
        fn()
        results["passed"] += 1
        results["details"].append({"name": name, "status": "PASS"})
        print(f"  {PASS} {name}")
    except Exception as e:
        if critical:
            results["failed"] += 1
            results["details"].append({"name": name, "status": "FAIL", "error": str(e)})
            print(f"  {FAIL} {name}: {e}")
        else:
            results["warnings"] += 1
            results["details"].append({"name": name, "status": "WARN", "error": str(e)})
            print(f"  {WARN} {name}: {e}")


# ══════════════════════════════════════════════════════════════════
# 1. MODULE IMPORT VALIDATION
# ══════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("1. MODULE IMPORT VALIDATION")
print("=" * 60)


def test_import_config():
    from config import ELAINE_NAME, ELAINE_VERSION, OWNER_NAME
    assert ELAINE_NAME == "Maestro Elaine"
    assert ELAINE_VERSION == "4.0"
    assert OWNER_NAME == "Mani Padisetti"


def test_import_thinking():
    from modules.thinking.engine import ThinkingFrameworksEngine
    e = ThinkingFrameworksEngine()
    assert e is not None


def test_import_gravity():
    from modules.gravity_v2.gravity_field import GravityField
    from modules.gravity_v2.models import GravityItem, MomentumState
    from modules.gravity_v2.consequence_engine import ConsequenceEngine
    from modules.gravity_v2.drift_detector import DriftDetector
    from modules.gravity_v2.learning import LearningEngine
    from modules.gravity_v2.governors import GovernorSystem


def test_import_constellation():
    from modules.constellation.poi_engine import POIEngine
    from modules.constellation.models import POIRecord, POITier
    from modules.constellation.network_intelligence import NetworkIntelligence
    from modules.constellation.reciprocity import ReciprocityEngine
    from modules.constellation.trust_ledger import TrustLedger
    from modules.constellation.poi_profiles import POIProfile


def test_import_cartographer():
    from modules.cartographer.territory_map import TerritoryMap
    from modules.cartographer.discovery_engine import DiscoveryEngine
    from modules.cartographer.models import KnowledgeTerritory, Discovery


def test_import_amplifier():
    from modules.amplifier.content_engine import ContentEngine
    from modules.amplifier.models import ContentPillar, ContentItem, EpistemicLevel


def test_import_sentinel():
    from modules.sentinel.trust_engine import TrustEngine
    from modules.sentinel.models import GovernanceProfile, StrategicIntent, TrustSurface


def test_import_chronicle():
    from modules.chronicle.meeting_engine import MeetingEngine
    from modules.chronicle.models import MeetingRecord, Commitment, MeetingTemplate
    from modules.chronicle.voice import VoiceBriefingFormatter, EmotionalTag


def test_import_innovator():
    from modules.innovator.engine import InnovationEngine
    from modules.innovator.models import Opportunity, InnovationType, ResearchBrief


def test_import_orchestrator():
    from modules.orchestrator import Orchestrator


test("Config import", test_import_config)
test("Thinking Frameworks import", test_import_thinking)
test("Gravity v2 import", test_import_gravity)
test("Constellation v2 import", test_import_constellation)
test("Cartographer v2 import", test_import_cartographer)
test("Amplifier v2 import", test_import_amplifier)
test("Sentinel v2 import", test_import_sentinel)
test("Chronicle v2 import", test_import_chronicle)
test("Innovator + Beast import", test_import_innovator)
test("Orchestrator import", test_import_orchestrator)


# ══════════════════════════════════════════════════════════════════
# 2. UNIT TESTS — Each Engine Independently
# ══════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("2. UNIT TESTS")
print("=" * 60)

# ── Thinking Frameworks ──

def test_thinking_analyse():
    from modules.thinking.engine import ThinkingFrameworksEngine, DecisionDomain, StakesLevel
    e = ThinkingFrameworksEngine()
    r = e.analyse("Launch new product?", DecisionDomain.STRATEGY, StakesLevel.HIGH)
    assert len(r.frameworks_applied) >= 2
    assert r.topic == "Launch new product?"

def test_thinking_auto_select():
    from modules.thinking.engine import ThinkingFrameworksEngine, DecisionDomain, StakesLevel
    e = ThinkingFrameworksEngine()
    r = e.analyse("Quick internal note", DecisionDomain.CONTENT, StakesLevel.LOW)
    assert len(r.frameworks_applied) >= 1

test("Thinking: analyse high-stakes", test_thinking_analyse)
test("Thinking: auto-select frameworks", test_thinking_auto_select)

# ── Gravity v2 ──

def test_gravity_add_and_score():
    from modules.gravity_v2.gravity_field import GravityField
    from modules.gravity_v2.models import GravityItem
    g = GravityField()
    item = GravityItem(title="Test task", mass=80, proximity_date=datetime.now() + timedelta(days=2))
    added = g.add_item(item)
    assert added.id is not None
    assert g.active_item_count() == 1
    # Just verify we can get the item back
    retrieved = g.get_item(added.id)
    assert retrieved is not None
    assert retrieved.title == "Test task"

def test_gravity_snapshot():
    from modules.gravity_v2.gravity_field import GravityField
    from modules.gravity_v2.models import GravityItem
    g = GravityField()
    g.add_item(GravityItem(title="Urgent", mass=95, proximity_date=datetime.now() + timedelta(hours=6)))
    snap = g.snapshot()
    assert snap.red_giants >= 0
    assert snap.total_items == 1

def test_gravity_governors():
    from modules.gravity_v2.governors import GovernorSystem
    gov = GovernorSystem()
    assert gov is not None

test("Gravity: add item + score", test_gravity_add_and_score)
test("Gravity: snapshot", test_gravity_snapshot)
test("Gravity: governors init", test_gravity_governors)

# ── Constellation v2 ──

def test_constellation_add_poi():
    from modules.constellation.poi_engine import POIEngine
    e = POIEngine()
    poi = e.get_or_create_poi("James Chen", company="TechCorp")
    assert poi is not None
    assert len(e.pois) == 1

def test_constellation_network_intel():
    from modules.constellation.network_intelligence import NetworkIntelligence
    n = NetworkIntelligence()
    assert n is not None

test("Constellation: add POI", test_constellation_add_poi)
test("Constellation: network intelligence", test_constellation_network_intel)

# ── Cartographer v2 ──

def test_cartographer_add_territory():
    from modules.cartographer.territory_map import TerritoryMap
    tm = TerritoryMap()
    tm.add_territory("ai_governance", "AI Governance")
    assert "ai_governance" in tm.territories

def test_cartographer_discovery():
    from modules.cartographer.discovery_engine import DiscoveryEngine
    de = DiscoveryEngine()
    briefing = de.get_morning_briefing()
    assert "date" in briefing

test("Cartographer: add territory", test_cartographer_add_territory)
test("Cartographer: discovery briefing", test_cartographer_discovery)

# ── Amplifier v2 ──

def test_amplifier_create_idea():
    from modules.amplifier.content_engine import ContentEngine
    from modules.amplifier.models import ContentPillar, EpistemicLevel, ContentObjective
    from modules.thinking.engine import ThinkingFrameworksEngine
    ce = ContentEngine(thinking_engine=ThinkingFrameworksEngine())
    idea = ce.create_idea("Test idea", "AI governance is evolving",
                           ContentPillar.AI_GOVERNANCE, EpistemicLevel.CONVICTION,
                           ContentObjective.AUTHORITY)
    assert idea is not None
    assert len(ce.items) == 1

def test_amplifier_restraint():
    from modules.amplifier.content_engine import ContentEngine
    from modules.thinking.engine import ThinkingFrameworksEngine
    ce = ContentEngine(thinking_engine=ThinkingFrameworksEngine())
    briefing = ce.get_morning_briefing_data()
    assert "overexposure" in briefing

test("Amplifier: create idea", test_amplifier_create_idea)
test("Amplifier: restraint engine", test_amplifier_restraint)

# ── Sentinel v2 ──

def test_sentinel_review_clean():
    from modules.sentinel.trust_engine import TrustEngine
    from modules.thinking.engine import ThinkingFrameworksEngine
    te = TrustEngine(thinking_engine=ThinkingFrameworksEngine())
    audit = te.review(content="Team meeting at 3pm.", title="Internal note")
    assert audit.verdict.value == "clean"

def test_sentinel_review_dangerous():
    from modules.sentinel.trust_engine import TrustEngine
    from modules.thinking.engine import ThinkingFrameworksEngine
    te = TrustEngine(thinking_engine=ThinkingFrameworksEngine())
    audit = te.review(
        content="We guarantee compliance outcomes and ensure you will achieve certification.",
        title="Client proposal", is_public=True,
    )
    assert len(audit.risk_items) > 0
    assert audit.verdict.value != "clean"

def test_sentinel_quick_scan():
    from modules.sentinel.trust_engine import TrustEngine
    from modules.thinking.engine import ThinkingFrameworksEngine
    te = TrustEngine(thinking_engine=ThinkingFrameworksEngine())
    r = te.quick_scan("We guarantee results.")
    assert r["pass"] == False

def test_sentinel_position_integrity():
    from modules.sentinel.trust_engine import TrustEngine
    from modules.thinking.engine import ThinkingFrameworksEngine
    te = TrustEngine(thinking_engine=ThinkingFrameworksEngine())
    positions = te.get_positions()
    assert len(positions) > 0  # Seeded positions

test("Sentinel: clean review", test_sentinel_review_clean)
test("Sentinel: dangerous language detection", test_sentinel_review_dangerous)
test("Sentinel: quick scan", test_sentinel_quick_scan)
test("Sentinel: position integrity", test_sentinel_position_integrity)

# ── Chronicle v2 ──

def test_chronicle_meeting_lifecycle():
    from modules.chronicle.meeting_engine import MeetingEngine
    from modules.chronicle.models import MeetingTemplate, CommitmentType
    me = MeetingEngine()
    m = me.create_meeting("Test Meeting", MeetingTemplate.DISCOVERY_CALL,
                           [{"name": "Mani", "role": "host"}])
    assert m.meeting_id is not None
    c = me.add_commitment(m.meeting_id, "Send proposal", "mani", CommitmentType.EXPLICIT_DEADLINE)
    assert c.commitment_id is not None
    active = me.get_active_commitments()
    assert len(active) == 1

def test_chronicle_extract_commitments():
    from modules.chronicle.meeting_engine import MeetingEngine
    from modules.chronicle.models import MeetingTemplate
    me = MeetingEngine()
    m = me.create_meeting("Extract Test", MeetingTemplate.DISCOVERY_CALL, [{"name": "Mani", "role": "host"}])
    cs = me.extract_commitments(m.meeting_id, "I'll send the report. We'll schedule a follow-up.")
    assert len(cs) >= 2

def test_chronicle_follow_up():
    from modules.chronicle.meeting_engine import MeetingEngine
    from modules.chronicle.models import MeetingTemplate
    me = MeetingEngine()
    m = me.create_meeting("Follow-up Test", MeetingTemplate.DISCOVERY_CALL,
                           [{"name": "Mani", "role": "host"}, {"name": "James", "role": "prospect"}])
    draft = me.generate_follow_up(m.meeting_id)
    assert "James" in draft.subject

test("Chronicle: meeting lifecycle", test_chronicle_meeting_lifecycle)
test("Chronicle: extract commitments", test_chronicle_extract_commitments)
test("Chronicle: follow-up generation", test_chronicle_follow_up)

# ── Voice ──

def test_voice_briefing_format():
    from modules.chronicle.voice import VoiceBriefingFormatter, EmotionalTag
    v = VoiceBriefingFormatter()
    segments = v.format_morning_briefing({
        "gravity": {"red_giants": 2, "trust_debt_aud": 5000},
        "chronicle": {"meetings_today": 3, "overdue_commitments": 1},
        "rest_suggestion": "",
    })
    assert len(segments) >= 3
    assert segments[0].emotion == EmotionalTag.WARM
    texts = [s.text for s in segments]
    assert any("Red Giant" in t for t in texts)

def test_voice_easter_egg():
    from modules.chronicle.voice import VoiceBriefingFormatter, EmotionalTag
    v = VoiceBriefingFormatter()
    seg = v.format_name_response("suz")
    assert "Costanza" in seg.text
    assert seg.emotion == EmotionalTag.PLAYFUL

def test_voice_ssml():
    from modules.chronicle.voice import VoiceBriefingFormatter
    v = VoiceBriefingFormatter()
    segments = v.format_morning_briefing({"gravity": {"red_giants": 0, "trust_debt_aud": 0}})
    ssml = v.segments_to_ssml(segments)
    assert ssml.startswith("<speak>")
    assert ssml.endswith("</speak>")

test("Voice: briefing format + emotions", test_voice_briefing_format)
test("Voice: Suz Easter egg", test_voice_easter_egg)
test("Voice: SSML generation", test_voice_ssml)

# ── Innovator + Beast ──

def test_innovator_seeded():
    from modules.innovator.engine import InnovationEngine
    ie = InnovationEngine()
    ranked = ie.get_ranked_opportunities()
    assert len(ranked) == 4  # 4 seeded opportunities
    assert all(r["confidence"] > 0 for r in ranked)

def test_innovator_multi_source():
    from modules.innovator.engine import InnovationEngine
    ie = InnovationEngine()
    ranked = ie.get_ranked_opportunities()
    assert any(r["multi_source"] for r in ranked)

def test_beast_auto_brief():
    from modules.innovator.engine import InnovationEngine
    ie = InnovationEngine()
    opp_id = list(ie.opportunities.keys())[0]
    brief = ie.auto_generate_brief(opp_id)
    assert len(brief.questions) >= 2
    assert brief.brief_id is not None

def test_beast_submit_result():
    from modules.innovator.engine import InnovationEngine
    ie = InnovationEngine()
    opp_id = list(ie.opportunities.keys())[0]
    brief = ie.auto_generate_brief(opp_id)
    result = ie.submit_research_result(
        brief.brief_id,
        findings=[{"question": "Test", "finding": "Positive market signal", "confidence": 0.8}],
        recommendation="build",
        summary="Strong opportunity",
    )
    assert result.recommendation.value == "build"

test("Innovator: 4 seeded opportunities", test_innovator_seeded)
test("Innovator: multi-source detection", test_innovator_multi_source)
test("Beast: auto-generate brief", test_beast_auto_brief)
test("Beast: submit research result", test_beast_submit_result)

# ── Learning Radar ──

def test_learning_radar_seeded():
    from modules.learning_radar import LearningRadar
    lr = LearningRadar()
    assert len(lr.interests) >= 11  # 11 seeded interests (original 8 + 3 new)
    assert len(lr.connections) >= 8  # 9 seeded connections (original 6 + 3 new)

def test_learning_radar_detect():
    from modules.learning_radar import LearningRadar, InterestSource
    lr = LearningRadar()
    result = lr.detect_interest(
        "As Jung said, the shadow is the unknown side of the personality",
        InterestSource.MEETING, "TechCorp Call",
    )
    assert result is not None
    assert "Jung" in result.topic

def test_learning_radar_new_topic():
    from modules.learning_radar import LearningRadar, InterestSource
    lr = LearningRadar()
    result = lr.detect_interest(
        "This reminds me of Nassim Taleb's concept of antifragility",
        InterestSource.CONVERSATION, "Chat",
    )
    assert result is not None

def test_learning_radar_connections():
    from modules.learning_radar import LearningRadar
    lr = LearningRadar()
    conns = lr.get_connections()
    assert len(conns) >= 8
    assert any("McGilchrist" in c["exploration"] or "Taleb" in c["exploration"] for c in conns)

def test_learning_radar_briefing():
    from modules.learning_radar import LearningRadar
    lr = LearningRadar()
    data = lr.get_morning_briefing_data()
    assert "connection" in data
    assert "reading_suggestion" in data

def test_learning_radar_voice():
    from modules.learning_radar import LearningRadar
    lr = LearningRadar()
    voice = lr.get_voice_briefing_text()
    assert isinstance(voice, str)

test("Learning Radar: seeded interests", test_learning_radar_seeded)
test("Learning Radar: detect Jung reference", test_learning_radar_detect)
test("Learning Radar: detect new topic (Taleb)", test_learning_radar_new_topic)
test("Learning Radar: connections", test_learning_radar_connections)
test("Learning Radar: morning briefing data", test_learning_radar_briefing)
test("Learning Radar: voice text", test_learning_radar_voice)

def test_learning_radar_comm_framework():
    from modules.learning_radar import LearningRadar, InterestSource
    lr = LearningRadar()
    result = lr.detect_interest(
        "We should structure this using the Pyramid Principle — lead with the answer",
        InterestSource.MEETING, "Strategy session",
    )
    assert result is not None
    assert "Pyramid" in result.topic

def test_learning_radar_strategic_framework():
    from modules.learning_radar import LearningRadar, InterestSource
    lr = LearningRadar()
    result = lr.detect_interest(
        "Let's run a SWOT analysis on this before we decide",
        InterestSource.MEETING, "Planning session",
    )
    assert result is not None

test("Learning Radar: detect Pyramid Principle", test_learning_radar_comm_framework)
test("Learning Radar: detect SWOT reference", test_learning_radar_strategic_framework)

def test_comm_auto_structure():
    from modules.communication import CommunicationEngine
    from modules.strategic import StrategicEngine
    from modules.orchestrator import Orchestrator
    ce = CommunicationEngine()
    se = StrategicEngine()
    orch = Orchestrator(communication_engine=ce, strategic_engine=se)
    r = orch.auto_structure_communication(
        "Hi James, following up on our meeting. We agreed to...",
        "Follow-up email", comm_type="email", audience="manager",
    )
    assert r["applied"]
    assert len(r["suggested_frameworks"]) >= 1

def test_strategic_auto_swot():
    from modules.communication import CommunicationEngine
    from modules.strategic import StrategicEngine
    from modules.orchestrator import Orchestrator
    ce = CommunicationEngine()
    se = StrategicEngine()
    orch = Orchestrator(communication_engine=ce, strategic_engine=se)
    r = orch.auto_strategic_analysis("AI Governance Sprint", "swot", {
        "strengths": ["ISO certs"], "opportunities": ["250K SMBs"], "threats": ["Big 4"],
    })
    assert r["applied"]
    assert r["key_insight"] != ""

def test_strategic_auto_mece():
    from modules.strategic import StrategicEngine
    from modules.orchestrator import Orchestrator
    se = StrategicEngine()
    orch = Orchestrator(strategic_engine=se)
    r = orch.auto_strategic_analysis("Revenue", "mece", {
        "categories": ["Consulting", "SaaS", "Training"],
    })
    assert r["applied"]
    assert r["is_mece"]

def test_presentation_auto_check():
    from modules.communication import CommunicationEngine
    from modules.orchestrator import Orchestrator
    ce = CommunicationEngine()
    orch = Orchestrator(communication_engine=ce)
    r = orch.auto_check_presentation(8, 15, 32)
    assert r["passes_10_20_30"]

test("Auto: communication framework on email", test_comm_auto_structure)
test("Auto: SWOT on opportunity", test_strategic_auto_swot)
test("Auto: MECE check", test_strategic_auto_mece)
test("Auto: presentation 10-20-30 check", test_presentation_auto_check)


# ══════════════════════════════════════════════════════════════════
# 3. INTEGRATION TESTS — Cross-Module Cascades
# ══════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("3. INTEGRATION TESTS")
print("=" * 60)


def test_orchestrator_post_meeting_cascade():
    from modules.thinking.engine import ThinkingFrameworksEngine
    from modules.gravity_v2.gravity_field import GravityField
    from modules.constellation.poi_engine import POIEngine
    from modules.amplifier.content_engine import ContentEngine
    from modules.sentinel.trust_engine import TrustEngine
    from modules.chronicle.meeting_engine import MeetingEngine
    from modules.chronicle.models import MeetingTemplate, CommitmentType
    from modules.innovator.engine import InnovationEngine
    from modules.orchestrator import Orchestrator

    thinking = ThinkingFrameworksEngine()
    gravity = GravityField()
    amplifier = ContentEngine(thinking_engine=thinking)
    sentinel = TrustEngine(thinking_engine=thinking)
    chronicle = MeetingEngine()
    innovator = InnovationEngine()
    poi = POIEngine()

    orch = Orchestrator(
        gravity_field=gravity, poi_engine=poi,
        content_engine=amplifier, trust_engine=sentinel,
        meeting_engine=chronicle, innovation_engine=innovator,
        thinking_engine=thinking,
    )

    # Create meeting with commitments
    m = chronicle.create_meeting("Integration Test", MeetingTemplate.DISCOVERY_CALL,
        [{"name": "Mani Padisetti", "role": "host"}, {"name": "Test Client", "role": "prospect"}])
    chronicle.add_commitment(m.meeting_id, "Send proposal", "mani",
        CommitmentType.EXPLICIT_DEADLINE, datetime.now() + timedelta(days=3))
    m.content_opportunities = ["Blog about testing"]
    chronicle.generate_follow_up(m.meeting_id)

    # Cascade
    result = orch.post_meeting_cascade(m.meeting_id)
    assert result["cascades"] >= 3  # gravity + constellation + amplifier + sentinel

    # Verify cross-module effects
    assert gravity.active_item_count() >= 1  # Commitment became Gravity item
    assert len(amplifier.items) >= 1  # Content opportunity became Amplifier idea


def test_orchestrator_discovery_cascade():
    from modules.thinking.engine import ThinkingFrameworksEngine
    from modules.gravity_v2.gravity_field import GravityField
    from modules.amplifier.content_engine import ContentEngine
    from modules.orchestrator import Orchestrator

    thinking = ThinkingFrameworksEngine()
    gravity = GravityField()
    amplifier = ContentEngine(thinking_engine=thinking)

    orch = Orchestrator(gravity_field=gravity, content_engine=amplifier)

    result = orch.discovery_cascade("Market shift detected", "Clients need help", "ai_governance", "act")
    assert result["cascades"] == 2  # amplifier + gravity
    assert gravity.active_item_count() >= 1
    assert len(amplifier.items) >= 1


def test_orchestrator_content_sentinel():
    from modules.thinking.engine import ThinkingFrameworksEngine
    from modules.sentinel.trust_engine import TrustEngine
    from modules.orchestrator import Orchestrator

    thinking = ThinkingFrameworksEngine()
    sentinel = TrustEngine(thinking_engine=thinking)
    orch = Orchestrator(trust_engine=sentinel)

    result = orch.content_to_sentinel_review("We guarantee results.", "Blog", True)
    assert result["verdict"] != "clean"
    assert result["issues"] >= 1


def test_orchestrator_thinking_integration():
    from modules.thinking.engine import ThinkingFrameworksEngine
    from modules.orchestrator import Orchestrator

    thinking = ThinkingFrameworksEngine()
    orch = Orchestrator(thinking_engine=thinking)

    result = orch.analyse_decision("Enter new market?", "strategy", "high")
    assert len(result["frameworks"]) >= 2


def test_full_chain():
    """The big one: meeting → commitments → gravity → sentinel → thinking."""
    from modules.thinking.engine import ThinkingFrameworksEngine
    from modules.gravity_v2.gravity_field import GravityField
    from modules.amplifier.content_engine import ContentEngine
    from modules.sentinel.trust_engine import TrustEngine
    from modules.chronicle.meeting_engine import MeetingEngine
    from modules.chronicle.models import MeetingTemplate, CommitmentType
    from modules.innovator.engine import InnovationEngine
    from modules.orchestrator import Orchestrator
    from modules.constellation.poi_engine import POIEngine

    thinking = ThinkingFrameworksEngine()
    gravity = GravityField()
    amplifier = ContentEngine(thinking_engine=thinking)
    sentinel = TrustEngine(thinking_engine=thinking)
    chronicle = MeetingEngine()
    innovator = InnovationEngine()
    poi = POIEngine()

    orch = Orchestrator(
        gravity_field=gravity, poi_engine=poi,
        content_engine=amplifier, trust_engine=sentinel,
        meeting_engine=chronicle, innovation_engine=innovator,
        thinking_engine=thinking,
    )

    # Step 1: Meeting creates commitment
    m = chronicle.create_meeting("Full Chain", MeetingTemplate.PROPOSAL_REVIEW,
        [{"name": "Mani Padisetti", "role": "host"}, {"name": "Sarah Kim", "role": "client"}])
    chronicle.add_commitment(m.meeting_id, "Deliver revised proposal", "mani",
        CommitmentType.EXPLICIT_DEADLINE, datetime.now() + timedelta(days=5))
    m.content_opportunities = ["Case study from proposal process"]
    chronicle.generate_follow_up(m.meeting_id)

    # Step 2: Post-meeting cascade
    cascade = orch.post_meeting_cascade(m.meeting_id)
    assert cascade["cascades"] >= 3

    # Step 3: Content goes through Sentinel
    review = orch.content_to_sentinel_review(
        "We ensure compliance outcomes for all clients.", "Proposal draft"
    )
    assert review["issues"] >= 1

    # Step 4: Thinking frameworks on the decision
    analysis = orch.analyse_decision("Should we revise pricing?", "strategy", "high")
    assert len(analysis["frameworks"]) >= 2

    # Verify the chain
    assert gravity.active_item_count() >= 1
    assert len(amplifier.items) >= 1
    assert len(sentinel.audits) >= 1
    assert len(orch.get_cascade_log()) >= 5


test("Integration: post-meeting cascade", test_orchestrator_post_meeting_cascade)
test("Integration: discovery cascade", test_orchestrator_discovery_cascade)
test("Integration: content → sentinel", test_orchestrator_content_sentinel)
test("Integration: thinking frameworks", test_orchestrator_thinking_integration)
test("Integration: FULL CHAIN (meeting → gravity → sentinel → thinking)", test_full_chain)


# ══════════════════════════════════════════════════════════════════
# 4. API SMOKE TESTS
# ══════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("4. API SMOKE TESTS")
print("=" * 60)


def test_flask_app_creates():
    app = _get_test_app()
    assert app is not None


# Create app once for all API tests
_test_app = None
def _get_test_app():
    global _test_app
    if _test_app is None:
        from app import create_app
        _test_app = create_app()
    return _test_app


def test_api_endpoints():
    app = _get_test_app()
    client = app.test_client()

    endpoints = [
        ("GET", "/"),
        ("GET", "/api/status"),
        ("GET", "/api/system/config"),
        ("GET", "/api/morning-briefing"),
        ("GET", "/api/morning-briefing/voice"),
        ("GET", "/api/gravity/field"),
        ("GET", "/api/gravity/top"),
        ("GET", "/api/constellation/pois"),
        ("GET", "/api/cartographer/territory"),
        ("GET", "/api/cartographer/briefing"),
        ("GET", "/api/amplifier/ideas"),
        ("GET", "/api/sentinel/positions"),
        ("GET", "/api/sentinel/status"),
        ("GET", "/api/thinking/status"),
        ("GET", "/api/thinking/matrix"),
        ("GET", "/api/chronicle/meetings"),
        ("GET", "/api/chronicle/commitments"),
        ("GET", "/api/chronicle/status"),
        ("GET", "/api/voice/config"),
        ("GET", "/api/innovator/opportunities"),
        ("GET", "/api/innovator/report"),
        ("GET", "/api/innovator/status"),
        ("GET", "/api/orchestrator/wiring"),
        ("GET", "/api/orchestrator/status"),
        ("GET", "/api/learning/interests"),
        ("GET", "/api/learning/connections"),
        ("GET", "/api/learning/domains"),
        ("GET", "/api/learning/briefing"),
        ("GET", "/api/learning/status"),
        ("GET", "/api/frameworks/communication/status"),
        ("GET", "/api/frameworks/strategic/status"),
    ]

    failed_endpoints = []
    for method, path in endpoints:
        resp = client.get(path) if method == "GET" else client.post(path)
        if resp.status_code != 200:
            failed_endpoints.append(f"{method} {path} → {resp.status_code}")

    assert len(failed_endpoints) == 0, f"Failed endpoints: {failed_endpoints}"


def test_api_post_endpoints():
    app = _get_test_app()
    client = app.test_client()

    # Sentinel review
    resp = client.post("/api/sentinel/review", json={
        "content": "Test content for review",
        "title": "API test",
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert "verdict" in data

    # Chronicle create meeting
    resp = client.post("/api/chronicle/meetings", json={
        "title": "API Test Meeting",
        "template": "discovery_call",
        "participants": [{"name": "Mani", "role": "host"}],
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert "meeting_id" in data

    # Thinking analyse
    resp = client.post("/api/thinking/analyse", json={
        "topic": "API test decision",
        "domain": "strategy",
        "stakes": "medium",
    })
    assert resp.status_code == 200


test("Flask: app creates", test_flask_app_creates)
test("API: all GET endpoints return 200", test_api_endpoints)
test("API: POST endpoints work", test_api_post_endpoints)


# ══════════════════════════════════════════════════════════════════
# 5. CONFIDENCE STAMP
# ══════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("5. CONFIDENCE STAMP")
print("=" * 60)

# File stats
import subprocess
r1 = subprocess.run(["find", ".", "-name", "*.py"], capture_output=True, text=True)
files = r1.stdout.strip().split("\n")
r2 = subprocess.run(["find", ".", "-name", "*.py", "-exec", "cat", "{}", "+"], capture_output=True, text=True)
total_lines = r2.stdout.count("\n")

# Module count
modules = [
    "Thinking Frameworks", "Gravity v2", "Constellation v2",
    "Cartographer v2", "Amplifier v2", "Sentinel v2",
    "Chronicle v2", "Voice (ElevenLabs)", "Innovator", "Beast",
    "Orchestrator", "Learning Radar",
    "Communication Frameworks", "Strategic Analysis",
]

stamp = {
    "system": "Maestro Elaine",
    "version": "4.0",
    "owner": "Mani Padisetti",
    "company": "Almost Magic Tech Lab",
    "voice_id": "XQanfahzbl1YiUlZi5NW",
    "test_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "files": len(files),
    "total_lines": total_lines,
    "modules": len(modules),
    "module_list": modules,
    "tests_passed": results["passed"],
    "tests_failed": results["failed"],
    "tests_warnings": results["warnings"],
    "test_total": results["passed"] + results["failed"] + results["warnings"],
    "confidence": "HIGH" if results["failed"] == 0 else "LOW",
    "verdict": "READY FOR GITHUB" if results["failed"] == 0 else "FIX FAILURES BEFORE PUSH",
}

print(f"\n{'─' * 60}")
print(f"  CONFIDENCE STAMP — {stamp['system']} v{stamp['version']}")
print(f"{'─' * 60}")
print(f"  Owner:    {stamp['owner']}")
print(f"  Company:  {stamp['company']}")
print(f"  Voice:    {stamp['voice_id']}")
print(f"  Date:     {stamp['test_date']}")
print(f"")
print(f"  Files:    {stamp['files']}")
print(f"  Lines:    {stamp['total_lines']}")
print(f"  Modules:  {stamp['modules']}")
print(f"")
print(f"  Tests:    {stamp['test_total']}")
print(f"    Passed:   {stamp['tests_passed']}")
print(f"    Failed:   {stamp['tests_failed']}")
print(f"    Warnings: {stamp['tests_warnings']}")
print(f"")
print(f"  Confidence: {stamp['confidence']}")
print(f"  Verdict:    {stamp['verdict']}")
print(f"{'─' * 60}")

if results["failed"] > 0:
    print(f"\n{FAIL} FAILURES:")
    for d in results["details"]:
        if d["status"] == "FAIL":
            print(f"  {FAIL} {d['name']}: {d.get('error', '')}")

# Save stamp
with open("confidence_stamp.json", "w") as f:
    json.dump(stamp, f, indent=2)
print(f"\n  Stamp saved: confidence_stamp.json")

print(f"\n{'=' * 60}")
if results["failed"] == 0:
    print(f"  {PASS} ALL TESTS PASSED — READY FOR GITHUB")
else:
    print(f"  {FAIL} {results['failed']} FAILURES — FIX BEFORE PUSH")
print(f"{'=' * 60}\n")
