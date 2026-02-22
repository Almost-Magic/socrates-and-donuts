"""
Chamber 9 — The Oracle

Predictive forecasting - what keywords and topics will matter in 90 days.

Signal inputs:
1. Google Trends (via SearXNG)
2. Emerging query patterns from probe data
3. Regulatory signals
4. Competitor velocity
5. Performance data from Chamber 7

Per DEC-005: Uses Claude CLI + SearXNG.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict
from uuid import UUID

from sqlalchemy import Column, Integer, String, DateTime, JSON, Float, UUID as SQLUUID, ForeignKey

from app.models.database import Base, get_session

logger = logging.getLogger(__name__)


class OracleForecast(Base):
    """Oracle forecast data."""
    __tablename__ = 'oracle_forecasts'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    domain_id = Column(SQLUUID(as_uuid=True), ForeignKey('domains.domain_id'), nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)
    forecast_days = Column(Integer, default=90)
    topics = Column(JSON)  # List of predicted topics
    calendar = Column(JSON)  # 90-day content calendar
    confidence = Column(Float, default=0.0)  # 0-1
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'domain_id': str(self.domain_id),
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'forecast_days': self.forecast_days,
            'topics': self.topics,
            'calendar': self.calendar,
            'confidence': self.confidence,
        }


def _get_ai_engine():
    from app.services.ai_engine import AIEngine
    return AIEngine()


def generate_forecast(domain_id: UUID) -> Dict:
    """Generate 90-day forecast."""
    engine = _get_ai_engine()
    session = get_session()
    
    try:
        # Get keywords and probes for context
        from app.services.keyword_engine import TargetQuery
        from app.models.probe import Probe
        
        keywords = session.query(TargetQuery).filter_by(domain_id=domain_id).all()
        probes = session.query(Probe).filter_by(domain_id=domain_id).all()
        
        # Build context
        topic_list = [kw.query for kw in keywords[:20]]
        probe_queries = [p.query for p in probes[:10]]
        
        prompt = f"""You are a content strategy expert. Analyse these topics and probes for a business:

Current Topics: {', '.join(topic_list[:10])}
Recent Queries: {', '.join(probe_queries[:5])}

Predict the top 10 topics that will be most important for this business in the next 90 days.
For each topic provide:
1. Topic name
2. Why it will matter (1-2 sentences)
3. Predicted interest trajectory (rising/stable/declining)
4. Suggested content type (article/guide/case study)

Respond as JSON array."""

        try:
            result = engine.reason(prompt, "You are a strategic content planner.")
            if result.get('success'):
                # Parse topics
                topics = []
                try:
                    import json
                    topics = json.loads(result['response'])
                except:
                    topics = [{'topic': t.strip(), 'why': 'Predicted trend', 'trajectory': 'rising'} 
                             for t in result['response'].split('\n') if t.strip()]
                
                # Generate calendar
                calendar = []
                for i, topic in enumerate(topics[:10]):
                    # Spread topics over 90 days
                    day = (i * 9) + 1
                    calendar.append({
                        'day': day,
                        'topic': topic.get('topic', str(topic)),
                        'type': topic.get('type', 'article'),
                    })
                
                # Save forecast
                forecast = OracleForecast(
                    domain_id=domain_id,
                    topics=topics,
                    calendar=calendar,
                    confidence=0.7,  # Default confidence
                )
                session.add(forecast)
                session.commit()
                
                return {
                    'status': 'ready',
                    'topics': topics,
                    'calendar': calendar,
                    'confidence': 0.7,
                }
        except Exception as e:
            logger.error(f"Forecast generation failed: {e}")
        
        return {'status': 'error', 'message': str(e)}
    finally:
        session.close()


def get_latest_forecast(domain_id: UUID) -> Dict:
    """Get latest forecast."""
    session = get_session()
    try:
        forecast = session.query(OracleForecast).filter_by(
            domain_id=domain_id
        ).order_by(OracleForecast.generated_at.desc()).first()
        
        if not forecast:
            return {'status': 'pending', 'message': 'No forecast. Generate one first.'}
        
        return forecast.to_dict()
    finally:
        session.close()


def get_calendar(domain_id: UUID) -> List[Dict]:
    """Get 90-day content calendar."""
    forecast = get_latest_forecast(domain_id)
    return forecast.get('calendar', [])
