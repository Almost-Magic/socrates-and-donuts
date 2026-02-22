"""
Hallucination model for Peterman.

Jira-style hallucination tracking per AMTL-PETERMAN-SPC-2.0-PART1 Section 6.1.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, UUID, ForeignKey

from app.models.database import Base, TimestampMixin


class Hallucination(Base, TimestampMixin):
    """Hallucination record per AMTL-PETERMAN-SPC-2.0-PART1 Section 6.1.
    
    Attributes:
        hallucination_id: Primary key UUID.
        domain_id: Reference to the domain.
        detected_at: When the hallucination was detected.
        llm_source: Which LLM produced the hallucination.
        query_triggered: The query that triggered the hallucination.
        false_claim: The false claim detected.
        severity_score: 1-10 severity score.
        status: Hallucination status (open, brief_generated, content_deployed, verified_closed, suppressed).
        assigned_brief_id: Reference to the brief that addresses it.
        closed_at: When the hallucination was closed.
        resolution_evidence: Evidence that the hallucination was resolved.
    """
    
    __tablename__ = 'hallucinations'
    
    hallucination_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain_id = Column(UUID(as_uuid=True), ForeignKey('domains.domain_id'), nullable=False)
    detected_at = Column(DateTime, default=datetime.utcnow)
    llm_source = Column(String(50), nullable=False)
    query_triggered = Column(String(500), nullable=False)
    false_claim = Column(Text, nullable=False)
    severity_score = Column(Integer, default=5)
    status = Column(String(30), default='open')
    assigned_brief_id = Column(UUID)
    closed_at = Column(DateTime)
    resolution_evidence = Column(Text)
    
    def to_dict(self) -> dict:
        """Convert hallucination to dictionary representation."""
        return {
            'hallucination_id': str(self.hallucination_id),
            'domain_id': str(self.domain_id),
            'detected_at': self.detected_at.isoformat() if self.detected_at else None,
            'llm_source': self.llm_source,
            'query_triggered': self.query_triggered,
            'false_claim': self.false_claim,
            'severity_score': self.severity_score,
            'status': self.status,
            'assigned_brief_id': str(self.assigned_brief_id) if self.assigned_brief_id else None,
            'closed_at': self.closed_at.isoformat() if self.closed_at else None,
            'resolution_evidence': self.resolution_evidence,
        }
    
    def __repr__(self) -> str:
        return f"<Hallucination(id={self.hallucination_id}, severity={self.severity_score})>"
