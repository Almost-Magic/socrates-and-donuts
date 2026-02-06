"""
AMTL Thinking — Communication Frameworks Engine
Structured communication for writing, presenting, and persuading.

Frameworks:
1. Pyramid Principle (Minto/McKinsey) — lead with answer, MECE structure
2. SCQA — Situation, Complication, Question, Answer
3. ABT — And, But, Therefore (narrative structure)
4. Rule of Three — cluster information for memorability
5. Story Mountain — dramatic arc for presentations
6. 5S for Communication — Sort, Straighten, Shine, Standardise, Sustain
7. Presentation Delivery — 10-20-30, Signposting, Power Pause

Usage:
    from amtl_thinking.communication import CommunicationEngine
    engine = CommunicationEngine()
    result = engine.pyramid("We should enter the ANZ market", [...])

Almost Magic Tech Lab — Proprietary IP
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

logger = logging.getLogger("amtl.communication")


# ── Enums ────────────────────────────────────────────────────────

class CommunicationType(str, Enum):
    EMAIL = "email"
    PRESENTATION = "presentation"
    PROPOSAL = "proposal"
    REPORT = "report"
    MEETING = "meeting"
    LINKEDIN = "linkedin"
    BLOG = "blog"
    EXECUTIVE_BRIEF = "executive_brief"


class AudienceLevel(str, Enum):
    C_SUITE = "c_suite"           # Time-poor, want the answer first
    MANAGER = "manager"           # Want answer + key supporting logic
    PRACTITIONER = "practitioner" # Want detail + methodology
    GENERAL = "general"           # Need context before conclusion


# ── Framework Results ────────────────────────────────────────────

@dataclass
class PyramidResult:
    """Minto Pyramid Principle structure."""
    answer: str                     # The recommendation (top of pyramid)
    supporting_arguments: list[str] = field(default_factory=list)  # 3 MECE pillars
    evidence: list[list[str]] = field(default_factory=list)        # Data per pillar
    scqa: dict = field(default_factory=dict)  # {situation, complication, question, answer}
    is_mece: bool = False           # Do arguments pass MECE test?
    mece_gaps: list[str] = field(default_factory=list)
    mece_overlaps: list[str] = field(default_factory=list)


@dataclass
class SCQAResult:
    """Situation-Complication-Question-Answer framework."""
    situation: str = ""        # The known context
    complication: str = ""     # What changed / the problem
    question: str = ""         # The strategic question arising
    answer: str = ""           # Your recommendation
    narrative: str = ""        # Combined flowing text


@dataclass
class ABTResult:
    """And-But-Therefore narrative structure."""
    and_statement: str = ""    # Sets the stage (context)
    but_statement: str = ""    # Introduces conflict/tension
    therefore: str = ""        # The resolution/recommendation
    narrative: str = ""        # Combined flowing text


@dataclass
class RuleOfThreeResult:
    """Information clustered for memorability."""
    topic: str = ""
    three_points: list[str] = field(default_factory=list)
    elaborations: list[str] = field(default_factory=list)
    summary_line: str = ""     # One sentence capturing all three


@dataclass
class StoryMountainResult:
    """Dramatic arc for presentations."""
    beginning: str = ""        # Context and setup
    rising_action: str = ""    # Building tension / problem deepening
    climax: str = ""           # The core problem at peak tension
    falling_action: str = ""   # How it gets resolved
    resolution: str = ""       # The new state / recommendation
    call_to_action: str = ""


@dataclass
class FiveSResult:
    """5S Methodology applied to communication."""
    sort_removed: list[str] = field(default_factory=list)      # Noise removed
    straighten_flow: list[str] = field(default_factory=list)    # Logical order
    shine_improvements: list[str] = field(default_factory=list) # Language/clarity fixes
    standardise_templates: list[str] = field(default_factory=list)  # Consistent patterns
    sustain_habits: list[str] = field(default_factory=list)     # Ongoing practices
    before_word_count: int = 0
    after_word_count: int = 0


@dataclass
class PresentationResult:
    """Presentation delivery framework."""
    slides_count: int = 0
    passes_10_20_30: bool = False  # ≤10 slides, ≤20 min, ≥30pt font
    signposts: list[str] = field(default_factory=list)     # Verbal guideposts
    power_pauses: list[str] = field(default_factory=list)  # Where to pause
    opening_hook: str = ""
    closing_call: str = ""
    timing_minutes: int = 0
    recommendations: list[str] = field(default_factory=list)


@dataclass
class CommunicationResult:
    """Combined result from communication analysis."""
    topic: str
    comm_type: CommunicationType
    audience: AudienceLevel
    frameworks_applied: list[str] = field(default_factory=list)
    results: dict = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


# ── The Communication Engine ─────────────────────────────────────

class CommunicationEngine:
    """
    Structured communication frameworks.
    Helps you write, present, and persuade with clarity.
    """

    def __init__(self):
        self._history: list[CommunicationResult] = []
        self._framework_usage: dict[str, int] = {}

    def _track(self, name: str):
        self._framework_usage[name] = self._framework_usage.get(name, 0) + 1

    # ── Pyramid Principle ────────────────────────────────────────

    def pyramid(self, answer: str, supporting_arguments: list[str],
                evidence: list[list[str]] = None,
                situation: str = "", complication: str = "",
                question: str = "") -> PyramidResult:
        """
        Structure communication using Minto's Pyramid Principle.

        answer: Your main recommendation (top of pyramid)
        supporting_arguments: 3 MECE pillars that support the answer
        evidence: List of evidence lists, one per argument
        """
        evidence = evidence or [[] for _ in supporting_arguments]

        # MECE check
        is_mece = True
        gaps = []
        overlaps = []

        if len(supporting_arguments) < 2:
            gaps.append("Need at least 2-3 supporting arguments for a strong pyramid")
            is_mece = False
        if len(supporting_arguments) > 5:
            overlaps.append("More than 5 arguments suggests overlap — try to consolidate")
            is_mece = False

        # Check for obvious overlaps (simple keyword overlap)
        for i, arg1 in enumerate(supporting_arguments):
            for j, arg2 in enumerate(supporting_arguments):
                if i < j:
                    words1 = set(arg1.lower().split())
                    words2 = set(arg2.lower().split())
                    overlap = words1 & words2 - {"the", "and", "is", "to", "of", "a", "in", "for"}
                    if len(overlap) > 2:
                        overlaps.append(f"Arguments {i+1} and {j+1} may overlap on: {', '.join(overlap)}")
                        is_mece = False

        scqa = {}
        if situation or complication or question:
            scqa = {
                "situation": situation,
                "complication": complication,
                "question": question or f"What should we do about {complication.lower()[:50]}?",
                "answer": answer,
            }

        result = PyramidResult(
            answer=answer,
            supporting_arguments=supporting_arguments,
            evidence=evidence,
            scqa=scqa,
            is_mece=is_mece,
            mece_gaps=gaps,
            mece_overlaps=overlaps,
        )
        self._track("pyramid")
        logger.info(f"Pyramid: {answer[:60]} | {len(supporting_arguments)} pillars | MECE: {is_mece}")
        return result

    # ── SCQA ─────────────────────────────────────────────────────

    def scqa(self, situation: str, complication: str,
             question: str = "", answer: str = "") -> SCQAResult:
        """
        Situation-Complication-Question-Answer framework.
        Creates a natural narrative arc for executive communication.
        """
        if not question:
            question = f"How should we respond to {complication.lower()[:60]}?"
        narrative = f"{situation} However, {complication.lower()} This raises the question: {question} Our recommendation: {answer}"

        result = SCQAResult(
            situation=situation,
            complication=complication,
            question=question,
            answer=answer,
            narrative=narrative,
        )
        self._track("scqa")
        logger.info(f"SCQA: {situation[:40]}...")
        return result

    # ── ABT (And, But, Therefore) ────────────────────────────────

    def abt(self, and_statement: str, but_statement: str,
            therefore: str) -> ABTResult:
        """
        And-But-Therefore narrative structure.
        Quick, punchy storytelling for any context.
        """
        narrative = f"{and_statement} But {but_statement.lower()} Therefore, {therefore.lower()}"
        result = ABTResult(
            and_statement=and_statement,
            but_statement=but_statement,
            therefore=therefore,
            narrative=narrative,
        )
        self._track("abt")
        logger.info(f"ABT: {and_statement[:40]}...")
        return result

    # ── Rule of Three ────────────────────────────────────────────

    def rule_of_three(self, topic: str, three_points: list[str],
                       elaborations: list[str] = None) -> RuleOfThreeResult:
        """
        Cluster information into three memorable points.
        """
        if len(three_points) != 3:
            # Force to 3 — truncate or pad
            three_points = (three_points + ["", "", ""])[:3]

        elaborations = elaborations or [""] * 3
        summary = f"{topic}: {three_points[0]}, {three_points[1]}, and {three_points[2]}."

        result = RuleOfThreeResult(
            topic=topic,
            three_points=three_points,
            elaborations=(elaborations + [""] * 3)[:3],
            summary_line=summary,
        )
        self._track("rule_of_three")
        logger.info(f"Rule of Three: {topic[:40]}")
        return result

    # ── Story Mountain ───────────────────────────────────────────

    def story_mountain(self, beginning: str, rising_action: str,
                        climax: str, falling_action: str,
                        resolution: str, call_to_action: str = "") -> StoryMountainResult:
        """
        Dramatic arc structure for presentations and narratives.
        """
        result = StoryMountainResult(
            beginning=beginning,
            rising_action=rising_action,
            climax=climax,
            falling_action=falling_action,
            resolution=resolution,
            call_to_action=call_to_action,
        )
        self._track("story_mountain")
        logger.info(f"Story Mountain: {beginning[:40]}...")
        return result

    # ── 5S for Communication ─────────────────────────────────────

    def five_s(self, content: str, context: dict = None) -> FiveSResult:
        """
        Apply 5S methodology to communication.
        Sort (remove noise), Straighten (logical flow), Shine (clarity),
        Standardise (consistent), Sustain (habits).
        """
        ctx = context or {}
        words = len(content.split())

        result = FiveSResult(
            sort_removed=ctx.get("sort_removed", []),
            straighten_flow=ctx.get("straighten_flow", []),
            shine_improvements=ctx.get("shine_improvements", []),
            standardise_templates=ctx.get("standardise_templates", []),
            sustain_habits=ctx.get("sustain_habits", [
                "Lead every email with the action required",
                "Use consistent headers across all documents",
                "Review against Pyramid Principle before sending",
            ]),
            before_word_count=words,
            after_word_count=ctx.get("after_word_count", words),
        )
        self._track("five_s")
        logger.info(f"5S Communication: {words} words analysed")
        return result

    # ── Presentation Delivery ────────────────────────────────────

    def presentation_check(self, slides_count: int, timing_minutes: int,
                            min_font_size: int = 30,
                            key_moments: list[str] = None) -> PresentationResult:
        """
        Check presentation against 10-20-30 rule and generate delivery guidance.
        """
        passes = slides_count <= 10 and timing_minutes <= 20 and min_font_size >= 30

        signposts = [
            "Let me start by showing you where we are today.",
            "That brings us to the core challenge.",
            "Here's what the data tells us.",
            "So what does this mean for us?",
            "Let me leave you with three things.",
        ]

        power_pauses = key_moments or [
            "After stating your main recommendation — pause 3 seconds",
            "Before the 'But' in any ABT structure — pause 2 seconds",
            "After showing a surprising data point — pause 3 seconds",
            "Before your closing call to action — pause 2 seconds",
        ]

        recommendations = []
        if slides_count > 10:
            recommendations.append(f"Reduce from {slides_count} to ≤10 slides — cut supporting detail to appendix")
        if timing_minutes > 20:
            recommendations.append(f"Trim from {timing_minutes} to ≤20 minutes — respect attention spans")
        if min_font_size < 30:
            recommendations.append(f"Increase minimum font from {min_font_size}pt to ≥30pt — if they can't read it, remove it")
        if not recommendations:
            recommendations.append("Passes 10-20-30 rule ✓")

        result = PresentationResult(
            slides_count=slides_count,
            passes_10_20_30=passes,
            signposts=signposts[:slides_count],
            power_pauses=power_pauses,
            timing_minutes=timing_minutes,
            recommendations=recommendations,
        )
        self._track("presentation")
        logger.info(f"Presentation check: {slides_count} slides, {timing_minutes}min, 10-20-30: {passes}")
        return result

    # ── Auto-Select Based on Type + Audience ─────────────────────

    def suggest_frameworks(self, comm_type: CommunicationType,
                            audience: AudienceLevel) -> list[str]:
        """Suggest which communication frameworks to apply."""
        suggestions = {
            (CommunicationType.EMAIL, AudienceLevel.C_SUITE): ["pyramid", "scqa"],
            (CommunicationType.EMAIL, AudienceLevel.MANAGER): ["pyramid", "rule_of_three"],
            (CommunicationType.EMAIL, AudienceLevel.PRACTITIONER): ["five_s"],
            (CommunicationType.PRESENTATION, AudienceLevel.C_SUITE): ["pyramid", "story_mountain", "presentation"],
            (CommunicationType.PRESENTATION, AudienceLevel.MANAGER): ["pyramid", "abt", "presentation"],
            (CommunicationType.PRESENTATION, AudienceLevel.GENERAL): ["story_mountain", "rule_of_three", "presentation"],
            (CommunicationType.PROPOSAL, AudienceLevel.C_SUITE): ["pyramid", "scqa", "rule_of_three"],
            (CommunicationType.PROPOSAL, AudienceLevel.MANAGER): ["pyramid", "abt"],
            (CommunicationType.REPORT, AudienceLevel.C_SUITE): ["pyramid", "scqa"],
            (CommunicationType.REPORT, AudienceLevel.PRACTITIONER): ["five_s", "rule_of_three"],
            (CommunicationType.LINKEDIN, AudienceLevel.GENERAL): ["abt", "rule_of_three"],
            (CommunicationType.BLOG, AudienceLevel.GENERAL): ["story_mountain", "abt"],
            (CommunicationType.EXECUTIVE_BRIEF, AudienceLevel.C_SUITE): ["pyramid", "scqa", "rule_of_three"],
        }
        key = (comm_type, audience)
        return suggestions.get(key, ["pyramid", "rule_of_three"])

    # ── Combined Analysis ────────────────────────────────────────

    def analyse(self, topic: str, comm_type: CommunicationType,
                audience: AudienceLevel, context: dict = None) -> CommunicationResult:
        """
        Run communication analysis with auto-suggested frameworks.
        """
        ctx = context or {}
        frameworks = self.suggest_frameworks(comm_type, audience)

        results = {}
        for fw in frameworks:
            if fw == "pyramid" and ctx.get("pyramid"):
                p = ctx["pyramid"]
                results["pyramid"] = self.pyramid(
                    p.get("answer", ""), p.get("arguments", []),
                    situation=p.get("situation", ""),
                    complication=p.get("complication", ""),
                )
            elif fw == "scqa" and ctx.get("scqa"):
                s = ctx["scqa"]
                results["scqa"] = self.scqa(s.get("situation", ""), s.get("complication", ""),
                                             s.get("question", ""), s.get("answer", ""))
            elif fw == "abt" and ctx.get("abt"):
                a = ctx["abt"]
                results["abt"] = self.abt(a.get("and", ""), a.get("but", ""), a.get("therefore", ""))

        result = CommunicationResult(
            topic=topic,
            comm_type=comm_type,
            audience=audience,
            frameworks_applied=frameworks,
            results=results,
            recommendations=[f"Apply {fw} framework" for fw in frameworks if fw not in results],
        )
        self._history.append(result)
        logger.info(f"Communication analysis: {topic[:40]} | {comm_type.value} | {audience.value} | {len(frameworks)} frameworks")
        return result

    # ── Reporting ────────────────────────────────────────────────

    def status(self) -> dict:
        return {
            "total_analyses": len(self._history),
            "framework_usage": self._framework_usage,
        }
