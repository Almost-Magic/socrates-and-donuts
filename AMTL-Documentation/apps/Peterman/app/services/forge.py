"""
The Forge - Content Brief Generation for Peterman.

Generates content briefs to fix hallucinations and fill gaps in LLM presence.
"""

import logging
import json
from datetime import datetime
from typing import List, Dict, Optional
from uuid import UUID

from app.models.database import get_session
from app.models.domain import Domain
from app.models.brief import ContentBrief
from app.models.hallucination import Hallucination
from app.services.ai_engine import call_claude_cli

logger = logging.getLogger(__name__)


def generate_brief_for_hallucination(domain_id: UUID, hallucination_id: int) -> Dict:
    """Generate a content brief to fix a hallucination.
    
    Args:
        domain_id: UUID of the domain.
        hallucination_id: ID of the hallucination to fix.
        
    Returns:
        Generated brief dictionary.
    """
    session = get_session()
    
    try:
        domain = session.query(Domain).filter_by(domain_id=domain_id).first()
        if not domain:
            raise ValueError(f"Domain not found: {domain_id}")
        
        # Get hallucination
        from app.services.hallucination_detector import Hallucination
        hallucination = session.query(Hallucination).filter_by(id=hallucination_id).first()
        if not hallucination:
            raise ValueError(f"Hallucination not found: {hallucination_id}")
        
        # Get crawl data
        crawl_data = domain.crawl_data
        business_summary = crawl_data.get('business_summary', {}) if crawl_data else {}
        
        # Generate brief using Claude
        brief_data = generate_content_brief(
            domain_name=domain.domain_name,
            hallucination_claim=hallucination.claim_text,
            hallucination_type=hallucination.hallucination_type,
            correct_facts=hallucination.evidence or '',
            business_summary=business_summary,
            target_query=hallucination_id  # Could link to query
        )
        
        # Create brief record
        brief = ContentBrief(
            domain_id=domain_id,
            hallucination_id=hallucination_id,
            title=brief_data.get('title', 'Content Brief'),
            target_query=brief_data.get('target_query'),
            key_facts=json.dumps(brief_data.get('key_facts', [])),
            content_structure=brief_data.get('content_structure', ''),
            where_to_publish=brief_data.get('where_to_publish', ''),
            expected_score_impact=brief_data.get('expected_score_impact', ''),
            status='pending',
            priority=brief_data.get('priority', 'medium')
        )
        session.add(brief)
        
        # Update hallucination status
        hallucination.status = 'brief_generated'
        
        session.commit()
        
        logger.info(f"Generated brief for hallucination {hallucination_id}")
        
        result = brief.to_dict()
        result['hallucination_status'] = hallucination.status
        
        return result
        
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to generate brief: {e}")
        raise
        
    finally:
        session.close()


def generate_gap_brief(domain_id: UUID, gap_type: str = 'missing_coverage') -> Dict:
    """Generate a content brief for a gap in coverage.
    
    Args:
        domain_id: UUID of the domain.
        gap_type: Type of gap (missing_coverage, weak_positioning, etc.)
        
    Returns:
        Generated brief dictionary.
    """
    session = get_session()
    
    try:
        domain = session.query(Domain).filter_by(domain_id=domain_id).first()
        if not domain:
            raise ValueError(f"Domain not found: {domain_id}")
        
        # Get crawl data
        crawl_data = domain.crawl_data
        business_summary = crawl_data.get('business_summary', {}) if crawl_data else {}
        
        # Generate brief using Claude
        brief_data = generate_content_brief(
            domain_name=domain.domain_name,
            gap_type=gap_type,
            business_summary=business_summary
        )
        
        # Create brief record
        brief = ContentBrief(
            domain_id=domain_id,
            title=brief_data.get('title', 'Gap Analysis Brief'),
            target_query=brief_data.get('target_query'),
            key_facts=json.dumps(brief_data.get('key_facts', [])),
            content_structure=brief_data.get('content_structure', ''),
            where_to_publish=brief_data.get('where_to_publish', ''),
            expected_score_impact=brief_data.get('expected_score_impact', ''),
            status='pending',
            priority=brief_data.get('priority', 'medium')
        )
        session.add(brief)
        session.commit()
        
        logger.info(f"Generated gap brief for domain {domain_id}")
        
        return brief.to_dict()
        
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to generate gap brief: {e}")
        raise
        
    finally:
        session.close()


def generate_content_brief(
    domain_name: str,
    hallucination_claim: str = None,
    hallucination_type: str = None,
    correct_facts: str = '',
    business_summary: dict = None,
    target_query: str = None,
    gap_type: str = None
) -> Dict:
    """Generate a content brief using Claude CLI.
    
    Args:
        domain_name: Domain name.
        hallucination_claim: The false claim to address.
        hallucination_type: Type of hallucination.
        correct_facts: Correct information.
        business_summary: Business summary from crawl.
        target_query: Target query.
        gap_type: Type of gap if not hallucination-based.
        
    Returns:
        Brief data dictionary.
    """
    what_they_do = business_summary.get('what_they_do', '') if business_summary else ''
    key_services = business_summary.get('key_services', []) if business_summary else []
    unique_value = business_summary.get('unique_value', '') if business_summary else ''
    
    if hallucination_claim:
        prompt = f"""Generate a content brief to fix a hallucination about {domain_name}.

The hallucination: {hallucination_claim}
Type: {hallucination_type}
Correct facts: {correct_facts}

Business: {what_they_do}
Services: {', '.join(key_services)}
Unique value: {unique_value}

Generate a content brief with:
1. "title": A compelling title for the brief
2. "target_query": The search query this content should target
3. "key_facts": Array of 3-5 facts that must be included
4. "content_structure": Brief outline of the content
5. "where_to_publish": Recommended page or section
6. "expected_score_impact": Expected improvement (e.g., "+5-10% SoV")
7. "priority": low/medium/high/critical based on severity

Respond as JSON only."""
    else:
        prompt = f"""Generate a content brief to fill a coverage gap for {domain_name}.

Gap type: {gap_type or 'missing_coverage'}
Business: {what_they_do}
Services: {', '.join(key_services)}
Unique value: {unique_value}

Generate a content brief with:
1. "title": A compelling title for the brief
2. "target_query": The search query this content should target
3. "key_facts": Array of 3-5 facts that must be included
4. "content_structure": Brief outline of the content
5. "where_to_publish": Recommended page or section
6. "expected_score_impact": Expected improvement
7. "priority": low/medium/high/critical

Respond as JSON only."""

    system_prompt = "You are Peterman, a content strategy tool. Generate actionable content briefs."
    
    try:
        result = call_claude_cli(prompt, system_prompt, timeout=60)
        
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
        logger.error(f"Brief generation failed: {e}")
        return {
            'title': 'Content Brief',
            'target_query': target_query or '',
            'key_facts': [],
            'content_structure': 'To be defined',
            'where_to_publish': 'To be determined',
            'expected_score_impact': 'Unknown',
            'priority': 'medium'
        }


def get_domain_briefs(domain_id: UUID, status: Optional[str] = None) -> List[Dict]:
    """Get content briefs for a domain.
    
    Args:
        domain_id: UUID of the domain.
        status: Optional status filter.
        
    Returns:
        List of brief dictionaries.
    """
    session = get_session()
    
    try:
        query = session.query(ContentBrief).filter_by(domain_id=domain_id)
        if status:
            query = query.filter_by(status=status)
        
        briefs = query.order_by(ContentBrief.priority.desc(), ContentBrief.created_at.desc()).all()
        return [b.to_dict() for b in briefs]
        
    finally:
        session.close()


def get_brief(brief_id: int) -> Dict:
    """Get a specific content brief.
    
    Args:
        brief_id: ID of the brief.
        
    Returns:
        Brief dictionary.
    """
    session = get_session()
    
    try:
        brief = session.query(ContentBrief).filter_by(id=brief_id).first()
        if not brief:
            raise ValueError(f"Brief not found: {brief_id}")
        
        return brief.to_dict()
        
    finally:
        session.close()


def approve_brief(brief_id: int) -> Dict:
    """Approve a content brief.
    
    Args:
        brief_id: ID of the brief.
        
    Returns:
        Updated brief dictionary.
    """
    session = get_session()
    
    try:
        brief = session.query(ContentBrief).filter_by(id=brief_id).first()
        if not brief:
            raise ValueError(f"Brief not found: {brief_id}")
        
        brief.status = 'approved'
        brief.approved_at = datetime.utcnow()
        
        session.commit()
        
        return brief.to_dict()
        
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to approve brief: {e}")
        raise
        
    finally:
        session.close()


def mark_brief_deployed(brief_id: int) -> Dict:
    """Mark a brief as deployed.
    
    Args:
        brief_id: ID of the brief.
        
    Returns:
        Updated brief dictionary.
    """
    session = get_session()
    
    try:
        brief = session.query(ContentBrief).filter_by(id=brief_id).first()
        if not brief:
            raise ValueError(f"Brief not found: {brief_id}")
        
        brief.status = 'deployed'
        
        # Update hallucination if linked
        if brief.hallucination_id:
            from app.services.hallucination_detector import Hallucination
            hallucination = session.query(Hallucination).filter_by(id=brief.hallucination_id).first()
            if hallucination:
                hallucination.status = 'content_deployed'
        
        session.commit()
        
        return brief.to_dict()
        
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to mark brief deployed: {e}")
        raise
        
    finally:
        session.close()
