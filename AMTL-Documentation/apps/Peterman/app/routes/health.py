"""
Health endpoint for Peterman.

Returns health status including dependency checks for PostgreSQL, Redis, OllNG, ELAINE, and Workshop.
ama, SearX"""

import time
import logging
from flask import Blueprint, jsonify
import httpx
from sqlalchemy import text

from app.config import config
from app.models.database import engine

logger = logging.getLogger(__name__)

health_bp = Blueprint('health', __name__)


def check_postgresql() -> dict:
    """Check PostgreSQL connection health."""
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
        logger.error(f"PostgreSQL health check failed: {e}")
        return {
            'status': 'unhealthy',
            'latency_ms': None,
            'error': str(e)
        }


def check_redis() -> dict:
    """Check Redis connection health."""
    start_time = time.time()
    try:
        import redis
        r = redis.from_url(config['REDIS_URL'])
        r.ping()
        latency_ms = int((time.time() - start_time) * 1000)
        return {
            'status': 'healthy',
            'latency_ms': latency_ms
        }
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return {
            'status': 'unhealthy',
            'latency_ms': None,
            'error': str(e)
        }


def check_ollama() -> dict:
    """Check Ollama connection health via Supervisor."""
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
                    'status': 'unhealthy',
                    'latency_ms': None,
                    'error': f"HTTP {response.status_code}"
                }
    except Exception as e:
        logger.error(f"Ollama health check failed: {e}")
        return {
            'status': 'unhealthy',
            'latency_ms': None,
            'error': str(e)
        }


def check_searxng() -> dict:
    """Check SearXNG connection health."""
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
                    'status': 'unhealthy',
                    'latency_ms': None,
                    'error': f"HTTP {response.status_code}"
                }
    except Exception as e:
        logger.error(f"SearXNG health check failed: {e}")
        return {
            'status': 'unhealthy',
            'latency_ms': None,
            'error': str(e)
        }


def check_elaine() -> dict:
    """Check ELAINE connection health."""
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
                    'status': 'unhealthy',
                    'latency_ms': None,
                    'error': f"HTTP {response.status_code}"
                }
    except Exception as e:
        logger.error(f"ELAINE health check failed: {e}")
        return {
            'status': 'unhealthy',
            'latency_ms': None,
            'error': str(e)
        }


def check_workshop() -> dict:
    """Check Workshop connection health."""
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
                    'status': 'unhealthy',
                    'latency_ms': None,
                    'error': f"HTTP {response.status_code}"
                }
    except Exception as e:
        logger.error(f"Workshop health check failed: {e}")
        return {
            'status': 'unhealthy',
            'latency_ms': None,
            'error': str(e)
        }


@health_bp.route('/api/health', methods=['GET'])
def health_check():
    """Main health endpoint."""
    import os
    
    # Check all dependencies
    dependencies = {
        'postgresql': check_postgresql(),
        'redis': check_redis(),
        'ollama': check_ollama(),
        'searxng': check_searxng(),
        'elaine': check_elaine(),
        'workshop': check_workshop(),
    }
    
    # Determine overall status
    all_healthy = all(d['status'] == 'healthy' for d in dependencies.values())
    critical_healthy = (
        dependencies['postgresql']['status'] == 'healthy' and
        dependencies['ollama']['status'] == 'healthy'
    )
    
    if all_healthy:
        overall_status = 'healthy'
    elif critical_healthy:
        overall_status = 'degraded'
    else:
        overall_status = 'unhealthy'
    
    response = {
        'status': overall_status,
        'app': 'peterman',
        'version': '2.0.0',
        'port': config['PORT'],
        'uptime_seconds': int(time.time() - (int(os.environ.get('APP_START_TIME', time.time())))),
        'dependencies': dependencies
    }
    
    status_code = 200 if overall_status == 'healthy' else 503 if overall_status == 'unhealthy' else 200
    
    return jsonify(response), status_code
