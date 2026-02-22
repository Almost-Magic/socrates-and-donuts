"""
ELAINE Integration for Peterman.

Handles bidirectional communication between Peterman and ELAINE:
- Outbound: Content briefs, approval requests, critical alerts, morning briefings
- Inbound: Status queries, approval responses, strategic queries, trigger commands
"""

import logging
import requests
from datetime import datetime
from uuid import UUID
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# ELAINE endpoint configuration
ELAINE_BASE_URL = 'http://localhost:9000'
ELAINE_API_PREFIX = '/api/elaine'


class ElaineIntegration:
    """Handles integration with ELAINE AI assistant."""
    
    def __init__(self):
        self.base_url = ELAINE_BASE_URL
        self.timeout = 30
    
    # === OUTBOUND: Peterman → ELAINE ===
    
    def send_approval_request(
        self,
        approval_id: UUID,
        domain_id: UUID,
        domain_name: str,
        action: str,
        risk_level: str,
        preview_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send approval request to ELAINE with voice script.
        
        Voice scripts follow gate levels:
        - Low-gate: Auto-proceed in 10 seconds unless objected
        - Medium-gate: Ask for explicit approval
        - Hard-gate: High-risk - require explicit approval
        """
        
        voice_scripts = {
            'auto': f'Peterman wants to update the meta description for {domain_name}. I\'ll proceed in 10 seconds unless you object.',
            'low': f'Peterman wants to update the meta description for {domain_name}. I\'ll proceed in 10 seconds unless you object.',
            'medium': f'Peterman has generated a new FAQ page about {domain_name}. Shall I approve?',
            'hard': f'Peterman recommends changing the canonical URL for {domain_name}. This is high-risk. Would you like to review the preview?',
        }
        
        voice_script = voice_scripts.get(risk_level, voice_scripts['medium'])
        
        payload = {
            'type': 'approval_request',
            'approval_id': str(approval_id),
            'domain_id': str(domain_id),
            'domain_name': domain_name,
            'action': action,
            'risk_level': risk_level,
            'voice_script': voice_script,
            'preview_url': preview_url,
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        try:
            response = requests.post(
                f'{self.base_url}{ELAINE_API_PREFIX}/receive',
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return {'status': 'sent', 'elaine_response': response.json()}
            else:
                logger.warning(f'ELAINE rejected approval request: {response.status_code}')
                return {'status': 'failed', 'error': response.text}
                
        except requests.RequestException as e:
            logger.error(f'Failed to send to ELAINE: {e}')
            return {'status': 'error', 'error': str(e)}
    
    def send_content_brief(
        self,
        brief_id: UUID,
        domain_id: UUID,
        title: str,
        brief_content: str
    ) -> Dict[str, Any]:
        """Send approved content brief to ELAINE's brief queue."""
        
        payload = {
            'type': 'content_brief',
            'brief_id': str(brief_id),
            'domain_id': str(domain_id),
            'title': title,
            'brief_content': brief_content,
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        try:
            response = requests.post(
                f'{self.base_url}{ELAINE_API_PREFIX}/receive',
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return {'status': 'sent', 'brief_id': str(brief_id)}
            else:
                return {'status': 'failed', 'error': response.text}
                
        except requests.RequestException as e:
            logger.error(f'Failed to send brief to ELAINE: {e}')
            return {'status': 'error', 'error': str(e)}
    
    def send_critical_alert(
        self,
        domain_id: UUID,
        alert_type: str,
        severity: int,
        message: str,
        details: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Send critical alert to ELAINE.
        
        Alert types:
        - hallucination_severity_8plus
        - competitive_threat_level_4plus
        - defensive_shield_critical
        - score_drop_10plus
        - deployment_failure
        """
        
        payload = {
            'type': 'critical_alert',
            'domain_id': str(domain_id),
            'alert_type': alert_type,
            'severity': severity,
            'message': message,
            'details': details or {},
            'timestamp': datetime.utcnow().isoformat(),
            'urgency': 'critical' if severity >= 8 else 'high',
        }
        
        try:
            response = requests.post(
                f'{self.base_url}{ELAINE_API_PREFIX}/receive',
                json=payload,
                timeout=self.timeout
            )
            
            return {'status': 'sent' if response.status_code == 200 else 'failed'}
            
        except requests.RequestException as e:
            logger.error(f'Failed to send alert to ELAINE: {e}')
            return {'status': 'error', 'error': str(e)}
    
    def send_morning_briefing(
        self,
        domain_id: UUID,
        score_data: Dict[str, Any],
        pending_approvals: List[Dict[str, Any]],
        hallucinations_detected: List[Dict[str, Any]],
        score_changes: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Send morning briefing data to ELAINE."""
        
        payload = {
            'type': 'morning_briefing',
            'domain_id': str(domain_id),
            'current_score': score_data.get('total_score'),
            'grade': score_data.get('grade'),
            'score_changes': score_changes or {},
            'pending_approvals': pending_approvals,
            'hallucinations_detected': hallucinations_detected,
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        try:
            response = requests.post(
                f'{self.base_url}{ELAINE_API_PREFIX}/receive',
                json=payload,
                timeout=self.timeout
            )
            
            return {'status': 'sent' if response.status_code == 200 else 'failed'}
            
        except requests.RequestException as e:
            logger.error(f'Failed to send briefing to ELAINE: {e}')
            return {'status': 'error', 'error': str(e)}
    
    # === INBOUND: ELAINE → Peterman ===
    
    def query_status(self, domain_id: UUID) -> Dict[str, Any]:
        """Query Peterman status for ELAINE."""
        from app.services.score_engine import compute_peterman_score
        
        try:
            score_data = compute_peterman_score(domain_id)
            return {
                'domain_id': str(domain_id),
                'status': 'ok',
                'score': score_data,
            }
        except Exception as e:
            logger.error(f'Failed to get status: {e}')
            return {'status': 'error', 'error': str(e)}
    
    def query_score(self, domain_id: UUID) -> Dict[str, Any]:
        """Query Peterman Score for ELAINE."""
        from app.services.score_engine import compute_peterman_score
        
        try:
            score_data = compute_peterman_score(domain_id)
            return score_data
        except Exception as e:
            logger.error(f'Failed to get score: {e}')
            return {'error': str(e)}
    
    def get_pending_briefs(self, domain_id: UUID = None) -> List[Dict[str, Any]]:
        """Get pending content briefs for ELAINE."""
        from app.models.database import get_session
        from app.models.brief import ContentBrief
        
        session = get_session()
        try:
            query = session.query(ContentBrief).filter_by(status='pending')
            
            if domain_id:
                query = query.filter_by(domain_id=domain_id)
            
            briefs = query.all()
            
            return [
                {
                    'brief_id': str(b.brief_id),
                    'domain_id': str(b.domain_id),
                    'title': b.title,
                    'status': b.status,
                    'created_at': b.created_at.isoformat() if b.created_at else None,
                }
                for b in briefs
            ]
        finally:
            session.close()
    
    def process_approval_response(
        self,
        approval_id: UUID,
        approved: bool,
        notes: str = None
    ) -> Dict[str, Any]:
        """Process approval response from ELAINE/operator."""
        from app.models.database import get_session
        from app.models.audit import AuditLog
        
        session = get_session()
        try:
            from app.models.brief import ContentBrief
            from app.services.approvals import Approval
            
            # Get approval
            approval = session.query(Approval).filter_by(approval_id=approval_id).first()
            if not approval:
                return {'status': 'error', 'message': 'Approval not found'}
            
            # Update approval status
            approval.status = 'approved' if approved else 'rejected'
            approval.resolved_at = datetime.utcnow()
            approval.resolution_notes = notes
            
            # If approved, update associated brief
            if approval.brief_id:
                brief = session.query(ContentBrief).filter_by(
                    brief_id=approval.brief_id
                ).first()
                if brief:
                    brief.status = 'approved' if approved else 'rejected'
            
            # Log in audit trail
            audit = AuditLog(
                domain_id=approval.domain_id,
                action='approval_response',
                details={
                    'approval_id': str(approval_id),
                    'approved': approved,
                    'notes': notes,
                    'source': 'elaine',
                }
            )
            session.add(audit)
            session.commit()
            
            return {
                'status': 'processed',
                'approval_id': str(approval_id),
                'new_status': approval.status,
            }
            
        except Exception as e:
            session.rollback()
            logger.error(f'Failed to process approval response: {e}')
            return {'status': 'error', 'error': str(e)}
        finally:
            session.close()
    
    def handle_trigger_command(
        self,
        command: str,
        params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Handle trigger commands from ELAINE."""
        
        params = params or {}
        
        if command == 'run_probe':
            # Trigger probe on specified query
            from app.services.probe_engine import run_probe
            
            domain_id = params.get('domain_id')
            query = params.get('query')
            
            if not domain_id or not query:
                return {'status': 'error', 'message': 'domain_id and query required'}
            
            try:
                result = run_probe(domain_id, query)
                return {'status': 'executed', 'result': result}
            except Exception as e:
                return {'status': 'error', 'error': str(e)}
        
        elif command == 'run_crawl':
            # Trigger domain crawl
            from app.services.crawler import crawl_domain
            
            domain_id = params.get('domain_id')
            
            if not domain_id:
                return {'status': 'error', 'message': 'domain_id required'}
            
            try:
                result = crawl_domain(domain_id)
                return {'status': 'executed', 'result': result}
            except Exception as e:
                return {'status': 'error', 'error': str(e)}
        
        elif command == 'compute_score':
            # Recompute Peterman Score
            domain_id = params.get('domain_id')
            
            if not domain_id:
                return {'status': 'error', 'message': 'domain_id required'}
            
            try:
                from app.services.score_engine import compute_peterman_score
                result = compute_peterman_score(domain_id)
                return {'status': 'executed', 'result': result}
            except Exception as e:
                return {'status': 'error', 'error': str(e)}
        
        else:
            return {'status': 'unknown_command', 'command': command}


# Convenience functions
def send_approval_to_elaine(approval_id: UUID, domain_id: UUID, domain_name: str, action: str, risk_level: str) -> Dict[str, Any]:
    """Send approval request to ELAINE."""
    integration = ElaineIntegration()
    return integration.send_approval_request(approval_id, domain_id, domain_name, action, risk_level)


def send_brief_to_elaine(brief_id: UUID, domain_id: UUID, title: str, content: str) -> Dict[str, Any]:
    """Send content brief to ELAINE."""
    integration = ElaineIntegration()
    return integration.send_content_brief(brief_id, domain_id, title, content)


def send_alert_to_elaine(domain_id: UUID, alert_type: str, severity: int, message: str) -> Dict[str, Any]:
    """Send critical alert to ELAINE."""
    integration = ElaineIntegration()
    return integration.send_critical_alert(domain_id, alert_type, severity, message)
