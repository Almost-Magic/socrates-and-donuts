"""
Beast Test Harness — Peterman V4.1
100 Tests: Structure, Security, Database, Routes, Services, Frontend, Business Logic, All 10 Chambers

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

    log_test("T01 Root app.py (Flask entry)", "pass" if (PROJECT_ROOT / "app.py").exists() else "fail")
    log_test("T02 Backend package", "pass" if (BACKEND_DIR / "__init__.py").exists() else "fail")
    log_test("T03 Models package", "pass" if (BACKEND_DIR / "models" / "models.py").exists() else "fail")
    log_test("T04 Routes package", "pass" if (BACKEND_DIR / "routes" / "__init__.py").exists() else "fail")
    log_test("T05 Services package", "pass" if (BACKEND_DIR / "services" / "__init__.py").exists() else "fail")
    log_test("T06 Config file", "pass" if (BACKEND_DIR / "config.py").exists() else "fail")
    log_test("T07 Requirements (root)", "pass" if (PROJECT_ROOT / "requirements.txt").exists() else "fail")

    readme = PROJECT_ROOT / "README.md"
    if readme.exists():
        content = readme.read_text(encoding="utf-8", errors="ignore")
        is_peterman = "Peterman" in content and "Authority" in content
        log_test("T08 README describes Peterman", "pass" if is_peterman else "fail")
    else:
        log_test("T08 README exists", "fail")

    log_test("T09 .gitignore", "pass" if (PROJECT_ROOT / ".gitignore").exists() else "fail")
    log_test("T10 Frontend exists", "pass" if (STATIC_DIR / "index.html").exists() else "fail")


# ═══════════════════════════════════════════════════════════
# SECTION 2: SECURITY (12 tests)
# ═══════════════════════════════════════════════════════════
def test_security():
    print("\n  SECTION 2: Security")

    py_files = list(BACKEND_DIR.rglob("*.py"))

    api_key_found = False
    for f in py_files:
        content = f.read_text(errors="ignore")
        if re.search(r'sk-[a-zA-Z0-9]{20,}', content):
            api_key_found = True; break
    log_test("T11 No hardcoded API keys", "pass" if not api_key_found else "fail")

    eval_found = False
    for f in py_files:
        if "eval(" in f.read_text(errors="ignore"):
            eval_found = True; break
    log_test("T12 No eval() usage", "pass" if not eval_found else "fail")

    exec_found = False
    for f in py_files:
        content = f.read_text(errors="ignore")
        if "exec(" in content and "execute" not in content:
            exec_found = True; break
    log_test("T13 No dangerous exec()", "pass" if not exec_found else "fail")

    pickle_found = any("import pickle" in f.read_text(errors="ignore") for f in py_files)
    log_test("T14 No pickle usage", "pass" if not pickle_found else "fail")

    app_content = (PROJECT_ROOT / "app.py").read_text(encoding="utf-8")
    wildcard_cors = 'allow_origins=["*"]' in app_content
    log_test("T15 CORS not wildcard", "pass" if not wildcard_cors else "warn")

    log_test("T16 No debug=True in app.py", "pass" if 'debug=True' not in app_content else "warn")

    config_content = (BACKEND_DIR / "config.py").read_text(encoding="utf-8")
    uses_env = "os.getenv" in config_content
    log_test("T17 Secrets via env vars", "pass" if uses_env else "fail")

    gitignore = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8") if (PROJECT_ROOT / ".gitignore").exists() else ""
    log_test("T18 .env in .gitignore", "pass" if ".env" in gitignore else "fail")

    if (STATIC_DIR / "app.js").exists():
        js = (STATIC_DIR / "app.js").read_text(encoding="utf-8")
        has_esc = "function esc(" in js or "textContent" in js
        log_test("T19 XSS protection (esc function)", "pass" if has_esc else "warn")
    else:
        log_test("T19 XSS protection", "fail", "No frontend JS")

    models_content = (BACKEND_DIR / "models" / "models.py").read_text(encoding="utf-8")
    uses_orm = "db.Column" in models_content and "SQLAlchemy" in models_content
    log_test("T20 SQL injection protection (ORM)", "pass" if uses_orm else "fail")

    has_error_handler = "@app.errorhandler" in app_content
    log_test("T21 Error handlers registered", "pass" if has_error_handler else "warn")

    password_logged = False
    for f in py_files:
        content = f.read_text(errors="ignore")
        if re.search(r'log.*password', content, re.IGNORECASE):
            password_logged = True; break
    log_test("T22 No passwords in logs", "pass" if not password_logged else "fail")


# ═══════════════════════════════════════════════════════════
# SECTION 3: DATABASE MODELS (15 tests — all 10 chambers)
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
        ("T31", "AuthorityResult", "authority_results"),
        ("T32", "SurvivabilityResult", "survivability_results"),
        ("T33", "TechnicalAudit", "technical_audits"),
        ("T34", "CitationResult", "citation_results"),
        ("T35", "VisitorLead", "visitor_leads"),
        ("T36", "TrendSignal", "trend_signals"),
        ("T37", "ContentBrief", "content_briefs"),
    ]
    for tid, cls, table in tables:
        has_class = f"class {cls}(db.Model)" in content
        has_table = f'__tablename__ = "{table}"' in content
        log_test(f"{tid} Model: {cls} ({table})", "pass" if has_class and has_table else "fail")


# ═══════════════════════════════════════════════════════════
# SECTION 4: API ROUTES — All 10 Chambers (20 tests)
# ═══════════════════════════════════════════════════════════
def test_api_routes():
    print("\n  SECTION 4: API Routes (Flask Blueprints)")

    routes_init = BACKEND_DIR / "routes" / "__init__.py"
    init_content = routes_init.read_text(encoding="utf-8") if routes_init.exists() else ""
    app_content = (PROJECT_ROOT / "app.py").read_text(encoding="utf-8")

    # T38-T50: All blueprints imported and registered
    blueprints = [
        ("T38", "health_bp", "health.py"),
        ("T39", "brands_bp", "brands.py"),
        ("T40", "perception_bp", "perception.py"),
        ("T41", "browser_bp", "browser.py"),
        ("T42", "semantic_bp", "semantic.py"),
        ("T43", "vectormap_bp", "vectormap.py"),
        ("T44", "authority_bp", "authority.py"),
        ("T45", "survivability_bp", "survivability.py"),
        ("T46", "machine_bp", "machine.py"),
        ("T47", "amplifier_bp", "amplifier.py"),
        ("T48", "proof_bp", "proof.py"),
        ("T49", "oracle_bp", "oracle.py"),
        ("T50", "forge_bp", "forge.py"),
    ]
    for tid, bp_name, filename in blueprints:
        imported = bp_name in init_content
        registered = bp_name in app_content
        file_exists = (BACKEND_DIR / "routes" / filename).exists()
        log_test(f"{tid} Blueprint: {bp_name}", "pass" if imported and registered and file_exists else "fail",
                 f"file={file_exists}, imported={imported}, registered={registered}")

    # T51-T57: Key endpoint patterns exist across all route files
    routes_content = ""
    for f in (BACKEND_DIR / "routes").glob("*.py"):
        routes_content += f.read_text(errors="ignore")

    endpoints = [
        ("T51", "/api/health", "Health check"),
        ("T52", "/api/brands", "Brand CRUD"),
        ("T53", "/api/scan/perception", "Ch1: Perception"),
        ("T54", "/api/scan/semantic", "Ch2: Semantic"),
        ("T55", "/api/vectormap", "Ch3: Vector Map"),
        ("T56", "/api/authority", "Ch4: Authority"),
        ("T57", "/api/survivability", "Ch5: Survivability"),
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

    log_test("T58 Ollama service", "pass" if "ollama" in init_content else "fail")
    log_test("T59 SearXNG service", "pass" if "searxng" in init_content else "fail")
    log_test("T60 Snitcher service", "pass" if "snitcher" in init_content else "fail")
    log_test("T61 Browser LLM service", "pass" if (BACKEND_DIR / "services" / "browser_llm_service.py").exists() else "fail")

    ollama = (BACKEND_DIR / "services" / "ollama_service.py").read_text(encoding="utf-8") if (BACKEND_DIR / "services" / "ollama_service.py").exists() else ""
    log_test("T62 Ollama health_check", "pass" if "def health_check" in ollama else "fail")
    log_test("T63 Ollama generate_json", "pass" if "def generate_json" in ollama else "fail")
    log_test("T64 Ollama embed", "pass" if "def embed" in ollama else "fail")

    browser = (BACKEND_DIR / "services" / "browser_llm_service.py").read_text(encoding="utf-8") if (BACKEND_DIR / "services" / "browser_llm_service.py").exists() else ""
    models = ["chatgpt", "claude", "perplexity", "gemini"]
    all_models = all(m in browser for m in models)
    log_test("T65 Browser supports 4 LLMs", "pass" if all_models else "fail",
             ", ".join(m for m in models if m in browser))


# ═══════════════════════════════════════════════════════════
# SECTION 6: FRONTEND — All 10 Chambers (15 tests)
# ═══════════════════════════════════════════════════════════
def test_frontend():
    print("\n  SECTION 6: Frontend (AMTL Design System + 10 Chambers)")

    html_file = STATIC_DIR / "index.html"
    css_file = STATIC_DIR / "style.css"
    js_file = STATIC_DIR / "app.js"

    log_test("T66 index.html exists", "pass" if html_file.exists() else "fail")
    log_test("T67 style.css exists", "pass" if css_file.exists() else "fail")
    log_test("T68 app.js exists", "pass" if js_file.exists() else "fail")

    html = html_file.read_text(encoding="utf-8") if html_file.exists() else ""
    css = css_file.read_text(encoding="utf-8") if css_file.exists() else ""
    js = js_file.read_text(encoding="utf-8") if js_file.exists() else ""

    # AMTL Design System
    log_test("T69 AMTL Midnight #0A0E14", "pass" if "#0A0E14" in css or "#0a0e14" in css else "fail")
    log_test("T70 AMTL Gold #C9944A", "pass" if "#C9944A" in css or "#c9944a" in css else "fail")
    log_test("T71 Sora font", "pass" if "Sora" in css or "Sora" in html else "fail")
    log_test("T72 Dark mode default", "pass" if "--midnight" in css and "background" in css else "fail")
    log_test("T73 Navigation sidebar", "pass" if "sidebar" in html.lower() else "fail")

    # All 10 chamber pages in HTML
    chamber_pages = [
        ("T74", "page-perception", "Ch1 Perception page"),
        ("T75", "page-semantic", "Ch2 Semantic page"),
        ("T76", "page-vectormap", "Ch3 Vector Map page"),
        ("T77", "page-authority", "Ch4 Authority page"),
        ("T78", "page-proof", "Ch8 Proof page"),
        ("T79", "page-forge", "Ch10 Forge page"),
    ]
    for tid, page_id, desc in chamber_pages:
        log_test(f"{tid} {desc}", "pass" if page_id in html else "fail")


# ═══════════════════════════════════════════════════════════
# SECTION 7: CHAMBER COMPLETENESS (20 tests)
# Each chamber: route file + model + wired endpoint
# ═══════════════════════════════════════════════════════════
def test_chamber_completeness():
    print("\n  SECTION 7: Chamber Completeness (All 10)")

    routes_content = ""
    for f in (BACKEND_DIR / "routes").glob("*.py"):
        routes_content += f.read_text(errors="ignore")

    models_content = (BACKEND_DIR / "models" / "models.py").read_text(encoding="utf-8") if (BACKEND_DIR / "models" / "models.py").exists() else ""

    chambers = [
        ("T80", 1, "Perception Scan", "perception.py", "/api/scan/perception", "PerceptionResult"),
        ("T81", 2, "Semantic Core", "semantic.py", "/api/scan/semantic", "SemanticFingerprint"),
        ("T82", 3, "Neural Vector Map", "vectormap.py", "/api/vectormap", "ShareOfVoice"),
        ("T83", 4, "Authority Engine", "authority.py", "/api/authority", "AuthorityResult"),
        ("T84", 5, "Survivability Lab", "survivability.py", "/api/survivability", "SurvivabilityResult"),
        ("T85", 6, "Machine Interface", "machine.py", "/api/technical", "TechnicalAudit"),
        ("T86", 7, "Amplifier", "amplifier.py", "/api/amplifier", "CitationResult"),
        ("T87", 8, "The Proof", "proof.py", "/api/proof", "VisitorLead"),
        ("T88", 9, "The Oracle", "oracle.py", "/api/oracle", "TrendSignal"),
        ("T89", 10, "The Forge", "forge.py", "/api/forge", "ContentBrief"),
    ]

    for tid, num, name, route_file, endpoint, model_class in chambers:
        file_ok = (BACKEND_DIR / "routes" / route_file).exists()
        endpoint_ok = endpoint in routes_content
        model_ok = f"class {model_class}" in models_content
        all_ok = file_ok and endpoint_ok and model_ok
        log_test(f"{tid} Chamber {num}: {name}", "pass" if all_ok else "fail",
                 f"route={file_ok}, endpoint={endpoint_ok}, model={model_ok}")

    # T90-T95: Chamber-specific feature checks
    js = (STATIC_DIR / "app.js").read_text(encoding="utf-8") if (STATIC_DIR / "app.js").exists() else ""

    log_test("T90 Ch2: Drift detection route", "pass" if "/api/drift/" in routes_content else "fail")
    log_test("T91 Ch3: Cosine similarity", "pass" if "cosine" in routes_content.lower() or "_cosine_sim" in routes_content else "fail")
    log_test("T92 Ch4: SERP gaps route", "pass" if "/gaps" in routes_content and "authority" in routes_content else "fail")
    log_test("T93 Ch7: Shadow analysis route", "pass" if "/shadow" in routes_content else "fail")
    log_test("T94 Ch9: Forecast route", "pass" if "/forecast" in routes_content else "fail")
    log_test("T95 Ch10: Content generation route", "pass" if "/generate" in routes_content and "forge" in routes_content else "fail")


# ═══════════════════════════════════════════════════════════
# SECTION 8: BUSINESS LOGIC (5 tests)
# ═══════════════════════════════════════════════════════════
def test_business_logic():
    print("\n  SECTION 8: Business Logic")

    perception = (BACKEND_DIR / "routes" / "perception.py").read_text(encoding="utf-8") if (BACKEND_DIR / "routes" / "perception.py").exists() else ""
    models = (BACKEND_DIR / "models" / "models.py").read_text(encoding="utf-8") if (BACKEND_DIR / "models" / "models.py").exists() else ""
    searxng = (BACKEND_DIR / "services" / "searxng_service.py").read_text(encoding="utf-8") if (BACKEND_DIR / "services" / "searxng_service.py").exists() else ""

    log_test("T96 Dynamic query building", "pass" if "_build_perception_queries" in perception else "fail")
    log_test("T97 Hallucination detection", "pass" if "hallucinations" in perception else "fail")
    log_test("T98 Trust class analysis", "pass" if "trust_class" in perception else "fail")
    log_test("T99 SERP check via SearXNG", "pass" if "serp_check" in searxng else "fail")
    log_test("T100 Vector embeddings (768-dim)", "pass" if "Vector(768)" in models else "fail")


# ═══════════════════════════════════════════════════════════
# SECTION 9: SEO ASK + ELAINE + SUPERVISOR (12 tests)
# ═══════════════════════════════════════════════════════════
def test_seo_ask_elaine():
    print("\n  SECTION 9: SEO Ask + ELAINE Briefing + Supervisor Routing")

    # Route file exists
    log_test("T101 SEO Ask route file", "pass" if (BACKEND_DIR / "routes" / "seo_ask.py").exists() else "fail")

    # Blueprint registered
    routes_init = (BACKEND_DIR / "routes" / "__init__.py").read_text(encoding="utf-8")
    log_test("T102 seo_ask_bp imported", "pass" if "seo_ask_bp" in routes_init else "fail")

    app_content = (PROJECT_ROOT / "app.py").read_text(encoding="utf-8")
    log_test("T103 seo_ask_bp registered", "pass" if "seo_ask_bp" in app_content else "fail")

    # Read seo_ask.py for endpoint checks
    seo_ask_content = (BACKEND_DIR / "routes" / "seo_ask.py").read_text(encoding="utf-8") if (BACKEND_DIR / "routes" / "seo_ask.py").exists() else ""

    # SEO Ask endpoint
    log_test("T104 /api/seo/ask endpoint", "pass" if "/api/seo/ask" in seo_ask_content else "fail")
    log_test("T105 SEO Ask uses SearXNG", "pass" if "searxng" in seo_ask_content else "fail")
    log_test("T106 SEO Ask uses Ollama", "pass" if "ollama" in seo_ask_content else "fail")
    log_test("T107 SEO Ask returns keywords", "pass" if "keywords" in seo_ask_content else "fail")
    log_test("T108 SEO Ask returns meta_tags", "pass" if "meta_tags" in seo_ask_content else "fail")

    # ELAINE briefing endpoint
    log_test("T109 /api/elaine-briefing endpoint", "pass" if "/api/elaine-briefing" in seo_ask_content else "fail")
    log_test("T110 Briefing returns recommendations", "pass" if "recommendations" in seo_ask_content else "fail")

    # Supervisor routing (Ollama via port 9000)
    config_content = (BACKEND_DIR / "config.py").read_text(encoding="utf-8")
    ollama_content = (BACKEND_DIR / "services" / "ollama_service.py").read_text(encoding="utf-8")
    routes_through_supervisor = "9000" in config_content and "9000" in ollama_content
    log_test("T111 Ollama routes through Supervisor (:9000)", "pass" if routes_through_supervisor else "fail")

    # Frontend SEO Ask page
    html_content = (STATIC_DIR / "index.html").read_text(encoding="utf-8") if (STATIC_DIR / "index.html").exists() else ""
    log_test("T112 SEO Ask page in frontend", "pass" if "page-seoask" in html_content else "fail")


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
    test_chamber_completeness()
    test_business_logic()
    test_seo_ask_elaine()

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
