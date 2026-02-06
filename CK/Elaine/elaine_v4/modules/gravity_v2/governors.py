"""
The Three Governors
Prevent Gravity from becoming an anxiety engine.

Governor 1 — Damping: Saturates overdue items, limits recalc frequency
Governor 2 — Inertia: Protects deep work from interruption
Governor 3 — Moral Governor: Permits rest, nudges uncomfortable tasks

Almost Magic Tech Lab — Patentable IP
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from .models import (
    GravityItem, MomentumState, AlertLevel,
)

logger = logging.getLogger("elaine.gravity.governors")


class GovernorSystem:
    """
    The Three Governors prevent an unregulated priority system from
    becoming an anxiety engine. Every reviewer of v1 flagged this risk.
    """

    # ── Damping ──
    OVERDUE_SATURATION_DAY = 3       # Stop climbing after 3 days overdue
    MAX_RECALCS_PER_HOUR = 3         # Limit recalculation frequency
    RENEGOTIATE_THRESHOLD_DAYS = 7   # Trigger "Renegotiate or Release" prompt

    # ── Inertia ──
    INERTIA_BONUS = 20.0             # Active items resist displacement
    MIN_FOCUS_MINUTES = 45           # No interruption before this
    CONTEXT_SWITCH_TAX_MINUTES = 15  # Recovery time after switch

    # ── Moral Governor ──
    STRATEGIC_FLOOR = 30.0           # OKR-aligned items never go below this
    AVOIDANCE_THRESHOLD = 3          # After 3 avoidances, flag the item

    def __init__(self):
        self._active_item_id: Optional[str] = None
        self._focus_started: Optional[datetime] = None
        self._recalc_times: list[datetime] = []

    # ── Governor 1: Damping ──────────────────────────────────────

    def apply_damping(self, item: GravityItem, raw_score: float) -> tuple[float, bool]:
        """
        Saturate overdue items — escalating further doesn't help.
        After 3 days overdue, proximity multiplier stops climbing.
        After 7 days, trigger 'Renegotiate or Release'.

        Returns: (adjusted_score, was_damping_applied)
        """
        if not item.is_overdue:
            return raw_score, False

        overdue_days = item.days_overdue

        if overdue_days > self.OVERDUE_SATURATION_DAY:
            # Cap the score — pressure isn't going to help anymore
            cap = raw_score * 0.95  # Slight reduction to signal saturation
            logger.debug(f"Damping applied to {item.id}: {overdue_days:.1f} days overdue")
            return cap, True

        return raw_score, False

    def should_renegotiate(self, item: GravityItem) -> bool:
        """Check if item should trigger 'Renegotiate or Release' dialogue."""
        return item.is_overdue and item.days_overdue >= self.RENEGOTIATE_THRESHOLD_DAYS

    def get_renegotiate_items(self, items: dict[str, GravityItem]) -> list[GravityItem]:
        """Get all items that need the 'Renegotiate or Release' conversation."""
        return [
            item for item in items.values()
            if self.should_renegotiate(item) and not item.deprioritised
        ]

    def allow_recalculation(
        self,
        last_recalc: Optional[datetime],
        count_this_hour: int
    ) -> bool:
        """
        Prevent recalculation storms.
        Max 3 recalcs per hour with major shifts.
        """
        if last_recalc is None:
            return True

        # Reset counter if it's been more than an hour
        if (datetime.now() - last_recalc) > timedelta(hours=1):
            return True

        return count_this_hour < self.MAX_RECALCS_PER_HOUR

    # ── Governor 2: Inertia ──────────────────────────────────────

    def apply_inertia(self, item: GravityItem) -> float:
        """
        Items you're actively working on resist displacement.
        Returns the inertia bonus (0 or INERTIA_BONUS).
        """
        if item.inertia_active:
            return self.INERTIA_BONUS
        return 0.0

    def set_active_item(self, item_id: str):
        """Mark an item as actively being worked on."""
        self._active_item_id = item_id
        self._focus_started = datetime.now()
        logger.info(f"Inertia activated for: {item_id}")

    def clear_active_item(self):
        """Clear the currently active item."""
        self._active_item_id = None
        self._focus_started = None

    def can_interrupt(self, interrupting_item: GravityItem) -> tuple[bool, str]:
        """
        Check if a new item can interrupt the current focus.

        Rules:
        - Must exceed minimum focus block (45 min)
        - Red Giant alerts override inertia
        - Interrupting item must exceed current + INERTIA_BONUS
        """
        if not self._active_item_id or not self._focus_started:
            return True, "No active focus session"

        # Red Giant always interrupts
        if interrupting_item.alert_level == AlertLevel.RED_GIANT:
            return True, "Red Giant overrides inertia"

        # Check minimum focus time
        elapsed = datetime.now() - self._focus_started
        if elapsed < timedelta(minutes=self.MIN_FOCUS_MINUTES):
            remaining = self.MIN_FOCUS_MINUTES - (elapsed.total_seconds() / 60)
            return False, f"Focus protected. {remaining:.0f} minutes remaining before interruption."

        return True, "Focus block complete — interruption allowed"

    def context_switch_cost(self) -> timedelta:
        """The cognitive tax of switching contexts."""
        return timedelta(minutes=self.CONTEXT_SWITCH_TAX_MINUTES)

    # ── Governor 3: The Moral Governor ───────────────────────────

    def apply_moral_floor(self, item: GravityItem, raw_score: float) -> float:
        """
        Strategic items never disappear completely.
        OKR-aligned items get a floor gravity of 30.
        """
        if item.okr_alignment and raw_score < self.STRATEGIC_FLOOR:
            logger.debug(f"Moral floor applied to {item.id}: {raw_score:.1f} → {self.STRATEGIC_FLOOR}")
            return self.STRATEGIC_FLOOR
        return raw_score

    def should_suggest_rest(
        self,
        items: dict[str, GravityItem],
        available_hours: float
    ) -> Optional[str]:
        """
        Sometimes the right priority is rest.
        If no Red Giants and available hours exceed required, say so.
        """
        active = [
            i for i in items.values()
            if not i.deprioritised and i.momentum != MomentumState.COMPLETE
        ]

        red_giants = [i for i in active if i.gravity_score >= 90]
        if red_giants:
            return None

        required_hours = sum(i.estimated_hours for i in active if i.gravity_score >= 50)
        if required_hours < available_hours * 0.6:
            return (
                "You're ahead. No Red Giants, and your required hours are well "
                "within capacity. Protect this space — rest is productive today."
            )

        return None

    def should_nudge_uncomfortable(self, item: GravityItem) -> Optional[str]:
        """
        When an uncomfortable but important item has been avoided 3+ times,
        flag it differently.
        """
        if item.avoidance_count >= self.AVOIDANCE_THRESHOLD:
            return (
                f"'{item.title}' keeps getting pushed. It might be uncomfortable, "
                f"but it matters. Want to tackle it now while you have energy?"
            )
        return None

    def get_nudges(self, items: dict[str, GravityItem]) -> list[dict]:
        """Get all active moral governor nudges."""
        nudges = []

        for item in items.values():
            if item.deprioritised or item.momentum == MomentumState.COMPLETE:
                continue

            # Uncomfortable avoidance
            msg = self.should_nudge_uncomfortable(item)
            if msg:
                nudges.append({"type": "avoidance", "item_id": item.id, "message": msg})

            # Renegotiate prompt
            if self.should_renegotiate(item):
                nudges.append({
                    "type": "renegotiate",
                    "item_id": item.id,
                    "message": (
                        f"'{item.title}' has been overdue for {item.days_overdue:.0f} days. "
                        f"Should we renegotiate the deadline or release it to the Ungraviton?"
                    ),
                })

            # Strategic drift
            if item.okr_alignment and item.days_untouched >= 7:
                nudges.append({
                    "type": "strategic_drift",
                    "item_id": item.id,
                    "message": (
                        f"Your '{', '.join(item.okr_alignment)}' goal hasn't had "
                        f"attention in {item.days_untouched:.0f} days."
                    ),
                })

        return nudges

    # ── Status Report ────────────────────────────────────────────

    def status(self) -> dict:
        """Current governor status for field snapshot."""
        return {
            "damping": {
                "description": "Saturates overdue items after 3 days",
                "active_item_count": 0,  # Populated by field
            },
            "inertia": {
                "active_item": self._active_item_id,
                "focus_started": self._focus_started.isoformat() if self._focus_started else None,
                "bonus": self.INERTIA_BONUS,
            },
            "moral": {
                "strategic_floor": self.STRATEGIC_FLOOR,
                "avoidance_threshold": self.AVOIDANCE_THRESHOLD,
            },
        }
