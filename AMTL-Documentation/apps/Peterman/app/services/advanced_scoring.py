"""
Advanced Scoring Features for Peterman.

Adds sophisticated metrics beyond basic SoV:
- Multi-LLM Consensus Presence Score
- Zero-Click Authority Index
- Conversation Stickiness Score
- Authority Decay Detection
- Retrain-Pulse Watcher
"""

import logging
from uuid import UUID
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


def compute_multi_llm_consensus(domain_id: UUID) -> Dict[str, Any]:
    """
    Multi-LLM Consensus Presence Score.
    
    Measures how consistently a brand is mentioned across ALL LLMs.
    High consensus = strong brand presence. Low consensus = inconsistent.
    
    Returns:
        - consensus_score (0-100): Percentage of LLMs that mention the brand
        - providers_mentioned: List of providers where brand was mentioned
        - providers_total: Total number of providers queried
    """
    from app.models.database import get_session
    from sqlalchemy import text
    
    session = get_session()
    try:
        # Get unique providers probed
        query = text("""
            SELECT DISTINCT provider FROM probe_results 
            WHERE domain_id = :domain_id
        """)
        result = session.execute(query, {'domain_id': str(domain_id)})
        all_providers = [r[0] for r in result.fetchall() if r[0]]
        
        if not all_providers:
            return {
                'consensus_score': None,
                'status': 'no_data',
                'message': 'No probe data available',
            }
        
        # Get providers where brand was mentioned
        mention_query = text("""
            SELECT DISTINCT provider FROM probe_results 
            WHERE domain_id = :domain_id AND brand_mentioned = true
        """)
        result = session.execute(mention_query, {'domain_id': str(domain_id)})
        mentioned_providers = [r[0] for r in result.fetchall() if r[0]]
        
        # Calculate consensus
        consensus_score = (len(mentioned_providers) / len(all_providers)) * 100 if all_providers else 0
        
        return {
            'consensus_score': round(consensus_score, 2),
            'providers_mentioned': mentioned_providers,
            'providers_total': len(all_providers),
            'providers_absent': list(set(all_providers) - set(mentioned_providers)),
            'status': 'ready',
        }
        
    finally:
        session.close()


def compute_zero_click_authority(domain_id: UUID) -> Dict[str, Any]:
    """
    Zero-Click Authority Index.
    
    Measures whether LLMs cite the brand as an authoritative source
    when answering queries - not just mentioning, but citing as source.
    
    This requires enhanced probe data with citation tracking.
    For now, uses brand_mentioned as a proxy.
    """
    from app.models.database import get_session
    from sqlalchemy import text
    
    session = get_session()
    try:
        # For now, use brand_mentioned as proxy for authority
        # In production, this would track actual citations
        query = text("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN brand_mentioned = true THEN 1 ELSE 0 END) as mentioned
            FROM probe_results 
            WHERE domain_id = :domain_id
        """)
        result = session.execute(query, {'domain_id': str(domain_id)})
        row = result.fetchone()
        
        if not row or row[0] == 0:
            return {
                'authority_index': None,
                'status': 'no_data',
                'message': 'No probe data available',
            }
        
        total = row[0]
        mentioned = row[1] or 0
        
        # Authority index = mention rate (as proxy for citation)
        authority_index = (mentioned / total) * 100
        
        return {
            'authority_index': round(authority_index, 2),
            'mentions': mentioned,
            'total_probes': total,
            'status': 'ready',
            'note': 'Based on brand mentions - actual citation tracking requires enhanced probes',
        }
        
    finally:
        session.close()


def compute_conversation_stickiness(domain_id: UUID) -> Dict[str, Any]:
    """
    Conversation Stickiness Score.
    
    Measures whether LLMs keep referencing the brand in multi-turn conversations.
    Probes: ask follow-up questions - does LLM still reference the brand?
    
    Requires multi-turn probe data. Uses latest probe as proxy.
    """
    from app.models.database import get_session
    from sqlalchemy import text
    
    session = get_session()
    try:
        # Get latest probes for each query (proxy for follow-up capability)
        query = text("""
            SELECT query_text, brand_mentioned, provider
            FROM probe_results 
            WHERE domain_id = :domain_id
            ORDER BY probed_at DESC
            LIMIT 50
        """)
        result = session.execute(query, {'domain_id': str(domain_id)})
        probes = result.fetchall()
        
        if not probes:
            return {
                'stickiness_score': None,
                'status': 'no_data',
                'message': 'No multi-turn probe data',
            }
        
        # Group by provider
        provider_stickiness = {}
        for probe in probes:
            query_text, brand_mentioned, provider = probe
            if provider not in provider_stickiness:
                provider_stickiness[provider] = {'mentions': 0, 'total': 0}
            
            provider_stickiness[provider]['total'] += 1
            if brand_mentioned:
                provider_stickiness[provider]['mentions'] += 1
        
        # Calculate average stickiness
        total_mentions = sum(p['mentions'] for p in provider_stickiness.values())
        total_probes = sum(p['total'] for p in provider_stickiness.values())
        
        stickiness_score = (total_mentions / total_probes * 100) if total_probes > 0 else 0
        
        return {
            'stickiness_score': round(stickiness_score, 2),
            'provider_breakdown': {
                k: round(v['mentions'] / v['total'] * 100, 2) if v['total'] > 0 else 0
                for k, v in provider_stickiness.items()
            },
            'status': 'ready',
        }
        
    finally:
        session.close()


def compute_authority_decay(domain_id: UUID) -> Dict[str, Any]:
    """
    Authority Decay Detection.
    
    Compares current SoV to 30-day and 90-day historical SoV.
    Alerts when decay exceeds threshold (e.g., 20% drop).
    """
    from app.models.database import get_session
    from app.models.score import PetermanScore
    from sqlalchemy import text
    
    session = get_session()
    try:
        now = datetime.utcnow()
        thirty_days_ago = now - timedelta(days=30)
        ninety_days_ago = now - timedelta(days=90)
        
        # Get current SoV (most recent)
        current_query = text("""
            SELECT sov_score FROM peterman_scores 
            WHERE domain_id = :domain_id 
            ORDER BY created_at DESC LIMIT 1
        """)
        result = session.execute(current_query, {'domain_id': str(domain_id)})
        current_row = result.fetchone()
        current_sov = current_row[0] if current_row else None
        
        if current_sov is None:
            return {
                'decay_status': 'no_data',
                'message': 'No current score data',
            }
        
        # Get 30-day average SoV
        thirty_query = text("""
            SELECT AVG(sov_score) FROM peterman_scores 
            WHERE domain_id = :domain_id 
            AND created_at >= :thirty_days_ago
        """)
        result = session.execute(thirty_query, {
            'domain_id': str(domain_id),
            'thirty_days_ago': thirty_days_ago
        })
        thirty_day_avg = result.scalar() or 0
        
        # Get 90-day average SoV
        ninety_query = text("""
            SELECT AVG(sov_score) FROM peterman_scores 
            WHERE domain_id = :domain_id 
            AND created_at >= :ninety_days_ago
        """)
        result = session.execute(ninety_query, {
            'domain_id': str(domain_id),
            'ninety_days_ago': ninety_days_ago
        })
        ninety_day_avg = result.scalar() or 0
        
        # Calculate decay
        decay_30_day = ((thirty_day_avg - current_sov) / thirty_day_avg * 100) if thirty_day_avg > 0 else 0
        decay_90_day = ((ninety_day_avg - current_sov) / ninety_day_avg * 100) if ninety_day_avg > 0 else 0
        
        # Determine status
        threshold = 20  # Alert if >20% decay
        if decay_30_day > threshold:
            status = 'critical'
            message = f'Authority dropped {abs(decay_30_day):.1f}% in 30 days'
        elif decay_90_day > threshold:
            status = 'warning'
            message = f'Authority dropped {abs(decay_90_day):.1f}% in 90 days'
        elif decay_30_day > 0 or decay_90_day > 0:
            status = 'declining'
            message = 'Minor authority decay detected'
        else:
            status = 'stable'
            message = 'Authority is stable or growing'
        
        return {
            'current_sov': round(current_sov, 2),
            'thirty_day_avg': round(thirty_day_avg, 2) if thirty_day_avg else None,
            'ninety_day_avg': round(ninety_day_avg, 2) if ninety_day_avg else None,
            'decay_30_day': round(decay_30_day, 2),
            'decay_90_day': round(decay_90_day, 2),
            'status': status,
            'message': message,
            'alert': decay_30_day > threshold or decay_90_day > threshold,
        }
        
    finally:
        session.close()


def detect_retrain_pulse(domain_id: UUID) -> Dict[str, Any]:
    """
    Retrain-Pulse Watcher.
    
    Detects when LLMs update their models (sudden SoV shifts across all queries).
    Triggers re-probe burst within 48 hours.
    Flags LCRI scores for re-computation.
    """
    from app.models.database import get_session
    from sqlalchemy import text
    
    session = get_session()
    try:
        # Get SoV changes over time - look for sudden shifts
        query = text("""
            SELECT created_at, sov_score FROM peterman_scores 
            WHERE domain_id = :domain_id 
            AND sov_score IS NOT NULL
            ORDER BY created_at DESC
            LIMIT 30
        """)
        result = session.execute(query, {'domain_id': str(domain_id)})
        scores = result.fetchall()
        
        if len(scores) < 5:
            return {
                'pulse_detected': False,
                'status': 'insufficient_data',
                'message': 'Not enough score history to detect pulses',
            }
        
        # Calculate day-over-day changes
        changes = []
        for i in range(len(scores) - 1):
            if scores[i][1] and scores[i+1][1]:
                change = scores[i][1] - scores[i+1][1]
                changes.append({
                    'date': scores[i][0],
                    'change': change,
                })
        
        if not changes:
            return {
                'pulse_detected': False,
                'status': 'no_variance',
                'message': 'No variance in scores',
            }
        
        # Detect significant sudden changes (>30% in a day)
        significant_changes = [c for c in changes if abs(c['change']) > 30]
        
        if significant_changes:
            # Check if it's recent (within last 7 days)
            recent_pulse = any(
                c['date'] > datetime.utcnow() - timedelta(days=7) 
                for c in significant_changes
            )
            
            if recent_pulse:
                return {
                    'pulse_detected': True,
                    'status': 'retrain_detected',
                    'message': 'LLM model update likely detected - re-probing recommended',
                    'significant_changes': significant_changes[:3],
                    'action_required': True,
                    'recommended_actions': [
                        'Trigger re-probe burst within 48 hours',
                        'Flag LCRI scores for re-computation',
                        'Notify operator of model change',
                    ],
                }
        
        return {
            'pulse_detected': False,
            'status': 'stable',
            'message': 'No LLM retrain detected',
            'max_single_day_change': max(abs(c['change']) for c in changes) if changes else 0,
        }
        
    finally:
        session.close()


def get_advanced_metrics(domain_id: UUID) -> Dict[str, Any]:
    """Get all advanced metrics."""
    
    consensus = compute_multi_llm_consensus(domain_id)
    authority = compute_zero_click_authority(domain_id)
    stickiness = compute_conversation_stickiness(domain_id)
    decay = compute_authority_decay(domain_id)
    pulse = detect_retrain_pulse(domain_id)
    
    # Composite advanced score
    available_scores = []
    if consensus.get('consensus_score') is not None:
        available_scores.append(consensus['consensus_score'])
    if authority.get('authority_index') is not None:
        available_scores.append(authority['authority_index'])
    if stickiness.get('stickiness_score') is not None:
        available_scores.append(stickiness['stickiness_score'])
    
    advanced_score = sum(available_scores) / len(available_scores) if available_scores else None
    
    return {
        'advanced_score': round(advanced_score, 2) if advanced_score else None,
        'multi_llm_consensus': consensus,
        'zero_click_authority': authority,
        'conversation_stickiness': stickiness,
        'authority_decay': decay,
        'retrain_pulse': pulse,
        'generated_at': datetime.utcnow().isoformat(),
    }
