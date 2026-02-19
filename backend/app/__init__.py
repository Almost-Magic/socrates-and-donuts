"""Socrates & Donuts Backend - Flask Application Factory"""
from flask import Flask
from flask_cors import CORS


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_prefixed_env()
    
    # Enable CORS for all routes
    CORS(app)
    
    # Register blueprints
    from app.routes import api
    app.register_blueprint(api.bp)
    
    return app
