"""
Elaine v4 — Learning Radar
Lightweight intellectual interest detection + exploration suggestions.

Not a learning platform. A Chief of Staff who pays attention to what
you're drawn to and connects the dots you haven't connected yet.

Sources:
  - Chronicle: What you reference in meetings
  - Amplifier: What themes appear in your content
  - Cartographer: Adjacent territories you keep touching
  - Constellation: Who you quote and admire

Outputs:
  - Morning briefing: "You've been drawn to X, Y, Z this week"
  - Connection suggestions: "There's a thread between these"
  - Reading/exploration prompts: "Go deeper here"

Almost Magic Tech Lab — Patentable IP
Patentable: Passive Intellectual Interest Detection from Professional Activity
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
import uuid

logger = logging.getLogger("elaine.learning_radar")


# ── Models ───────────────────────────────────────────────────────

class InterestSource(str, Enum):
    MEETING = "meeting"           # Referenced in a meeting
    CONTENT = "content"           # Appeared in content you wrote
    RESEARCH = "research"         # Cartographer discovery interaction
    CONVERSATION = "conversation" # Direct conversation with Elaine
    QUOTE = "quote"               # You quoted someone
    MANUAL = "manual"             # You explicitly said "I'm interested in X"


class InterestStrength(str, Enum):
    PASSING = "passing"       # Mentioned once
    RECURRING = "recurring"   # 2-3 mentions
    DEEPENING = "deepening"   # 4+ mentions, or asked follow-up questions
    PASSIONATE = "passionate" # Consistent over weeks, weaves into multiple contexts


@dataclass
class InterestSignal:
    """A single instance of interest detected."""
    text: str               # What was said/written
    source: InterestSource
    context: str = ""       # Meeting name, content title, etc.
    detected_at: datetime = field(default_factory=datetime.now)


@dataclass
class IntellectualInterest:
    """A tracked intellectual interest."""
    interest_id: str = ""
    topic: str = ""
    domain: str = ""        # philosophy, psychology, technology, history, etc.
    signals: list[InterestSignal] = field(default_factory=list)
    strength: InterestStrength = InterestStrength.PASSING
    first_detected: datetime = field(default_factory=datetime.now)
    last_detected: datetime = field(default_factory=datetime.now)
    connections: list[str] = field(default_factory=list)  # Related interest_ids
    suggested_reading: list[str] = field(default_factory=list)
    explored: bool = False  # Mani marked as "explored enough"

    def __post_init__(self):
        if not self.interest_id:
            self.interest_id = f"int_{uuid.uuid4().hex[:6]}"

    @property
    def mention_count(self) -> int:
        return len(self.signals)

    @property
    def days_active(self) -> int:
        return max(1, (self.last_detected - self.first_detected).days)

    @property
    def this_week(self) -> int:
        week_ago = datetime.now() - timedelta(days=7)
        return sum(1 for s in self.signals if s.detected_at > week_ago)


@dataclass
class Connection:
    """A detected connection between interests."""
    interest_ids: list[str]
    topic_names: list[str]
    thread: str             # The connecting insight
    suggested_exploration: str
    confidence: float = 0.7
    detected_at: datetime = field(default_factory=datetime.now)


# ── Seeded Knowledge (Mani's known interests) ───────────────────

SEED_INTERESTS = [
    {
        "topic": "Vipassana meditation",
        "domain": "philosophy",
        "signals": [
            InterestSignal("Long-time Vipassana practitioner", InterestSource.MANUAL, "Profile"),
        ],
        "reading": [
            "The Art of Living — William Hart (S.N. Goenka tradition)",
            "Walpola Rahula — What the Buddha Taught",
            "Bhikkhu Bodhi — In the Buddha's Words",
        ],
    },
    {
        "topic": "Stoic philosophy",
        "domain": "philosophy",
        "signals": [
            InterestSignal("References to Seneca and Marcus Aurelius in content", InterestSource.CONTENT, "LinkedIn"),
        ],
        "reading": [
            "Letters from a Stoic — Seneca",
            "Meditations — Marcus Aurelius (Hays translation)",
            "The Inner Citadel — Pierre Hadot",
        ],
    },
    {
        "topic": "Carl Jung / depth psychology",
        "domain": "psychology",
        "signals": [
            InterestSignal("Jung references in conversations", InterestSource.CONVERSATION),
        ],
        "reading": [
            "Man and His Symbols — Carl Jung (accessible entry)",
            "The Archetypes and the Collective Unconscious — Jung",
            "Owning Your Own Shadow — Robert A. Johnson",
            "Women Who Run With the Wolves — Clarissa Pinkola Estés",
        ],
    },
    {
        "topic": "Second-order thinking",
        "domain": "decision_science",
        "signals": [
            InterestSignal("Embedded in Elaine's Thinking Frameworks", InterestSource.MANUAL, "Elaine v4"),
        ],
        "reading": [
            "The Art of Thinking Clearly — Rolf Dobelli",
            "Thinking in Bets — Annie Duke",
            "Superforecasting — Philip Tetlock",
        ],
    },
    {
        "topic": "AI ethics and governance",
        "domain": "technology",
        "signals": [
            InterestSignal("Core business domain", InterestSource.MANUAL, "AMTL"),
            InterestSignal("ISO 42001 certification", InterestSource.MANUAL, "Credentials"),
        ],
        "reading": [
            "The Alignment Problem — Brian Christian",
            "Atlas of AI — Kate Crawford",
            "Weapons of Math Destruction — Cathy O'Neil",
        ],
    },
    {
        "topic": "Systems thinking",
        "domain": "decision_science",
        "signals": [
            InterestSignal("Embedded in Elaine's Thinking Frameworks", InterestSource.MANUAL, "Elaine v4"),
        ],
        "reading": [
            "Thinking in Systems — Donella Meadows",
            "The Fifth Discipline — Peter Senge",
            "Seeing the Forest for the Trees — Dennis Sherwood",
        ],
    },
    {
        "topic": "Poetry and creative writing",
        "domain": "arts",
        "signals": [
            InterestSignal("Published poet, 25+ books", InterestSource.MANUAL, "Profile"),
        ],
        "reading": [
            "The Poetry Handbook — Mary Oliver",
            "Big Magic — Elizabeth Gilbert",
            "Bird by Bird — Anne Lamott",
        ],
    },
    {
        "topic": "Rumi / Sufi poetry",
        "domain": "philosophy",
        "signals": [
            InterestSignal("Rumi references in writing", InterestSource.CONTENT, "Books"),
        ],
        "reading": [
            "The Essential Rumi — Coleman Barks translation",
            "The Book of Rumi — Rumi (Maryam Mafi translation)",
            "The Forty Rules of Love — Elif Shafak (novel)",
        ],
    },
    # Communication Frameworks
    {
        "topic": "Pyramid Principle / structured communication",
        "domain": "communication",
        "signals": [
            InterestSignal("AMTL Communication Engine", InterestSource.MANUAL, "amtl-thinking"),
        ],
        "reading": [
            "The Pyramid Principle — Barbara Minto",
            "The Minto Pyramid Principle — Logic in Writing and Thinking",
            "Say It with Charts — Gene Zelazny",
        ],
    },
    {
        "topic": "Storytelling and narrative structure",
        "domain": "communication",
        "signals": [
            InterestSignal("ABT + Story Mountain in AMTL toolkit", InterestSource.MANUAL, "amtl-thinking"),
        ],
        "reading": [
            "Houston, We Have a Narrative — Randy Olson (ABT method)",
            "Resonate — Nancy Duarte",
            "The Storyteller's Secret — Carmine Gallo",
        ],
    },
    # Strategic Frameworks
    {
        "topic": "Strategic analysis frameworks",
        "domain": "strategy",
        "signals": [
            InterestSignal("SWOT, PESTLE, BCG in AMTL toolkit", InterestSource.MANUAL, "amtl-thinking"),
        ],
        "reading": [
            "Good Strategy Bad Strategy — Richard Rumelt",
            "Playing to Win — A.G. Lafley & Roger Martin",
            "The Art of Strategy — Avinash Dixit & Barry Nalebuff",
        ],
    },
]

SEED_CONNECTIONS = [
    {
        "topics": ["Vipassana meditation", "Carl Jung / depth psychology"],
        "thread": "Both explore the unconscious mind — Vipassana through direct observation, Jung through symbolic interpretation. The shadow work in Jungian psychology parallels the equanimity practice in Vipassana.",
        "exploration": "Iain McGilchrist's 'The Master and His Emissary' bridges Eastern contemplative traditions with Western depth psychology through the lens of brain hemispheres.",
        "confidence": 0.85,
    },
    {
        "topics": ["Stoic philosophy", "Second-order thinking"],
        "thread": "The Stoic premeditation of adversity (premeditatio malorum) is essentially second-order thinking applied to life decisions. Marcus Aurelius was practicing pre-mortem analysis 2000 years ago.",
        "exploration": "Nassim Taleb's 'Antifragile' connects Stoic philosophy with modern decision science — things that gain from disorder.",
        "confidence": 0.90,
    },
    {
        "topics": ["Vipassana meditation", "Systems thinking"],
        "thread": "Vipassana teaches you to observe arising and passing of sensations without reaction. Systems thinking teaches you to observe feedback loops without premature intervention. Both are about seeing clearly before acting.",
        "exploration": "Fritjof Capra's 'The Tao of Physics' draws explicit parallels between Eastern contemplative traditions and systems science.",
        "confidence": 0.75,
    },
    {
        "topics": ["Carl Jung / depth psychology", "Poetry and creative writing"],
        "thread": "Jung saw creative expression as the psyche's way of integrating unconscious material. Your poetry practice is essentially active imagination — one of Jung's core therapeutic techniques.",
        "exploration": "James Hillman's 'The Soul's Code' bridges depth psychology and creative vocation. Also Robert Bly's 'Iron John' applies Jungian archetypes to creative life.",
        "confidence": 0.80,
    },
    {
        "topics": ["AI ethics and governance", "Stoic philosophy"],
        "thread": "The Stoic concept of 'what is in our control' maps directly to AI governance — we can't control AI development speed, but we can control our preparedness, our frameworks, our ethical stance.",
        "exploration": "Shannon Vallor's 'Technology and the Virtues' explicitly applies virtue ethics (Stoic roots) to technology governance.",
        "confidence": 0.85,
    },
    {
        "topics": ["Rumi / Sufi poetry", "Carl Jung / depth psychology"],
        "thread": "Rumi's poetry is essentially Jungian individuation expressed through metaphor. The beloved in Sufi poetry is the Self in Jungian terms — the wholeness we're journeying toward.",
        "exploration": "Robert A. Johnson's 'Ecstasy' explores the intersection of mystical experience and depth psychology.",
        "confidence": 0.80,
    },
    {
        "topics": ["Pyramid Principle / structured communication", "Second-order thinking"],
        "thread": "The Pyramid Principle forces you to state your conclusion first — but second-order thinking asks 'and then what?' Second-order on your own communication: if they accept your recommendation, what happens next? Build that into the pyramid.",
        "exploration": "Chip Heath's 'Made to Stick' bridges structured communication with cognitive impact — why some ideas survive and others die.",
        "confidence": 0.85,
    },
    {
        "topics": ["Storytelling and narrative structure", "Poetry and creative writing"],
        "thread": "ABT structure (And, But, Therefore) is the DNA of every poem you've written. The 'But' is the turn — the volta in a sonnet. You already think in narrative arcs. These frameworks just name what you do instinctively.",
        "exploration": "Robert McKee's 'Story' formalises narrative structure at the deepest level — connects creative writing instincts with persuasive communication.",
        "confidence": 0.90,
    },
    {
        "topics": ["Strategic analysis frameworks", "Systems thinking"],
        "thread": "SWOT and PESTLE give you the snapshot. Systems thinking shows you the dynamics — the feedback loops that make a strength become a weakness over time, or an opportunity create a new threat. Static analysis without dynamic thinking is dangerous.",
        "exploration": "John Sterman's 'Business Dynamics' connects strategic frameworks with systems modelling. Also Donella Meadows' 'Leverage Points' essay.",
        "confidence": 0.85,
    },
]


# ── Learning Radar Engine ────────────────────────────────────────

class LearningRadar:
    """
    Passive intellectual interest detection.
    Watches what Mani references, quotes, and explores,
    then connects the dots and suggests where to go deeper.
    """

    def __init__(self):
        self.interests: dict[str, IntellectualInterest] = {}
        self.connections: list[Connection] = []
        self._seed()

    def _seed(self):
        """Seed with Mani's known interests."""
        for seed in SEED_INTERESTS:
            interest = IntellectualInterest(
                topic=seed["topic"],
                domain=seed["domain"],
                signals=seed["signals"],
                suggested_reading=seed.get("reading", []),
            )
            interest.strength = self._calculate_strength(interest)
            self.interests[interest.interest_id] = interest

        # Seed connections
        for conn in SEED_CONNECTIONS:
            topic_ids = []
            topic_names = conn["topics"]
            for name in topic_names:
                for i in self.interests.values():
                    if i.topic == name:
                        topic_ids.append(i.interest_id)
                        break
            if len(topic_ids) >= 2:
                self.connections.append(Connection(
                    interest_ids=topic_ids,
                    topic_names=topic_names,
                    thread=conn["thread"],
                    suggested_exploration=conn["exploration"],
                    confidence=conn.get("confidence", 0.7),
                ))

    def _calculate_strength(self, interest: IntellectualInterest) -> InterestStrength:
        count = interest.mention_count
        if count >= 4:
            return InterestStrength.DEEPENING
        elif count >= 2:
            return InterestStrength.RECURRING
        return InterestStrength.PASSING

    # ── Signal Detection ─────────────────────────────────────────

    def detect_interest(self, text: str, source: InterestSource,
                         context: str = "") -> Optional[IntellectualInterest]:
        """
        Detect intellectual interests from text.
        Called by Orchestrator when meetings/content/conversations happen.
        """
        signal = InterestSignal(text=text, source=source, context=context)

        # Check against existing interests
        matched = self._match_existing(text)
        if matched:
            matched.signals.append(signal)
            matched.last_detected = datetime.now()
            matched.strength = self._calculate_strength(matched)
            logger.info(f"Interest signal: '{matched.topic}' ({matched.strength.value}) from {source.value}")
            return matched

        # Check against known topic patterns
        new_interest = self._detect_new_topic(text, signal)
        if new_interest:
            self.interests[new_interest.interest_id] = new_interest
            logger.info(f"New interest detected: '{new_interest.topic}' from {source.value}")
            return new_interest

        return None

    def _match_existing(self, text: str) -> Optional[IntellectualInterest]:
        """Match text against existing tracked interests."""
        text_lower = text.lower()
        for interest in self.interests.values():
            keywords = interest.topic.lower().split()
            # Match if 2+ significant words appear
            matches = sum(1 for w in keywords if len(w) > 3 and w in text_lower)
            if matches >= 2:
                return interest
            # Exact topic mention
            if interest.topic.lower() in text_lower:
                return interest
        return None

    # Known intellectual patterns to watch for
    TOPIC_PATTERNS = {
        "jung": ("Carl Jung / depth psychology", "psychology"),
        "archetype": ("Carl Jung / depth psychology", "psychology"),
        "shadow": ("Carl Jung / depth psychology", "psychology"),
        "vipassana": ("Vipassana meditation", "philosophy"),
        "mindfulness": ("Contemplative practice", "philosophy"),
        "meditation": ("Contemplative practice", "philosophy"),
        "stoic": ("Stoic philosophy", "philosophy"),
        "marcus aurelius": ("Stoic philosophy", "philosophy"),
        "seneca": ("Stoic philosophy", "philosophy"),
        "rumi": ("Rumi / Sufi poetry", "philosophy"),
        "sufi": ("Rumi / Sufi poetry", "philosophy"),
        "second-order": ("Second-order thinking", "decision_science"),
        "systems thinking": ("Systems thinking", "decision_science"),
        "first principles": ("First principles thinking", "decision_science"),
        "pre-mortem": ("Decision analysis", "decision_science"),
        "inversion": ("Mental models", "decision_science"),
        "kahneman": ("Behavioural economics", "psychology"),
        "taleb": ("Risk and antifragility", "decision_science"),
        "nassim": ("Risk and antifragility", "decision_science"),
        "munger": ("Mental models", "decision_science"),
        "feynman": ("First principles thinking", "science"),
        "complexity": ("Complexity science", "science"),
        "emergence": ("Complexity science", "science"),
        "wittgenstein": ("Philosophy of language", "philosophy"),
        "heidegger": ("Existential philosophy", "philosophy"),
        "nietzsche": ("Existential philosophy", "philosophy"),
        "zen": ("Zen Buddhism", "philosophy"),
        "tao": ("Taoism", "philosophy"),
        "lao tzu": ("Taoism", "philosophy"),
        "mcgilchrist": ("Hemispheric brain theory", "neuroscience"),
        "sensemaking": ("Sensemaking", "decision_science"),
        "cynefin": ("Complexity frameworks", "decision_science"),
        "wardley": ("Strategic mapping", "strategy"),
        "game theory": ("Game theory", "decision_science"),
        "network effects": ("Network theory", "technology"),
        "antifragile": ("Risk and antifragility", "decision_science"),
        # Communication frameworks
        "pyramid principle": ("Pyramid Principle / structured communication", "communication"),
        "minto": ("Pyramid Principle / structured communication", "communication"),
        "scqa": ("Pyramid Principle / structured communication", "communication"),
        "situation complication": ("Pyramid Principle / structured communication", "communication"),
        "rule of three": ("Storytelling and narrative structure", "communication"),
        "story mountain": ("Storytelling and narrative structure", "communication"),
        "narrative arc": ("Storytelling and narrative structure", "communication"),
        "and but therefore": ("Storytelling and narrative structure", "communication"),
        "signposting": ("Presentation delivery", "communication"),
        "10-20-30": ("Presentation delivery", "communication"),
        "power pause": ("Presentation delivery", "communication"),
        # Strategic frameworks
        "swot": ("Strategic analysis frameworks", "strategy"),
        "pestle": ("Strategic analysis frameworks", "strategy"),
        "mece": ("Strategic analysis frameworks", "strategy"),
        "mutually exclusive": ("Strategic analysis frameworks", "strategy"),
        "collectively exhaustive": ("Strategic analysis frameworks", "strategy"),
        "mckinsey 7s": ("Organisational analysis", "strategy"),
        "seven s": ("Organisational analysis", "strategy"),
        "bcg matrix": ("Portfolio strategy", "strategy"),
        "growth-share": ("Portfolio strategy", "strategy"),
        "ansoff": ("Growth strategy", "strategy"),
        "balanced scorecard": ("Performance management", "strategy"),
        "porter": ("Competitive strategy", "strategy"),
        "five forces": ("Competitive strategy", "strategy"),
        "blue ocean": ("Market creation strategy", "strategy"),
        "three cs": ("Strategic analysis frameworks", "strategy"),
        "okr": ("Goal-setting frameworks", "strategy"),
        "north star metric": ("Product strategy", "strategy"),
    }

    def _detect_new_topic(self, text: str, signal: InterestSignal) -> Optional[IntellectualInterest]:
        """Detect a new topic from known intellectual patterns."""
        text_lower = text.lower()
        for pattern, (topic, domain) in self.TOPIC_PATTERNS.items():
            if pattern in text_lower:
                # Check if already tracked
                existing = self._match_existing(topic)
                if existing:
                    existing.signals.append(signal)
                    existing.last_detected = datetime.now()
                    existing.strength = self._calculate_strength(existing)
                    return existing  # Return existing with new signal added
                return IntellectualInterest(
                    topic=topic,
                    domain=domain,
                    signals=[signal],
                )
        return None

    # ── Manual Interest Registration ─────────────────────────────

    def add_interest(self, topic: str, domain: str = "general",
                      reading: list[str] = None) -> IntellectualInterest:
        """Manually register an interest."""
        interest = IntellectualInterest(
            topic=topic,
            domain=domain,
            signals=[InterestSignal(topic, InterestSource.MANUAL, "Direct")],
            suggested_reading=reading or [],
        )
        self.interests[interest.interest_id] = interest
        logger.info(f"Interest added: '{topic}' ({domain})")
        return interest

    def add_connection(self, interest_ids: list[str], thread: str,
                        exploration: str) -> Optional[Connection]:
        """Manually add a connection between interests."""
        names = []
        for iid in interest_ids:
            interest = self.interests.get(iid)
            if interest:
                names.append(interest.topic)
        if len(names) < 2:
            return None
        conn = Connection(
            interest_ids=interest_ids,
            topic_names=names,
            thread=thread,
            suggested_exploration=exploration,
        )
        self.connections.append(conn)
        return conn

    # ── Morning Briefing ─────────────────────────────────────────

    def get_morning_briefing_data(self) -> dict:
        """What Elaine says about your intellectual life today."""

        # Active this week
        week_active = [i for i in self.interests.values() if i.this_week > 0]

        # Deepening interests (worth noting)
        deepening = [i for i in self.interests.values()
                     if i.strength in (InterestStrength.DEEPENING, InterestStrength.PASSIONATE)]

        # Pick a connection to surface
        surfaceable = [c for c in self.connections if c.confidence >= 0.75]
        todays_connection = surfaceable[0] if surfaceable else None

        # Reading suggestion (from deepening interest)
        reading_suggestion = None
        for interest in deepening:
            if interest.suggested_reading:
                reading_suggestion = {
                    "topic": interest.topic,
                    "book": interest.suggested_reading[0],
                }
                break

        return {
            "active_interests_this_week": len(week_active),
            "topics_this_week": [i.topic for i in week_active],
            "deepening": [{"topic": i.topic, "mentions": i.mention_count} for i in deepening[:3]],
            "connection": {
                "topics": todays_connection.topic_names,
                "thread": todays_connection.thread,
                "explore": todays_connection.suggested_exploration,
            } if todays_connection else None,
            "reading_suggestion": reading_suggestion,
        }

    def get_voice_briefing_text(self) -> str:
        """Voice-ready text for morning briefing."""
        data = self.get_morning_briefing_data()

        parts = []
        if data["active_interests_this_week"] > 0:
            topics = ", ".join(data["topics_this_week"][:3])
            parts.append(f"You've been drawn to {topics} this week.")

        if data["connection"]:
            conn = data["connection"]
            parts.append(f"There's a thread worth pulling: {conn['thread'][:120]}")
            parts.append(f"If you want to go deeper, try {conn['explore'][:100]}.")

        if data["reading_suggestion"]:
            r = data["reading_suggestion"]
            parts.append(f"On your reading radar: {r['book']}.")

        return " ".join(parts) if parts else ""

    # ── Queries ──────────────────────────────────────────────────

    def get_interests(self, domain: str = "", strength: str = "") -> list[dict]:
        """Get tracked interests with optional filters."""
        interests = list(self.interests.values())
        if domain:
            interests = [i for i in interests if i.domain == domain]
        if strength:
            interests = [i for i in interests if i.strength.value == strength]

        return [
            {
                "id": i.interest_id,
                "topic": i.topic,
                "domain": i.domain,
                "strength": i.strength.value,
                "mentions": i.mention_count,
                "this_week": i.this_week,
                "days_active": i.days_active,
                "reading": i.suggested_reading,
                "explored": i.explored,
            }
            for i in sorted(interests, key=lambda i: i.mention_count, reverse=True)
        ]

    def get_connections(self) -> list[dict]:
        return [
            {
                "topics": c.topic_names,
                "thread": c.thread,
                "exploration": c.suggested_exploration,
                "confidence": round(c.confidence, 2),
            }
            for c in sorted(self.connections, key=lambda c: c.confidence, reverse=True)
        ]

    def get_domains(self) -> dict:
        """Interests grouped by domain."""
        domains = {}
        for i in self.interests.values():
            domains.setdefault(i.domain, []).append(i.topic)
        return domains

    def status(self) -> dict:
        return {
            "interests_tracked": len(self.interests),
            "connections": len(self.connections),
            "domains": len(self.get_domains()),
            "deepening": len([i for i in self.interests.values()
                             if i.strength in (InterestStrength.DEEPENING, InterestStrength.PASSIONATE)]),
        }
