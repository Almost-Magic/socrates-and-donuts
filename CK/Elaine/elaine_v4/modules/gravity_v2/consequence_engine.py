"""
Consequence Engine v2
Models what breaks downstream if an item doesn't get done.
Not in feelings — in money, relationships, blocked work, and strategic cost.

Patentable: Failure Impact Cascade with Financial Quantification

Almost Magic Tech Lab — Patentable IP
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from .models import GravityItem, ConsequenceData, PropagationEffect

logger = logging.getLogger("elaine.gravity.consequence")


@dataclass
class ConsequenceChain:
    """Complete consequence analysis for 'What If You Don't'."""
    item_id: str
    item_title: str

    # The five consequence dimensions
    revenue_at_risk: float = 0.0
    revenue_probability: float = 0.0
    trust_erosion_description: str = ""
    trust_recovery_cost: str = ""
    blocked_items: list[dict] = field(default_factory=list)  # [{id, title, impact}]
    strategic_setback: str = ""
    recovery_cost_if_today: str = ""
    recovery_cost_if_week: str = ""

    # Upside: what happens if you DO
    upside: list[str] = field(default_factory=list)

    # Severity rating
    severity: str = "moderate"  # mild, moderate, severe, critical


class ConsequenceEngine:
    """
    Analyses the downstream impact of not completing a gravity item.

    Zero-input: consequences are auto-inferred from:
    - Business Context Engine (deal value, client tier, pipeline stage)
    - Chronicle (meeting commitments, who was promised what)
    - Gravity Propagation Graph (blocked dependencies)
    - OKR/Goal Database (strategic alignment)
    - Historical Patterns (recovery cost from similar failures)
    """

    # Revenue risk thresholds
    REVENUE_THRESHOLDS = {
        "critical": 50_000,
        "severe": 25_000,
        "moderate": 10_000,
        "mild": 5_000,
    }

    # Trust erosion patterns
    TRUST_PATTERNS = {
        "first_offence": {
            "description": "First missed commitment — forgivable but noted",
            "recovery": "Acknowledgment + expedited delivery",
            "cost_multiplier": 1.0,
        },
        "repeat_offence": {
            "description": "2nd+ missed commitment — trust significantly damaged",
            "recovery": "Apology call + expedited delivery + goodwill gesture",
            "cost_multiplier": 2.5,
        },
        "none": {
            "description": "No trust at stake",
            "recovery": "N/A",
            "cost_multiplier": 0.0,
        },
    }

    def __init__(self):
        self._failure_history: list[dict] = []

    def analyse(self, item: GravityItem, all_items: dict[str, GravityItem]) -> ConsequenceChain:
        """
        Build a complete consequence chain for an item.
        Shows 'What If You Don't' and 'What If You Do'.
        """
        chain = ConsequenceChain(
            item_id=item.id,
            item_title=item.title,
        )

        # ── Revenue at Risk ──
        chain.revenue_at_risk = item.consequence.revenue_at_risk
        chain.revenue_probability = self._estimate_loss_probability(item)

        # ── Trust Erosion ──
        erosion_type = item.consequence.trust_erosion or "none"
        pattern = self.TRUST_PATTERNS.get(erosion_type, self.TRUST_PATTERNS["none"])
        chain.trust_erosion_description = pattern["description"]

        if item.charge.people:
            person_str = ", ".join(item.charge.people[:3])
            miss_count = item.charge.prior_misses + 1
            chain.trust_erosion_description = (
                f"This would be miss #{miss_count} with {person_str}. "
                f"{pattern['description']}"
            )

        chain.trust_recovery_cost = pattern["recovery"]

        # ── Blocked Dependencies ──
        for blocked_id in item.consequence.blocked_items:
            blocked_item = all_items.get(blocked_id)
            if blocked_item:
                chain.blocked_items.append({
                    "id": blocked_id,
                    "title": blocked_item.title,
                    "impact": f"Blocked until {item.title} completes",
                })

        # ── Strategic Setback ──
        if item.consequence.strategic_setback:
            chain.strategic_setback = (
                f"OKR '{item.consequence.strategic_setback}' impacted. "
                f"Progress stalls until this is resolved."
            )

        # ── Recovery Cost ──
        hours = item.consequence.recovery_cost_hours
        chain.recovery_cost_if_today = (
            f"{hours:.0f} hours to recover" if hours > 0 else "Minimal"
        )
        chain.recovery_cost_if_week = (
            f"{hours * 2.5:.0f} hours + relationship repair" if hours > 0 else "Moderate"
        )

        # ── Upside (What If You DO) ──
        chain.upside = self._build_upside(item)

        # ── Severity Rating ──
        chain.severity = self._calculate_severity(chain)

        return chain

    def _estimate_loss_probability(self, item: GravityItem) -> float:
        """Estimate probability of loss if item is not completed on time."""
        base = 0.3  # 30% base probability

        if item.is_overdue:
            base += 0.2 * min(item.days_overdue, 5)
        if item.charge.prior_misses >= 2:
            base += 0.25
        elif item.charge.prior_misses == 1:
            base += 0.15
        if item.charge.elasticity.value == "brittle":
            base += 0.2

        return min(base, 0.95)

    def _build_upside(self, item: GravityItem) -> list[str]:
        """What happens if you DO complete this now."""
        upside = []

        if item.consequence.revenue_at_risk > 0:
            upside.append(
                f"${item.consequence.revenue_at_risk:,.0f} deal secured"
            )

        if item.charge.people:
            if item.charge.prior_misses == 0:
                upside.append(f"Trust strengthened with {item.charge.people[0]}")
            else:
                upside.append(f"Trust recovery with {item.charge.people[0]}")

        if item.consequence.blocked_items:
            upside.append(
                f"Unblocks {len(item.consequence.blocked_items)} downstream items"
            )

        if item.okr_alignment:
            upside.append(f"OKR progress: {', '.join(item.okr_alignment)}")

        if not upside:
            upside.append("Task completed — field pressure reduced")

        return upside

    def _calculate_severity(self, chain: ConsequenceChain) -> str:
        """Calculate overall consequence severity."""
        score = 0

        if chain.revenue_at_risk >= self.REVENUE_THRESHOLDS["critical"]:
            score += 4
        elif chain.revenue_at_risk >= self.REVENUE_THRESHOLDS["severe"]:
            score += 3
        elif chain.revenue_at_risk >= self.REVENUE_THRESHOLDS["moderate"]:
            score += 2

        if "repeat" in chain.trust_erosion_description.lower():
            score += 3
        elif "first" in chain.trust_erosion_description.lower():
            score += 1

        score += len(chain.blocked_items)

        if chain.strategic_setback:
            score += 2

        if score >= 8:
            return "critical"
        elif score >= 5:
            return "severe"
        elif score >= 3:
            return "moderate"
        return "mild"

    def record_failure(self, item: GravityItem, failure_type: str, root_causes: dict):
        """Record a failure for Failure Archaeology."""
        self._failure_history.append({
            "item_id": item.id,
            "item_title": item.title,
            "failure_type": failure_type,
            "root_causes": root_causes,
            "date": datetime.now(),
            "tags": item.tags,
            "context_type": item.context_type.value,
        })
        logger.warning(f"Failure recorded: {item.title} — {failure_type}")

    def get_failure_patterns(self, lookback_days: int = 30) -> dict:
        """Analyse failure patterns for prevention."""
        cutoff = datetime.now()
        recent = [
            f for f in self._failure_history
            if (cutoff - f["date"]).days <= lookback_days
        ]

        if not recent:
            return {"failures": 0, "patterns": [], "prevention_rules": []}

        # Aggregate root causes
        from collections import Counter
        all_causes = Counter()
        all_tags = Counter()
        all_contexts = Counter()

        for f in recent:
            for cause, pct in f["root_causes"].items():
                all_causes[cause] += 1
            for tag in f["tags"]:
                all_tags[tag] += 1
            all_contexts[f["context_type"]] += 1

        prevention_rules = []
        if all_contexts.most_common(1):
            ctx, count = all_contexts.most_common(1)[0]
            if count >= 2:
                prevention_rules.append(
                    f"Items of type '{ctx}' have failed {count} times — "
                    f"consider scheduling them during peak energy hours"
                )

        return {
            "failures": len(recent),
            "top_causes": dict(all_causes.most_common(5)),
            "vulnerable_categories": dict(all_tags.most_common(3)),
            "prevention_rules": prevention_rules,
        }
