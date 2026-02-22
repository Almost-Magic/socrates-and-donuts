"""
Probe Engine for Peterman.

LLM probing with normalisation protocol per DEC-010.
Supports both automatic (Claude CLI) and manual (paste-back) probing.
"""

import logging
import time
import json
from datetime import datetime
from uuid import UUID
from typing import List, Dict, Optional

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, UUID as SQLUUID, ForeignKey

from app.models.database import Base, get_session
from app.models.domain import Domain
from app.models.probe import ProbeResult  # Import from models, don't redefine
from app.services.ai_engine import call_claude_cli, AIEngine

logger = logging.getLogger(__name__)

# Standard probe specification per DEC-010
PROBE_SPEC = {
    'temperature': 0.0,
    'top_p': 1.0,
    'runs_per_query': 5,
    'timeout_seconds': 30,
}

# System prompt for probing
PETERMAN_STANDARD_SYSTEM_PROMPT = """You are Peterman, an AI presence analysis tool. 
You will be asked questions about brands, companies, or organisations. 
Respond accurately and factually. If you do not have information about a brand, state that clearly. 
Do not hallucinate or speculate. Format your response to clearly indicate whether the brand was mentioned."""


class ManualProbeQueue(Base):
    """Manual probe queue for desktop apps without CLI."""
    
    __tablename__ = 'manual_probe_queue'
    
    id = Column(Integer, primary_key=True)
    domain_id = Column(SQLUUID(as_uuid=True), ForeignKey('domains.domain_id'), nullable=False)
    query_id = Column(Integer, ForeignKey('target_queries.id'))
    query = Column(Text, nullable=False)
    llm_provider = Column(String(50), nullable=False)
    status = Column(String(20), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    responded_at = Column(DateTime)
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'domain_id': str(self.domain_id),
            'query_id': self.query_id,
            'query': self.query,
            'llm_provider': self.llm_provider,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'responded_at': self.responded_at.isoformat() if self.responded_at else None,
        }


def get_current_probe_cycle(domain_id: UUID) -> int:
    """Get the current probe cycle number for a domain."""
    session = get_session()
    try:
        latest = session.query(ProbeResult).filter_by(
            domain_id=domain_id
        ).order_by(ProbeResult.probe_cycle.desc()).first()
        return (latest.probe_cycle + 1) if latest else 1
    finally:
        session.close()


def run_auto_probe(domain_id: UUID, query: str, llm_provider: str = 'claude_cli') -> Dict:
    """Run automatic probe using Claude CLI."""
    session = get_session()
    cycle = get_current_probe_cycle(domain_id)
    
    try:
        domain = session.query(Domain).filter_by(domain_id=domain_id).first()
        if not domain:
            raise ValueError(f"Domain not found: {domain_id}")
        
        domain_name = domain.domain_name
        
        # Run 5 probes per DEC-010
        results = []
        for run_num in range(1, PROBE_SPEC['runs_per_query'] + 1):
            prompt = f"""Query: {query}

Respond to this query as you would if asked by a user. 
Focus on mentioning {domain_name} if relevant to the query.
Provide a helpful, accurate response."""
            
            try:
                response_text = call_claude_cli(prompt, PETERMAN_STANDARD_SYSTEM_PROMPT, timeout=60)
            except Exception as e:
                logger.warning(f"Probe run {run_num} failed: {e}")
                response_text = f"Probe failed: {e}"
            
            analysis = analyse_probe_response(response_text, query, domain_name)
            
            # Store result - FIX: removed duplicate run_number=
            probe = ProbeResult(
                domain_id=domain_id,
                llm_provider=llm_provider,
                query=query,
                run_number=run_num,
                response_text=response_text,
                brand_mentioned=analysis['brand_mentioned'],
                mention_position=analysis['mention_position'],
                sentiment=analysis['sentiment'],
                mention_quote=analysis.get('mention_quote'),
                competitors_mentioned=json.dumps(analysis.get('competitors_mentioned', [])),
                confidence=analysis['confidence'],
                is_manual=False,
                probe_cycle=cycle,
            )
            session.add(probe)
            results.append({
                'run_number': run_num,
                'response': response_text,
                **analysis
            })
            
            if run_num < PROBE_SPEC['runs_per_query']:
                time.sleep(0.5)
        
        session.commit()
        
        normalised = normalise_results(results)
        normalised['query'] = query
        normalised['llm_provider'] = llm_provider
        normalised['domain_id'] = str(domain_id)
        normalised['probe_cycle'] = cycle
        
        logger.info(f"Auto-probe complete for {domain_name}: {query[:50]}... ({len(results)} runs)")
        
        return normalised
        
    except Exception as e:
        session.rollback()
        logger.error(f"Auto-probe failed: {e}")
        raise
    finally:
        session.close()


def run_manual_probe(domain_id: UUID, query: str, llm_provider: str, response_text: str) -> Dict:
    """Process a manual probe response (paste-back from desktop app)."""
    session = get_session()
    cycle = get_current_probe_cycle(domain_id)
    
    try:
        domain = session.query(Domain).filter_by(domain_id=domain_id).first()
        if not domain:
            raise ValueError(f"Domain not found: {domain_id}")
        
        domain_name = domain.domain_name
        
        analysis = analyse_probe_response(response_text, query, domain_name)
        
        probe = ProbeResult(
            domain_id=domain_id,
            llm_provider=llm_provider,
            query=query,
            run_number=1,
            response_text=response_text,
            brand_mentioned=analysis['brand_mentioned'],
            mention_position=analysis['mention_position'],
            sentiment=analysis['sentiment'],
            mention_quote=analysis.get('mention_quote'),
            competitors_mentioned=json.dumps(analysis.get('competitors_mentioned', [])),
            confidence=analysis['confidence'],
            is_manual=True,
            probe_cycle=cycle,
        )
        session.add(probe)
        session.commit()
        
        result = probe.to_dict()
        result['probe_cycle'] = cycle
        
        logger.info(f"Manual probe complete: {llm_provider} for {domain_name}")
        
        return result
        
    except Exception as e:
        session.rollback()
        logger.error(f"Manual probe failed: {e}")
        raise
    finally:
        session.close()


def create_manual_probe_queue(domain_id: UUID, query: str, llm_provider: str) -> Dict:
    """Create a manual probe queue entry."""
    session = get_session()
    
    try:
        queue_item = ManualProbeQueue(
            domain_id=domain_id,
            query=query,
            llm_provider=llm_provider,
            status='pending'
        )
        session.add(queue_item)
        session.commit()
        
        return queue_item.to_dict()
        
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to create probe queue: {e}")
        raise
    finally:
        session.close()


def get_probe_queue(domain_id: UUID) -> List[Dict]:
    """Get pending manual probes for a domain."""
    session = get_session()
    
    try:
        items = session.query(ManualProbeQueue).filter_by(
            domain_id=domain_id
        ).filter(ManualProbeQueue.status.in_(['pending', 'awaiting_response'])).all()
        
        return [item.to_dict() for item in items]
        
    finally:
        session.close()


def analyse_probe_response(response_text: str, query: str, domain_name: str) -> Dict:
    """Analyse an LLM response for brand mention using Claude CLI."""
    prompt = f"""Given this query: "{query}"

And this response from an LLM:
"{response_text}"

For the domain "{domain_name}", determine:
1. Is the domain mentioned? (yes/no)
2. Position of first mention (1st, 2nd, 3rd, 4th, 5th, 6th, 7th, or "not mentioned")
3. Sentiment of the mention (positive/neutral/negative)
4. Exact quote of the mention (or "not mentioned")
5. What competing businesses are mentioned instead? (list or "none")

Respond as JSON only:
{{"brand_mentioned": true/false, "mention_position": "1st"/"2nd"/etc/"not mentioned", "sentiment": "positive/neutral/negative", "mention_quote": "...", "competitors": []}}"""

    system_prompt = "You are Peterman, an accurate analysis tool. Extract brand presence information from LLM responses."
    
    try:
        result = call_claude_cli(prompt, system_prompt, timeout=30)
        
        result = result.strip()
        if result.startswith('```json'):
            result = result[7:]
        if result.startswith('```'):
            result = result[3:]
        if result.endswith('```'):
            result = result[:-3]
        
        analysis = json.loads(result.strip())
        
        position_map = {'1st': 1, '2nd': 2, '3rd': 3, '4th': 4, '5th': 5, '6th': 6, '7th': 7}
        mention_position = position_map.get(analysis.get('mention_position', 'not mentioned'))
        if analysis.get('mention_position') == 'not mentioned':
            mention_position = None
        
        return {
            'brand_mentioned': analysis.get('brand_mentioned', False),
            'mention_position': mention_position,
            'sentiment': analysis.get('sentiment', 'neutral'),
            'mention_quote': analysis.get('mention_quote'),
            'competitors_mentioned': analysis.get('competitors', []),
            'confidence': 0.9 if analysis.get('brand_mentioned') else 0.7,
        }
        
    except Exception as e:
        logger.warning(f"Analysis failed, using fallback: {e}")
        return fallback_analysis(response_text, domain_name)


def fallback_analysis(response_text: str, domain_name: str) -> Dict:
    """Simple fallback analysis if Claude CLI fails."""
    response_lower = response_text.lower()
    domain_lower = domain_name.lower()
    
    brand_mentioned = domain_lower in response_lower
    
    mention_position = None
    if brand_mentioned:
        pos = response_lower.find(domain_lower)
        total_len = len(response_text)
        char_percent = pos / total_len if total_len > 0 else 1
        if char_percent < 0.1:
            mention_position = 1
        elif char_percent < 0.25:
            mention_position = 2
        elif char_percent < 0.5:
            mention_position = 3
        else:
            mention_position = 4
    
    positive_words = ['excellent', 'great', 'recommended', 'best', 'trusted', 'good']
    negative_words = ['poor', 'avoid', 'not recommended', 'scam', 'problem', 'bad']
    
    sentiment = 'neutral'
    if any(word in response_lower for word in positive_words):
        sentiment = 'positive'
    elif any(word in response_lower for word in negative_words):
        sentiment = 'negative'
    
    return {
        'brand_mentioned': brand_mentioned,
        'mention_position': mention_position,
        'sentiment': sentiment,
        'mention_quote': domain_name if brand_mentioned else None,
        'competitors_mentioned': [],
        'confidence': 0.5,
    }


def normalise_results(results: List[Dict]) -> Dict:
    """Normalise multiple probe runs into a single result."""
    if not results:
        return {
            'mention_consistency': 0,
            'position_consistency': 0,
            'sentiment_consistency': 0,
            'composite_confidence': 0,
            'runs': []
        }
    
    mentions = [r.get('brand_mentioned', False) for r in results]
    mention_count = sum(1 for m in mentions if m)
    mention_consistency = mention_count / len(results) if results else 0
    
    positions = [r['mention_position'] for r in results if r.get('mention_position')]
    if positions:
        avg_position = sum(positions) / len(positions)
        variance = sum((p - avg_position) ** 2 for p in positions) / len(positions)
        position_consistency = 1 / (1 + variance)
    else:
        position_consistency = 0
    
    sentiments = [r.get('sentiment', 'neutral') for r in results]
    if sentiments:
        dominant = max(set(sentiments), key=sentiments.count)
        sentiment_consistency = sentiments.count(dominant) / len(sentiments)
    else:
        sentiment_consistency = 0
    
    composite_confidence = (
        mention_consistency * 0.4 +
        position_consistency * 0.3 +
        sentiment_consistency * 0.3
    )
    
    return {
        'mention_consistency': round(mention_consistency, 2),
        'position_consistency': round(position_consistency, 2),
        'sentiment_consistency': round(sentiment_consistency, 2),
        'composite_confidence': round(composite_confidence, 2),
        'brand_mention_rate': round(mention_consistency, 2),
        'runs': results
    }


def get_probe_results(domain_id: UUID, cycle: Optional[int] = None) -> List[Dict]:
    """Get all probe results for a domain."""
    session = get_session()
    
    try:
        query = session.query(ProbeResult).filter_by(domain_id=domain_id)
        if cycle:
            query = query.filter_by(probe_cycle=cycle)
        
        results = query.order_by(ProbeResult.probed_at.desc()).all()
        return [r.to_dict() for r in results]
        
    finally:
        session.close()


def get_latest_probe_cycle(domain_id: UUID) -> Optional[int]:
    """Get the most recent probe cycle number."""
    session = get_session()
    try:
        latest = session.query(ProbeResult).filter_by(
            domain_id=domain_id
        ).order_by(ProbeResult.probe_cycle.desc()).first()
        return latest.probe_cycle if latest else None
    finally:
        session.close()


def get_approved_queries(domain_id: UUID) -> List[Dict]:
    """Get approved queries for probing."""
    session = get_session()
    try:
        from app.models.keyword_engine import TargetQuery
        queries = session.query(TargetQuery).filter_by(
            domain_id=domain_id,
            status='approved'
        ).all()
        return [{'id': q.id, 'query': q.query, 'category': q.category} for q in queries]
    finally:
        session.close()


# Aliases for backward compatibility with __init__.py exports
def run_probe(domain_id: UUID, query: str, llm_provider: str = 'claude_cli') -> Dict:
    """Alias for run_auto_probe for backward compatibility."""
    return run_auto_probe(domain_id, query, llm_provider)


def run_probe_batch(domain_id: UUID, queries: List[str], llm_provider: str = 'claude_cli') -> List[Dict]:
    """Run multiple probes in batch."""
    results = []
    for query in queries:
        result = run_auto_probe(domain_id, query, llm_provider)
        results.append(result)
    return results
