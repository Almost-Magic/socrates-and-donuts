"""
GitHub Adapter for Static Sites.

Deploys content to GitHub repositories for static site generation.
Supports Netlify, Vercel, and other static site platforms.
"""

import logging
import os
import base64
import requests
from datetime import datetime
from uuid import UUID
from typing import Dict, Any

from .base import CMSAdapter

logger = logging.getLogger(__name__)

# Configuration
GITHUB_TOKEN = os.getenv('AMTL_PTR_GITHUB_TOKEN')
GITHUB_OWNER = os.getenv('AMTL_PTR_GITHUB_OWNER')
GITHUB_REPO = os.getenv('AMTL_PTR_GITHUB_REPO')
GITHUB_BRANCH = os.getenv('AMTL_PTR_GITHUB_BRANCH', 'main')
NETLIFY_HOOK_URL = os.getenv('AMTL_PTR_NETLIFY_HOOK')
VERCEL_HOOK_URL = os.getenv('AMTL_PTR_VERCEL_HOOK')


class GitHubAdapter(CMSAdapter):
    """GitHub adapter for static site deployment."""
    
    def __init__(self):
        self.token = GITHUB_TOKEN
        self.owner = GITHUB_OWNER
        self.repo = GITHUB_REPO
        self.branch = GITHUB_BRANCH
        self.netlify_hook = NETLIFY_HOOK_URL
        self.vercel_hook = VERCEL_HOOK_URL
        self.api_url = 'https://api.github.com'
        self.timeout = 30
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for GitHub API."""
        return {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json',
        }
    
    def is_configured(self) -> bool:
        """Check if GitHub is configured."""
        return bool(self.token and self.owner and self.repo)
    
    def deploy(self, domain_id: UUID, content: Dict[str, Any], target: str) -> Dict[str, Any]:
        """
        Deploy content to GitHub as a file commit.
        
        Content should include:
        - path: File path in repo (e.g., 'content/blog/post.md')
        - content: File content
        - message: Commit message
        """
        
        if not self.is_configured():
            return {
                'status': 'error',
                'error': 'GitHub not configured',
                'deployment_id': None,
            }
        
        try:
            file_path = content.get('path', target.lstrip('/'))
            file_content = content.get('content', '')
            commit_message = content.get('message', f'Peterman deployment: {file_path}')
            
            # Encode content as base64
            encoded_content = base64.b64encode(file_content.encode('utf-8')).decode('utf-8')
            
            # Get current file SHA if it exists (for updates)
            sha = None
            get_url = f'{self.api_url}/repos/{self.owner}/{self.repo}/contents/{file_path}'
            response = requests.get(get_url, headers=self._get_headers(), params={'ref': self.branch})
            
            if response.status_code == 200:
                sha = response.json().get('sha')
            
            # Create or update file
            put_url = f'{self.api_url}/repos/{self.owner}/{self.repo}/contents/{file_path}'
            payload = {
                'message': commit_message,
                'content': encoded_content,
                'branch': self.branch,
            }
            if sha:
                payload['sha'] = sha
            
            response = requests.put(put_url, headers=self._get_headers(), json=payload)
            
            if response.status_code in (200, 201):
                data = response.json()
                commit_sha = data.get('commit', {}).get('sha', '')
                
                # Trigger rebuild if configured
                rebuild_triggered = self._trigger_rebuild()
                
                return {
                    'status': 'deployed',
                    'deployment_id': f'gh-{commit_sha[:7]}',
                    'cms': 'github',
                    'commit_sha': commit_sha,
                    'file_path': file_path,
                    'rebuild_triggered': rebuild_triggered,
                }
            else:
                logger.warning(f'GitHub API error: {response.status_code}')
                return {
                    'status': 'error',
                    'error': f'HTTP {response.status_code}: {response.text[:200]}',
                    'deployment_id': None,
                }
                
        except Exception as e:
            logger.error(f'GitHub deployment failed: {e}')
            return {
                'status': 'error',
                'error': str(e),
                'deployment_id': None,
            }
    
    def _trigger_rebuild(self) -> bool:
        """Trigger rebuild on Netlify or Vercel."""
        triggered = False
        
        if self.netlify_hook:
            try:
                r = requests.post(self.netlify_hook, timeout=10)
                if r.status_code == 200:
                    triggered = True
                    logger.info('Netlify rebuild triggered')
            except Exception as e:
                logger.warning(f'Netlify hook failed: {e}')
        
        if self.vercel_hook:
            try:
                r = requests.post(self.vercel_hook, timeout=10)
                if r.status_code == 200:
                    triggered = True
                    logger.info('Vercel rebuild triggered')
            except Exception as e:
                logger.warning(f'Vercel hook failed: {e}')
        
        return triggered
    
    def rollback(self, domain_id: UUID, deployment_id: str) -> Dict[str, Any]:
        """
        Rollback GitHub deployment.
        
        Uses git revert - creates a new commit that undoes the changes.
        """
        
        if not self.is_configured():
            return {
                'status': 'error',
                'error': 'GitHub not configured',
            }
        
        try:
            # Get the commit to revert
            commit_sha = deployment_id.replace('gh-', '')
            
            # GitHub doesn't have native revert - return advisory
            return {
                'status': 'advisory',
                'message': f'GitHub rollback requires manual git revert of commit {commit_sha[:7]}',
                'deployment_id': deployment_id,
                'cms': 'github',
                'commit_sha': commit_sha,
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def verify(self, domain_id: UUID, deployment_id: str) -> Dict[str, Any]:
        """Verify GitHub deployment by checking the commit."""
        
        if not self.is_configured():
            return {'status': 'unknown', 'message': 'GitHub not configured'}
        
        try:
            commit_sha = deployment_id.replace('gh-', '')
            url = f'{self.api_url}/repos/{self.owner}/{self.repo}/commits/{commit_sha}'
            response = requests.get(url, headers=self._get_headers())
            
            if response.status_code == 200:
                return {
                    'status': 'verified',
                    'deployment_id': deployment_id,
                    'cms': 'github',
                }
            else:
                return {'status': 'failed', 'message': f'HTTP {response.status_code}'}
                
        except Exception:
            return {'status': 'unknown', 'message': 'Could not verify'}
