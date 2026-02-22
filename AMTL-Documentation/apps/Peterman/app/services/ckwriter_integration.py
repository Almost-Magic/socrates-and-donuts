"""
CK Writer Integration for Peterman.

Handles sending content briefs to CK Writer for drafting and
receiving completed content back.
"""

import logging
import requests
from datetime import datetime
from uuid import UUID
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# CK Writer endpoint (configure via environment)
CKWRITER_BASE_URL = 'http://localhost:8888'


class CKWriterIntegration:
    """Handles integration with CK Writer for content drafting."""
    
    def __init__(self):
        self.base_url = CKWRITER_BASE_URL
        self.timeout = 120  # Longer timeout for content generation
    
    def send_brief_to_writer(
        self,
        brief_id: UUID,
        domain_id: UUID,
        title: str,
        brief_content: str,
        target_url: Optional[str] = None,
        keywords: list = None
    ) -> Dict[str, Any]:
        """
        Send a content brief to CK Writer for drafting.
        
        Returns job_id for tracking the drafting process.
        """
        
        payload = {
            'job_type': 'content_draft',
            'brief_id': str(brief_id),
            'domain_id': str(domain_id),
            'title': title,
            'brief_content': brief_content,
            'target_url': target_url,
            'keywords': keywords or [],
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        try:
            # Try CK Writer endpoint
            response = requests.post(
                f'{self.base_url}/api/draft',
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'status': 'sent',
                    'job_id': result.get('job_id', str(brief_id)),
                    'brief_id': str(brief_id),
                }
            else:
                # CK Writer not available - stub response
                logger.warning(f'CK Writer unavailable: {response.status_code}')
                return self._create_stub_response(brief_id, domain_id, title)
                
        except requests.RequestException as e:
            logger.warning(f'CK Writer not reachable: {e}')
            # Return stub response for testing
            return self._create_stub_response(brief_id, domain_id, title)
    
    def _create_stub_response(self, brief_id: UUID, domain_id: UUID, title: str) -> Dict[str, Any]:
        """Create stub response when CK Writer is unavailable."""
        return {
            'status': 'stub',
            'job_id': f'stub-{str(brief_id)[:8]}',
            'brief_id': str(brief_id),
            'message': 'CK Writer not available - using stub response',
            'simulated_content': f'Simulated content draft for: {title}',
        }
    
    def check_draft_status(self, job_id: str) -> Dict[str, Any]:
        """Check status of a drafting job."""
        
        try:
            response = requests.get(
                f'{self.base_url}/api/draft/{job_id}/status',
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'status': 'unknown', 'error': f'HTTP {response.status_code}'}
                
        except requests.RequestException:
            return {'status': 'unavailable', 'message': 'CK Writer not reachable'}
    
    def receive_completed_content(
        self,
        job_id: str,
        content: str,
        alignment_score: float
    ) -> Dict[str, Any]:
        """
        Receive completed content from CK Writer.
        
        This is called when CK Writer returns drafted content.
        """
        from app.models.database import get_session
        from app.models.brief import ContentBrief
        from app.models.audit import AuditLog
        
        session = get_session()
        try:
            # Find brief by job_id or brief_id
            brief = session.query(ContentBrief).filter(
                ContentBrief.brief_id == job_id.replace('stub-', '')
            ).first()
            
            if not brief:
                return {'status': 'error', 'message': 'Brief not found'}
            
            # Update brief with drafted content
            brief.generated_content = content
            brief.status = 'drafted'
            brief.drafted_at = datetime.utcnow()
            
            # Calculate alignment score
            brief.alignment_score = alignment_score
            
            # Log in audit trail
            audit = AuditLog(
                domain_id=brief.domain_id,
                action='content_drafted',
                details={
                    'brief_id': str(brief.brief_id),
                    'job_id': job_id,
                    'alignment_score': alignment_score,
                }
            )
            session.add(audit)
            session.commit()
            
            # Determine next steps based on alignment score
            if alignment_score >= 80:
                # Queue for deployment approval
                return {
                    'status': 'ready_for_approval',
                    'brief_id': str(brief.brief_id),
                    'alignment_score': alignment_score,
                    'next_action': 'Queue for deployment approval',
                }
            else:
                # Flag for revision
                return {
                    'status': 'needs_revision',
                    'brief_id': str(brief.brief_id),
                    'alignment_score': alignment_score,
                    'next_action': 'Flag for revision - alignment below 80%',
                }
            
        except Exception as e:
            session.rollback()
            logger.error(f'Failed to receive content: {e}')
            return {'status': 'error', 'error': str(e)}
        finally:
            session.close()
    
    def check_alignment(
        self,
        brief_id: UUID,
        generated_content: str
    ) -> Dict[str, Any]:
        """
        Check alignment between brief requirements and generated content.
        
        Uses simple keyword/phrase matching. In production, could use
        embeddings or LLM-based evaluation.
        """
        from app.models.database import get_session
        from app.models.brief import ContentBrief
        
        session = get_session()
        try:
            brief = session.query(ContentBrief).filter_by(brief_id=brief_id).first()
            if not brief:
                return {'error': 'Brief not found'}
            
            # Simple alignment check based on keywords
            keywords = brief.keywords or []
            
            if not keywords:
                # No keywords - give benefit of doubt
                return {'alignment_score': 85.0, 'matched': [], 'missing': []}
            
            content_lower = generated_content.lower()
            matched = [kw for kw in keywords if kw.lower() in content_lower]
            missing = [kw for kw in keywords if kw.lower() not in content_lower]
            
            # Calculate score
            if keywords:
                alignment_score = (len(matched) / len(keywords)) * 100
            else:
                alignment_score = 85.0
            
            return {
                'alignment_score': alignment_score,
                'matched': matched,
                'missing': missing,
                'total_keywords': len(keywords),
            }
            
        finally:
            session.close()


def send_to_ck_writer(brief_id: UUID, domain_id: UUID, title: str, content: str) -> Dict[str, Any]:
    """Convenience function to send brief to CK Writer."""
    integration = CKWriterIntegration()
    return integration.send_brief_to_writer(brief_id, domain_id, title, content)


def check_alignment(brief_id: UUID, generated_content: str) -> Dict[str, Any]:
    """Convenience function to check alignment."""
    integration = CKWriterIntegration()
    return integration.check_alignment(brief_id, generated_content)
