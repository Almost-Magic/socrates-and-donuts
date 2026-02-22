"""
Probe Result model for Peterman.

LLM probe results with normalisation data per DEC-010.
"""

import uuid
import json
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey

from app.models.database import Base, TimestampMixin


class ProbeResult(Base, TimestampMixin):
    """Probe result record per AMTL-PTR-TDD-1.0 Section 6.4."""
    
    __tablename__ = 'probe_results'
    
    id = Column(Integer, primary_key=True)
    domain_id = Column(String(36), ForeignKey('domains.domain_id'), nullable=False)
    llm_provider = Column(String(50), nullable=False)
    query = Column(Text, nullable=False)
    run_number = Column(Integer, default=1)
    response_text = Column(Text)
    brand_mentioned = Column(Boolean, default=False)
    mention_position = Column(Integer)
    sentiment = Column(String(20), default='neutral')
    mention_quote = Column(Text)
    competitors_mentioned = Column(Text)
    confidence = Column(Float, default=0.0)
    is_manual = Column(Boolean, default=False)
    probe_cycle = Column(Integer, default=1)
    probed_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'domain_id': str(self.domain_id),
            'llm_provider': self.llm_provider,
            'query': self.query,
            'run_number': self.run_number,
            'response_text': self.response_text,
            'brand_mentioned': self.brand_mentioned,
            'mention_position': self.mention_position,
            'sentiment': self.sentiment,
            'mention_quote': self.mention_quote,
            'competitors_mentioned': json.loads(self.competitors_mentioned) if self.competitors_mentioned else [],
            'confidence': self.confidence,
            'is_manual': self.is_manual,
            'probe_cycle': self.probe_cycle,
            'probed_at': self.probed_at.isoformat() if self.probed_at else None,
        }
    
    def __repr__(self):
        return f"<ProbeResult(id={self.id}, provider='{self.llm_provider}')>"
