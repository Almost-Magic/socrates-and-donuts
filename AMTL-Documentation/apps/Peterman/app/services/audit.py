"""
Audit logging service for Peterman.

Append-only audit trail per DEC-008.
"""

import logging
from datetime import datetime
from uuid import UUID

from app.models.database import get_session
from app.models.audit import AuditLog

logger = logging.getLogger(__name__)


def log_audit_entry(
    domain_id: UUID,
    action_type: str,
    action_detail: dict,
    initiated_by: str,
    approval_gate: str = None,
    approved_by: str = None,
    approved_at: datetime = None,
    outcome: str = 'pending',
    snapshot_id: UUID = None,
    notes: str = None
) -> AuditLog:
    """Create an immutable audit log entry.
    
    Per DEC-008: This is the only way to write to the audit_log table.
    
    Args:
        domain_id: UUID of the domain this action relates to.
        action_type: Type of action (e.g., 'domain_created', 'deployment_executed').
        action_detail: Full JSON payload of the action.
        initiated_by: Who initiated (peterman_auto, operator_manual, elaine_voice).
        approval_gate: Gate level used (auto, low, medium, hard, prohibited).
        approved_by: Who approved (system, operator:[id]).
        approved_at: When approval was given.
        outcome: Action outcome (success, failed, rolled_back, pending).
        snapshot_id: Reference to snapshot if applicable.
        notes: Additional notes.
        
    Returns:
        The created AuditLog instance.
    """
    session = get_session()
    try:
        entry = AuditLog(
            domain_id=domain_id,
            action_type=action_type,
            action_detail=action_detail,
            initiated_by=initiated_by,
            approval_gate=approval_gate,
            approved_by=approved_by,
            approved_at=approved_at,
            outcome=outcome,
            snapshot_id=snapshot_id,
            notes=notes
        )
        session.add(entry)
        session.commit()
        
        logger.info(
            f"Audit entry created: {action_type}",
            extra={
                'context': {
                    'domain_id': str(domain_id),
                    'action_type': action_type,
                    'entry_id': str(entry.entry_id)
                }
            }
        )
        
        return entry
        
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to create audit entry: {e}")
        raise
        
    finally:
        session.close()


def get_audit_trail(domain_id: UUID, limit: int = 100) -> list:
    """Get audit trail for a domain.
    
    Args:
        domain_id: UUID of the domain.
        limit: Maximum number of entries to return.
        
    Returns:
        List of AuditLog dictionaries.
    """
    session = get_session()
    try:
        entries = (
            session.query(AuditLog)
            .filter_by(domain_id=domain_id)
            .order_by(AuditLog.timestamp.desc())
            .limit(limit)
            .all()
        )
        return [e.to_dict() for e in entries]
        
    finally:
        session.close()
