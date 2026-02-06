"""
Reciprocity Engine v2
Tracks give/take balance across relationships.
Alerts when imbalanced — before it becomes a problem.

Patentable: Relationship Balance Monitoring with Proactive Value Delivery

Almost Magic Tech Lab — Patentable IP
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from .models import (
    POIRecord, POITier, ReciprocityBalance,
    TrustTransactionType,
)

logger = logging.getLogger("elaine.constellation.reciprocity")


class ReciprocityEngine:
    """
    Monitors give/take balance in relationships.
    Healthy relationships have roughly balanced reciprocity.
    """

    # Transaction classification
    GIVE_TYPES = {
        TrustTransactionType.PROACTIVE_VALUE,
        TrustTransactionType.REFERRAL_MADE,
        TrustTransactionType.COMMITMENT_HONOURED,
        TrustTransactionType.COMMITMENT_EARLY,
        TrustTransactionType.INTEGRITY_SIGNAL,
    }

    TAKE_TYPES = {
        TrustTransactionType.REFERRAL_RECEIVED,
    }

    def analyse_reciprocity(self, poi: POIRecord, lookback_days: int = 90) -> dict:
        """
        Analyse the give/take balance for a POI relationship.
        """
        cutoff = datetime.now() - timedelta(days=lookback_days)
        recent = [
            t for t in poi.trust_account.transactions
            if t.date > cutoff and t.transaction_type != TrustTransactionType.DECAY
        ]

        give_count = sum(1 for t in recent if t.transaction_type in self.GIVE_TYPES)
        take_count = sum(1 for t in recent if t.transaction_type in self.TAKE_TYPES)
        give_value = sum(abs(t.amount) for t in recent if t.transaction_type in self.GIVE_TYPES)
        take_value = sum(abs(t.amount) for t in recent if t.transaction_type in self.TAKE_TYPES)

        # Determine balance
        total = give_count + take_count
        if total == 0:
            balance = ReciprocityBalance.UNKNOWN
        elif give_count > take_count * 2:
            balance = ReciprocityBalance.OVER_GIVING
        elif take_count > give_count * 2:
            balance = ReciprocityBalance.UNDER_GIVING
        else:
            balance = ReciprocityBalance.BALANCED

        poi.reciprocity = balance

        return {
            "poi_name": poi.name,
            "balance": balance.value,
            "give_count": give_count,
            "take_count": take_count,
            "give_value": give_value,
            "take_value": take_value,
            "recommendation": self._recommend(poi, balance),
        }

    def _recommend(self, poi: POIRecord, balance: ReciprocityBalance) -> str:
        if balance == ReciprocityBalance.OVER_GIVING:
            return (
                f"You've been giving more than receiving with {poi.name}. "
                f"This is fine for new relationships, but consider whether "
                f"there's value you could ask for (intro, feedback, referral)."
            )
        elif balance == ReciprocityBalance.UNDER_GIVING:
            return (
                f"You've received more than given to {poi.name}. "
                f"Send value before your next ask — share an article, "
                f"make an introduction, or offer help unprompted."
            )
        elif balance == ReciprocityBalance.BALANCED:
            return f"Healthy balance with {poi.name}. Maintain rhythm."
        return f"Not enough data on {poi.name} yet."

    def analyse_all(self, pois: dict[str, POIRecord]) -> dict:
        """Analyse reciprocity across all active POIs."""
        results = {
            "balanced": [],
            "over_giving": [],
            "under_giving": [],
            "unknown": [],
        }

        for poi in pois.values():
            if poi.tier.value > 3:  # Skip awareness tier
                continue
            analysis = self.analyse_reciprocity(poi)
            results[analysis["balance"]].append({
                "name": poi.name,
                "tier": poi.tier.name,
                "give_count": analysis["give_count"],
                "take_count": analysis["take_count"],
            })

        # Summary
        total = sum(len(v) for v in results.values())
        return {
            "total_analysed": total,
            "balanced_count": len(results["balanced"]),
            "over_giving_count": len(results["over_giving"]),
            "under_giving_count": len(results["under_giving"]),
            "details": results,
            "action_items": self._build_action_items(results),
        }

    def _build_action_items(self, results: dict) -> list[str]:
        actions = []
        for entry in results.get("under_giving", [])[:3]:
            actions.append(
                f"Deliver value to {entry['name']} before next ask"
            )
        for entry in results.get("over_giving", [])[:2]:
            actions.append(
                f"Consider asking {entry['name']} for an intro or referral"
            )
        return actions
