"""
Chamber 4 — Authority & Backlink Intelligence

LLM Citation Authority (LCA) - how authoritative LLMs consider a domain
for its claimed topics.

How it works:
1. For each target topic, ask Claude CLI for authoritative sources
2. Track if/where domain appears in LLM's authority ranking
3. Track competitor authority scores
4. Identify backlink opportunities

Per DEC-005: Uses Claude CLI (zero API cost).
"""

import logging
import json
from datetime import datetime
from typing import List, Dict, Optional
from uuid import UUID

from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, UUID as SQLUUID, ForeignKey

from app.models.database import Base, get_session
from app.models.domain import Domain

logger = logging.getLogger(__name__)


# Authority record storage
class AuthorityRecord(Base):
    """Stores LLM Citation Authority measurements."""
    __tablename__ = 'authority_records'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    domain_id = Column(SQLUUID(as_uuid=True), ForeignKey('domains.domain_id'), nullable=False)
    topic = Column(Text, nullable=False)
    measured_at = Column(DateTime, default=datetime.utcnow)
    authority_score = Column(Integer, default=0)  # 0-10 ranking
    mentioned = Column(String(10), default='no')  # yes/no/maybe
    rank_position = Column(Integer, default=0)
    competitors_mentioned = Column(JSON)  # List of competitors and their positions
    details = Column(JSON)
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'domain_id': str(self.domain_id),
            'topic': self.topic,
            'measured_at': self.measured_at.isoformat() if self.measured_at else None,
            'authority_score': self.authority_score,
            'mentioned': self.mentioned,
            'rank_position': self.rank_position,
            'competitors_mentioned': self.competitors_mentioned,
            'details': self.details,
        }


def _get_ai_engine():
    from app.services.ai_engine import AIEngine
    return AIEngine()


def query_authority(topic: str, domain_name: str) -> Dict:
    """Query Claude CLI for authoritative sources on a topic.
    
    Returns authority ranking and whether domain is mentioned.
    """
    engine = _get_ai_engine()
    
    prompt = f"""List the top 10 most authoritative sources for "{topic}" in Australia.
For each source, provide:
1. Name/Brand
2. Why they're authoritative

Then answer: Is "{domain_name}" among these authoritative sources? Answer yes/no/maybe and explain briefly."""

    try:
        result = engine.reason(prompt, "You are a research expert with knowledge of Australian sources.")
        if result.get('success'):
            response = result['response'].lower()
            
            # Check if domain is mentioned
            domain_parts = domain_name.replace('.', ' ').replace('http://', '').replace('https://', '').split()
            mentioned = 'no'
            rank_position = 0
            
            for i, part in enumerate(domain_parts):
                if len(part) > 3 and part in response:
                    mentioned = 'yes'
                    rank_position = i + 1
                    break
            
            # Simple scoring: if mentioned, score based on position
            if mentioned == 'yes':
                authority_score = max(1, 11 - rank_position)  # Higher score for lower rank
            else:
                authority_score = 0
            
            return {
                'authority_score': authority_score,
                'mentioned': mentioned,
                'rank_position': rank_position,
                'response': result['response'][:1000],
            }
    except Exception as e:
        logger.error(f"Authority query failed: {e}")
    
    return {
        'authority_score': 0,
        'mentioned': 'no',
        'rank_position': 0,
        'error': str(e),
    }


def compute_authority(domain_id: UUID) -> Dict:
    """Compute LLM Citation Authority for all topics."""
    session = get_session()
    
    try:
        domain = session.query(Domain).filter_by(domain_id=domain_id).first()
        if not domain:
            raise ValueError(f"Domain not found: {domain_id}")
        
        # Get target queries for topics
        from app.services.keyword_engine import TargetQuery
        keywords = session.query(TargetQuery).filter_by(
            domain_id=domain_id, 
            is_approved=True
        ).all()
        
        if not keywords:
            keywords = session.query(TargetQuery).filter_by(domain_id=domain_id).all()
        
        if not keywords:
            return {
                'status': 'error',
                'message': 'No keywords available. Generate keywords first.',
                'topics': [],
            }
        
        # Get unique topics from keywords
        topics = list(set(kw.query for kw in keywords[:10]))  # Limit to 10 topics
        
        results = []
        
        for topic in topics:
            # Query authority
            authority = query_authority(topic, domain.domain_name)
            
            # Save record
            record = AuthorityRecord(
                domain_id=domain_id,
                topic=topic,
                authority_score=authority.get('authority_score', 0),
                mentioned=authority.get('mentioned', 'no'),
                rank_position=authority.get('rank_position', 0),
                details={'response': authority.get('response', '')},
            )
            session.add(record)
            results.append(record.to_dict())
        
        session.commit()
        
        # Calculate average authority
        avg_score = sum(r['authority_score'] for r in results) / len(results) if results else 0
        mentioned_count = sum(1 for r in results if r['mentioned'] == 'yes')
        
        return {
            'status': 'ready',
            'topics_tested': len(topics),
            'average_authority': round(avg_score, 2),
            'topics_mentioned': mentioned_count,
            'topics': results,
        }
        
    except Exception as e:
        logger.error(f"Authority computation failed: {e}")
        session.rollback()
        return {
            'status': 'error',
            'message': str(e),
            'topics': [],
        }
    finally:
        session.close()


def get_authority_summary(domain_id: UUID) -> Dict:
    """Get authority summary for a domain."""
    session = get_session()
    
    try:
        records = session.query(AuthorityRecord).filter_by(
            domain_id=domain_id
        ).order_by(AuthorityRecord.measured_at.desc()).limit(20).all()
        
        if not records:
            return {
                'status': 'pending',
                'message': 'No authority data. Run authority scan.',
                'average_authority': None,
            }
        
        avg_score = sum(r.authority_score for r in records) / len(records)
        mentioned = sum(1 for r in records if r.mentioned == 'yes')
        
        return {
            'status': 'ready',
            'average_authority': round(avg_score, 2),
            'topics_mentioned': mentioned,
            'total_topics': len(records),
            'measured_at': records[0].measured_at.isoformat() if records else None,
        }
    finally:
        session.close()


def get_authority_history(domain_id: UUID) -> List[Dict]:
    """Get historical authority measurements."""
    session = get_session()
    
    try:
        records = session.query(AuthorityRecord).filter_by(
            domain_id=domain_id
        ).order_by(AuthorityRecord.measured_at.desc()).limit(50).all()
        
        return [r.to_dict() for r in records]
    finally:
        session.close()
