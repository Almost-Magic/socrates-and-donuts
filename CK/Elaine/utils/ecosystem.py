"""
ELAINE Ecosystem — Live health checks for all AMTL apps.
Pings each app's health endpoint with a short timeout.
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

logger = logging.getLogger("elaine.ecosystem")

try:
    import requests as _requests
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False

# All known AMTL apps
APPS = [
    {"name": "ELAINE", "port": 5000, "health": "/api/health", "category": "core"},
    {"name": "Costanza", "port": 5001, "health": "/api/health", "category": "intelligence"},
    {"name": "Learning Assistant", "port": 5002, "health": "/api/health", "category": "learning"},
    {"name": "Workshop API", "port": 5003, "health": "/api/health", "category": "core"},
    {"name": "CK Writer", "port": 5004, "health": "/api/health", "category": "creative"},
    {"name": "Junk Drawer Frontend", "port": 3005, "health": "/", "category": "core"},
    {"name": "Junk Drawer API", "port": 5005, "health": "/api/health", "category": "core"},
    {"name": "Peterman", "port": 5008, "health": "/api/health", "category": "business"},
    {"name": "Genie", "port": 8000, "health": "/api/health", "category": "finance"},
    {"name": "Supervisor", "port": 9000, "health": "/api/health", "category": "infra"},
    {"name": "Foreperson", "port": 9100, "health": "/api/health", "category": "infra"},
]

HEALTH_TIMEOUT = 2  # seconds per check


def _check_app(app: dict) -> dict:
    """Ping a single app's health endpoint. Returns enriched app dict."""
    result = {
        "name": app["name"],
        "port": app["port"],
        "category": app["category"],
        "status": "down",
        "version": None,
        "latency_ms": None,
        "detail": None,
    }
    if not _HAS_REQUESTS:
        return result

    import time
    url = f"http://localhost:{app['port']}{app['health']}"
    try:
        start = time.time()
        resp = _requests.get(url, timeout=HEALTH_TIMEOUT)
        latency = int((time.time() - start) * 1000)
        if resp.status_code < 400:
            result["status"] = "running"
            result["latency_ms"] = latency
            try:
                data = resp.json()
                result["version"] = data.get("version")
                result["detail"] = {
                    k: v for k, v in data.items()
                    if k in ("status", "service", "version", "modules", "total")
                }
            except Exception:
                pass
    except _requests.ConnectionError:
        pass
    except _requests.Timeout:
        result["status"] = "timeout"
    except Exception as exc:
        logger.debug("Health check for %s failed: %s", app["name"], exc)

    return result


def check_ecosystem() -> dict:
    """Check all AMTL apps concurrently. Returns full ecosystem status."""
    apps_status = []
    healthy = 0

    with ThreadPoolExecutor(max_workers=10) as pool:
        futures = {pool.submit(_check_app, app): app for app in APPS}
        for future in as_completed(futures):
            result = future.result()
            apps_status.append(result)
            if result["status"] == "running":
                healthy += 1

    # Sort by port for consistent ordering
    apps_status.sort(key=lambda x: x["port"])

    return {
        "apps": apps_status,
        "healthy": healthy,
        "total": len(APPS),
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


def get_app_data(port: int, path: str, timeout: int = 2) -> dict | None:
    """Fetch JSON data from a specific app endpoint. Returns parsed JSON or None."""
    if not _HAS_REQUESTS:
        return None
    try:
        resp = _requests.get(f"http://localhost:{port}{path}", timeout=timeout)
        if resp.ok:
            return resp.json()
    except Exception:
        pass
    return None
