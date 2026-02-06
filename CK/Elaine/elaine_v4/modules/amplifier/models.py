"""
Amplifier v2 — Data Models
Content Orchestration & Authority Engine

Almost Magic Tech Lab — Patentable IP
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


# ── Enums ────────────────────────────────────────────────────────

class EpistemicLevel(str, Enum):
    CONVICTION = "conviction"     # Hard-earned belief, evidence + experience
    PROVISIONAL = "provisional"   # Strong hypothesis, growing evidence
    EXPLORATORY = "exploratory"   # Thinking out loud, testing an idea


class ContentObjective(str, Enum):
    AUTHORITY = "authority"           # Citations, backlinks, speaking invites
    PIPELINE = "pipeline"             # Deal influence, prospect engagement
    STRATEGIC_POSITIONING = "strategic"  # Topic ownership vs competitors
    NETWORK_DEPTH = "network"         # POI engagement, introductions


class ContentStatus(str, Enum):
    IDEA = "idea"
    DRAFT = "draft"
    REVIEW = "review"
    QUALITY_GATE = "quality_gate"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    REPURPOSED = "repurposed"
    ARCHIVED = "archived"


class ContentFormat(str, Enum):
    LINKEDIN_POST = "linkedin_post"
    LINKEDIN_CAROUSEL = "linkedin_carousel"
    NEWSLETTER = "newsletter"
    BLOG_POST = "blog_post"
    THREAD = "thread"
    PODCAST_POINT = "podcast_point"
    CLIENT_EMAIL = "client_email"
    CONFERENCE_SLIDE = "conference_slide"
    VIDEO_SCRIPT = "video_script"
    WHITEPAPER = "whitepaper"
    COMMENT = "comment"


class ContentPillar(str, Enum):
    AI_GOVERNANCE = "ai_governance"
    CYBERSECURITY = "cybersecurity"
    BUILDING_IN_PUBLIC = "building_in_public"
    THOUGHT_LEADERSHIP = "thought_leadership"
    CLIENT_SUCCESS = "client_success"


class RestraintType(str, Enum):
    OVEREXPOSURE = "overexposure"
    STRATEGIC_SCARCITY = "strategic_scarcity"
    CLIENT_SENSITIVITY = "client_sensitivity"
    TIMING_CONFLICT = "timing_conflict"
    SILENCE_PREMIUM = "silence_premium"
    RED_GIANT_ACTIVE = "red_giant_active"


class QualityGateStatus(str, Enum):
    PASS = "pass"
    PASS_WITH_EDITS = "pass_with_edits"
    FAIL = "fail"
    PENDING = "pending"


# ── Objective Weights ────────────────────────────────────────────
OBJECTIVE_WEIGHTS = {
    ContentObjective.AUTHORITY: 0.30,
    ContentObjective.PIPELINE: 0.30,
    ContentObjective.STRATEGIC_POSITIONING: 0.25,
    ContentObjective.NETWORK_DEPTH: 0.15,
}


# ── Data Models ──────────────────────────────────────────────────

@dataclass
class GeneWeight:
    """Learned effectiveness of a content gene."""
    gene_type: str   # hook_type, structure, evidence_type
    value: str       # "contrarian_reframe", "case_study", etc.
    effectiveness: float = 0.5
    sample_size: int = 0

    def update(self, outcome: float, learning_rate: float = 0.1):
        self.effectiveness += learning_rate * (outcome - self.effectiveness)
        self.sample_size += 1


@dataclass
class ContentGenome:
    """The DNA of a piece of content."""
    genome_id: str = ""
    thesis: str = ""
    argument_structure: str = ""  # contrarian_reframe, story_lesson, problem_solution
    certainty_level: EpistemicLevel = EpistemicLevel.CONVICTION
    evidence: list[dict] = field(default_factory=list)  # {type, data, decay_check}
    voice_score: float = 0.0
    pillar: ContentPillar = ContentPillar.THOUGHT_LEADERSHIP
    audience_primary: str = ""
    audience_secondary: str = ""
    format: ContentFormat = ContentFormat.LINKEDIN_POST
    objective: ContentObjective = ContentObjective.AUTHORITY

    gene_weights: dict[str, GeneWeight] = field(default_factory=dict)
    mutations: list[str] = field(default_factory=list)
    pipeline_relevance: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.genome_id:
            self.genome_id = f"gen_{uuid.uuid4().hex[:6]}"


@dataclass
class AudienceFitness:
    """How well content reached the right audience."""
    icp_engagement_pct: float = 0.0
    non_icp_engagement_pct: float = 0.0
    adverse_resonance_pct: float = 0.0
    top_segments: list[dict] = field(default_factory=list)  # {segment, pct}


@dataclass
class ContentPerformance:
    """Multi-objective performance tracking."""
    impressions: int = 0
    reactions: int = 0
    comments: int = 0
    saves: int = 0
    shares: int = 0
    audience_fitness: AudienceFitness = field(default_factory=AudienceFitness)
    pipeline_influence: list[str] = field(default_factory=list)  # POI names who engaged
    authority_signals: dict = field(default_factory=lambda: {"citations": 0, "backlinks": 0, "llm_mentions": 0})
    compound_score: float = 0.0

    # Multi-objective scores (0-10)
    authority_score: float = 0.0
    pipeline_score: float = 0.0
    strategic_score: float = 0.0
    network_score: float = 0.0

    @property
    def multi_objective_score(self) -> float:
        return (
            self.authority_score * OBJECTIVE_WEIGHTS[ContentObjective.AUTHORITY]
            + self.pipeline_score * OBJECTIVE_WEIGHTS[ContentObjective.PIPELINE]
            + self.strategic_score * OBJECTIVE_WEIGHTS[ContentObjective.STRATEGIC_POSITIONING]
            + self.network_score * OBJECTIVE_WEIGHTS[ContentObjective.NETWORK_DEPTH]
        )


@dataclass
class QualityGateResult:
    """Result of pre-publish quality gate."""
    gate_status: QualityGateStatus = QualityGateStatus.PENDING
    factual_accuracy: str = "pending"
    epistemic_alignment: str = "pending"
    voice_consistency: float = 0.0
    client_sensitivity: str = "pending"
    audience_fitness_prediction: str = "pending"
    brand_alignment: str = "pending"
    warnings: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    thinking_frameworks_applied: list[str] = field(default_factory=list)


@dataclass
class RestraintSignal:
    """A reason to NOT publish."""
    restraint_type: RestraintType
    message: str
    severity: str = "advisory"  # advisory, warning, block
    expires: Optional[datetime] = None


@dataclass
class ContentItem:
    """A piece of content in the Amplifier pipeline."""
    content_id: str = ""
    title: str = ""
    body: str = ""
    genome: ContentGenome = field(default_factory=ContentGenome)
    status: ContentStatus = ContentStatus.IDEA
    performance: ContentPerformance = field(default_factory=ContentPerformance)
    quality_gate: QualityGateResult = field(default_factory=QualityGateResult)
    restraint_signals: list[RestraintSignal] = field(default_factory=list)
    scheduled_date: Optional[datetime] = None
    published_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    source_discovery_id: str = ""  # If triggered by Cartographer
    authority_graph_links: dict = field(default_factory=lambda: {"supports": [], "extends": [], "contradicts": [], "series": ""})

    def __post_init__(self):
        if not self.content_id:
            self.content_id = f"amp_{uuid.uuid4().hex[:6]}"


@dataclass
class CommentaryOpportunity:
    """A suggested comment on someone else's post."""
    poi_name: str
    poi_company: str = ""
    post_topic: str = ""
    suggested_comment: str = ""
    why: str = ""
    objective: ContentObjective = ContentObjective.NETWORK_DEPTH
    urgency: str = "normal"  # normal, timely (< 4 hours)


@dataclass
class WarmLead:
    """A prospect detected from content engagement."""
    name: str
    company: str = ""
    title: str = ""
    engagement_pattern: list[str] = field(default_factory=list)
    intent_score: float = 0.0
    segment: str = ""
    suggested_outreach: str = ""
    detected_at: datetime = field(default_factory=datetime.now)
