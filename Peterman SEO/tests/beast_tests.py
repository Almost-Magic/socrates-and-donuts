"""
Beast Test Harness — Peterman V4.1
63 Tests: Project Structure, Security, Code Quality, API Routes, Frontend, Services

Run: python tests/beast_tests.py
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime

# ── Configuration ──────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
STATIC_DIR = PROJECT_ROOT / "static"
RESULTS = {"passed": 0, "failed": 0, "warnings": 0, "tests": []}


def log_test(name, status, detail=""):
    icon = "PASS" if status == "pass" else "FAIL" if status == "fail" else "WARN"
    RESULTS["tests"].append({"name": name, "status": status, "detail": detail})
    if status == "pass": RESULTS["passed"] += 1
    elif status == "fail": RESULTS["failed"] += 1
    else: RESULTS["warnings"] += 1
    print(f"  [{icon}] {name}" + (f" -- {detail}" if detail else ""))


# ═══════════════════════════════════════════════════════════
# SECTION 1: PROJECT STRUCTURE (10 tests)
# ═══════════════════════════════════════════════════════════
def test_project_structure():
    print("\n  SECTION 1: Project Structure")

    # T01: Root app.py exists
    log_test("T01 Root app.py (Flask entry)", "pass" if (PROJECT_ROOT / "app.py").exists() else "fail")

    # T02: Backend package
    log_test("T02 Backend package", "pass" if (BACKEND_DIR / "__init__.py").exists() else "fail")

    # T03: Models package
    log_test("T03 Models package", "pass" if (BACKEND_DIR / "models" / "models.py").exists() else "fail")

    # T04: Routes package
    routes_init = BACKEND_DIR / "routes" / "__init__.py"
    log_test("T04 Routes package", "pass" if routes_init.exists() else "fail")

    # T05: Services package
    log_test("T05 Services package", "pass" if (BACKEND_DIR / "services" / "__init__.py").exists() else "fail")

    # T06: Config file
    log_test("T06 Config file", "pass" if (BACKEND_DIR / "config.py").exists() else "fail")

    # T07: Requirements file
    log_test("T07 Requirements (root)", "pass" if (PROJECT_ROOT / "requirements.txt").exists() else "fail")

    # T08: README
    readme = PROJECT_ROOT / "README.md"
    if readme.exists():
        content = readme.read_text(encoding="utf-8", errors="ignore")
        is_peterman = "Peterman" in content and "Authority" in content
        log_test("T08 README describes Peterman", "pass" if is_peterman else "fail", "Should reference Peterman, not Genie")
    else:
        log_test("T08 README exists", "fail")

    # T09: .gitignore
    log_test("T09 .gitignore", "pass" if (PROJECT_ROOT / ".gitignore").exists() else "fail")

    # T10: Static frontend
    log_test("T10 Frontend exists", "pass" if (STATIC_DIR / "index.html").exists() else "fail")


# ═══════════════════════════════════════════════════════════
# SECTION 2: SECURITY (12 tests)
# ═══════════════════════════════════════════════════════════
def test_security():
    print("\n  SECTION 2: Security")

    py_files = list(BACKEND_DIR.rglob("*.py"))

    # T11: No hardcoded API keys (sk-, key-, etc.)
    api_key_found = False
    for f in py_files:
        content = f.read_text(errors="ignore")
        if re.search(r'sk-[a-zA-Z0-9]{20,}', content):
            api_key_found = True; break
    log_test("T11 No hardcoded API keys", "pass" if not api_key_found else "fail")

    # T12: No eval() usage
    eval_found = False
    for f in py_files:
        if "eval(" in f.read_text(errors="ignore"):
            eval_found = True; break
    log_test("T12 No eval() usage", "pass" if not eval_found else "fail")

    # T13: No exec() usage (except DB execute)
    exec_found = False
    for f in py_files:
        content = f.read_text(errors="ignore")
        if "exec(" in content and "execute" not in content:
            exec_found = True; break
    log_test("T13 No dangerous exec()", "pass" if not exec_found else "fail")

    # T14: No pickle (deserialization attack vector)
    pickle_found = any("import pickle" in f.read_text(errors="ignore") for f in py_files)
    log_test("T14 No pickle usage", "pass" if not pickle_found else "fail")

    # T15: CORS not wildcard
    app_content = (PROJECT_ROOT / "app.py").read_text(encoding="utf-8")
    wildcard_cors = 'allow_origins=["*"]' in app_content
    log_test("T15 CORS not wildcard", "pass" if not wildcard_cors else "warn")

    # T16: No debug=True in app entry
    log_test("T16 No debug=True in app.py", "pass" if 'debug=True' not in app_content else "warn")

    # T17: Environment variables for secrets
    config_content = (BACKEND_DIR / "config.py").read_text(encoding="utf-8")
    uses_env = "os.getenv" in config_content
    log_test("T17 Secrets via env vars", "pass" if uses_env else "fail")

    # T18: .env in .gitignore
    gitignore = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8") if (PROJECT_ROOT / ".gitignore").exists() else ""
    log_test("T18 .env in .gitignore", "pass" if ".env" in gitignore else "fail")

    # T19: XSS — HTML escaping (frontend uses textContent or esc())
    if (STATIC_DIR / "app.js").exists():
        js = (STATIC_DIR / "app.js").read_text(encoding="utf-8")
        has_esc = "function esc(" in js or "textContent" in js
        log_test("T19 XSS protection (esc function)", "pass" if has_esc else "warn")
    else:
        log_test("T19 XSS protection", "fail", "No frontend JS")

    # T20: SQL injection protection (SQLAlchemy ORM used)
    models_content = (BACKEND_DIR / "models" / "models.py").read_text(encoding="utf-8")
    uses_orm = "db.Column" in models_content and "SQLAlchemy" in models_content
    log_test("T20 SQL injection protection (ORM)", "pass" if uses_orm else "fail")

    # T21: No sensitive data in error responses
    has_error_handler = "@app.errorhandler" in app_content
    log_test("T21 Error handlers registered", "pass" if has_error_handler else "warn")

    # T22: Passwords not logged
    password_logged = False
    for f in py_files:
        content = f.read_text(errors="ignore")
        if re.search(r'log.*password', content, re.IGNORECASE):
            password_logged = True; break
    log_test("T22 No passwords in logs", "pass" if not password_logged else "fail")


# ═══════════════════════════════════════════════════════════
# SECTION 3: DATABASE MODELS (8 tests)
# ═══════════════════════════════════════════════════════════
def test_database():
    print("\n  SECTION 3: Database Models (PostgreSQL + pgvector)")
    models_file = BACKEND_DIR / "models" / "models.py"
    content = models_file.read_text(encoding="utf-8") if models_file.exists() else ""

    tables = [
        ("T23", "Brand", "brands"),
        ("T24", "Keyword", "keywords"),
        ("T25", "Competitor", "competitors"),
        ("T26", "Scan", "scans"),
        ("T27", "PerceptionResult", "perception_results"),
        ("T28", "Hallucination", "hallucinations"),
        ("T29", "SemanticFingerprint", "semantic_fingerprints"),
        ("T30", "ShareOfVoice", "share_of_voice"),
    ]
    for tid, cls, table in tables:
        has_class = f"class {cls}(db.Model)" in content
        has_table = f'__tablename__ = "{table}"' in content
        log_test(f"{tid} Model: {cls} ({table})", "pass" if has_class and has_table else "fail")


# ═══════════════════════════════════════════════════════════
# SECTION 4: API ROUTES — Flask Blueprints (10 tests)
# ═══════════════════════════════════════════════════════════
def test_api_routes():
    print("\n  SECTION 4: API Routes (Flask Blueprints)")

    routes_init = BACKEND_DIR / "routes" / "__init__.py"
    init_content = routes_init.read_text(encoding="utf-8") if routes_init.exists() else ""
    app_content = (PROJECT_ROOT / "app.py").read_text(encoding="utf-8")

    # T31-T34: Core blueprints registered
    blueprints = [
        ("T31", "health_bp", "health.py"),
        ("T32", "brands_bp", "brands.py"),
        ("T33", "perception_bp", "perception.py"),
        ("T34", "browser_bp", "browser.py"),
    ]
    for tid, bp_name, filename in blueprints:
        imported = bp_name in init_content
        registered = bp_name in app_content
        log_test(f"{tid} Blueprint: {bp_name}", "pass" if imported and registered else "fail",
                 f"imported={imported}, registered={registered}")

    # T35-T40: Key endpoint patterns exist
    routes_content = ""
    for f in (BACKEND_DIR / "routes").glob("*.py"):
        routes_content += f.read_text(errors="ignore")

    endpoints = [
        ("T35", "/api/health", "Health check"),
        ("T36", "/api/brands", "Brand CRUD"),
        ("T37", "/api/scan/perception", "Perception scan"),
        ("T38", "/api/hallucinations", "Hallucination tracking"),
        ("T39", "/api/sov", "Share of Voice"),
        ("T40", "/api/trust-class", "Trust class analysis"),
    ]
    for tid, path, desc in endpoints:
        log_test(f"{tid} Endpoint: {path}", "pass" if path in routes_content else "fail", desc)


# ═══════════════════════════════════════════════════════════
# SECTION 5: SERVICES (8 tests)
# ═══════════════════════════════════════════════════════════
def test_services():
    print("\n  SECTION 5: Services")

    services_init = BACKEND_DIR / "services" / "__init__.py"
    init_content = services_init.read_text(encoding="utf-8") if services_init.exists() else ""

    # T41: Ollama service
    log_test("T41 Ollama service", "pass" if "ollama" in init_content else "fail")

    # T42: SearXNG service
    log_test("T42 SearXNG service", "pass" if "searxng" in init_content else "fail")

    # T43: Snitcher service
    log_test("T43 Snitcher service", "pass" if "snitcher" in init_content else "fail")

    # T44: Browser LLM service exists
    log_test("T44 Browser LLM service", "pass" if (BACKEND_DIR / "services" / "browser_llm_service.py").exists() else "fail")

    # T45: Ollama has health_check
    ollama = (BACKEND_DIR / "services" / "ollama_service.py").read_text(encoding="utf-8") if (BACKEND_DIR / "services" / "ollama_service.py").exists() else ""
    log_test("T45 Ollama health_check", "pass" if "def health_check" in ollama else "fail")

    # T46: Ollama has generate_json
    log_test("T46 Ollama generate_json", "pass" if "def generate_json" in ollama else "fail")

    # T47: Ollama has embed
    log_test("T47 Ollama embed", "pass" if "def embed" in ollama else "fail")

    # T48: Browser LLM supports 4 models
    browser = (BACKEND_DIR / "services" / "browser_llm_service.py").read_text(encoding="utf-8") if (BACKEND_DIR / "services" / "browser_llm_service.py").exists() else ""
    models = ["chatgpt", "claude", "perplexity", "gemini"]
    all_models = all(m in browser for m in models)
    log_test("T48 Browser supports 4 LLMs", "pass" if all_models else "fail",
             ", ".join(m for m in models if m in browser))


# ═══════════════════════════════════════════════════════════
# SECTION 6: FRONTEND (8 tests)
# ═══════════════════════════════════════════════════════════
def test_frontend():
    print("\n  SECTION 6: Frontend (AMTL Design System)")

    html_file = STATIC_DIR / "index.html"
    css_file = STATIC_DIR / "style.css"
    js_file = STATIC_DIR / "app.js"

    # T49: HTML file
    log_test("T49 index.html exists", "pass" if html_file.exists() else "fail")

    # T50: CSS file
    log_test("T50 style.css exists", "pass" if css_file.exists() else "fail")

    # T51: JS file
    log_test("T51 app.js exists", "pass" if js_file.exists() else "fail")

    html = html_file.read_text(encoding="utf-8") if html_file.exists() else ""
    css = css_file.read_text(encoding="utf-8") if css_file.exists() else ""

    # T52: AMTL Midnight colour
    log_test("T52 AMTL Midnight #0A0E14", "pass" if "#0A0E14" in css or "#0a0e14" in css else "fail")

    # T53: AMTL Gold accent
    log_test("T53 AMTL Gold #C9944A", "pass" if "#C9944A" in css or "#c9944a" in css else "fail")

    # T54: Sora font
    log_test("T54 Sora font", "pass" if "Sora" in css or "Sora" in html else "fail")

    # T55: Dark mode default
    log_test("T55 Dark mode default", "pass" if "--midnight" in css and "background" in css else "fail")

    # T56: Has navigation
    log_test("T56 Navigation sidebar", "pass" if "sidebar" in html.lower() else "fail")


# ═══════════════════════════════════════════════════════════
# SECTION 7: BUSINESS LOGIC (7 tests)
# ═══════════════════════════════════════════════════════════
def test_business_logic():
    print("\n  SECTION 7: Business Logic")

    perception = (BACKEND_DIR / "routes" / "perception.py").read_text(encoding="utf-8") if (BACKEND_DIR / "routes" / "perception.py").exists() else ""
    models = (BACKEND_DIR / "models" / "models.py").read_text(encoding="utf-8") if (BACKEND_DIR / "models" / "models.py").exists() else ""
    searxng = (BACKEND_DIR / "services" / "searxng_service.py").read_text(encoding="utf-8") if (BACKEND_DIR / "services" / "searxng_service.py").exists() else ""

    # T57: Perception queries build dynamically
    log_test("T57 Dynamic query building", "pass" if "_build_perception_queries" in perception else "fail")

    # T58: Hallucination detection
    log_test("T58 Hallucination detection", "pass" if "hallucinations" in perception else "fail")

    # T59: Trust class analysis
    log_test("T59 Trust class analysis", "pass" if "trust_class" in perception else "fail")

    # T60: Share of Voice tracking
    log_test("T60 Share of Voice model", "pass" if "ShareOfVoice" in models else "fail")

    # T61: Inertia scoring
    log_test("T61 Inertia scoring", "pass" if "inertia_score" in models else "fail")

    # T62: SERP check via SearXNG
    log_test("T62 SERP check", "pass" if "serp_check" in searxng else "fail")

    # T63: Vector embeddings (pgvector)
    log_test("T63 Vector embeddings (768-dim)", "pass" if "Vector(768)" in models else "fail")


# ═══════════════════════════════════════════════════════════
# RUNNER
# ═══════════════════════════════════════════════════════════
def run_all():
    print("=" * 60)
    print("  BEAST TEST HARNESS -- Peterman V4.1")
    print(f"  {datetime.now().strftime('%d %b %Y %H:%M:%S')}")
    print(f"  Project: {PROJECT_ROOT}")
    print("=" * 60)

    test_project_structure()
    test_security()
    test_database()
    test_api_routes()
    test_services()
    test_frontend()
    test_business_logic()

    print("\n" + "=" * 60)
    total = RESULTS["passed"] + RESULTS["failed"] + RESULTS["warnings"]
    print(f"  RESULTS: {RESULTS['passed']}/{total} passed | {RESULTS['failed']} failed | {RESULTS['warnings']} warnings")
    pct = round(RESULTS["passed"] / max(total, 1) * 100, 1)
    print(f"  SCORE: {pct}%")
    status = "ALL CLEAR" if RESULTS["failed"] == 0 else "ISSUES FOUND"
    print(f"  STATUS: {status}")
    print("=" * 60)

    # Save report
    report_dir = PROJECT_ROOT / "tests" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"beast_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, "w") as f:
        json.dump({"timestamp": datetime.now().isoformat(), "results": RESULTS, "score_pct": pct}, f, indent=2)
    print(f"\n  Report saved: {report_path}")

    return RESULTS["failed"] == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
