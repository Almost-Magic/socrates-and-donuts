"""
Keyword/Query Engine for Peterman.

Generates 45 target queries from crawl data per DEC-005.
Uses Claude CLI for query generation.
"""

import logging
import json
from datetime import datetime
from typing import List, Dict, Optional
from uuid import UUID

from app.models.database import get_session
from app.models.keyword_engine import TargetQuery

# Lazy import to avoid circular import
def _get_claude_cli():
    from app.services.ai_engine import call_claude_cli
    return call_claude_cli

logger = logging.getLogger(__name__)

# Query categories per DEC-005
QUERY_CATEGORIES = {
    'brand': {'count': 20, 'priority': 'high', 'description': 'Direct brand queries'},
    'comparison': {'count': 10, 'priority': 'medium', 'description': 'Comparison queries'},
    'category': {'count': 10, 'priority': 'medium', 'description': 'Category/product queries'},
    'reputation': {'count': 5, 'priority': 'medium', 'description': 'Reputation queries'},
}


def generate_queries_from_crawl(crawl_data: Dict, domain_name: str) -> List[Dict]:
    """Generate 45 target queries from crawl data using Claude CLI.
    
    Args:
        crawl_data: Crawl data from crawler service.
        domain_name: Domain name.
        
    Returns:
        List of query dictionaries.
    """
    business_summary = crawl_data.get('business_summary', {})
    homepage = crawl_data.get('homepage', {})
    metadata = homepage.get('metadata', {})
    
    what_they_do = business_summary.get('what_they_do', 'this business')
    key_services = business_summary.get('key_services', [])
    industry = business_summary.get('industry', 'this industry')
    unique_value = business_summary.get('unique_value', '')
    
    services_text = ', '.join(key_services) if key_services else 'their services'
    
    prompt = f"""Generate 45 target queries for LLM probing about a brand.

Business: {domain_name}
What they do: {what_they_do}
Key services: {services_text}
Industry: {industry}
Unique value: {unique_value}

Generate queries in these categories:
- 20 BRAND queries: Direct queries about the brand (e.g., "{domain_name} reviews", "is {domain_name} good")
- 10 COMPARISON queries: Comparing with competitors (e.g., "{domain_name} vs [competitor]", "best [service] [location]")
- 10 CATEGORY queries: General category searches (e.g., "[service] near me", "best [service] in [location]")
- 5 REPUTATION queries: Trust and review queries (e.g., "{domain_name} complaints", "[domain_name] trust score")

For each query provide:
1. The query text
2. Category (brand/comparison/category/reputation)
3. Priority (high/medium/low)
4. What the ideal answer should contain (expected_answer)

Respond as JSON array only, no other text. Example format:
[
  {{"query": "...", "category": "brand", "priority": "high", "expected_answer": "..."}},
  ...
]"""

    system_prompt = "You are Peterman, a brand intelligence analysis tool. Generate accurate, realistic search queries."
    
    try:
        call_claude_cli = _get_claude_cli()
        result = call_claude_cli(prompt, system_prompt, timeout=60)
        
        # Parse JSON response
        result = result.strip()
        if result.startswith('```json'):
            result = result[7:]
        if result.startswith('```'):
            result = result[3:]
        if result.endswith('```'):
            result = result[:-3]
        
        queries = json.loads(result.strip())
        
        # Validate we got 45 queries
        if len(queries) < 45:
            logger.warning(f"Only generated {len(queries)} queries, expected 45")
        
        return queries[:45]  # Ensure max 45
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse query generation: {e}")
        raise
    except Exception as e:
        logger.error(f"Query generation failed: {e}")
        raise


def create_target_queries(domain_id: UUID, crawl_data: Dict) -> Dict:
    """Create target queries for a domain from crawl data.
    
    Args:
        domain_id: UUID of the domain.
        crawl_data: Crawl data from crawler.
        
    Returns:
        Creation results.
    """
    session = get_session()
    
    try:
        # Generate queries using Claude CLI
        queries_data = generate_queries_from_crawl(crawl_data, 
            crawl_data.get('homepage', {}).get('metadata', {}).get('title', 'the domain'))
        
        # Create query records
        created_queries = []
        for q in queries_data:
            query = TargetQuery(
                domain_id=domain_id,
                query=q.get('query', ''),
                category=q.get('category', 'brand'),
                priority=q.get('priority', 'medium'),
                expected_answer=q.get('expected_answer'),
                is_approved=False,
            )
            session.add(query)
            created_queries.append(query)
        
        session.commit()
        
        logger.info(f"Created {len(created_queries)} target queries for domain {domain_id}")
        
        return {
            'domain_id': str(domain_id),
            'queries_created': len(created_queries),
            'by_category': {
                'brand': len([q for q in created_queries if q.category == 'brand']),
                'comparison': len([q for q in created_queries if q.category == 'comparison']),
                'category': len([q for q in created_queries if q.category == 'category']),
                'reputation': len([q for q in created_queries if q.category == 'reputation']),
            }
        }
        
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to create target queries: {e}")
        raise
        
    finally:
        session.close()


def get_domain_queries(domain_id: UUID) -> List[Dict]:
    """Get all target queries for a domain.
    
    Args:
        domain_id: UUID of the domain.
        
    Returns:
        List of query dictionaries.
    """
    session = get_session()
    
    try:
        queries = session.query(TargetQuery).filter_by(domain_id=domain_id).order_by(
            TargetQuery.category, TargetQuery.priority
        ).all()
        
        return [q.to_dict() for q in queries]
        
    finally:
        session.close()


def get_unapproved_queries(domain_id: UUID) -> List[Dict]:
    """Get unapproved queries for a domain (for approval inbox).
    
    Args:
        domain_id: UUID of the domain.
        
    Returns:
        List of unapproved query dictionaries.
    """
    session = get_session()
    
    try:
        queries = session.query(TargetQuery).filter_by(
            domain_id=domain_id, 
            is_approved=False
        ).order_by(TargetQuery.priority.desc()).all()
        
        return [q.to_dict() for q in queries]
        
    finally:
        session.close()


def update_query(query_id: int, updates: Dict) -> Dict:
    """Update a target query.
    
    Args:
        query_id: ID of the query.
        updates: Fields to update.
        
    Returns:
        Updated query dictionary.
    """
    session = get_session()
    
    try:
        query = session.query(TargetQuery).filter_by(id=query_id).first()
        if not query:
            raise ValueError(f"Query not found: {query_id}")
        
        for key, value in updates.items():
            if hasattr(query, key):
                setattr(query, key, value)
        
        query.updated_at = datetime.utcnow()
        session.commit()
        
        return query.to_dict()
        
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to update query {query_id}: {e}")
        raise
        
    finally:
        session.close()


def approve_query(query_id: int) -> Dict:
    """Approve a target query.
    
    Args:
        query_id: ID of the query.
        
    Returns:
        Approved query dictionary.
    """
    return update_query(query_id, {'is_approved': True})


def approve_all_queries(domain_id: UUID) -> Dict:
    """Approve all queries for a domain.
    
    Args:
        domain_id: UUID of the domain.
        
    Returns:
        Approval results.
    """
    session = get_session()
    
    try:
        count = session.query(TargetQuery).filter_by(
            domain_id=domain_id, 
            is_approved=False
        ).update({'is_approved': True, 'updated_at': datetime.utcnow()})
        
        session.commit()
        
        logger.info(f"Approved {count} queries for domain {domain_id}")
        
        return {
            'domain_id': str(domain_id),
            'approved_count': count
        }
        
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to approve queries: {e}")
        raise
        
    finally:
        session.close()


def get_approved_queries(domain_id: UUID) -> List[Dict]:
    """Get approved queries ready for probing.
    
    Args:
        domain_id: UUID of the domain.
        
    Returns:
        List of approved query dictionaries.
    """
    session = get_session()
    
    try:
        queries = session.query(TargetQuery).filter_by(
            domain_id=domain_id, 
            is_approved=True
        ).order_by(TargetQuery.priority.desc()).all()
        
        return [q.to_dict() for q in queries]
        
    finally:
        session.close()
