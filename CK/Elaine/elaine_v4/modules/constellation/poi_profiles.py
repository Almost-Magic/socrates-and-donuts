"""
POI Profiles v2
Auto-built profiles enriched from multi-channel data.
Almost Magic Tech Lab — Patentable IP
"""

import logging
from datetime import datetime
from typing import Optional

from .models import POIRecord, POITier, CommunicationIntelligence

logger = logging.getLogger("elaine.constellation.profiles")


class POIProfile:
    """
    Builds and enriches POI profiles from available data.
    Profiles are auto-built and continuously updated.
    """

    def build_profile_summary(self, poi: POIRecord) -> dict:
        """Build a complete profile summary for display or meeting prep."""
        return {
            "identity": {
                "name": poi.name,
                "title": poi.title,
                "company": poi.company,
                "location": poi.location,
                "email": poi.email,
                "linkedin": poi.linkedin,
            },
            "relationship": {
                "tier": poi.tier.name,
                "tier_trend": poi.tier_trend.value if hasattr(poi.tier_trend, 'value') else poi.tier_trend,
                "trust_balance": round(poi.trust_account.balance, 1),
                "trust_health": poi.trust_account.health,
                "trust_trajectory": poi.trust_account.trajectory,
                "days_since_interaction": round(poi.days_since_interaction, 0),
                "interaction_frequency": poi.interaction_frequency,
                "reciprocity": poi.reciprocity.value,
            },
            "intelligence": {
                "communication_style": poi.intelligence.style,
                "decision_speed": poi.intelligence.decision_speed,
                "follow_through_rate": poi.intelligence.follow_through_rate,
                "hot_buttons": poi.intelligence.hot_buttons,
                "avoids": poi.intelligence.avoids,
            },
            "professional_context": {
                "company_size": poi.company_size,
                "reports_to": poi.reports_to,
                "budget_authority": poi.budget_authority,
                "recent_moves": poi.recent_moves,
            },
            "content_engagement": {
                "posts_liked": poi.content_engagement.posts_liked,
                "posts_commented": poi.content_engagement.posts_commented,
                "topics": poi.content_engagement.topics_engaged,
                "last_engagement": poi.content_engagement.last_engagement,
            },
            "economics": {
                "direct_value": poi.economics.direct_value,
                "referral_value": poi.economics.referral_value,
                "total_rlv": poi.economics.total_rlv_expected,
                "roi_per_hour": poi.economics.roi_per_hour,
            },
            "network": {
                "known_connections": len(poi.known_connections),
                "referrals_made": len(poi.referrals_made),
                "referrals_received": len(poi.referrals_received),
            },
            "upcoming_actions": self._suggest_actions(poi),
        }

    def build_meeting_prep(self, poi: POIRecord) -> dict:
        """Build a pre-meeting intelligence brief for a POI."""
        recent_tx = [
            t for t in poi.trust_account.transactions
            if (datetime.now() - t.date).days <= 30
        ]

        return {
            "name": poi.name,
            "trust_status": f"{poi.trust_account.balance:.0f} ({poi.trust_account.health})",
            "last_interaction_days": round(poi.days_since_interaction, 0),
            "recent_trust_changes": [
                {"date": t.date.strftime("%d %b"), "amount": t.amount, "reason": t.reason}
                for t in recent_tx[-5:]
            ],
            "communication_style": poi.intelligence.style or "Unknown — observe in meeting",
            "hot_buttons": poi.intelligence.hot_buttons or ["Not yet learned"],
            "avoids": poi.intelligence.avoids or ["Not yet learned"],
            "follow_through_rate": f"{poi.intelligence.follow_through_rate:.0%}" if poi.intelligence.follow_through_rate else "No data yet",
            "open_commitments": self._get_open_commitments(poi),
            "content_they_engage_with": poi.content_engagement.topics_engaged[:5],
            "suggested_talking_points": self._suggest_talking_points(poi),
        }

    def _suggest_actions(self, poi: POIRecord) -> list[str]:
        """Suggest next actions for a POI relationship."""
        actions = []

        if poi.trust_account.health == "cooling":
            actions.append(f"Schedule interaction this week — trust is cooling")
        elif poi.trust_account.health == "at_risk":
            actions.append(f"URGENT: Reach out immediately — relationship at risk")

        if poi.days_since_interaction > 14 and poi.tier in (POITier.INNER_CIRCLE, POITier.ACTIVE_NETWORK):
            actions.append(f"No interaction for {poi.days_since_interaction:.0f} days — check in")

        if poi.content_engagement.posts_commented > 0 and poi.tier == POITier.AWARENESS:
            actions.append("Multiple content engagements — consider promoting to active network")

        if poi.reciprocity.value == "under_giving":
            actions.append("Relationship imbalanced — deliver value before asking for anything")

        if not actions:
            actions.append("Maintain current rhythm")

        return actions

    def _suggest_talking_points(self, poi: POIRecord) -> list[str]:
        """Suggest talking points for next interaction."""
        points = []

        if poi.content_engagement.topics_engaged:
            points.append(f"Topics they care about: {', '.join(poi.content_engagement.topics_engaged[:3])}")

        if poi.intelligence.hot_buttons:
            points.append(f"Hot buttons: {', '.join(poi.intelligence.hot_buttons[:3])}")

        if poi.recent_moves:
            points.append(f"Recent career move: {poi.recent_moves[-1]}")

        if not points:
            points.append("First conversation — focus on discovery and listening")

        return points

    def _get_open_commitments(self, poi: POIRecord) -> list[str]:
        """Get any open commitments related to this POI."""
        # Placeholder — would be populated from Chronicle integration
        return []

    def enrich_from_email_patterns(self, poi: POIRecord, avg_response_hours: float,
                                    tone_formality: float):
        """Enrich POI profile from email pattern analysis."""
        if avg_response_hours < 2:
            poi.intelligence.decision_speed = "fast"
        elif avg_response_hours < 24:
            poi.intelligence.decision_speed = "moderate"
        else:
            poi.intelligence.decision_speed = "slow"

        if tone_formality > 0.7:
            poi.intelligence.style = "formal"
        elif tone_formality < 0.3:
            poi.intelligence.style = "casual"
        else:
            poi.intelligence.style = "professional"

    def enrich_from_meeting_patterns(self, poi: POIRecord,
                                      commitments_made: int,
                                      commitments_honoured: int):
        """Enrich POI profile from meeting commitment patterns."""
        if commitments_made > 0:
            poi.intelligence.follow_through_rate = commitments_honoured / commitments_made
