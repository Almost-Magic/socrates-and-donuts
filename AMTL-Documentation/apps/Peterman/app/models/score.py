"""
Peterman Score model for Peterman.

Composite domain health score per AMTL-PTR-SPC-1.0 Section 10.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, JSON, UUID, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB

from app.models.database import Base, TimestampMixin


class PetermanScore(Base, TimestampMixin):
    """Peterman Score record per AMTL-PTR-TDD-1.0 Section 4.1.
    
    Attributes:
        score_id: Primary key UUID.
        domain_id: Reference to the domain.
        total_score: Composite score 0-100.
        confidence: Confidence interval for the score.
        sov_score: LLM Share of Voice score.
        sov_confidence: SoV confidence interval.
        sgs_score: Semantic Gravity Score.
        sgs_confidence: SGS confidence interval.
        technical_score: Technical Foundation score.
        survivability_score: Content Survivability score.
        hallucination_debt: Hallucination debt score.
        competitive_score: Competitive Position score.
        predictive_velocity: Predictive Velocity score.
        component_detail: Full breakdown of each component.
    """
    
    __tablename__ = 'peterman_scores'
    
    score_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain_id = Column(UUID(as_uuid=True), ForeignKey('domains.domain_id'), nullable=False)
    total_score = Column(Float)
    confidence = Column(Float)
    sov_score = Column(Float)
    sov_confidence = Column(Float)
    sgs_score = Column(Float)
    sgs_confidence = Column(Float)
    technical_score = Column(Float)
    survivability_score = Column(Float)
    hallucination_debt = Column(Float)
    competitive_score = Column(Float)
    predictive_velocity = Column(Float)
    component_detail = Column(JSONB)
    
    def to_dict(self) -> dict:
        """Convert score to dictionary representation."""
        return {
            'score_id': str(self.score_id),
            'domain_id': str(self.domain_id),
            'computed_at': self.created_at.isoformat() if self.created_at else None,
            'total_score': self.total_score,
            'confidence': self.confidence,
            'sov_score': self.sov_score,
            'sov_confidence': self.sov_confidence,
            'sgs_score': self.sgs_score,
            'sgs_confidence': self.sgs_confidence,
            'technical_score': self.technical_score,
            'survivability_score': self.survivability_score,
            'hallucination_debt': self.hallucination_debt,
            'competitive_score': self.competitive_score,
            'predictive_velocity': self.predictive_velocity,
            'component_detail': self.component_detail,
        }
    
    def __repr__(self) -> str:
        return f"<PetermanScore(id={self.score_id}, score={self.total_score})>"
