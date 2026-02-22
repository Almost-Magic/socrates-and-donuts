"""
Budget tracking model for Peterman.

Per-domain cost tracking with 80%/100% thresholds per KNW-002.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey

from app.models.database import Base, TimestampMixin


class BudgetTracking(Base, TimestampMixin):
    """Budget tracking entry per AMTL-PTR-TDD-1.0 Section 10.4.
    
    Attributes:
        tracking_id: Primary key UUID (stored as string for SQLite).
        domain_id: Reference to the domain.
        api_provider: Which API provider was used (openai, anthropic).
        cost_aud: Cost incurred in AUD.
        description: Description of the API call.
    """
    
    __tablename__ = 'budget_tracking'
    
    tracking_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    domain_id = Column(String(36), ForeignKey('domains.domain_id'), nullable=False)
    api_provider = Column(String(50), nullable=False)
    cost_aud = Column(Float, nullable=False)
    description = Column(String(255))
    incurred_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Convert budget tracking entry to dictionary representation."""
        return {
            'tracking_id': str(self.tracking_id),
            'domain_id': str(self.domain_id),
            'api_provider': self.api_provider,
            'cost_aud': self.cost_aud,
            'description': self.description,
            'incurred_at': self.incurred_at.isoformat() if self.incurred_at else None,
        }
    
    def __repr__(self) -> str:
        return f"<BudgetTracking(id={self.tracking_id}, provider='{self.api_provider}', cost={self.cost_aud})>"
