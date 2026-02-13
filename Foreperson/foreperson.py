"""
The Foreperson — Quality Audit Engine
Almost Magic Tech Lab — February 2026

Verifies promised vs delivered for every app.
Reads YAML specs, runs automated checks, produces gap reports.

Usage:
    python foreperson.py --all                  Run all app audits
    python foreperson.py --app elaine           Audit a specific app
    python foreperson.py --serve                Start web dashboard on :9100
    python foreperson.py --report               Show latest report summary
"""

import argparse
import io
import json
import os
import socket
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import urllib.request
import urllib.error

# Fix Windows console encoding for unicode output
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

try:
    import yaml
except ImportError:
    print("PyYAML required: pip install pyyaml")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent
SPECS_DIR = BASE_DIR / "specs"
REPORTS_DIR = BASE_DIR / "reports"
DASHBOARD_FILE = BASE_DIR / "index.html"

REPORTS_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Status constants
# ---------------------------------------------------------------------------
STATUS_WORKING = "working"       # Feature confirmed operational
STATUS_PARTIAL = "partial"       # Feature responds but incomplete
STATUS_MISSING = "missing"       # Feature does not respond or exist
STATUS_NOT_TESTED = "not_tested" # Cannot be auto-tested
STATUS_NOT_IMPL = "not_implemented"  # Explicitly marked not built yet

STATUS_ICONS = {
    STATUS_WORKING: "\u2705",       # green check
    STATUS_PARTIAL: "\u26a0\ufe0f", # warning
    STATUS_MISSING: "\u274c",       # red X
    STATUS_NOT_TESTED: "\U0001f507",# muted speaker
    STATUS_NOT_IMPL: "\U0001f6a7",  # construction
}

STATUS_LABELS = {
    STATUS_WORKING: "Working",
    STATUS_PARTIAL: "Partial",
    STATUS_MISSING: "Missing",
    STATUS_NOT_TESTED: "Not Tested",
    STATUS_NOT_IMPL: "Not Implemented",
}

# ---------------------------------------------------------------------------
# Spec loader
# ---------------------------------------------------------------------------
def load_specs(app_filter=None):
    """Load all YAML spec files, optionally filtered by app id."""
    specs = []
    for f in sorted(SPECS_DIR.glob("*.yaml")):
        with open(f, "r", encoding="utf-8") as fh:
            spec = yaml.safe_load(fh)
            if spec:
                spec["_file"] = f.name
                if app_filter is None or f.stem.lower() == app_filter.lower():
                    specs.append(spec)
    return specs


# ---------------------------------------------------------------------------
# Check runners
# ---------------------------------------------------------------------------
def check_port_open(host, port, timeout=3, retries=2):
    """Check if a TCP port is open (with retry for transient failures)."""
    for attempt in range(retries):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, int(port)))
            sock.close()
            if result == 0:
                return True
        except Exception:
            pass
        if attempt < retries - 1:
            import time
            time.sleep(1)
    return False


def http_request(url, method="GET", body=None, timeout=5):
    """Make an HTTP request and return (status_code, body_text)."""
    try:
        data = None
        headers = {"Content-Type": "application/json"}
        if body:
            if isinstance(body, str):
                data = body.encode("utf-8")
            else:
                data = json.dumps(body).encode("utf-8")

        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body_text = resp.read().decode("utf-8", errors="replace")
            return resp.status, body_text
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception:
        return None, ""


def run_check(feature, base_url):
    """Run a single feature check and return a result dict."""
    check_type = feature.get("check", "manual_ui_check")
    result = {
        "id": feature["id"],
        "name": feature["name"],
        "check_type": check_type,
        "status": STATUS_NOT_TESTED,
        "detail": "",
        "notes": feature.get("notes", ""),
    }

    if check_type == "not_implemented":
        result["status"] = STATUS_NOT_IMPL
        result["detail"] = "Explicitly marked as not yet built"
        return result

    if check_type == "manual_ui_check":
        result["status"] = STATUS_NOT_TESTED
        result["detail"] = "Requires manual verification"
        return result

    if check_type == "process_check":
        proc_name = feature.get("process_name", "")
        # On Windows, check tasklist
        try:
            import subprocess
            out = subprocess.check_output(
                ["tasklist", "/FI", f"IMAGENAME eq {proc_name}*"],
                text=True, timeout=5, creationflags=0x08000000  # CREATE_NO_WINDOW
            )
            if proc_name.lower() in out.lower():
                result["status"] = STATUS_WORKING
                result["detail"] = f"Process '{proc_name}' found running"
            else:
                result["status"] = STATUS_MISSING
                result["detail"] = f"Process '{proc_name}' not found"
        except Exception as e:
            result["status"] = STATUS_MISSING
            result["detail"] = f"Process check failed: {e}"
        return result

    if check_type == "port_open":
        port = feature.get("port", 0)
        if check_port_open("localhost", port):
            result["status"] = STATUS_WORKING
            result["detail"] = f"Port {port} is open"
        else:
            result["status"] = STATUS_MISSING
            result["detail"] = f"Port {port} is not reachable"
        return result

    if check_type == "command_check":
        cmd = feature.get("command", "")
        expected = feature.get("expected_contains", "")
        try:
            import subprocess
            out = subprocess.check_output(
                cmd, shell=True, text=True, timeout=feature.get("timeout", 15),
                stderr=subprocess.STDOUT,
                creationflags=0x08000000  # CREATE_NO_WINDOW
            )
            if expected and expected.lower() in out.lower():
                result["status"] = STATUS_WORKING
                result["detail"] = f"Command output contains '{expected}'"
            elif not expected and out.strip():
                result["status"] = STATUS_WORKING
                result["detail"] = "Command executed successfully"
            else:
                result["status"] = STATUS_MISSING
                result["detail"] = f"Output missing '{expected}'"
        except subprocess.TimeoutExpired:
            result["status"] = STATUS_MISSING
            result["detail"] = "Command timed out"
        except Exception as e:
            result["status"] = STATUS_MISSING
            result["detail"] = f"Command failed: {e}"
        return result

    # HTTP checks — feature-level url overrides base_url + path
    if "url" in feature:
        url = feature["url"]
    else:
        path = feature.get("path", "/")
        url = f"{base_url.rstrip('/')}{path}"
    timeout = feature.get("timeout", 5)

    if check_type == "http_get":
        status_code, body = http_request(url, "GET", timeout=timeout)
    elif check_type == "http_post":
        post_body = feature.get("body", {})
        status_code, body = http_request(url, "POST", body=post_body, timeout=timeout)
    else:
        result["detail"] = f"Unknown check type: {check_type}"
        return result

    if status_code is None:
        result["status"] = STATUS_MISSING
        result["detail"] = f"Connection failed to {url}"
        return result

    expected_status = feature.get("expected_status", 200)
    expected_contains = feature.get("expected_contains", "")

    if status_code != expected_status:
        result["status"] = STATUS_MISSING
        result["detail"] = f"Expected HTTP {expected_status}, got {status_code}"
        return result

    if expected_contains:
        if expected_contains.lower() in body.lower():
            result["status"] = STATUS_WORKING
            result["detail"] = f"HTTP {status_code}, contains '{expected_contains}'"
        else:
            result["status"] = STATUS_PARTIAL
            result["detail"] = f"HTTP {status_code} OK but '{expected_contains}' not found in response"
        return result

    result["status"] = STATUS_WORKING
    result["detail"] = f"HTTP {status_code} OK"
    return result


# ---------------------------------------------------------------------------
# Audit engine
# ---------------------------------------------------------------------------
def audit_app(spec):
    """Run all checks for a single app spec. Returns audit result dict."""
    app_name = spec.get("app", "Unknown")
    base_url = spec.get("url", f"http://localhost:{spec.get('port', 80)}")
    port = spec.get("port", 0)

    # First check if the port is even reachable
    port_alive = check_port_open("localhost", port) if port else False

    results = []
    for feature in spec.get("features", []):
        if not port_alive and feature.get("check", "") in ("http_get", "http_post"):
            # Skip HTTP checks if port is down
            results.append({
                "id": feature["id"],
                "name": feature["name"],
                "check_type": feature.get("check", ""),
                "status": STATUS_MISSING,
                "detail": f"Port {port} not reachable — app appears down",
                "notes": feature.get("notes", ""),
            })
        else:
            results.append(run_check(feature, base_url))

    # Compute summary
    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1

    total = len(results)
    working = counts.get(STATUS_WORKING, 0)
    not_tested = counts.get(STATUS_NOT_TESTED, 0)
    score = round((working / total * 100) if total > 0 else 0, 1)
    achievable = total - not_tested
    max_achievable_score = round((working / achievable * 100) if achievable > 0 else 0, 1)

    return {
        "app": app_name,
        "port": port,
        "category": spec.get("category", ""),
        "priority": spec.get("priority", ""),
        "description": spec.get("description", ""),
        "url": base_url,
        "port_alive": port_alive,
        "features": results,
        "summary": {
            "total": total,
            "working": counts.get(STATUS_WORKING, 0),
            "partial": counts.get(STATUS_PARTIAL, 0),
            "missing": counts.get(STATUS_MISSING, 0),
            "not_tested": not_tested,
            "not_implemented": counts.get(STATUS_NOT_IMPL, 0),
            "score": score,
            "achievable": achievable,
            "max_achievable_score": max_achievable_score,
        },
    }


def run_full_audit(app_filter=None):
    """Run audit across all specs (or filtered). Returns full report."""
    specs = load_specs(app_filter)
    if not specs:
        print(f"No specs found{' for ' + app_filter if app_filter else ''}.")
        return None

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "generated_by": "The Foreperson v2.0",
        "apps": [],
    }

    for spec in specs:
        print(f"  Auditing {spec.get('app', spec['_file'])}...", end=" ", flush=True)
        result = audit_app(spec)
        report["apps"].append(result)
        score = result["summary"]["score"]
        total = result["summary"]["total"]
        working = result["summary"]["working"]
        icon = "\u2705" if score >= 80 else ("\u26a0\ufe0f" if score >= 50 else "\u274c")
        print(f"{icon} {working}/{total} features ({score}%)")

    # Overall summary
    all_total = sum(a["summary"]["total"] for a in report["apps"])
    all_working = sum(a["summary"]["working"] for a in report["apps"])
    all_achievable = sum(a["summary"]["achievable"] for a in report["apps"])
    overall_score = round((all_working / all_total * 100) if all_total > 0 else 0, 1)
    overall_max_achievable = round((all_working / all_achievable * 100) if all_achievable > 0 else 0, 1)
    report["overall"] = {
        "total_apps": len(report["apps"]),
        "total_features": all_total,
        "total_working": all_working,
        "overall_score": overall_score,
        "total_achievable": all_achievable,
        "overall_max_achievable_score": overall_max_achievable,
    }

    return report


def save_report(report):
    """Save report to reports/ directory with timestamp."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = REPORTS_DIR / f"audit_{ts}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\n  Report saved: {filepath}")

    # Also save as latest.json for the dashboard
    latest = REPORTS_DIR / "latest.json"
    with open(latest, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    return filepath


def get_latest_report():
    """Load the most recent report."""
    latest = REPORTS_DIR / "latest.json"
    if latest.exists():
        with open(latest, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def get_report_history():
    """Load all historical reports for trend analysis."""
    reports = []
    for f in sorted(REPORTS_DIR.glob("audit_*.json")):
        try:
            with open(f, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                reports.append({
                    "file": f.name,
                    "timestamp": data.get("timestamp", ""),
                    "overall": data.get("overall", {}),
                    "apps": [
                        {
                            "app": a["app"],
                            "score": a["summary"]["score"],
                            "working": a["summary"]["working"],
                            "total": a["summary"]["total"],
                        }
                        for a in data.get("apps", [])
                    ],
                })
        except Exception:
            continue
    return reports


# ---------------------------------------------------------------------------
# Console report formatter
# ---------------------------------------------------------------------------
def print_report(report):
    """Pretty-print the audit report to console."""
    if not report:
        print("No report data.")
        return

    print("\n" + "=" * 70)
    print("  THE FOREPERSON — Audit Report")
    print(f"  {report['timestamp']}")
    print("=" * 70)

    for app in report["apps"]:
        s = app["summary"]
        score = s["score"]
        bar = "\u2588" * int(score / 5) + "\u2591" * (20 - int(score / 5))
        status_icon = "\u2705" if score >= 80 else ("\u26a0\ufe0f" if score >= 50 else "\u274c")

        print(f"\n  {status_icon} {app['app']} (:{app['port']})")
        print(f"    Score: [{bar}] {score}%")
        if s.get("achievable", s["total"]) < s["total"]:
            mas = s.get("max_achievable_score", score)
            print(f"    Achievable: {s['working']}/{s['achievable']} testable ({mas}%)  [{s['not_tested']} manual-only]")
        print(f"    {s['working']}\u2705  {s['partial']}\u26a0\ufe0f  {s['missing']}\u274c  {s['not_tested']}\U0001f507  {s['not_implemented']}\U0001f6a7")

        for feat in app["features"]:
            icon = STATUS_ICONS.get(feat["status"], "?")
            print(f"      {icon} {feat['name']}")
            if feat["detail"]:
                print(f"         {feat['detail']}")
            if feat["notes"]:
                print(f"         Note: {feat['notes']}")

    o = report.get("overall", {})
    print("\n" + "-" * 70)
    print(f"  OVERALL: {o.get('total_working', 0)}/{o.get('total_features', 0)} features working across {o.get('total_apps', 0)} apps ({o.get('overall_score', 0)}%)")
    if o.get("total_achievable", o.get("total_features", 0)) < o.get("total_features", 0):
        print(f"  ACHIEVABLE: {o.get('total_working', 0)}/{o.get('total_achievable', 0)} testable features ({o.get('overall_max_achievable_score', 0)}%)")
    print("=" * 70 + "\n")


# ---------------------------------------------------------------------------
# Web server for dashboard + API
# ---------------------------------------------------------------------------
class ForepersonHandler(SimpleHTTPRequestHandler):
    """Serves the dashboard and API endpoints."""

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self._serve_file(DASHBOARD_FILE, "text/html")
        elif self.path == "/api/report":
            self._json_response(get_latest_report() or {"error": "No report yet. Run: python foreperson.py --all"})
        elif self.path == "/api/history":
            self._json_response(get_report_history())
        elif self.path == "/api/specs":
            specs = load_specs()
            self._json_response([{k: v for k, v in s.items() if k != "_file"} for s in specs])
        elif self.path == "/api/health":
            self._json_response({
                "status": "ok",
                "service": "The Foreperson",
                "version": "2.0",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
        elif self.path.startswith("/api/audit"):
            # Run audit on demand
            app_filter = None
            if "?" in self.path:
                query = self.path.split("?", 1)[1]
                for param in query.split("&"):
                    if param.startswith("app="):
                        app_filter = param.split("=", 1)[1]
            print(f"\n  Running audit{' for ' + app_filter if app_filter else ' (all apps)'}...")
            report = run_full_audit(app_filter)
            if report:
                save_report(report)
                self._json_response(report)
            else:
                self._json_response({"error": "No specs found"}, 404)
        else:
            self.send_error(404, "Not Found")

    def _serve_file(self, filepath, content_type):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", f"{content_type}; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, "Dashboard not found")

    def _json_response(self, data, status=200):
        content = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format, *args):
        # Quieter logging
        pass


def start_server(port=9100):
    """Start the Foreperson web dashboard."""
    server = HTTPServer(("0.0.0.0", port), ForepersonHandler)
    print(f"\n  The Foreperson dashboard: http://localhost:{port}")
    print(f"  API endpoints:")
    print(f"    GET  /api/health   — Service health")
    print(f"    GET  /api/report   — Latest audit report")
    print(f"    GET  /api/history  — Historical reports")
    print(f"    GET  /api/specs    — All app specs")
    print(f"    GET  /api/audit    — Run audit now")
    print(f"    GET  /api/audit?app=elaine — Audit single app")
    print(f"\n  Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Foreperson stopped.")
        server.server_close()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="The Foreperson — Quality Audit Engine (Almost Magic Tech Lab)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python foreperson.py --all              Audit all apps
  python foreperson.py --app elaine       Audit ELAINE only
  python foreperson.py --report           Show latest report
  python foreperson.py --serve            Start web dashboard on :9100
  python foreperson.py --serve --port 8080  Custom port

"Promised -> spec -> checked -> reported."
— Almost Magic Tech Lab
        """,
    )
    parser.add_argument("--all", action="store_true", help="Run audit on all apps")
    parser.add_argument("--app", type=str, help="Audit a specific app (spec filename without .yaml)")
    parser.add_argument("--serve", action="store_true", help="Start web dashboard")
    parser.add_argument("--port", type=int, default=9100, help="Dashboard port (default: 9100)")
    parser.add_argument("--report", action="store_true", help="Show latest report")
    parser.add_argument("--json", action="store_true", help="Output report as JSON")

    args = parser.parse_args()

    print("\n  \u2692\ufe0f  The Foreperson v2.0 — Almost Magic Tech Lab")
    print("  " + "-" * 50)

    if args.report:
        report = get_latest_report()
        if args.json:
            print(json.dumps(report, indent=2, ensure_ascii=False))
        else:
            print_report(report)
        return

    if args.all or args.app:
        report = run_full_audit(args.app)
        if report:
            save_report(report)
            if args.json:
                print(json.dumps(report, indent=2, ensure_ascii=False))
            else:
                print_report(report)

        if args.serve:
            start_server(args.port)
        return

    if args.serve:
        start_server(args.port)
        return

    # Default: show help
    parser.print_help()


if __name__ == "__main__":
    main()
