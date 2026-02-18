"""
ELAINE Phase 5: Self-Healing Framework
Error recovery, health monitoring, and graceful degradation.
Wraps all module calls with resilience patterns.
"""

import json
import time
import traceback
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from functools import wraps


class ResilienceEngine:
    """
    Provides error recovery, health monitoring, and graceful degradation.
    Wraps module calls so that failures don't crash the whole system.
    """

    def __init__(self):
        self.home = Path.home() / ".elaine"
        self.home.mkdir(exist_ok=True)
        self.db_path = str(self.home / "health.db")
        self._init_db()
        self._module_status = {}

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS error_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module TEXT,
            function_name TEXT,
            error_type TEXT,
            error_message TEXT,
            traceback TEXT,
            recovered INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS health_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module TEXT,
            status TEXT,
            response_ms INTEGER,
            details TEXT,
            checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS module_status (
            module TEXT PRIMARY KEY,
            status TEXT DEFAULT 'unknown',
            last_success TIMESTAMP,
            last_error TIMESTAMP,
            error_count_24h INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        conn.commit()
        conn.close()

    def safe_call(self, module_name, func, *args, fallback=None, **kwargs):
        """
        Safely call a function with error recovery.
        Returns the function result or fallback on error.
        """
        start = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed = int((time.time() - start) * 1000)
            self._record_success(module_name, func.__name__, elapsed)
            return result
        except Exception as e:
            elapsed = int((time.time() - start) * 1000)
            self._record_error(module_name, func.__name__, e)

            # Try once more with a brief pause
            try:
                time.sleep(0.5)
                result = func(*args, **kwargs)
                self._record_success(module_name, func.__name__, elapsed, recovered=True)
                return result
            except Exception:
                pass

            return fallback() if callable(fallback) else fallback

    def _record_success(self, module, func_name, elapsed_ms, recovered=False):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""INSERT OR REPLACE INTO module_status
            (module, status, last_success, updated_at)
            VALUES (?, 'healthy', ?, ?)""",
            (module, datetime.now().isoformat(), datetime.now().isoformat()))
        c.execute("""INSERT INTO health_checks
            (module, status, response_ms, details)
            VALUES (?, ?, ?, ?)""",
            (module, 'recovered' if recovered else 'ok', elapsed_ms, func_name))
        conn.commit()
        conn.close()

    def _record_error(self, module, func_name, error):
        tb = traceback.format_exc()
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""INSERT INTO error_log
            (module, function_name, error_type, error_message, traceback)
            VALUES (?, ?, ?, ?, ?)""",
            (module, func_name, type(error).__name__, str(error), tb))

        # Update module status
        c.execute("SELECT error_count_24h FROM module_status WHERE module = ?", (module,))
        row = c.fetchone()
        count = (row[0] + 1) if row else 1
        status = 'degraded' if count < 5 else 'unhealthy'

        c.execute("""INSERT OR REPLACE INTO module_status
            (module, status, last_error, error_count_24h, updated_at)
            VALUES (?, ?, ?, ?, ?)""",
            (module, status, datetime.now().isoformat(), count,
             datetime.now().isoformat()))

        conn.commit()
        conn.close()

    def get_health_report(self):
        """Get full system health report."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        # Module statuses
        c.execute("SELECT * FROM module_status ORDER BY module")
        modules = [dict(r) for r in c.fetchall()]

        # Recent errors
        c.execute("""SELECT module, error_type, error_message, created_at
            FROM error_log ORDER BY created_at DESC LIMIT 20""")
        recent_errors = [dict(r) for r in c.fetchall()]

        # Error counts last 24h
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        c.execute("""SELECT module, COUNT(*) as count
            FROM error_log WHERE created_at >= ?
            GROUP BY module""", (yesterday,))
        error_counts = dict(c.fetchall())

        # Overall health
        unhealthy = sum(1 for m in modules if m.get("status") == "unhealthy")
        degraded = sum(1 for m in modules if m.get("status") == "degraded")
        healthy = sum(1 for m in modules if m.get("status") == "healthy")

        if unhealthy > 0:
            overall = "unhealthy"
        elif degraded > 0:
            overall = "degraded"
        elif healthy > 0:
            overall = "healthy"
        else:
            overall = "unknown"

        conn.close()
        return {
            "overall": overall,
            "modules": modules,
            "recent_errors": recent_errors,
            "error_counts_24h": error_counts,
            "summary": {
                "healthy": healthy,
                "degraded": degraded,
                "unhealthy": unhealthy
            }
        }

    def get_error_log(self, module=None, limit=50):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        if module:
            c.execute("SELECT * FROM error_log WHERE module = ? ORDER BY created_at DESC LIMIT ?",
                (module, limit))
        else:
            c.execute("SELECT * FROM error_log ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return rows

    def reset_error_counts(self):
        """Reset 24h error counts (for daily maintenance)."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("UPDATE module_status SET error_count_24h = 0")
        conn.commit()
        conn.close()

    def run_health_checks(self):
        """Run health checks on all modules."""
        results = {}

        # Check Business Context
        results["business"] = self._check_module(
            "business",
            lambda: __import__('modules.phase4_business.business_context',
                               fromlist=['BusinessContextEngine']).BusinessContextEngine()
        )

        # Check The Current
        results["the_current"] = self._check_module(
            "the_current",
            lambda: __import__('modules.phase4_current.the_current',
                               fromlist=['TheCurrentEngine']).TheCurrentEngine()
        )

        # Check Chronicle
        results["chronicle"] = self._check_module(
            "chronicle",
            lambda: __import__('modules.phase4_chronicle.chronicle',
                               fromlist=['ChronicleEngine']).ChronicleEngine()
        )

        # Check Briefing
        results["briefing"] = self._check_module(
            "briefing",
            lambda: __import__('modules.phase5_briefing.morning_briefing',
                               fromlist=['MorningBriefingEngine']).MorningBriefingEngine()
        )

        # Check network
        results["network"] = self._check_network()

        # Check disk space
        results["disk"] = self._check_disk()

        return results

    def _check_module(self, name, init_fn):
        start = time.time()
        try:
            instance = init_fn()
            elapsed = int((time.time() - start) * 1000)
            self._record_success(name, "health_check", elapsed)
            return {"status": "healthy", "response_ms": elapsed}
        except Exception as e:
            elapsed = int((time.time() - start) * 1000)
            return {"status": "error", "response_ms": elapsed, "error": str(e)}

    def _check_network(self):
        try:
            import requests
            start = time.time()
            r = requests.get("https://news.google.com", timeout=2)
            elapsed = int((time.time() - start) * 1000)
            return {"status": "healthy" if r.status_code == 200 else "degraded",
                    "response_ms": elapsed}
        except Exception as e:
            return {"status": "offline", "error": str(e)}

    def _check_disk(self):
        try:
            import shutil
            usage = shutil.disk_usage(str(self.home))
            free_gb = usage.free / (1024 ** 3)
            return {
                "status": "healthy" if free_gb > 1 else "warning",
                "free_gb": round(free_gb, 2),
                "total_gb": round(usage.total / (1024 ** 3), 2)
            }
        except Exception:
            return {"status": "unknown"}


# ─── Decorator for resilient function calls ───

_resilience = None

def get_resilience():
    global _resilience
    if _resilience is None:
        _resilience = ResilienceEngine()
    return _resilience

def resilient(module_name, fallback_value=None):
    """Decorator to make any function resilient."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            engine = get_resilience()
            return engine.safe_call(
                module_name, func, *args,
                fallback=fallback_value, **kwargs
            )
        return wrapper
    return decorator
