"""Socrates & Donuts Question Bank - 50+ questions tagged by framework, domain, and intensity"""

# Question bank with metadata
QUESTIONS = [
    # Stoic questions - Courage & Fear, Decisions & Uncertainty
    {
        "id": "stoic_001",
        "question": "What would the wise version of you say about this situation?",
        "framework": "stoic",
        "domain": "decisions",
        "intensity": "reflective",
        "tags": ["wisdom", "perspective", "rationality"]
    },
    {
        "id": "stoic_002",
        "question": "What is within your control, and what isn't?",
        "framework": "stoic",
        "domain": "decisions",
        "intensity": "deep",
        "tags": ["control", "acceptance", "boundaries"]
    },
    {
        "id": "stoic_003",
        "question": "How will you view this moment a year from now?",
        "framework": "stoic",
        "domain": "purpose",
        "intensity": "reflective",
        "tags": ["impermanence", "perspective", "time"]
    },
    {
        "id": "stoic_004",
        "question": "What would courage look like right now?",
        "framework": "stoic",
        "domain": "courage",
        "intensity": "confronting",
        "tags": ["courage", "action", "fear"]
    },
    {
        "id": "stoic_005",
        "question": "The obstacle is the way. What's the obstacle teaching you?",
        "framework": "stoic",
        "domain": "purpose",
        "intensity": "deep",
        "tags": ["adversity", "growth", "lessons"]
    },
    
    # Buddhist questions - Identity & Self-Knowledge, Change & Impermanence
    {
        "id": "buddhist_001",
        "question": "Where do you feel this in your body right now?",
        "framework": "buddhist",
        "domain": "body",
        "intensity": "gentle",
        "tags": ["sensation", "present-moment", "body-awareness"]
    },
    {
        "id": "buddhist_002",
        "question": "What are you clinging to that you need to release?",
        "framework": "buddhist",
        "domain": "identity",
        "intensity": "deep",
        "tags": ["attachment", "letting-go", "craving"]
    },
    {
        "id": "buddhist_003",
        "question": "This feeling you're experiencing — does it have a beginning, middle, or end?",
        "framework": "buddhist",
        "domain": "impermanence",
        "intensity": "reflective",
        "tags": ["impermanence", "emptiness", "nature-of-things"]
    },
    {
        "id": "buddhist_004",
        "question": "Who is the 'I' that's feeling this way?",
        "framework": "buddhist",
        "domain": "identity",
        "intensity": "confronting",
        "tags": ["self", "no-self", "observation"]
    },
    {
        "id": "buddhist_005",
        "question": "What would the space around this feeling look like?",
        "framework": "buddhist",
        "domain": "impermanence",
        "intensity": "reflective",
        "tags": ["awareness", "space", "observation"]
    },
    
    # Indigenous wisdom - Relationships & Connection, Joy & Gratitude
    {
        "id": "indigenous_001",
        "question": "How would your ancestors counsel you on this?",
        "framework": "indigenous",
        "domain": "relationships",
        "intensity": "reflective",
        "tags": ["ancestors", "wisdom", "lineage"]
    },
    {
        "id": "indigenous_002",
        "question": "What story are you telling yourself about this situation?",
        "framework": "indigenous",
        "domain": "belief",
        "intensity": "reflective",
        "tags": ["narrative", "story", "perception"]
    },
    {
        "id": "indigenous_003",
        "question": "What would the land teach about patience right now?",
        "framework": "indigenous",
        "domain": "purpose",
        "intensity": "gentle",
        "tags": ["nature", "patience", "cycles"]
    },
    {
        "id": "indigenous_004",
        "question": "Who in your community could you turn to for support?",
        "framework": "indigenous",
        "domain": "relationships",
        "intensity": "gentle",
        "tags": ["community", "connection", "support"]
    },
    {
        "id": "indigenous_005",
        "question": "What are you grateful for in this very moment?",
        "framework": "indigenous",
        "domain": "joy",
        "intensity": "gentle",
        "tags": ["gratitude", "presence", "appreciation"]
    },
    
    # Existentialist questions - Purpose & Meaning, Identity & Self-Knowledge
    {
        "id": "existential_001",
        "question": "If you had to choose, what would you die for?",
        "framework": "existential",
        "domain": "purpose",
        "intensity": "confronting",
        "tags": ["values", "meaning", "death"]
    },
    {
        "id": "existential_002",
        "question": "What are you doing when you lose track of time?",
        "framework": "existential",
        "domain": "purpose",
        "intensity": "reflective",
        "tags": ["flow", "meaning", "engagement"]
    },
    {
        "id": "existential_003",
        "question": "What would you do if you knew you couldn't fail?",
        "framework": "existential",
        "domain": "courage",
        "intensity": "reflective",
        "tags": ["fear", "authenticity", "possibility"]
    },
    {
        "id": "existential_004",
        "question": "Who would you be if no one was watching?",
        "framework": "existential",
        "domain": "identity",
        "intensity": "deep",
        "tags": ["authenticity", "self", "performance"]
    },
    {
        "id": "existential_005",
        "question": "What does it mean to live a good life to you?",
        "framework": "existential",
        "domain": "purpose",
        "intensity": "deep",
        "tags": ["meaning", "values", "ethics"]
    },
    
    # Taoist questions - Change & Impermanence, Anger & Frustration
    {
        "id": "taoist_001",
        "question": "What would happen if you did nothing about this?",
        "framework": "taoist",
        "domain": "decisions",
        "intensity": "reflective",
        "tags": ["wu-wei", "non-action", "surrender"]
    },
    {
        "id": "taoist_002",
        "question": "Where is the resistance pointing you?",
        "framework": "taoist",
        "domain": "anger",
        "intensity": "reflective",
        "tags": ["resistance", "flow", "direction"]
    },
    {
        "id": "taoist_003",
        "question": "What softens when you stop fighting it?",
        "framework": "taoist",
        "domain": "impermanence",
        "intensity": "reflective",
        "tags": ["softness", "acceptance", "yielding"]
    },
    {
        "id": "taoist_004",
        "question": "What is the opposite of your current struggle?",
        "framework": "taoist",
        "domain": "decisions",
        "intensity": "gentle",
        "tags": ["balance", "polarity", "perspective"]
    },
    {
        "id": "taoist_005",
        "question": "What would a river do in your situation?",
        "framework": "taoist",
        "domain": "impermanence",
        "intensity": "gentle",
        "tags": ["flow", "adaptation", "continuity"]
    },
    
    # Sufi questions - Loss & Grief, Joy & Gratitude
    {
        "id": "sufi_001",
        "question": "What are you grieving, and what is it teaching you about love?",
        "framework": "sufi",
        "domain": "grief",
        "intensity": "deep",
        "tags": ["grief", "love", "loss"]
    },
    {
        "id": "sufi_002",
        "question": "Where in your heart is the wound, and where is the door?",
        "framework": "sufi",
        "domain": "grief",
        "intensity": "confronting",
        "tags": ["heart", "wound", "healing"]
    },
    {
        "id": "sufi_003",
        "question": "What beauty have you noticed recently that others might miss?",
        "framework": "sufi",
        "domain": "joy",
        "intensity": "gentle",
        "tags": ["beauty", "attention", "wonder"]
    },
    {
        "id": "sufi_004",
        "question": "The heart has its reasons. What is your heart saying?",
        "framework": "sufi",
        "domain": "identity",
        "intensity": "reflective",
        "tags": ["heart", "intuition", "reason"]
    },
    {
        "id": "sufi_005",
        "question": "What hidden blessing might be disguised in this difficulty?",
        "framework": "sufi",
        "domain": "purpose",
        "intensity": "reflective",
        "tags": ["blessing", "hidden", "transformation"]
    },
    
    # African proverbs - Relationships & Connection, Work & Contribution
    {
        "id": "african_001",
        "question": "It takes a village. Who is in your village right now?",
        "framework": "african",
        "domain": "relationships",
        "intensity": "gentle",
        "tags": ["community", "support", "connection"]
    },
    {
        "id": "african_002",
        "question": "What are you teaching others by how you handle this?",
        "framework": "african",
        "domain": "relationships",
        "intensity": "reflective",
        "tags": ["leadership", "example", "teaching"]
    },
    {
        "id": "african_003",
        "question": "When does your work become your worship?",
        "framework": "african",
        "domain": "work",
        "intensity": "reflective",
        "tags": ["work", "service", "meaning"]
    },
    {
        "id": "african_004",
        "question": "What agreement have you made that you're now breaking?",
        "framework": "african",
        "domain": "relationships",
        "intensity": "confronting",
        "tags": ["commitment", "integrity", "word"]
    },
    {
        "id": "african_005",
        "question": "The sun also rises. What are you rising from?",
        "framework": "african",
        "domain": "impermanence",
        "intensity": "reflective",
        "tags": ["resilience", "renewal", "strength"]
    },
    
    # Secular humanist - Decisions & Uncertainty, Identity & Self-Knowledge
    {
        "id": "humanist_001",
        "question": "What evidence would change your mind about this?",
        "framework": "humanist",
        "domain": "belief",
        "intensity": "reflective",
        "tags": ["evidence", "openness", "curiosity"]
    },
    {
        "id": "humanist_002",
        "question": "How would you advise a friend in your exact situation?",
        "framework": "humanist",
        "domain": "relationships",
        "intensity": "gentle",
        "tags": ["compassion", "perspective", "advice"]
    },
    {
        "id": "humanist_003",
        "question": "What values are in conflict here?",
        "framework": "humanist",
        "domain": "decisions",
        "intensity": "deep",
        "tags": ["values", "ethics", "priorities"]
    },
    {
        "id": "humanist_004",
        "question": "What would your future self thank you for doing?",
        "framework": "humanist",
        "domain": "purpose",
        "intensity": "reflective",
        "tags": ["future", "self-compassion", "long-term"]
    },
    {
        "id": "humanist_005",
        "question": "What are you most curious about in this situation?",
        "framework": "humanist",
        "domain": "belief",
        "intensity": "gentle",
        "tags": ["curiosity", "inquiry", "learning"]
    },
    
    # General reflective questions
    {
        "id": "general_001",
        "question": "What's the hardest part of this for you?",
        "framework": "socratic",
        "domain": "general",
        "intensity": "reflective",
        "tags": ["difficulty", "challenge", "honesty"]
    },
    {
        "id": "general_002",
        "question": "What would you tell someone you love who was in your position?",
        "framework": "socratic",
        "domain": "relationships",
        "intensity": "reflective",
        "tags": ["compassion", "perspective", "love"]
    },
    {
        "id": "general_003",
        "question": "What's the story you're afraid to tell yourself?",
        "framework": "socratic",
        "domain": "identity",
        "intensity": "confronting",
        "tags": ["fear", "story", "truth"]
    },
    {
        "id": "general_004",
        "question": "What do you need that you're not giving yourself?",
        "framework": "socratic",
        "domain": "identity",
        "intensity": "reflective",
        "tags": ["needs", "self-care", "nurture"]
    },
    {
        "id": "general_005",
        "question": "What is this moment asking of you?",
        "framework": "socratic",
        "domain": "purpose",
        "intensity": "deep",
        "tags": ["presence", "call", "attention"]
    },
    {
        "id": "general_006",
        "question": "What have you been avoiding thinking about?",
        "framework": "socratic",
        "domain": "belief",
        "intensity": "confronting",
        "tags": ["avoidance", "truth", "courage"]
    },
    {
        "id": "general_007",
        "question": "What's the gift in this situation, even if it's hard to see?",
        "framework": "socratic",
        "domain": "purpose",
        "intensity": "reflective",
        "tags": ["gift", "meaning", "growth"]
    },
    {
        "id": "general_008",
        "question": "What boundary do you need to set or reinforce?",
        "framework": "socratic",
        "domain": "relationships",
        "intensity": "reflective",
        "tags": ["boundary", "limits", "self-respect"]
    },
    {
        "id": "general_009",
        "question": "What does your body need right now?",
        "framework": "socratic",
        "domain": "body",
        "intensity": "gentle",
        "tags": ["body", "needs", "rest"]
    },
    {
        "id": "general_010",
        "question": "If you were kind to yourself right now, what would that look like?",
        "framework": "socratic",
        "domain": "identity",
        "intensity": "gentle",
        "tags": ["kindness", "self-compassion", "care"]
    }
]


def get_daily_question(date: str = None, intensity: str = 'reflective', domain: str = None):
    """Get a deterministic daily question based on date."""
    from datetime import datetime
    import hashlib
    
    if date:
        try:
            dt = datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            dt = datetime.now()
    else:
        dt = datetime.now()
    
    # Create deterministic index from date
    date_str = dt.strftime('%Y%m%d')
    hash_val = int(hashlib.md5(date_str.encode()).hexdigest(), 16)
    index = hash_val % len(QUESTIONS)
    
    question = QUESTIONS[index]
    
    # Filter by intensity if specified and matches
    if intensity and intensity != 'reflective':
        # Find next matching question if this one doesn't match
        for i in range(len(QUESTIONS)):
            check_idx = (index + i) % len(QUESTIONS)
            if QUESTIONS[check_idx]['intensity'] == intensity:
                if domain is None or QUESTIONS[check_idx]['domain'] == domain:
                    question = QUESTIONS[check_idx]
                    break
    
    return question


def get_random_question(intensity: str = 'reflective', domain: str = None):
    """Get a random question filtered by intensity and domain."""
    import random
    
    filtered = QUESTIONS.copy()
    
    if intensity:
        filtered = [q for q in filtered if q['intensity'] == intensity]
    
    if domain:
        filtered = [q for q in filtered if q['domain'] == domain]
    
    if not filtered:
        # Fallback to any question
        filtered = QUESTIONS
    
    return random.choice(filtered)
