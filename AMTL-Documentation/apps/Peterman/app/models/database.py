"""
Database models and connection management for Peterman.
"""

import logging
from datetime import datetime
from flask import Flask
from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, DateTime, Text, JSON, UUID, ForeignKey, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base

from app.config import config

logger = logging.getLogger(__name__)

# Single shared MetaData
metadata = MetaData()

# Single shared Base - CRITICAL: all models must use this
Base = declarative_base(metadata=metadata)

# Create engine
engine = create_engine(
    config['DB_URL'],
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True
)

# Session factory
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

# For backward compatibility
db = None


def init_db(app: Flask = None):
    """Initialize the database."""
    global Session
    
    # Import all models to register them with the SAME Base
    from app.models import domain, audit, budget, deployment, score, hallucination, probe, brief, embedding
    from app.models.keyword_engine import TargetQuery
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    logger.info("Database initialised")


def get_session():
    """Get a database session."""
    return Session()


def close_session():
    """Remove the current database session."""
    Session.remove()


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
