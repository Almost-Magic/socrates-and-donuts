"""
Approval System for Peterman.

Manages approval gates for keywords, briefs, and other decisions.
"""

import logging
from datetime import datetime
from typing import List, Dict, Optional
from uuid import UUID

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, UUID as SQLUUID, ForeignKey

from app.models.database import Base, get_session

logger = logging.getLogger(__name__)


class Approval(Base):
    """Approval model for tracking approval-gated items."""
    
    __tablename__ = 'approvals'
    
    id = Column(Integer, primary_key=True)
    domain_id = Column(SQLUUID(as_uuid=True), ForeignKey('domains.domain_id'), nullable=False)
    approval_type = Column(String(50), nullable=False)  # 'keyword', 'brief', 'probe', 'config'
    item_id = Column(Integer, nullable=False)  # ID of the item (query_id, brief_id, etc.)
    item_type = Column(String(50), nullable=False)  # Type of item (target_query, content_brief, etc.)
    risk_level = Column(String(20), nullable=False)  # low, medium, high, critical
    title = Column(Text, nullable=False)
    description = Column(Text)
    impact_statement = Column(Text)
    status = Column(String(20), default='pending')  # pending, approved, declined
    decided_at = Column(DateTime)
    decided_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'domain_id': str(self.domain_id),
            'approval_type': self.approval_type,
            'item_id': self.item_id,
            'item_type': self.item_type,
            'risk_level': self.risk_level,
            'title': self.title,
            'description': self.description,
            'impact_statement': self.impact_statement,
            'status': self.status,
            'decided_at': self.decided_at.isoformat() if self.decided_at else None,
            'decided_by': self.decided_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


def create_keyword_approval(domain_id: UUID, query_id: int, query_text: str, category: str) -> Dict:
    """Create an approval for a keyword/query.
    
    Args:
        domain_id: UUID of the domain.
        query_id: ID of the query.
        query_text: The query text.
        category: Query category.
        
    Returns:
        Created approval dictionary.
    """
    session = get_session()
    
    try:
        approval = Approval(
            domain_id=domain_id,
            approval_type='keyword',
            item_id=query_id,
            item_type='target_query',
            risk_level='low',
            title=f"Approve keyword: {query_text[:50]}...",
            description=f"Category: {category}",
            impact_statement="This query will be used for LLM probing",
            status='pending'
        )
        session.add(approval)
        session.commit()
        
        logger.info(f"Created keyword approval {approval.id} for domain {domain_id}")
        
        return approval.to_dict()
        
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to create keyword approval: {e}")
        raise
        
    finally:
        session.close()


def create_brief_approval(domain_id: UUID, brief_id: int, brief_title: str, priority: str) -> Dict:
    """Create an approval for a content brief.
    
    Args:
        domain_id: UUID of the domain.
        brief_id: ID of the brief.
        brief_title: Title of the brief.
        priority: Brief priority.
        
    Returns:
        Created approval dictionary.
    """
    session = get_session()
    
    try:
        approval = Approval(
            domain_id=domain_id,
            approval_type='brief',
            item_id=brief_id,
            item_type='content_brief',
            risk_level=map_priority_to_risk(priority),
            title=f"Approve brief: {brief_title[:50]}...",
            description=f"Priority: {priority}",
            impact_statement="This brief will be sent for content creation",
            status='pending'
        )
        session.add(approval)
        session.commit()
        
        logger.info(f"Created brief approval {approval.id} for domain {domain_id}")
        
        return approval.to_dict()
        
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to create brief approval: {e}")
        raise
        
    finally:
        session.close()


def map_priority_to_risk(priority: str) -> str:
    """Map priority to risk level."""
    mapping = {
        'critical': 'critical',
        'high': 'high',
        'medium': 'medium',
        'low': 'low'
    }
    return mapping.get(priority.lower(), 'medium')


def get_domain_approvals(domain_id: UUID, status: Optional[str] = None) -> List[Dict]:
    """Get approvals for a domain.
    
    Args:
        domain_id: UUID of the domain.
        status: Optional status filter.
        
    Returns:
        List of approval dictionaries.
    """
    session = get_session()
    
    try:
        query = session.query(Approval).filter_by(domain_id=domain_id)
        if status:
            query = query.filter_by(status=status)
        
        approvals = query.order_by(Approval.created_at.desc()).all()
        return [a.to_dict() for a in approvals]
        
    finally:
        session.close()


def get_pending_approvals(domain_id: UUID) -> List[Dict]:
    """Get pending approvals for a domain.
    
    Args:
        domain_id: UUID of the domain.
        
    Returns:
        List of pending approval dictionaries.
    """
    return get_domain_approvals(domain_id, status='pending')


def get_approval(approval_id: int) -> Dict:
    """Get a specific approval.
    
    Args:
        approval_id: ID of the approval.
        
    Returns:
        Approval dictionary.
    """
    session = get_session()
    
    try:
        approval = session.query(Approval).filter_by(id=approval_id).first()
        if not approval:
            raise ValueError(f"Approval not found: {approval_id}")
        
        return approval.to_dict()
        
    finally:
        session.close()


def approve_item(approval_id: int, decided_by: str = 'admin') -> Dict:
    """Approve an item.
    
    Args:
        approval_id: ID of the approval.
        decided_by: Who approved it.
        
    Returns:
        Updated approval dictionary.
    """
    session = get_session()
    
    try:
        approval = session.query(Approval).filter_by(id=approval_id).first()
        if not approval:
            raise ValueError(f"Approval not found: {approval_id}")
        
        approval.status = 'approved'
        approval.decided_at = datetime.utcnow()
        approval.decided_by = decided_by
        
        session.commit()
        
        # Handle the actual approval based on type
        if approval.approval_type == 'keyword':
            from app.services.keyword_engine import approve_query
            approve_query(approval.item_id)
        elif approval.approval_type == 'brief':
            from app.services.forge import approve_brief
            approve_brief(approval.item_id)
        
        logger.info(f"Approved {approval.approval_type} item {approval.item_id}")
        
        return approval.to_dict()
        
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to approve: {e}")
        raise
        
    finally:
        session.close()


def decline_item(approval_id: int, decided_by: str = 'admin', reason: str = None) -> Dict:
    """Decline an item.
    
    Args:
        approval_id: ID of the approval.
        decided_by: Who declined it.
        reason: Optional reason for decline.
        
    Returns:
        Updated approval dictionary.
    """
    session = get_session()
    
    try:
        approval = session.query(Approval).filter_by(id=approval_id).first()
        if not approval:
            raise ValueError(f"Approval not found: {approval_id}")
        
        approval.status = 'declined'
        approval.decided_at = datetime.utcnow()
        approval.decided_by = decided_by
        
        if reason:
            approval.description = f"{approval.description}\n\nDeclined: {reason}"
        
        session.commit()
        
        logger.info(f"Declined {approval.approval_type} item {approval.item_id}")
        
        return approval.to_dict()
        
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to decline: {e}")
        raise
        
    finally:
        session.close()


def bulk_approve_keywords(domain_id: UUID, decided_by: str = 'admin') -> Dict:
    """Approve all pending keyword approvals for a domain.
    
    Args:
        domain_id: UUID of the domain.
        decided_by: Who approved.
        
    Returns:
        Bulk approval results.
    """
    session = get_session()
    
    try:
        # Get all pending keyword approvals
        pending = session.query(Approval).filter_by(
            domain_id=domain_id,
            approval_type='keyword',
            status='pending'
        ).all()
        
        approved_count = 0
        for approval in pending:
            approval.status = 'approved'
            approval.decided_at = datetime.utcnow()
            approval.decided_by = decided_by
            approved_count += 1
            
            # Approve the actual query
            from app.services.keyword_engine import approve_query
            try:
                approve_query(approval.item_id)
            except Exception as e:
                logger.warning(f"Failed to approve query {approval.item_id}: {e}")
        
        session.commit()
        
        logger.info(f"Bulk approved {approved_count} keyword approvals for domain {domain_id}")
        
        return {
            'domain_id': str(domain_id),
            'approved_count': approved_count
        }
        
    except Exception as e:
        session.rollback()
        logger.error(f"Bulk approval failed: {e}")
        raise
        
    finally:
        session.close()
