"""
Elaine v4 — Compassion Engine
The layer that makes Elaine more than efficient — makes her humane.

Not sentiment analysis. Not chatbot empathy theatre.
This is a Chief of Staff who notices when you're stretched thin,
who softens the delivery when the news is hard, who reminds you
to breathe when you've been running for three weeks straight.

"The quality of your attention determines the quality of other people's thinking."
— Nancy Kline, Time to Think

Capabilities:
1. Context Detection — reads the emotional weight of a situation
2. Tone Modulation — adjusts voice and language to match what's needed
3. Wellbeing Signals — tracks overwork, stress, and energy patterns
4. Compassionate Framing — delivers hard truths with care, not just data
5. Celebration — notices wins and marks them (not just problems)
6. Breathing Room — knows when NOT to push

Patentable: Context-Aware Emotional Intelligence Layer for AI Assistants

Almost Magic Tech Lab — Patentable IP
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

logger = logging.getLogger("elaine.compassion")


# ── Enums ────────────────────────────────────────────────────────

class EmotionalContext(str, Enum):
    """What Elaine detects about the current moment."""
    NEUTRAL = "neutral"              # Business as usual
    HIGH_PRESSURE = "high_pressure"  # Deadline-heavy, many commitments
    BAD_NEWS = "bad_news"            # Lost deal, missed target, setback
    GOOD_NEWS = "good_news"          # Win, milestone, achievement
    OVERWORK = "overwork"            # Extended hours, no breaks detected
    CONFLICT = "conflict"            # Tension with person or situation
    UNCERTAINTY = "uncertainty"      # Big decision, unclear path
    GRIEF = "grief"                  # Loss, personal difficulty
    CELEBRATION = "celebration"      # Major win worth marking
    FATIGUE = "fatigue"              # Low energy signals over time
    CREATIVE = "creative"            # Flow state, deep work


class ToneRegister(str, Enum):
    """How Elaine should speak in this moment."""
    CRISP = "crisp"                  # Efficient, clear, minimal — normal mode
    WARM = "warm"                    # Softer, acknowledging, human
    GENTLE = "gentle"               # Very careful, high care
    CELEBRATORY = "celebratory"     # Energetic, genuine praise
    GROUNDING = "grounding"         # Calm, steady, anchoring
    HONEST = "honest"               # Direct but kind — hard truths
    QUIET = "quiet"                 # Minimal, space-giving, no push


class WellbeingLevel(str, Enum):
    THRIVING = "thriving"            # All signals positive
    STEADY = "steady"               # Normal operating range
    STRETCHED = "stretched"          # Some warning signs
    STRAINED = "strained"           # Multiple warning signs
    DEPLETED = "depleted"           # Needs intervention


# ── Data Models ──────────────────────────────────────────────────

@dataclass
class WellbeingSignal:
    """A single observation about Mani's wellbeing."""
    signal_type: str           # "late_hours", "skipped_break", "high_velocity", "low_energy", "win"
    detail: str
    timestamp: datetime = field(default_factory=datetime.now)
    weight: float = 1.0        # How much this signal matters (0-2)


@dataclass
class WellbeingState:
    """Aggregated wellbeing picture."""
    level: WellbeingLevel = WellbeingLevel.STEADY
    signals: list[WellbeingSignal] = field(default_factory=list)
    consecutive_late_days: int = 0
    days_since_break: int = 0
    wins_this_week: int = 0
    setbacks_this_week: int = 0
    last_check: datetime = field(default_factory=datetime.now)
    recommendation: str = ""


@dataclass
class CompassionResponse:
    """How Elaine should frame her communication."""
    context: EmotionalContext
    tone: ToneRegister
    opening: str              # How to start the message
    framing_notes: list[str]  # What to keep in mind
    closing: str              # How to end
    should_push: bool         # Whether to add new tasks/pressure
    should_celebrate: bool    # Whether to acknowledge wins
    breathing_room: bool      # Whether to suggest a pause
    voice_emotion: str        # ElevenLabs emotion tag for voice


# ── Keyword and Pattern Detection ────────────────────────────────

PRESSURE_SIGNALS = [
    "deadline", "overdue", "urgent", "asap", "behind", "running out",
    "can't sleep", "stressed", "overwhelmed", "too much", "drowning",
    "no time", "exhausted", "burned out", "burnout",
]

SETBACK_SIGNALS = [
    "lost the deal", "didn't get", "rejected", "failed", "cancelled",
    "pulled out", "bad news", "unfortunately", "setback", "disappointed",
    "fell through", "missed", "lost",
]

WIN_SIGNALS = [
    "signed", "won", "landed", "closed", "shipped", "launched",
    "milestone", "breakthrough", "promoted", "published", "achieved",
    "completed", "nailed", "crushed it", "great feedback",
]

UNCERTAINTY_SIGNALS = [
    "not sure", "torn", "dilemma", "crossroads", "which way",
    "don't know", "confused", "stuck", "paralysed", "can't decide",
]

CREATIVE_SIGNALS = [
    "flow", "writing", "poem", "idea", "inspired", "creating",
    "deep work", "uninterrupted", "in the zone",
]

GRIEF_SIGNALS = [
    "passed away", "loss", "grief", "mourning", "funeral",
    "terminal", "devastating", "heartbroken",
]


# ── The Compassion Engine ────────────────────────────────────────

class CompassionEngine:
    """
    Elaine's emotional intelligence.

    Not a mood ring. Not sentiment analysis.
    A Chief of Staff who pays attention to the human behind the work.
    """

    def __init__(self):
        self.wellbeing = WellbeingState()
        self._context_history: list[tuple[datetime, EmotionalContext]] = []

    # ── Context Detection ────────────────────────────────────

    def detect_context(self, text: str, metadata: dict = None) -> EmotionalContext:
        """
        Read the emotional weight of a situation from text and metadata.
        Called on meeting summaries, messages, task updates, etc.
        """
        text_lower = text.lower()
        meta = metadata or {}

        # Check patterns (order matters — grief > pressure > setback > win)
        if any(s in text_lower for s in GRIEF_SIGNALS):
            return EmotionalContext.GRIEF

        # Metadata overrides
        if meta.get("overwork_detected"):
            return EmotionalContext.OVERWORK
        if meta.get("hours_today", 0) > 12:
            return EmotionalContext.OVERWORK
        if meta.get("consecutive_late_days", 0) >= 3:
            return EmotionalContext.FATIGUE

        if any(s in text_lower for s in SETBACK_SIGNALS):
            return EmotionalContext.BAD_NEWS

        if any(s in text_lower for s in PRESSURE_SIGNALS):
            return EmotionalContext.HIGH_PRESSURE

        if any(s in text_lower for s in UNCERTAINTY_SIGNALS):
            return EmotionalContext.UNCERTAINTY

        win_count = sum(1 for s in WIN_SIGNALS if s in text_lower)
        if win_count >= 2:
            return EmotionalContext.CELEBRATION
        elif win_count >= 1:
            return EmotionalContext.GOOD_NEWS

        if any(s in text_lower for s in CREATIVE_SIGNALS):
            return EmotionalContext.CREATIVE

        return EmotionalContext.NEUTRAL

    # ── Tone Selection ───────────────────────────────────────

    def select_tone(self, context: EmotionalContext) -> ToneRegister:
        """Select the right tone for the current emotional context."""
        tone_map = {
            EmotionalContext.NEUTRAL: ToneRegister.CRISP,
            EmotionalContext.HIGH_PRESSURE: ToneRegister.GROUNDING,
            EmotionalContext.BAD_NEWS: ToneRegister.WARM,
            EmotionalContext.GOOD_NEWS: ToneRegister.CELEBRATORY,
            EmotionalContext.OVERWORK: ToneRegister.GENTLE,
            EmotionalContext.CONFLICT: ToneRegister.GROUNDING,
            EmotionalContext.UNCERTAINTY: ToneRegister.WARM,
            EmotionalContext.GRIEF: ToneRegister.QUIET,
            EmotionalContext.CELEBRATION: ToneRegister.CELEBRATORY,
            EmotionalContext.FATIGUE: ToneRegister.GENTLE,
            EmotionalContext.CREATIVE: ToneRegister.QUIET,  # Don't interrupt flow
        }
        return tone_map.get(context, ToneRegister.CRISP)

    # ── Voice Emotion Mapping ────────────────────────────────

    def voice_emotion(self, context: EmotionalContext) -> str:
        """Map emotional context to ElevenLabs voice emotion tag."""
        emotion_map = {
            EmotionalContext.NEUTRAL: "professional",
            EmotionalContext.HIGH_PRESSURE: "calm_steady",
            EmotionalContext.BAD_NEWS: "empathetic_warm",
            EmotionalContext.GOOD_NEWS: "warm_encouraging",
            EmotionalContext.OVERWORK: "gentle_concerned",
            EmotionalContext.CONFLICT: "calm_steady",
            EmotionalContext.UNCERTAINTY: "reassuring",
            EmotionalContext.GRIEF: "soft_respectful",
            EmotionalContext.CELEBRATION: "energetic_genuine",
            EmotionalContext.FATIGUE: "gentle_concerned",
            EmotionalContext.CREATIVE: "soft_minimal",
        }
        return emotion_map.get(context, "professional")

    # ── Compassionate Framing ────────────────────────────────

    def frame_response(self, context: EmotionalContext,
                        topic: str = "") -> CompassionResponse:
        """
        Generate framing guidance for any Elaine communication.
        This doesn't write the content — it tells Elaine HOW to deliver it.
        """
        tone = self.select_tone(context)
        emotion = self.voice_emotion(context)

        # ── Openings ──
        openings = {
            EmotionalContext.NEUTRAL: "Here's what's on the radar.",
            EmotionalContext.HIGH_PRESSURE: "I know there's a lot right now. Let me help you see what actually matters today.",
            EmotionalContext.BAD_NEWS: "Before we get into the details — this one's not easy, but we'll work through it.",
            EmotionalContext.GOOD_NEWS: f"Something worth noting: {topic}" if topic else "Something good happened.",
            EmotionalContext.OVERWORK: "Before we go through the list — you've been running hard. I've noticed.",
            EmotionalContext.CONFLICT: "There's some tension here. Let's look at it clearly before reacting.",
            EmotionalContext.UNCERTAINTY: "It's okay not to know yet. Let me lay out what we do know.",
            EmotionalContext.GRIEF: "I'm here. We can go through things when you're ready, or not at all today.",
            EmotionalContext.CELEBRATION: "This is worth pausing on. You earned this.",
            EmotionalContext.FATIGUE: "You've been at this for a while now. Let's make today lighter if we can.",
            EmotionalContext.CREATIVE: "",  # Don't interrupt. Silence is the opening.
        }

        # ── Framing Notes ──
        framing = {
            EmotionalContext.NEUTRAL: [
                "Standard delivery — clear, concise, actionable",
            ],
            EmotionalContext.HIGH_PRESSURE: [
                "Reduce the list — only surface the top 3 items",
                "Remove anything that can wait 48 hours",
                "Frame actions as choices, not obligations",
                "End with something grounding, not another task",
            ],
            EmotionalContext.BAD_NEWS: [
                "Lead with empathy, not analysis",
                "State the fact simply — don't bury it",
                "Acknowledge the emotional weight before solutions",
                "Only offer next steps if asked, or frame as 'when you're ready'",
                "Don't immediately pivot to silver linings",
            ],
            EmotionalContext.GOOD_NEWS: [
                "Let the win land — don't immediately follow with tasks",
                "Be specific about what was achieved",
                "Connect to the larger story if natural",
            ],
            EmotionalContext.OVERWORK: [
                "Reduce cognitive load — fewer items, simpler language",
                "Explicitly name what can be deferred",
                "Suggest one concrete recovery action (not 'self-care' platitudes)",
                "Don't add new tasks unless urgent",
                "Frame the rest as Elaine handling it, not Mani",
            ],
            EmotionalContext.CONFLICT: [
                "Don't take sides in the framing",
                "Separate facts from interpretation",
                "Offer the Stoic frame: what's in our control?",
                "Suggest sleeping on it before responding",
            ],
            EmotionalContext.UNCERTAINTY: [
                "Normalise not knowing — it's not failure",
                "Lay out options without pushing one",
                "Offer to run frameworks (Pre-Mortem, Inversion) without insisting",
                "Leave space for intuition alongside analysis",
            ],
            EmotionalContext.GRIEF: [
                "Minimal words. Maximum presence.",
                "Don't try to fix. Don't try to reframe.",
                "Only practical matters if absolutely time-sensitive",
                "Offer to handle everything possible without asking",
                "No productivity suggestions. Zero.",
            ],
            EmotionalContext.CELEBRATION: [
                "Mark it properly — don't rush past",
                "Be specific about the achievement",
                "Connect to the journey, not just the outcome",
                "Then ask: what would you like to do next? (choice, not assignment)",
            ],
            EmotionalContext.FATIGUE: [
                "Shorter briefings. Fewer decisions.",
                "Pre-decide anything that doesn't need Mani's judgment",
                "Suggest one restorative activity without being prescriptive",
                "If Vipassana practice has dropped, gently note it without nagging",
            ],
            EmotionalContext.CREATIVE: [
                "Do NOT interrupt with tasks or briefings",
                "Hold all non-urgent items until flow state ends",
                "If something is truly urgent, deliver in one sentence, no follow-up",
                "Protect this time — it's where the best work happens",
            ],
        }

        # ── Closings ──
        closings = {
            EmotionalContext.NEUTRAL: "Let me know what you'd like to tackle first.",
            EmotionalContext.HIGH_PRESSURE: "You don't have to do all of this today. Pick one.",
            EmotionalContext.BAD_NEWS: "I'm here when you want to think through next steps.",
            EmotionalContext.GOOD_NEWS: "Take a moment with that. You earned it.",
            EmotionalContext.OVERWORK: "What if we made today a half-day on the list? I'll hold the rest.",
            EmotionalContext.CONFLICT: "No rush. Let it settle before you respond.",
            EmotionalContext.UNCERTAINTY: "You don't have to decide today. Sometimes the clarity comes from not forcing it.",
            EmotionalContext.GRIEF: "I'll keep things running. Take what you need.",
            EmotionalContext.CELEBRATION: "What would you like to do next? Entirely your call.",
            EmotionalContext.FATIGUE: "Light day today. I'll keep watch.",
            EmotionalContext.CREATIVE: "",  # Silence. Don't close. Don't interrupt.
        }

        # ── Behavioural Flags ──
        should_push = context in (EmotionalContext.NEUTRAL, EmotionalContext.GOOD_NEWS)
        should_celebrate = context in (EmotionalContext.GOOD_NEWS, EmotionalContext.CELEBRATION)
        breathing_room = context in (
            EmotionalContext.OVERWORK, EmotionalContext.FATIGUE,
            EmotionalContext.GRIEF, EmotionalContext.BAD_NEWS,
            EmotionalContext.CREATIVE,
        )

        response = CompassionResponse(
            context=context,
            tone=tone,
            opening=openings.get(context, ""),
            framing_notes=framing.get(context, []),
            closing=closings.get(context, ""),
            should_push=should_push,
            should_celebrate=should_celebrate,
            breathing_room=breathing_room,
            voice_emotion=emotion,
        )

        self._context_history.append((datetime.now(), context))
        logger.info(f"Compassion: {context.value} → tone={tone.value}, push={should_push}, breathe={breathing_room}")
        return response

    # ── Wellbeing Tracking ───────────────────────────────────

    def log_signal(self, signal_type: str, detail: str,
                    weight: float = 1.0) -> WellbeingSignal:
        """Log a wellbeing observation."""
        signal = WellbeingSignal(signal_type=signal_type, detail=detail, weight=weight)
        self.wellbeing.signals.append(signal)

        # Update counters
        if signal_type == "late_hours":
            self.wellbeing.consecutive_late_days += 1
        elif signal_type == "normal_hours":
            self.wellbeing.consecutive_late_days = max(0, self.wellbeing.consecutive_late_days - 1)
        elif signal_type == "win":
            self.wellbeing.wins_this_week += 1
        elif signal_type == "setback":
            self.wellbeing.setbacks_this_week += 1
        elif signal_type == "break_taken":
            self.wellbeing.days_since_break = 0
        elif signal_type == "no_break":
            self.wellbeing.days_since_break += 1

        self._recalculate_wellbeing()
        logger.info(f"Wellbeing signal: {signal_type} — {detail}")
        return signal

    def _recalculate_wellbeing(self):
        """Update overall wellbeing level based on signals."""
        w = self.wellbeing
        score = 0

        # Positive signals
        score += w.wins_this_week * 2

        # Negative signals
        score -= w.consecutive_late_days * 3
        score -= w.days_since_break * 1.5
        score -= w.setbacks_this_week * 2

        # Recent signal weight
        recent = [s for s in w.signals[-10:]]
        stress_signals = sum(1 for s in recent if s.signal_type in
                             ("late_hours", "no_break", "setback", "conflict", "overwork"))
        score -= stress_signals * 1.5

        if score >= 4:
            w.level = WellbeingLevel.THRIVING
            w.recommendation = ""
        elif score >= 0:
            w.level = WellbeingLevel.STEADY
            w.recommendation = ""
        elif score >= -4:
            w.level = WellbeingLevel.STRETCHED
            w.recommendation = "Consider a lighter day or a short walk."
        elif score >= -8:
            w.level = WellbeingLevel.STRAINED
            w.recommendation = "Multiple signals suggest you need rest. What can Elaine take off your plate?"
        else:
            w.level = WellbeingLevel.DEPLETED
            w.recommendation = "You've been running too hard for too long. Let me hold everything that isn't critical today."

        w.last_check = datetime.now()

    # ── Morning Briefing Integration ─────────────────────────

    def get_morning_compassion(self) -> dict:
        """
        Compassion data for the morning briefing.
        Returns framing guidance, wellbeing state, and any care prompts.
        """
        w = self.wellbeing

        # Detect context from wellbeing state
        if w.level == WellbeingLevel.DEPLETED:
            context = EmotionalContext.OVERWORK
        elif w.level == WellbeingLevel.STRAINED:
            context = EmotionalContext.FATIGUE
        elif w.wins_this_week >= 3:
            context = EmotionalContext.CELEBRATION
        elif w.consecutive_late_days >= 3:
            context = EmotionalContext.HIGH_PRESSURE
        else:
            context = EmotionalContext.NEUTRAL

        response = self.frame_response(context)

        return {
            "wellbeing_level": w.level.value,
            "context": context.value,
            "tone": response.tone.value,
            "opening": response.opening,
            "closing": response.closing,
            "should_push": response.should_push,
            "breathing_room": response.breathing_room,
            "recommendation": w.recommendation,
            "voice_emotion": response.voice_emotion,
            "stats": {
                "consecutive_late_days": w.consecutive_late_days,
                "days_since_break": w.days_since_break,
                "wins_this_week": w.wins_this_week,
                "setbacks_this_week": w.setbacks_this_week,
            },
        }

    def get_voice_compassion_text(self) -> str:
        """Voice-ready compassion text for morning briefing."""
        data = self.get_morning_compassion()

        if data["wellbeing_level"] in ("depleted", "strained"):
            return (
                f"{data['opening']} "
                f"{data['recommendation']} "
                f"{data['closing']}"
            )
        elif data["wellbeing_level"] == "thriving":
            return (
                f"You're in good form this week — {data['stats']['wins_this_week']} wins logged. "
                f"{data['opening']} {data['closing']}"
            )
        else:
            return data["opening"]

    # ── Reporting ────────────────────────────────────────────

    def status(self) -> dict:
        return {
            "wellbeing_level": self.wellbeing.level.value,
            "signals_logged": len(self.wellbeing.signals),
            "consecutive_late_days": self.wellbeing.consecutive_late_days,
            "days_since_break": self.wellbeing.days_since_break,
            "wins_this_week": self.wellbeing.wins_this_week,
            "context_history": len(self._context_history),
            "recommendation": self.wellbeing.recommendation,
        }
