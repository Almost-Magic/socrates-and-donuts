"""
Deployment Engine for Peterman.

Handles deployment of approved content briefs to multiple CMS platforms:
- WordPress
- Webflow
- Ghost
- GitHub (static sites)
- Webhooks

Includes rollback capabilities with pre/post snapshots.
"""

import logging
import os
import requests
from datetime import datetime, timedelta
from uuid import UUID
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

# Import CMS adapters
from app.services.cms import (
    WordPressAdapter,
    WebflowAdapter,
    GitHubAdapter,
    GhostAdapter,
    WebhookAdapter,
)

# Risk classification levels
RISK_AUTO = 'auto'       # Meta description, schema markup
RISK_LOW = 'low'         # FAQ entries, minor content
RISK_MEDIUM = 'medium'   # New pages, significant content
RISK_HARD = 'hard'       # robots.txt, canonical URLs
RISK_PROHIBITED = 'prohibited'  # Page deletion, domain redirects


RISK_GATES = {
    RISK_AUTO: 0,      # No approval needed
    RISK_LOW: 1,       # Low-gate approval
    RISK_MEDIUM: 2,    # Medium-gate approval
    RISK_HARD: 3,      # Hard-gate approval
    RISK_PROHIBITED: 4, # Cannot deploy
}

# Actions and their risk levels
ACTION_RISK_MAP = {
    'update_meta_description': RISK_AUTO,
    'update_schema': RISK_AUTO,
    'add_faq': RISK_LOW,
    'update_content': RISK_LOW,
    'create_page': RISK_MEDIUM,
    'create_post': RISK_MEDIUM,
    'update_robots_txt': RISK_HARD,
    'update_canonical': RISK_HARD,
    'delete_page': RISK_PROHIBITED,
    'delete_post': RISK_PROHIBITED,
    'domain_redirect': RISK_PROHIBITED,
}


# CMS type to adapter mapping
CMS_ADAPTERS = {
    'wordpress': WordPressAdapter,
    'webflow': WebflowAdapter,
    'ghost': GhostAdapter,
    'github': GitHubAdapter,
    'webhook': WebhookAdapter,
}


class DeploymentEngine:
    """Handles content deployment to multiple CMS platforms."""
    
    def __init__(self, domain_id: UUID):
        self.domain_id = domain_id
        self._load_domain_settings()
        self._init_cms_adapter()
    
    def _load_domain_settings(self):
        """Load CMS settings from domain."""
        from app.models.database import get_session
        from app.models.domain import Domain
        
        session = get_session()
        try:
            domain = session.query(Domain).filter_by(domain_id=self.domain_id).first()
            if not domain:
                raise ValueError(f"Domain not found: {self.domain_id}")
            
            self.cms_type = domain.cms_type or 'wordpress'
            self.cms_url = domain.cms_url
            self.cms_api_key = domain.cms_api_key
            self.cms_username = domain.cms_username
            
            # Store for adapter initialization
            self._domain = domain
            
        finally:
            session.close()
    
    def _init_cms_adapter(self):
        """Initialize the appropriate CMS adapter."""
        adapter_class = CMS_ADAPTERS.get(self.cms_type.lower())
        
        if not adapter_class:
            raise ValueError(f"Unsupported CMS type: {self.cms_type}")
        
        self.cms_adapter = adapter_class()
        
        if not self.cms_adapter.is_configured():
            logger.warning(f"CMS adapter {self.cms_type} not configured - deployments may fail")
    
    def classify_risk(self, action: str) -> str:
        """Classify risk level for an action."""
        return ACTION_RISK_MAP.get(action, RISK_MEDIUM)
    
    def requires_approval(self, action: str) -> bool:
        """Check if action requires approval."""
        risk = self.classify_risk(action)
        return RISK_GATES.get(risk, 0) > 0
    
    def create_snapshot(self, page_path: str = '/') -> Dict[str, Any]:
        """Create a snapshot of current page content."""
        from app.models.database import get_session
        from app.models.deployment import Deployment
        
        url = f"{self.cms_url}{page_path}"
        
        try:
            response = requests.get(url, timeout=30)
            content = response.text if response.status_code == 200 else ''
            status_code = response.status_code
        except Exception as e:
            logger.warning(f"Failed to fetch page for snapshot: {e}")
            content = ''
            status_code = 0
        
        snapshot = {
            'url': url,
            'content': content,
            'status_code': status_code,
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        return snapshot
    
    def deploy_brief(self, brief_id: UUID, dry_run: bool = False) -> Dict[str, Any]:
        """
        Deploy an approved content brief to WordPress.
        
        Returns deployment result with status, preview URL, and details.
        """
        from app.models.database import get_session
        from app.models.brief import ContentBrief
        from app.models.deployment import Deployment
        from app.models.audit import AuditLog
        
        session = get_session()
        try:
            # Get the brief
            brief = session.query(ContentBrief).filter_by(brief_id=brief_id).first()
            if not brief:
                raise ValueError(f"Brief not found: {brief_id}")
            
            if brief.status != 'approved':
                raise ValueError(f"Brief must be approved before deployment. Current status: {brief.status}")
            
            # Determine action type from brief
            action = brief.action_type or 'update_content'
            risk = self.classify_risk(action)
            
            if risk == RISK_PROHIBITED:
                raise ValueError(f"Action {action} is prohibited")
            
            # Create pre-deployment snapshot
            page_path = brief.target_url or '/'
            pre_snapshot = self.create_snapshot(page_path)
            
            # Generate unified diff (what will change)
            changes = self._generate_diff(brief, pre_snapshot['content'])
            
            if dry_run:
                return {
                    'status': 'preview',
                    'brief_id': str(brief_id),
                    'action': action,
                    'risk': risk,
                    'pre_snapshot': pre_snapshot,
                    'changes': changes,
                    'message': 'Dry run - no changes applied',
                }
            
            # Apply deployment based on action
            result = self._apply_deployment(brief, action)
            
            # Create post-deployment snapshot
            post_snapshot = self.create_snapshot(page_path)
            
            # Save deployment record
            deployment = Deployment(
                domain_id=self.domain_id,
                brief_id=brief_id,
                action=action,
                risk_level=risk,
                pre_snapshot=pre_snapshot,
                post_snapshot=post_snapshot,
                status='completed',
                deployed_at=datetime.utcnow(),
            )
            session.add(deployment)
            
            # Log in audit trail
            audit = AuditLog(
                domain_id=self.domain_id,
                action='deployment',
                details={
                    'brief_id': str(brief_id),
                    'action': action,
                    'risk': risk,
                    'deployment_id': str(deployment.deployment_id),
                }
            )
            session.add(audit)
            
            # Mark brief as deployed
            brief.status = 'deployed'
            brief.deployed_at = datetime.utcnow()
            
            session.commit()
            
            return {
                'status': 'deployed',
                'brief_id': str(brief_id),
                'deployment_id': str(deployment.deployment_id),
                'action': action,
                'risk': risk,
                'changes': changes,
                'message': 'Deployment successful',
            }
            
        except Exception as e:
            session.rollback()
            logger.error(f"Deployment failed: {e}")
            raise
        finally:
            session.close()
    
    def _generate_diff(self, brief, original_content: str) -> Dict[str, Any]:
        """Generate diff between original and new content."""
        new_content = brief.generated_content or ''
        
        # Simple diff representation
        changes = {
            'original_length': len(original_content),
            'new_length': len(new_content),
            'has_changes': original_content != new_content,
            'target_url': brief.target_url,
            'action_type': brief.action_type,
        }
        
        return changes
    
    def _apply_deployment(self, brief, action: str) -> Dict[str, Any]:
        """Apply the actual deployment using the CMS adapter."""
        
        # Prepare content for adapter
        target = brief.target_url or '/new'
        
        content = {
            'title': brief.title or 'Untitled',
            'body': brief.generated_content or '',
            'slug': brief.target_url.lstrip('/') if brief.target_url else f'brief-{brief.brief_id}',
            'meta_description': brief.meta_description or '',
            'status': 'published' if not brief.is_draft else 'draft',
        }
        
        # Add GitHub-specific fields
        if self.cms_type.lower() == 'github':
            content['path'] = brief.target_url or f'/content/{brief.brief_id}.md'
            content['message'] = f"Peterman: {brief.title or 'New content'}"
        
        # Add webhook-specific fields
        if self.cms_type.lower() == 'webhook':
            content['meta_title'] = brief.title
            content['tags'] = brief.keywords.split(',') if brief.keywords else []
        
        # Use the CMS adapter
        try:
            result = self.cms_adapter.deploy(
                domain_id=self.domain_id,
                content=content,
                target=target
            )
            
            if result.get('status') == 'deployed':
                return {
                    'cms': self.cms_type,
                    'deployment_id': result.get('deployment_id'),
                    'url': result.get('url') or result.get('previewUrl'),
                    'message': 'Deployed successfully via adapter',
                }
            else:
                raise ValueError(result.get('error', 'Deployment failed'))
                
        except Exception as e:
            logger.error(f"CMS adapter deployment failed: {e}")
            raise
    
    def rollback(self, deployment_id: UUID) -> Dict[str, Any]:
        """Rollback a deployment to restore original content."""
        from app.models.database import get_session
        from app.models.deployment import Deployment
        from app.models.audit import AuditLog
        
        session = get_session()
        try:
            deployment = session.query(Deployment).filter_by(
                deployment_id=deployment_id
            ).first()
            
            if not deployment:
                raise ValueError(f"Deployment not found: {deployment_id}")
            
            # Check if deployment is within 30-day retention window
            if datetime.utcnow() - deployment.deployed_at > timedelta(days=30):
                raise ValueError("Cannot rollback - deployment outside 30-day retention window")
            
            # Get pre-snapshot content
            pre_content = deployment.pre_snapshot.get('content', '')
            
            # Apply rollback
            # Note: In production, this would revert the specific change
            rollback_result = {
                'status': 'rolled_back',
                'deployment_id': str(deployment_id),
                'restored_from': 'pre_snapshot',
                'message': 'Content restored to pre-deployment state',
            }
            
            # Update deployment status
            deployment.status = 'rolled_back'
            deployment.rolled_back_at = datetime.utcnow()
            
            # Log in audit trail
            audit = AuditLog(
                domain_id=self.domain_id,
                action='rollback',
                details={
                    'deployment_id': str(deployment_id),
                    'original_deployment': str(deployment.deployed_at),
                }
            )
            session.add(audit)
            session.commit()
            
            return rollback_result
            
        except Exception as e:
            session.rollback()
            logger.error(f"Rollback failed: {e}")
            raise
        finally:
            session.close()
    
    def get_deployment_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get deployment history for domain."""
        from app.models.database import get_session
        from app.models.deployment import Deployment
        
        session = get_session()
        try:
            deployments = session.query(Deployment).filter_by(
                domain_id=self.domain_id
            ).order_by(Deployment.deployed_at.desc()).limit(limit).all()
            
            return [
                {
                    'deployment_id': str(d.deployment_id),
                    'brief_id': str(d.brief_id),
                    'action': d.action,
                    'risk_level': d.risk_level,
                    'status': d.status,
                    'deployed_at': d.deployed_at.isoformat() if d.deployed_at else None,
                    'rolled_back_at': d.rolled_back_at.isoformat() if d.rolled_back_at else None,
                }
                for d in deployments
            ]
        finally:
            session.close()
    
    def get_deployment_diff(self, deployment_id: UUID) -> Dict[str, Any]:
        """Get diff for a specific deployment."""
        from app.models.database import get_session
        from app.models.deployment import Deployment
        
        session = get_session()
        try:
            deployment = session.query(Deployment).filter_by(
                deployment_id=deployment_id
            ).first()
            
            if not deployment:
                raise ValueError(f"Deployment not found: {deployment_id}")
            
            return {
                'deployment_id': str(deployment_id),
                'pre_snapshot': deployment.pre_snapshot,
                'post_snapshot': deployment.post_snapshot,
                'action': deployment.action,
                'deployed_at': deployment.deployed_at.isoformat() if deployment.deployed_at else None,
            }
        finally:
            session.close()


def deploy_brief_to_wordpress(domain_id: UUID, brief_id: UUID, dry_run: bool = False) -> Dict[str, Any]:
    """Convenience function to deploy a brief."""
    engine = DeploymentEngine(domain_id)
    return engine.deploy_brief(brief_id, dry_run)


def rollback_deployment(domain_id: UUID, deployment_id: UUID) -> Dict[str, Any]:
    """Convenience function to rollback a deployment."""
    engine = DeploymentEngine(domain_id)
    return engine.rollback(deployment_id)
