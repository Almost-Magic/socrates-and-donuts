"""
Domain Embedding model for Peterman.

pgvector embeddings for semantic operations per DEC-004.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, UUID, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import JSONB

from app.models.database import Base, TimestampMixin

# Try to import pgvector, fallback to JSON
try:
    from pgvector import Vector
    VECTOR_TYPE = Vector(768)
    HAS_PGVECTOR = True
except ImportError:
    HAS_PGVECTOR = False
    VECTOR_TYPE = JSONB


class DomainEmbedding(Base, TimestampMixin):
    """Domain Embedding record per AMTL-PTR-TDD-1.0 Section 6.8.
    
    Uses pgvector for similarity queries. nomic-embed-text produces 768-dimensional vectors.
    
    Attributes:
        embedding_id: Primary key UUID.
        domain_id: Reference to the domain.
        page_url: URL of the page embedded.
        page_title: Title of the page.
        content_snippet: Snippet of content embedded.
        embedding: 768-dimensional vector from nomic-embed-text.
    """
    
    __tablename__ = 'domain_embeddings'
    
    embedding_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain_id = Column(UUID(as_uuid=True), ForeignKey('domains.domain_id'), nullable=False)
    page_url = Column(String(500))
    page_title = Column(String(255))
    content_snippet = Column(Text)
    embedding = Column(VECTOR_TYPE)
    computed_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Convert embedding to dictionary representation."""
        return {
            'embedding_id': str(self.embedding_id),
            'domain_id': str(self.domain_id),
            'page_url': self.page_url,
            'page_title': self.page_title,
            'content_snippet': self.content_snippet[:200] + '...' if self.content_snippet and len(self.content_snippet) > 200 else self.content_snippet,
            'embedding': self.embedding.tolist() if self.embedding is not None else None,
            'computed_at': self.computed_at.isoformat() if self.computed_at else None,
        }
    
    def __repr__(self) -> str:
        return f"<DomainEmbedding(id={self.embedding_id}, url='{self.page_url}')>"
