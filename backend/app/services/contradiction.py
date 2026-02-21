"""Contradiction Finder Service - Rule-based detection without AI required"""

import re

# Positive/negative sentiment word pairs for the same topic
CONTRADICTION_PATTERNS = [
    # Love/hate - work
    (r'\b(love|enjoy|appreciate|value|treasure)\b.*\b(work|job|role|career)\b',
     r'\b(hate|dread|despise|loathe|resist)\b.*\b(work|job|role|career)\b',
     'You said you {pos} your work, but expressed {neg} about it earlier.'),

    # Love/hate - relationship
    (r'\b(love|adore|cherish)\b.*\b(them|him|her|partner|friend|parent)\b',
     r'\b(hate|resent|anger|frustrated)\b.*\b(them|him|her|partner|friend|parent)\b',
     'There seems to be both warmth and frustration here.'),

    # Easy/difficult
    (r'\b(easy|simple|effortless|straightforward)\b',
     r'\b(hard|difficult|struggle|overwhelming|impossible)\b',
     'Something shifted — you described this as {pos}, then {neg}.'),

    # Happy/unhappy
    (r'\b(happy|content|satisfied|fulfilled|at peace|joy)\b',
     r'\b(unhappy|discontent|dissatisfied|empty|restless|sad|angry)\b',
     'You mentioned feeling {pos}, and also {neg}. What lives between them?'),

    # Want/don't want
    (r'\b(want|need|wish|hope|desire|crave)\b',
     r'\b(don\'t want|don\'t need|don\'t wish|avoid|reject|afraid)\b',
     "There's a tension between wanting and avoiding here."),

    # Trust/distrust
    (r'\b(trust|believe in|rely on|count on|confident)\b',
     r'\b(don\'t trust|distrust|doubt|uncertain|skeptical)\b',
     'You seem to hold both trust and doubt about this.'),

    # Can/can't
    (r'\b(can|able|capable|possible)\b',
     r"\b(can't|unable|impossible|cannot)\b",
     "There's both possibility and limitation in what you're describing."),

    # Should/shouldn't
    (r'\b(should|must|have to|need to)\b',
     r"\b(shouldn't|mustn't|don't have to|don't need to)\b",
     "You're telling yourself both what you should and shouldn't do."),

    # Will/won't
    (r'\b(will|going to|intend to)\b',
     r"\b(won't|refuse|never)\b",
     "There's both intention and resistance here."),
]


def find_contradictions_in_session(current_response: str, session_history: list = None) -> list:
    """
    Check for contradictions within this response and against past responses.
    Returns a list of gentle observations, not accusations.
    
    Args:
        current_response: The user's current response text
        session_history: Optional list of past session responses
        
    Returns:
        List of observation dictionaries with gentle prompts
    """
    observations = []
    text = current_response.lower()
    
    # Intra-session contradictions (within current response)
    for pattern_a, pattern_b, template in CONTRADICTION_PATTERNS:
        try:
            match_a = re.search(pattern_a, text, re.IGNORECASE)
            match_b = re.search(pattern_b, text, re.IGNORECASE)
            
            if match_a and match_b:
                # Extract the matched phrases for the template
                pos_phrase = match_a.group(0)
                neg_phrase = match_b.group(0)
                
                observation = {
                    'type': 'intra_session',
                    'observation': template.format(pos=pos_phrase, neg=neg_phrase),
                    'prompt': "What lives between these two things?"
                }
                observations.append(observation)
                break  # Only one intra-session observation to avoid overwhelming
        except re.error:
            continue
    
    # Cross-session contradictions (if history provided)
    if session_history and len(session_history) > 0:
        for past_session in session_history[-5:]:  # Last 5 sessions max
            past_text = (past_session.get('response_text') or '').lower()
            
            for pattern_a, pattern_b, template in CONTRADICTION_PATTERNS:
                try:
                    past_has_a = re.search(pattern_a, past_text, re.IGNORECASE)
                    current_has_b = re.search(pattern_b, text, re.IGNORECASE)
                    
                    if past_has_a and current_has_b:
                        observations.append({
                            'type': 'cross_session',
                            'observation': "You said something different about this in a past reflection.",
                            'prompt': "What's changed, or what's stayed the same?"
                        })
                        break  # One cross-session observation is enough
                except re.error:
                    continue
            
            if any(o['type'] == 'cross_session' for o in observations):
                break
    
    # Never overwhelm — max 2 observations
    return observations[:2]
