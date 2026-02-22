"""Safety service - Crisis detection and grounding"""

# Crisis detection keywords (Australian resources)
CRISIS_KEYWORDS = [
    "want to die", "want to end it", "kill myself", "end my life",
    "hurt myself", "harm myself", "self harm", "suicide",
    "no point", "better off dead", "everyone would be better",
    "can't go on", "can't take anymore", "end everything",
    "permanent solution", "final answer", "nothing matters"
]

AUSTRALIAN_RESOURCES = {
    "lifeline": {
        "name": "Lifeline",
        "phone": "13 11 14",
        "available": "24 hours",
        "website": "www.lifeline.org.au"
    },
    "beyond_blue": {
        "name": "Beyond Blue",
        "phone": "1300 22 4636",
        "available": "24 hours",
        "website": "www.beyondblue.org.au"
    },
    "headspace": {
        "name": "headspace",
        "phone": "1800 650 890",
        "available": "24 hours",
        "website": "www.headspace.org.au"
    },
    "mensline": {
        "name": "MensLine Australia",
        "phone": "1300 789 978",
        "available": "24 hours",
        "website": "www.mensline.org.au"
    }
}


def check_crisis(text: str) -> dict:
    """Check text for crisis keywords and return appropriate response."""
    text_lower = text.lower()
    
    # Check for crisis keywords
    for keyword in CRISIS_KEYWORDS:
        if keyword in text_lower:
            return {
                "is_crisis": True,
                "response": "This feels like it might be bigger than a question right now. Would it help to talk to someone?",
                "resources": AUSTRALIAN_RESOURCES
            }
    
    return {"is_crisis": False}


def get_grounding_response() -> dict:
    """Get a grounding mode response."""
    return {
        "is_crisis": False,
        "is_grounding": True,
        "response": "Let's take a moment together. Breathe in slowly. Breathe out slowly. You're here. This moment is enough."
    }
