"""
Hallucination Detector for Peterman.

Detects hallucinations in LLM responses by comparing claims against crawl data.
"""

import logging
import json
from datetime import datetime
from typing import List, Dict, Optional
from uuid import UUID

from app.models.database import get_session
from app.models.domain import Domain
from app.models.probe import ProbeResult
from app.models.hallucination import Hallucination
from app.services.ai_engine import call_claude_cli

logger = logging.getLogger(__name__)


def detect_hallucinations(domain_id: UUID) -> Dict:
    """Detect hallucinations in recent probe results.
    
    Compares LLM claims against crawl data to identify inaccuracies.
    
    Args:
        domain_id: UUID of the domain.
        
    Returns:
        Detection results.
    """
    session = get_session()
    
    try:
        domain = session.query(Domain).filter_by(domain_id=domain_id).first()
        if not domain:
            raise ValueError(f"Domain not found: {domain_id}")
        
        # Get crawl data for comparison
        crawl_data = domain.crawl_data
        if not crawl_data:
            return {'hallucinations_found': 0, 'message': 'No crawl data available'}
        
        # Get recent probe results
        recent_probes = session.query(ProbeResult).filter_by(
            domain_id=domain_id
        ).order_by(ProbeResult.probed_at.desc()).limit(20).all()
        
        if not recent_probes:
            return {'hallucinations_found': 0, 'message': 'No probe results to analyse'}
        
        # Check each probe response for hallucinations
        hallucinations_found = 0
        
        for probe in recent_probes:
            if not probe.brand_mentioned:
                # Domain wasn't mentioned - could be a hallucination if query was brand-specific
                continue
            
            # Use Claude to compare response against crawl data
            analysis = analyse_for_hallucination(
                probe.response_text,
                probe.query,
                crawl_data,
                domain.domain_name
            )
            
            if analysis.get('hallucinations'):
                for h in analysis['hallucinations']:
                    hallucination = Hallucination(
                        domain_id=domain_id,
                        probe_result_id=probe.id,
                        claim_text=h.get('claim', ''),
                        hallucination_type=h.get('type', 'fact'),
                        severity=h.get('severity', 5),
                        status='open',
                        evidence=h.get('evidence', '')
                    )
                    session.add(hallucination)
                    hallucinations_found += 1
        
        session.commit()
        
        logger.info(f"Hallucination detection complete: {hallucinations_found} found for domain {domain_id}")
        
        return {
            'hallucinations_found': hallucinations_found,
            'probes_analyzed': len(recent_probes)
        }
        
    except Exception as e:
        session.rollback()
        logger.error(f"Hallucination detection failed: {e}")
        raise
        
    finally:
        session.close()


def analyse_for_hallucinations(response_text: str, query: str, crawl_data: dict, domain_name: str) -> Dict:
    """Use Claude to analyse a response for hallucinations.
    
    Args:
        response_text: The LLM response.
        query: The original query.
        crawl_data: Domain crawl data for comparison.
        domain_name: Domain name.
        
    Returns:
        Analysis results with any detected hallucinations.
    """
    # Extract key facts from crawl data
    business_summary = crawl_data.get('business_summary', {})
    homepage = crawl_data.get('homepage', {})
    metadata = homepage.get('metadata', {})
    
    what_they_do = business_summary.get('what_they_do', 'Unknown')
    key_services = business_summary.get('key_services', [])
    location = business_summary.get('location', 'Unknown')
    industry = business_summary.get('industry', 'Unknown')
    
    services_text = ', '.join(key_services) if key_services else 'Not specified'
    
    prompt = f"""Analyse this LLM response for hallucinations (false claims) compared to the known facts about the business.

Domain: {domain_name}
What they do: {what_they_do}
Key services: {services_text}
Location: {location}
Industry: {industry}

Query asked: {query}

LLM Response:
{response_text}

Compare the LLM response against the known facts above. Identify any claims that are:
1. Factually incorrect
2. Not supported by the business information
3. Contradicting the business's actual services/location/etc.

For each hallucination found, provide:
- The specific claim made
- The type (fact/service/location/pricing/capability)
- Severity (1-10, where 10 is most severe)
- Evidence from the known facts that contradicts it

Respond as JSON only:
{{"hallucinations": [{{"claim": "...", "type": "...", "severity": 5, "evidence": "..."}}]}}

If no hallucinations are found, respond:
{{"hallucinations": []}}"""

    system_prompt = "You are Peterman, a brand intelligence analysis tool. Accurately detect false claims about businesses."
    
    try:
        result = call_claude_cli(prompt, system_prompt, timeout=30)
        
        # Parse JSON
        result = result.strip()
        if result.startswith('```json'):
            result = result[7:]
        if result.startswith('```'):
            result = result[3:]
        if result.endswith('```'):
            result = result[:-3]
        
        return json.loads(result.strip())
        
    except Exception as e:
        logger.warning(f"Analysis failed: {e}")
        return {'hallucinations': []}


def get_domain_hallucinations(domain_id: UUID, status: Optional[str] = None) -> List[Dict]:
    """Get hallucinations for a domain.
    
    Args:
        domain_id: UUID of the domain.
        status: Optional status filter.
        
    Returns:
        List of hallucination dictionaries.
    """
    session = get_session()
    
    try:
        query = session.query(Hallucination).filter_by(domain_id=domain_id)
        if status:
            query = query.filter_by(status=status)
        
        hallucinations = query.order_by(Hallucination.severity.desc()).all()
        return [h.to_dict() for h in hallucinations]
        
    finally:
        session.close()


def get_hallucination(hallucination_id: int) -> Dict:
    """Get a specific hallucination.
    
    Args:
        hallucination_id: ID of the hallucination.
        
    Returns:
        Hallucination dictionary.
    """
    session = get_session()
    
    try:
        hallucination = session.query(Hallucination).filter_by(id=hallucination_id).first()
        if not hallucination:
            raise ValueError(f"Hallucination not found: {hallucination_id}")
        
        return hallucination.to_dict()
        
    finally:
        session.close()


def update_hallucination_status(hallucination_id: int, status: str, notes: str = None) -> Dict:
    """Update hallucination status.
    
    Args:
        hallucination_id: ID of the hallucination.
        status: New status.
        notes: Optional resolution notes.
        
    Returns:
        Updated hallucination dictionary.
    """
    session = get_session()
    
    try:
        hallucination = session.query(Hallucination).filter_by(id=hallucination_id).first()
        if not hallucination:
            raise ValueError(f"Hallucination not found: {hallucination_id}")
        
        hallucination.status = status
        if notes:
            hallucination.resolution_notes = notes
        
        if status in ['verified_closed', 'content_deployed']:
            hallucination.resolved_at = datetime.utcnow()
        
        session.commit()
        
        return hallucination.to_dict()
        
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to update hallucination: {e}")
        raise
        
    finally:
        session.close()
