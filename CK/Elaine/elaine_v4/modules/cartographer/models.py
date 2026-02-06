"""
Cartographer v2 — Data Models
Governed Intelligence & Discovery System

Almost Magic Tech Lab — Patentable IP
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


# ── Enums ────────────────────────────────────────────────────────

class DepthLevel(str, Enum):
    DEEP = "deep"             # Score > 80
    GROWING = "growing"       # 50-80
    SURFACE = "surface"       # 25-50
    PERIPHERAL = "peripheral" # 10-25
    UNEXPLORED = "unexplored" # < 10


class DiscoveryLayer(str, Enum):
    SIGNAL = "signal"       # Act on today
    PATTERN = "pattern"     # Emerging trend (3+ signals)
    HORIZON = "horizon"     # 6-24 months out
    FORECAST = "forecast"   # Predicted developments


class ActionabilityLevel(str, Enum):
    ARCHIVE = "archive"   # Below threshold — logged but not surfaced
    INFORM = "inform"     # Know this exists, no action now
    PREPARE = "prepare"   # Action needed within 30 days
    ACT = "act"           # Action needed within 7 days
    URGENT = "urgent"     # Immediate business impact


class CognitivePhase(str, Enum):
    CRISIS = "crisis"       # 3+ Red Giants — signal only, 3 items max
    EXECUTION = "execution" # Major deliverable — budget 50%, no horizon
    PLANNING = "planning"   # OKR/strategy — full budget, horizon boosted
    RECOVERY = "recovery"   # Low gravity — full exploration
    LEARNING = "learning"   # Explicit exploration — no limits


class SourceTier(int, Enum):
    PRIMARY = 1       # Government, ISO, NIST — base 0.90
    AUTHORITATIVE = 2 # Reuters, journals, major law firms — 0.80
    EXPERT = 3        # Named analysts — 0.70
    INDUSTRY = 4      # Blogs, vendor reports — 0.55
    COMMUNITY = 5     # Reddit, forums, social — 0.30
    AI_GENERATED = 6  # Unverified AI content — 0.10


class InteractionType(str, Enum):
    READ = "read"           # Opened, spent 30+ seconds
    SAVED = "saved"         # Bookmarked
    ACTED_ON = "acted_on"   # Created gravity item, wrote content, contacted client
    SHARED = "shared"       # Sent to someone, posted
    DISMISSED = "dismissed" # Explicitly rejected
    IGNORED = "ignored"     # Never opened after 48 hours


class MissionType(str, Enum):
    RECONNAISSANCE = "reconnaissance"     # Quick scan of new territory
    DEEP_DIVE = "deep_dive"              # Comprehensive analysis
    ADJACENT_WATCH = "adjacent_watch"     # Monitor near expertise
    COMPETITOR_INTEL = "competitor_intel"  # Track competitive landscape
    CLIENT_HORIZON = "client_horizon"     # What's coming for clients
    BLIND_SPOT_PROBE = "blind_spot_probe" # Explore what you're NOT looking at
    WEAK_SIGNAL_SCAN = "weak_signal_scan" # Detect embryonic topics
    NEGATIVE_SPACE_MAP = "negative_space_map"  # What's conspicuously absent


class TerritoryTrend(str, Enum):
    EXPANDING = "expanding"
    STABLE = "stable"
    CONTRACTING = "contracting"
    STALE = "stale"


SOURCE_BASE_CREDIBILITY = {
    SourceTier.PRIMARY: 0.90,
    SourceTier.AUTHORITATIVE: 0.80,
    SourceTier.EXPERT: 0.70,
    SourceTier.INDUSTRY: 0.55,
    SourceTier.COMMUNITY: 0.30,
    SourceTier.AI_GENERATED: 0.10,
}

INTERACTION_WEIGHTS = {
    InteractionType.READ: 0.2,
    InteractionType.SAVED: 0.6,
    InteractionType.ACTED_ON: 1.0,
    InteractionType.SHARED: 0.7,
    InteractionType.DISMISSED: -0.4,
    InteractionType.IGNORED: -0.1,
}

DEPTH_THRESHOLDS = {
    DepthLevel.DEEP: 80,
    DepthLevel.GROWING: 50,
    DepthLevel.SURFACE: 25,
    DepthLevel.PERIPHERAL: 10,
    DepthLevel.UNEXPLORED: 0,
}

# ── Data Models ──────────────────────────────────────────────────

@dataclass
class DepthSignals:
    """Multi-signal analysis for knowledge depth calculation."""
    credentials: float = 0.0      # 25% weight — certs, degrees, formal training
    content_production: float = 0.0  # 25% — articles, posts, proposals
    time_investment: float = 0.0  # 20% — hours in meetings, research
    query_complexity: float = 0.0 # 15% — basic vs advanced questions
    teaching_evidence: float = 0.0  # 10% — explains to others
    peer_recognition: float = 0.0 # 5% — citations, mentions, speaking invites

    @property
    def score(self) -> float:
        return (
            self.credentials * 0.25
            + self.content_production * 0.25
            + self.time_investment * 0.20
            + self.query_complexity * 0.15
            + self.teaching_evidence * 0.10
            + self.peer_recognition * 0.05
        )

    @property
    def depth_level(self) -> DepthLevel:
        s = self.score
        if s > 80:
            return DepthLevel.DEEP
        elif s > 50:
            return DepthLevel.GROWING
        elif s > 25:
            return DepthLevel.SURFACE
        elif s > 10:
            return DepthLevel.PERIPHERAL
        return DepthLevel.UNEXPLORED


@dataclass
class KnowledgeTerritory:
    """A node in Mani's knowledge territory map."""
    territory_id: str
    label: str
    depth_signals: DepthSignals = field(default_factory=DepthSignals)
    decay_rate_per_quarter: float = 0.05  # 5% default, 2% for credentialed
    last_engagement: Optional[datetime] = None
    adjacent_territories: list[str] = field(default_factory=list)
    negative_spaces: list[str] = field(default_factory=list)
    discovery_count_30d: int = 0
    action_rate_30d: float = 0.0
    knowledge_debt_hours: float = 0.0
    knowledge_debt_description: str = ""
    knowledge_debt_roi: str = ""
    trend: TerritoryTrend = TerritoryTrend.STABLE
    predictive_signals: dict = field(default_factory=dict)

    @property
    def depth(self) -> DepthLevel:
        return self.depth_signals.depth_level

    @property
    def depth_score(self) -> float:
        return self.depth_signals.score


@dataclass
class Source:
    """An intelligence source with dynamic credibility."""
    source_id: str
    name: str
    url: str = ""
    source_type: str = "rss"  # rss, api, social, alert, manual
    base_tier: SourceTier = SourceTier.INDUSTRY
    credibility_adjustments: list[dict] = field(default_factory=list)
    domains: list[str] = field(default_factory=list)
    geographic_focus: str = ""
    engagement_rate: float = 0.0
    action_rate: float = 0.0
    early_detection_count: int = 0
    false_report_count: int = 0
    last_scanned: Optional[datetime] = None

    @property
    def current_credibility(self) -> float:
        base = SOURCE_BASE_CREDIBILITY.get(self.base_tier, 0.50)
        adj = sum(a.get("delta", 0) for a in self.credibility_adjustments)
        return max(0.05, min(0.99, base + adj))


@dataclass
class Propagation:
    """Actions triggered in other Elaine modules by a discovery."""
    gravity_item_created: str = ""
    amplifier_content_suggested: str = ""
    sentinel_staleness_check: list[str] = field(default_factory=list)
    trust_ledger_alert: str = ""
    poi_engagement_opportunity: str = ""


@dataclass
class Discovery:
    """A single intelligence discovery."""
    discovery_id: str = ""
    title: str = ""
    summary: str = ""
    so_what: str = ""          # Business impact for Mani
    source_name: str = ""
    source_credibility: float = 0.5
    convergence_sources: list[str] = field(default_factory=list)
    convergence_confidence: float = 0.0
    layer: DiscoveryLayer = DiscoveryLayer.SIGNAL
    actionability: ActionabilityLevel = ActionabilityLevel.INFORM
    territory: str = ""
    adjacency_from: str = ""
    is_negative_space: bool = False
    relevance_score: float = 0.0
    action_suggested: str = ""
    propagation: Propagation = field(default_factory=Propagation)
    interaction: Optional[InteractionType] = None
    interaction_timestamp: Optional[datetime] = None
    pattern_membership: list[str] = field(default_factory=list)
    decay_half_life_days: int = 60
    decayed: bool = False
    budget_cost: int = 1
    discovered_at: datetime = field(default_factory=datetime.now)
    related_discoveries: list[str] = field(default_factory=list)


@dataclass
class Pattern:
    """An emerging pattern detected from multiple discoveries."""
    pattern_id: str
    label: str
    description: str = ""
    discovery_ids: list[str] = field(default_factory=list)
    signal_count: int = 0
    confidence: float = 0.0
    first_detected: datetime = field(default_factory=datetime.now)
    predicted_mainstream: str = ""  # e.g. "Q3 2026"
    action_recommended: str = ""
    territory: str = ""


@dataclass
class CognitiveBudget:
    """Daily discovery budget with phase-aware adjustments."""
    signal_max: int = 5
    pattern_max_per_week: int = 2
    horizon_max_per_week: int = 1
    serendipity_max_per_week: int = 1
    contrarian_max_per_week: int = 1
    current_phase: CognitivePhase = CognitivePhase.RECOVERY

    # Today's usage
    signal_used: int = 0
    pattern_used_this_week: int = 0
    horizon_used_this_week: int = 0

    @property
    def effective_signal_max(self) -> int:
        if self.current_phase == CognitivePhase.CRISIS:
            return 3
        elif self.current_phase == CognitivePhase.EXECUTION:
            return max(2, self.signal_max // 2)
        return self.signal_max

    @property
    def horizon_suppressed(self) -> bool:
        return self.current_phase in (CognitivePhase.CRISIS, CognitivePhase.EXECUTION)

    @property
    def serendipity_suppressed(self) -> bool:
        return self.current_phase in (CognitivePhase.CRISIS, CognitivePhase.EXECUTION)

    def can_deliver(self, layer: DiscoveryLayer) -> bool:
        if layer == DiscoveryLayer.SIGNAL:
            return self.signal_used < self.effective_signal_max
        elif layer == DiscoveryLayer.PATTERN:
            return self.pattern_used_this_week < self.pattern_max_per_week
        elif layer == DiscoveryLayer.HORIZON:
            return not self.horizon_suppressed and self.horizon_used_this_week < self.horizon_max_per_week
        elif layer == DiscoveryLayer.FORECAST:
            return not self.horizon_suppressed
        return True

    def consume(self, layer: DiscoveryLayer):
        if layer == DiscoveryLayer.SIGNAL:
            self.signal_used += 1
        elif layer == DiscoveryLayer.PATTERN:
            self.pattern_used_this_week += 1
        elif layer in (DiscoveryLayer.HORIZON, DiscoveryLayer.FORECAST):
            self.horizon_used_this_week += 1


@dataclass
class CounterfactualGap:
    """A discovery Mani found elsewhere that the Cartographer missed."""
    gap_id: str
    title: str
    where_found: str  # "Hacker News", "James Chen shared", etc.
    root_causes: list[str] = field(default_factory=list)
    corrections_applied: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class NewsCategory:
    """A configurable news category."""
    category_id: str
    label: str
    enabled: bool = True
    auto_detected: bool = False
    keywords: list[str] = field(default_factory=list)


@dataclass
class IntelligenceCalendarSlot:
    """A day in the intelligence calendar."""
    day_of_week: int  # 0=Monday ... 6=Sunday
    mission_type: str = ""
    description: str = ""
    engagement_rate: float = 0.0
    learned: bool = False
