"""
Audit log model for Peterman.

Immutable append-only audit trail per DEC-008.
"""

import uuid
import json
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey

from app.models.database import Base, TimestampMixin


class AuditLog(Base, TimestampMixin):
    """Immutable audit log entry per AMTL-PTR-TDD-1.0 Section 9.
    
    Per DEC-008: INSERT-only permissions for application role.
    
    Attributes:
        entry_id: Primary key UUID (stored as string for SQLite).
        domain_id: Reference to the domain.
        timestamp: When the action occurred.
        action_type: Type of action (e.g., 'domain_created', 'deployment_executed').
        action_detail: Full JSON payload of the action.
        initiated_by: Who initiated (peterman_auto, operator_manual, elaine_voice).
        approval_gate: Gate level used (auto, low, medium, hard, prohibited).
        approved_by: Who approved (system, operator:[id]).
        approved_at: When approval was given.
        outcome: Action outcome (success, failed, rolled_back, pending).
        snapshot_id: Reference to snapshot if applicable.
        notes: Additional notes.
    """
    
    __tablename__ = 'audit_log'
    
    entry_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    domain_id = Column(String(36), ForeignKey('domains.domain_id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    action_type = Column(String(100), nullable=False)
    action_detail = Column(Text, nullable=False)  # JSON stored as text
    initiated_by = Column(String(50), nullable=False)
    approval_gate = Column(String(20))
    approved_by = Column(String(100))
    approved_at = Column(DateTime)
    outcome = Column(String(20), default='pending')
    snapshot_id = Column(String(36))
    notes = Column(Text)
    
    def to_dict(self) -> dict:
        """Convert audit entry to dictionary representation."""
        return {
            'entry_id': str(self.entry_id),
            'domain_id': str(self.domain_id),
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'action_type': self.action_type,
            'action_detail': self.action_detail,
            'initiated_by': self.initiated_by,
            'approval_gate': self.approval_gate,
            'approved_by': self.approved_by,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'outcome': self.outcome,
            'snapshot_id': str(self.snapshot_id) if self.snapshot_id else None,
            'notes': self.notes,
        }
    
    def __repr__(self) -> str:
        return f"<AuditLog(id={self.entry_id}, type='{self.action_type}')>"
