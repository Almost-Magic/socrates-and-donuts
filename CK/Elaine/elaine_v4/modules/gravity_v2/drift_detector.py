"""
Strategic Drift Detector
The #1 silent killer: being busy every day while making zero strategic progress.

Monitors the balance of urgent-tactical vs important-strategic work
and alerts when strategic goals are dying silently.

Patentable: Urgent-Strategic Balance Monitoring with Drift Alerting

Almost Magic Tech Lab — Patentable IP
"""

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

from .models import GravityItem, MomentumState, StrategicBalance

logger = logging.getLogger("elaine.gravity.drift")


@dataclass
class DriftAnalysis:
    """Complete strategic drift analysis."""
    period_days: int = 7
    urgent_tactical_pct: float = 0.0
    important_strategic_pct: float = 0.0
    administrative_pct: float = 0.0

    okr_status: dict = field(default_factory=dict)  # OKR key → hours spent
    okrs_at_risk: list[str] = field(default_factory=list)
    drift_alert: bool = False
    drift_severity: str = "none"  # none, mild, moderate, severe

    ungraviton_pattern: Optional[str] = None
    recommendation: str = ""


class DriftDetector:
    """
    Monitors strategic drift: the silent death of OKRs.

    Weekly analysis of:
    - Time allocation: urgent-tactical vs important-strategic
    - OKR progress: hours per goal, streak tracking
    - Ungraviton patterns: systematic avoidance of growth work
    """

    DRIFT_THRESHOLDS = {
        "strategic_min_pct": 20.0,   # Below this → drift warning
        "tactical_max_pct": 70.0,    # Above this → tactical overload
        "okr_zero_weeks": 2,         # Weeks with zero OKR hours → alert
    }

    def __init__(self):
        self._weekly_snapshots: list[dict] = []
        self._okr_definitions: dict[str, dict] = {}  # OKR key → {name, target_hours_weekly}

    def register_okr(self, key: str, name: str, target_hours_weekly: float = 5.0):
        """Register an OKR for tracking."""
        self._okr_definitions[key] = {
            "name": name,
            "target_hours_weekly": target_hours_weekly,
            "consecutive_zero_weeks": 0,
        }

    def record_completion(self, item: GravityItem, hours_spent: float):
        """Record a completed item for drift tracking."""
        category = self._categorise_item(item)
        self._weekly_snapshots.append({
            "timestamp": datetime.now(),
            "item_id": item.id,
            "category": category,
            "hours": hours_spent,
            "okrs": item.okr_alignment,
            "tags": item.tags,
        })

    def _categorise_item(self, item: GravityItem) -> str:
        """Categorise an item as tactical, strategic, or administrative."""
        if item.okr_alignment:
            return "strategic"

        strategic_tags = {"content", "growth", "marketing", "research", "innovation"}
        admin_tags = {"admin", "email", "invoicing", "scheduling", "filing"}

        item_tags = set(item.tags)
        if item_tags & strategic_tags:
            return "strategic"
        if item_tags & admin_tags:
            return "administrative"

        return "tactical"

    def analyse(self, lookback_days: int = 7) -> DriftAnalysis:
        """
        Produce a strategic drift analysis.
        Returns actionable insights about where time is going.
        """
        cutoff = datetime.now() - timedelta(days=lookback_days)
        recent = [s for s in self._weekly_snapshots if s["timestamp"] > cutoff]

        analysis = DriftAnalysis(period_days=lookback_days)

        if not recent:
            analysis.recommendation = "No completed items this period — nothing to analyse yet."
            return analysis

        # ── Time Allocation ──
        total_hours = sum(s["hours"] for s in recent)
        if total_hours == 0:
            return analysis

        tactical_hours = sum(s["hours"] for s in recent if s["category"] == "tactical")
        strategic_hours = sum(s["hours"] for s in recent if s["category"] == "strategic")
        admin_hours = sum(s["hours"] for s in recent if s["category"] == "administrative")

        analysis.urgent_tactical_pct = round(tactical_hours / total_hours * 100, 1)
        analysis.important_strategic_pct = round(strategic_hours / total_hours * 100, 1)
        analysis.administrative_pct = round(admin_hours / total_hours * 100, 1)

        # ── OKR Progress ──
        okr_hours = defaultdict(float)
        for s in recent:
            for okr in s["okrs"]:
                okr_hours[okr] += s["hours"]

        analysis.okr_status = {}
        for okr_key, defn in self._okr_definitions.items():
            hours = okr_hours.get(okr_key, 0)
            target = defn["target_hours_weekly"]

            if hours == 0:
                defn["consecutive_zero_weeks"] += 1
            else:
                defn["consecutive_zero_weeks"] = 0

            status = "on_track" if hours >= target * 0.7 else "behind"
            if defn["consecutive_zero_weeks"] >= self.DRIFT_THRESHOLDS["okr_zero_weeks"]:
                status = "at_risk"
                analysis.okrs_at_risk.append(okr_key)

            analysis.okr_status[okr_key] = {
                "name": defn["name"],
                "hours_this_period": round(hours, 1),
                "target_hours": target,
                "status": status,
                "zero_weeks_streak": defn["consecutive_zero_weeks"],
            }

        # ── Drift Detection ──
        if analysis.important_strategic_pct < self.DRIFT_THRESHOLDS["strategic_min_pct"]:
            analysis.drift_alert = True
            if analysis.important_strategic_pct < 10:
                analysis.drift_severity = "severe"
            elif analysis.important_strategic_pct < 15:
                analysis.drift_severity = "moderate"
            else:
                analysis.drift_severity = "mild"

        # ── Recommendation ──
        analysis.recommendation = self._build_recommendation(analysis)

        return analysis

    def _build_recommendation(self, analysis: DriftAnalysis) -> str:
        """Build a human-readable recommendation."""
        parts = []

        if analysis.drift_severity == "severe":
            parts.append(
                "⚠️ DRIFT ALERT: You're executing well on tactical work but "
                "your strategic goals have received almost no attention. "
                "This is how strategic goals die silently."
            )
        elif analysis.drift_severity == "moderate":
            parts.append(
                "⚠️ Strategic work is below target. Consider blocking "
                "dedicated time this week."
            )

        if analysis.okrs_at_risk:
            at_risk_names = [
                self._okr_definitions[k]["name"]
                for k in analysis.okrs_at_risk
                if k in self._okr_definitions
            ]
            parts.append(
                f"OKRs at risk: {', '.join(at_risk_names)}. "
                f"Zero progress for {self.DRIFT_THRESHOLDS['okr_zero_weeks']}+ weeks."
            )

        if analysis.administrative_pct > 25:
            parts.append(
                f"Admin work is {analysis.administrative_pct:.0f}% of your time. "
                f"Consider delegating or automating."
            )

        if not parts:
            parts.append("Strategic balance looks healthy. Keep it up.")

        return " ".join(parts)

    def get_trajectory(self, weeks: int = 4) -> list[dict]:
        """
        Show how strategic balance has changed over time.
        Returns weekly snapshots for trend analysis.
        """
        trajectory = []

        for week_offset in range(weeks, 0, -1):
            start = datetime.now() - timedelta(weeks=week_offset)
            end = start + timedelta(weeks=1)

            week_data = [
                s for s in self._weekly_snapshots
                if start <= s["timestamp"] < end
            ]

            total = sum(s["hours"] for s in week_data) or 1
            trajectory.append({
                "week": f"W-{week_offset}",
                "tactical_pct": round(
                    sum(s["hours"] for s in week_data if s["category"] == "tactical") / total * 100, 1
                ),
                "strategic_pct": round(
                    sum(s["hours"] for s in week_data if s["category"] == "strategic") / total * 100, 1
                ),
                "admin_pct": round(
                    sum(s["hours"] for s in week_data if s["category"] == "administrative") / total * 100, 1
                ),
            })

        return trajectory
