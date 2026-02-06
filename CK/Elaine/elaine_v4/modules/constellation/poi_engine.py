"""
POI Engine v2
Auto-discovers People of Interest from email, calendar, meetings, content.
Zero-input: Mani never manually enters a contact.

Patentable: Autonomous Relationship Detection from Multi-Channel Activity

Almost Magic Tech Lab — Patentable IP
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from .models import (
    POIRecord, POITier, TierTrend, DiscoverySource,
    TrustAccount, TrustTransactionType,
)
from .trust_ledger import TrustLedger

logger = logging.getLogger("elaine.constellation.poi")


class POIEngine:
    """
    The People Discovery Engine.
    Auto-discovers and ranks people from multi-channel activity.
    """

    def __init__(self):
        self.pois: dict[str, POIRecord] = {}
        self.trust_ledger = TrustLedger()
        self._discovery_log: list[dict] = []

    # ── POI Management ───────────────────────────────────────────

    def get_or_create_poi(
        self,
        name: str,
        email: str = "",
        source: DiscoverySource = DiscoverySource.EMAIL,
        **kwargs,
    ) -> POIRecord:
        """Get existing POI by email or create new. Zero-input."""
        if email:
            for poi in self.pois.values():
                if poi.email.lower() == email.lower():
                    return poi

        name_lower = name.lower().strip()
        for poi in self.pois.values():
            if poi.name.lower().strip() == name_lower:
                return poi

        poi = POIRecord(
            name=name, email=email, discovery_source=source,
            auto_discovered=True, **kwargs,
        )
        self.pois[poi.poi_id] = poi
        self._discovery_log.append({
            "poi_id": poi.poi_id, "name": name,
            "source": source.value, "timestamp": datetime.now(),
        })
        logger.info(f"New POI discovered: {name} via {source.value}")
        return poi

    def get_poi(self, poi_id: str) -> Optional[POIRecord]:
        return self.pois.get(poi_id)

    def search_pois(
        self, query: str = "", tier: Optional[POITier] = None,
        company: str = "", min_trust: Optional[float] = None,
    ) -> list[POIRecord]:
        results = list(self.pois.values())
        if query:
            q = query.lower()
            results = [p for p in results if q in p.name.lower()
                       or q in p.company.lower() or q in p.email.lower()]
        if tier:
            results = [p for p in results if p.tier == tier]
        if company:
            results = [p for p in results if company.lower() in p.company.lower()]
        if min_trust is not None:
            results = [p for p in results if p.trust_account.balance >= min_trust]
        return sorted(results, key=lambda p: p.trust_account.balance, reverse=True)

    # ── Signal Processing ────────────────────────────────────────

    def process_email_signal(self, from_name: str, from_email: str,
                             subject: str = "", **kwargs) -> POIRecord:
        poi = self.get_or_create_poi(from_name, from_email, DiscoverySource.EMAIL)
        poi.trust_account.last_interaction = datetime.now()
        return poi

    def process_calendar_signal(self, participant_name: str,
                                participant_email: str = "",
                                was_cancelled: bool = False, **kwargs) -> POIRecord:
        poi = self.get_or_create_poi(participant_name, participant_email, DiscoverySource.CALENDAR)
        if was_cancelled:
            self.trust_ledger.withdraw(poi, TrustTransactionType.CANCELLED_MEETING,
                                        reason="Meeting cancelled")
        poi.trust_account.last_interaction = datetime.now()
        return poi

    def process_chronicle_signal(self, participant_name: str,
                                  participant_email: str = "",
                                  commitment_made: Optional[str] = None,
                                  commitment_honoured: bool = False,
                                  commitment_missed: bool = False) -> POIRecord:
        poi = self.get_or_create_poi(participant_name, participant_email, DiscoverySource.CHRONICLE)
        if commitment_honoured and commitment_made:
            self.trust_ledger.deposit(poi, TrustTransactionType.COMMITMENT_HONOURED,
                                       reason=f"Honoured: {commitment_made}")
        elif commitment_missed and commitment_made:
            self.trust_ledger.withdraw(poi, TrustTransactionType.COMMITMENT_MISSED,
                                        reason=f"Missed: {commitment_made}")
        poi.trust_account.last_interaction = datetime.now()
        return poi

    def process_content_signal(self, person_name: str, action: str = "liked",
                                content_topic: str = "") -> POIRecord:
        poi = self.get_or_create_poi(person_name, source=DiscoverySource.AMPLIFIER)
        poi.content_engagement.last_engagement = datetime.now()
        if action == "liked":
            poi.content_engagement.posts_liked += 1
        elif action == "commented":
            poi.content_engagement.posts_commented += 1
        if content_topic and content_topic not in poi.content_engagement.topics_engaged:
            poi.content_engagement.topics_engaged.append(content_topic)
        return poi

    def process_voice_agent_signal(self, visitor_name: str, visitor_email: str = "",
                                    company: str = "", notes: str = "") -> POIRecord:
        """Process lead from External Elaine voice agent."""
        poi = self.get_or_create_poi(visitor_name, visitor_email, DiscoverySource.VOICE_AGENT)
        if company:
            poi.company = company
        if notes:
            poi.notes = notes
        poi.trust_account.last_interaction = datetime.now()
        logger.info(f"Voice agent lead captured: {visitor_name} ({company})")
        return poi

    # ── Tier Recalculation ───────────────────────────────────────

    def recalculate_all_tiers(self):
        """Recalculate tiers for all POIs."""
        for poi in self.pois.values():
            self.trust_ledger.recalculate_tier(poi)

    # ── Decay Processing ─────────────────────────────────────────

    def process_weekly_decay(self) -> list[dict]:
        """Apply trust decay to all POIs and return alerts."""
        return self.trust_ledger.apply_decay_all(self.pois)

    # ── Reporting ────────────────────────────────────────────────

    def get_morning_briefing_data(self) -> dict:
        """Data for Elaine's morning briefing — trust alerts and highlights."""
        alerts = self.trust_ledger.get_trust_alerts(self.pois)
        portfolio = self.trust_ledger.get_portfolio_summary(self.pois)

        # Recent discoveries
        recent_discoveries = [
            d for d in self._discovery_log
            if (datetime.now() - d["timestamp"]).days <= 7
        ]

        # Tier 1 activity
        inner_circle = [
            p for p in self.pois.values()
            if p.tier == POITier.INNER_CIRCLE
        ]
        inner_circle_updates = []
        for p in inner_circle:
            if p.content_engagement.last_engagement:
                days = (datetime.now() - p.content_engagement.last_engagement).days
                if days <= 3:
                    inner_circle_updates.append({
                        "name": p.name,
                        "update": f"Engaged with content {days} days ago",
                    })

        return {
            "trust_alerts": alerts,
            "portfolio": portfolio,
            "recent_discoveries": len(recent_discoveries),
            "inner_circle_updates": inner_circle_updates,
        }

    def get_poi_count(self) -> dict:
        """Count POIs by tier."""
        counts = {tier: 0 for tier in POITier}
        for poi in self.pois.values():
            counts[poi.tier] += 1
        return {tier.name: count for tier, count in counts.items()}
