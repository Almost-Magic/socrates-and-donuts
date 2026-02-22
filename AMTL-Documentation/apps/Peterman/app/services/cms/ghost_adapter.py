"""
Ghost CMS Adapter.

Deploys content to Ghost via the Admin API.
"""

import logging
import os
import requests
from datetime import datetime
from uuid import UUID
from typing import Dict, Any, List

from .base import CMSAdapter

logger = logging.getLogger(__name__)

# Configuration
GHOST_API_URL = os.getenv('AMTL_PTR_GHOST_URL')  # e.g., https://yoursite.ghost.io
GHOST_ADMIN_KEY = os.getenv('AMTL_PTR_GHOST_ADMIN_KEY')


class GhostAdapter(CMSAdapter):
    """Ghost CMS adapter."""
    
    def __init__(self):
        self.api_url = GHOST_API_URL.rstrip('/') if GHOST_API_URL else None
        self.admin_key = GHOST_ADMIN_KEY
        self.timeout = 30
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for Ghost Admin API."""
        return {
            'Authorization': f'Ghost {self.admin_key}',
            'Content-Type': 'application/json',
        }
    
    def is_configured(self) -> bool:
        """Check if Ghost is configured."""
        return bool(self.api_url and self.admin_key)
    
    def deploy(self, domain_id: UUID, content: Dict[str, Any], target: str) -> Dict[str, Any]:
        """
        Deploy content to Ghost.
        
        Content should include:
        - title: Post title
        - body: HTML or Markdown content
        - status: draft, scheduled, or published
        - tags: List of tag names
        """
        
        if not self.is_configured():
            return {
                'status': 'error',
                'error': 'Ghost not configured',
                'deployment_id': None,
            }
        
        try:
            # Prepare payload
            post_data = {
                'posts': [{
                    'title': content.get('title', 'Untitled'),
                    'html': content.get('body', ''),
                    'status': content.get('status', 'draft'),
                    'slug': content.get('slug', target.lstrip('/')),
                    'meta_description': content.get('meta_description', ''),
                    'tags': [{'name': tag} for tag in content.get('tags', [])],
                }]
            }
            
            # Check if updating existing
            if target and target != '/' and not target.startswith('new'):
                # Update existing post
                post_id = target.lstrip('/')
                url = f'{self.api_url}/ghost/api/admin/posts/{post_id}/'
                method = 'PUT'
            else:
                # Create new post
                url = f'{self.api_url}/ghost/api/admin/posts/'
                method = 'POST'
            
            response = requests.request(
                method=method,
                url=url,
                json=post_data,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            if response.status_code in (200, 201):
                data = response.json()
                post = data.get('posts', [{}])[0]
                return {
                    'status': 'deployed',
                    'deployment_id': post.get('id', f'ghost-{datetime.utcnow().timestamp()}'),
                    'cms': 'ghost',
                    'post_id': post.get('id'),
                    'url': post.get('url'),
                    'published_at': post.get('published_at'),
                }
            else:
                logger.warning(f'Ghost API error: {response.status_code}')
                return {
                    'status': 'error',
                    'error': f'HTTP {response.status_code}: {response.text[:200]}',
                    'deployment_id': None,
                }
                
        except requests.RequestException as e:
            logger.error(f'Ghost deployment failed: {e}')
            return {
                'status': 'error',
                'error': str(e),
                'deployment_id': None,
            }
    
    def rollback(self, domain_id: UUID, deployment_id: str) -> Dict[str, Any]:
        """
        Rollback Ghost deployment.
        
        Ghost has basic versioning - restore from previous version.
        """
        
        if not self.is_configured():
            return {
                'status': 'error',
                'error': 'Ghost not configured',
            }
        
        try:
            # Get post details
            url = f'{self.api_url}/ghost/api/admin/posts/{deployment_id}/'
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                post = data.get('posts', [{}])[0]
                
                # Ghost doesn't have native rollback - mark as advisory
                return {
                    'status': 'advisory',
                    'message': f'Ghost rollback requires manual intervention. Post was published at {post.get("published_at")}',
                    'deployment_id': deployment_id,
                    'cms': 'ghost',
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Could not fetch post: HTTP {response.status_code}',
                }
                
        except requests.RequestException as e:
            return {
                'status': 'error',
                'message': str(e),
            }
    
    def verify(self, domain_id: UUID, deployment_id: str) -> Dict[str, Any]:
        """Verify Ghost deployment."""
        
        if not self.is_configured():
            return {'status': 'unknown', 'message': 'Ghost not configured'}
        
        try:
            url = f'{self.api_url}/ghost/api/admin/posts/{deployment_id}/'
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            
            if response.status_code == 200:
                return {
                    'status': 'verified',
                    'deployment_id': deployment_id,
                    'cms': 'ghost',
                }
            else:
                return {'status': 'failed', 'message': f'HTTP {response.status_code}'}
                
        except requests.RequestException:
            return {'status': 'unknown', 'message': 'Could not verify'}
