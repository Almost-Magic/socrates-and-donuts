"""
AMTL Thinking — Strategic Analysis Frameworks Engine
Structured analysis for business strategy and market assessment.

Frameworks:
1. MECE — Mutually Exclusive, Collectively Exhaustive decomposition
2. SWOT — Strengths, Weaknesses, Opportunities, Threats
3. PESTLE — Political, Economic, Social, Technological, Legal, Environmental
4. 3Cs — Company, Customer, Competition
5. McKinsey 7S — Strategy, Structure, Systems, Shared Values, Style, Staff, Skills
6. BCG Matrix — Stars, Cash Cows, Question Marks, Dogs
7. Ansoff Matrix — Market Penetration, Development, Product Development, Diversification
8. Balanced Scorecard — Financial, Customer, Internal, Learning

Usage:
    from amtl_thinking.strategic import StrategicEngine
    engine = StrategicEngine()
    result = engine.swot(strengths=[...], weaknesses=[...], ...)

Almost Magic Tech Lab — Proprietary IP
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

logger = logging.getLogger("amtl.strategic")


# ── Framework Results ────────────────────────────────────────────

@dataclass
class MECEResult:
    """MECE decomposition of a problem."""
    problem: str
    categories: list[str] = field(default_factory=list)
    is_mutually_exclusive: bool = False
    is_collectively_exhaustive: bool = False
    is_mece: bool = False
    gaps: list[str] = field(default_factory=list)       # What's missing
    overlaps: list[str] = field(default_factory=list)    # What overlaps
    recommendations: list[str] = field(default_factory=list)


@dataclass
class SWOTResult:
    """SWOT Analysis."""
    topic: str
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    opportunities: list[str] = field(default_factory=list)
    threats: list[str] = field(default_factory=list)
    key_insight: str = ""          # The strategic implication
    priority_action: str = ""      # What to do first


@dataclass
class PESTLEResult:
    """PESTLE macro-environmental analysis."""
    topic: str
    political: list[str] = field(default_factory=list)
    economic: list[str] = field(default_factory=list)
    social: list[str] = field(default_factory=list)
    technological: list[str] = field(default_factory=list)
    legal: list[str] = field(default_factory=list)
    environmental: list[str] = field(default_factory=list)
    highest_impact_factor: str = ""
    recommendations: list[str] = field(default_factory=list)


@dataclass
class ThreeCsResult:
    """3Cs Analysis — Company, Customer, Competition."""
    topic: str
    company: dict = field(default_factory=dict)     # {strengths, weaknesses, capabilities}
    customer: dict = field(default_factory=dict)     # {needs, segments, trends}
    competition: dict = field(default_factory=dict)  # {players, positioning, advantages}
    strategic_fit: str = ""        # Where company meets customer needs vs competition
    competitive_advantage: str = ""


@dataclass
class SevenSResult:
    """McKinsey 7S Model."""
    topic: str
    strategy: str = ""
    structure: str = ""
    systems: str = ""
    shared_values: str = ""
    style: str = ""
    staff: str = ""
    skills: str = ""
    alignment_score: float = 0.0   # 0-1, how aligned are the 7 elements
    misalignments: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


class BCGQuadrant(str, Enum):
    STAR = "star"                  # High growth, high share → invest
    CASH_COW = "cash_cow"          # Low growth, high share → harvest
    QUESTION_MARK = "question_mark" # High growth, low share → decide
    DOG = "dog"                    # Low growth, low share → divest


@dataclass
class BCGItem:
    name: str
    quadrant: BCGQuadrant
    market_growth: float = 0.0     # % growth rate
    market_share: float = 0.0      # Relative market share
    recommendation: str = ""


@dataclass
class BCGResult:
    """BCG Growth-Share Matrix."""
    topic: str
    items: list[BCGItem] = field(default_factory=list)
    portfolio_balance: str = ""    # Assessment of portfolio health
    recommendations: list[str] = field(default_factory=list)


class AnsoffQuadrant(str, Enum):
    MARKET_PENETRATION = "market_penetration"     # Existing product, existing market
    MARKET_DEVELOPMENT = "market_development"     # Existing product, new market
    PRODUCT_DEVELOPMENT = "product_development"   # New product, existing market
    DIVERSIFICATION = "diversification"           # New product, new market


@dataclass
class AnsoffResult:
    """Ansoff Growth Matrix."""
    topic: str
    strategies: list[dict] = field(default_factory=list)  # {quadrant, description, risk, opportunity}
    recommended_quadrant: AnsoffQuadrant = AnsoffQuadrant.MARKET_PENETRATION
    risk_assessment: str = ""


@dataclass
class BalancedScorecardResult:
    """Balanced Scorecard — four perspectives."""
    topic: str
    financial: list[dict] = field(default_factory=list)     # {objective, measure, target}
    customer: list[dict] = field(default_factory=list)
    internal_process: list[dict] = field(default_factory=list)
    learning_growth: list[dict] = field(default_factory=list)
    overall_assessment: str = ""


@dataclass
class StrategicResult:
    """Combined strategic analysis result."""
    topic: str
    frameworks_applied: list[str] = field(default_factory=list)
    results: dict = field(default_factory=dict)
    key_insights: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


# ── The Strategic Analysis Engine ────────────────────────────────

class StrategicEngine:
    """
    Strategic analysis frameworks for business decisions.
    """

    def __init__(self):
        self._history: list[StrategicResult] = []
        self._framework_usage: dict[str, int] = {}

    def _track(self, name: str):
        self._framework_usage[name] = self._framework_usage.get(name, 0) + 1

    # ── MECE ─────────────────────────────────────────────────────

    def mece_check(self, problem: str, categories: list[str]) -> MECEResult:
        """
        Check if a decomposition is MECE.
        Mutually Exclusive: no overlap between categories.
        Collectively Exhaustive: categories cover the full problem space.
        """
        gaps = []
        overlaps = []

        # Simple overlap detection
        for i, cat1 in enumerate(categories):
            for j, cat2 in enumerate(categories):
                if i < j:
                    words1 = set(cat1.lower().split())
                    words2 = set(cat2.lower().split())
                    common = words1 & words2 - {"the", "and", "is", "to", "of", "a", "in", "for", "with"}
                    if len(common) > 2:
                        overlaps.append(f"'{cat1}' and '{cat2}' may overlap on: {', '.join(common)}")

        is_me = len(overlaps) == 0
        is_ce = len(categories) >= 3  # Heuristic: at least 3 for exhaustive

        if len(categories) < 3:
            gaps.append("Consider whether more categories are needed for full coverage")
        if len(categories) > 7:
            gaps.append("More than 7 categories may be too granular — consider consolidating")

        recommendations = []
        if not is_me:
            recommendations.append("Redefine categories to eliminate overlap")
        if not is_ce:
            recommendations.append("Test coverage by asking: 'What doesn't fit in any category?'")

        result = MECEResult(
            problem=problem,
            categories=categories,
            is_mutually_exclusive=is_me,
            is_collectively_exhaustive=is_ce,
            is_mece=is_me and is_ce,
            gaps=gaps,
            overlaps=overlaps,
            recommendations=recommendations,
        )
        self._track("mece")
        logger.info(f"MECE check: {problem[:40]} | {len(categories)} categories | MECE: {is_me and is_ce}")
        return result

    # ── SWOT ─────────────────────────────────────────────────────

    def swot(self, topic: str, strengths: list[str] = None,
             weaknesses: list[str] = None, opportunities: list[str] = None,
             threats: list[str] = None) -> SWOTResult:
        """Classic SWOT analysis."""
        s = strengths or []
        w = weaknesses or []
        o = opportunities or []
        t = threats or []

        # Generate insight
        insight = ""
        if s and o:
            insight = f"Leverage {s[0].lower()} to capture {o[0].lower()}"
        priority = ""
        if w and t:
            priority = f"Address {w[0].lower()} before {t[0].lower()} becomes critical"

        result = SWOTResult(
            topic=topic,
            strengths=s, weaknesses=w,
            opportunities=o, threats=t,
            key_insight=insight,
            priority_action=priority,
        )
        self._track("swot")
        logger.info(f"SWOT: {topic[:40]} | S:{len(s)} W:{len(w)} O:{len(o)} T:{len(t)}")
        return result

    # ── PESTLE ───────────────────────────────────────────────────

    def pestle(self, topic: str, political: list[str] = None,
               economic: list[str] = None, social: list[str] = None,
               technological: list[str] = None, legal: list[str] = None,
               environmental: list[str] = None) -> PESTLEResult:
        """PESTLE macro-environmental analysis."""
        factors = {
            "political": political or [],
            "economic": economic or [],
            "social": social or [],
            "technological": technological or [],
            "legal": legal or [],
            "environmental": environmental or [],
        }

        # Find highest impact factor
        highest = max(factors, key=lambda k: len(factors[k]))

        result = PESTLEResult(
            topic=topic,
            political=factors["political"],
            economic=factors["economic"],
            social=factors["social"],
            technological=factors["technological"],
            legal=factors["legal"],
            environmental=factors["environmental"],
            highest_impact_factor=highest,
            recommendations=[f"Monitor {highest} factors most closely"],
        )
        self._track("pestle")
        logger.info(f"PESTLE: {topic[:40]} | highest impact: {highest}")
        return result

    # ── 3Cs ──────────────────────────────────────────────────────

    def three_cs(self, topic: str, company: dict = None,
                  customer: dict = None, competition: dict = None) -> ThreeCsResult:
        """3Cs Analysis — Company, Customer, Competition."""
        result = ThreeCsResult(
            topic=topic,
            company=company or {},
            customer=customer or {},
            competition=competition or {},
        )
        self._track("three_cs")
        logger.info(f"3Cs: {topic[:40]}")
        return result

    # ── McKinsey 7S ──────────────────────────────────────────────

    def seven_s(self, topic: str, strategy: str = "", structure: str = "",
                systems: str = "", shared_values: str = "", style: str = "",
                staff: str = "", skills: str = "") -> SevenSResult:
        """McKinsey 7S Model for organisational analysis."""
        elements = [strategy, structure, systems, shared_values, style, staff, skills]
        filled = sum(1 for e in elements if e)
        alignment = filled / 7 if filled else 0.0

        misalignments = []
        if not shared_values:
            misalignments.append("Shared Values undefined — this is the core; all other S's orbit it")
        if strategy and not structure:
            misalignments.append("Strategy defined but Structure unclear — execution at risk")
        if skills and not staff:
            misalignments.append("Skills identified but Staff not assessed — capability gap")

        result = SevenSResult(
            topic=topic,
            strategy=strategy, structure=structure, systems=systems,
            shared_values=shared_values, style=style, staff=staff, skills=skills,
            alignment_score=round(alignment, 2),
            misalignments=misalignments,
            recommendations=[f"Address {m.split('—')[0].strip()}" for m in misalignments],
        )
        self._track("seven_s")
        logger.info(f"7S: {topic[:40]} | alignment: {alignment:.0%}")
        return result

    # ── BCG Matrix ───────────────────────────────────────────────

    def bcg_matrix(self, topic: str, items: list[dict] = None) -> BCGResult:
        """
        BCG Growth-Share Matrix.
        items: [{name, market_growth, market_share}]
        """
        bcg_items = []
        for item in (items or []):
            growth = item.get("market_growth", 0)
            share = item.get("market_share", 0)

            if growth > 10 and share > 1.0:
                quadrant = BCGQuadrant.STAR
                rec = "Invest heavily"
            elif growth <= 10 and share > 1.0:
                quadrant = BCGQuadrant.CASH_COW
                rec = "Harvest — maximise cash flow"
            elif growth > 10 and share <= 1.0:
                quadrant = BCGQuadrant.QUESTION_MARK
                rec = "Decide — invest to grow share or exit"
            else:
                quadrant = BCGQuadrant.DOG
                rec = "Consider divesting"

            bcg_items.append(BCGItem(
                name=item.get("name", ""),
                quadrant=quadrant,
                market_growth=growth,
                market_share=share,
                recommendation=rec,
            ))

        stars = sum(1 for i in bcg_items if i.quadrant == BCGQuadrant.STAR)
        cows = sum(1 for i in bcg_items if i.quadrant == BCGQuadrant.CASH_COW)
        balance = "Healthy" if stars >= 1 and cows >= 1 else "Needs rebalancing"

        result = BCGResult(
            topic=topic,
            items=bcg_items,
            portfolio_balance=balance,
            recommendations=[i.recommendation for i in bcg_items],
        )
        self._track("bcg")
        logger.info(f"BCG: {topic[:40]} | {len(bcg_items)} items | {balance}")
        return result

    # ── Ansoff Matrix ────────────────────────────────────────────

    def ansoff(self, topic: str, strategies: list[dict] = None) -> AnsoffResult:
        """
        Ansoff Growth Matrix.
        strategies: [{quadrant, description, risk, opportunity}]
        """
        strats = []
        for s in (strategies or []):
            strats.append({
                "quadrant": s.get("quadrant", "market_penetration"),
                "description": s.get("description", ""),
                "risk": s.get("risk", "medium"),
                "opportunity": s.get("opportunity", ""),
            })

        # Recommend lowest-risk by default
        risk_order = {"low": 0, "medium": 1, "high": 2, "very_high": 3}
        recommended = AnsoffQuadrant.MARKET_PENETRATION
        if strats:
            lowest = min(strats, key=lambda s: risk_order.get(s["risk"], 2))
            recommended = AnsoffQuadrant(lowest["quadrant"])

        result = AnsoffResult(
            topic=topic,
            strategies=strats,
            recommended_quadrant=recommended,
            risk_assessment=f"Recommended: {recommended.value} (lowest risk path)",
        )
        self._track("ansoff")
        logger.info(f"Ansoff: {topic[:40]} | {len(strats)} strategies")
        return result

    # ── Balanced Scorecard ───────────────────────────────────────

    def balanced_scorecard(self, topic: str, financial: list[dict] = None,
                            customer: list[dict] = None,
                            internal_process: list[dict] = None,
                            learning_growth: list[dict] = None) -> BalancedScorecardResult:
        """Balanced Scorecard — four perspectives."""
        perspectives = {
            "financial": financial or [],
            "customer": customer or [],
            "internal_process": internal_process or [],
            "learning_growth": learning_growth or [],
        }
        filled = sum(1 for v in perspectives.values() if v)
        assessment = "Comprehensive" if filled == 4 else f"Incomplete — {4-filled} perspectives missing"

        result = BalancedScorecardResult(
            topic=topic,
            financial=perspectives["financial"],
            customer=perspectives["customer"],
            internal_process=perspectives["internal_process"],
            learning_growth=perspectives["learning_growth"],
            overall_assessment=assessment,
        )
        self._track("balanced_scorecard")
        logger.info(f"Balanced Scorecard: {topic[:40]} | {filled}/4 perspectives")
        return result

    # ── Reporting ────────────────────────────────────────────────

    def status(self) -> dict:
        return {
            "total_analyses": len(self._history),
            "framework_usage": self._framework_usage,
        }
