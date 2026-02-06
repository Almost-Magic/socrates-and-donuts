"""
Sentinel v2 — Data Models
Quality Governance & Trust Intelligence Engine

Nine Trust Dimensions, Risk Economics, Audience-Aware Scoring,
Position Integrity Graph, Multi-Perspective Review Council.

Almost Magic Tech Lab — Patentable IP
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


# ── Enums ────────────────────────────────────────────────────────

class GovernanceProfile(str, Enum):
    INTERNAL = "internal"            # Notes, drafts, chat
    SOCIAL_CONTENT = "social_content"  # LinkedIn, newsletter, blog
    CLIENT_COMMUNICATION = "client_communication"  # Emails, reports
    SALES_MATERIALS = "sales_materials"  # Proposals, pricing, decks
    REGULATED_OUTPUT = "regulated_output"  # ISO reports, compliance docs
    PUBLIC_STATEMENT = "public_statement"  # Press, media, conferences


class StrategicIntent(str, Enum):
    CLOSE_DEAL = "close_deal"
    BUILD_RELATIONSHIP = "build_relationship"
    DE_ESCALATE = "de_escalate"
    ASSERT_AUTHORITY = "assert_authority"
    THOUGHT_LEADERSHIP = "thought_leadership"
    INTERNAL_COMMS = "internal"


class RiskSeverity(str, Enum):
    CRITICAL = "critical"         # >$50K exposure or regulatory breach
    HIGH = "high"                 # $10K-$50K
    MODERATE = "moderate"         # $1K-$10K
    LOW = "low"                   # <$1K
    POSITIVE_RISK = "positive"    # Upside > 4× downside


class AuditVerdict(str, Enum):
    CLEAN = "clean"                     # No issues
    READY_WITH_CHANGES = "ready_with_changes"  # Minor fixes
    HOLD = "hold"                       # Significant issues
    BLOCKED = "blocked"                 # Critical — cannot send
    EXCEPTION_GRANTED = "exception_granted"  # Rule broken intentionally


class OverrideOutcome(str, Enum):
    CORRECT = "correct"       # Mani was right to override
    NEUTRAL = "neutral"       # No measurable impact
    INCORRECT = "incorrect"   # Override led to negative outcome


class ResilienceLevel(str, Enum):
    HIGH = "high"         # Will age well — principles, stable facts
    MODERATE = "moderate"  # Needs date-stamping or hedging
    LOW = "low"           # Will age badly — volatile data, model names


# ── Intent-Based Dimension Weights ───────────────────────────────

INTENT_WEIGHTS = {
    StrategicIntent.CLOSE_DEAL: {
        "accuracy": 0.95, "consistency": 0.85, "completeness": 0.90,
        "professionalism": 0.85, "voice_match": 0.70, "compliance": 0.90,
        "timeliness": 0.80, "audience_fit": 0.85, "resilience": 0.70,
    },
    StrategicIntent.BUILD_RELATIONSHIP: {
        "accuracy": 0.70, "consistency": 0.75, "completeness": 0.60,
        "professionalism": 0.75, "voice_match": 0.90, "compliance": 0.60,
        "timeliness": 0.70, "audience_fit": 0.85, "resilience": 0.50,
    },
    StrategicIntent.DE_ESCALATE: {
        "accuracy": 0.80, "consistency": 0.80, "completeness": 0.70,
        "professionalism": 0.85, "voice_match": 0.80, "compliance": 0.70,
        "timeliness": 0.60, "audience_fit": 0.95, "resilience": 0.50,
    },
    StrategicIntent.ASSERT_AUTHORITY: {
        "accuracy": 0.95, "consistency": 0.90, "completeness": 0.85,
        "professionalism": 0.90, "voice_match": 0.75, "compliance": 0.95,
        "timeliness": 0.85, "audience_fit": 0.80, "resilience": 0.80,
    },
    StrategicIntent.THOUGHT_LEADERSHIP: {
        "accuracy": 0.80, "consistency": 0.80, "completeness": 0.70,
        "professionalism": 0.75, "voice_match": 0.90, "compliance": 0.65,
        "timeliness": 0.75, "audience_fit": 0.75, "resilience": 0.85,
    },
    StrategicIntent.INTERNAL_COMMS: {
        "accuracy": 0.60, "consistency": 0.50, "completeness": 0.50,
        "professionalism": 0.40, "voice_match": 0.30, "compliance": 0.40,
        "timeliness": 0.50, "audience_fit": 0.30, "resilience": 0.20,
    },
}

# ── Profile → Auto Gate Level ────────────────────────────────────

PROFILE_GATE_LEVELS = {
    GovernanceProfile.INTERNAL: 1,
    GovernanceProfile.SOCIAL_CONTENT: 2,
    GovernanceProfile.CLIENT_COMMUNICATION: 2,
    GovernanceProfile.SALES_MATERIALS: 3,
    GovernanceProfile.REGULATED_OUTPUT: 3,
    GovernanceProfile.PUBLIC_STATEMENT: 3,
}

# ── Staleness Half-Lives (days) ──────────────────────────────────

HALF_LIVES = {
    "statistic": 180,
    "regulatory_reference": 180,
    "technology_claim": 90,
    "pricing": 60,
    "competitor_reference": 30,
    "market_prediction": 90,
    "methodology": 365,
    "person_reference": 60,
}


# ── Data Models ──────────────────────────────────────────────────

@dataclass
class TrustSurface:
    """Nine-dimensional trust scoring."""
    accuracy: float = 100.0
    consistency: float = 100.0
    completeness: float = 100.0
    professionalism: float = 100.0
    voice_match: float = 100.0
    compliance: float = 100.0
    timeliness: float = 100.0
    audience_fit: float = 100.0
    resilience: float = 100.0

    @property
    def overall(self) -> float:
        dims = [
            self.accuracy, self.consistency, self.completeness,
            self.professionalism, self.voice_match, self.compliance,
            self.timeliness, self.audience_fit, self.resilience,
        ]
        return round(sum(dims) / len(dims), 1)

    def weighted_score(self, intent: StrategicIntent) -> float:
        weights = INTENT_WEIGHTS.get(intent, INTENT_WEIGHTS[StrategicIntent.INTERNAL_COMMS])
        total_weight = sum(weights.values())
        weighted = (
            self.accuracy * weights["accuracy"]
            + self.consistency * weights["consistency"]
            + self.completeness * weights["completeness"]
            + self.professionalism * weights["professionalism"]
            + self.voice_match * weights["voice_match"]
            + self.compliance * weights["compliance"]
            + self.timeliness * weights["timeliness"]
            + self.audience_fit * weights["audience_fit"]
            + self.resilience * weights["resilience"]
        )
        return round(weighted / total_weight, 1)

    def to_dict(self) -> dict:
        return {
            "accuracy": self.accuracy, "consistency": self.consistency,
            "completeness": self.completeness, "professionalism": self.professionalism,
            "voice_match": self.voice_match, "compliance": self.compliance,
            "timeliness": self.timeliness, "audience_fit": self.audience_fit,
            "resilience": self.resilience, "overall": self.overall,
        }


@dataclass
class AudienceTrustPrediction:
    """Trust impact prediction for a specific audience member."""
    audience_name: str
    audience_role: str = ""
    trust_delta: float = 0.0
    risks: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)


@dataclass
class RiskEconomicsItem:
    """Risk/benefit analysis for a single flagged issue."""
    issue: str
    location: str = ""  # "Page 5, paragraph 2"
    severity: RiskSeverity = RiskSeverity.MODERATE
    financial_downside_low: float = 0.0
    financial_downside_high: float = 0.0
    probability_of_harm: float = 0.0
    expected_downside: float = 0.0
    expected_upside: float = 0.0
    risk_ratio: float = 0.0  # upside / downside
    recommendation: str = ""  # CHANGE, KEEP, HEDGE
    suggested_fix: str = ""


@dataclass
class PositionConflict:
    """A detected conflict between current content and prior positions."""
    claim_in_document: str
    conflicts_with: str  # "blog_post_jan_2026", "proposal_techcorp"
    conflict_description: str = ""
    resolution_options: list[str] = field(default_factory=list)
    severity: str = "moderate"  # low, moderate, high


@dataclass
class TrackedPosition:
    """A position/claim tracked in the Position Integrity Graph."""
    position_id: str = ""
    claim: str = ""
    source_document: str = ""
    date_stated: datetime = field(default_factory=datetime.now)
    category: str = ""  # pricing, timeline, capability, methodology
    still_current: bool = True

    def __post_init__(self):
        if not self.position_id:
            self.position_id = f"pos_{uuid.uuid4().hex[:6]}"


@dataclass
class PerspectiveReview:
    """Result from one persona in the Multi-Perspective Review Council."""
    persona: str  # regulator, lawyer, client_sponsor, competitor, prospect
    flags: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    flag_count: int = 0


@dataclass
class StrategicException:
    """A governed rule-break with reasoning."""
    exception_id: str = ""
    rule_broken: str = ""
    intent: str = ""
    risk_ratio: float = 0.0
    reasoning: str = ""
    conditions: list[str] = field(default_factory=list)
    granted: bool = False
    outcome: Optional[str] = None
    tracked_at: Optional[datetime] = None

    def __post_init__(self):
        if not self.exception_id:
            self.exception_id = f"exc_{uuid.uuid4().hex[:6]}"


@dataclass
class OverrideRecord:
    """A record of Mani overriding a Sentinel recommendation."""
    override_id: str = ""
    audit_id: str = ""
    issue_overridden: str = ""
    reason: str = ""
    outcome: Optional[OverrideOutcome] = None
    outcome_detail: str = ""
    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not self.override_id:
            self.override_id = f"ovr_{uuid.uuid4().hex[:6]}"


@dataclass
class IncidentRecord:
    """A real-world incident traced back to content."""
    incident_id: str = ""
    description: str = ""
    root_cause: str = ""
    self_correction: str = ""
    new_rule: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    affected_audits: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.incident_id:
            self.incident_id = f"inc_{uuid.uuid4().hex[:6]}"


@dataclass
class StalenessItem:
    """An item approaching its freshness half-life."""
    item_type: str  # statistic, regulatory_reference, etc.
    content: str = ""
    source_document: str = ""
    age_days: int = 0
    half_life_days: int = 180
    freshness_pct: float = 100.0
    action_needed: str = ""


@dataclass
class CredibilitySuggestion:
    """A suggested credibility injection."""
    signal_type: str  # expertise, reliability, understanding, integrity
    suggestion: str = ""
    expected_trust_impact: float = 0.0


@dataclass
class QualityAudit:
    """Complete audit result for a reviewed document."""
    audit_id: str = ""
    document_title: str = ""
    document_type: str = ""
    governance_profile: GovernanceProfile = GovernanceProfile.INTERNAL
    strategic_intent: StrategicIntent = StrategicIntent.INTERNAL_COMMS

    # Trust Surface
    trust_surface: TrustSurface = field(default_factory=TrustSurface)
    weighted_trust_score: float = 0.0

    # Audience
    audience_predictions: list[AudienceTrustPrediction] = field(default_factory=list)

    # Risk Economics
    risk_items: list[RiskEconomicsItem] = field(default_factory=list)
    total_downside: float = 0.0
    total_upside: float = 0.0
    net_risk_ratio: float = 0.0

    # Position Integrity
    position_conflicts: list[PositionConflict] = field(default_factory=list)

    # Multi-Perspective Review
    perspective_reviews: list[PerspectiveReview] = field(default_factory=list)

    # Counts
    facts_checked: int = 0
    facts_verified: int = 0
    compliance_rules_checked: int = 0
    compliance_passed: int = 0
    brand_checks: int = 0
    brand_passed: int = 0
    brand_deviations_approved: int = 0

    # Staleness & Resilience
    staleness_items: list[StalenessItem] = field(default_factory=list)
    resilience_score: float = 100.0

    # Credibility Engineering
    credibility_present: list[str] = field(default_factory=list)
    credibility_missing: list[str] = field(default_factory=list)
    credibility_suggestions: list[CredibilitySuggestion] = field(default_factory=list)

    # Thinking Frameworks
    thinking_frameworks_applied: list[str] = field(default_factory=list)
    thinking_synthesis: str = ""

    # Verdict
    verdict: AuditVerdict = AuditVerdict.CLEAN
    summary: str = ""
    critical_issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)

    # Metadata
    reviewed_at: datetime = field(default_factory=datetime.now)
    overrides: list[OverrideRecord] = field(default_factory=list)

    def __post_init__(self):
        if not self.audit_id:
            self.audit_id = f"qa_{uuid.uuid4().hex[:8]}"
