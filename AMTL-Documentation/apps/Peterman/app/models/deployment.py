"""
Deployment model for Peterman.

Handles deployments and rollback snapshots per DEC-011.
"""

import uuid
from datetime import datetime, timedelta
from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey

from app.models.database import Base, TimestampMixin


class Deployment(Base, TimestampMixin):
    """Deployment record per AMTL-PTR-TDD-1.0 Section 8.1.
    
    Attributes:
        deployment_id: Primary key UUID (stored as string for SQLite).
        domain_id: Reference to the domain.
        action_type: Type of action deployed.
        target_url: URL where the change was deployed.
        html_before: Full HTML before change.
        html_after: Full HTML after change.
        diff: Unified diff of changes.
        metadata_before: Metadata before change (stored as JSON text).
        metadata_after: Metadata after change (stored as JSON text).
        approval_id: Reference to approval if applicable.
        deployed_at: When deployment occurred.
        rollback_status: Snapshot status (available, used, expired).
        rollback_expires_at: When snapshot expires (30 days from capture).
        peterman_score_delta: Score change from deployment.
    """
    
    __tablename__ = 'deployments'
    
    deployment_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    domain_id = Column(String(36), ForeignKey('domains.domain_id'), nullable=False)
    action_type = Column(String(100), nullable=False)
    target_url = Column(String(500))
    html_before = Column(Text)
    html_after = Column(Text)
    diff = Column(Text)
    metadata_before = Column(Text)  # JSON stored as text
    metadata_after = Column(Text)  # JSON stored as text
    approval_id = Column(String(36))
    deployed_at = Column(DateTime, default=datetime.utcnow)
    rollback_status = Column(String(20), default='available')
    rollback_expires_at = Column(DateTime)
    peterman_score_delta = Column(Float)
    
    def __init__(self, *args, **kwargs):
        # Set 30-day expiry on creation
        if 'rollback_expires_at' not in kwargs:
            kwargs['rollback_expires_at'] = datetime.utcnow() + datetime.timedelta(days=30)
        super().__init__(*args, **kwargs)
    
    def to_dict(self) -> dict:
        """Convert deployment to dictionary representation."""
        return {
            'deployment_id': str(self.deployment_id),
            'domain_id': str(self.domain_id),
            'action_type': self.action_type,
            'target_url': self.target_url,
            'diff': self.diff,
            'approval_id': str(self.approval_id) if self.approval_id else None,
            'deployed_at': self.deployed_at.isoformat() if self.deployed_at else None,
            'rollback_status': self.rollback_status,
            'rollback_expires_at': self.rollback_expires_at.isoformat() if self.rollback_expires_at else None,
            'peterman_score_delta': self.peterman_score_delta,
        }
    
    def __repr__(self) -> str:
        return f"<Deployment(id={self.deployment_id}, type='{self.action_type}')>"
