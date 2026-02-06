"""
App Innovator + Beast — Data Models
Autonomous Opportunity Detection + Research Delegation Protocol

Almost Magic Tech Lab — Patentable IP
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


# ── Enums ────────────────────────────────────────────────────────

class InnovationType(str, Enum):
    INTERNAL_TOOL = "internal_tool"          # Proposal generator, automations
    CUSTOMER_PRODUCT = "customer_product"     # New service packages
    SERVICE_PACKAGE = "service_package"       # Bundled offerings
    PROCESS_IMPROVEMENT = "process_improvement"
    CONTENT_PRODUCT = "content_product"       # Courses, templates, guides
    PARTNERSHIP = "partnership"               # Joint offerings


class InnovationStatus(str, Enum):
    DETECTED = "detected"           # Pattern found, not yet reviewed
    INVESTIGATING = "investigating"  # Mani reviewing
    RESEARCH_PENDING = "research_pending"  # Delegated to Beast
    RESEARCH_COMPLETE = "research_complete"
    APPROVED = "approved"           # Mani says build
    REJECTED = "rejected"           # Not pursuing
    BUILDING = "building"           # In development
    LAUNCHED = "launched"


class SignalSource(str, Enum):
    CHRONICLE = "chronicle"     # Meeting patterns, client requests
    CARTOGRAPHER = "cartographer"  # Market gaps, negative space
    AMPLIFIER = "amplifier"     # Content demand signals
    SENTINEL = "sentinel"       # Quality patterns, common failures
    GRAVITY = "gravity"         # Time sinks, repeated tasks
    CONSTELLATION = "constellation"  # Competitor/peer intelligence
    BEAST = "beast"             # Market research findings


class ResearchType(str, Enum):
    COMPETITOR_ANALYSIS = "competitor_analysis"
    TAM_ESTIMATION = "tam_estimation"
    REGULATORY_PIPELINE = "regulatory_pipeline"
    POSITIONING_GAPS = "positioning_gaps"
    PRICING_RESEARCH = "pricing_research"
    CUSTOMER_VALIDATION = "customer_validation"
    TREND_ANALYSIS = "trend_analysis"


class ResearchStatus(str, Enum):
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    FAILED = "failed"


class Recommendation(str, Enum):
    BUILD = "build"
    DONT_BUILD = "dont_build"
    NEED_MORE_DATA = "need_more_data"
    INVESTIGATE = "investigate"
    DEFER = "defer"  # Good idea, wrong timing


# ── Data Models ──────────────────────────────────────────────────

@dataclass
class InnovationSignal:
    """A signal from one of Elaine's modules pointing to an opportunity."""
    source: SignalSource
    evidence: str
    strength: float = 0.5  # 0-1
    detected_at: datetime = field(default_factory=datetime.now)


@dataclass
class Opportunity:
    """A detected product/service/tool opportunity."""
    opportunity_id: str = ""
    title: str = ""
    innovation_type: InnovationType = InnovationType.CUSTOMER_PRODUCT
    description: str = ""
    signals: list[InnovationSignal] = field(default_factory=list)
    status: InnovationStatus = InnovationStatus.DETECTED
    recommendation: Recommendation = Recommendation.INVESTIGATE
    confidence: float = 0.0
    estimated_revenue: str = ""
    estimated_time_savings_hours: float = 0.0
    roi_notes: str = ""
    mani_decision: Optional[str] = None
    decided_at: Optional[datetime] = None
    detected_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not self.opportunity_id:
            self.opportunity_id = f"opp_{uuid.uuid4().hex[:6]}"

    @property
    def signal_count(self) -> int:
        return len(self.signals)

    @property
    def multi_source(self) -> bool:
        """True if signals come from 2+ different modules."""
        sources = set(s.source for s in self.signals)
        return len(sources) >= 2

    @property
    def composite_confidence(self) -> float:
        """Higher when multiple sources converge."""
        if not self.signals:
            return 0.0
        base = sum(s.strength for s in self.signals) / len(self.signals)
        # Multi-source bonus: +15% per additional source
        sources = len(set(s.source for s in self.signals))
        bonus = (sources - 1) * 0.15
        return min(0.95, base + bonus)


@dataclass
class ResearchQuestion:
    """A specific research question within a Beast brief."""
    question: str
    research_type: ResearchType
    priority: int = 1  # 1=highest


@dataclass
class ResearchBrief:
    """A structured research request delegated to Beast."""
    brief_id: str = ""
    opportunity_id: str = ""
    title: str = ""
    context: str = ""
    questions: list[ResearchQuestion] = field(default_factory=list)
    deadline_days: int = 5
    format_requested: str = "Executive brief (1 page) + detailed appendix"
    confidence_threshold: float = 0.70  # Flag anything below this
    status: ResearchStatus = ResearchStatus.QUEUED
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        if not self.brief_id:
            self.brief_id = f"beast_{uuid.uuid4().hex[:6]}"


@dataclass
class ResearchFinding:
    """A finding returned by Beast research."""
    question_answered: str
    finding: str
    confidence: float = 0.7
    sources: list[str] = field(default_factory=list)
    data_points: dict = field(default_factory=dict)


@dataclass
class ResearchResult:
    """Complete research result from Beast."""
    brief_id: str = ""
    findings: list[ResearchFinding] = field(default_factory=list)
    recommendation: Recommendation = Recommendation.INVESTIGATE
    executive_summary: str = ""
    risks: list[str] = field(default_factory=list)
    completed_at: datetime = field(default_factory=datetime.now)
