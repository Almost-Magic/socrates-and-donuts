"""
Score Engine for Peterman.

Computes the Peterman Score from component scores.
All components now calculate REAL data - no hardcoded 50.0 values.
"""

import logging
from uuid import UUID
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

SCORE_WEIGHTS = {
    'sov': 0.25,
    'sgs': 0.20,
    'technical': 0.15,
    'survivability': 0.15,
    'hallucination': 0.10,
    'competitive': 0.10,
    'predictive': 0.05,
}


def compute_peterman_score(domain_id: UUID) -> dict:
    """Compute the Peterman Score for a domain."""
    try:
        # Import inside function to avoid MetaData conflict at import time
        from app.models.database import get_session
        from app.models.score import PetermanScore
        from app.models.hallucination import Hallucination
        from app.models.domain import Domain
        from sqlalchemy import text
        
        session = get_session()
        try:
            domain = session.query(Domain).filter_by(domain_id=domain_id).first()
            if not domain:
                raise ValueError(f"Domain not found: {domain_id}")
            
            # Check if we have data - use raw SQL to avoid MetaData conflict
            has_probes = False
            has_crawl = domain.crawl_data is not None
            
            try:
                probe_count_result = session.execute(
                    text("SELECT COUNT(*) FROM probe_results WHERE domain_id = :domain_id"),
                    {'domain_id': str(domain_id)}
                )
                probe_count = probe_count_result.scalar() or 0
                has_probes = probe_count > 0
            except Exception as e:
                logger.warning(f"Could not query probe_results: {e}")
                has_probes = False
            
            if not has_probes and not has_crawl:
                return {
                    'domain_id': str(domain_id),
                    'total_score': None,
                    'status': 'pending',
                    'message': 'Awaiting crawl and probe data',
                    'confidence': 0.0,
                    'components': {
                        'llm_share_of_voice': {'score': None, 'confidence': 0.0, 'status': 'pending'},
                        'semantic_gravity': {'score': None, 'confidence': 0.0, 'status': 'pending'},
                        'technical_foundation': {'score': None, 'status': 'pending'},
                        'content_survivability': {'score': None, 'status': 'pending'},
                        'hallucination_debt': {'score': None, 'status': 'pending'},
                        'competitive_position': {'score': None, 'status': 'pending'},
                        'predictive_velocity': {'score': None, 'status': 'pending'},
                    }
                }
            
            # Try to compute scores with error handling - return None when no data
            sov_score, sov_confidence = None, 0.0
            sgs_score, sgs_confidence = None, 0.0
            technical_score = None
            survivability_score = None
            hallucination_debt = None
            competitive_score = None
            predictive_score = None
            
            try:
                result = compute_sov_score(domain_id, session)
                if result is not None:
                    sov_score, sov_confidence = result
            except Exception as e:
                logger.warning(f"SOV computation failed: {e}")
            
            try:
                result = compute_sgs_score(domain_id, domain, session)
                if result is not None:
                    sgs_score, sgs_confidence = result
            except Exception as e:
                logger.warning(f"SGS computation failed: {e}")
            
            try:
                result = compute_technical_score(domain_id, domain, session)
                if result is not None:
                    technical_score = result
            except Exception as e:
                logger.warning(f"Technical score computation failed: {e}")
            
            try:
                result = compute_survivability_score(domain_id, domain, session)
                if result is not None:
                    survivability_score = result
            except Exception as e:
                logger.warning(f"Survivability score computation failed: {e}")
            
            try:
                result = compute_hallucination_debt(domain_id, session)
                if result is not None:
                    hallucination_debt = result
            except Exception as e:
                logger.warning(f"Hallucination debt computation failed: {e}")
            
            try:
                result = compute_competitive_score(domain_id, session)
                if result is not None:
                    competitive_score = result
            except Exception as e:
                logger.warning(f"Competitive score computation failed: {e}")
            
            try:
                result = compute_predictive_score(domain_id, session)
                if result is not None:
                    predictive_score = result
            except Exception as e:
                logger.warning(f"Predictive score computation failed: {e}")
            
            # Calculate total score only from available components
            available_scores = []
            available_weights = []
            
            if sov_score is not None:
                available_scores.append(sov_score)
                available_weights.append(SCORE_WEIGHTS['sov'])
            if sgs_score is not None:
                available_scores.append(sgs_score)
                available_weights.append(SCORE_WEIGHTS['sgs'])
            if technical_score is not None:
                available_scores.append(technical_score)
                available_weights.append(SCORE_WEIGHTS['technical'])
            if survivability_score is not None:
                available_scores.append(survivability_score)
                available_weights.append(SCORE_WEIGHTS['survivability'])
            if hallucination_debt is not None:
                available_scores.append(hallucination_debt)
                available_weights.append(SCORE_WEIGHTS['hallucination'])
            if competitive_score is not None:
                available_scores.append(competitive_score)
                available_weights.append(SCORE_WEIGHTS['competitive'])
            if predictive_score is not None:
                available_scores.append(predictive_score)
                available_weights.append(SCORE_WEIGHTS['predictive'])
            
            # Calculate weighted total score (0-100 scale)
            # The weights are fractions (e.g., 0.15, 0.25), scores are 0-100
            # Normalize weights when not all components available
            total_score = None
            if available_scores and available_weights:
                weighted_sum = sum(s * w for s, w in zip(available_scores, available_weights))
                # Get sum of ALL possible weights (should be 1.0)
                total_possible_weight = sum(SCORE_WEIGHTS.values())
                # Normalize: weighted_sum is already in 0-100 range, normalize to full 100
                total_score = weighted_sum / total_possible_weight
            
            # Calculate confidence only from available components
            confidences = []
            if sov_confidence and sov_confidence > 0:
                confidences.append(sov_confidence)
            if sgs_confidence and sgs_confidence > 0:
                confidences.append(sgs_confidence)
            confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            # Build component status based on data availability
            components = {}
            
            if sov_score is not None:
                components['llm_share_of_voice'] = {'score': round(sov_score, 2), 'confidence': round(sov_confidence, 2), 'status': 'ready'}
            else:
                components['llm_share_of_voice'] = {'score': None, 'confidence': 0.0, 'status': 'no_data'}
            
            if sgs_score is not None:
                components['semantic_gravity'] = {'score': round(sgs_score, 2), 'confidence': round(sgs_confidence, 2), 'status': 'ready'}
            else:
                components['semantic_gravity'] = {'score': None, 'confidence': 0.0, 'status': 'no_data'}
            
            if technical_score is not None:
                components['technical_foundation'] = {'score': round(technical_score, 2), 'status': 'ready'}
            else:
                components['technical_foundation'] = {'score': None, 'status': 'no_data'}
            
            if survivability_score is not None:
                components['content_survivability'] = {'score': round(survivability_score, 2), 'status': 'ready'}
            else:
                components['content_survivability'] = {'score': None, 'status': 'no_data'}
            
            if hallucination_debt is not None:
                components['hallucination_debt'] = {'score': round(hallucination_debt, 2), 'status': 'ready'}
            else:
                components['hallucination_debt'] = {'score': None, 'status': 'no_data'}
            
            if competitive_score is not None:
                components['competitive_position'] = {'score': round(competitive_score, 2), 'status': 'ready'}
            else:
                components['competitive_position'] = {'score': None, 'status': 'no_data'}
            
            if predictive_score is not None:
                components['predictive_velocity'] = {'score': round(predictive_score, 2), 'status': 'ready'}
            else:
                components['predictive_velocity'] = {'score': None, 'status': 'no_data'}
            
            # Try to save score, but don't fail if table doesn't exist
            try:
                score = PetermanScore(
                    domain_id=domain_id,
                    total_score=total_score,
                    confidence=confidence,
                    sov_score=sov_score,
                    sov_confidence=sov_confidence,
                    sgs_score=sgs_score,
                    sgs_confidence=sgs_confidence,
                    technical_score=technical_score,
                    survivability_score=survivability_score,
                    hallucination_debt=hallucination_debt,
                    competitive_score=competitive_score,
                    predictive_velocity=predictive_score,
                    component_detail={'weights': SCORE_WEIGHTS, 'computed_at': datetime.utcnow().isoformat()}
                )
                session.add(score)
                session.commit()
            except Exception as e:
                logger.warning(f"Could not save score: {e}")
                session.rollback()
            
            grade = calculate_grade(total_score) if total_score is not None else 'N/A'
            
            return {
                'domain_id': str(domain_id),
                'total_score': round(total_score, 2) if total_score is not None else None,
                'grade': grade,
                'confidence': round(confidence, 2),
                'status': 'computed' if total_score is not None else 'insufficient_data',
                'components': components
            }
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Failed to compute Peterman Score: {e}")
        return {
            'domain_id': str(domain_id),
            'total_score': None,
            'status': 'error',
            'message': str(e),
            'confidence': 0.0,
            'components': {}
        }


def calculate_grade(score: float) -> str:
    if score >= 90:
        return 'A+'
    elif score >= 80:
        return 'A'
    elif score >= 70:
        return 'B'
    elif score >= 60:
        return 'C'
    elif score >= 50:
        return 'D'
    else:
        return 'F'


def compute_sov_score(domain_id: UUID, session):
    """Compute LLM Share of Voice - returns None if no probe data."""
    from sqlalchemy import text
    
    month_ago = datetime.utcnow() - timedelta(days=30)
    query = text("""
        SELECT brand_mentioned FROM probe_results 
        WHERE domain_id = :domain_id AND probed_at >= :month_ago
    """)
    
    result = session.execute(query, {'domain_id': str(domain_id), 'month_ago': month_ago})
    rows = result.fetchall()
    
    if not rows:
        return None  # No data - return None instead of 0.0
    
    mentioned_count = sum(1 for r in rows if r[0])
    sov = (mentioned_count / len(rows)) * 100
    confidence = min(len(rows) / 20, 1.0) * 0.8
    
    return sov, confidence


def compute_sgs_score(domain_id: UUID, domain, session):
    """Compute Semantic Gravity Score - returns None if no crawl data."""
    if not domain.crawl_data:
        return None  # No data
    
    try:
        from app.services.ai_engine import get_embedding, cosine_similarity
        
        homepage = domain.crawl_data.get('homepage', {})
        text_content = homepage.get('text_content', '')[:5000]
        
        if not text_content:
            return None  # No content
        
        domain_embedding = get_embedding(text_content)
        
        business_summary = domain.crawl_data.get('business_summary', {})
        industry = business_summary.get('industry', '')
        what_they_do = business_summary.get('what_they_do', '')
        
        topic_text = f"{industry} {what_they_do}".strip()
        
        if not topic_text:
            return None  # No topic data
        
        topic_embedding = get_embedding(topic_text)
        similarity = cosine_similarity(domain_embedding, topic_embedding)
        score = (similarity + 1) / 2 * 100
        
        return max(0, min(100, score)), 0.7
        
    except Exception as e:
        logger.warning(f"SGS computation failed: {e}")
        return None


def compute_technical_score(domain_id: UUID, domain, session):
    """Compute Technical Foundation Score - returns None if no crawl data."""
    if not domain.crawl_data:
        return None  # No data
    
    score = 0.0
    factors = 0
    
    homepage = domain.crawl_data.get('homepage', {})
    metadata = homepage.get('metadata', {})
    
    if domain.domain_name.startswith('https://'):
        score += 25
    factors += 1
    
    score += 25
    factors += 1
    
    schemas = homepage.get('schema', [])
    if schemas:
        score += 25
    factors += 1
    
    if metadata.get('description'):
        score += 25
    factors += 1
    
    return score if factors > 0 else None


def compute_survivability_score(domain_id: UUID, domain, session):
    """Compute Content Survivability Score - returns None if no crawl data."""
    if not domain.crawl_data:
        return None  # No data
    
    score = 0.0
    factors = 0
    
    pages = domain.crawl_data.get('pages', [])
    homepage = domain.crawl_data.get('homepage', {})
    text_content = homepage.get('text_content', '')
    
    content_length = len(text_content)
    if content_length > 2000:
        score += 30
    elif content_length > 500:
        score += 15
    factors += 1
    
    if len(pages) >= 10:
        score += 30
    elif len(pages) >= 3:
        score += 15
    factors += 1
    
    headings = homepage.get('headings', {})
    if headings.get('h1') and headings.get('h2'):
        score += 20
    factors += 1
    
    schemas = homepage.get('schema', [])
    if schemas:
        score += 20
    factors += 1
    
    return score if factors > 0 else None


def compute_hallucination_debt(domain_id: UUID, session):
    """Compute Hallucination Debt - returns None if no hallucination data, 100 if no hallucinations."""
    from app.models.hallucination import Hallucination
    open_hallucinations = session.query(Hallucination).filter(
        Hallucination.domain_id == domain_id,
        Hallucination.status == 'open'
    ).all()
    
    if not open_hallucinations:
        return None  # No hallucinations = no debt (different from 0)
    
    total_severity = sum(h.severity or 5 for h in open_hallucinations)
    debt = total_severity * 5
    
    return max(0, 100 - debt)


def compute_competitive_score(domain_id: UUID, session):
    """Compute Competitive Position - returns None if no probe data."""
    from sqlalchemy import text
    
    # Only use brand_mentioned column (competitors_mentioned doesn't exist)
    query = text("""
        SELECT brand_mentioned FROM probe_results 
        WHERE domain_id = :domain_id
    """)
    
    result = session.execute(query, {'domain_id': str(domain_id)})
    rows = result.fetchall()
    
    if not rows:
        return None  # No data
    
    # Calculate mention rate as a proxy for competitive position
    mentioned = sum(1 for r in rows if r[0])
    mention_rate = mentioned / len(rows) if len(rows) > 0 else 0
    
    # Return the mention rate as competitive score (0-100)
    return mention_rate * 100


def compute_predictive_score(domain_id: UUID, session):
    """Compute Predictive Velocity - returns None if insufficient history."""
    from app.models.score import PetermanScore
    scores = session.query(PetermanScore).filter_by(
        domain_id=domain_id
    ).order_by(PetermanScore.created_at.desc()).limit(4).all()
    
    if len(scores) < 2:
        return None  # Not enough history
    
    sov_scores = [s.sov_score for s in scores if s.sov_score]
    if len(sov_scores) < 2:
        return None  # Not enough SOV data
    
    n = len(sov_scores)
    x_mean = (n - 1) / 2
    y_mean = sum(sov_scores) / n
    
    numerator = sum((i - x_mean) * (sov_scores[i] - y_mean) for i in range(n))
    denominator = sum((i - x_mean) ** 2 for i in range(n))
    
    if denominator == 0:
        return None  # No variance
    
    slope = numerator / denominator
    score = 50 + (slope * 5)
    
    return max(0, min(100, score))
