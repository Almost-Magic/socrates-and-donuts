"""
Target Query model for keyword engine.
"""

import logging
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey

from app.models.database import Base, get_session

logger = logging.getLogger(__name__)


class TargetQuery(Base):
    """Target query model for domain probing."""
    
    __tablename__ = 'target_queries'
    
    id = Column(Integer, primary_key=True)
    domain_id = Column(String(36), ForeignKey('domains.domain_id'), nullable=False)
    query = Column(String(1000), nullable=False)
    category = Column(String(50))
    priority = Column(String(20), default='medium')
    status = Column(String(20), default='pending')  # pending, approved, declined
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'domain_id': str(self.domain_id),
            'query': self.query,
            'category': self.category,
            'priority': self.priority,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
