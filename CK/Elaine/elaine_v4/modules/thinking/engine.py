"""
Thinking Frameworks Engine v1
The Oracle Layer — embeds structured thinking into every decision.

Six frameworks, applied automatically or on request:
1. Second-Order Thinking — "And then what?"
2. Systems Thinking — feedback loops, leverage points
3. Six Thinking Hats — multi-perspective analysis
4. Pre-Mortem — "Assume this failed. Why?"
5. First Principles — strip assumptions, rebuild
6. Inversion — "What guarantees failure?"

Patentable: Multi-Framework Decision Intelligence with Auto-Application

Almost Magic Tech Lab — Patentable IP
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

logger = logging.getLogger("elaine.thinking")


# ── Enums ────────────────────────────────────────────────────────

class FrameworkType(str, Enum):
    SECOND_ORDER = "second_order"
    SYSTEMS = "systems"
    SIX_HATS = "six_hats"
    PRE_MORTEM = "pre_mortem"
    FIRST_PRINCIPLES = "first_principles"
    INVERSION = "inversion"


class StakesLevel(str, Enum):
    LOW = "low"           # Routine, reversible
    MEDIUM = "medium"     # Moderate impact, partially reversible
    HIGH = "high"         # Significant impact, hard to reverse
    CRITICAL = "critical" # Business-defining, irreversible


class DecisionDomain(str, Enum):
    CONTENT = "content"         # Amplifier — publishing decisions
    PRIORITY = "priority"       # Gravity — task/project prioritisation
    RELATIONSHIP = "relationship"  # Constellation — people decisions
    STRATEGY = "strategy"       # Business/market decisions
    PROPOSAL = "proposal"       # Client proposals
    FINANCIAL = "financial"     # Spending, pricing, investment
    TECHNOLOGY = "technology"   # Architecture, tool choices
    COMMUNICATION = "communication"  # Emails, messages, presentations


# ── Data Models ──────────────────────────────────────────────────

@dataclass
class SecondOrderResult:
    action: str
    first_order: str   # Immediate consequence
    second_order: str  # What the first consequence causes
    third_order: str   # What the second consequence causes
    hidden_risks: list[str] = field(default_factory=list)
    hidden_opportunities: list[str] = field(default_factory=list)
    recommendation: str = ""


@dataclass
class SystemsMapResult:
    topic: str
    components: list[dict] = field(default_factory=list)     # {name, role, type}
    feedback_loops: list[dict] = field(default_factory=list)  # {name, type: reinforcing|balancing, components}
    leverage_points: list[dict] = field(default_factory=list) # {point, impact, effort}
    delays: list[dict] = field(default_factory=list)          # {where, duration, consequence}
    resistance_points: list[str] = field(default_factory=list)
    recommendation: str = ""


@dataclass
class SixHatsResult:
    question: str
    white_hat: str = ""   # Facts, data, what we know and don't know
    red_hat: str = ""     # Feelings, intuition, gut reaction
    black_hat: str = ""   # Risks, dangers, difficulties
    yellow_hat: str = ""  # Benefits, optimism, best-case
    green_hat: str = ""   # Alternatives, creative ideas
    blue_hat: str = ""    # Process meta: summary and next steps
    synthesis: str = ""   # Combined recommendation


@dataclass
class FailureScenario:
    scenario: str
    probability: float  # 0.0-1.0
    severity: str       # mild, moderate, severe, catastrophic
    mitigation: str = ""
    early_warning: str = ""


@dataclass
class PreMortemResult:
    plan: str
    failure_scenarios: list[FailureScenario] = field(default_factory=list)
    top_risk: str = ""
    mitigation_plan: str = ""
    kill_criteria: list[str] = field(default_factory=list)  # When to abandon
    confidence_after_analysis: float = 0.0  # 0-1, how confident after seeing risks


@dataclass
class FirstPrinciplesResult:
    question: str
    stated_belief: str = ""
    assumptions_identified: list[str] = field(default_factory=list)
    fundamental_truths: list[str] = field(default_factory=list)
    rebuilt_answer: str = ""
    conventional_vs_fundamental: str = ""  # How the answers differ


@dataclass
class InversionResult:
    goal: str
    guaranteed_failures: list[str] = field(default_factory=list)
    inversions: list[dict] = field(default_factory=list)  # {failure, avoidance_strategy}
    hidden_risks: list[str] = field(default_factory=list)
    anti_checklist: list[str] = field(default_factory=list)  # "Never do these"


@dataclass
class ThinkingResult:
    """Combined result from one or more frameworks."""
    topic: str
    domain: DecisionDomain
    stakes: StakesLevel
    frameworks_applied: list[FrameworkType] = field(default_factory=list)
    results: dict = field(default_factory=dict)  # framework_type → result
    synthesis: str = ""
    confidence: float = 0.0
    recommended_action: str = ""
    warnings: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


# ── Framework Auto-Selection ─────────────────────────────────────

# Which frameworks to apply based on domain and stakes
FRAMEWORK_MATRIX = {
    # (domain, stakes) → [frameworks]
    # Low stakes: minimal analysis
    (DecisionDomain.CONTENT, StakesLevel.LOW): [FrameworkType.INVERSION],
    (DecisionDomain.PRIORITY, StakesLevel.LOW): [],
    (DecisionDomain.COMMUNICATION, StakesLevel.LOW): [],

    # Medium stakes: 1-2 frameworks
    (DecisionDomain.CONTENT, StakesLevel.MEDIUM): [FrameworkType.PRE_MORTEM, FrameworkType.INVERSION],
    (DecisionDomain.PRIORITY, StakesLevel.MEDIUM): [FrameworkType.SECOND_ORDER],
    (DecisionDomain.RELATIONSHIP, StakesLevel.MEDIUM): [FrameworkType.SECOND_ORDER, FrameworkType.INVERSION],
    (DecisionDomain.COMMUNICATION, StakesLevel.MEDIUM): [FrameworkType.INVERSION],
    (DecisionDomain.PROPOSAL, StakesLevel.MEDIUM): [FrameworkType.PRE_MORTEM, FrameworkType.INVERSION],

    # High stakes: 2-3 frameworks
    (DecisionDomain.CONTENT, StakesLevel.HIGH): [FrameworkType.PRE_MORTEM, FrameworkType.INVERSION, FrameworkType.SIX_HATS],
    (DecisionDomain.PRIORITY, StakesLevel.HIGH): [FrameworkType.SECOND_ORDER, FrameworkType.PRE_MORTEM],
    (DecisionDomain.RELATIONSHIP, StakesLevel.HIGH): [FrameworkType.SECOND_ORDER, FrameworkType.SYSTEMS, FrameworkType.INVERSION],
    (DecisionDomain.STRATEGY, StakesLevel.HIGH): [FrameworkType.SIX_HATS, FrameworkType.SECOND_ORDER, FrameworkType.PRE_MORTEM],
    (DecisionDomain.PROPOSAL, StakesLevel.HIGH): [FrameworkType.PRE_MORTEM, FrameworkType.INVERSION, FrameworkType.SECOND_ORDER],
    (DecisionDomain.FINANCIAL, StakesLevel.HIGH): [FrameworkType.FIRST_PRINCIPLES, FrameworkType.PRE_MORTEM, FrameworkType.INVERSION],
    (DecisionDomain.TECHNOLOGY, StakesLevel.HIGH): [FrameworkType.FIRST_PRINCIPLES, FrameworkType.SECOND_ORDER],

    # Critical stakes: full analysis (3-4 frameworks)
    (DecisionDomain.STRATEGY, StakesLevel.CRITICAL): [
        FrameworkType.SIX_HATS, FrameworkType.PRE_MORTEM,
        FrameworkType.FIRST_PRINCIPLES, FrameworkType.SECOND_ORDER,
    ],
    (DecisionDomain.PROPOSAL, StakesLevel.CRITICAL): [
        FrameworkType.PRE_MORTEM, FrameworkType.INVERSION,
        FrameworkType.SIX_HATS, FrameworkType.SECOND_ORDER,
    ],
    (DecisionDomain.FINANCIAL, StakesLevel.CRITICAL): [
        FrameworkType.FIRST_PRINCIPLES, FrameworkType.PRE_MORTEM,
        FrameworkType.INVERSION, FrameworkType.SECOND_ORDER,
    ],
}

# Default for any unmatched (domain, stakes) pair
DEFAULT_HIGH_FRAMEWORKS = [FrameworkType.PRE_MORTEM, FrameworkType.SECOND_ORDER]
DEFAULT_CRITICAL_FRAMEWORKS = [
    FrameworkType.SIX_HATS, FrameworkType.PRE_MORTEM,
    FrameworkType.SECOND_ORDER, FrameworkType.INVERSION,
]


# ── The Thinking Frameworks Engine ───────────────────────────────

class ThinkingFrameworksEngine:
    """
    The Oracle Layer.

    Applies structured thinking frameworks to any decision, content,
    or action — automatically or on request.

    Invoked by:
    1. Sentinel (quality gate applies frameworks to outbound content)
    2. Gravity (consequence chains use second-order; collisions use pre-mortem)
    3. Constellation (network risk uses systems thinking)
    4. Amplifier (content review uses inversion + pre-mortem)
    5. Mani directly ("Run Six Hats on this")
    6. Elaine proactively ("Before you decide, here's a pre-mortem")
    """

    def __init__(self):
        self._history: list[ThinkingResult] = []
        self._framework_usage: dict[str, int] = {ft.value: 0 for ft in FrameworkType}

    # ── Individual Frameworks ────────────────────────────────────

    def second_order(self, action: str, context: dict = None) -> SecondOrderResult:
        """
        'And then what?'
        Traces consequences through 3 orders.
        Surfaces unintended consequences hiding in obvious actions.
        """
        ctx = context or {}
        result = SecondOrderResult(
            action=action,
            first_order=ctx.get("first_order", ""),
            second_order=ctx.get("second_order", ""),
            third_order=ctx.get("third_order", ""),
            hidden_risks=ctx.get("hidden_risks", []),
            hidden_opportunities=ctx.get("hidden_opportunities", []),
            recommendation=ctx.get("recommendation", ""),
        )
        self._framework_usage[FrameworkType.SECOND_ORDER.value] += 1
        logger.info(f"Second-Order analysis: {action[:60]}")
        return result

    def systems_map(self, topic: str, context: dict = None) -> SystemsMapResult:
        """
        'How does this connect to everything else?'
        Maps feedback loops, leverage points, delays, resistance.
        """
        ctx = context or {}
        result = SystemsMapResult(
            topic=topic,
            components=ctx.get("components", []),
            feedback_loops=ctx.get("feedback_loops", []),
            leverage_points=ctx.get("leverage_points", []),
            delays=ctx.get("delays", []),
            resistance_points=ctx.get("resistance_points", []),
            recommendation=ctx.get("recommendation", ""),
        )
        self._framework_usage[FrameworkType.SYSTEMS.value] += 1
        logger.info(f"Systems map: {topic[:60]}")
        return result

    def six_hats(self, question: str, context: dict = None) -> SixHatsResult:
        """
        de Bono's Six Thinking Hats.
        Forces multi-perspective analysis on any question.
        """
        ctx = context or {}
        result = SixHatsResult(
            question=question,
            white_hat=ctx.get("white_hat", ""),
            red_hat=ctx.get("red_hat", ""),
            black_hat=ctx.get("black_hat", ""),
            yellow_hat=ctx.get("yellow_hat", ""),
            green_hat=ctx.get("green_hat", ""),
            blue_hat=ctx.get("blue_hat", ""),
            synthesis=ctx.get("synthesis", ""),
        )
        self._framework_usage[FrameworkType.SIX_HATS.value] += 1
        logger.info(f"Six Hats analysis: {question[:60]}")
        return result

    def pre_mortem(self, plan: str, context: dict = None) -> PreMortemResult:
        """
        'Assume this failed. Why?'
        Works backwards from failure to identify risks.
        """
        ctx = context or {}
        scenarios = []
        for s in ctx.get("failure_scenarios", []):
            scenarios.append(FailureScenario(
                scenario=s.get("scenario", ""),
                probability=s.get("probability", 0.5),
                severity=s.get("severity", "moderate"),
                mitigation=s.get("mitigation", ""),
                early_warning=s.get("early_warning", ""),
            ))

        result = PreMortemResult(
            plan=plan,
            failure_scenarios=scenarios,
            top_risk=ctx.get("top_risk", ""),
            mitigation_plan=ctx.get("mitigation_plan", ""),
            kill_criteria=ctx.get("kill_criteria", []),
            confidence_after_analysis=ctx.get("confidence_after_analysis", 0.7),
        )
        self._framework_usage[FrameworkType.PRE_MORTEM.value] += 1
        logger.info(f"Pre-Mortem: {plan[:60]}")
        return result

    def first_principles(self, question: str, context: dict = None) -> FirstPrinciplesResult:
        """
        'What is actually true here?'
        Strips assumptions, rebuilds from fundamental truths.
        """
        ctx = context or {}
        result = FirstPrinciplesResult(
            question=question,
            stated_belief=ctx.get("stated_belief", question),
            assumptions_identified=ctx.get("assumptions_identified", []),
            fundamental_truths=ctx.get("fundamental_truths", []),
            rebuilt_answer=ctx.get("rebuilt_answer", ""),
            conventional_vs_fundamental=ctx.get("conventional_vs_fundamental", ""),
        )
        self._framework_usage[FrameworkType.FIRST_PRINCIPLES.value] += 1
        logger.info(f"First Principles: {question[:60]}")
        return result

    def inversion(self, goal: str, context: dict = None) -> InversionResult:
        """
        'What would guarantee failure?'
        Lists failure conditions, inverts to success strategies.
        """
        ctx = context or {}
        failures = ctx.get("guaranteed_failures", [])
        inversions = []
        for f in failures:
            inversions.append({
                "failure": f,
                "avoidance_strategy": f"Actively avoid: {f}",
            })
        inversions = ctx.get("inversions", inversions)

        result = InversionResult(
            goal=goal,
            guaranteed_failures=failures,
            inversions=inversions,
            hidden_risks=ctx.get("hidden_risks", []),
            anti_checklist=[f"NEVER: {f}" for f in failures[:5]],
        )
        self._framework_usage[FrameworkType.INVERSION.value] += 1
        logger.info(f"Inversion: {goal[:60]}")
        return result

    # ── Auto-Select & Combined Analysis ──────────────────────────

    def select_frameworks(
        self,
        domain: DecisionDomain,
        stakes: StakesLevel,
    ) -> list[FrameworkType]:
        """
        Auto-select which frameworks to apply based on domain and stakes.
        Low stakes = minimal analysis (0-1 frameworks).
        Critical stakes = full analysis (3-4 frameworks).
        """
        key = (domain, stakes)
        if key in FRAMEWORK_MATRIX:
            return FRAMEWORK_MATRIX[key]

        # Fallback based on stakes alone
        if stakes == StakesLevel.LOW:
            return []
        elif stakes == StakesLevel.MEDIUM:
            return [FrameworkType.PRE_MORTEM]
        elif stakes == StakesLevel.HIGH:
            return DEFAULT_HIGH_FRAMEWORKS
        else:
            return DEFAULT_CRITICAL_FRAMEWORKS

    def analyse(
        self,
        topic: str,
        domain: DecisionDomain,
        stakes: StakesLevel,
        context: dict = None,
        frameworks: list[FrameworkType] = None,
    ) -> ThinkingResult:
        """
        Run a combined analysis using auto-selected or specified frameworks.
        Returns a ThinkingResult with all framework outputs and synthesis.

        If frameworks is None, auto-selects based on domain + stakes.
        """
        ctx = context or {}

        if frameworks is None:
            frameworks = self.select_frameworks(domain, stakes)

        results = {}
        for fw in frameworks:
            fw_context = ctx.get(fw.value, {})
            if fw == FrameworkType.SECOND_ORDER:
                results[fw.value] = self.second_order(topic, fw_context)
            elif fw == FrameworkType.SYSTEMS:
                results[fw.value] = self.systems_map(topic, fw_context)
            elif fw == FrameworkType.SIX_HATS:
                results[fw.value] = self.six_hats(topic, fw_context)
            elif fw == FrameworkType.PRE_MORTEM:
                results[fw.value] = self.pre_mortem(topic, fw_context)
            elif fw == FrameworkType.FIRST_PRINCIPLES:
                results[fw.value] = self.first_principles(topic, fw_context)
            elif fw == FrameworkType.INVERSION:
                results[fw.value] = self.inversion(topic, fw_context)

        thinking_result = ThinkingResult(
            topic=topic,
            domain=domain,
            stakes=stakes,
            frameworks_applied=frameworks,
            results=results,
            synthesis=ctx.get("synthesis", ""),
            confidence=ctx.get("confidence", 0.7),
            recommended_action=ctx.get("recommended_action", ""),
            warnings=ctx.get("warnings", []),
        )

        self._history.append(thinking_result)
        logger.info(
            f"Thinking analysis complete: {topic[:40]} | "
            f"{len(frameworks)} frameworks | domain={domain.value} stakes={stakes.value}"
        )
        return thinking_result

    # ── Convenience Methods for Module Integration ───────────────

    def gravity_consequence_analysis(
        self, item_title: str, revenue_at_risk: float,
        people_affected: list[str], context: dict = None,
    ) -> ThinkingResult:
        """
        Called by Gravity Engine for high-consequence items.
        Auto-applies second-order + pre-mortem.
        """
        ctx = context or {}
        ctx.setdefault("second_order", {
            "first_order": f"Missing '{item_title}' loses ${revenue_at_risk:,.0f}",
        })
        ctx.setdefault("pre_mortem", {
            "failure_scenarios": [
                {"scenario": "Time pressure causes quality drop", "probability": 0.4, "severity": "moderate"},
                {"scenario": f"Relationship damage with {', '.join(people_affected[:2])}", "probability": 0.6, "severity": "severe"},
            ],
        })

        stakes = StakesLevel.HIGH if revenue_at_risk > 20000 else StakesLevel.MEDIUM
        return self.analyse(
            topic=item_title,
            domain=DecisionDomain.PRIORITY,
            stakes=stakes,
            context=ctx,
            frameworks=[FrameworkType.SECOND_ORDER, FrameworkType.PRE_MORTEM],
        )

    def constellation_network_risk(
        self, poi_name: str, relationship_context: dict = None,
    ) -> ThinkingResult:
        """
        Called by Constellation for relationship risk assessment.
        Auto-applies systems thinking + second-order + inversion.
        """
        ctx = relationship_context or {}
        return self.analyse(
            topic=f"Relationship risk: {poi_name}",
            domain=DecisionDomain.RELATIONSHIP,
            stakes=StakesLevel.HIGH,
            context=ctx,
            frameworks=[FrameworkType.SYSTEMS, FrameworkType.SECOND_ORDER, FrameworkType.INVERSION],
        )

    def amplifier_content_review(
        self, content_title: str, is_public: bool = True,
        context: dict = None,
    ) -> ThinkingResult:
        """
        Called by Amplifier before publishing content.
        Auto-applies pre-mortem + inversion.
        """
        stakes = StakesLevel.HIGH if is_public else StakesLevel.MEDIUM
        return self.analyse(
            topic=content_title,
            domain=DecisionDomain.CONTENT,
            stakes=stakes,
            context=context,
            frameworks=[FrameworkType.PRE_MORTEM, FrameworkType.INVERSION],
        )

    def sentinel_quality_gate(
        self, content_description: str, gate_level: int,
        context: dict = None,
    ) -> ThinkingResult:
        """
        Called by Sentinel at Gate 2 and Gate 3.
        Gate 2: pre-mortem + inversion.
        Gate 3: full analysis (all frameworks relevant to content).
        """
        if gate_level >= 3:
            frameworks = [
                FrameworkType.PRE_MORTEM, FrameworkType.INVERSION,
                FrameworkType.SIX_HATS, FrameworkType.SECOND_ORDER,
            ]
            stakes = StakesLevel.CRITICAL
        else:
            frameworks = [FrameworkType.PRE_MORTEM, FrameworkType.INVERSION]
            stakes = StakesLevel.HIGH

        return self.analyse(
            topic=content_description,
            domain=DecisionDomain.PROPOSAL,
            stakes=stakes,
            context=context,
            frameworks=frameworks,
        )

    def cartographer_territory_assessment(
        self, territory: str, context: dict = None,
    ) -> ThinkingResult:
        """
        Called by Cartographer for strategic territory decisions.
        Auto-applies first principles + six hats.
        """
        return self.analyse(
            topic=f"Territory assessment: {territory}",
            domain=DecisionDomain.STRATEGY,
            stakes=StakesLevel.MEDIUM,
            context=context,
            frameworks=[FrameworkType.FIRST_PRINCIPLES, FrameworkType.SIX_HATS],
        )

    # ── Reporting ────────────────────────────────────────────────

    def status(self) -> dict:
        return {
            "total_analyses": len(self._history),
            "framework_usage": self._framework_usage,
            "recent_topics": [
                {"topic": r.topic[:60], "frameworks": len(r.frameworks_applied), "stakes": r.stakes.value}
                for r in self._history[-5:]
            ],
        }

    def get_history(self, limit: int = 10) -> list[dict]:
        return [
            {
                "topic": r.topic,
                "domain": r.domain.value,
                "stakes": r.stakes.value,
                "frameworks": [f.value for f in r.frameworks_applied],
                "synthesis": r.synthesis,
                "recommended_action": r.recommended_action,
                "warnings": r.warnings,
                "timestamp": r.timestamp.isoformat(),
            }
            for r in self._history[-limit:]
        ]
