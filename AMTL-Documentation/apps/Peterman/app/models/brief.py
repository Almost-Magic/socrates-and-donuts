"""
Content Brief model for Peterman.

Content brief tracking per AMTL-PETERMAN-SPC-2.0-PART2 Chamber 10.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey

from app.models.database import Base, TimestampMixin


class ContentBrief(Base, TimestampMixin):
    """Content Brief record per AMTL-PETERMAN-SPC-2.0-PART2 Section (Chamber 10).
    
    Attributes:
        brief_id: Primary key UUID (stored as string for SQLite).
        domain_id: Reference to the domain.
        source: What triggered the brief (hallucination_autopilot, oracle, shadow_mode, manual).
        trigger_id: UUID of the trigger event.
        target_query: The query this content should answer.
        target_llms: JSON array of target LLM providers (stored as JSON text).
        target_cluster: SGS cluster this targets.
        channel_intent: Channel type (web_page, rag_document, linkedin_article, faq_block).
        key_facts: JSON array of required facts (stored as JSON text).
        key_headings: JSON array of suggested headings (stored as JSON text).
        word_count_range: Target word count range.
        schema_type: Schema type to implement.
        lcri_target: Target LCRI score.
        sgs_delta_estimate: Expected SGS improvement.
        priority: Brief priority (critical, high, medium, low).
        status: Brief status (queued, in_elaine, written, approved, deployed, verified).
        alignment_score: How well written content matches brief.
        deadline: When the brief needs to be completed.
    """
    
    __tablename__ = 'content_briefs'
    
    brief_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    domain_id = Column(String(36), ForeignKey('domains.domain_id'), nullable=False)
    source = Column(String(50), nullable=False)
    trigger_id = Column(String(36))
    target_query = Column(String(500))
    target_llms = Column(Text)  # JSON stored as text
    target_cluster = Column(String(255))
    channel_intent = Column(String(50))
    key_facts = Column(Text)  # JSON stored as text
    key_headings = Column(Text)  # JSON stored as text
    word_count_range = Column(String(20))
    schema_type = Column(String(100))
    lcri_target = Column(Float)
    sgs_delta_estimate = Column(Float)
    priority = Column(String(20), default='medium')
    status = Column(String(30), default='queued')
    alignment_score = Column(Float)
    deadline = Column(DateTime)
    
    def to_dict(self) -> dict:
        """Convert brief to dictionary representation."""
        return {
            'brief_id': str(self.brief_id),
            'domain_id': str(self.domain_id),
            'source': self.source,
            'trigger_id': str(self.trigger_id) if self.trigger_id else None,
            'target_query': self.target_query,
            'target_llms': self.target_llms,
            'target_cluster': self.target_cluster,
            'channel_intent': self.channel_intent,
            'key_facts': self.key_facts,
            'key_headings': self.key_headings,
            'word_count_range': self.word_count_range,
            'schema_type': self.schema_type,
            'lcri_target': self.lcri_target,
            'sgs_delta_estimate': self.sgs_delta_estimate,
            'priority': self.priority,
            'status': self.status,
            'alignment_score': self.alignment_score,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self) -> str:
        return f"<ContentBrief(id={self.brief_id}, status='{self.status}')>"
