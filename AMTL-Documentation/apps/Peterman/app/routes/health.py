"""
Health endpoint for Peterman.

Returns health status including dependency checks for SQLite, Ollama, ELAINE, SearXNG, and Workshop.
Per AMTL-ECO-OPS-1.0: All services are optional except SQLite (always available).
"""

import time
import logging
from flask import Blueprint, jsonify
import httpx
from sqlalchemy import text

from app.config import config
from app.models.database import engine

logger = logging.getLogger(__name__)

health_bp = Blueprint('health', __name__)


def check_database() -> dict:
    """Check SQLite database connection health."""
    start_time = time.time()
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        latency_ms = int((time.time() - start_time) * 1000)
        return {
            'status': 'healthy',
            'latency_ms': latency_ms
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            'status': 'unhealthy',
            'latency_ms': None,
            'error': str(e)
        }


def check_ollama() -> dict:
    """Check Ollama connection health - OPTIONAL."""
    start_time = time.time()
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{config['OLLAMA_URL']}/api/health")
            if response.status_code == 200:
                latency_ms = int((time.time() - start_time) * 1000)
                return {
                    'status': 'healthy',
                    'latency_ms': latency_ms
                }
            else:
                return {
                    'status': 'unavailable',
                    'latency_ms': None,
                    'error': f"HTTP {response.status_code}"
                }
    except Exception as e:
        logger.debug(f"Ollama not available: {e}")
        return {
            'status': 'unavailable',
            'latency_ms': None,
            'error': str(e)
        }


def check_searxng() -> dict:
    """Check SearXNG connection health - OPTIONAL."""
    start_time = time.time()
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{config['SEARXNG_URL']}/health")
            if response.status_code in [200, 302]:
                latency_ms = int((time.time() - start_time) * 1000)
                return {
                    'status': 'healthy',
                    'latency_ms': latency_ms
                }
            else:
                return {
                    'status': 'unavailable',
                    'latency_ms': None,
                    'error': f"HTTP {response.status_code}"
                }
    except Exception as e:
        logger.debug(f"SearXNG not available: {e}")
        return {
            'status': 'unavailable',
            'latency_ms': None,
            'error': str(e)
        }


def check_elaine() -> dict:
    """Check ELAINE connection health - OPTIONAL."""
    start_time = time.time()
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{config['ELAINE_URL']}/api/health")
            if response.status_code == 200:
                latency_ms = int((time.time() - start_time) * 1000)
                return {
                    'status': 'healthy',
                    'latency_ms': latency_ms
                }
            else:
                return {
                    'status': 'unavailable',
                    'latency_ms': None,
                    'error': f"HTTP {response.status_code}"
                }
    except Exception as e:
        logger.debug(f"ELAINE not available: {e}")
        return {
            'status': 'unavailable',
            'latency_ms': None,
            'error': str(e)
        }


def check_workshop() -> dict:
    """Check Workshop connection health - OPTIONAL."""
    start_time = time.time()
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{config['WORKSHOP_URL']}/api/health")
            if response.status_code == 200:
                latency_ms = int((time.time() - start_time) * 1000)
                return {
                    'status': 'healthy',
                    'latency_ms': latency_ms
                }
            else:
                return {
                    'status': 'unavailable',
                    'latency_ms': None,
                    'error': f"HTTP {response.status_code}"
                }
    except Exception as e:
        logger.debug(f"Workshop not available: {e}")
        return {
            'status': 'unavailable',
            'latency_ms': None,
            'error': str(e)
        }


@health_bp.route('/api/health', methods=['GET'])
def health_check():
    """Main health endpoint.
    
    Per AMTL-ECO-OPS-1.0: The ONLY hard requirement is SQLite.
    Everything else is optional - the app works in degraded mode.
    """
    import os
    
    # Check all dependencies (all optional except database)
    dependencies = {
        'database': check_database(),
        'ollama': check_ollama(),
        'searxng': check_searxng(),
        'elaine': check_elaine(),
        'workshop': check_workshop(),
    }
    
    # Determine overall status
    # Only database is critical - everything else is optional
    db_healthy = dependencies['database']['status'] == 'healthy'
    
    # Count available optional services
    optional_services = ['ollama', 'searxng', 'elaine', 'workshop']
    available_count = sum(1 for s in optional_services if dependencies[s]['status'] == 'healthy')
    
    if db_healthy:
        if available_count == len(optional_services):
            overall_status = 'healthy'
        elif available_count > 0:
            overall_status = 'degraded'  # Some optional services available
        else:
            overall_status = 'standalone'  # Database only - core functionality works
    else:
        overall_status = 'unhealthy'  # Database is down - critical failure
    
    # Build response
    response = {
        'status': overall_status,
        'app': 'peterman',
        'version': '2.0.0',
        'port': config['PORT'],
        'mode': 'standalone' if overall_status == 'standalone' else 'connected' if available_count == len(optional_services) else 'degraded',
        'uptime_seconds': int(time.time() - (int(os.environ.get('APP_START_TIME', time.time())))),
        'dependencies': dependencies
    }
    
    # 200 for all healthy/degraded/standalone, 503 only for truly unhealthy
    status_code = 200 if db_healthy else 503
    
    return jsonify(response), status_code
