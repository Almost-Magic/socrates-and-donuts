"""
ELAINE — Embedded Wisdom Knowledge Base
Sitcom quotes, great one-liners, world culture idioms, philosophy classics.
Accessible to all AMTL apps via /api/wisdom/* endpoints.

"A little wisdom sprinkled through the day keeps the monotony at bay."

Almost Magic Tech Lab
"""

import random
from datetime import datetime

# ── Sitcom Quotes ────────────────────────────────────────────────

SITCOM_QUOTES = [
    # Seinfeld
    {"text": "It's not a lie if you believe it.", "author": "George Costanza", "source": "Seinfeld", "category": "sitcom"},
    {"text": "No soup for you!", "author": "The Soup Nazi", "source": "Seinfeld", "category": "sitcom"},
    {"text": "I'm not a businessman. I'm a business, man.", "author": "Jerry Seinfeld", "source": "Seinfeld", "category": "sitcom"},
    {"text": "These pretzels are making me thirsty.", "author": "Kramer", "source": "Seinfeld", "category": "sitcom"},
    {"text": "Serenity now!", "author": "Frank Costanza", "source": "Seinfeld", "category": "sitcom"},
    {"text": "I don't want to be a pirate!", "author": "Jerry Seinfeld", "source": "Seinfeld", "category": "sitcom"},
    {"text": "You know, we're living in a society!", "author": "George Costanza", "source": "Seinfeld", "category": "sitcom"},
    {"text": "Not that there's anything wrong with that.", "author": "Jerry & George", "source": "Seinfeld", "category": "sitcom"},
    {"text": "Yada yada yada.", "author": "Elaine Benes", "source": "Seinfeld", "category": "sitcom"},
    {"text": "I was in the pool! I was in the pool!", "author": "George Costanza", "source": "Seinfeld", "category": "sitcom"},
    # The Office
    {"text": "Would I rather be feared or loved? Easy. Both. I want people to be afraid of how much they love me.", "author": "Michael Scott", "source": "The Office", "category": "sitcom"},
    {"text": "Sometimes I'll start a sentence and I don't even know where it's going. I just hope I find it along the way.", "author": "Michael Scott", "source": "The Office", "category": "sitcom"},
    {"text": "Identity theft is not a joke, Jim! Millions of families suffer every year!", "author": "Dwight Schrute", "source": "The Office", "category": "sitcom"},
    {"text": "I'm not superstitious, but I am a little stitious.", "author": "Michael Scott", "source": "The Office", "category": "sitcom"},
    {"text": "Bears. Beets. Battlestar Galactica.", "author": "Jim Halpert", "source": "The Office", "category": "sitcom"},
    {"text": "I wish there was a way to know you're in the good old days before you've actually left them.", "author": "Andy Bernard", "source": "The Office", "category": "sitcom"},
    {"text": "There's a lot of beauty in ordinary things. Isn't that kind of the point?", "author": "Pam Beesly", "source": "The Office", "category": "sitcom"},
    {"text": "I talk a lot, so I've learned to tune myself out.", "author": "Kelly Kapoor", "source": "The Office", "category": "sitcom"},
    {"text": "The worst thing about prison was the dementors.", "author": "Michael Scott", "source": "The Office", "category": "sitcom"},
    {"text": "Why are you the way that you are?", "author": "Michael Scott", "source": "The Office", "category": "sitcom"},
    # Parks and Recreation
    {"text": "I'm a simple man. I like pretty, dark-haired women and breakfast food.", "author": "Ron Swanson", "source": "Parks and Rec", "category": "sitcom"},
    {"text": "Treat yo self!", "author": "Tom Haverford & Donna Meagle", "source": "Parks and Rec", "category": "sitcom"},
    {"text": "Everything hurts and I'm dying.", "author": "Leslie Knope", "source": "Parks and Rec", "category": "sitcom"},
    {"text": "Never half-arse two things. Whole-arse one thing.", "author": "Ron Swanson", "source": "Parks and Rec", "category": "sitcom"},
    {"text": "I once worked with a man for three years and never learned his name. Best friend I ever had.", "author": "Ron Swanson", "source": "Parks and Rec", "category": "sitcom"},
    {"text": "There has never been a sadness that can't be cured by breakfast food.", "author": "Ron Swanson", "source": "Parks and Rec", "category": "sitcom"},
    {"text": "I typed your symptoms into the thing up here, and it says you could have network connectivity problems.", "author": "Andy Dwyer", "source": "Parks and Rec", "category": "sitcom"},
    {"text": "Give a man a fish and you feed him for a day. Don't teach a man to fish and you feed yourself. He's a grown man. Fishing's not that hard.", "author": "Ron Swanson", "source": "Parks and Rec", "category": "sitcom"},
    {"text": "I have no idea what I'm doing, but I know I'm doing it really, really well.", "author": "Andy Dwyer", "source": "Parks and Rec", "category": "sitcom"},
    {"text": "We need to remember what's important in life: friends, waffles, work. Or waffles, friends, work. But work is third.", "author": "Leslie Knope", "source": "Parks and Rec", "category": "sitcom"},
]

# ── Great One-Liners ─────────────────────────────────────────────

ONE_LINERS = [
    {"text": "If you want to go fast, go alone. If you want to go far, go together.", "author": "African Proverb", "source": "proverb", "category": "one-liner"},
    {"text": "Done is better than perfect.", "author": "Sheryl Sandberg", "source": "attribution", "category": "one-liner"},
    {"text": "The best time to plant a tree was twenty years ago. The second best time is now.", "author": "Chinese Proverb", "source": "proverb", "category": "one-liner"},
    {"text": "Strong opinions, loosely held.", "author": "Paul Saffo", "source": "attribution", "category": "one-liner"},
    {"text": "Culture eats strategy for breakfast.", "author": "Peter Drucker", "source": "attribution", "category": "one-liner"},
    {"text": "Make it work, make it right, make it fast.", "author": "Kent Beck", "source": "attribution", "category": "one-liner"},
    {"text": "Perfection is achieved not when there is nothing more to add, but when there is nothing left to take away.", "author": "Antoine de Saint-Exupery", "source": "attribution", "category": "one-liner"},
    {"text": "The map is not the territory.", "author": "Alfred Korzybski", "source": "attribution", "category": "one-liner"},
    {"text": "We are what we repeatedly do. Excellence, then, is not an act, but a habit.", "author": "Aristotle (via Will Durant)", "source": "philosophy", "category": "one-liner"},
    {"text": "In the middle of difficulty lies opportunity.", "author": "Albert Einstein", "source": "attribution", "category": "one-liner"},
    {"text": "The only way to do great work is to love what you do.", "author": "Steve Jobs", "source": "attribution", "category": "one-liner"},
    {"text": "Simplicity is the ultimate sophistication.", "author": "Leonardo da Vinci", "source": "attribution", "category": "one-liner"},
    {"text": "Move fast and fix things.", "author": "Modern Tech Proverb", "source": "attribution", "category": "one-liner"},
    {"text": "Every system is perfectly designed to get the results it gets.", "author": "W. Edwards Deming", "source": "attribution", "category": "one-liner"},
    {"text": "What gets measured gets managed.", "author": "Peter Drucker", "source": "attribution", "category": "one-liner"},
    {"text": "Compound interest is the eighth wonder of the world. He who understands it, earns it. He who doesn't, pays it.", "author": "Albert Einstein", "source": "attribution", "category": "one-liner"},
    {"text": "The reasonable man adapts himself to the world; the unreasonable one persists in trying to adapt the world to himself.", "author": "George Bernard Shaw", "source": "attribution", "category": "one-liner"},
    {"text": "If you can't explain it simply, you don't understand it well enough.", "author": "Albert Einstein", "source": "attribution", "category": "one-liner"},
    {"text": "Plans are useless, but planning is indispensable.", "author": "Dwight D. Eisenhower", "source": "attribution", "category": "one-liner"},
    {"text": "The impediment to action advances action. What stands in the way becomes the way.", "author": "Marcus Aurelius", "source": "philosophy", "category": "one-liner"},
]

# ── World Culture Idioms ─────────────────────────────────────────

WORLD_IDIOMS = [
    {"text": "Fall seven times, stand up eight.", "author": "Japanese Proverb", "culture": "Japanese", "category": "idiom"},
    {"text": "A smooth sea never made a skilled sailor.", "author": "English Proverb", "culture": "English", "category": "idiom"},
    {"text": "Not my circus, not my monkeys.", "author": "Polish Proverb", "culture": "Polish", "category": "idiom"},
    {"text": "The nail that sticks out gets hammered down.", "author": "Japanese Proverb", "culture": "Japanese", "category": "idiom"},
    {"text": "When the winds of change blow, some build walls while others build windmills.", "author": "Chinese Proverb", "culture": "Chinese", "category": "idiom"},
    {"text": "You can't clap with one hand.", "author": "Arabic Proverb", "culture": "Arabic", "category": "idiom"},
    {"text": "A frog in a well does not know the great ocean.", "author": "Japanese Proverb", "culture": "Japanese", "category": "idiom"},
    {"text": "However long the night, the dawn will break.", "author": "African Proverb", "culture": "African", "category": "idiom"},
    {"text": "The axe forgets what the tree remembers.", "author": "African Proverb", "culture": "African", "category": "idiom"},
    {"text": "One who speaks does not know, one who knows does not speak.", "author": "Lao Tzu (Chinese)", "culture": "Chinese", "category": "idiom"},
    {"text": "Don't insult the alligator until you've crossed the river.", "author": "Haitian Proverb", "culture": "Haitian", "category": "idiom"},
    {"text": "A gem cannot be polished without friction, nor a person perfected without trials.", "author": "Chinese Proverb", "culture": "Chinese", "category": "idiom"},
    {"text": "She'll be right, mate.", "author": "Australian Proverb", "culture": "Australian", "category": "idiom"},
    {"text": "Fair dinkum.", "author": "Australian Idiom", "culture": "Australian", "category": "idiom"},
    {"text": "No worries.", "author": "Australian Idiom", "culture": "Australian", "category": "idiom"},
    {"text": "It's better to be a warrior in a garden than a gardener in a war.", "author": "Chinese Proverb", "culture": "Chinese", "category": "idiom"},
    {"text": "Sitting quietly, doing nothing, spring comes, and the grass grows by itself.", "author": "Zen Proverb", "culture": "Japanese", "category": "idiom"},
    {"text": "He who asks a question is a fool for five minutes. He who does not ask remains a fool forever.", "author": "Chinese Proverb", "culture": "Chinese", "category": "idiom"},
    {"text": "Knowledge without wisdom is like water in the sand.", "author": "Guinean Proverb", "culture": "African", "category": "idiom"},
    {"text": "If you want to go quickly, go alone. If you want to go far, go together.", "author": "African Proverb", "culture": "African", "category": "idiom"},
]

# ── Philosophy Classics ──────────────────────────────────────────

PHILOSOPHY = [
    {"text": "The unexamined life is not worth living.", "author": "Socrates", "source": "Apology", "category": "philosophy"},
    {"text": "I think, therefore I am.", "author": "Rene Descartes", "source": "Meditations", "category": "philosophy"},
    {"text": "He who has a why to live can bear almost any how.", "author": "Friedrich Nietzsche", "source": "Twilight of the Idols", "category": "philosophy"},
    {"text": "The only thing I know is that I know nothing.", "author": "Socrates", "source": "Plato's Dialogues", "category": "philosophy"},
    {"text": "Happiness depends upon ourselves.", "author": "Aristotle", "source": "Nicomachean Ethics", "category": "philosophy"},
    {"text": "You have power over your mind — not outside events. Realise this, and you will find strength.", "author": "Marcus Aurelius", "source": "Meditations", "category": "philosophy"},
    {"text": "To be is to be perceived.", "author": "George Berkeley", "source": "A Treatise Concerning the Principles of Human Knowledge", "category": "philosophy"},
    {"text": "Man is condemned to be free.", "author": "Jean-Paul Sartre", "source": "Existentialism Is a Humanism", "category": "philosophy"},
    {"text": "The mind is everything. What you think you become.", "author": "Buddha", "source": "Dhammapada", "category": "philosophy"},
    {"text": "One cannot step twice in the same river.", "author": "Heraclitus", "source": "Fragments", "category": "philosophy"},
    {"text": "Knowing yourself is the beginning of all wisdom.", "author": "Aristotle", "source": "attribution", "category": "philosophy"},
    {"text": "It is not death that a man should fear, but he should fear never beginning to live.", "author": "Marcus Aurelius", "source": "Meditations", "category": "philosophy"},
    {"text": "Life must be understood backwards. But it must be lived forwards.", "author": "Soren Kierkegaard", "source": "Journals", "category": "philosophy"},
    {"text": "Do not dwell in the past, do not dream of the future, concentrate the mind on the present moment.", "author": "Buddha", "source": "Dhammapada", "category": "philosophy"},
    {"text": "Whereof one cannot speak, thereof one must be silent.", "author": "Ludwig Wittgenstein", "source": "Tractatus Logico-Philosophicus", "category": "philosophy"},
]


# ── Knowledge Base Class ─────────────────────────────────────────

class WisdomKB:
    """Embedded wisdom knowledge base — no external API required.
    Serves quotes from sitcoms, one-liners, world idioms, and philosophy.
    Accessible to all AMTL apps."""

    def __init__(self):
        self.all_quotes = SITCOM_QUOTES + ONE_LINERS + WORLD_IDIOMS + PHILOSOPHY
        self._daily_cache = {}  # date → quote

    def random(self, category: str = None) -> dict:
        """Get a random quote, optionally filtered by category."""
        pool = self.all_quotes
        if category:
            pool = [q for q in pool if q.get("category") == category]
        if not pool:
            pool = self.all_quotes
        return random.choice(pool)

    def daily(self) -> dict:
        """Get the quote of the day (same quote all day, changes at midnight)."""
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self._daily_cache:
            # Use date as seed for consistent daily quote
            rng = random.Random(today)
            self._daily_cache = {today: rng.choice(self.all_quotes)}
        return self._daily_cache[today]

    def search(self, query: str, limit: int = 10) -> list[dict]:
        """Search quotes by keyword (text, author, source, culture)."""
        q = query.lower()
        results = []
        for quote in self.all_quotes:
            score = 0
            if q in quote["text"].lower():
                score += 3
            if q in quote.get("author", "").lower():
                score += 2
            if q in quote.get("source", "").lower():
                score += 1
            if q in quote.get("culture", "").lower():
                score += 1
            if score > 0:
                results.append({**quote, "_score": score})
        results.sort(key=lambda x: x["_score"], reverse=True)
        return [{k: v for k, v in r.items() if k != "_score"} for r in results[:limit]]

    def by_source(self, source: str) -> list[dict]:
        """Get all quotes from a specific source (e.g. 'Seinfeld', 'The Office')."""
        s = source.lower()
        return [q for q in self.all_quotes if s in q.get("source", "").lower()]

    def by_culture(self, culture: str) -> list[dict]:
        """Get all quotes from a specific culture."""
        c = culture.lower()
        return [q for q in self.all_quotes if c in q.get("culture", "").lower()]

    def categories(self) -> dict:
        """Return category counts."""
        counts = {}
        for q in self.all_quotes:
            cat = q.get("category", "unknown")
            counts[cat] = counts.get(cat, 0) + 1
        return counts

    def stats(self) -> dict:
        return {
            "total_quotes": len(self.all_quotes),
            "categories": self.categories(),
            "sources": list({q.get("source", "") for q in self.all_quotes if q.get("source")}),
        }
