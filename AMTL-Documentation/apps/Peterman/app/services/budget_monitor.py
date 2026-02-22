"""
Budget monitoring service for Peterman.

Per-domain cost tracking with 80%/100% thresholds per KNW-002.
"""

import logging
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import func

from app.models.database import get_session
from app.models.domain import Domain
from app.models.budget import BudgetTracking

logger = logging.getLogger(__name__)

BUDGET_WARNING_THRESHOLD = 0.80  # 80%
BUDGET_HARD_THRESHOLD = 1.00  # 100%


def get_weekly_spend(domain_id: UUID) -> float:
    """Calculate total spend for the current rolling week.
    
    Args:
        domain_id: UUID of the domain.
        
    Returns:
        Total spend in AUD.
    """
    session = get_session()
    try:
        week_ago = datetime.utcnow() - timedelta(days=7)
        total = (
            session.query(func.sum(BudgetTracking.cost_aud))
            .filter(BudgetTracking.domain_id == domain_id)
            .filter(BudgetTracking.incurred_at >= week_ago)
            .scalar()
        )
        return float(total) if total else 0.0
        
    finally:
        session.close()


def check_budget(domain_id: UUID) -> dict:
    """Check budget status for a domain.
    
    Args:
        domain_id: UUID of the domain.
        
    Returns:
        Dictionary with budget status and warnings.
    """
    session = get_session()
    try:
        domain = session.get(Domain, domain_id)
        if not domain:
            raise ValueError(f"Domain {domain_id} not found")
        
        weekly_budget = domain.budget_weekly_aud
        current_spend = get_weekly_spend(domain_id)
        
        usage_ratio = current_spend / weekly_budget if weekly_budget > 0 else 0
        
        status = 'ok'
        warnings = []
        
        if usage_ratio >= BUDGET_HARD_THRESHOLD:
            status = 'exceeded'
            warnings.append(
                f"Budget exceeded: ${current_spend:.2f} / ${weekly_budget:.2f}"
            )
        elif usage_ratio >= BUDGET_WARNING_THRESHOLD:
            status = 'warning'
            warnings.append(
                f"Budget at {usage_ratio*100:.0f}%: ${current_spend:.2f} / ${weekly_budget:.2f}"
            )
        
        return {
            'domain_id': str(domain_id),
            'weekly_budget': weekly_budget,
            'current_spend': current_spend,
            'remaining': weekly_budget - current_spend,
            'usage_ratio': usage_ratio,
            'status': status,
            'warnings': warnings
        }
        
    finally:
        session.close()


def track_cost(
    domain_id: UUID,
    api_provider: str,
    cost_aud: float,
    description: str = None
) -> BudgetTracking:
    """Track an API cost.
    
    Args:
        domain_id: UUID of the domain.
        api_provider: Which API provider was used.
        cost_aud: Cost in AUD.
        description: Description of the API call.
        
    Returns:
        The created BudgetTracking instance.
    """
    session = get_session()
    try:
        tracking = BudgetTracking(
            domain_id=domain_id,
            api_provider=api_provider,
            cost_aud=cost_aud,
            description=description
        )
        session.add(tracking)
        session.commit()
        
        logger.info(
            f"Cost tracked: ${cost_aud:.4f} for {api_provider}",
            extra={
                'context': {
                    'domain_id': str(domain_id),
                    'api_provider': api_provider,
                    'cost_aud': cost_aud
                }
            }
        )
        
        return tracking
        
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to track cost: {e}")
        raise
        
    finally:
        session.close()


def can_proceed(domain_id: UUID) -> tuple[bool, str]:
    """Check if probing can proceed based on budget.
    
    Args:
        domain_id: UUID of the domain.
        
    Returns:
        Tuple of (can_proceed: bool, reason: str).
    """
    budget_status = check_budget(domain_id)
    
    if budget_status['status'] == 'exceeded':
        return False, f"Budget exceeded. Cannot proceed with API calls."
    
    if budget_status['status'] == 'warning':
        return True, f"Budget at {budget_status['usage_ratio']*100:.0f}%. Proceed with caution."
    
    return True, f"Budget OK. ${budget_status['remaining']:.2f} remaining."
