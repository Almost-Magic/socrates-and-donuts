"""
WordPress CMS Adapter.

Deploys content to WordPress via the REST API.
"""

import logging
import os
import requests
from datetime import datetime
from uuid import UUID
from typing import Dict, Any

from .base import CMSAdapter

logger = logging.getLogger(__name__)

# Configuration
WORDPRESS_URL = os.getenv('AMTL_PTR_WORDPRESS_URL')  # e.g., https://example.com
WORDPRESS_USER = os.getenv('AMTL_PTR_WORDPRESS_USER')
WORDPRESS_APP_PASSWORD = os.getenv('AMTL_PTR_WORDPRESS_APP_PASSWORD')


class WordPressAdapter(CMSAdapter):
    """WordPress CMS adapter."""
    
    def __init__(self):
        self.wp_url = WORDPRESS_URL.rstrip('/') if WORDPRESS_URL else None
        self.username = WORDPRESS_USER
        self.app_password = WORDPRESS_APP_PASSWORD
        self.timeout = 30
    
    def _get_auth(self) -> tuple:
        """Get username and app password for Basic Auth."""
        return (self.username, self.app_password)
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for WordPress API."""
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
    
    def is_configured(self) -> bool:
        """Check if WordPress is configured."""
        return bool(self.wp_url and self.username and self.app_password)
    
    def deploy(self, domain_id: UUID, content: Dict[str, Any], target: str) -> Dict[str, Any]:
        """
        Deploy content to WordPress.
        
        Content should include:
        - title: Post title
        - body: HTML content
        - status: draft, publish, pending, future
        - categories: List of category IDs
        - tags: List of tag IDs
        - slug: URL slug
        """
        
        if not self.is_configured():
            return {
                'status': 'error',
                'error': 'WordPress not configured',
                'deployment_id': None,
            }
        
        try:
            # Prepare payload
            payload = {
                'title': content.get('title', 'Untitled'),
                'content': content.get('body', ''),
                'status': content.get('status', 'draft'),
                'slug': content.get('slug', target.lstrip('/')),
            }
            
            # Add categories if provided
            if 'categories' in content:
                payload['categories'] = content['categories']
            
            # Add tags if provided
            if 'tags' in content:
                payload['tags'] = content['tags']
            
            # Add excerpt/meta if provided
            if 'excerpt' in content:
                payload['excerpt'] = content['excerpt']
            
            if 'meta' in content:
                payload['meta'] = content['meta']
            
            # Check if updating existing post
            post_id = None
            if target and target != '/' and not target.startswith('new'):
                # Extract post ID from target (could be numeric ID or slug)
                post_id = target.lstrip('/')
                if post_id.isdigit():
                    url = f'{self.wp_url}/wp-json/wp/v2/posts/{post_id}'
                    method = 'POST'  # WP uses POST for update with ID in URL
                else:
                    # Try to find by slug
                    url = f'{self.wp_url}/wp-json/wp/v2/posts'
                    params = {'slug': post_id}
                    response = requests.get(
                        url, 
                        auth=self._get_auth(), 
                        headers=self._get_headers(),
                        params=params,
                        timeout=10
                    )
                    if response.status_code == 200:
                        posts = response.json()
                        if posts:
                            post_id = posts[0]['id']
                            url = f'{self.wp_url}/wp-json/wp/v2/posts/{post_id}'
                            method = 'POST'
                        else:
                            # Create new with this slug
                            payload['slug'] = post_id
                            url = f'{self.wp_url}/wp-json/wp/v2/posts'
                            method = 'POST'
                    else:
                        url = f'{self.wp_url}/wp-json/wp/v2/posts'
                        method = 'POST'
            else:
                # Create new post
                url = f'{self.wp_url}/wp-json/wp/v2/posts'
                method = 'POST'
            
            # Make the request
            response = requests.request(
                method=method,
                url=url,
                json=payload if method == 'POST' else None,
                auth=self._get_auth() if not post_id else None,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            if response.status_code in (200, 201):
                data = response.json()
                return {
                    'status': 'deployed',
                    'deployment_id': str(data.get('id', f'wp-{datetime.utcnow().timestamp()}')),
                    'cms': 'wordpress',
                    'post_id': data.get('id'),
                    'url': data.get('link'),
                    'slug': data.get('slug'),
                }
            else:
                logger.warning(f'WordPress API error: {response.status_code}')
                return {
                    'status': 'error',
                    'error': f'HTTP {response.status_code}: {response.text[:200]}',
                    'deployment_id': None,
                }
                
        except requests.RequestException as e:
            logger.error(f'WordPress deployment failed: {e}')
            return {
                'status': 'error',
                'error': str(e),
                'deployment_id': None,
            }
    
    def rollback(self, domain_id: UUID, deployment_id: str) -> Dict[str, Any]:
        """
        Rollback WordPress deployment.
        
        WordPress has revision history - can restore from revisions.
        """
        
        if not self.is_configured():
            return {
                'status': 'error',
                'error': 'WordPress not configured',
            }
        
        try:
            # Get revisions
            url = f'{self.wp_url}/wp-json/wp/v2/posts/{deployment_id}/revisions'
            response = requests.get(
                url,
                auth=self._get_auth(),
                headers=self._get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                revisions = response.json()
                if revisions:
                    # Get the previous revision (second to last)
                    prev_revision = revisions[-2] if len(revisions) > 1 else revisions[0]
                    
                    return {
                        'status': 'advisory',
                        'message': f'WordPress rollback available - previous revision ID: {prev_revision["id"]}. Use WordPress admin to restore.',
                        'deployment_id': deployment_id,
                        'cms': 'wordpress',
                        'available_revisions': len(revisions),
                    }
            
            return {
                'status': 'advisory',
                'message': 'WordPress rollback requires manual intervention via WP Admin',
                'deployment_id': deployment_id,
                'cms': 'wordpress',
            }
            
        except requests.RequestException as e:
            return {
                'status': 'error',
                'message': str(e),
            }
    
    def verify(self, domain_id: UUID, deployment_id: str) -> Dict[str, Any]:
        """Verify WordPress deployment."""
        
        if not self.is_configured():
            return {'status': 'unknown', 'message': 'WordPress not configured'}
        
        try:
            url = f'{self.wp_url}/wp-json/wp/v2/posts/{deployment_id}'
            response = requests.get(url, auth=self._get_auth(), timeout=10)
            
            if response.status_code == 200:
                return {
                    'status': 'verified',
                    'deployment_id': deployment_id,
                    'cms': 'wordpress',
                }
            else:
                return {'status': 'failed', 'message': f'HTTP {response.status_code}'}
                
        except requests.RequestException:
            return {'status': 'unknown', 'message': 'Could not verify'}
