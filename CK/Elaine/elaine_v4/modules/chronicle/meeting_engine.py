"""
Chronicle v2 — Meeting Engine
Commitment Graph, Follow-Through Prediction, Decision Archaeology,
Relationship Trajectory, Meeting Patterns, App Innovator.

Patentable:
- Multi-Party Commitment Graph with Trust Impact
- Follow-Through Prediction Model
- Three-Phase Meeting Intelligence Lifecycle
- Meeting Effectiveness Learning Engine
- Decision Archaeology with Outcome Correlation
- Relationship Trajectory Tracking
- Autonomous App Innovation Engine

Almost Magic Tech Lab — Patentable IP
"""

import logging
import re
import uuid
from datetime import datetime, timedelta
from typing import Optional

from .models import (
    MeetingRecord, MeetingTemplate, Participant,
    Commitment, CommitmentType, CommitmentStatus, TrustStake,
    Decision, DecisionContext, DecisionOutcome,
    MeetingIntelligence, MeetingPatterns, MeetingScore,
    PreMeetingBrief, FollowUpDraft,
    RelationshipTrajectory, TrajectoryDirection,
    PersonFollowThroughModel,
    Innovation, InnovationType,
    CalendarIntelligence,
    COMMITMENT_MASS, COMMITMENT_CONFIDENCE,
)

logger = logging.getLogger("elaine.chronicle")


# ── Commitment Detection Patterns ────────────────────────────────

COMMITMENT_PATTERNS = [
    (r"\bI'll\s+(\w+)", CommitmentType.EXPLICIT_DEADLINE, "mani"),
    (r"\bI will\s+(\w+)", CommitmentType.EXPLICIT_DEADLINE, "mani"),
    (r"\bWe'll\s+(\w+)", CommitmentType.MUTUAL, "mutual"),
    (r"\bLet me\s+(\w+)", CommitmentType.SOFT, "mani"),
    (r"\bI can\s+(\w+)", CommitmentType.CONDITIONAL, "mani"),
    (r"\bWe should\s+(\w+)", CommitmentType.ASPIRATIONAL, "mutual"),
    (r"\bAction:\s*(.+)", CommitmentType.ACTION_ITEM, "assigned"),
]


class MeetingEngine:
    """
    Core Chronicle engine. Manages meeting lifecycle,
    commitment tracking, decision archaeology, and innovations.
    """

    def __init__(self):
        self.meetings: dict[str, MeetingRecord] = {}
        self.follow_through_models: dict[str, PersonFollowThroughModel] = {}
        self.innovations: list[Innovation] = []

        # Aggregate stats for pattern learning
        self._meeting_scores_by_template: dict[str, list[float]] = {}
        self._decision_outcomes: list[dict] = []

    # ── Meeting Lifecycle ────────────────────────────────────────

    def create_meeting(self, title: str, template: MeetingTemplate,
                       participants: list[dict],
                       date: datetime = None,
                       duration_minutes: int = 0,
                       **kwargs) -> MeetingRecord:
        """Create a new meeting record."""
        parts = [Participant(**p) if isinstance(p, dict) else p for p in participants]
        meeting = MeetingRecord(
            title=title,
            template=template,
            participants=parts,
            date=date or datetime.now(),
            duration_minutes=duration_minutes,
            **kwargs,
        )
        self.meetings[meeting.meeting_id] = meeting
        logger.info(f"Meeting created: {title} ({template.value})")
        return meeting

    def get_meeting(self, meeting_id: str) -> Optional[MeetingRecord]:
        return self.meetings.get(meeting_id)

    def list_meetings(self, limit: int = 20, person: str = "") -> list[MeetingRecord]:
        meetings = list(self.meetings.values())
        if person:
            meetings = [
                m for m in meetings
                if any(p.name.lower() == person.lower() for p in m.participants)
            ]
        return sorted(meetings, key=lambda m: m.date, reverse=True)[:limit]

    # ── Pre-Meeting Brief ────────────────────────────────────────

    def generate_pre_meeting_brief(self, meeting_id: str) -> PreMeetingBrief:
        """Generate intelligence brief before a meeting."""
        meeting = self.meetings.get(meeting_id)
        if not meeting:
            return PreMeetingBrief()

        brief = PreMeetingBrief()

        # Relationship context from meeting history
        for p in meeting.participants:
            if p.role != "host":
                prior = [
                    m for m in self.meetings.values()
                    if any(pp.name == p.name for pp in m.participants)
                    and m.meeting_id != meeting_id
                ]
                if prior:
                    brief.relationship_context = f"{len(prior)} prior meetings with {p.name}"
                else:
                    brief.relationship_context = f"First meeting with {p.name}"

        # What you owe them (overdue commitments)
        for m in self.meetings.values():
            for c in m.commitments:
                if c.owner == "mani" and c.status == CommitmentStatus.PENDING:
                    # Check if any participant matches
                    for p in meeting.participants:
                        if p.name != "Mani Padisetti" and p.name in m.title:
                            brief.what_you_owe.append(f"{c.text} (from {m.title})")

        # Template-based prep questions
        template_questions = {
            MeetingTemplate.DISCOVERY_CALL: [
                "What prompted this conversation now?",
                "Who else is involved in this decision?",
                "What's your timeline?",
                "Have you worked with consultants before?",
                "What does success look like?",
            ],
            MeetingTemplate.PROPOSAL_REVIEW: [
                "Any concerns about the proposal?",
                "Does the timeline work?",
                "Who needs to approve?",
                "What's the budget process?",
            ],
            MeetingTemplate.STRATEGY_SESSION: [
                "What are the top 3 priorities?",
                "What's blocking progress?",
                "What decisions need to be made today?",
            ],
        }
        brief.prep_questions = template_questions.get(meeting.template, [])

        meeting.pre_meeting = brief
        logger.info(f"Pre-meeting brief generated: {meeting.title}")
        return brief

    # ── Commitment Extraction ────────────────────────────────────

    def extract_commitments(self, meeting_id: str, text: str) -> list[Commitment]:
        """Extract commitments from meeting transcript/notes."""
        meeting = self.meetings.get(meeting_id)
        if not meeting:
            return []

        commitments = []
        for pattern, ctype, default_owner in COMMITMENT_PATTERNS:
            matches = re.finditer(pattern, text, re.I)
            for match in matches:
                # Get surrounding context (40 chars each side)
                start = max(0, match.start() - 40)
                end = min(len(text), match.end() + 60)
                context = text[start:end].strip()

                commitment = Commitment(
                    text=context,
                    owner=default_owner,
                    commitment_type=ctype,
                    trust_stake=TrustStake.HIGH if ctype in (
                        CommitmentType.EXPLICIT_DEADLINE, CommitmentType.ACTION_ITEM
                    ) else TrustStake.MEDIUM,
                )

                # Detect due dates from context
                date_match = re.search(
                    r"by\s+(friday|monday|tuesday|wednesday|thursday|saturday|sunday|"
                    r"end of (?:week|month)|tomorrow|next week|\d{1,2}\s*\w+)",
                    context, re.I
                )
                if date_match:
                    commitment.due_date = datetime.now() + timedelta(days=7)  # Simplified

                commitments.append(commitment)

        meeting.commitments.extend(commitments)

        # Update patterns
        mani_count = sum(1 for c in commitments if c.owner == "mani")
        other_count = len(commitments) - mani_count
        meeting.patterns.commitment_balance = {"mani": mani_count, "other": other_count}

        logger.info(f"Extracted {len(commitments)} commitments from {meeting.title}")
        return commitments

    def add_commitment(self, meeting_id: str, text: str, owner: str,
                       commitment_type: CommitmentType,
                       due_date: datetime = None,
                       trust_stake: TrustStake = TrustStake.HIGH) -> Commitment:
        """Manually add a commitment."""
        meeting = self.meetings.get(meeting_id)
        if not meeting:
            return Commitment()

        commitment = Commitment(
            text=text, owner=owner, commitment_type=commitment_type,
            due_date=due_date, trust_stake=trust_stake,
        )
        meeting.commitments.append(commitment)
        logger.info(f"Commitment added: {text[:40]} ({owner})")
        return commitment

    # ── Commitment Status Management ─────────────────────────────

    def update_commitment_status(self, meeting_id: str, commitment_id: str,
                                  status: CommitmentStatus, notes: str = ""):
        meeting = self.meetings.get(meeting_id)
        if not meeting:
            return
        for c in meeting.commitments:
            if c.commitment_id == commitment_id:
                old = c.status
                c.status = status
                c.outcome_notes = notes

                # Update follow-through model
                if c.owner != "mani" and c.owner != "mutual":
                    self._update_follow_through(c.owner, status)

                logger.info(f"Commitment {commitment_id}: {old.value} → {status.value}")
                break

    def get_active_commitments(self, owner: str = "") -> list[dict]:
        """Get all active commitments across all meetings."""
        active = []
        for m in self.meetings.values():
            for c in m.commitments:
                if c.status in (CommitmentStatus.PENDING, CommitmentStatus.IN_PROGRESS):
                    if not owner or c.owner == owner:
                        active.append({
                            "meeting": m.title,
                            "meeting_id": m.meeting_id,
                            "commitment_id": c.commitment_id,
                            "text": c.text,
                            "owner": c.owner,
                            "type": c.commitment_type.value,
                            "due_date": c.due_date.isoformat() if c.due_date else None,
                            "trust_stake": c.trust_stake.value,
                            "overdue": c.is_overdue,
                            "prediction": round(c.follow_through_prediction, 2),
                            "mass": c.default_mass,
                        })
        return sorted(active, key=lambda x: x.get("due_date") or "9999")

    def get_overdue_commitments(self) -> list[dict]:
        return [c for c in self.get_active_commitments() if c["overdue"]]

    # ── Follow-Through Prediction ────────────────────────────────

    def _update_follow_through(self, person_name: str, status: CommitmentStatus):
        if person_name not in self.follow_through_models:
            self.follow_through_models[person_name] = PersonFollowThroughModel(person_name=person_name)
        model = self.follow_through_models[person_name]
        model.total_commitments += 1
        if status == CommitmentStatus.COMPLETED:
            model.completed += 1
        elif status == CommitmentStatus.BROKEN:
            model.broken += 1

    def get_follow_through_prediction(self, person_name: str) -> float:
        model = self.follow_through_models.get(person_name)
        if model:
            return model.follow_through_rate
        return 0.55  # Default for unknown people

    # ── Decision Tracking ────────────────────────────────────────

    def add_decision(self, meeting_id: str, text: str, made_by: str,
                     context: DecisionContext, data_informed: bool = False,
                     pressure_level: str = "moderate") -> Decision:
        meeting = self.meetings.get(meeting_id)
        if not meeting:
            return Decision()
        decision = Decision(
            text=text, made_by=made_by, context=context,
            data_informed=data_informed, pressure_level=pressure_level,
            meeting_id=meeting_id,
        )
        meeting.decisions.append(decision)
        meeting.patterns.decision_density = len(meeting.decisions)
        logger.info(f"Decision recorded: {text[:40]}")
        return decision

    def record_decision_outcome(self, meeting_id: str, decision_id: str,
                                 outcome: DecisionOutcome, notes: str = ""):
        meeting = self.meetings.get(meeting_id)
        if not meeting:
            return
        for d in meeting.decisions:
            if d.decision_id == decision_id:
                d.outcome = outcome
                d.outcome_notes = notes
                d.outcome_tracked_at = datetime.now()
                self._decision_outcomes.append({
                    "context": d.context.value,
                    "data_informed": d.data_informed,
                    "pressure": d.pressure_level,
                    "outcome": outcome.value,
                })
                logger.info(f"Decision outcome: {d.text[:30]} → {outcome.value}")
                break

    def get_decision_archaeology(self) -> dict:
        """Decision quality analysis by context."""
        if not self._decision_outcomes:
            return {"decisions_tracked": 0, "message": "No decision outcomes recorded yet."}

        by_context = {}
        for d in self._decision_outcomes:
            ctx = d["context"]
            if ctx not in by_context:
                by_context[ctx] = {"total": 0, "good": 0}
            by_context[ctx]["total"] += 1
            if d["outcome"] in ("great", "good"):
                by_context[ctx]["good"] += 1

        return {
            "decisions_tracked": len(self._decision_outcomes),
            "by_context": {
                k: {"total": v["total"], "good_rate": round(v["good"] / max(v["total"], 1), 2)}
                for k, v in by_context.items()
            },
            "data_informed_rate": round(
                sum(1 for d in self._decision_outcomes if d["data_informed"])
                / max(len(self._decision_outcomes), 1), 2
            ),
            "under_pressure_rate": round(
                sum(1 for d in self._decision_outcomes if d["pressure"] == "high")
                / max(len(self._decision_outcomes), 1), 2
            ),
        }

    # ── Meeting Scoring ──────────────────────────────────────────

    def score_meeting(self, meeting_id: str) -> MeetingScore:
        meeting = self.meetings.get(meeting_id)
        if not meeting:
            return MeetingScore()

        # Score based on decision density, commitment balance, completeness
        dd_score = min(10, meeting.patterns.decision_density * 2.5)
        balance = meeting.patterns.commitment_balance
        balance_score = 8 if abs(balance.get("mani", 0) - balance.get("other", 0)) <= 2 else 5
        coverage_score = meeting.patterns.topic_coverage * 10

        overall = round((dd_score + balance_score + coverage_score) / 3, 1)

        # Track for pattern learning
        template = meeting.template.value
        self._meeting_scores_by_template.setdefault(template, []).append(overall)
        all_scores = self._meeting_scores_by_template[template]
        percentile = int(sum(1 for s in all_scores if s <= overall) / max(len(all_scores), 1) * 100)

        score = MeetingScore(
            overall=overall,
            percentile=percentile,
            comparison=f"{'Top' if percentile >= 50 else 'Bottom'} {100 - percentile}% of {template} meetings",
        )
        meeting.score = score
        return score

    # ── Follow-Up Draft ──────────────────────────────────────────

    def generate_follow_up(self, meeting_id: str) -> FollowUpDraft:
        meeting = self.meetings.get(meeting_id)
        if not meeting:
            return FollowUpDraft()

        # Build follow-up from meeting context
        participant_names = [p.name for p in meeting.participants if p.role != "host"]
        main_contact = participant_names[0] if participant_names else "there"

        mani_commitments = [c for c in meeting.commitments if c.owner == "mani"]
        their_commitments = [c for c in meeting.commitments if c.owner != "mani" and c.owner != "mutual"]

        body_parts = [f"Hi {main_contact},\n"]
        body_parts.append(f"Great connecting today. I enjoyed our conversation about {meeting.title}.\n")

        if mani_commitments:
            body_parts.append("As discussed, I'll be working on:")
            for c in mani_commitments[:3]:
                body_parts.append(f"  - {c.text}")

        if their_commitments:
            body_parts.append(f"\nOn your end, it would be helpful to have:")
            for c in their_commitments[:2]:
                body_parts.append(f"  - {c.text}")

        body_parts.append("\nLooking forward to the next steps.\n\nBest,\nMani")

        draft = FollowUpDraft(
            subject=f"Great connecting today, {main_contact}",
            body="\n".join(body_parts),
            tone="warm_professional",
        )
        meeting.follow_up = draft
        logger.info(f"Follow-up draft generated for {meeting.title}")
        return draft

    # ── Relationship Trajectory ──────────────────────────────────

    def get_relationship_trajectory(self, person_name: str) -> RelationshipTrajectory:
        """Track relationship health across multiple meetings."""
        person_meetings = []
        for m in sorted(self.meetings.values(), key=lambda m: m.date):
            if any(p.name.lower() == person_name.lower() for p in m.participants):
                mani_count = sum(1 for c in m.commitments if c.owner == "mani")
                other_count = len(m.commitments) - mani_count
                person_meetings.append({
                    "date": m.date.isoformat(),
                    "title": m.title,
                    "score": m.score.overall,
                    "trust_delta": m.score.overall - 5,  # Simplified: >5 = positive
                    "commitment_balance": {"mani": mani_count, "other": other_count},
                })

        # Determine direction
        if len(person_meetings) < 2:
            direction = TrajectoryDirection.STABLE
        else:
            recent_scores = [m["score"] for m in person_meetings[-3:]]
            if all(s > 7 for s in recent_scores):
                direction = TrajectoryDirection.RISING
            elif recent_scores[-1] < recent_scores[0]:
                direction = TrajectoryDirection.DECLINING
            else:
                direction = TrajectoryDirection.STABLE

        trajectory = RelationshipTrajectory(
            person_name=person_name,
            meetings=person_meetings,
            direction=direction,
        )

        if direction == TrajectoryDirection.DECLINING:
            trajectory.risk = "Relationship momentum declining"
            trajectory.suggested_action = "Re-engage with original pain point or share relevant content"

        return trajectory

    # ── Calendar Intelligence ────────────────────────────────────

    def get_calendar_intelligence(self) -> CalendarIntelligence:
        """Analyse meeting patterns for this week."""
        now = datetime.now()
        week_start = now - timedelta(days=now.weekday())
        week_meetings = [
            m for m in self.meetings.values()
            if week_start <= m.date <= week_start + timedelta(days=7)
        ]

        intel = CalendarIntelligence(
            meeting_count=len(week_meetings),
        )

        if len(week_meetings) > intel.avg_meetings_per_week:
            intel.pattern_insights.append(
                f"Meeting load: {len(week_meetings)} (↑ from your {intel.avg_meetings_per_week:.0f}/week average)"
            )
            intel.productivity_prediction = f"Predicted {int((len(week_meetings) / intel.avg_meetings_per_week - 1) * 20)}% lower deep work output"

        return intel

    # ── App Innovator ────────────────────────────────────────────

    def detect_innovations(self) -> list[Innovation]:
        """Detect product/service opportunities from meeting patterns."""
        innovations = []

        # Pattern: Repeated client questions
        all_hot_buttons = []
        for m in self.meetings.values():
            all_hot_buttons.extend(m.intelligence.hot_buttons)

        from collections import Counter
        common_buttons = Counter(all_hot_buttons).most_common(3)
        for button, count in common_buttons:
            if count >= 3:
                innovations.append(Innovation(
                    title=f"Product opportunity: {button}",
                    innovation_type=InnovationType.CUSTOMER_PRODUCT,
                    description=f"{count} clients mentioned '{button}' as a pain point",
                    sources={"chronicle": [f"{count} meetings referenced {button}"]},
                    recommendation="investigate",
                    confidence=min(0.9, 0.3 + count * 0.15),
                ))

        self.innovations.extend(innovations)
        return innovations

    # ── Meeting Patterns Report ──────────────────────────────────

    def get_meeting_patterns(self) -> dict:
        """Monthly meeting effectiveness report."""
        by_template = {}
        for template, scores in self._meeting_scores_by_template.items():
            by_template[template] = {
                "avg_score": round(sum(scores) / max(len(scores), 1), 1),
                "count": len(scores),
            }

        follow_through = {}
        for name, model in self.follow_through_models.items():
            follow_through[name] = {
                "rate": round(model.follow_through_rate, 2),
                "total": model.total_commitments,
                "strong_areas": model.strong_areas,
                "weak_areas": model.weak_areas,
            }

        return {
            "by_template": by_template,
            "follow_through_models": follow_through,
            "total_meetings": len(self.meetings),
            "total_commitments": sum(len(m.commitments) for m in self.meetings.values()),
            "total_decisions": sum(len(m.decisions) for m in self.meetings.values()),
            "innovations_detected": len(self.innovations),
        }

    # ── Morning Briefing Data ────────────────────────────────────

    def get_morning_briefing_data(self) -> dict:
        now = datetime.now()
        today = now.replace(hour=0, minute=0, second=0)
        tomorrow = today + timedelta(days=1)

        today_meetings = [
            m for m in self.meetings.values()
            if today <= m.date < tomorrow
        ]

        overdue = self.get_overdue_commitments()

        return {
            "meetings_today": len(today_meetings),
            "today_schedule": [
                {"title": m.title, "time": m.date.strftime("%H:%M"),
                 "template": m.template.value, "participants": [p.name for p in m.participants]}
                for m in sorted(today_meetings, key=lambda m: m.date)
            ],
            "overdue_commitments": len(overdue),
            "overdue_details": overdue[:3],
            "active_commitments": len(self.get_active_commitments(owner="mani")),
        }

    # ── Status ───────────────────────────────────────────────────

    def status(self) -> dict:
        return {
            "total_meetings": len(self.meetings),
            "active_commitments": len(self.get_active_commitments()),
            "overdue": len(self.get_overdue_commitments()),
            "follow_through_models": len(self.follow_through_models),
            "decisions_tracked": sum(len(m.decisions) for m in self.meetings.values()),
            "innovations": len(self.innovations),
        }
