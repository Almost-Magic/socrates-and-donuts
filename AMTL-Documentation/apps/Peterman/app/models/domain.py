"""
Domain model for Peterman.

Represents a managed domain with its configuration and status.
Per DEC-001: multi-domain architecture from day one.
"""

import uuid
import json
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON
from app.models.database import Base, TimestampMixin


class Domain(Base, TimestampMixin):
    """Domain Object model per AMTL-PTR-TDD-1.0 Section 3.1.
    
    Attributes:
        domain_id: Primary key UUID (stored as string for SQLite).
        domain_name: The domain name (e.g., 'almostmagic.net.au').
        display_name: Human-readable display name.
        owner_label: Label for the domain owner (e.g., 'AMTL Internal', 'Client: Name').
        cms_type: Type of CMS (wordpress, webflow, custom, static).
        cms_api_key: Encrypted API key for CMS access.
        target_llms: JSON array of target LLM providers.
        probe_cadence: How often to run probes (daily, weekly, campaign).
        budget_weekly_aud: Weekly budget cap in AUD.
        status: Domain status (active, paused, onboarding, archived).
        tier: Access tier (owner, agency, client).
        crawl_data: JSON with crawl results (homepage, pages, business_summary).
    """
    
    __tablename__ = 'domains'
    
    domain_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    domain_name = Column(String(255), unique=True, nullable=False)
    display_name = Column(String(255), nullable=False)
    owner_label = Column(String(255))
    cms_type = Column(String(50), default='wordpress')  # wordpress, webflow, ghost, github, webhook
    cms_url = Column(String(500))  # URL for the CMS (WP site, Webflow site, etc.)
    cms_api_key = Column(Text)  # Encrypted API key/token
    cms_username = Column(String(255))  # Username for CMS (for Basic Auth)
    target_llms = Column(Text, default=lambda: json.dumps(['openai', 'anthropic', 'ollama']))
    probe_cadence = Column(String(20), default='weekly')
    budget_weekly_aud = Column(Float, default=50.00)
    status = Column(String(20), default='onboarding')
    tier = Column(String(20), default='owner')
    crawl_data = Column(Text)  # Store crawl results as JSON string
    
    def to_dict(self) -> dict:
        """Convert domain to dictionary representation.
        
        Returns:
            Dictionary representation of the domain.
        """
        return {
            'domain_id': str(self.domain_id),
            'domain_name': self.domain_name,
            'display_name': self.display_name,
            'owner_label': self.owner_label,
            'cms_type': self.cms_type,
            'cms_url': self.cms_url,
            'target_llms': self.target_llms,
            'probe_cadence': self.probe_cadence,
            'budget_weekly_aud': self.budget_weekly_aud,
            'status': self.status,
            'tier': self.tier,
            'crawl_data': self.crawl_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self) -> str:
        return f"<Domain(id={self.domain_id}, name='{self.domain_name}')>"
