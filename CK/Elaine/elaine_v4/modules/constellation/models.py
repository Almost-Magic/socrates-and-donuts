"""
Constellation v2 — Data Models
Defines POI records, trust accounts, tiers, and relationship economics.
Almost Magic Tech Lab — Patentable IP
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


# ── Enums ──────────────────────────────────────────────────────────

class POITier(Enum):
    INNER_CIRCLE = 1     # Trust > 60, interaction > weekly, max 15
    ACTIVE_NETWORK = 2   # Trust 30-60, interaction > monthly, max 50
    EXTENDED_NETWORK = 3  # Trust 10-30, interaction > quarterly, max 200
    AWARENESS = 4         # Trust < 10 or new, unlimited


class TierTrend(Enum):
    RISING = "rising"
    STABLE = "stable"
    FALLING = "falling"


class TrustTransactionType(Enum):
    # Deposits
    COMMITMENT_HONOURED = "commitment_honoured"
    COMMITMENT_EARLY = "commitment_early"
    PROACTIVE_VALUE = "proactive_value"
    INTEGRITY_SIGNAL = "integrity_signal"
    REFERRAL_MADE = "referral_made"
    REFERRAL_RECEIVED = "referral_received"

    # Withdrawals
    COMMITMENT_MISSED = "commitment_missed"
    COMMITMENT_LATE = "commitment_late"
    SLOW_RESPONSE = "slow_response"
    CANCELLED_MEETING = "cancelled_meeting"
    GENERIC_COMMUNICATION = "generic_communication"

    # Their actions
    THEIR_FOLLOW_THROUGH_FAILURE = "their_follow_through_failure"

    # System
    DECAY = "decay"
    MANUAL_ADJUSTMENT = "manual_adjustment"


class ReciprocityBalance(Enum):
    BALANCED = "balanced"         # give ≈ take
    OVER_GIVING = "over_giving"   # Mani gives more than receives
    UNDER_GIVING = "under_giving"  # Mani takes more than gives
    UNKNOWN = "unknown"


class DiscoverySource(Enum):
    EMAIL = "email"
    CALENDAR = "calendar"
    LINKEDIN = "linkedin"
    CHRONICLE = "chronicle"
    AMPLIFIER = "amplifier"
    CARTOGRAPHER = "cartographer"
    MANUAL = "manual"
    VOICE_AGENT = "voice_agent"  # External Elaine


# ── Trust Transaction ──────────────────────────────────────────────

@dataclass
class TrustTransaction:
    """A single deposit or withdrawal from a trust account."""
    id: str = field(default_factory=lambda: f"tx_{uuid.uuid4().hex[:8]}")
    date: datetime = field(default_factory=datetime.now)
    amount: float = 0.0
    transaction_type: TrustTransactionType = TrustTransactionType.MANUAL_ADJUSTMENT
    reason: str = ""
    source: DiscoverySource = DiscoverySource.MANUAL
    auto_detected: bool = False
    context: str = ""  # Additional context for the transaction


# ── Default transaction amounts ────────────────────────────────────

TRUST_DEFAULTS = {
    TrustTransactionType.COMMITMENT_HONOURED: 10,
    TrustTransactionType.COMMITMENT_EARLY: 12,
    TrustTransactionType.PROACTIVE_VALUE: 8,
    TrustTransactionType.INTEGRITY_SIGNAL: 15,
    TrustTransactionType.REFERRAL_MADE: 15,
    TrustTransactionType.REFERRAL_RECEIVED: 20,
    TrustTransactionType.COMMITMENT_MISSED: -20,
    TrustTransactionType.COMMITMENT_LATE: -8,
    TrustTransactionType.SLOW_RESPONSE: -5,
    TrustTransactionType.CANCELLED_MEETING: -5,
    TrustTransactionType.GENERIC_COMMUNICATION: -3,
    TrustTransactionType.THEIR_FOLLOW_THROUGH_FAILURE: -10,
}


# ── Trust Account ──────────────────────────────────────────────────

@dataclass
class TrustAccount:
    """Running trust balance per person."""
    balance: float = 0.0
    transactions: list[TrustTransaction] = field(default_factory=list)
    last_interaction: Optional[datetime] = None
    trajectory: str = "new"  # rising, stable, cooling, flatten_warning, new

    # Decay model parameters
    decay_rate: float = 0.5  # Base: 0.5 points/week
    relationship_age_months: float = 0.0

    @property
    def health(self) -> str:
        """Trust health based on balance."""
        if self.balance > 30:
            return "healthy"
        elif self.balance > 15:
            return "cooling"
        elif self.balance > 5:
            return "at_risk"
        else:
            return "cold"

    @property
    def effective_decay_rate(self) -> float:
        """Adjusted decay rate based on relationship age and context."""
        rate = self.decay_rate

        # Deep relationships decay slower
        if self.relationship_age_months > 12:
            rate *= 0.5
        # New relationships decay fast
        elif self.relationship_age_months < 3:
            rate *= 2.0

        # Recent referral makes relationship sticky
        recent_referrals = [
            t for t in self.transactions
            if t.transaction_type in (
                TrustTransactionType.REFERRAL_MADE,
                TrustTransactionType.REFERRAL_RECEIVED,
            )
            and (datetime.now() - t.date).days <= 90
        ]
        if recent_referrals:
            rate *= 0.3

        return rate


# ── Communication Intelligence ─────────────────────────────────────

@dataclass
class CommunicationIntelligence:
    """Learned communication preferences for a POI."""
    style: str = ""          # direct_data_driven, narrative, formal, casual
    decision_speed: str = ""  # fast, moderate, slow
    follow_through_rate: float = 0.0
    hot_buttons: list[str] = field(default_factory=list)
    avoids: list[str] = field(default_factory=list)
    preferred_channel: str = ""  # email, phone, linkedin, in_person


@dataclass
class ContentEngagement:
    """How a POI engages with Mani's content."""
    posts_liked: int = 0
    posts_commented: int = 0
    topics_engaged: list[str] = field(default_factory=list)
    last_engagement: Optional[datetime] = None


# ── Relationship Economics ─────────────────────────────────────────

@dataclass
class RelationshipEconomics:
    """Lifetime relationship value calculation."""
    direct_value: float = 0.0
    referral_value: float = 0.0
    network_value: float = 0.0
    reputation_value: float = 0.0

    investment_hours_monthly: float = 0.0

    @property
    def total_rlv_expected(self) -> float:
        """Total Relationship Lifetime Value (expected)."""
        return self.direct_value + self.referral_value + self.network_value

    @property
    def total_rlv_optimistic(self) -> float:
        """Optimistic RLV including reputation value."""
        return self.total_rlv_expected + self.reputation_value

    @property
    def roi_per_hour(self) -> float:
        """ROI per hour invested in this relationship."""
        if self.investment_hours_monthly <= 0:
            return 0.0
        annual_investment = self.investment_hours_monthly * 12
        return round(self.total_rlv_expected / annual_investment, 2) if annual_investment else 0.0


# ── Network Connection ─────────────────────────────────────────────

@dataclass
class NetworkConnection:
    """A known connection of a POI."""
    poi_id: str = ""
    name: str = ""
    relationship_to_poi: str = ""  # colleague, client, mentor, etc
    warm_intro_probability: float = 0.5
    estimated_value: float = 0.0
    notes: str = ""


# ── The POI Record ─────────────────────────────────────────────────

@dataclass
class POIRecord:
    """
    Person of Interest — the core entity in the Constellation.
    Auto-discovered, auto-enriched, trust-tracked.
    """
    poi_id: str = field(default_factory=lambda: f"poi_{uuid.uuid4().hex[:8]}")

    # Identity
    name: str = ""
    title: str = ""
    company: str = ""
    email: str = ""
    linkedin: str = ""
    location: str = ""
    phone: str = ""

    # Relationship
    tier: POITier = POITier.AWARENESS
    tier_trend: TierTrend = TierTrend.STABLE
    trust_account: TrustAccount = field(default_factory=TrustAccount)
    reciprocity: ReciprocityBalance = ReciprocityBalance.UNKNOWN

    # Intelligence
    intelligence: CommunicationIntelligence = field(default_factory=CommunicationIntelligence)
    content_engagement: ContentEngagement = field(default_factory=ContentEngagement)
    economics: RelationshipEconomics = field(default_factory=RelationshipEconomics)

    # Network
    known_connections: list[NetworkConnection] = field(default_factory=list)
    referrals_made: list[str] = field(default_factory=list)  # POI IDs
    referrals_received: list[str] = field(default_factory=list)

    # Professional context
    company_size: Optional[int] = None
    reports_to: str = ""
    budget_authority: str = ""
    recent_moves: list[str] = field(default_factory=list)

    # Discovery
    auto_discovered: bool = True
    discovery_source: DiscoverySource = DiscoverySource.EMAIL
    discovered_at: datetime = field(default_factory=datetime.now)

    # Metadata
    tags: list[str] = field(default_factory=list)
    notes: str = ""
    pinned_tier: bool = False  # Mani manually set this tier

    @property
    def days_since_interaction(self) -> float:
        if not self.trust_account.last_interaction:
            return (datetime.now() - self.discovered_at).days
        return (datetime.now() - self.trust_account.last_interaction).days

    @property
    def interaction_frequency(self) -> str:
        """Estimated interaction frequency."""
        days = self.days_since_interaction
        if days <= 7:
            return "weekly"
        elif days <= 30:
            return "monthly"
        elif days <= 90:
            return "quarterly"
        return "rare"
