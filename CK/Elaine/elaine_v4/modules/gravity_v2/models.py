"""
Gravity Engine v2 — Data Models
Defines GravityItem, GravityField snapshot, and supporting types.
Almost Magic Tech Lab — Patentable IP
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
import uuid


# ── Enums ──────────────────────────────────────────────────────────

class ItemSource(Enum):
    PIPELINE = "pipeline"
    CHRONICLE = "chronicle"       # Meeting commitment
    EMAIL = "email"               # Email commitment
    CALENDAR = "calendar"
    MANUAL = "manual"
    CARTOGRAPHER = "cartographer"  # Content opportunity
    CONSTELLATION = "constellation"  # Relationship maintenance
    OKR = "okr"


class MomentumState(Enum):
    NOT_STARTED = "not_started"
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    NEAR_COMPLETE = "near_complete"
    COMPLETE = "complete"
    ABANDONED = "abandoned"


class EnergyCategory(Enum):
    DEEP_COGNITIVE = "deep_cognitive"
    COLLABORATIVE = "collaborative"
    CREATIVE = "creative"
    ADMINISTRATIVE = "administrative"
    UNCOMFORTABLE = "uncomfortable"


class AlertLevel(Enum):
    RED_GIANT = "red_giant"           # Gravity > 90 or collision
    APPROACHING_MASS = "approaching"  # Gravity crosses 70
    ORBITAL_DRIFT = "drift"           # Untouched 5+ days, rising
    STRATEGIC_FLOOR = "strategic"     # OKR item untouched 7+ days
    NORMAL = "normal"


class TrajectoryDirection(Enum):
    RISING = "rising"
    STABLE = "stable"
    FALLING = "falling"
    SATURATED = "saturated"  # Governor-capped


class RelationshipElasticity(Enum):
    BRITTLE = "brittle"     # New prospect — one miss can lose them
    MODERATE = "moderate"    # Active Tier 1 client
    ELASTIC = "elastic"     # Long-term partner
    HIGH = "high"           # Close collaborator


# ── Core Data Models ───────────────────────────────────────────────

@dataclass
class ChargeData:
    """Relational weight: who's counting on this item."""
    people: list[str] = field(default_factory=list)
    poi_ids: list[str] = field(default_factory=list)
    tier: Optional[int] = None
    promises: list[str] = field(default_factory=list)
    trust_cost_aud: float = 0.0
    elasticity: RelationshipElasticity = RelationshipElasticity.MODERATE
    prior_misses: int = 0

    @property
    def charge_multiplier(self) -> float:
        """Calculate charge multiplier from relational weight."""
        base = 1.0
        if self.tier == 1:
            base += 0.5
        elif self.tier == 2:
            base += 0.3
        elif self.tier == 3:
            base += 0.1
        if self.prior_misses >= 2:
            base += 0.4
        elif self.prior_misses == 1:
            base += 0.2
        if len(self.promises) > 0:
            base += 0.1 * min(len(self.promises), 3)
        return min(base, 2.5)


@dataclass
class ConsequenceData:
    """What breaks downstream if this doesn't get done."""
    revenue_at_risk: float = 0.0
    trust_erosion: str = "none"       # none, first_offence, repeat_offence
    blocked_items: list[str] = field(default_factory=list)
    strategic_setback: Optional[str] = None  # OKR key
    recovery_cost_hours: float = 0.0

    @property
    def kq_multiplier(self) -> float:
        """Calculate consequence multiplier (Kq). Capped at 2.5."""
        kq = 1.0
        if self.revenue_at_risk > 50_000:
            kq += 1.0
        elif self.revenue_at_risk > 10_000:
            kq += 0.5
        if self.trust_erosion == "repeat_offence":
            kq += 0.5
        if len(self.blocked_items) >= 3:
            kq += 0.3
        if self.strategic_setback:
            kq += 0.2
        if self.recovery_cost_hours > 0:
            # Recovery cost > 2x estimated effort
            kq += 0.3
        return min(kq, 2.5)


@dataclass
class PropagationEffect:
    """What happens to another item when this one completes or delays."""
    target_id: str
    on_complete_delta: Optional[float] = None  # e.g. +45
    on_delay_impact: Optional[str] = None       # "severe", "moderate", etc
    eliminate_on_complete: bool = False


@dataclass
class GravityBreakdown:
    """Full transparency: how the score was calculated."""
    mass_component: float = 0.0
    proximity_multiplier: float = 1.0
    charge_multiplier: float = 1.0
    consequence_multiplier: float = 1.0
    momentum_adjustment: float = 0.0
    burst_component: float = 0.0
    energy_fit_modifier: float = 0.0
    raw_score: float = 0.0
    normalised_score: float = 0.0
    governor_caps_applied: list[str] = field(default_factory=list)
    inertia_active: bool = False
    explanation: str = ""


@dataclass
class FailureRecord:
    """Post-mortem record from Failure Archaeology."""
    date: datetime = field(default_factory=datetime.now)
    failure_type: str = ""  # missed_deadline, abandoned, quality_failure
    root_causes: dict = field(default_factory=dict)  # cause → percentage
    prevention_rules: list[str] = field(default_factory=list)
    similar_items_adjusted: list[str] = field(default_factory=list)


@dataclass
class GravityItem:
    """
    A single item in the gravity field.
    Every task, commitment, deadline, or opportunity.
    """
    id: str = field(default_factory=lambda: f"grav_{uuid.uuid4().hex[:8]}")
    title: str = ""
    description: str = ""
    source: ItemSource = ItemSource.MANUAL
    source_id: Optional[str] = None  # External system reference

    # ── The Five Forces ──
    mass: float = 50.0                    # Intrinsic importance (0-100)
    learned_mass_adjustment: float = 1.0  # From revealed preference learning
    proximity_date: Optional[datetime] = None
    personal_cliff_multiplier: float = 1.0  # Learned from behaviour

    charge: ChargeData = field(default_factory=ChargeData)
    consequence: ConsequenceData = field(default_factory=ConsequenceData)

    # ── State ──
    momentum: MomentumState = MomentumState.NOT_STARTED
    progress_percent: float = 0.0
    inertia_active: bool = False
    energy_fit: EnergyCategory = EnergyCategory.DEEP_COGNITIVE
    estimated_hours: float = 1.0
    context_type: EnergyCategory = EnergyCategory.DEEP_COGNITIVE
    last_touched: Optional[datetime] = None

    # ── Calculated ──
    gravity_score: float = 0.0
    breakdown: Optional[GravityBreakdown] = None
    alert_level: AlertLevel = AlertLevel.NORMAL
    trajectory: TrajectoryDirection = TrajectoryDirection.STABLE

    # ── Relationships ──
    collision_risk: list[str] = field(default_factory=list)
    propagation_effects: list[PropagationEffect] = field(default_factory=list)
    okr_alignment: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    # ── Lifecycle ──
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    deprioritised: bool = False
    deprioritised_since: Optional[datetime] = None
    avoidance_count: int = 0
    failure_history: list[FailureRecord] = field(default_factory=list)

    @property
    def is_overdue(self) -> bool:
        if not self.proximity_date:
            return False
        return datetime.now() > self.proximity_date

    @property
    def days_until_due(self) -> Optional[float]:
        if not self.proximity_date:
            return None
        delta = self.proximity_date - datetime.now()
        return delta.total_seconds() / 86400

    @property
    def days_overdue(self) -> float:
        if not self.proximity_date or not self.is_overdue:
            return 0.0
        delta = datetime.now() - self.proximity_date
        return delta.total_seconds() / 86400

    @property
    def days_untouched(self) -> float:
        if not self.last_touched:
            delta = datetime.now() - self.created_at
        else:
            delta = datetime.now() - self.last_touched
        return delta.total_seconds() / 86400


@dataclass
class CollisionOption:
    """One resolution option for a time collision."""
    label: str = ""
    description: str = ""
    gains: list[str] = field(default_factory=list)
    costs: list[str] = field(default_factory=list)
    net_impact: str = ""
    trust_cost: str = ""
    recommended: bool = False


@dataclass
class Collision:
    """Two high-gravity items that can't both be done in available time."""
    item_a_id: str = ""
    item_b_id: str = ""
    options: list[CollisionOption] = field(default_factory=list)
    detected_at: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolution_chosen: Optional[str] = None


@dataclass
class StrategicBalance:
    """Weekly balance of urgent-tactical vs important-strategic work."""
    period_start: datetime = field(default_factory=datetime.now)
    period_end: Optional[datetime] = None
    urgent_tactical_pct: float = 0.0
    important_strategic_pct: float = 0.0
    administrative_pct: float = 0.0
    drift_alert: bool = False
    okrs_at_risk: list[str] = field(default_factory=list)
    recommendation: str = ""


@dataclass
class ContextCollapseWarning:
    """Warning when too many cognitive context switches in one day."""
    date: datetime = field(default_factory=datetime.now)
    context_types_required: int = 0
    estimated_switching_cost_hours: float = 0.0
    batching_recommendation: dict = field(default_factory=dict)
    estimated_savings_hours: float = 0.0


@dataclass
class GravityFieldSnapshot:
    """
    Daily snapshot of the entire gravity field.
    Used for morning briefing and trajectory analysis.
    """
    date: datetime = field(default_factory=datetime.now)
    total_items: int = 0
    red_giants: int = 0
    approaching: int = 0
    stable: int = 0
    peripheral: int = 0

    collisions: list[Collision] = field(default_factory=list)
    top_3_ids: list[str] = field(default_factory=list)

    trust_debt_total_aud: float = 0.0
    trust_debt_items: int = 0
    relationships_cooling: list[str] = field(default_factory=list)

    consequence_exposure: dict = field(default_factory=dict)
    strategic_balance: Optional[StrategicBalance] = None
    context_collapse: Optional[ContextCollapseWarning] = None

    available_hours: float = 8.0
    required_hours_red_giant: float = 0.0

    governor_status: dict = field(default_factory=dict)
    learning_status: dict = field(default_factory=dict)

    # The Ungraviton
    ungraviton_count: int = 0
    ungraviton_pattern: Optional[str] = None
