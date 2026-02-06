"""
Network Intelligence v2
Second-order relationship intelligence: infers opportunities through POI connections.

Patentable: Second-Order Network Intelligence with Warm Intro Probability

Almost Magic Tech Lab — Patentable IP
"""

import logging
from dataclasses import dataclass, field
from typing import Optional

from .models import POIRecord, POITier, NetworkConnection

logger = logging.getLogger("elaine.constellation.network")


@dataclass
class NetworkOpportunity:
    """A detected opportunity through a POI's network."""
    source_poi_id: str
    source_poi_name: str
    target_name: str
    target_company: str = ""
    relationship: str = ""  # How they know each other
    warm_intro_probability: float = 0.5
    estimated_value: float = 0.0
    rationale: str = ""
    action: str = ""
    prerequisites: list[str] = field(default_factory=list)


@dataclass
class NetworkRisk:
    """Risk assessment if a POI relationship goes bad."""
    poi_id: str
    poi_name: str
    trust_at_stake: float = 0.0
    connected_relationships_at_risk: int = 0
    pipeline_impact: float = 0.0
    network_impact_description: str = ""


class NetworkIntelligence:
    """
    Analyses second-order relationships: who knows whom, what opportunities
    exist through existing connections, and what's at risk if relationships fail.
    """

    def __init__(self):
        pass

    def find_opportunities(self, pois: dict[str, POIRecord]) -> list[NetworkOpportunity]:
        """
        Detect warm introduction opportunities through existing POI connections.
        """
        opportunities = []

        for poi in pois.values():
            if poi.tier not in (POITier.INNER_CIRCLE, POITier.ACTIVE_NETWORK):
                continue  # Only leverage strong relationships

            if poi.trust_account.health in ("at_risk", "cold"):
                continue  # Don't ask favours from cooling relationships

            for connection in poi.known_connections:
                # Check if connection is already a POI
                existing = self._find_poi_by_name(pois, connection.name)
                if existing and existing.tier.value <= 2:
                    continue  # Already an active relationship

                if connection.estimated_value > 5000:
                    # Calculate warm intro probability
                    probability = self._calculate_intro_probability(poi, connection)

                    opportunities.append(NetworkOpportunity(
                        source_poi_id=poi.poi_id,
                        source_poi_name=poi.name,
                        target_name=connection.name,
                        target_company=connection.relationship_to_poi,
                        relationship=connection.relationship_to_poi,
                        warm_intro_probability=probability,
                        estimated_value=connection.estimated_value,
                        rationale=f"Known connection of {poi.name}",
                        action=self._suggest_intro_action(poi, connection, probability),
                        prerequisites=self._get_prerequisites(poi),
                    ))

        return sorted(opportunities, key=lambda o: o.estimated_value * o.warm_intro_probability, reverse=True)

    def _calculate_intro_probability(self, poi: POIRecord, connection: NetworkConnection) -> float:
        """Estimate probability that POI will make an introduction."""
        base = 0.5

        # Strong trust = more likely to introduce
        if poi.trust_account.balance > 60:
            base += 0.2
        elif poi.trust_account.balance > 40:
            base += 0.1

        # Has already made referrals = referral-friendly
        if poi.referrals_made:
            base += 0.15

        # Reciprocity: if they owe us, more likely
        if poi.reciprocity.value == "over_giving":
            base += 0.1

        return min(base, 0.95)

    def _suggest_intro_action(self, poi: POIRecord, connection: NetworkConnection,
                               probability: float) -> str:
        if probability > 0.7:
            return f"Ask {poi.name} for introduction to {connection.name}"
        elif probability > 0.4:
            return f"Build more trust with {poi.name} first, then request intro"
        return f"Long-term: cultivate {poi.name} relationship before asking"

    def _get_prerequisites(self, poi: POIRecord) -> list[str]:
        prereqs = []
        if poi.trust_account.health != "healthy":
            prereqs.append(f"Restore trust with {poi.name} first")
        if poi.reciprocity.value == "under_giving":
            prereqs.append(f"Deliver value to {poi.name} before asking for intro")
        return prereqs

    def _find_poi_by_name(self, pois: dict[str, POIRecord], name: str) -> Optional[POIRecord]:
        name_lower = name.lower().strip()
        for poi in pois.values():
            if poi.name.lower().strip() == name_lower:
                return poi
        return None

    # ── Network Risk Analysis ────────────────────────────────────

    def assess_network_risk(self, poi: POIRecord, all_pois: dict[str, POIRecord]) -> NetworkRisk:
        """
        What happens to the network if this POI relationship goes bad?
        """
        # Find POIs connected through this person
        connected = []
        for other_poi in all_pois.values():
            if other_poi.poi_id == poi.poi_id:
                continue
            # Check if they were referred by this POI
            if poi.poi_id in other_poi.referrals_received:
                connected.append(other_poi)

        # Calculate pipeline impact
        pipeline_impact = sum(
            p.economics.direct_value for p in connected
        ) + poi.economics.direct_value

        description = ""
        if connected:
            names = [p.name for p in connected[:3]]
            description = (
                f"If relationship with {poi.name} fails: "
                f"{len(connected)} connected relationships at risk "
                f"({', '.join(names)}). "
                f"Pipeline impact: ${pipeline_impact:,.0f}"
            )
        else:
            description = f"Direct impact only: ${poi.economics.direct_value:,.0f}"

        return NetworkRisk(
            poi_id=poi.poi_id,
            poi_name=poi.name,
            trust_at_stake=poi.trust_account.balance,
            connected_relationships_at_risk=len(connected),
            pipeline_impact=pipeline_impact,
            network_impact_description=description,
        )

    # ── Portfolio Analytics ──────────────────────────────────────

    def analyse_portfolio(self, pois: dict[str, POIRecord]) -> dict:
        """
        Relationship portfolio analysis: concentration, gaps, health.
        """
        if not pois:
            return {"status": "No POIs yet"}

        active = [p for p in pois.values() if p.tier.value <= 3]

        # Concentration risk: revenue from top N clients
        by_value = sorted(active, key=lambda p: p.economics.direct_value, reverse=True)
        total_value = sum(p.economics.direct_value for p in active) or 1

        top_3_value = sum(p.economics.direct_value for p in by_value[:3])
        concentration_pct = round(top_3_value / total_value * 100, 1)

        # Relationship gaps
        gaps = []
        industries = set(p.tags for p in active if p.tags)
        tier_1_count = len([p for p in active if p.tier == POITier.INNER_CIRCLE])

        if tier_1_count < 5:
            gaps.append("Inner circle is thin — invest in deepening Tier 2 relationships")
        if concentration_pct > 60:
            gaps.append(f"Revenue concentration: {concentration_pct}% from top 3. Diversify.")

        # Referral health
        referrers = [p for p in active if p.referrals_made]
        if len(referrers) < 2:
            gaps.append("Few active referrers — cultivate referral relationships")

        return {
            "total_active": len(active),
            "concentration_pct": concentration_pct,
            "top_3_by_value": [{"name": p.name, "value": p.economics.direct_value} for p in by_value[:3]],
            "gaps": gaps,
            "referrer_count": len(referrers),
            "avg_trust_tier1": round(
                sum(p.trust_account.balance for p in active if p.tier == POITier.INNER_CIRCLE)
                / max(tier_1_count, 1), 1
            ),
        }
