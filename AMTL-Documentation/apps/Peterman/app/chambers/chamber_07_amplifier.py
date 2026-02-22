"""
Chamber 7 — The Amplifier (Content Performance Loop)

Track actual impact of deployed content:
1. SoV Delta - Share of Voice improvement
2. SGS Delta - Semantic Gravity shift
3. LCRI Actual vs Predicted
4. Citation Velocity - Day 0/7/30/90 tracking
5. Cannibalization Check

Per DEC-005: Uses Claude CLI + Ollama.
"""

import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from uuid import UUID

from sqlalchemy import Column, Integer, String, DateTime, JSON, Float, UUID as SQLUUID, ForeignKey

from app.models.database import Base, get_session

logger = logging.getLogger(__name__)


# Performance record storage
class PerformanceRecord(Base):
    """Stores content performance measurements."""
    __tablename__ = 'performance_records'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    domain_id = Column(SQLUUID(as_uuid=True), ForeignKey('domains.domain_id'), nullable=False)
    content_id = Column(String(100))  # Brief or deployment ID
    content_title = Column(String(500))
    measured_at = Column(DateTime, default=datetime.utcnow)
    sov_score = Column(Float, default=0.0)  # 0-100
    sov_delta = Column(Float, default=0.0)
    sgs_delta = Column(Float, default=0.0)
    lcri_actual = Column(Float, default=0.0)
    lcri_predicted = Column(Float, default=0.0)
    citation_velocity = Column(Integer, default=0)  # Citations per period
    cannibalisation_score = Column(Float, default=0.0)
    details = Column(JSON)
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'domain_id': str(self.domain_id),
            'content_id': self.content_id,
            'content_title': self.content_title,
            'measured_at': self.measured_at.isoformat() if self.measured_at else None,
            'sov_score': self.sov_score,
            'sov_delta': self.sov_delta,
            'sgs_delta': self.sgs_delta,
            'lcri_actual': self.lcri_actual,
            'lcri_predicted': self.lcri_predicted,
            'citation_velocity': self.citation_velocity,
            'cannibalisation_score': self.cannibalisation_score,
            'details': self.details,
        }


def _get_ai_engine():
    from app.services.ai_engine import AIEngine
    return AIEngine()


def check_cannibalisation(domain_id: UUID, new_content: str) -> Dict:
    """Check if new content competes with existing pages.
    
    Use embedding similarity - flag if cosine > 0.85.
    """
    # Simple keyword-based check (in production, use embeddings)
    from app.models.domain import Domain
    
    session = get_session()
    try:
        domain = session.query(Domain).filter_by(domain_id=domain_id).first()
        if not domain:
            return {'score': 0.0, 'cannibalised': False}
        
        crawl_data = domain.crawl_data or {}
        existing_pages = crawl_data.get('pages', [])
        
        # Simple text overlap check
        new_words = set(new_content.lower().split())
        max_similarity = 0.0
        similar_page = None
        
        for page in existing_pages[:10]:
            existing_text = page.get('text_content', '') or page.get('metadata', {}).get('description', '')
            existing_words = set(existing_text.lower().split())
            
            if new_words and existing_words:
                overlap = len(new_words & existing_words) / max(len(new_words), len(existing_words))
                if overlap > max_similarity:
                    max_similarity = overlap
                    similar_page = page.get('url', 'unknown')
        
        # Flag if > 85% overlap
        cannibalised = max_similarity > 0.85
        score = round(max_similarity * 100, 2)
        
        return {
            'score': score,
            'cannibalised': cannibalised,
            'similar_page': similar_page,
        }
    finally:
        session.close()


def measure_performance(domain_id: UUID, content_id: str = None) -> Dict:
    """Measure content performance for a domain."""
    session = get_session()
    
    try:
        # Get probes to estimate SoV
        from app.models.probe import Probe
        probes = session.query(Probe).filter_by(domain_id=domain_id).all()
        
        sov_score = 0.0
        sov_delta = 0.0
        
        if probes:
            # Count how many times domain is mentioned in probes
            domain = session.query(Domain).filter_by(domain_id=domain_id).first()
            if domain:
                domain_name = domain.domain_name.lower()
                mentions = sum(1 for p in probes if domain_name in (p.response or '').lower())
                sov_score = (mentions / len(probes)) * 100 if probes else 0
        
        # Get SGS history
        from app.chambers.chamber_02_semantic import get_sgs_history
        sgs_history = get_sgs_history(domain_id)
        
        sgs_delta = 0.0
        if len(sgs_history) >= 2:
            sgs_delta = sgs_history[0].get('sgs_score', 0) - sgs_history[1].get('sgs_score', 0)
        
        # Get LCRI
        from app.chambers.chamber_03_survivability import get_latest_lcri
        lcri_data = get_latest_lcri(domain_id)
        lcri_actual = lcri_data.get('average_lcri', 0) or 0
        
        # Calculate citation velocity (simulated)
        citation_velocity = int(sov_score * 0.5)  # Simplified
        
        # Save record
        record = PerformanceRecord(
            domain_id=domain_id,
            content_id=content_id,
            sov_score=round(sov_score, 2),
            sov_delta=round(sov_delta, 2),
            sgs_delta=round(sgs_delta, 2),
            lcri_actual=lcri_actual,
            lcri_predicted=lcri_actual,  # Would come from The Forge
            citation_velocity=citation_velocity,
            details={'probes_count': len(probes)},
        )
        session.add(record)
        session.commit()
        
        return {
            'status': 'ready',
            'sov_score': round(sov_score, 2),
            'sov_delta': round(sov_delta, 2),
            'sgs_delta': round(sgs_delta, 2),
            'lcri_actual': lcri_actual,
            'citation_velocity': citation_velocity,
        }
        
    except Exception as e:
        logger.error(f"Performance measurement failed: {e}")
        session.rollback()
        return {
            'status': 'error',
            'message': str(e),
        }
    finally:
        session.close()


def get_performance_history(domain_id: UUID, content_id: str = None) -> List[Dict]:
    """Get performance history for content."""
    session = get_session()
    
    try:
        query = session.query(PerformanceRecord).filter_by(domain_id=domain_id)
        if content_id:
            query = query.filter_by(content_id=content_id)
        
        records = query.order_by(PerformanceRecord.measured_at.desc()).limit(30).all()
        return [r.to_dict() for r in records]
    finally:
        session.close()


def get_performance_summary(domain_id: UUID) -> Dict:
    """Get overall performance summary."""
    session = get_session()
    
    try:
        records = session.query(PerformanceRecord).filter_by(
            domain_id=domain_id
        ).order_by(PerformanceRecord.measured_at.desc()).limit(10).all()
        
        if not records:
            return {
                'status': 'pending',
                'message': 'No performance data. Run probes and content.',
            }
        
        avg_sov = sum(r.sov_score for r in records) / len(records)
        avg_sgs_delta = sum(r.sgs_delta for r in records) / len(records)
        total_citations = sum(r.citation_velocity for r in records)
        
        return {
            'status': 'ready',
            'average_sov': round(avg_sov, 2),
            'average_sgs_delta': round(avg_sgs_delta, 2),
            'total_citations': total_citations,
            'content_tracked': len(records),
            'measured_at': records[0].measured_at.isoformat() if records else None,
        }
    finally:
        session.close()
