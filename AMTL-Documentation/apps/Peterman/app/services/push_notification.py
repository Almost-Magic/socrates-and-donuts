"""
Push Notification Service for Peterman.

Uses ntfy.sh for mobile push notifications on critical alerts.
Zero cost - uses free tier or self-hosted ntfy server.
"""

import logging
import os
import requests
from datetime import datetime
from uuid import UUID
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# ntfy.sh configuration
NTFY_TOPIC = os.getenv('AMTL_PTR_NTFY_TOPIC', 'peterman-alerts')
NTFY_SERVER = os.getenv('AMTL_PTR_NTFY_SERVER', 'https://ntfy.sh')
NTFY_AUTH_TOKEN = os.getenv('AMTL_PTR_NTFY_TOKEN', None)

# Priority levels
PRIORITY_DEFAULT = 'default'
PRIORITY_LOW = 'low'
PRIORITY_HIGH = 'high'
PRIORITY_URGENT = 'urgent'

# Alert types
ALERT_HALLUCINATION = 'hallucination_severity_8plus'
ALERT_COMPETITIVE_THREAT = 'competitive_threat_level_4plus'
ALERT_DEFENSIVE_CRITICAL = 'defensive_shield_critical'
ALERT_SCORE_DROP = 'score_drop_10plus'
ALERT_DEPLOYMENT_FAILURE = 'deployment_failure'


class PushNotificationService:
    """Handles push notifications via ntfy.sh."""
    
    def __init__(self):
        self.server = NTFY_SERVER
        self.topic = NTFY_TOPIC
        self.auth_token = NTFY_AUTH_TOKEN
        self.timeout = 10
    
    def _build_headers(self, title: str, priority: str = PRIORITY_DEFAULT) -> Dict[str, str]:
        """Build HTTP headers for ntfy.sh."""
        headers = {
            'Title': title,
            'Priority': priority,
            'Tags': 'warning,robot',
        }
        
        if self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'
        
        return headers
    
    def send(
        self,
        title: str,
        message: str,
        priority: str = PRIORITY_DEFAULT,
        tags: list = None,
        actions: list = None
    ) -> Dict[str, Any]:
        """
        Send push notification.
        
        Args:
            title: Notification title
            message: Notification body
            priority: Priority level (default, low, high, urgent)
            tags: List of tags for notification
            actions: List of action buttons
        
        Returns:
            Dict with status and details
        """
        
        url = f'{self.server}/{self.topic}'
        headers = self._build_headers(title, priority)
        
        if tags:
            headers['Tags'] = ','.join(tags)
        
        data = {
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        if actions:
            data['actions'] = actions
        
        try:
            response = requests.post(
                url,
                headers=headers,
                data=message,  # ntfy expects plain text in body
                timeout=self.timeout
            )
            
            if response.status_code in (200, 201):
                return {
                    'status': 'sent',
                    'notification_id': response.headers.get('X-Message-ID'),
                    'title': title,
                }
            else:
                logger.warning(f'ntfy.sh returned {response.status_code}: {response.text}')
                return {
                    'status': 'failed',
                    'error': f'HTTP {response.status_code}',
                }
                
        except requests.RequestException as e:
            logger.error(f'Failed to send push notification: {e}')
            return {
                'status': 'error',
                'error': str(e),
            }
    
    def send_hallucination_alert(
        self,
        domain_name: str,
        severity: int,
        hallucination_text: str
    ) -> Dict[str, Any]:
        """Send alert for high-severity hallucination."""
        
        title = f'⚠️ Hallucination Detected: {domain_name}'
        message = f'Severity {severity}/10: {hallucination_text[:200]}'
        
        priority = PRIORITY_URGENT if severity >= 9 else PRIORITY_HIGH
        tags = ['warning', 'robot', 'brain']
        
        return self.send(title, message, priority, tags)
    
    def send_competitive_threat_alert(
        self,
        domain_name: str,
        threat_level: int,
        competitor_name: str
    ) -> Dict[str, Any]:
        """Send alert for competitive threat."""
        
        title = f'🎯 Competitive Threat: {domain_name}'
        message = f'Threat Level {threat_level}/5: {competitor_name} is gaining ground'
        
        priority = PRIORITY_HIGH
        tags = ['warning', 'robot', 'target']
        
        return self.send(title, message, priority, tags)
    
    def send_defensive_critical_alert(
        self,
        domain_name: str,
        issue: str
    ) -> Dict[str, Any]:
        """Send alert for defensive shield critical issue."""
        
        title = f'🛡️ Defensive Alert: {domain_name}'
        message = f'Critical perception issue detected: {issue}'
        
        priority = PRIORITY_URGENT
        tags = ['warning', 'robot', 'shield']
        
        return self.send(title, message, priority, tags)
    
    def send_score_drop_alert(
        self,
        domain_name: str,
        old_score: float,
        new_score: float,
        reason: str = None
    ) -> Dict[str, Any]:
        """Send alert when Peterman Score drops significantly."""
        
        drop = old_score - new_score
        title = f'📉 Score Drop: {domain_name}'
        message = f'Score dropped from {old_score} to {new_score} (-{drop:.1f})'
        
        if reason:
            message += f'\n\nReason: {reason}'
        
        priority = PRIORITY_HIGH
        tags = ['warning', 'robot', 'chart_with_downwards_trend']
        
        return self.send(title, message, priority, tags)
    
    def send_deployment_failure_alert(
        self,
        domain_name: str,
        brief_title: str,
        error: str
    ) -> Dict[str, Any]:
        """Send alert for deployment failure."""
        
        title = f'❌ Deployment Failed: {domain_name}'
        message = f'Failed to deploy: {brief_title}\n\nError: {error}'
        
        priority = PRIORITY_HIGH
        tags = ['warning', 'robot', 'x']
        
        return self.send(title, message, priority, tags)
    
    def test_connection(self) -> Dict[str, Any]:
        """Test ntfy.sh connection."""
        return self.send(
            'Peterman Test',
            'Push notifications are working!',
            PRIORITY_LOW,
            ['white_check_mark']
        )


# Module-level convenience functions
def send_push(title: str, message: str, priority: str = PRIORITY_DEFAULT) -> Dict[str, Any]:
    """Send a push notification."""
    service = PushNotificationService()
    return service.send(title, message, priority)


def send_hallucination_alert(domain_name: str, severity: int, text: str) -> Dict[str, Any]:
    """Send hallucination alert."""
    service = PushNotificationService()
    return service.send_hallucination_alert(domain_name, severity, text)


def send_competitive_alert(domain_name: str, threat: int, competitor: str) -> Dict[str, Any]:
    """Send competitive threat alert."""
    service = PushNotificationService()
    return service.send_competitive_threat_alert(domain_name, threat, competitor)


def send_score_drop_alert(domain_name: str, old_score: float, new_score: float, reason: str = None) -> Dict[str, Any]:
    """Send score drop alert."""
    service = PushNotificationService()
    return service.send_score_drop_alert(domain_name, old_score, new_score, reason)


def send_deployment_failure_alert(domain_name: str, brief_title: str, error: str) -> Dict[str, Any]:
    """Send deployment failure alert."""
    service = PushNotificationService()
    return service.send_deployment_failure_alert(domain_name, brief_title, error)
