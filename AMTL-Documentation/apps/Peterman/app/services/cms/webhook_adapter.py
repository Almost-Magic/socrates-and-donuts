"""
Generic Webhook Adapter.

Sends content to any endpoint via HTTP POST webhook.
Useful for custom CMS integrations, Zapier, Make (Integromat), etc.
"""

import logging
import os
import requests
from datetime import datetime
from uuid import UUID
from typing import Dict, Any

from .base import CMSAdapter

logger = logging.getLogger(__name__)

# Configuration - use a single configurable webhook
WEBHOOK_URL = os.getenv('AMTL_PTR_WEBHOOK_URL')
WEBHOOK_SECRET = os.getenv('AMTL_PTR_WEBHOOK_SECRET')
WEBHOOK_METHOD = os.getenv('AMTL_PTR_WEBHOOK_METHOD', 'POST')


class WebhookAdapter(CMSAdapter):
    """Generic webhook adapter."""
    
    def __init__(self):
        self.webhook_url = WEBHOOK_URL
        self.webhook_secret = WEBHOOK_SECRET
        self.method = WEBHOOK_METHOD
        self.timeout = 30
    
    def _get_headers(self, content_type: str = 'application/json') -> Dict[str, str]:
        """Get headers for webhook request."""
        headers = {
            'Content-Type': content_type,
            'User-Agent': 'Peterman/1.0 CMS Adapter',
        }
        if self.webhook_secret:
            headers['X-Webhook-Secret'] = self.webhook_secret
        return headers
    
    def is_configured(self) -> bool:
        """Check if webhook is configured."""
        return bool(self.webhook_url)
    
    def deploy(self, domain_id: UUID, content: Dict[str, Any], target: str) -> Dict[str, Any]:
        """
        Deploy content via webhook.
        
        Content is sent as JSON payload with:
        - domain_id
        - title
        - body
        - slug/path
        - meta
        - timestamp
        """
        
        if not self.is_configured():
            return {
                'status': 'error',
                'error': 'Webhook not configured',
                'deployment_id': None,
            }
        
        try:
            # Prepare payload
            payload = {
                'domain_id': str(domain_id),
                'title': content.get('title', 'Untitled'),
                'body': content.get('body', ''),
                'slug': target.lstrip('/'),
                'path': target,
                'meta_title': content.get('meta_title', ''),
                'meta_description': content.get('meta_description', ''),
                'tags': content.get('tags', []),
                'status': content.get('status', 'draft'),
                'timestamp': datetime.utcnow().isoformat(),
            }
            
            # Send request
            response = requests.request(
                method=self.method,
                url=self.webhook_url,
                json=payload,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            if response.status_code in (200, 201, 202):
                # Generate deployment ID from response or timestamp
                deployment_id = f'wh-{datetime.utcnow().timestamp()}'
                try:
                    # Try to get ID from response
                    data = response.json()
                    deployment_id = data.get('id', data.get('deployment_id', deployment_id))
                except:
                    pass
                
                return {
                    'status': 'deployed',
                    'deployment_id': deployment_id,
                    'cms': 'webhook',
                    'http_status': response.status_code,
                    'response': response.text[:200] if response.text else None,
                }
            else:
                logger.warning(f'Webhook error: {response.status_code}')
                return {
                    'status': 'error',
                    'error': f'HTTP {response.status_code}: {response.text[:200]}',
                    'deployment_id': None,
                }
                
        except requests.RequestException as e:
            logger.error(f'Webhook deployment failed: {e}')
            return {
                'status': 'error',
                'error': str(e),
                'deployment_id': None,
            }
    
    def rollback(self, domain_id: UUID, deployment_id: str) -> Dict[str, Any]:
        """
        Rollback via webhook.
        
        Sends a DELETE or ROLLBACK request to the webhook.
        """
        
        if not self.is_configured():
            return {
                'status': 'error',
                'error': 'Webhook not configured',
            }
        
        try:
            # Send rollback request
            payload = {
                'action': 'rollback',
                'domain_id': str(domain_id),
                'deployment_id': deployment_id,
                'timestamp': datetime.utcnow().isoformat(),
            }
            
            response = requests.request(
                method='POST',  # Always POST for rollback
                url=self.webhook_url,
                json=payload,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            if response.status_code in (200, 201, 202):
                return {
                    'status': 'deployed',
                    'message': 'Rollback request sent',
                    'deployment_id': deployment_id,
                    'cms': 'webhook',
                }
            else:
                return {
                    'status': 'error',
                    'message': f'HTTP {response.status_code}',
                }
                
        except requests.RequestException as e:
            return {
                'status': 'error',
                'message': str(e),
            }
    
    def verify(self, domain_id: UUID, deployment_id: str) -> Dict[str, Any]:
        """Verify webhook deployment - send verification request."""
        
        if not self.is_configured():
            return {'status': 'unknown', 'message': 'Webhook not configured'}
        
        try:
            payload = {
                'action': 'verify',
                'domain_id': str(domain_id),
                'deployment_id': deployment_id,
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers=self._get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    'status': 'verified',
                    'deployment_id': deployment_id,
                    'cms': 'webhook',
                }
            else:
                return {'status': 'failed', 'message': f'HTTP {response.status_code}'}
                
        except requests.RequestException:
            return {'status': 'unknown', 'message': 'Could not verify'}
