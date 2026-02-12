"""Ripple CRM — SQLAlchemy models."""

from app.models.base import Base
from app.models.contact import Contact
from app.models.company import Company
from app.models.interaction import Interaction
from app.models.relationship import Relationship
from app.models.deal import Deal
from app.models.commitment import Commitment
from app.models.tag import Tag, contact_tags
from app.models.task import Task
from app.models.note import Note
from app.models.privacy_consent import PrivacyConsent
from app.models.audit_log import AuditLog
from app.models.lead_score import LeadScore
from app.models.email import Email
from app.models.scoring_rule import ScoringRule

__all__ = [
    "Base",
    "Contact",
    "Company",
    "Interaction",
    "Relationship",
    "Deal",
    "Commitment",
    "Tag",
    "contact_tags",
    "Task",
    "Note",
    "PrivacyConsent",
    "AuditLog",
    "LeadScore",
    "Email",
    "ScoringRule",
]
