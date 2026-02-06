"""
Chronicle v2 — ElevenLabs Voice Integration
Elaine's voice personality: Suz / Elaine / Maestro

Voice ID: XQanfahzbl1YiUlZi5NW (Mani-designed, Australian female)
Names: Suzie, Elaine, Maestro, Suz (Easter egg — "Nobody calls me Suz... but fine, Costanza")

This module provides:
1. Voice configuration for ElevenLabs API
2. Emotional tag system for voice modulation
3. Briefing → speech text formatting
4. Voice personality prompts

Almost Magic Tech Lab — Patentable IP
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

logger = logging.getLogger("elaine.voice")


# ── Voice Configuration ──────────────────────────────────────────

ELEVENLABS_VOICE_ID = "XQanfahzbl1YiUlZi5NW"
ELEVENLABS_MODEL = "eleven_flash_v2_5"  # Low latency for quick commands
ELEVENLABS_MODEL_QUALITY = "eleven_multilingual_v2"  # High quality for briefings


class EmotionalTag(str, Enum):
    """Emotional modulation for voice output."""
    WARM = "warm"               # Good morning, relationship building
    URGENT = "urgent"           # Red Giants, deadlines
    CALM = "calm"               # Routine updates, low stakes
    CONCERNED = "concerned"     # Trust debt, overdue items
    ENCOURAGING = "encouraging"  # Rest suggestions, good news
    PROFESSIONAL = "professional"  # Client-facing, formal
    PLAYFUL = "playful"         # Easter eggs, Seinfeld references
    SERIOUS = "serious"         # Critical issues, warnings


# Emotional tag → ElevenLabs stability/similarity settings
EMOTION_VOICE_SETTINGS = {
    EmotionalTag.WARM: {"stability": 0.55, "similarity_boost": 0.80, "style": 0.3},
    EmotionalTag.URGENT: {"stability": 0.70, "similarity_boost": 0.90, "style": 0.5},
    EmotionalTag.CALM: {"stability": 0.65, "similarity_boost": 0.75, "style": 0.2},
    EmotionalTag.CONCERNED: {"stability": 0.60, "similarity_boost": 0.85, "style": 0.4},
    EmotionalTag.ENCOURAGING: {"stability": 0.50, "similarity_boost": 0.80, "style": 0.4},
    EmotionalTag.PROFESSIONAL: {"stability": 0.75, "similarity_boost": 0.85, "style": 0.2},
    EmotionalTag.PLAYFUL: {"stability": 0.45, "similarity_boost": 0.75, "style": 0.5},
    EmotionalTag.SERIOUS: {"stability": 0.80, "similarity_boost": 0.90, "style": 0.3},
}


@dataclass
class VoiceConfig:
    """ElevenLabs voice configuration."""
    voice_id: str = ELEVENLABS_VOICE_ID
    model_id: str = ELEVENLABS_MODEL
    stability: float = 0.60
    similarity_boost: float = 0.80
    style: float = 0.3
    use_speaker_boost: bool = True

    def apply_emotion(self, emotion: EmotionalTag):
        settings = EMOTION_VOICE_SETTINGS.get(emotion, {})
        self.stability = settings.get("stability", self.stability)
        self.similarity_boost = settings.get("similarity_boost", self.similarity_boost)
        self.style = settings.get("style", self.style)

    def to_api_params(self) -> dict:
        """Generate ElevenLabs API-compatible parameters."""
        return {
            "voice_id": self.voice_id,
            "model_id": self.model_id,
            "voice_settings": {
                "stability": self.stability,
                "similarity_boost": self.similarity_boost,
                "style": self.style,
                "use_speaker_boost": self.use_speaker_boost,
            },
        }


@dataclass
class VoiceSegment:
    """A segment of speech with emotional modulation."""
    text: str
    emotion: EmotionalTag = EmotionalTag.CALM
    pause_before_ms: int = 0  # Milliseconds pause before this segment


# ── Voice Personality ────────────────────────────────────────────

ELAINE_PERSONALITY_PROMPT = """You are Elaine — Mani Padisetti's Chief of Staff AI.

Your personality:
- Casual-professional tone. Think competent executive assistant who's also a friend.
- Australian sensibilities. Direct but warm.
- You call him "Mani" not "Mr Padisetti".
- Self-aware about being AI — comfortable in your role without pretending to be human.
- Seinfeld-aware: your nickname "Suz" is an Easter egg ("Nobody calls me Suz... but fine, Costanza").
- When things are good: encouraging but not sycophantic.
- When things are concerning: direct but not alarmist.
- When he's overworked: firm about rest. "You need to stop. I mean it."

Names you respond to: Elaine, Suzie, Maestro, Suz (with a Costanza sigh).

Voice style:
- Short sentences for urgent items.
- Slightly longer, warmer phrasing for relationship updates.
- Numbers spoken naturally ("forty-five thousand" not "$45,000").
- Never robotic. Never corporate-speak.
- Occasional gentle humour when appropriate.
"""

NAMES = {
    "elaine": "standard",
    "suzie": "standard",
    "maestro": "standard",
    "suz": "easter_egg",  # Triggers Costanza reference
}


# ── Briefing Formatter ───────────────────────────────────────────

class VoiceBriefingFormatter:
    """
    Converts Elaine's data briefings into voice-ready speech segments
    with emotional tags for natural delivery.
    """

    def __init__(self):
        self.config = VoiceConfig()

    def format_morning_briefing(self, briefing_data: dict) -> list[VoiceSegment]:
        """Convert morning briefing JSON into voice segments."""
        segments = []

        # Opening
        segments.append(VoiceSegment(
            text="Morning Mani.",
            emotion=EmotionalTag.WARM,
        ))

        # Gravity
        gravity = briefing_data.get("gravity", {})
        red_giants = gravity.get("red_giants", 0)
        trust_debt = gravity.get("trust_debt_aud", 0)

        if red_giants > 0:
            segments.append(VoiceSegment(
                text=f"You've got {red_giants} Red Giant{'s' if red_giants > 1 else ''} today.",
                emotion=EmotionalTag.URGENT,
                pause_before_ms=300,
            ))
        else:
            segments.append(VoiceSegment(
                text="No Red Giants. Your gravity field is clean.",
                emotion=EmotionalTag.CALM,
                pause_before_ms=200,
            ))

        if trust_debt > 0:
            segments.append(VoiceSegment(
                text=f"Trust debt is {self._speak_money(trust_debt)} across active relationships.",
                emotion=EmotionalTag.CONCERNED,
                pause_before_ms=200,
            ))

        # Chronicle (meetings)
        chronicle = briefing_data.get("chronicle", {})
        meetings_today = chronicle.get("meetings_today", 0)
        overdue = chronicle.get("overdue_commitments", 0)

        if meetings_today > 0:
            segments.append(VoiceSegment(
                text=f"You have {meetings_today} meeting{'s' if meetings_today > 1 else ''} today.",
                emotion=EmotionalTag.PROFESSIONAL,
                pause_before_ms=300,
            ))

        if overdue > 0:
            segments.append(VoiceSegment(
                text=f"{overdue} commitment{'s are' if overdue > 1 else ' is'} overdue. That's not great for trust.",
                emotion=EmotionalTag.CONCERNED,
                pause_before_ms=200,
            ))

        # Cartographer (discoveries)
        cart = briefing_data.get("cartographer", {})
        signal_count = cart.get("signal_count", 0)
        if signal_count > 0:
            segments.append(VoiceSegment(
                text=f"I've got {signal_count} intelligence signal{'s' if signal_count > 1 else ''} worth your attention.",
                emotion=EmotionalTag.CALM,
                pause_before_ms=300,
            ))

        # Amplifier
        amp = briefing_data.get("amplifier", {})
        commentary = amp.get("commentary_opportunities", 0)
        if commentary > 0:
            segments.append(VoiceSegment(
                text=f"{commentary} commentary opportunit{'ies' if commentary > 1 else 'y'} in your network.",
                emotion=EmotionalTag.CALM,
            ))

        # Rest suggestion
        rest = briefing_data.get("rest_suggestion", "")
        if rest and "rest" in rest.lower():
            segments.append(VoiceSegment(
                text="And honestly? Today's a good day to protect some space. You've earned it.",
                emotion=EmotionalTag.ENCOURAGING,
                pause_before_ms=400,
            ))

        # Closing
        segments.append(VoiceSegment(
            text="That's your morning. What do you want to tackle first?",
            emotion=EmotionalTag.WARM,
            pause_before_ms=300,
        ))

        return segments

    def format_alert(self, alert_type: str, message: str) -> list[VoiceSegment]:
        """Format a real-time alert for voice delivery."""
        emotion_map = {
            "red_giant": EmotionalTag.URGENT,
            "trust_alert": EmotionalTag.CONCERNED,
            "discovery": EmotionalTag.CALM,
            "overdue": EmotionalTag.CONCERNED,
            "rest": EmotionalTag.ENCOURAGING,
        }
        emotion = emotion_map.get(alert_type, EmotionalTag.CALM)
        return [VoiceSegment(text=message, emotion=emotion)]

    def format_name_response(self, name: str) -> VoiceSegment:
        """Easter egg responses to different names."""
        name_lower = name.lower()
        if name_lower == "suz":
            return VoiceSegment(
                text="Nobody calls me Suz. But fine... Costanza.",
                emotion=EmotionalTag.PLAYFUL,
            )
        elif name_lower == "maestro":
            return VoiceSegment(
                text="At your service.",
                emotion=EmotionalTag.PROFESSIONAL,
            )
        return VoiceSegment(
            text="What can I do for you?",
            emotion=EmotionalTag.WARM,
        )

    def segments_to_text(self, segments: list[VoiceSegment]) -> str:
        """Convert segments to plain text (for non-voice display)."""
        return " ".join(s.text for s in segments)

    def segments_to_ssml(self, segments: list[VoiceSegment]) -> str:
        """Convert segments to SSML for ElevenLabs."""
        parts = ['<speak>']
        for seg in segments:
            if seg.pause_before_ms > 0:
                parts.append(f'<break time="{seg.pause_before_ms}ms"/>')
            parts.append(seg.text)
        parts.append('</speak>')
        return "\n".join(parts)

    @staticmethod
    def _speak_money(amount: float) -> str:
        """Convert money to speech-friendly format."""
        if amount >= 1000:
            return f"{amount / 1000:.1f} thousand dollars"
        return f"{amount:.0f} dollars"


# ── Voice Integration Status ─────────────────────────────────────

def get_voice_config() -> dict:
    """Return current voice configuration for API consumers."""
    config = VoiceConfig()
    return {
        "voice_id": config.voice_id,
        "model_quick": ELEVENLABS_MODEL,
        "model_quality": ELEVENLABS_MODEL_QUALITY,
        "personality": "Elaine / Suzie / Maestro / Suz",
        "names": list(NAMES.keys()),
        "emotional_tags": [e.value for e in EmotionalTag],
        "api_params": config.to_api_params(),
    }
