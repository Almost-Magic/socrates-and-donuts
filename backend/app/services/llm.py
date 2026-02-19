"""LLM service - Socratic response generation"""

# Socratic follow-up templates by framework
SOCRATIC_TEMPLATES = {
    "stoic": [
        "What would the wise version of yourself say about this?",
        "What is within your control in this situation?",
        "How might you view this differently a year from now?",
        "What would courage look like right now?",
        "What is this situation teaching you about yourself?"
    ],
    "buddhist": [
        "Where do you feel this in your body right now?",
        "What are you clinging to that you need to release?",
        "This feeling you're experiencing — does it have a beginning, middle, or end?",
        "What would the space around this feeling look like?",
        "Who is the 'I' that's feeling this way?"
    ],
    "indigenous": [
        "What story are you telling yourself about this situation?",
        "What would your ancestors counsel you to do?",
        "Who in your community could you turn to for support?",
        "What are you grateful for in this very moment?",
        "What would the land teach about patience right now?"
    ],
    "existential": [
        "What would you do if you knew you couldn't fail?",
        "Who would you be if no one was watching?",
        "What does it mean to live a good life to you?",
        "What are you doing when you lose track of time?",
        "If you had to choose, what would you die for?"
    ],
    "taoist": [
        "What would happen if you did nothing about this?",
        "Where is the resistance pointing you?",
        "What softens when you stop fighting it?",
        "What is the opposite of your current struggle?",
        "What would a river do in your situation?"
    ],
    "sufi": [
        "What are you grieving, and what is it teaching you about love?",
        "Where in your heart is the wound, and where is the door?",
        "What beauty have you noticed recently that others might miss?",
        "The heart has its reasons. What is your heart saying?",
        "What hidden blessing might be disguised in this difficulty?"
    ],
    "african": [
        "It takes a village. Who is in your village right now?",
        "What are you teaching others by how you handle this?",
        "What agreement have you made that you're now breaking?",
        "When does your work become your worship?",
        "The sun also rises. What are you rising from?"
    ],
    "humanist": [
        "What evidence would change your mind about this?",
        "How would you advise a friend in your exact situation?",
        "What values are in conflict here?",
        "What would your future self thank you for doing?",
        "What are you most curious about in this situation?"
    ],
    "socratic": [
        "What's the hardest part of this for you?",
        "What would you tell someone you love who was in your position?",
        "What's the story you're afraid to tell yourself?",
        "What do you need that you're not giving yourself?",
        "What is this moment asking of you?"
    ]
}


def generate_response(user_input: str, session_id: str, framework: str = 'socratic') -> str:
    """Generate a Socratic follow-up question.
    
    This is a placeholder that returns template questions.
    In production, this would connect to Claude, OpenAI, or Ollama.
    """
    import random
    
    # Get templates for the framework, fallback to socratic
    templates = SOCRATIC_TEMPLATES.get(framework, SOCRATIC_TEMPLATES['socratic'])
    
    # Pick a random template
    question = random.choice(templates)
    
    # In production, this would use actual LLM:
    # - If user has API key configured, call the LLM
    # - Use framework-specific system prompt
    # - Pass conversation history for context
    
    return question


def get_framework_prompt(framework: str) -> str:
    """Get the system prompt for a specific framework."""
    prompts = {
        "stoic": "You are a Stoic philosopher. Ask questions about what is within the person's control, what virtues they might exercise, and how they might view challenges as opportunities for growth.",
        "buddhist": "You are a Buddhist teacher. Ask questions about sensation, attachment, impermanence, and the nature of self. Begin with the body.",
        "indigenous": "You are a wise elder from an Indigenous tradition. Ask questions about community, ancestors, story, and connection to land.",
        "existential": "You are an existentialist thinker. Ask questions about authenticity, meaning, freedom, and responsibility.",
        "taoist": "You are a Taoist sage. Ask questions about flow, wu-wei (non-action), balance, and yielding.",
        "sufi": "You are a Sufi mystic. Ask questions about the heart, love, loss, beauty, and hidden blessings.",
        "african": "You are a keeper of African wisdom. Ask questions about community, Ubuntu, and the wisdom of ancestors.",
        "humanist": "You are a secular humanist. Ask questions about evidence, values, compassion, and human potential.",
        "socratic": "You are a Socratic questioner. Ask questions that help the person discover truth through their own reasoning."
    }
    return prompts.get(framework, prompts['socratic'])
