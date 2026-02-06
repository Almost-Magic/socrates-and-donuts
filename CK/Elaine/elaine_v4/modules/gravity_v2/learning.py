"""
Gravity Learning Engine v2
The system learns, not just calculates.

1. Revealed Preference Learning: adjusts mass from observed behaviour
2. Adaptive Proximity Curve: learns personal deadline patterns
3. Failure Archaeology: automated post-mortems with prevention
4. Energy Pattern Learning: infers energy from behaviour

Patentable: Behavioural Mass Calibration + Automated Failure Archaeology

Almost Magic Tech Lab — Patentable IP
"""

import logging
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

from .models import (
    GravityItem, MomentumState, EnergyCategory, FailureRecord,
)

logger = logging.getLogger("elaine.gravity.learning")


@dataclass
class PreferenceObservation:
    """Records what Mani chose vs. what Gravity recommended."""
    timestamp: datetime = field(default_factory=datetime.now)
    recommended_id: str = ""
    recommended_score: float = 0.0
    chosen_id: str = ""
    chosen_score: float = 0.0
    deviation: float = 0.0  # How far off was the recommendation


@dataclass
class EnergyObservation:
    """Records task completion patterns for energy inference."""
    timestamp: datetime = field(default_factory=datetime.now)
    hour: int = 0
    context_type: EnergyCategory = EnergyCategory.DEEP_COGNITIVE
    completion_speed: float = 0.0  # Ratio: estimated time / actual time
    quality_indicator: float = 1.0  # 1.0 = normal, <1 = below, >1 = above


class LearningEngine:
    """
    Observes Mani's actual behaviour and adjusts Gravity's models.
    Over time, Gravity becomes Mani-specific.

    Learning windows:
    - Revealed preference: 90-day rolling
    - Proximity curve: 30-day calibration, monthly recalibration
    - Energy patterns: 90-day behaviour analysis
    """

    PREFERENCE_WINDOW_DAYS = 90
    CLIFF_CALIBRATION_DAYS = 30
    ENERGY_WINDOW_DAYS = 90

    # Bounded adjustments — prevents runaway
    MASS_ADJUSTMENT_MIN = 0.5
    MASS_ADJUSTMENT_MAX = 1.5

    def __init__(self):
        self._preference_log: list[PreferenceObservation] = []
        self._energy_log: list[EnergyObservation] = []
        self._completion_log: list[dict] = []
        self._failure_log: list[FailureRecord] = []

        # Learned adjustments
        self._mass_adjustments: dict[str, float] = {}  # tag → multiplier
        self._personal_cliff: dict[str, float] = {}    # zone → multiplier
        self._energy_map: dict[int, list[EnergyCategory]] = {}  # hour → best categories

    # ── 1. Revealed Preference Learning ──────────────────────────

    def record_choice(
        self,
        recommended: GravityItem,
        chosen: GravityItem,
    ):
        """
        Record when Mani chooses differently from Gravity's recommendation.
        Over time, this calibrates mass weights.
        """
        obs = PreferenceObservation(
            recommended_id=recommended.id,
            recommended_score=recommended.gravity_score,
            chosen_id=chosen.id,
            chosen_score=chosen.gravity_score,
            deviation=abs(recommended.gravity_score - chosen.gravity_score),
        )
        self._preference_log.append(obs)

        logger.info(
            f"Preference recorded: recommended {recommended.title} "
            f"({recommended.gravity_score:.0f}), chose {chosen.title} "
            f"({chosen.gravity_score:.0f})"
        )

    def calculate_mass_adjustments(
        self,
        items: dict[str, GravityItem],
    ) -> dict[str, float]:
        """
        Analyse revealed preferences to adjust mass weights.

        Formula:
          adjusted_mass = declared_mass × revealed_preference_multiplier
          multiplier = actual_completion_rate / expected_completion_rate
          Bounded: 0.5 to 1.5

        Returns: dict of tag → adjustment multiplier
        """
        cutoff = datetime.now() - timedelta(days=self.PREFERENCE_WINDOW_DAYS)
        recent = [p for p in self._preference_log if p.timestamp > cutoff]

        if len(recent) < 10:
            return {}  # Not enough data yet

        # Count how often items of each tag are chosen vs. recommended
        tag_chosen = Counter()
        tag_recommended = Counter()

        for obs in recent:
            chosen = items.get(obs.chosen_id)
            recommended = items.get(obs.recommended_id)
            if chosen:
                for tag in chosen.tags:
                    tag_chosen[tag] += 1
            if recommended:
                for tag in recommended.tags:
                    tag_recommended[tag] += 1

        adjustments = {}
        for tag in set(list(tag_chosen.keys()) + list(tag_recommended.keys())):
            chosen_count = tag_chosen.get(tag, 0)
            recommended_count = tag_recommended.get(tag, 1)  # Avoid division by zero
            ratio = chosen_count / recommended_count

            # Bound the adjustment
            multiplier = max(
                self.MASS_ADJUSTMENT_MIN,
                min(ratio, self.MASS_ADJUSTMENT_MAX)
            )
            adjustments[tag] = round(multiplier, 2)

        self._mass_adjustments = adjustments
        logger.info(f"Mass adjustments recalculated: {adjustments}")
        return adjustments

    def get_mass_adjustment(self, item: GravityItem) -> float:
        """Get the learned mass adjustment for an item based on its tags."""
        if not self._mass_adjustments:
            return 1.0

        # Average adjustment across item's tags
        relevant = [
            self._mass_adjustments[tag]
            for tag in item.tags
            if tag in self._mass_adjustments
        ]

        if not relevant:
            return 1.0

        return round(sum(relevant) / len(relevant), 2)

    def get_preference_accuracy(self) -> float:
        """
        What % of the time does Gravity's top-3 match Mani's actual choices?
        """
        cutoff = datetime.now() - timedelta(days=30)
        recent = [p for p in self._preference_log if p.timestamp > cutoff]

        if not recent:
            return 0.0

        matches = sum(1 for p in recent if p.deviation < 10)  # Within 10 points
        return round(matches / len(recent) * 100, 1)

    # ── 2. Adaptive Proximity Curve ──────────────────────────────

    def record_completion(self, item: GravityItem):
        """Record when an item was completed relative to its deadline."""
        if not item.proximity_date or not item.completed_at:
            return

        days_before = (item.proximity_date - item.completed_at).total_seconds() / 86400

        self._completion_log.append({
            "item_id": item.id,
            "tags": item.tags,
            "days_before_deadline": days_before,
            "timestamp": item.completed_at,
        })

    def calibrate_cliff_curve(self) -> dict:
        """
        Learn Mani's personal deadline response pattern.

        If Mani consistently starts 2 days before → curve shifts earlier
        If Mani reliably delivers under pressure → curve relaxes
        If Mani panics at 5 days out → curve steepens earlier

        Returns: personalised cliff multipliers per zone
        """
        cutoff = datetime.now() - timedelta(days=self.CLIFF_CALIBRATION_DAYS)
        recent = [c for c in self._completion_log if c["timestamp"] > cutoff]

        if len(recent) < 5:
            return {}  # Not enough data

        # Analyse when Mani actually starts working
        days_before = [c["days_before_deadline"] for c in recent]
        avg_start = sum(days_before) / len(days_before)

        curve = {}
        if avg_start >= 5:
            # Early starter — relax the curve slightly
            curve = {
                "awareness_multiplier": 0.9,
                "tension_multiplier": 0.9,
                "description": "You start early — curve relaxed slightly",
            }
        elif avg_start <= 1:
            # Last-minute worker — steepen the curve
            curve = {
                "awareness_multiplier": 1.3,
                "tension_multiplier": 1.2,
                "description": "You work best under pressure — but curve steepened for safety",
            }
        else:
            curve = {
                "awareness_multiplier": 1.0,
                "tension_multiplier": 1.0,
                "description": "Balanced deadline approach — curve at default",
            }

        self._personal_cliff = curve
        logger.info(f"Cliff curve calibrated: {curve}")
        return curve

    # ── 3. Failure Archaeology ───────────────────────────────────

    def record_failure(
        self,
        item: GravityItem,
        failure_type: str,
        root_causes: dict[str, float],
    ) -> FailureRecord:
        """
        Automated post-mortem when a gravity item fails.
        Analyses why and applies prevention to similar items.

        Args:
            item: The failed item
            failure_type: missed_deadline, abandoned, quality_failure
            root_causes: Dict of cause → percentage (should sum to 100)
        """
        record = FailureRecord(
            failure_type=failure_type,
            root_causes=root_causes,
            prevention_rules=self._generate_prevention_rules(item, root_causes),
        )

        item.failure_history.append(record)
        self._failure_log.append(record)

        logger.warning(
            f"Failure archaeology: {item.title} — {failure_type}. "
            f"Prevention rules: {record.prevention_rules}"
        )

        return record

    def _generate_prevention_rules(
        self,
        item: GravityItem,
        root_causes: dict[str, float],
    ) -> list[str]:
        """Generate prevention rules from failure analysis."""
        rules = []

        for cause, pct in root_causes.items():
            if pct < 15:
                continue  # Skip minor causes

            if "mass" in cause.lower() or "weight" in cause.lower():
                rules.append(
                    f"Items tagged '{', '.join(item.tags)}': mass increased by +20"
                )
            elif "collision" in cause.lower():
                rules.append(
                    "Collision detection window expanded from 3 days to 5 days"
                )
            elif "energy" in cause.lower():
                rules.append(
                    f"'{item.context_type.value}' tasks: auto-scheduled for morning blocks only"
                )
            elif "disruption" in cause.lower() or "external" in cause.lower():
                rules.append(
                    "30-minute recovery buffer added after client calls"
                )
            elif "underestimate" in cause.lower() or "time" in cause.lower():
                rules.append(
                    f"Similar items: time estimates increased by 1.5x"
                )

        return rules

    def get_failure_report(self, lookback_days: int = 30) -> dict:
        """Monthly failure archaeology report."""
        cutoff = datetime.now() - timedelta(days=lookback_days)
        recent = [f for f in self._failure_log if f.date > cutoff]

        if not recent:
            return {
                "failures": 0,
                "learnings": [],
                "accuracy_trend": self.get_preference_accuracy(),
            }

        all_causes = Counter()
        all_rules = []
        for f in recent:
            for cause in f.root_causes:
                all_causes[cause] += 1
            all_rules.extend(f.prevention_rules)

        return {
            "failures": len(recent),
            "top_causes": dict(all_causes.most_common(5)),
            "prevention_rules_active": len(set(all_rules)),
            "learnings": list(set(all_rules)),
            "accuracy_trend": self.get_preference_accuracy(),
        }

    # ── 4. Energy Pattern Learning ───────────────────────────────

    def record_energy_observation(
        self,
        context_type: EnergyCategory,
        completion_speed: float,
        quality_indicator: float = 1.0,
    ):
        """Record an energy/performance observation."""
        obs = EnergyObservation(
            hour=datetime.now().hour,
            context_type=context_type,
            completion_speed=completion_speed,
            quality_indicator=quality_indicator,
        )
        self._energy_log.append(obs)

    def learn_energy_patterns(self) -> dict[int, list[EnergyCategory]]:
        """
        Analyse which tasks perform best at which hours.
        Returns: hour → list of best energy categories (ranked)
        """
        cutoff = datetime.now() - timedelta(days=self.ENERGY_WINDOW_DAYS)
        recent = [e for e in self._energy_log if e.timestamp > cutoff]

        if len(recent) < 20:
            return {}

        # Group by hour and category, average speed
        hour_category_speeds = defaultdict(lambda: defaultdict(list))
        for obs in recent:
            hour_category_speeds[obs.hour][obs.context_type].append(obs.completion_speed)

        energy_map = {}
        for hour, categories in hour_category_speeds.items():
            # Rank categories by average speed at this hour
            avg_speeds = {
                cat: sum(speeds) / len(speeds)
                for cat, speeds in categories.items()
                if len(speeds) >= 2  # Need at least 2 observations
            }
            if avg_speeds:
                ranked = sorted(avg_speeds.items(), key=lambda x: x[1], reverse=True)
                energy_map[hour] = [cat for cat, _ in ranked]

        self._energy_map = energy_map
        logger.info(f"Energy patterns learned for {len(energy_map)} hours")
        return energy_map

    def get_best_time_for(self, category: EnergyCategory) -> Optional[str]:
        """Suggest the best time of day for a given task type."""
        if not self._energy_map:
            # Defaults
            defaults = {
                EnergyCategory.DEEP_COGNITIVE: "morning (7-11am)",
                EnergyCategory.COLLABORATIVE: "mid-morning to early afternoon",
                EnergyCategory.CREATIVE: "varies — check after 30 days of data",
                EnergyCategory.ADMINISTRATIVE: "late afternoon",
                EnergyCategory.UNCOMFORTABLE: "when energy is high — morning",
            }
            return defaults.get(category)

        best_hours = []
        for hour, categories in self._energy_map.items():
            if categories and categories[0] == category:
                best_hours.append(hour)

        if best_hours:
            times = [f"{h}:00" for h in sorted(best_hours)]
            return f"Best hours: {', '.join(times)}"

        return None

    # ── Aggregate Learning Status ────────────────────────────────

    def status(self) -> dict:
        """Learning system status for field snapshot."""
        return {
            "preference_observations": len(self._preference_log),
            "recommendation_accuracy_30d": self.get_preference_accuracy(),
            "mass_adjustments": self._mass_adjustments,
            "cliff_curve": self._personal_cliff,
            "energy_patterns_learned": len(self._energy_map),
            "failures_recorded": len(self._failure_log),
            "prevention_rules_active": len(set(
                rule for f in self._failure_log for rule in f.prevention_rules
            )),
        }
