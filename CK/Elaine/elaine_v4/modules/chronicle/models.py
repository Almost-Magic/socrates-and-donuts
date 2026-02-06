"""
Chronicle v2 — Data Models
Meeting Intelligence & Commitment Lifecycle Engine

Almost Magic Tech Lab — Patentable IP
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


# ── Enums ────────────────────────────────────────────────────────

class MeetingTemplate(str, Enum):
    DISCOVERY_CALL = "discovery_call"
    PROPOSAL_REVIEW = "proposal_review"
    STRATEGY_SESSION = "strategy_session"
    CHECK_IN = "check_in"
    WEBINAR = "webinar"
    SALES_NEGOTIATION = "sales_negotiation"
    BOARD_EXECUTIVE = "board_executive"
    INCIDENT_ESCALATION = "incident_escalation"
    CUSTOM = "custom"


class CommitmentType(str, Enum):
    EXPLICIT_DEADLINE = "explicit_deadline"   # "I'll send it by Friday"
    SOFT = "soft"                             # "Let me think about that"
    MUTUAL = "mutual"                        # "We'll schedule a follow-up"
    CONDITIONAL = "conditional"               # "I can introduce you to..."
    ASPIRATIONAL = "aspirational"             # "We should catch up more"
    DELEGATION = "delegation"                 # "I need you to..."
    THIRD_PARTY = "third_party"              # "Sarah will handle..."
    ACTION_ITEM = "action_item"              # "Action: Mani to draft scope"


class CommitmentStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    BROKEN = "broken"
    CANCELLED = "cancelled"


class TrustStake(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DecisionContext(str, Enum):
    COLLABORATIVE = "collaborative"  # Made in meeting
    SOLO = "solo"                   # Mani's judgment alone
    DATA_INFORMED = "data_informed"  # Used Cartographer/research
    PRESSURED = "pressured"         # Under time pressure
    ORACLE_ASSISTED = "oracle_assisted"  # Used Thinking Frameworks


class DecisionOutcome(str, Enum):
    GREAT = "great"
    GOOD = "good"
    NEUTRAL = "neutral"
    BAD = "bad"
    UNKNOWN = "unknown"


class TrajectoryDirection(str, Enum):
    RISING = "rising"
    STABLE = "stable"
    FLATTENING = "flattening"
    DECLINING = "declining"
    STALLED = "stalled"


class InnovationType(str, Enum):
    INTERNAL_TOOL = "internal_tool"
    CUSTOMER_PRODUCT = "customer_product"
    SERVICE_PACKAGE = "service_package"
    PROCESS_IMPROVEMENT = "process_improvement"


# ── Commitment Mass Defaults ─────────────────────────────────────

COMMITMENT_MASS = {
    CommitmentType.EXPLICIT_DEADLINE: 80,
    CommitmentType.SOFT: 45,
    CommitmentType.MUTUAL: 60,
    CommitmentType.CONDITIONAL: 35,
    CommitmentType.ASPIRATIONAL: 15,
    CommitmentType.DELEGATION: 50,
    CommitmentType.THIRD_PARTY: 30,
    CommitmentType.ACTION_ITEM: 70,
}

COMMITMENT_CONFIDENCE = {
    CommitmentType.EXPLICIT_DEADLINE: 0.95,
    CommitmentType.SOFT: 0.75,
    CommitmentType.MUTUAL: 0.85,
    CommitmentType.CONDITIONAL: 0.70,
    CommitmentType.ASPIRATIONAL: 0.40,
    CommitmentType.DELEGATION: 0.90,
    CommitmentType.THIRD_PARTY: 0.80,
    CommitmentType.ACTION_ITEM: 0.95,
}


# ── Data Models ──────────────────────────────────────────────────

@dataclass
class Participant:
    name: str
    role: str = ""        # host, prospect, client, partner, stakeholder
    company: str = ""
    poi_id: str = ""      # Link to Constellation
    email: str = ""


@dataclass
class Commitment:
    """A commitment extracted from a meeting."""
    commitment_id: str = ""
    text: str = ""
    owner: str = ""            # "mani" or participant name
    commitment_type: CommitmentType = CommitmentType.EXPLICIT_DEADLINE
    due_date: Optional[datetime] = None
    confidence: float = 0.95
    trust_stake: TrustStake = TrustStake.HIGH
    follow_through_prediction: float = 0.7
    gravity_item_id: str = ""  # Auto-created Gravity item
    status: CommitmentStatus = CommitmentStatus.PENDING
    outcome_notes: str = ""
    detected_at: Optional[str] = None  # Timestamp in meeting

    def __post_init__(self):
        if not self.commitment_id:
            self.commitment_id = f"cmt_{uuid.uuid4().hex[:6]}"
        if self.confidence == 0.95:  # Default — use type-based
            self.confidence = COMMITMENT_CONFIDENCE.get(self.commitment_type, 0.70)

    @property
    def default_mass(self) -> int:
        return COMMITMENT_MASS.get(self.commitment_type, 50)

    @property
    def is_overdue(self) -> bool:
        return (
            self.due_date is not None
            and self.due_date < datetime.now()
            and self.status == CommitmentStatus.PENDING
        )


@dataclass
class Decision:
    """A decision made in or after a meeting."""
    decision_id: str = ""
    text: str = ""
    made_by: str = ""         # "mani", "mutual", participant name
    context: DecisionContext = DecisionContext.COLLABORATIVE
    pressure_level: str = "moderate"
    data_informed: bool = False
    outcome: DecisionOutcome = DecisionOutcome.UNKNOWN
    outcome_notes: str = ""
    outcome_tracked_at: Optional[datetime] = None
    meeting_id: str = ""

    def __post_init__(self):
        if not self.decision_id:
            self.decision_id = f"dec_{uuid.uuid4().hex[:6]}"


@dataclass
class MeetingIntelligence:
    """Business intelligence extracted from a meeting."""
    budget_range_min: float = 0
    budget_range_max: float = 0
    currency: str = "AUD"
    decision_maker: str = ""
    approval_chain: list[str] = field(default_factory=list)
    timeline: str = ""
    competitor_exposure: str = ""
    hot_buttons: list[str] = field(default_factory=list)
    tech_stack: list[str] = field(default_factory=list)


@dataclass
class MeetingPatterns:
    """Patterns detected during a meeting."""
    decision_density: int = 0
    commitment_balance: dict = field(default_factory=lambda: {"mani": 0, "other": 0})
    topic_coverage: float = 0.0
    sentiment_trajectory: str = ""
    power_dynamics: str = ""


@dataclass
class MeetingScore:
    overall: float = 0.0
    percentile: int = 0
    comparison: str = ""


@dataclass
class PreMeetingBrief:
    """Intelligence prepared before a meeting."""
    relationship_context: str = ""
    what_you_owe: list[str] = field(default_factory=list)
    what_they_might_need: list[str] = field(default_factory=list)
    preparation_gaps: list[str] = field(default_factory=list)
    suggested_opening: str = ""
    prep_questions: list[str] = field(default_factory=list)
    poi_recent_activity: list[str] = field(default_factory=list)


@dataclass
class FollowUpDraft:
    """Auto-generated follow-up email."""
    subject: str = ""
    body: str = ""
    tone: str = "warm_professional"
    sentinel_checked: bool = False
    sentinel_verdict: str = ""
    sent: bool = False


@dataclass
class MeetingRecord:
    """Complete meeting record."""
    meeting_id: str = ""
    title: str = ""
    date: datetime = field(default_factory=datetime.now)
    duration_minutes: int = 0
    template: MeetingTemplate = MeetingTemplate.DISCOVERY_CALL
    participants: list[Participant] = field(default_factory=list)

    # Three phases
    pre_meeting: PreMeetingBrief = field(default_factory=PreMeetingBrief)
    commitments: list[Commitment] = field(default_factory=list)
    decisions: list[Decision] = field(default_factory=list)
    intelligence: MeetingIntelligence = field(default_factory=MeetingIntelligence)
    patterns: MeetingPatterns = field(default_factory=MeetingPatterns)
    score: MeetingScore = field(default_factory=MeetingScore)
    content_opportunities: list[str] = field(default_factory=list)
    follow_up: FollowUpDraft = field(default_factory=FollowUpDraft)

    # Transcript
    transcript: str = ""
    summary: str = ""

    def __post_init__(self):
        if not self.meeting_id:
            self.meeting_id = f"mtg_{uuid.uuid4().hex[:8]}"


@dataclass
class RelationshipTrajectory:
    """Multi-meeting relationship health for a person/company."""
    person_name: str
    company: str = ""
    meetings: list[dict] = field(default_factory=list)  # {date, trust_delta, balance, notes}
    direction: TrajectoryDirection = TrajectoryDirection.STABLE
    risk: str = ""
    suggested_action: str = ""


@dataclass
class PersonFollowThroughModel:
    """Per-person follow-through prediction model."""
    person_name: str
    total_commitments: int = 0
    completed: int = 0
    broken: int = 0
    avg_days_late: float = 0.0
    strong_areas: list[str] = field(default_factory=list)   # "technical items"
    weak_areas: list[str] = field(default_factory=list)     # "internal approvals"

    @property
    def follow_through_rate(self) -> float:
        if self.total_commitments == 0:
            return 0.55  # Default for unknown
        return self.completed / self.total_commitments


@dataclass
class Innovation:
    """A product/service opportunity detected by the App Innovator."""
    innovation_id: str = ""
    title: str = ""
    innovation_type: InnovationType = InnovationType.CUSTOMER_PRODUCT
    description: str = ""
    sources: dict = field(default_factory=dict)  # module → [evidence]
    recommendation: str = ""  # build, don't_build, need_more_data
    confidence: float = 0.0
    estimated_revenue: str = ""
    beast_research_requested: bool = False
    mani_decision: Optional[str] = None
    detected_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not self.innovation_id:
            self.innovation_id = f"innov_{uuid.uuid4().hex[:6]}"


@dataclass
class CalendarIntelligence:
    """Weekly calendar analysis."""
    meeting_count: int = 0
    avg_meetings_per_week: float = 10.0
    deep_work_blocks: int = 0
    deep_work_target: int = 4
    buffer_warnings: list[str] = field(default_factory=list)
    quality_forecast: list[dict] = field(default_factory=list)  # {meeting, predicted_value}
    pattern_insights: list[str] = field(default_factory=list)
    productivity_prediction: str = ""
