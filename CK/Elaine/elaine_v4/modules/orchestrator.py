"""
Elaine v4 — The Orchestrator
Cross-module intelligence wiring.

This is where Elaine becomes more than the sum of her parts.
Every action in one module cascades to the others:

  Chronicle commitment → Gravity item (auto)
  Cartographer discovery → Amplifier content idea (auto)
  Amplifier content → Sentinel quality gate (auto)
  Sentinel incident → Gravity priority boost (auto)
  Meeting follow-up → Sentinel review (auto)
  Innovator opportunity → Beast research brief (auto)
  Override outcome → Sentinel learning (auto)

Patentable: Cross-System Intelligence Propagation Engine

Almost Magic Tech Lab — Patentable IP
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger("elaine.orchestrator")


class Orchestrator:
    """
    Wires all Elaine modules together.
    Receives references to each engine at init,
    then provides cascade methods that trigger cross-module actions.
    """

    def __init__(self, gravity_field=None, poi_engine=None,
                 territory_map=None, discovery_engine=None,
                 content_engine=None, trust_engine=None,
                 meeting_engine=None, innovation_engine=None,
                 thinking_engine=None, voice_formatter=None,
                 learning_radar=None, communication_engine=None,
                 strategic_engine=None, compassion_engine=None):
        self.gravity = gravity_field
        self.constellation = poi_engine
        self.cartographer_map = territory_map
        self.cartographer = discovery_engine
        self.amplifier = content_engine
        self.sentinel = trust_engine
        self.chronicle = meeting_engine
        self.innovator = innovation_engine
        self.thinking = thinking_engine
        self.voice = voice_formatter
        self.learning = learning_radar
        self.communication = communication_engine
        self.strategic = strategic_engine
        self.compassion = compassion_engine

        self._cascade_log: list[dict] = []

    def _log(self, source: str, target: str, action: str, detail: str = ""):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "source": source,
            "target": target,
            "action": action,
            "detail": detail,
        }
        self._cascade_log.append(entry)
        logger.info(f"CASCADE: {source} → {target}: {action}")

    # ── Chronicle → Gravity ──────────────────────────────────────
    # When a commitment is extracted, auto-create a Gravity item

    def commitment_to_gravity(self, commitment_text: str, owner: str,
                               mass: int = 70, due_date: datetime = None,
                               trust_stake: str = "high") -> Optional[str]:
        """Convert a meeting commitment into a Gravity item."""
        if not self.gravity:
            return None

        if owner != "mani":
            return None

        proximity = 7
        if due_date:
            days_until = (due_date - datetime.now()).days
            proximity = max(1, days_until)

        from modules.gravity_v2.models import GravityItem
        item = GravityItem(
            title=commitment_text[:80],
            mass=mass,
            proximity_date=due_date or (datetime.now() + timedelta(days=proximity)),
            description=f"Commitment ({trust_stake})",
        )
        added = self.gravity.add_item(item)

        self._log("chronicle", "gravity", "commitment_to_item",
                   f"'{commitment_text[:40]}' → mass {mass}, proximity {proximity}")
        return added.id

    # ── Cartographer → Amplifier ─────────────────────────────────
    # When a discovery passes the actionability gate, suggest content

    def discovery_to_content_idea(self, discovery_title: str,
                                    so_what: str, territory: str) -> Optional[str]:
        """Convert a Cartographer discovery into an Amplifier content idea."""
        if not self.amplifier:
            return None

        from modules.amplifier.models import ContentPillar, EpistemicLevel, ContentObjective

        # Map territory to content pillar
        pillar_map = {
            "ai_governance": ContentPillar.AI_GOVERNANCE,
            "cybersecurity": ContentPillar.CYBERSECURITY,
            "business_strategy": ContentPillar.THOUGHT_LEADERSHIP,
            "ai_agents": ContentPillar.AI_GOVERNANCE,
            "building_in_public": ContentPillar.BUILDING_IN_PUBLIC,
        }
        pillar = pillar_map.get(territory, ContentPillar.AI_GOVERNANCE)

        idea = self.amplifier.create_idea(
            title=f"From discovery: {discovery_title[:60]}",
            thesis=so_what,
            pillar=pillar,
            certainty=EpistemicLevel.PROVISIONAL,
            objective=ContentObjective.AUTHORITY,
        )

        self._log("cartographer", "amplifier", "discovery_to_idea",
                   f"'{discovery_title[:40]}' → content idea")
        return idea.content_id if idea else None

    # ── Amplifier → Sentinel ─────────────────────────────────────
    # Before publishing, content passes through Sentinel quality gate

    def content_to_sentinel_review(self, content_text: str,
                                     title: str = "",
                                     is_public: bool = True) -> dict:
        """Run content through Sentinel before publishing."""
        if not self.sentinel:
            return {"verdict": "no_sentinel"}

        audit = self.sentinel.review(
            content=content_text,
            title=title,
            document_type="content",
            is_public=is_public,
        )

        self._log("amplifier", "sentinel", "content_review",
                   f"'{title[:40]}' → {audit.verdict.value}")
        return {
            "audit_id": audit.audit_id,
            "verdict": audit.verdict.value,
            "trust_score": audit.weighted_trust_score,
            "issues": len(audit.risk_items),
        }

    # ── Sentinel → Gravity ───────────────────────────────────────
    # Position conflicts or incidents create priority items

    def sentinel_alert_to_gravity(self, alert_type: str,
                                    description: str, urgency: int = 80):
        """Convert a Sentinel alert into a Gravity priority item."""
        if not self.gravity:
            return

        from modules.gravity_v2.models import GravityItem
        item = GravityItem(
            title=f"[Sentinel] {description[:60]}",
            mass=urgency,
            proximity_date=datetime.now() + timedelta(days=2),
            description="Sentinel alert — requires attention",
        )
        self.gravity.add_item(item)

        self._log("sentinel", "gravity", "alert_to_priority",
                   f"'{description[:40]}' → mass {urgency}")

    # ── Chronicle → Constellation ────────────────────────────────
    # Meeting participants auto-update POI profiles

    def meeting_to_poi_update(self, participant_name: str,
                                company: str = "", notes: str = ""):
        """Update POI profile from meeting intelligence."""
        if not self.constellation:
            return

        # Check if POI exists, update last contact
        for poi in self.constellation.pois.values():
            if poi.name.lower() == participant_name.lower():
                poi.last_contact = datetime.now()
                self._log("chronicle", "constellation", "poi_updated",
                           f"'{participant_name}' last contact updated")
                return

        self._log("chronicle", "constellation", "poi_not_found",
                   f"'{participant_name}' — consider adding as POI")

    # ── Chronicle → Amplifier ────────────────────────────────────
    # Content opportunities from meetings

    def meeting_to_content_opportunities(self, opportunities: list[str],
                                           meeting_title: str):
        """Convert meeting content opportunities to Amplifier ideas."""
        if not self.amplifier:
            return

        from modules.amplifier.models import ContentPillar, EpistemicLevel, ContentObjective

        for opp in opportunities[:3]:  # Max 3 per meeting
            self.amplifier.create_idea(
                title=opp,
                thesis=f"Opportunity detected in meeting: {meeting_title}",
                pillar=ContentPillar.AI_GOVERNANCE,
                certainty=EpistemicLevel.EXPLORATORY,
                objective=ContentObjective.PIPELINE,
            )
            self._log("chronicle", "amplifier", "meeting_to_idea", opp[:40])

    # ── Innovator → Beast Auto-Brief ─────────────────────────────
    # High-confidence opportunities auto-trigger research

    def opportunity_to_research(self, opportunity_id: str,
                                  confidence_threshold: float = 0.75) -> Optional[str]:
        """Auto-delegate high-confidence opportunities to Beast."""
        if not self.innovator:
            return None

        opp = self.innovator.opportunities.get(opportunity_id)
        if not opp or opp.composite_confidence < confidence_threshold:
            return None

        brief = self.innovator.auto_generate_brief(opportunity_id)
        self._log("innovator", "beast", "auto_research",
                   f"'{opp.title[:40]}' → {len(brief.questions)} questions")
        return brief.brief_id

    # ── Thinking Frameworks → Any Module ─────────────────────────
    # Strategic analysis available to all modules

    def analyse_decision(self, topic: str, domain: str = "strategy",
                          stakes: str = "high") -> dict:
        """Run Thinking Frameworks analysis for any module."""
        if not self.thinking:
            return {"frameworks": 0}

        from modules.thinking.engine import DecisionDomain, StakesLevel
        domain_enum = DecisionDomain(domain)
        stakes_enum = StakesLevel(stakes)

        result = self.thinking.analyse(topic, domain_enum, stakes_enum)
        self._log("thinking", "any", "analysis",
                   f"'{topic[:40]}' → {len(result.frameworks_applied)} frameworks")
        return {
            "topic": topic,
            "frameworks": [f.value for f in result.frameworks_applied],
            "synthesis": result.synthesis,
            "warnings": result.warnings,
        }

    # ── Full Cascade: Post-Meeting ───────────────────────────────
    # The big one: after a meeting, cascade everything

    def post_meeting_cascade(self, meeting_id: str) -> dict:
        """
        Full cascade after a meeting ends.
        This is Elaine being a Chief of Staff.
        """
        if not self.chronicle:
            return {"cascades": 0}

        meeting = self.chronicle.get_meeting(meeting_id)
        if not meeting:
            return {"error": "Meeting not found"}

        cascades = []

        # 1. Commitments → Gravity
        for c in meeting.commitments:
            if c.owner == "mani":
                self.commitment_to_gravity(
                    c.text, c.owner, c.default_mass, c.due_date, c.trust_stake.value
                )
                cascades.append(f"commitment → gravity: {c.text[:30]}")

        # 2. Participants → Constellation
        for p in meeting.participants:
            if p.role != "host":
                self.meeting_to_poi_update(p.name, p.company)
                cascades.append(f"participant → constellation: {p.name}")

        # 3. Content opportunities → Amplifier
        if meeting.content_opportunities:
            self.meeting_to_content_opportunities(
                meeting.content_opportunities, meeting.title
            )
            cascades.append(f"content opps → amplifier: {len(meeting.content_opportunities)}")

        # 4. Follow-up → Sentinel review + Communication framework
        if meeting.follow_up and meeting.follow_up.body:
            result = self.content_to_sentinel_review(
                meeting.follow_up.body, meeting.follow_up.subject
            )
            meeting.follow_up.sentinel_checked = True
            meeting.follow_up.sentinel_verdict = result.get("verdict", "")
            cascades.append(f"follow-up → sentinel: {result.get('verdict')}")

            # Auto-apply Pyramid/SCQA to follow-up email
            if self.communication:
                comm_result = self.auto_structure_communication(
                    meeting.follow_up.body, meeting.follow_up.subject,
                    comm_type="email", audience="manager",
                )
                cascades.append(f"follow-up → communication: {len(comm_result.get('suggested_frameworks', []))} frameworks")

        # 5. Intelligence → Cartographer territory enrichment
        if meeting.intelligence.hot_buttons:
            self._log("chronicle", "cartographer", "territory_enrichment",
                       f"Hot buttons: {meeting.intelligence.hot_buttons}")
            cascades.append(f"intelligence → cartographer: {len(meeting.intelligence.hot_buttons)} signals")

        # 6. Transcript/summary → Learning Radar (detect intellectual interests)
        if self.learning and meeting.summary:
            from modules.learning_radar import InterestSource
            result = self.learning.detect_interest(
                meeting.summary, InterestSource.MEETING, meeting.title
            )
            if result:
                cascades.append(f"meeting → learning_radar: detected '{result.topic}'")
                self._log("chronicle", "learning_radar", "interest_detected", result.topic)

        # 7. Summary → Compassion (detect emotional context)
        if self.compassion and meeting.summary:
            context = self.compassion.detect_context(meeting.summary)
            if context.value != "neutral":
                response = self.compassion.frame_response(context, meeting.title)
                cascades.append(f"meeting → compassion: {context.value} → tone={response.tone.value}")
                self._log("chronicle", "compassion", "context_detected",
                           f"{context.value} — {response.tone.value}")

        self._log("orchestrator", "all", "post_meeting_cascade",
                   f"{meeting.title}: {len(cascades)} cascades")

        return {
            "meeting": meeting.title,
            "cascades": len(cascades),
            "details": cascades,
        }

    # ── Full Cascade: New Discovery ──────────────────────────────

    def discovery_cascade(self, discovery_title: str,
                           so_what: str, territory: str,
                           actionability: str = "act") -> dict:
        """Cascade a new discovery across all relevant modules."""
        cascades = []

        # 1. Discovery → Amplifier content idea
        if actionability in ("act", "prepare"):
            self.discovery_to_content_idea(discovery_title, so_what, territory)
            cascades.append("discovery → amplifier idea")

        # 2. If urgent → Gravity item
        if actionability == "act":
            self.sentinel_alert_to_gravity(
                "discovery", f"Act on: {discovery_title[:50]}", urgency=65
            )
            cascades.append("discovery → gravity priority")

        return {"cascades": len(cascades), "details": cascades}

    # ── Auto-Apply Communication Frameworks ─────────────────────
    # These fire automatically when content is created or reviewed

    def auto_structure_communication(self, content: str, title: str,
                                       comm_type: str = "email",
                                       audience: str = "c_suite") -> dict:
        """
        Auto-apply communication frameworks to any outbound content.
        Called by Sentinel review, Chronicle follow-ups, Amplifier content.
        Returns structuring suggestions without blocking.
        """
        if not self.communication:
            return {"applied": False}

        from modules.communication import CommunicationType, AudienceLevel
        ct = CommunicationType(comm_type)
        al = AudienceLevel(audience)

        suggested = self.communication.suggest_frameworks(ct, al)
        result = {
            "applied": True,
            "comm_type": comm_type,
            "audience": audience,
            "suggested_frameworks": suggested,
            "checks": {},
        }

        # Auto-run 5S on any content
        five_s = self.communication.five_s(content)
        result["checks"]["word_count"] = five_s.before_word_count
        result["checks"]["sustain_habits"] = five_s.sustain_habits

        self._log("communication", "auto", "structure_check",
                   f"'{title[:40]}' → {len(suggested)} frameworks suggested")
        return result

    def auto_check_presentation(self, slides: int, minutes: int,
                                  font_size: int = 30) -> dict:
        """Auto-check any presentation against 10-20-30 rule."""
        if not self.communication:
            return {"applied": False}

        result = self.communication.presentation_check(slides, minutes, font_size)
        self._log("communication", "auto", "presentation_check",
                   f"{slides} slides, {minutes}min, 10-20-30: {result.passes_10_20_30}")
        return {
            "passes_10_20_30": result.passes_10_20_30,
            "recommendations": result.recommendations,
            "signposts": result.signposts,
            "power_pauses": result.power_pauses,
        }

    # ── Auto-Apply Strategic Frameworks ──────────────────────────
    # These fire automatically when opportunities or discoveries arise

    def auto_strategic_analysis(self, topic: str,
                                  analysis_type: str = "swot",
                                  context: dict = None) -> dict:
        """
        Auto-apply strategic framework to opportunities or discoveries.
        Called by Innovator (new opportunity), Cartographer (territory assessment).
        """
        if not self.strategic:
            return {"applied": False}

        ctx = context or {}
        result = {"applied": True, "framework": analysis_type, "topic": topic}

        if analysis_type == "swot":
            swot = self.strategic.swot(topic,
                strengths=ctx.get("strengths", []),
                weaknesses=ctx.get("weaknesses", []),
                opportunities=ctx.get("opportunities", []),
                threats=ctx.get("threats", []),
            )
            result["key_insight"] = swot.key_insight
            result["priority_action"] = swot.priority_action
        elif analysis_type == "mece":
            mece = self.strategic.mece_check(topic, ctx.get("categories", []))
            result["is_mece"] = mece.is_mece
            result["gaps"] = mece.gaps
            result["overlaps"] = mece.overlaps
        elif analysis_type == "pestle":
            pestle = self.strategic.pestle(topic, **{
                k: ctx.get(k, []) for k in
                ["political", "economic", "social", "technological", "legal", "environmental"]
            })
            result["highest_impact"] = pestle.highest_impact_factor
        elif analysis_type == "bcg":
            bcg = self.strategic.bcg_matrix(topic, ctx.get("items", []))
            result["portfolio_balance"] = bcg.portfolio_balance
            result["items"] = [{"name": i.name, "quadrant": i.quadrant.value} for i in bcg.items]

        self._log("strategic", "auto", analysis_type,
                   f"'{topic[:40]}' → {analysis_type}")
        return result

    # ── Reporting ────────────────────────────────────────────────

    def get_cascade_log(self, limit: int = 50) -> list[dict]:
        return self._cascade_log[-limit:]

    def get_wiring_diagram(self) -> dict:
        """Return the module wiring map."""
        return {
            "chronicle_to": ["gravity", "constellation", "amplifier", "sentinel", "learning_radar", "communication"],
            "cartographer_to": ["amplifier", "gravity", "strategic"],
            "amplifier_to": ["sentinel", "communication"],
            "sentinel_to": ["gravity", "thinking_frameworks"],
            "innovator_to": ["beast", "strategic"],
            "thinking_to": ["sentinel", "gravity", "constellation", "amplifier", "cartographer"],
            "beast_to": ["innovator"],
            "gravity_to": ["thinking_frameworks"],
            "communication_auto": ["follow-ups", "content", "presentations", "proposals"],
            "strategic_auto": ["opportunities", "territories", "portfolio"],
            "learning_radar_from": ["chronicle", "amplifier", "cartographer", "conversation"],
            "compassion_from": ["chronicle", "gravity", "voice", "conversation"],
            "compassion_to": ["voice", "morning_briefing"],
        }

    def status(self) -> dict:
        return {
            "cascades_executed": len(self._cascade_log),
            "modules_connected": sum(1 for m in [
                self.gravity, self.constellation, self.cartographer,
                self.amplifier, self.sentinel, self.chronicle,
                self.innovator, self.thinking, self.voice, self.learning,
                self.communication, self.strategic, self.compassion,
            ] if m is not None),
            "wiring": self.get_wiring_diagram(),
        }
