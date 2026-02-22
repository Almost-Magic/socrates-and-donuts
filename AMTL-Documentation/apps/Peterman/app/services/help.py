"""
Context-Aware Help System for Peterman.

Per AMTL-ECO-CTX-1.0: Provides contextual help for every screen.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class HelpEntry:
    """A single help entry for a screen or component."""
    screen_id: str
    title: str
    content: str
    keywords: List[str]
    shortcuts: Optional[List[str]] = None


# All help content for Peterman
HELP_CONTENT: Dict[str, HelpEntry] = {
    # Main screens
    'war_room': HelpEntry(
        screen_id='war_room',
        title='War Room — Your Command Centre',
        content='''
The War Room is your central command centre for managing AI brand presence.

**What you can do here:**
• View all your domains at a glance
• See real-time Peterman Scores for each domain
• Access the Approval Inbox for pending content
• Monitor budget usage and probe status
• Launch audits and view reports

**Peterman Score Explained:**
The score ranges from 0-100 and reflects how well LLMs know about your brand.
• 75-100: Excellent — strong brand presence
• 50-74: Good — decent coverage
• 25-49: Warning — needs attention
• 0-24: Critical — immediate action required

**Quick Actions:**
• Click any domain card to drill into details
• Use the navigation menu to access specific chambers
• Press '?' to open this help anytime
        ''',
        keywords=['war room', 'command centre', 'dashboard', 'overview', 'score'],
        shortcuts=['?', 'a', 't', 'r']
    ),
    
    'domain_card': HelpEntry(
        screen_id='domain_card',
        title='Domain Card',
        content='''
Each card represents a managed domain in your portfolio.

**Card Information:**
• Domain name and display name
• Current Peterman Score (colour-coded)
• Status indicator (active, paused, onboarding)
• Last audit date
• Quick action buttons

**Actions:**
• Click to view domain details
• Hover for quick stats
• Use menu for advanced options
        ''',
        keywords=['domain', 'card', 'managed', 'portfolio'],
        shortcuts=None
    ),
    
    'approval_inbox': HelpEntry(
        screen_id='approval_inbox',
        title='Approval Inbox',
        content='''
Peterman requests your approval for content before it goes live.

**Approval Tiers:**
• Low: Minor changes (FAQ updates, meta descriptions)
• Medium: Standard content (blog posts, pages)
• High: Significant changes (new sections, major rewrites)

**How to Approve:**
1. Review the content brief
2. Click Approve to authorise deployment
3. Click Decline to reject (with optional reason)
4. Content moves to deployment queue when approved

**Notifications:**
You'll receive push notifications for new approvals.
        ''',
        keywords=['approval', 'inbox', 'approve', 'decline', 'content brief'],
        shortcuts=['a', '?']
    ),
    
    'journey_timeline': HelpEntry(
        screen_id='journey_timeline',
        title='Journey Timeline',
        content='''
Every action Peterman takes is logged here.

**What gets logged:**
• Domain crawls and audits
• Keyword discoveries
• LLM probe results
• Content brief generations
• Approvals and deployments
• Budget changes

**Using the Timeline:**
• Filter by domain, action type, or date
• Click any entry for detailed information
• Export timeline for reporting
        ''',
        keywords=['journey', 'timeline', 'audit log', 'history', 'actions'],
        shortcuts=['t', '?']
    ),
    
    'peterman_score': HelpEntry(
        screen_id='peterman_score',
        title='Peterman Score',
        content='''
Your Peterman Score is a composite measure of AI brand presence.

**Score Components (weighted):**
• Share of Voice (SoV): 30% — how often you're mentioned
• Authority: 25% — how you're cited as a source
• Consistency: 20% — presence across multiple queries
• Recency: 15% — how recently you were mentioned
• Quality: 10% — sentiment and context

**Improving Your Score:**
• Run regular audits
• Approve and deploy content briefs
• Monitor hallucination detection
• Address authority decay alerts
        ''',
        keywords=['score', 'peterman score', 'sov', 'share of voice', 'authority'],
        shortcuts=['?']
    ),
    
    # Chambers (11 chambers)
    'chamber_01_foundation': HelpEntry(
        screen_id='chamber_01_foundation',
        title='Chamber 01: Foundation',
        content='''
The Foundation Chamber establishes your brand baseline.

**What it measures:**
• Business information accuracy
• Contact details consistency
• Brand messaging clarity
• NAP (Name, Address, Phone) consistency
        ''',
        keywords=['foundation', 'chamber 01', 'baseline', 'business info', 'nap'],
        shortcuts=['?']
    ),
    
    'chamber_02_semantic': HelpEntry(
        screen_id='chamber_02_semantic',
        title='Chamber 02: Semantic Search',
        content='''
The Semantic Search Chamber measures semantic relevance.

**What it measures:**
• How semantically related your content is to target queries
• Topic cluster coverage
• Entity recognition alignment
        ''',
        keywords=['semantic', 'chamber 02', 'search', 'relevance', 'entities'],
        shortcuts=['?']
    ),
    
    'chamber_03_survivability': HelpEntry(
        screen_id='chamber_03_survivability',
        title='Chamber 03: Survivability',
        content='''
The Survivability Chamber assesses content longevity.

**What it measures:**
• Content freshness and updates
• Historical performance
• Age and decay patterns
        ''',
        keywords=['survivability', 'chamber 03', 'longevity', 'freshness', 'content age'],
        shortcuts=['?']
    ),
    
    'chamber_04_authority': HelpEntry(
        screen_id='chamber_04_authority',
        title='Chamber 04: Authority',
        content='''
The Authority Chamber measures brand authority in AI responses.

**What it measures:**
• Citations as authoritative source
• Expert positioning
• Thought leadership presence
        ''',
        keywords=['authority', 'chamber 04', 'citations', 'expert', 'thought leadership'],
        shortcuts=['?']
    ),
    
    'chamber_05_presence': HelpEntry(
        screen_id='chamber_05_presence',
        title='Chamber 05: Presence',
        content='''
The Presence Chamber tracks brand mention volume.

**What it measures:**
• Mention frequency across queries
• Presence consistency
• Competitive mention share
        ''',
        keywords=['presence', 'chamber 05', 'mentions', 'frequency', 'volume'],
        shortcuts=['?']
    ),
    
    'chamber_06_sentiment': HelpEntry(
        screen_id='chamber_06_sentiment',
        title='Chamber 06: Sentiment',
        content='''
The Sentiment Chamber analyses brand perception.

**What it measures:**
• Overall sentiment polarity
• Emotion detection
• Contextual tone analysis
        ''',
        keywords=['sentiment', 'chamber 06', 'emotion', 'tone', 'perception'],
        shortcuts=['?']
    ),
    
    'chamber_07_amplifier': HelpEntry(
        screen_id='chamber_07_amplifier',
        title='Chamber 07: Amplifier',
        content='''
The Amplifier Chamber measures amplification potential.

**What it measures:**
• Share of Voice percentage
• Competitive positioning
• Reach and visibility
        ''',
        keywords=['amplifier', 'chamber 07', 'sov', 'share of voice', 'amplification'],
        shortcuts=['?']
    ),
    
    'chamber_08_competitive': HelpEntry(
        screen_id='chamber_08_competitive',
        title='Chamber 08: Competitive',
        content='''
The Competitive Chamber benchmarks against competitors.

**What it measures:**
• Competitor mention rates
• Relative positioning
• Market share of mind
        ''',
        keywords=['competitive', 'chamber 08', 'competitors', 'benchmark', 'comparison'],
        shortcuts=['?']
    ),
    
    'chamber_09_oracle': HelpEntry(
        screen_id='chamber_09_oracle',
        title='Chamber 09: Oracle',
        content='''
The Oracle Chamber provides predictive insights.

**What it measures:**
• Trend detection
• Predictive scoring
• Future positioning forecasts
        ''',
        keywords=['oracle', 'chamber 09', 'predictive', 'trends', 'forecasting'],
        shortcuts=['?']
    ),
    
    'chamber_10_creative': HelpEntry(
        screen_id='chamber_10_creative',
        title='Chamber 10: Creative',
        content='''
The Creative Chamber assesses creative content.

**What it measures:**
• Brand expression diversity
• Content originality
• Creative asset presence
        ''',
        keywords=['creative', 'chamber 10', 'creativity', 'original', 'assets'],
        shortcuts=['?']
    ),
    
    'chamber_11_defensive': HelpEntry(
        screen_id='chamber_11_defensive',
        title='Chamber 11: Defensive',
        content='''
The Defensive Chamber monitors protection metrics.

**What it measures:**
• Misinformation detection
• Crisis indicators
• Brand safety signals
        ''',
        keywords=['defensive', 'chamber 11', 'safety', 'misinformation', 'protection'],
        shortcuts=['?']
    ),
    
    # Features
    'manual_probe': HelpEntry(
        screen_id='manual_probe',
        title='Manual Probe Station',
        content='''
The Manual Probe Station lets you test specific queries.

**How to use:**
1. Enter your query in the text box
2. Click 'Run Probe' or press Enter
3. Peterman will query all configured LLMs
4. Results show brand mentions per LLM

**Tip:** Great for testing specific scenarios or checking recent changes.
        ''',
        keywords=['manual probe', 'probe station', 'test query', 'manual test'],
        shortcuts=['?']
    ),
    
    'settings': HelpEntry(
        screen_id='settings',
        title='Settings',
        content='''
Configure Peterman to match your workflow.

**Configuration Options:**
• Domain CMS access (WordPress, Webflow, Ghost, GitHub, Webhook)
• Probe cadence (daily, weekly, campaign)
• Budget limits
• Notification preferences
• API keys (for Ollama embeddings)

**Security:**
All API keys are encrypted at rest.
Never share your API keys.
        ''',
        keywords=['settings', 'configuration', 'preferences', 'cms', 'api keys'],
        shortcuts=['?']
    ),
    
    'keyboard_shortcuts': HelpEntry(
        screen_id='keyboard_shortcuts',
        title='Keyboard Shortcuts',
        content='''
**Global Shortcuts:**
• `?` — Open help for current screen
• `Esc` — Close modal or help
• `a` — Jump to Approval Inbox
• `t` — Jump to Journey Timeline
• `r` — Refresh War Room data

**Navigation:**
• Use arrow keys to navigate lists
• Enter to select
• Tab to move between elements
        ''',
        keywords=['keyboard', 'shortcuts', 'keys', 'navigation'],
        shortcuts=['?', 'esc', 'a', 't', 'r']
    ),
}


def get_help_for_screen(screen_id: str) -> Optional[HelpEntry]:
    """
    Get help content for a specific screen.
    
    Args:
        screen_id: The screen identifier
        
    Returns:
        HelpEntry if found, None otherwise
    """
    return HELP_CONTENT.get(screen_id)


def search_help(query: str) -> List[HelpEntry]:
    """
    Search help content by keyword.
    
    Args:
        query: Search query
        
    Returns:
        List of matching help entries
    """
    query_lower = query.lower()
    results = []
    
    for entry in HELP_CONTENT.values():
        # Search in title, content, and keywords
        if (query_lower in entry.title.lower() or
            query_lower in entry.content.lower() or
            any(query_lower in kw.lower() for kw in entry.keywords)):
            results.append(entry)
    
    return results


def get_all_screens() -> List[Dict[str, Any]]:
    """
    Get list of all available help screens.
    
    Returns:
        List of screen metadata
    """
    return [
        {
            'screen_id': entry.screen_id,
            'title': entry.title,
            'keywords': entry.keywords[:3],  # First 3 keywords
        }
        for entry in HELP_CONTENT.values()
    ]


def get_shortcuts_for_screen(screen_id: str) -> List[str]:
    """
    Get keyboard shortcuts for a specific screen.
    
    Args:
        screen_id: The screen identifier
        
    Returns:
        List of shortcuts
    """
    entry = HELP_CONTENT.get(screen_id)
    if entry and entry.shortcuts:
        return entry.shortcuts
    
    # Return global shortcuts as fallback
    return ['?', 'Esc', 'a', 't', 'r']
