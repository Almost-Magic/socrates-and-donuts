"""
Gravity Field Engine v2
The core physics model: calculates gravity scores for all items,
detects collisions, manages the field, and produces the daily map.

Patentable: Multi-Body Decision Physics with Consequence Modelling

Almost Magic Tech Lab — Patentable IP
"""

import math
import logging
from datetime import datetime, timedelta
from typing import Optional

from .models import (
    GravityItem, GravityFieldSnapshot, GravityBreakdown,
    Collision, CollisionOption, ContextCollapseWarning,
    AlertLevel, MomentumState, EnergyCategory, TrajectoryDirection,
)
from .governors import GovernorSystem

logger = logging.getLogger("elaine.gravity")


class GravityField:
    """
    The Gravity Field: a multi-body physics model for decision-making.

    Items don't exist in isolation — they orbit each other, create clusters,
    propagate effects, and occasionally collide.

    Usage:
        field = GravityField()
        field.add_item(item)
        field.recalculate()
        snapshot = field.snapshot()
    """

    # ── Default proximity curve (learned over time) ──
    DEFAULT_CLIFF = {
        "calm":       {"days_min": 14, "days_max": None, "multiplier": 1.0},
        "awareness":  {"days_min": 7,  "days_max": 14,   "multiplier": 1.3},
        "tension":    {"days_min": 3,  "days_max": 7,    "multiplier": 1.8},
        "urgency":    {"days_min": 1,  "days_max": 3,    "multiplier": 3.0},
        "critical":   {"days_min": 0,  "days_max": 1,    "multiplier": 5.0},
        "overdue":    {"days_min": None, "days_max": 0,  "multiplier": 8.0},
    }

    NORMALISATION_DIVISOR = 350.0  # Tuned so typical max raw ≈ 350 → score 100

    def __init__(self):
        self.items: dict[str, GravityItem] = {}
        self.governors = GovernorSystem()
        self.personal_cliff = dict(self.DEFAULT_CLIFF)
        self._last_recalc: Optional[datetime] = None
        self._recalc_count_this_hour: int = 0
        self._snapshot_history: list[GravityFieldSnapshot] = []

    # ── Item Management ────────────────────────────────────────────

    def add_item(self, item: GravityItem) -> GravityItem:
        """Add a gravity item to the field."""
        self.items[item.id] = item
        logger.info(f"Added gravity item: {item.id} — {item.title}")
        return item

    def update_item(self, item_id: str, **kwargs) -> Optional[GravityItem]:
        """Update fields on an existing gravity item."""
        item = self.items.get(item_id)
        if not item:
            logger.warning(f"Item not found: {item_id}")
            return None
        for key, value in kwargs.items():
            if hasattr(item, key):
                setattr(item, key, value)
        item.last_touched = datetime.now()
        return item

    def complete_item(self, item_id: str) -> Optional[GravityItem]:
        """Mark an item as complete and propagate effects."""
        item = self.items.get(item_id)
        if not item:
            return None
        item.momentum = MomentumState.COMPLETE
        item.completed_at = datetime.now()
        item.progress_percent = 100.0
        item.gravity_score = 0.0
        self._propagate_completion(item)
        logger.info(f"Completed: {item.id} — {item.title}")
        return item

    def deprioritise_item(self, item_id: str) -> Optional[GravityItem]:
        """Move to the Ungraviton — conscious neglect."""
        item = self.items.get(item_id)
        if not item:
            return None
        item.deprioritised = True
        item.deprioritised_since = datetime.now()
        logger.info(f"Deprioritised: {item.id} — {item.title}")
        return item

    def revive_item(self, item_id: str) -> Optional[GravityItem]:
        """Bring back from the Ungraviton."""
        item = self.items.get(item_id)
        if not item:
            return None
        item.deprioritised = False
        item.deprioritised_since = None
        logger.info(f"Revived: {item.id} — {item.title}")
        return item

    def record_avoidance(self, item_id: str):
        """Record that Mani chose something else over this item."""
        item = self.items.get(item_id)
        if item:
            item.avoidance_count += 1

    # ── The Core Gravity Equation ──────────────────────────────────

    def calculate_gravity(self, item: GravityItem) -> GravityBreakdown:
        """
        G(item) = clamp( (M × P × C × Kq) + Mo + B + E, 0, 100 )

        Where:
          M   = Mass Score (0-100), adjusted by revealed preference
          P   = Proximity Multiplier (adaptive cliff curve)
          C   = Charge Multiplier (relational weight)
          Kq  = Consequence Multiplier (failure cascade severity)
          Mo  = Momentum Adjustment (with inertia)
          B   = Burst Events (external triggers)
          E   = Energy-Task Fit Modifier
        """
        if item.deprioritised or item.momentum == MomentumState.COMPLETE:
            return GravityBreakdown(
                normalised_score=0.0,
                explanation="Item is deprioritised or complete."
            )

        # M — Mass with learned adjustment
        M = item.mass * item.learned_mass_adjustment

        # P — Proximity multiplier
        P = self._calculate_proximity(item)

        # C — Charge multiplier
        C = item.charge.charge_multiplier

        # Kq — Consequence multiplier
        Kq = item.consequence.kq_multiplier

        # Mo — Momentum adjustment
        Mo = self._calculate_momentum(item)

        # B — Burst events (placeholder — fed by external systems)
        B = 0.0

        # E — Energy-task fit
        E = self._calculate_energy_fit(item)

        # ── The Equation ──
        raw = (M * P * C * Kq) + Mo + B + E

        # ── Apply Governors ──
        caps = []

        # Damping Governor — saturate overdue items
        raw, damping_applied = self.governors.apply_damping(item, raw)
        if damping_applied:
            caps.append("damping")

        # Inertia Governor — protect active work
        inertia_bonus = self.governors.apply_inertia(item)

        # Moral Governor — strategic floor
        raw = self.governors.apply_moral_floor(item, raw)

        # Normalise to 0-100
        normalised = min(max(raw / self.NORMALISATION_DIVISOR * 100, 0), 100)

        # Build explanation
        explanation = self._build_explanation(item, M, P, C, Kq, Mo, B, E, normalised)

        breakdown = GravityBreakdown(
            mass_component=M,
            proximity_multiplier=P,
            charge_multiplier=C,
            consequence_multiplier=Kq,
            momentum_adjustment=Mo,
            burst_component=B,
            energy_fit_modifier=E,
            raw_score=raw,
            normalised_score=round(normalised, 1),
            governor_caps_applied=caps,
            inertia_active=item.inertia_active,
            explanation=explanation,
        )

        return breakdown

    def _calculate_proximity(self, item: GravityItem) -> float:
        """Adaptive cliff curve: learns from personal patterns."""
        if not item.proximity_date:
            return 1.0  # No deadline = no time pressure

        days = item.days_until_due
        if days is None:
            return 1.0

        # Personal cliff multiplier adjusts the curve
        pcm = item.personal_cliff_multiplier

        if days > 14:
            return 1.0 * pcm
        elif days > 7:
            return 1.3 * pcm
        elif days > 3:
            return 1.8 * pcm
        elif days > 1:
            return 3.0 * pcm
        elif days > 0:
            return 5.0 * pcm
        else:
            # Overdue — saturates at day 3 (Damping Governor)
            overdue_days = abs(days)
            if overdue_days <= 1:
                return 8.0
            elif overdue_days <= 2:
                return 8.5
            else:
                return 9.0  # Saturated — Governor caps here

    def _calculate_momentum(self, item: GravityItem) -> float:
        """Momentum: work in progress gets a boost. Inertia protects it."""
        momentum_map = {
            MomentumState.NOT_STARTED: -5.0,
            MomentumState.STARTED: 5.0,
            MomentumState.IN_PROGRESS: 15.0,
            MomentumState.BLOCKED: -10.0,
            MomentumState.NEAR_COMPLETE: 25.0,
            MomentumState.COMPLETE: 0.0,
            MomentumState.ABANDONED: 0.0,
        }
        base = momentum_map.get(item.momentum, 0.0)

        # Progress bonus
        if item.progress_percent > 75:
            base += 10.0  # Almost there — don't drop it
        elif item.progress_percent > 50:
            base += 5.0

        return base

    def _calculate_energy_fit(self, item: GravityItem) -> float:
        """
        Energy-task fit modifier.
        Inferred from current time of day and observed energy patterns.
        Placeholder: will be fed by learning engine.
        """
        hour = datetime.now().hour

        # Simple heuristic until learning kicks in
        if item.context_type == EnergyCategory.DEEP_COGNITIVE:
            if 7 <= hour <= 11:
                return 5.0   # Morning = good for deep work
            elif 14 <= hour <= 16:
                return -5.0  # Post-lunch slump
        elif item.context_type == EnergyCategory.ADMINISTRATIVE:
            if 16 <= hour <= 18:
                return 5.0   # End of day = good for admin
        elif item.context_type == EnergyCategory.CREATIVE:
            if 9 <= hour <= 12:
                return 3.0

        return 0.0

    def _build_explanation(self, item, M, P, C, Kq, Mo, B, E, score) -> str:
        """Build human-readable explanation for the score."""
        parts = []
        parts.append(f"Gravity: {score:.0f}/100")

        reasons = []
        if P >= 5.0:
            reasons.append("due today or overdue")
        elif P >= 3.0:
            reasons.append(f"due within {item.days_until_due:.0f} days")
        if item.charge.tier == 1:
            reasons.append("Tier 1 client")
        if item.consequence.revenue_at_risk > 10000:
            reasons.append(f"${item.consequence.revenue_at_risk:,.0f} at risk")
        if len(item.consequence.blocked_items) > 0:
            reasons.append(f"{len(item.consequence.blocked_items)} items blocked")
        if item.okr_alignment:
            reasons.append(f"OKR: {', '.join(item.okr_alignment)}")
        if item.avoidance_count >= 3:
            reasons.append(f"avoided {item.avoidance_count} times")

        if reasons:
            parts.append("Because: " + " + ".join(reasons))

        return ". ".join(parts)

    # ── Field Operations ───────────────────────────────────────────

    def recalculate(self):
        """
        Recalculate gravity for ALL active items.
        Event-driven: called when items change, not on a timer.
        """
        # Damping Governor: limit recalc frequency
        if not self.governors.allow_recalculation(self._last_recalc, self._recalc_count_this_hour):
            logger.debug("Recalculation dampened — too frequent")
            return

        self._recalc_count_this_hour += 1
        self._last_recalc = datetime.now()

        active_items = [
            item for item in self.items.values()
            if not item.deprioritised and item.momentum != MomentumState.COMPLETE
        ]

        for item in active_items:
            breakdown = self.calculate_gravity(item)
            item.gravity_score = breakdown.normalised_score
            item.breakdown = breakdown
            item.alert_level = self._determine_alert_level(item)
            item.trajectory = self._calculate_trajectory(item)

        logger.info(f"Recalculated gravity for {len(active_items)} items")

    def _determine_alert_level(self, item: GravityItem) -> AlertLevel:
        """Determine the alert level for an item."""
        if item.gravity_score >= 90:
            return AlertLevel.RED_GIANT
        if item.gravity_score >= 70:
            return AlertLevel.APPROACHING_MASS
        if item.days_untouched >= 5 and item.trajectory == TrajectoryDirection.RISING:
            return AlertLevel.ORBITAL_DRIFT
        if item.okr_alignment and item.days_untouched >= 7:
            return AlertLevel.STRATEGIC_FLOOR
        return AlertLevel.NORMAL

    def _calculate_trajectory(self, item: GravityItem) -> TrajectoryDirection:
        """Determine if gravity is rising, stable, or falling."""
        if not item.proximity_date:
            return TrajectoryDirection.STABLE
        days = item.days_until_due
        if days is not None and days < 0 and abs(days) >= 3:
            return TrajectoryDirection.SATURATED
        if days is not None and days < 3:
            return TrajectoryDirection.RISING
        if item.momentum in (MomentumState.IN_PROGRESS, MomentumState.NEAR_COMPLETE):
            return TrajectoryDirection.FALLING  # Progress = gravity reducing
        return TrajectoryDirection.STABLE

    # ── Collision Detection ────────────────────────────────────────

    def detect_collisions(self, available_hours: float = 8.0) -> list[Collision]:
        """
        Detect when two high-gravity items can't both be done today.
        Returns collision objects with resolution options.
        """
        collisions = []
        red_and_approaching = sorted(
            [i for i in self.items.values()
             if i.alert_level in (AlertLevel.RED_GIANT, AlertLevel.APPROACHING_MASS)
             and not i.deprioritised and i.momentum != MomentumState.COMPLETE],
            key=lambda x: x.gravity_score,
            reverse=True,
        )

        total_hours_needed = sum(i.estimated_hours for i in red_and_approaching)
        if total_hours_needed <= available_hours:
            return []

        # Find pairs that can't coexist
        for i, item_a in enumerate(red_and_approaching):
            for item_b in red_and_approaching[i + 1:]:
                combined_hours = item_a.estimated_hours + item_b.estimated_hours
                if combined_hours > available_hours:
                    collision = Collision(
                        item_a_id=item_a.id,
                        item_b_id=item_b.id,
                        options=self._generate_resolution_options(item_a, item_b),
                    )
                    collisions.append(collision)

        return collisions

    def _generate_resolution_options(
        self, item_a: GravityItem, item_b: GravityItem
    ) -> list[CollisionOption]:
        """Generate resolution options with opportunity cost analysis."""
        options = []

        # Option A: Do item_a first
        options.append(CollisionOption(
            label=f"{item_a.title} first",
            description=f"Do {item_a.title} (morning), {item_b.title} (afternoon)",
            gains=[f"${item_a.consequence.revenue_at_risk:,.0f} secured" if item_a.consequence.revenue_at_risk else "Priority 1 completed"],
            costs=[f"{item_b.title} compressed — quality risk"],
            net_impact=f"+${item_a.consequence.revenue_at_risk:,.0f}" if item_a.consequence.revenue_at_risk else "Priority 1 secured",
            recommended=item_a.gravity_score > item_b.gravity_score,
        ))

        # Option B: Request extension on higher-gravity item
        options.append(CollisionOption(
            label="Request extension",
            description=f"Request 24-hour extension on {item_a.title}",
            gains=["Both items get proper attention"],
            costs=[f"Trust cost: {'LOW' if item_a.charge.prior_misses == 0 else 'MODERATE'}"],
            net_impact="No immediate financial impact",
            recommended=False,
        ))

        # Option C: Do item_b first
        options.append(CollisionOption(
            label=f"{item_b.title} first",
            description=f"Do {item_b.title} first, {item_a.title} evening",
            gains=[f"{item_b.title} quality maintained"],
            costs=[f"{item_a.title} quality suffers (low-energy evening)"],
            net_impact=f"-${item_a.consequence.revenue_at_risk:,.0f} risk" if item_a.consequence.revenue_at_risk else "Priority 1 delayed",
            recommended=False,
        ))

        return options

    # ── Propagation ────────────────────────────────────────────────

    def _propagate_completion(self, completed_item: GravityItem):
        """When an item completes, propagate effects to connected items."""
        for effect in completed_item.propagation_effects:
            target = self.items.get(effect.target_id)
            if not target:
                continue

            if effect.eliminate_on_complete:
                target.momentum = MomentumState.ABANDONED
                target.gravity_score = 0
                logger.info(f"Eliminated {target.id} (dependency on {completed_item.id} complete)")
            elif effect.on_complete_delta:
                target.mass += effect.on_complete_delta
                logger.info(f"Propagated +{effect.on_complete_delta} mass to {target.id}")

    # ── Context Collapse Detection ─────────────────────────────────

    def detect_context_collapse(self) -> Optional[ContextCollapseWarning]:
        """
        Detect when a day requires too many mental modes.
        Context switching costs ~40% cognitive efficiency.
        """
        active = [
            i for i in self.items.values()
            if i.gravity_score >= 40 and not i.deprioritised
            and i.momentum != MomentumState.COMPLETE
        ]

        context_types = set(i.context_type for i in active)
        if len(context_types) <= 3:
            return None

        # Estimate switching cost: ~25 min per switch
        num_switches = len(context_types) - 1
        switching_cost_hours = (num_switches * 25) / 60

        # Build batching recommendation
        batching = {}
        category_groups = {
            "analytical_morning": [EnergyCategory.DEEP_COGNITIVE, EnergyCategory.ADMINISTRATIVE],
            "communication_midday": [EnergyCategory.COLLABORATIVE, EnergyCategory.UNCOMFORTABLE],
            "creative_afternoon": [EnergyCategory.CREATIVE],
        }

        for slot, categories in category_groups.items():
            items_in_slot = [i.title for i in active if i.context_type in categories]
            if items_in_slot:
                batching[slot] = items_in_slot

        return ContextCollapseWarning(
            context_types_required=len(context_types),
            estimated_switching_cost_hours=round(switching_cost_hours, 1),
            batching_recommendation=batching,
            estimated_savings_hours=round(switching_cost_hours * 0.6, 1),
        )

    # ── Snapshot & Reporting ───────────────────────────────────────

    def snapshot(self) -> GravityFieldSnapshot:
        """Produce a complete field snapshot for the morning briefing."""
        self.recalculate()

        active = [
            i for i in self.items.values()
            if not i.deprioritised and i.momentum != MomentumState.COMPLETE
        ]
        deprioritised = [i for i in self.items.values() if i.deprioritised]

        red_giants = [i for i in active if i.alert_level == AlertLevel.RED_GIANT]
        approaching = [i for i in active if i.alert_level == AlertLevel.APPROACHING_MASS]
        stable = [i for i in active if i.alert_level == AlertLevel.NORMAL]
        peripheral = [i for i in active if i.gravity_score < 30]

        top_3 = sorted(active, key=lambda x: x.gravity_score, reverse=True)[:3]

        # Consequence exposure
        total_revenue_risk = sum(i.consequence.revenue_at_risk for i in active)
        total_blocked = sum(len(i.consequence.blocked_items) for i in active)
        okrs_at_risk = list(set(
            okr for i in active
            if i.days_untouched >= 7
            for okr in i.okr_alignment
        ))

        # Trust debt
        trust_debt = sum(i.charge.trust_cost_aud for i in active if i.charge.trust_cost_aud > 0)
        trust_items = len([i for i in active if i.charge.trust_cost_aud > 0])
        cooling = list(set(
            person for i in active
            if i.charge.prior_misses >= 2
            for person in i.charge.people
        ))

        # Ungraviton pattern analysis
        ungrav_tags = [tag for i in deprioritised for tag in i.tags]
        ungrav_pattern = None
        if ungrav_tags:
            from collections import Counter
            most_common = Counter(ungrav_tags).most_common(1)
            if most_common and most_common[0][1] >= 2:
                ungrav_pattern = f"{most_common[0][0]}_avoidance"

        snap = GravityFieldSnapshot(
            total_items=len(active),
            red_giants=len(red_giants),
            approaching=len(approaching),
            stable=len(stable),
            peripheral=len(peripheral),
            collisions=self.detect_collisions(),
            top_3_ids=[i.id for i in top_3],
            trust_debt_total_aud=trust_debt,
            trust_debt_items=trust_items,
            relationships_cooling=cooling,
            consequence_exposure={
                "total_revenue_at_risk": total_revenue_risk,
                "total_blocked_items": total_blocked,
                "okrs_at_risk": okrs_at_risk,
            },
            context_collapse=self.detect_context_collapse(),
            required_hours_red_giant=sum(i.estimated_hours for i in red_giants),
            governor_status=self.governors.status(),
            ungraviton_count=len(deprioritised),
            ungraviton_pattern=ungrav_pattern,
        )

        self._snapshot_history.append(snap)
        return snap

    def get_top_items(self, n: int = 5) -> list[GravityItem]:
        """Get top N items by gravity score."""
        active = [
            i for i in self.items.values()
            if not i.deprioritised and i.momentum != MomentumState.COMPLETE
        ]
        return sorted(active, key=lambda x: x.gravity_score, reverse=True)[:n]

    def get_ungraviton(self) -> list[GravityItem]:
        """Get all deprioritised items."""
        return [i for i in self.items.values() if i.deprioritised]

    def get_item(self, item_id: str) -> Optional[GravityItem]:
        """Get a specific item by ID."""
        return self.items.get(item_id)

    def active_item_count(self) -> int:
        """Number of active (non-deprioritised, non-complete) items."""
        return len([
            i for i in self.items.values()
            if not i.deprioritised and i.momentum != MomentumState.COMPLETE
        ])
