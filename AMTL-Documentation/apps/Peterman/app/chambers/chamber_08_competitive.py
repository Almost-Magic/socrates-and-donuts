"""
Chamber 8 — Competitive Shadow Mode

Monitor competitor domains:
1. Competitor Discovery from probe results
2. Competitor Probing
3. New Content Detection
4. Threat Levels 1-5
5. Auto-generate counter-briefs

Per DEC-005: Uses Claude CLI + SearXNG.
"""

import logging
from datetime import datetime
from typing import List, Dict
from uuid import UUID

from sqlalchemy import Column, Integer, String, DateTime, JSON, UUID as SQLUUID, ForeignKey

from app.models.database import Base, get_session

logger = logging.getLogger(__name__)


class CompetitorDomain(Base):
    """Competitor domain tracking."""
    __tablename__ = 'competitor_domains'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    domain_id = Column(SQLUUID(as_uuid=True), ForeignKey('domains.domain_id'), nullable=False)
    competitor_url = Column(String(500), nullable=False)
    competitor_name = Column(String(255))
    threat_level = Column(Integer, default=1)  # 1-5
    last_scanned = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'domain_id': str(self.domain_id),
            'competitor_url': self.competitor_url,
            'competitor_name': self.competitor_name,
            'threat_level': self.threat_level,
            'last_scanned': self.last_scanned.isoformat() if self.last_scanned else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


def discover_competitors(domain_id: UUID) -> List[Dict]:
    """Discover competitors from probe results."""
    from app.models.probe import Probe
    
    session = get_session()
    try:
        probes = session.query(Probe).filter_by(domain_id=domain_id).all()
        
        competitors = []
        seen = set()
        
        for probe in probes:
            # Look for other domains mentioned in responses
            response = (probe.response or '').lower()
            
            # Simple competitor detection from probe data
            if ' vs ' in (probe.query or '').lower():
                # Extract competitor from comparison query
                query = probe.query.lower()
                parts = query.replace(' vs ', ' ').replace(' vs', '').split()
                for part in parts:
                    if len(part) > 3 and part not in seen:
                        # Skip if it's our domain
                        domain = session.query(type('Domain', (), {'domain_name': ''})).filter_by(domain_id=domain_id).first()
                        if domain and part not in domain.domain_name.lower():
                            seen.add(part)
                            competitors.append({
                                'competitor_url': f"https://{part}.com",
                                'competitor_name': part.title(),
                            })
        
        return competitors[:10]  # Limit to 10
    finally:
        session.close()


def add_competitor(domain_id: UUID, competitor_url: str, competitor_name: str = None) -> Dict:
    """Manually add a competitor."""
    session = get_session()
    try:
        competitor = CompetitorDomain(
            domain_id=domain_id,
            competitor_url=competitor_url,
            competitor_name=competitor_name,
            threat_level=1,
        )
        session.add(competitor)
        session.commit()
        return competitor.to_dict()
    finally:
        session.close()


def get_competitors(domain_id: UUID) -> List[Dict]:
    """Get all competitors for a domain."""
    session = get_session()
    try:
        competitors = session.query(CompetitorDomain).filter_by(domain_id=domain_id).all()
        return [c.to_dict() for c in competitors]
    finally:
        session.close()


def assess_threats(domain_id: UUID) -> Dict:
    """Assess competitor threat levels."""
    competitors = get_competitors(domain_id)
    
    # Simple threat assessment
    threats = {
        'low': [c for c in competitors if c['threat_level'] <= 2],
        'medium': [c for c in competitors if 2 < c['threat_level'] <= 4],
        'critical': [c for c in competitors if c['threat_level'] > 4],
    }
    
    return {
        'total': len(competitors),
        'threats': threats,
    }
