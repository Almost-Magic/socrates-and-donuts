"""
CMS Adapters for Peterman.

Provides a unified interface for deploying content to different CMS platforms:
- WordPress (via REST API)
- Webflow (via API)
- Ghost (via Admin API)
- GitHub (for static sites)
- Webhook (generic)
"""

from .wordpress_adapter import WordPressAdapter
from .webflow_adapter import WebflowAdapter
from .ghost_adapter import GhostAdapter
from .github_adapter import GitHubAdapter
from .webhook_adapter import WebhookAdapter

__all__ = [
    'WordPressAdapter',
    'WebflowAdapter', 
    'GhostAdapter',
    'GitHubAdapter',
    'WebhookAdapter',
]
