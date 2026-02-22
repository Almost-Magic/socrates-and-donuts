"""
Peterman Test Configuration

Shared fixtures for all tests.
"""

import pytest
import os
import tempfile
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.database import Base, engine


@pytest.fixture(scope='session')
def app():
    """Create test application with temporary SQLite database."""
    # Use temporary database for tests
    test_db = tempfile.mktemp(suffix='.db')
    os.environ['AMTL_PTR_DB_URL'] = f'sqlite:///{test_db}'
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['LOG_LEVEL'] = 'ERROR'  # Suppress logs during tests
    
    with app.app_context():
        Base.metadata.create_all(bind=engine)
    
    yield app
    
    # Cleanup
    try:
        os.unlink(test_db)
    except:
        pass


@pytest.fixture
def client(app):
    """Test client."""
    return app.test_client()


@pytest.fixture
def sample_domain(client):
    """Create a sample domain for testing."""
    response = client.post('/api/domains', json={
        'domain_name': 'test-example.com.au',
        'display_name': 'Test Example Australia',
        'owner_label': 'test',
        'cms_type': 'wordpress',
        'tier': 'owner',
        'budget_weekly_aud': 50.0
    })
    return response.get_json()


@pytest.fixture
def sample_keyword(client, sample_domain):
    """Create a sample keyword for testing."""
    domain_id = sample_domain.get('domain_id')
    response = client.post(f'/api/domains/{domain_id}/keywords', json={
        'query': 'test keyword for peterman',
        'category': 'test',
        'priority': 'medium'
    })
    return response.get_json()


@pytest.fixture
def sample_probe(client, sample_domain, sample_keyword):
    """Create a sample probe for testing."""
    domain_id = sample_domain.get('domain_id')
    # First approve the keyword
    client.post(f'/api/domains/{domain_id}/keywords/approve-all')
    # Then trigger probe
    response = client.post(f'/api/domains/{domain_id}/probe')
    return response.get_json()
