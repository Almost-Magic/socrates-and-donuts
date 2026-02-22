"""
Peterman — Autonomous SEO & LLM Presence Engine

An autonomous agent that continuously monitors, analyses, plans, approves, executes,
verifies, and reports on a domain's SEO and LLM presence.

Version: 2.0.0
Almost Magic Tech Lab
"""

import logging
import os
from datetime import datetime
from flask import Flask
from flask_cors import CORS

from app.config import config
from app.routes.api import api_bp
from app.routes.health import health_bp


def create_app(test_config=None) -> Flask:
    """Create and configure the Peterman Flask application."""
    # Configure logging
    log_level = getattr(logging, config.get('LOG_LEVEL', 'INFO'))
    log_format = (
        '{"timestamp": "%(asctime)s", "app": "peterman", "level": "%(levelname)s", '
        '"module": "%(module)s", "message": "%(message)s"}'
    )
    
    # Ensure logs directory exists
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.FileHandler(os.path.join(logs_dir, 'peterman.log')),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Initialising Peterman application")
    
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=config.get('SECRET_KEY', 'dev-secret-key'),
        DEBUG=config.get('DEBUG', False),
        SQLALCHEMY_DATABASE_URI=config.get('DB_URL'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.update(test_config)
    
    # Enable CORS
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(health_bp)
    
    # Initialize database
    from app.models.database import init_db
    init_db(app)
    
    # Log startup
    logger.info(
        f"Peterman started on port {config.get('PORT', 5008)}",
        extra={'context': {'port': config.get('PORT', 5008)}}
    )
    
    return app


# Version and metadata
__version__ = '2.0.0'
__author__ = 'Almost Magic Tech Lab'
