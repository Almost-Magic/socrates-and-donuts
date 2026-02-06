"""
Trust Ledger v2
Quantified relationship economics: every interaction deposits or withdraws.

Patentable: Quantified Trust Ledger with Transaction History + Decay Model

Almost Magic Tech Lab — Patentable IP
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from .models import (
    POIRecord, TrustAccount, TrustTransaction,
    TrustTransactionType, TRUST_DEFAULTS, POITier,
)

logger = logging.getLogger("elaine.constellation.trust")


class TrustLedger:
    """
    Maintains trust accounts for all POIs.
    Every interaction either deposits or withdraws from trust.
    Relationships decay naturally without maintenance.
    """

    # Alert thresholds
    HEALTHY_THRESHOLD = 30
    COOLING_THRESHOLD = 15
    AT_RISK_THRESHOLD = 5

    # Tier thresholds
    TIER_THRESHOLDS = {
        POITier.INNER_CIRCLE: {"min_trust": 60, "min_frequency": "weekly"},
        POITier.ACTIVE_NETWORK: {"min_trust": 30, "min_frequency": "monthly"},
        POITier.EXTENDED_NETWORK: {"min_trust": 10, "min_frequency": "quarterly"},
        POITier.AWARENESS: {"min_trust": 0, "min_frequency": "rare"},
    }

    TIER_MAX_COUNTS = {
        POITier.INNER_CIRCLE: 15,
        POITier.ACTIVE_NETWORK: 50,
        POITier.EXTENDED_NETWORK: 200,
        POITier.AWARENESS: None,  # Unlimited
    }

    def __init__(self):
        pass

    # ── Transactions ─────────────────────────────────────────────

    def deposit(
        self,
        poi: POIRecord,
        transaction_type: TrustTransactionType,
        reason: str = "",
        amount: Optional[float] = None,
        auto_detected: bool = True,
        source: str = "manual",
    ) -> TrustTransaction:
        """Add a trust deposit to a POI's account."""
        if amount is None:
            amount = abs(TRUST_DEFAULTS.get(transaction_type, 5))

        tx = TrustTransaction(
            amount=abs(amount),
            transaction_type=transaction_type,
            reason=reason,
            auto_detected=auto_detected,
        )

        poi.trust_account.transactions.append(tx)
        poi.trust_account.balance += abs(amount)
        poi.trust_account.last_interaction = datetime.now()

        self._update_trajectory(poi)
        logger.info(
            f"Trust deposit: +{abs(amount)} for {poi.name} "
            f"({transaction_type.value}). Balance: {poi.trust_account.balance:.0f}"
        )
        return tx

    def withdraw(
        self,
        poi: POIRecord,
        transaction_type: TrustTransactionType,
        reason: str = "",
        amount: Optional[float] = None,
        auto_detected: bool = True,
    ) -> TrustTransaction:
        """Record a trust withdrawal from a POI's account."""
        if amount is None:
            amount = abs(TRUST_DEFAULTS.get(transaction_type, -5))

        tx = TrustTransaction(
            amount=-abs(amount),
            transaction_type=transaction_type,
            reason=reason,
            auto_detected=auto_detected,
        )

        poi.trust_account.transactions.append(tx)
        poi.trust_account.balance -= abs(amount)
        poi.trust_account.last_interaction = datetime.now()

        self._update_trajectory(poi)
        logger.warning(
            f"Trust withdrawal: -{abs(amount)} for {poi.name} "
            f"({transaction_type.value}). Balance: {poi.trust_account.balance:.0f}"
        )
        return tx

    # ── Decay ────────────────────────────────────────────────────

    def apply_decay(self, poi: POIRecord) -> float:
        """
        Apply natural trust decay based on time since last interaction.

        Base: 0.5 points/week
        Adjustments:
          × 0.5 if relationship > 12 months (deep relationships decay slower)
          × 2.0 if relationship < 3 months (new relationships decay fast)
          × 0.3 if recent referral (referral relationships are sticky)
          × 1.5 if competitor exposure detected
        """
        if poi.trust_account.last_interaction is None:
            return 0.0

        days_since = poi.days_since_interaction
        weeks_since = days_since / 7

        if weeks_since < 1:
            return 0.0  # No decay within first week

        rate = poi.trust_account.effective_decay_rate
        decay_amount = rate * weeks_since

        if decay_amount > 0:
            tx = TrustTransaction(
                amount=-decay_amount,
                transaction_type=TrustTransactionType.DECAY,
                reason=f"Natural decay: {weeks_since:.1f} weeks, rate {rate:.2f}/week",
                auto_detected=True,
            )
            poi.trust_account.transactions.append(tx)
            poi.trust_account.balance -= decay_amount

            self._update_trajectory(poi)
            logger.debug(
                f"Decay applied to {poi.name}: -{decay_amount:.1f}. "
                f"Balance: {poi.trust_account.balance:.0f}"
            )

        return decay_amount

    def apply_decay_all(self, pois: dict[str, POIRecord]) -> list[dict]:
        """Apply decay to all POIs and return alerts."""
        alerts = []
        for poi in pois.values():
            prev_health = poi.trust_account.health
            self.apply_decay(poi)
            new_health = poi.trust_account.health

            if prev_health != new_health and new_health in ("cooling", "at_risk", "cold"):
                alerts.append({
                    "poi_id": poi.poi_id,
                    "poi_name": poi.name,
                    "previous_health": prev_health,
                    "current_health": new_health,
                    "balance": poi.trust_account.balance,
                    "days_since_interaction": poi.days_since_interaction,
                    "action": self._suggest_action(poi, new_health),
                })

        return alerts

    def _suggest_action(self, poi: POIRecord, health: str) -> str:
        """Suggest action based on trust health."""
        if health == "cooling":
            return f"Schedule interaction with {poi.name} this week"
        elif health == "at_risk":
            return f"Prioritise contact with {poi.name} — relationship at risk"
        elif health == "cold":
            return f"Relationship with {poi.name} is functionally cold — decide: re-engage or let go"
        return "Maintain rhythm"

    # ── Trajectory ───────────────────────────────────────────────

    def _update_trajectory(self, poi: POIRecord):
        """Update trust trajectory based on recent transactions."""
        recent = [
            t for t in poi.trust_account.transactions
            if (datetime.now() - t.date).days <= 30
        ]

        if not recent:
            poi.trust_account.trajectory = "stable"
            return

        deposits = sum(t.amount for t in recent if t.amount > 0)
        withdrawals = abs(sum(t.amount for t in recent if t.amount < 0))

        if deposits > withdrawals * 1.5:
            poi.trust_account.trajectory = "rising"
        elif withdrawals > deposits * 1.5:
            poi.trust_account.trajectory = "cooling"
        else:
            poi.trust_account.trajectory = "stable"

        # Flatten warning: rising but no recent interaction
        if poi.trust_account.trajectory == "rising" and poi.days_since_interaction > 14:
            poi.trust_account.trajectory = "flatten_warning"

    # ── Tier Management ──────────────────────────────────────────

    def recalculate_tier(self, poi: POIRecord) -> POITier:
        """
        Auto-calculate tier based on trust balance and interaction frequency.
        Pinned tiers are not changed.
        """
        if poi.pinned_tier:
            return poi.tier

        balance = poi.trust_account.balance
        frequency = poi.interaction_frequency

        # Determine tier based on trust + frequency
        if balance >= 60 and frequency == "weekly":
            new_tier = POITier.INNER_CIRCLE
        elif balance >= 30 and frequency in ("weekly", "monthly"):
            new_tier = POITier.ACTIVE_NETWORK
        elif balance >= 10 and frequency in ("weekly", "monthly", "quarterly"):
            new_tier = POITier.EXTENDED_NETWORK
        else:
            new_tier = POITier.AWARENESS

        # Update trend
        if new_tier.value < poi.tier.value:  # Lower number = higher tier
            poi.tier_trend = "rising"
        elif new_tier.value > poi.tier.value:
            poi.tier_trend = "falling"
        else:
            poi.tier_trend = "stable"

        poi.tier = new_tier
        return new_tier

    # ── Trust Alerts ─────────────────────────────────────────────

    def get_trust_alerts(self, pois: dict[str, POIRecord]) -> list[dict]:
        """Get current trust alerts for the morning briefing."""
        alerts = []

        for poi in pois.values():
            health = poi.trust_account.health
            balance = poi.trust_account.balance

            if health == "cooling":
                alerts.append({
                    "poi_id": poi.poi_id,
                    "poi_name": poi.name,
                    "severity": "warning",
                    "balance": round(balance, 1),
                    "message": (
                        f"{poi.name}: Trust at {balance:.0f} (cooling). "
                        f"No interaction for {poi.days_since_interaction:.0f} days. "
                        f"Schedule contact this week."
                    ),
                })
            elif health == "at_risk":
                alerts.append({
                    "poi_id": poi.poi_id,
                    "poi_name": poi.name,
                    "severity": "urgent",
                    "balance": round(balance, 1),
                    "message": (
                        f"{poi.name}: Trust at {balance:.0f} (AT RISK). "
                        f"Prioritise immediate contact."
                    ),
                })
            elif health == "cold":
                alerts.append({
                    "poi_id": poi.poi_id,
                    "poi_name": poi.name,
                    "severity": "critical",
                    "balance": round(balance, 1),
                    "message": (
                        f"{poi.name}: Relationship is functionally cold "
                        f"(trust: {balance:.0f}). Re-engage or accept loss."
                    ),
                })

        return sorted(alerts, key=lambda a: a["balance"])

    # ── Reports ──────────────────────────────────────────────────

    def get_portfolio_summary(self, pois: dict[str, POIRecord]) -> dict:
        """Portfolio-level trust analytics."""
        tier_counts = {tier: 0 for tier in POITier}
        tier_avg_trust = {tier: [] for tier in POITier}
        total_trust_debt = 0
        cooling_count = 0

        for poi in pois.values():
            tier_counts[poi.tier] += 1
            tier_avg_trust[poi.tier].append(poi.trust_account.balance)
            if poi.trust_account.health in ("cooling", "at_risk", "cold"):
                cooling_count += 1
                if poi.trust_account.health != "healthy":
                    # Approximate trust debt as the gap to healthy
                    gap = max(0, self.HEALTHY_THRESHOLD - poi.trust_account.balance)
                    total_trust_debt += gap

        summary = {
            "tiers": {},
            "total_pois": len(pois),
            "cooling_count": cooling_count,
            "total_trust_debt": round(total_trust_debt, 1),
        }

        for tier in POITier:
            balances = tier_avg_trust[tier]
            summary["tiers"][tier.name] = {
                "count": tier_counts[tier],
                "avg_trust": round(sum(balances) / len(balances), 1) if balances else 0,
                "max_count": self.TIER_MAX_COUNTS.get(tier),
            }

        return summary
