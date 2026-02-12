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
import io
import json
import traceback
from datetime import datetime, timedelta
from io import StringIO

# Windows console encoding fix for emoji output
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "buffer") and getattr(sys.stdout, "encoding", "") != "utf-8":
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "buffer") and getattr(sys.stderr, "encoding", "") != "utf-8":
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except ValueError:
        pass

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

# ── Compassion Engine ────────────────────────────────────────────

def test_compassion_detect_neutral():
    from modules.compassion import CompassionEngine, EmotionalContext
    ce = CompassionEngine()
    ctx = ce.detect_context("Here are the quarterly results and next steps")
    assert ctx == EmotionalContext.NEUTRAL

def test_compassion_detect_pressure():
    from modules.compassion import CompassionEngine, EmotionalContext
    ce = CompassionEngine()
    ctx = ce.detect_context("I'm overwhelmed with deadlines and running out of time")
    assert ctx == EmotionalContext.HIGH_PRESSURE

def test_compassion_detect_bad_news():
    from modules.compassion import CompassionEngine, EmotionalContext
    ce = CompassionEngine()
    ctx = ce.detect_context("Unfortunately we lost the deal with Acme Corp")
    assert ctx == EmotionalContext.BAD_NEWS

def test_compassion_detect_celebration():
    from modules.compassion import CompassionEngine, EmotionalContext
    ce = CompassionEngine()
    ctx = ce.detect_context("We won the contract and shipped the product! Milestone achieved!")
    assert ctx == EmotionalContext.CELEBRATION

def test_compassion_detect_grief():
    from modules.compassion import CompassionEngine, EmotionalContext
    ce = CompassionEngine()
    ctx = ce.detect_context("My uncle passed away last night")
    assert ctx == EmotionalContext.GRIEF

def test_compassion_detect_overwork():
    from modules.compassion import CompassionEngine, EmotionalContext
    ce = CompassionEngine()
    ctx = ce.detect_context("Normal day", {"hours_today": 14})
    assert ctx == EmotionalContext.OVERWORK

def test_compassion_tone_selection():
    from modules.compassion import CompassionEngine, EmotionalContext, ToneRegister
    ce = CompassionEngine()
    assert ce.select_tone(EmotionalContext.GRIEF) == ToneRegister.QUIET
    assert ce.select_tone(EmotionalContext.HIGH_PRESSURE) == ToneRegister.GROUNDING
    assert ce.select_tone(EmotionalContext.CELEBRATION) == ToneRegister.CELEBRATORY
    assert ce.select_tone(EmotionalContext.CREATIVE) == ToneRegister.QUIET

def test_compassion_frame_response():
    from modules.compassion import CompassionEngine, EmotionalContext
    ce = CompassionEngine()
    r = ce.frame_response(EmotionalContext.BAD_NEWS)
    assert r.tone.value == "warm"
    assert r.should_push == False
    assert r.breathing_room == True
    assert "not easy" in r.opening.lower() or "details" in r.opening.lower()

def test_compassion_frame_grief():
    from modules.compassion import CompassionEngine, EmotionalContext
    ce = CompassionEngine()
    r = ce.frame_response(EmotionalContext.GRIEF)
    assert r.should_push == False
    assert r.breathing_room == True
    assert r.tone.value == "quiet"
    assert len(r.framing_notes) >= 3

def test_compassion_frame_creative():
    from modules.compassion import CompassionEngine, EmotionalContext
    ce = CompassionEngine()
    r = ce.frame_response(EmotionalContext.CREATIVE)
    assert r.opening == ""  # Don't interrupt flow
    assert r.should_push == False
    assert r.breathing_room == True

def test_compassion_wellbeing_tracking():
    from modules.compassion import CompassionEngine, WellbeingLevel
    ce = CompassionEngine()
    ce.log_signal("late_hours", "Worked until 11pm")
    ce.log_signal("late_hours", "Worked until midnight")
    ce.log_signal("late_hours", "Worked until 1am")
    ce.log_signal("no_break", "No lunch break")
    assert ce.wellbeing.consecutive_late_days == 3
    assert ce.wellbeing.level in (WellbeingLevel.STRETCHED, WellbeingLevel.STRAINED, WellbeingLevel.DEPLETED)

def test_compassion_wellbeing_recovery():
    from modules.compassion import CompassionEngine, WellbeingLevel
    ce = CompassionEngine()
    ce.log_signal("win", "Landed new client")
    ce.log_signal("win", "Published article")
    ce.log_signal("win", "Great feedback from partner")
    assert ce.wellbeing.wins_this_week == 3
    assert ce.wellbeing.level in (WellbeingLevel.THRIVING, WellbeingLevel.STEADY)

def test_compassion_morning_briefing():
    from modules.compassion import CompassionEngine
    ce = CompassionEngine()
    data = ce.get_morning_compassion()
    assert "wellbeing_level" in data
    assert "tone" in data
    assert "opening" in data
    assert "stats" in data

def test_compassion_voice_text():
    from modules.compassion import CompassionEngine
    ce = CompassionEngine()
    text = ce.get_voice_compassion_text()
    assert isinstance(text, str)

def test_compassion_status():
    from modules.compassion import CompassionEngine
    ce = CompassionEngine()
    s = ce.status()
    assert "wellbeing_level" in s
    assert "signals_logged" in s

test("Compassion: detect neutral", test_compassion_detect_neutral)
test("Compassion: detect pressure", test_compassion_detect_pressure)
test("Compassion: detect bad news", test_compassion_detect_bad_news)
test("Compassion: detect celebration", test_compassion_detect_celebration)
test("Compassion: detect grief", test_compassion_detect_grief)
test("Compassion: detect overwork (metadata)", test_compassion_detect_overwork)
test("Compassion: tone selection", test_compassion_tone_selection)
test("Compassion: frame bad news", test_compassion_frame_response)
test("Compassion: frame grief (quiet, no push)", test_compassion_frame_grief)
test("Compassion: frame creative (silence)", test_compassion_frame_creative)
test("Compassion: wellbeing degrades under stress", test_compassion_wellbeing_tracking)
test("Compassion: wellbeing recovers with wins", test_compassion_wellbeing_recovery)
test("Compassion: morning briefing data", test_compassion_morning_briefing)
test("Compassion: voice text", test_compassion_voice_text)
test("Compassion: status", test_compassion_status)

# ── Gatekeeper ───────────────────────────────────────────────────

def test_gatekeeper_clear():
    from modules.gatekeeper import Gatekeeper, ContentChannel
    gk = Gatekeeper()
    r = gk.check("Hi team, here are the meeting notes from today.", "Meeting notes", channel=ContentChannel.EMAIL)
    assert r.verdict.value in ("clear", "review")

def test_gatekeeper_priority_detect_sensitive():
    from modules.gatekeeper import Gatekeeper, ContentChannel
    gk = Gatekeeper()
    p = gk.detect_priority("Attached is the pricing proposal with our fee schedule", "client@acme.com")
    assert p.value == "sensitive"

def test_gatekeeper_priority_detect_critical():
    from modules.gatekeeper import Gatekeeper, ContentChannel
    gk = Gatekeeper()
    p = gk.detect_priority("Board presentation for investor meeting", "")
    assert p.value == "critical"

def test_gatekeeper_with_sentinel():
    from modules.sentinel.trust_engine import TrustEngine
    from modules.gatekeeper import Gatekeeper, ContentChannel
    se = TrustEngine()
    gk = Gatekeeper(sentinel=se)
    r = gk.check("We guarantee compliance and will ensure certification.", "Proposal", channel=ContentChannel.PROPOSAL)
    sentinel_check = next((c for c in r.checks if c.gate_name == "sentinel"), None)
    assert sentinel_check is not None
    assert len(sentinel_check.issues) > 0  # "guarantee" and "ensure" flagged

def test_gatekeeper_with_compassion():
    from modules.compassion import CompassionEngine
    from modules.gatekeeper import Gatekeeper, ContentChannel
    ce = CompassionEngine()
    gk = Gatekeeper(compassion=ce)
    r = gk.check("URGENT ASAP need this done immediately, deadline passed!", "Urgent request")
    compassion_check = next((c for c in r.checks if c.gate_name == "compassion"), None)
    assert compassion_check is not None

def test_gatekeeper_with_communication():
    from modules.communication import CommunicationEngine
    from modules.gatekeeper import Gatekeeper, ContentChannel
    ce = CommunicationEngine()
    gk = Gatekeeper(communication=ce)
    r = gk.check("What should we do about the budget? " + "x " * 300, "Long email", channel=ContentChannel.EMAIL)
    comm_check = next((c for c in r.checks if c.gate_name == "communication"), None)
    assert comm_check is not None
    assert len(comm_check.issues) > 0  # Too long + opens with question

def test_gatekeeper_override():
    from modules.gatekeeper import Gatekeeper, GateVerdict
    gk = Gatekeeper()
    r = gk.check("Test content", "Test")
    overridden = gk.override(r.item_id, "I know what I'm doing")
    assert overridden is not None
    assert overridden.verdict == GateVerdict.OVERRIDE

def test_gatekeeper_history():
    from modules.gatekeeper import Gatekeeper
    gk = Gatekeeper()
    gk.check("Test 1", "Email 1")
    gk.check("Test 2", "Email 2")
    history = gk.get_history()
    assert len(history) == 2

def test_gatekeeper_watched_folders():
    from modules.gatekeeper import Gatekeeper
    gk = Gatekeeper()
    folders = gk.get_watched_folders()
    assert len(folders) >= 2  # Default: Outbound + Proposals

def test_gatekeeper_outlook_rules():
    from modules.gatekeeper import Gatekeeper
    gk = Gatekeeper()
    rules = gk.get_outlook_rules()
    assert len(rules) >= 3  # Default: all outbound, proposals, government

def test_gatekeeper_outlook_script():
    from modules.gatekeeper import Gatekeeper
    gk = Gatekeeper()
    script = gk.get_outlook_hook_script()
    assert "win32com" in script
    assert "Outbox" in script

def test_gatekeeper_status():
    from modules.gatekeeper import Gatekeeper
    gk = Gatekeeper()
    gk.check("Test", "Test")
    s = gk.status()
    assert s["items_checked"] == 1

test("Gatekeeper: clean email clears", test_gatekeeper_clear)
test("Gatekeeper: detect sensitive priority", test_gatekeeper_priority_detect_sensitive)
test("Gatekeeper: detect critical priority", test_gatekeeper_priority_detect_critical)
test("Gatekeeper: Sentinel catches 'guarantee'", test_gatekeeper_with_sentinel)
test("Gatekeeper: Compassion checks tone", test_gatekeeper_with_compassion)
test("Gatekeeper: Communication flags structure", test_gatekeeper_with_communication)
test("Gatekeeper: override", test_gatekeeper_override)
test("Gatekeeper: history", test_gatekeeper_history)
test("Gatekeeper: watched folders", test_gatekeeper_watched_folders)
test("Gatekeeper: Outlook rules", test_gatekeeper_outlook_rules)
test("Gatekeeper: Outlook script", test_gatekeeper_outlook_script)
test("Gatekeeper: status", test_gatekeeper_status)


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
        ("GET", "/api/compassion/wellbeing"),
        ("GET", "/api/compassion/status"),
        ("GET", "/api/gatekeeper/status"),
        ("GET", "/api/gatekeeper/folders"),
        ("GET", "/api/gatekeeper/outlook-rules"),
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


# ── 4b. Stabilisation Tests ────────────────────────────────────────

print("\n" + "=" * 60)
print("4b. STABILISATION API TESTS")
print("=" * 60)


def test_health_endpoint():
    app = _get_test_app()
    client = app.test_client()
    resp = client.get("/api/health")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "ELAINE"
    assert "supervisor_connected" in data
    assert "timestamp" in data


def test_modules_endpoint():
    app = _get_test_app()
    client = app.test_client()
    resp = client.get("/api/modules")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "modules" in data
    assert "total" in data
    body_text = resp.get_data(as_text=True).lower()
    for expected in ["gravity", "constellation", "voice", "gatekeeper", "orchestrator"]:
        assert expected in body_text, f"'{expected}' not found in /api/modules"


def test_briefing_alias():
    app = _get_test_app()
    client = app.test_client()
    resp = client.get("/api/briefing")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "gravity" in data
    assert "constellation" in data


def test_frustration_post():
    app = _get_test_app()
    client = app.test_client()
    resp = client.post("/api/frustration", json={"text": "Test frustration entry"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["logged"] is True
    assert "timestamp" in data["entry"]


def test_frustration_empty():
    app = _get_test_app()
    client = app.test_client()
    resp = client.post("/api/frustration", json={"text": ""})
    assert resp.status_code == 400


def test_frustration_get():
    app = _get_test_app()
    client = app.test_client()
    client.post("/api/frustration", json={"text": "Test read-back"})
    resp = client.get("/api/frustration")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "entries" in data
    assert "total" in data


def test_health_contains_healthy():
    app = _get_test_app()
    client = app.test_client()
    resp = client.get("/api/health")
    body = resp.get_data(as_text=True)
    assert "healthy" in body


def test_regression_existing_endpoints():
    app = _get_test_app()
    client = app.test_client()
    for path in ["/", "/api/status", "/api/system/config",
                 "/api/morning-briefing", "/api/morning-briefing/voice"]:
        resp = client.get(path)
        assert resp.status_code == 200, f"Regression: {path} returned {resp.status_code}"


test("Health: /api/health returns 200", test_health_endpoint)
test("Modules: /api/modules lists active modules", test_modules_endpoint)
test("Briefing: /api/briefing alias works", test_briefing_alias)
test("Frustration: POST logs entry", test_frustration_post)
test("Frustration: empty text returns 400", test_frustration_empty)
test("Frustration: GET reads log", test_frustration_get)
test("Health: contains 'healthy' string", test_health_contains_healthy)
test("Regression: existing endpoints still 200", test_regression_existing_endpoints)


# ══════════════════════════════════════════════════════════════════
# 4c. CHAT + TOOLS + SERVICE HEALTH TESTS
# ══════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("4c. CHAT + TOOLS + SERVICE HEALTH TESTS")
print("=" * 60)


def test_import_chat_routes():
    from api_routes_chat import create_chat_routes, TOOLS, SYSTEM_PROMPT
    assert callable(create_chat_routes)
    assert len(TOOLS) >= 10
    assert "Elaine" in SYSTEM_PROMPT


def test_tools_endpoint():
    app = _get_test_app()
    client = app.test_client()
    resp = client.get("/api/tools")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.get_json()
    assert "tools" in data
    assert "total" in data
    assert data["total"] >= 10
    assert "lan_ip" in data
    # Check structure of first tool
    tool = data["tools"][0]
    for key in ("id", "name", "desc", "port", "url", "health", "category"):
        assert key in tool, f"Tool missing key: {key}"


def test_tools_contains_core_services():
    app = _get_test_app()
    client = app.test_client()
    resp = client.get("/api/tools")
    data = resp.get_json()
    ids = [t["id"] for t in data["tools"]]
    for required in ("workshop", "supervisor", "elaine", "ollama"):
        assert required in ids, f"Missing core service: {required}"


def test_tools_contains_business_services():
    app = _get_test_app()
    client = app.test_client()
    resp = client.get("/api/tools")
    data = resp.get_json()
    ids = [t["id"] for t in data["tools"]]
    for expected in ("ripple", "ripple-api", "touchstone", "peterman", "genie"):
        assert expected in ids, f"Missing business service: {expected}"


def test_tools_health_endpoint():
    app = _get_test_app()
    client = app.test_client()
    resp = client.get("/api/tools/health")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.get_json()
    assert "services" in data
    assert "running" in data
    assert "total" in data
    assert "timestamp" in data
    assert isinstance(data["running"], int)
    assert data["total"] >= 10
    # Each service has status + latency_ms
    for svc_id, svc_data in data["services"].items():
        assert "status" in svc_data, f"Service {svc_id} missing status"
        assert svc_data["status"] in ("running", "stopped"), f"Invalid status for {svc_id}"


def test_chat_rejects_empty():
    app = _get_test_app()
    client = app.test_client()
    resp = client.post("/api/chat", json={"message": ""})
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data


def test_chat_rejects_missing_message():
    app = _get_test_app()
    client = app.test_client()
    resp = client.post("/api/chat", json={})
    assert resp.status_code == 400


def test_chat_graceful_when_offline():
    """Chat returns structured response even when Ollama is unreachable."""
    app = _get_test_app()
    client = app.test_client()
    resp = client.post("/api/chat", json={"message": "hello"})
    # Either 200 (if Ollama is running) or 503 (offline) — both valid
    assert resp.status_code in (200, 503), f"Unexpected status: {resp.status_code}"
    data = resp.get_json()
    assert "reply" in data or "error" in data
    assert "via" in data


def test_chat_accepts_history():
    """Chat endpoint accepts conversation history."""
    app = _get_test_app()
    client = app.test_client()
    resp = client.post("/api/chat", json={
        "message": "hello",
        "history": [
            {"role": "user", "content": "previous message"},
            {"role": "assistant", "content": "previous reply"},
        ],
    })
    assert resp.status_code in (200, 503)
    data = resp.get_json()
    assert "via" in data


def test_web_ui_contains_tools():
    """Web UI has tools panel, chat integration, and key features."""
    app = _get_test_app()
    client = app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    for feature in ("tools-grid", "loadToolsHealth", "chatHistory", "typing-dots",
                     "/api/chat", "/api/tools", "AMTL Services"):
        assert feature in html, f"Web UI missing: {feature}"


def test_web_ui_has_dark_light_toggle():
    app = _get_test_app()
    client = app.test_client()
    resp = client.get("/")
    html = resp.get_data(as_text=True)
    assert "toggleTheme" in html
    assert "elaine-theme" in html
    assert 'data-theme="dark"' in html


test("Import: chat routes module", test_import_chat_routes)
test("Tools: /api/tools returns tool registry", test_tools_endpoint)
test("Tools: contains core services", test_tools_contains_core_services)
test("Tools: contains business services", test_tools_contains_business_services)
test("Tools Health: /api/tools/health returns statuses", test_tools_health_endpoint)
test("Chat: rejects empty message", test_chat_rejects_empty)
test("Chat: rejects missing message", test_chat_rejects_missing_message)
test("Chat: graceful when Ollama offline", test_chat_graceful_when_offline)
test("Chat: accepts conversation history", test_chat_accepts_history)
test("Web UI: contains tools + chat features", test_web_ui_contains_tools)
test("Web UI: dark/light theme toggle", test_web_ui_has_dark_light_toggle)


def test_stt_rejects_no_audio():
    """POST /api/stt without audio file returns 400."""
    app = _get_test_app()
    client = app.test_client()
    resp = client.post("/api/stt")
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}"
    data = resp.get_json()
    assert "error" in data


def test_stt_endpoint_exists():
    """POST /api/stt route is registered and accepts audio field."""
    app = _get_test_app()
    client = app.test_client()
    # Send a tiny WAV file (44-byte empty WAV header) to confirm route exists
    import io
    import struct
    # Minimal valid WAV: RIFF header + fmt chunk + empty data chunk
    buf = io.BytesIO()
    sample_rate = 16000
    buf.write(b"RIFF")
    buf.write(struct.pack("<I", 36))  # file size - 8
    buf.write(b"WAVE")
    buf.write(b"fmt ")
    buf.write(struct.pack("<I", 16))  # chunk size
    buf.write(struct.pack("<HHIIHH", 1, 1, sample_rate, sample_rate * 2, 2, 16))
    buf.write(b"data")
    buf.write(struct.pack("<I", 0))   # 0 bytes of audio data
    buf.seek(0)
    resp = client.post(
        "/api/stt",
        data={"audio": (buf, "test.wav", "audio/wav")},
        content_type="multipart/form-data",
    )
    # 200 (transcribed silence) or 500 (whisper error on empty audio) — not 404
    assert resp.status_code != 404, "STT endpoint not registered"
    data = resp.get_json()
    assert "text" in data or "error" in data


def test_web_ui_has_stt_support():
    """Web UI has MediaRecorder/Whisper STT fallback code."""
    app = _get_test_app()
    client = app.test_client()
    resp = client.get("/")
    html = resp.get_data(as_text=True)
    assert "transcribeAudio" in html, "Missing Whisper transcribeAudio function"
    assert "/api/stt" in html, "Missing /api/stt endpoint reference"
    assert "MediaRecorder" in html, "Missing MediaRecorder API usage"
    assert "sttMode" in html, "Missing sttMode detection"


test("STT: rejects request without audio", test_stt_rejects_no_audio)
test("STT: endpoint exists and accepts audio", test_stt_endpoint_exists)
test("Web UI: has Whisper STT fallback", test_web_ui_has_stt_support)


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
    "Compassion Engine",
    "Gatekeeper",
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
