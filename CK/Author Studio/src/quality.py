"""
Author Studio - Quality Checker
Plagiarism detection and AI-generated text identification
"""

import re
from typing import Dict, List, Tuple
from collections import Counter
import hashlib


class PlagiarismChecker:
    """
    Checks for potential plagiarism by analyzing text patterns.
    Note: This is a local heuristic checker. For thorough plagiarism detection,
    use services like Copyscape, Turnitin, or Grammarly.
    """
    
    # Common phrases that are often plagiarized or clichéd
    COMMON_CLICHES = [
        "at the end of the day",
        "think outside the box",
        "game changer",
        "paradigm shift",
        "low hanging fruit",
        "move the needle",
        "circle back",
        "deep dive",
        "synergy",
        "leverage",
        "best practices",
        "value proposition",
        "win-win",
        "take it to the next level",
        "push the envelope",
        "on the same page",
        "touch base",
        "bandwidth",
        "actionable insights",
        "thought leader",
    ]
    
    # Phrases that suggest copied content
    CITATION_INDICATORS = [
        "according to",
        "studies show",
        "research indicates",
        "as stated by",
        "in the words of",
        "to quote",
        "as mentioned in",
        "as described by",
    ]
    
    @staticmethod
    def analyze(text: str) -> Dict:
        """
        Analyze text for potential plagiarism indicators.
        
        Returns:
            Dict with analysis results and suggestions
        """
        results = {
            'risk_level': 'low',
            'risk_score': 0,
            'issues': [],
            'cliches_found': [],
            'uncited_claims': [],
            'suggestions': [],
            'fingerprint': None
        }
        
        words = text.lower().split()
        total_words = len(words)
        
        if total_words < 50:
            return results
        
        # Check for clichés
        text_lower = text.lower()
        for cliche in PlagiarismChecker.COMMON_CLICHES:
            count = text_lower.count(cliche)
            if count > 0:
                results['cliches_found'].append({
                    'phrase': cliche,
                    'count': count,
                    'suggestion': f"Consider replacing '{cliche}' with more original language"
                })
                results['risk_score'] += count * 2
        
        # Check for uncited claims
        sentences = re.split(r'[.!?]+', text)
        claim_patterns = [
            r'studies show',
            r'research proves',
            r'scientists believe',
            r'experts agree',
            r'statistics indicate',
            r'\d+%\s+of\s+people',
            r'most people',
            r'everyone knows',
        ]
        
        for sentence in sentences:
            sentence_lower = sentence.lower().strip()
            for pattern in claim_patterns:
                if re.search(pattern, sentence_lower):
                    # Check if there's a citation nearby
                    has_citation = any(ind in sentence_lower for ind in ['cited', 'source', 'reference', '(', '['])
                    if not has_citation:
                        results['uncited_claims'].append({
                            'sentence': sentence.strip()[:100] + '...' if len(sentence) > 100 else sentence.strip(),
                            'suggestion': 'Add a citation or source for this claim'
                        })
                        results['risk_score'] += 5
        
        # Check for unusual vocabulary consistency (might indicate copied sections)
        # Calculate vocabulary richness
        unique_words = set(words)
        vocab_richness = len(unique_words) / total_words
        
        if vocab_richness < 0.3:
            results['issues'].append({
                'type': 'low_vocabulary_diversity',
                'message': 'Low vocabulary diversity detected - text may be repetitive',
                'score': vocab_richness
            })
            results['risk_score'] += 10
        
        # Generate text fingerprint for comparison
        results['fingerprint'] = PlagiarismChecker._generate_fingerprint(text)
        
        # Determine risk level
        if results['risk_score'] > 30:
            results['risk_level'] = 'high'
            results['suggestions'].append("Consider reviewing flagged sections for originality")
            results['suggestions'].append("Use a professional plagiarism checker like Copyscape or Grammarly")
        elif results['risk_score'] > 15:
            results['risk_level'] = 'medium'
            results['suggestions'].append("Review and rephrase clichéd phrases")
            results['suggestions'].append("Add citations for factual claims")
        else:
            results['risk_level'] = 'low'
            results['suggestions'].append("Text appears original - good job!")
        
        return results
    
    @staticmethod
    def _generate_fingerprint(text: str) -> str:
        """Generate a fingerprint hash for the text."""
        # Normalize text
        normalized = re.sub(r'\s+', ' ', text.lower().strip())
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'is', 'it'}
        words = [w for w in normalized.split() if w not in stop_words]
        # Create hash
        content = ' '.join(words[:500])  # First 500 significant words
        return hashlib.md5(content.encode()).hexdigest()
    
    @staticmethod
    def compare_texts(text1: str, text2: str) -> Dict:
        """Compare two texts for similarity."""
        words1 = set(re.findall(r'\b\w+\b', text1.lower()))
        words2 = set(re.findall(r'\b\w+\b', text2.lower()))
        
        if not words1 or not words2:
            return {'similarity': 0, 'shared_words': 0}
        
        shared = words1 & words2
        similarity = len(shared) / min(len(words1), len(words2)) * 100
        
        return {
            'similarity': round(similarity, 1),
            'shared_words': len(shared),
            'unique_to_text1': len(words1 - words2),
            'unique_to_text2': len(words2 - words1)
        }


class AIDetector:
    """
    Detects patterns commonly associated with AI-generated text.
    Provides suggestions to make text sound more human.
    """
    
    # Patterns commonly seen in AI-generated text
    AI_PATTERNS = {
        'hedging_phrases': [
            "it's important to note",
            "it's worth noting",
            "it should be noted",
            "it is essential to",
            "it is crucial to",
            "it is important to understand",
            "one must consider",
            "we must acknowledge",
            "it goes without saying",
            "needless to say",
        ],
        'filler_phrases': [
            "in today's world",
            "in this day and age",
            "in the modern era",
            "in today's society",
            "in the current landscape",
            "moving forward",
            "going forward",
            "at the present time",
            "as we all know",
        ],
        'overused_transitions': [
            "furthermore",
            "moreover",
            "additionally",
            "consequently",
            "subsequently",
            "nevertheless",
            "notwithstanding",
            "henceforth",
            "thereby",
        ],
        'ai_vocabulary': [
            "utilize",
            "leverage",
            "facilitate",
            "implementation",
            "functionality",
            "methodology",
            "comprehensive",
            "robust",
            "seamless",
            "cutting-edge",
            "state-of-the-art",
            "groundbreaking",
            "revolutionary",
            "paradigm",
            "synergy",
            "holistic",
            "streamline",
            "optimize",
            "maximize",
            "delve",
            "realm",
            "tapestry",
            "beacon",
            "landscape",
            "multifaceted",
            "intricacies",
            "nuances",
        ],
        'generic_conclusions': [
            "in conclusion",
            "to sum up",
            "to summarize",
            "in summary",
            "all in all",
            "to conclude",
            "taking everything into account",
            "on the whole",
        ],
        'ai_sentence_starters': [
            "this is a",
            "this is an",
            "there are many",
            "there are several",
            "there are numerous",
            "one of the most",
            "it is clear that",
            "it is evident that",
            "it can be seen that",
        ]
    }
    
    # More human alternatives
    HUMAN_ALTERNATIVES = {
        "it's important to note": ["Notice that", "Keep in mind", "Here's the thing:"],
        "it's worth noting": ["Interestingly", "By the way", "Fun fact:"],
        "in today's world": ["Right now", "These days", "Lately"],
        "furthermore": ["Also", "Plus", "And"],
        "moreover": ["What's more", "On top of that", "And here's another thing"],
        "additionally": ["Also", "Plus", "Another thing"],
        "utilize": ["use"],
        "leverage": ["use", "take advantage of"],
        "facilitate": ["help", "make easier", "enable"],
        "comprehensive": ["complete", "thorough", "full"],
        "robust": ["strong", "solid", "reliable"],
        "seamless": ["smooth", "easy", "effortless"],
        "in conclusion": ["So", "Bottom line", "Here's what matters"],
        "delve": ["explore", "dig into", "look at"],
        "realm": ["area", "field", "world"],
        "tapestry": ["mix", "blend", "combination"],
        "landscape": ["scene", "situation", "world"],
        "multifaceted": ["complex", "varied", "many-sided"],
    }
    
    @staticmethod
    def analyze(text: str) -> Dict:
        """
        Analyze text for AI-generated patterns.
        
        Returns:
            Dict with AI probability score and improvement suggestions
        """
        results = {
            'ai_probability': 0,
            'ai_score': 0,
            'human_score': 0,
            'issues': [],
            'patterns_found': {},
            'suggestions': [],
            'rewrite_suggestions': []
        }
        
        text_lower = text.lower()
        words = text_lower.split()
        total_words = len(words)
        
        if total_words < 50:
            results['ai_probability'] = 0
            results['note'] = 'Text too short for reliable analysis'
            return results
        
        # Check each pattern category
        for category, patterns in AIDetector.AI_PATTERNS.items():
            found = []
            for pattern in patterns:
                count = text_lower.count(pattern)
                if count > 0:
                    found.append({'phrase': pattern, 'count': count})
                    results['ai_score'] += count * 3
            
            if found:
                results['patterns_found'][category] = found
        
        # Check sentence structure variety
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if sentences:
            # Check sentence length variety
            lengths = [len(s.split()) for s in sentences]
            avg_length = sum(lengths) / len(lengths)
            length_variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
            
            # Low variance = more AI-like
            if length_variance < 20:
                results['issues'].append({
                    'type': 'uniform_sentence_length',
                    'message': 'Sentences are too uniform in length - vary them more',
                    'avg_length': round(avg_length, 1)
                })
                results['ai_score'] += 10
            else:
                results['human_score'] += 10
            
            # Check sentence starters
            starters = [s.split()[0].lower() if s.split() else '' for s in sentences]
            starter_counts = Counter(starters)
            
            repeated_starters = [s for s, c in starter_counts.items() if c > 2 and s in ['the', 'this', 'it', 'there', 'i', 'we', 'they']]
            if repeated_starters:
                results['issues'].append({
                    'type': 'repetitive_sentence_starters',
                    'message': f'Too many sentences start with: {", ".join(repeated_starters)}',
                    'suggestion': 'Vary your sentence beginnings'
                })
                results['ai_score'] += 5 * len(repeated_starters)
        
        # Check for contractions (humans use more contractions)
        contractions = ["don't", "can't", "won't", "isn't", "aren't", "I'm", "you're", "we're", "they're", "it's", "that's", "what's", "there's", "here's", "let's"]
        contraction_count = sum(1 for c in contractions if c.lower() in text_lower)
        
        if contraction_count > 3:
            results['human_score'] += 15
        elif contraction_count == 0 and total_words > 200:
            results['issues'].append({
                'type': 'no_contractions',
                'message': 'No contractions found - text may sound stiff',
                'suggestion': 'Add contractions to sound more natural (e.g., "do not" → "don\'t")'
            })
            results['ai_score'] += 10
        
        # Check for personal voice
        personal_pronouns = ['i', 'my', 'me', 'we', 'our', 'us']
        pronoun_count = sum(words.count(p) for p in personal_pronouns)
        pronoun_ratio = pronoun_count / total_words * 100
        
        if pronoun_ratio < 0.5 and total_words > 200:
            results['issues'].append({
                'type': 'low_personal_voice',
                'message': 'Low use of personal pronouns - text may feel impersonal',
                'suggestion': 'Add more personal perspective ("I think...", "In my experience...")'
            })
            results['ai_score'] += 8
        elif pronoun_ratio > 2:
            results['human_score'] += 10
        
        # Calculate AI probability
        total_score = results['ai_score'] + results['human_score']
        if total_score > 0:
            results['ai_probability'] = min(95, max(5, round(results['ai_score'] / total_score * 100)))
        else:
            results['ai_probability'] = 30  # Default moderate
        
        # Generate rewrite suggestions
        for category, found_patterns in results['patterns_found'].items():
            for item in found_patterns[:3]:  # Top 3 per category
                phrase = item['phrase']
                if phrase in AIDetector.HUMAN_ALTERNATIVES:
                    alternatives = AIDetector.HUMAN_ALTERNATIVES[phrase]
                    results['rewrite_suggestions'].append({
                        'original': phrase,
                        'alternatives': alternatives,
                        'example': f'Instead of "{phrase}", try "{alternatives[0]}"'
                    })
        
        # Overall assessment
        if results['ai_probability'] > 70:
            results['assessment'] = 'High probability of AI-generated content'
            results['suggestions'].append('Significant rewriting recommended')
            results['suggestions'].append('Add personal anecdotes and experiences')
            results['suggestions'].append('Use more contractions and casual language')
            results['suggestions'].append('Vary sentence structure and length')
        elif results['ai_probability'] > 40:
            results['assessment'] = 'Moderate AI indicators detected'
            results['suggestions'].append('Consider rephrasing flagged sections')
            results['suggestions'].append('Add more personal voice')
        else:
            results['assessment'] = 'Text appears human-written'
            results['suggestions'].append('Text looks good!')
        
        return results
    
    @staticmethod
    def humanize_text(text: str) -> Dict:
        """
        Suggest specific changes to make text sound more human.
        """
        suggestions = []
        modified_text = text
        
        # Replace AI phrases with human alternatives
        for ai_phrase, alternatives in AIDetector.HUMAN_ALTERNATIVES.items():
            if ai_phrase.lower() in text.lower():
                # Find and suggest replacement
                pattern = re.compile(re.escape(ai_phrase), re.IGNORECASE)
                matches = pattern.findall(text)
                if matches:
                    suggestions.append({
                        'find': matches[0],
                        'replace_with': alternatives[0],
                        'all_alternatives': alternatives
                    })
                    # Apply first suggestion
                    modified_text = pattern.sub(alternatives[0], modified_text, count=1)
        
        return {
            'original_text': text,
            'modified_text': modified_text,
            'changes_made': len(suggestions),
            'suggestions': suggestions
        }


class QualityChecker:
    """Combined quality checker for manuscripts."""
    
    @staticmethod
    def full_check(text: str) -> Dict:
        """Run all quality checks on text."""
        
        # Plagiarism check
        plagiarism = PlagiarismChecker.analyze(text)
        
        # AI detection
        ai_detection = AIDetector.analyze(text)
        
        # Humanize suggestions
        humanize = AIDetector.humanize_text(text)
        
        # Overall quality score
        quality_score = 100
        
        # Deduct for plagiarism risk
        if plagiarism['risk_level'] == 'high':
            quality_score -= 30
        elif plagiarism['risk_level'] == 'medium':
            quality_score -= 15
        
        # Deduct for AI probability
        if ai_detection['ai_probability'] > 70:
            quality_score -= 25
        elif ai_detection['ai_probability'] > 40:
            quality_score -= 10
        
        quality_score = max(0, quality_score)
        
        # Grade
        if quality_score >= 90:
            grade = 'A'
        elif quality_score >= 75:
            grade = 'B'
        elif quality_score >= 60:
            grade = 'C'
        else:
            grade = 'D'
        
        return {
            'quality_score': quality_score,
            'quality_grade': grade,
            'plagiarism': plagiarism,
            'ai_detection': ai_detection,
            'humanize_suggestions': humanize,
            'summary': {
                'plagiarism_risk': plagiarism['risk_level'],
                'ai_probability': f"{ai_detection['ai_probability']}%",
                'total_issues': len(plagiarism['issues']) + len(ai_detection['issues']),
                'changes_suggested': humanize['changes_made']
            }
        }
