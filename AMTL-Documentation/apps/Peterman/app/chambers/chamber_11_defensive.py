"""
Chamber 11 — Defensive Perception Shield

Monitor and protect brand perception in LLM responses:
1. Sentiment Tracking - how is brand described?
2. Claim Verification - fact-check mentions
3. Negative Pattern Detection - flag problematic patterns
4. Correction Requests - generate correction prompts
5. Brand Narrative Score - overall perception health

Per DEC-005: Uses Claude CLI for sentiment/claim analysis.
"""

import logging
from datetime import datetime
from typing import List, Dict
from uuid import UUID

from sqlalchemy import Column, Integer, String, DateTime, JSON, Float, UUID as SQLUUID, ForeignKey

from app.models.database import Base, get_session

logger = logging.getLogger(__name__)


class PerceptionRecord(Base):
    """Perception monitoring data."""
    __tablename__ = 'perception_records'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    domain_id = Column(SQLUUID(as_uuid=True), ForeignKey('domains.domain_id'), nullable=False)
    measured_at = Column(DateTime, default=datetime.utcnow)
    sentiment_score = Column(Float, default=50.0)  # 0-100
    narrative_score = Column(Float, default=50.0)  # 0-100
    claim_count = Column(Integer, default=0)
    negative_claims = Column(Integer, default=0)
    positive_claims = Column(Integer, default=0)
    details = Column(JSON)
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'domain_id': str(self.domain_id),
            'measured_at': self.measured_at.isoformat() if self.measured_at else None,
            'sentiment_score': self.sentiment_score,
            'narrative_score': self.narrative_score,
            'claim_count': self.claim_count,
            'negative_claims': self.negative_claims,
            'positive_claims': self.positive_claims,
            'details': self.details,
        }


def _get_ai_engine():
    from app.services.ai_engine import AIEngine
    return AIEngine()


def analyze_perception(domain_id: UUID) -> Dict:
    """Analyze how LLMs perceive a brand."""
    engine = _get_ai_engine()
    session = get_session()
    
    try:
        from app.models.domain import Domain
        from app.models.probe import Probe
        
        # Get domain
        domain = session.query(Domain).filter_by(domain_id=domain_id).first()
        if not domain:
            return {'status': 'error', 'message': 'Domain not found'}
        
        # Get probes
        probes = session.query(Probe).filter_by(domain_id=domain_id).all()
        
        # Build context
        probe_texts = [p.response for p in probes[:20] if p.response]
        
        prompt = f"""Analyse how this brand is perceived based on these descriptions:

Brand: {domain.display_name}
Descriptions: {' | '.join(probe_texts[:10])}

Provide:
1. Overall sentiment score (0-100, where 100 is very positive)
2. Key positive descriptors found
3. Key negative descriptors found
4. Overall narrative coherence (0-100)

Respond as JSON with keys: sentiment_score, positive_descriptors (array), negative_descriptors (array), narrative_coherence."""

        try:
            result = engine.reason(prompt, "You are a brand perception analyst.")
            if result.get('success'):
                import json
                try:
                    data = json.loads(result['response'])
                except:
                    # Parse manually
                    data = {
                        'sentiment_score': 50,
                        'positive_descriptors': [],
                        'negative_descriptors': [],
                        'narrative_coherence': 50,
                    }
                
                # Save record
                record = PerceptionRecord(
                    domain_id=domain_id,
                    sentiment_score=data.get('sentiment_score', 50),
                    narrative_score=data.get('narrative_coherence', 50),
                    claim_count=len(probe_texts),
                    negative_claims=len(data.get('negative_descriptors', [])),
                    positive_claims=len(data.get('positive_descriptors', [])),
                    details=data,
                )
                session.add(record)
                session.commit()
                
                return {
                    'status': 'ready',
                    'sentiment_score': data.get('sentiment_score', 50),
                    'narrative_score': data.get('narrative_coherence', 50),
                    'details': data,
                }
        except Exception as e:
            logger.error(f"Perception analysis failed: {e}")
        
        return {'status': 'error', 'message': str(e)}
    finally:
        session.close()


def get_latest_perception(domain_id: UUID) -> Dict:
    """Get latest perception data."""
    session = get_session()
    try:
        record = session.query(PerceptionRecord).filter_by(
            domain_id=domain_id
        ).order_by(PerceptionRecord.measured_at.desc()).first()
        
        if not record:
            return {'status': 'pending', 'message': 'No perception data. Run analysis.'}
        
        return record.to_dict()
    finally:
        session.close()


def get_perception_trends(domain_id: UUID) -> List[Dict]:
    """Get perception trends over time."""
    session = get_session()
    try:
        records = session.query(PerceptionRecord).filter_by(
            domain_id=domain_id
        ).order_by(PerceptionRecord.measured_at.desc()).limit(30).all()
        
        return [r.to_dict() for r in records]
    finally:
        session.close()


def generate_correction_prompt(domain_id: UUID, negative_claim: str) -> Dict:
    """Generate a correction prompt for a negative claim."""
    engine = _get_ai_engine()
    
    from app.models.domain import Domain
    
    session = get_session()
    try:
        domain = session.query(Domain).filter_by(domain_id=domain_id).first()
        if not domain:
            return {'status': 'error'}
        
        prompt = f"""Create a factual correction for this incorrect claim about {domain.display_name}:

Incorrect claim: {negative_claim}

Provide:
1. The truth
2. A corrected statement
3. Suggested source to cite

Respond as JSON."""

        try:
            result = engine.reason(prompt, "You are a fact-checker.")
            if result.get('success'):
                import json
                try:
                    correction = json.loads(result['response'])
                except:
                    correction = {'truth': 'Factual correction needed', 'corrected': 'N/A'}
                
                return {
                    'status': 'ready',
                    'correction': correction,
                }
        except Exception as e:
            logger.error(f"Correction generation failed: {e}")
        
        return {'status': 'error'}
    finally:
        session.close()
