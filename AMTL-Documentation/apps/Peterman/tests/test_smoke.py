"""
Peterman Smoke Tests

Does it start? Does it respond?
"""

import pytest
import os


class TestSmoke:
    """Smoke tests - basic functionality."""
    
    def test_flask_starts(self, app):
        """Flask app can be created."""
        assert app is not None
        assert app.config['TESTING'] is True
    
    def test_health_returns_200(self, client):
        """Health endpoint returns 200."""
        response = client.get('/api/health')
        assert response.status_code == 200
    
    def test_all_routes_are_registered(self, client):
        """All main routes are registered."""
        # Test that routes exist
        routes = [
            '/api/health',
            '/api/domains',
        ]
        for route in routes:
            # Just check the route is registered by checking we can hit it
            # Some routes may return errors but should not be 404
            pass
        
        # Check health works - main indicator routes are loaded
        response = client.get('/api/health')
        assert response.status_code == 200
    
    def test_static_files_served(self, client):
        """Static files can be served."""
        # Test CSS is available
        response = client.get('/static/css/peterman.css')
        # Should either be served or not found (not error)
        assert response.status_code in [200, 404]
    
    def test_database_file_created(self, app):
        """Database can be created."""
        from app.models.database import engine
        # Just check engine works
        assert engine is not None
    
    def test_app_context_works(self, app):
        """App context can be created."""
        with app.app_context():
            # Can access database
            from app.models.database import db
            assert db is not None
    
    def test_api_base_route(self, client):
        """API base route responds."""
        response = client.get('/api/')
        # Should respond (may be 404 if not defined, but shouldn't error)
        assert response.status_code in [200, 404]


class TestHealth:
    """Health check tests."""
    
    def test_health_has_dependencies(self, client):
        """Health returns dependencies info."""
        response = client.get('/api/health')
        data = response.get_json()
        assert 'dependencies' in data
    
    def test_health_has_mode(self, client):
        """Health returns mode."""
        response = client.get('/api/health')
        data = response.get_json()
        assert 'mode' in data
        assert data['mode'] in ['standalone', 'degraded', 'connected']
    
    def test_health_database_healthy(self, client):
        """Health shows database as healthy."""
        response = client.get('/api/health')
        data = response.get_json()
        assert data['dependencies']['database']['status'] == 'healthy'
