"""
Webflow CMS Adapter.

Deploys content to Webflow via the Webflow API.
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
WEBFLOW_API_URL = 'https://api.webflow.com'
WEBFLOW_API_TOKEN = os.getenv('AMTL_PTR_WEBFLOW_TOKEN')
WEBFLOW_SITE_ID = os.getenv('AMTL_PTR_WEBFLOW_SITE_ID')


class WebflowAdapter(CMSAdapter):
    """Webflow CMS adapter."""
    
    def __init__(self):
        self.api_url = WEBFLOW_API_URL
        self.api_token = WEBFLOW_API_TOKEN
        self.site_id = WEBFLOW_SITE_ID
        self.timeout = 30
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for Webflow API."""
        return {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
    
    def is_configured(self) -> bool:
        """Check if Webflow is configured."""
        return bool(self.api_token and self.site_id)
    
    def deploy(self, domain_id: UUID, content: Dict[str, Any], target: str) -> Dict[str, Any]:
        """
        Deploy content to Webflow CMS.
        
        Content should include:
        - title: Page/item title
        - body: HTML content
        - slug: URL slug
        - collection_id: CMS collection ID (if using collections)
        """
        
        if not self.is_configured():
            return {
                'status': 'error',
                'error': 'Webflow not configured',
                'deployment_id': None,
            }
        
        try:
            # Get collection ID from content or use default
            collection_id = content.get('collection_id', self.site_id)
            
            # Prepare payload for Webflow
            payload = {
                'name': content.get('title', 'Untitled'),
                'slug': content.get('slug', target.lstrip('/')),
                'fields': {
                    'body': content.get('body', ''),
                    'meta-description': content.get('meta_description', ''),
                }
            }
            
            # Check if creating new or updating existing
            if target and target != '/':
                # Update existing item
                item_id = target.lstrip('/')
                url = f'{self.api_url}/collections/{collection_id}/items/{item_id}'
                method = 'PATCH'
            else:
                # Create new item
                url = f'{self.api_url}/collections/{collection_id}/items'
                method = 'POST'
            
            response = requests.request(
                method=method,
                url=url,
                json=payload,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            if response.status_code in (200, 201):
                data = response.json()
                return {
                    'status': 'deployed',
                    'deployment_id': data.get('id', f'wf-{datetime.utcnow().timestamp()}'),
                    'cms': 'webflow',
                    'item_id': data.get('id'),
                    'url': data.get('previewUrl'),
                }
            else:
                logger.warning(f'Webflow API error: {response.status_code}')
                return {
                    'status': 'error',
                    'error': f'HTTP {response.status_code}: {response.text[:200]}',
                    'deployment_id': None,
                }
                
        except requests.RequestException as e:
            logger.error(f'Webflow deployment failed: {e}')
            return {
                'status': 'error',
                'error': str(e),
                'deployment_id': None,
            }
    
    def rollback(self, domain_id: UUID, deployment_id: str) -> Dict[str, Any]:
        """
        Rollback Webflow deployment.
        
        Webflow doesn't have native versioning, so we mark it as advisory.
        """
        
        return {
            'status': 'advisory',
            'message': 'Webflow rollback requires manual intervention - use Webflow dashboard to restore previous version',
            'deployment_id': deployment_id,
            'cms': 'webflow',
        }
    
    def verify(self, domain_id: UUID, deployment_id: str) -> Dict[str, Any]:
        """Verify Webflow deployment."""
        
        if not self.is_configured():
            return {
                'status': 'unknown',
                'message': 'Webflow not configured',
            }
        
        try:
            # Try to fetch the item
            url = f'{self.api_url}/items/{deployment_id}'
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            
            if response.status_code == 200:
                return {
                    'status': 'verified',
                    'deployment_id': deployment_id,
                    'cms': 'webflow',
                }
            else:
                return {
                    'status': 'failed',
                    'message': f'HTTP {response.status_code}',
                }
                
        except requests.RequestException:
            return {
                'status': 'unknown',
                'message': 'Could not verify deployment',
            }
