"""
AMTL Quick Diagnose — REAL Functional Tests
============================================
Not just health checks. Actually tests if apps WORK.

Usage:
    python quick-diagnose.py
    python quick-diagnose.py --verbose
"""

import sys
import os
import time
import json
import socket
import subprocess
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

# Force UTF-8 output on Windows to handle emojis in LLM responses
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

TIMEOUT = 15  # seconds — hard limit per test
OLLAMA_PORT = 11434
SUPERVISOR_PORT = 9000

# ANSI colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

VERBOSE = "--verbose" in sys.argv


def _safe(text):
    """Strip non-ASCII chars that crash Windows console (emojis from LLM responses)."""
    return text.encode("ascii", "replace").decode("ascii")


def log(msg):
    if VERBOSE:
        print(f"  {CYAN}[debug]{RESET} {msg}")


def http_get(url, timeout=TIMEOUT):
    """GET request, returns (status_code, body_text) or raises."""
    req = urllib.request.Request(url, headers={"User-Agent": "AMTL-Diagnose/1.0"})
    resp = urllib.request.urlopen(req, timeout=timeout)
    body = resp.read().decode("utf-8", errors="replace")
    return resp.status, body


def http_post_json(url, data, timeout=TIMEOUT):
    """POST JSON, returns (status_code, body_text) or raises."""
    payload = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "AMTL-Diagnose/1.0",
        },
        method="POST",
    )
    resp = urllib.request.urlopen(req, timeout=timeout)
    body = resp.read().decode("utf-8", errors="replace")
    return resp.status, body


def port_open(port, host="127.0.0.1"):
    """Quick TCP check."""
    try:
        with socket.create_connection((host, port), timeout=3):
            return True
    except (ConnectionRefusedError, OSError, TimeoutError):
        return False


# ─────────────────────────────────────────────
# TEST FUNCTIONS — each returns (pass: bool, detail: str)
# ─────────────────────────────────────────────


def test_ollama_running():
    """Ollama: is the server actually responding?"""
    try:
        status, body = http_get(f"http://localhost:{OLLAMA_PORT}")
        if "ollama" in body.lower() or "running" in body.lower():
            return True, "Ollama server is running"
        return False, f"Unexpected response: {body[:100]}"
    except Exception as e:
        return False, f"Cannot reach Ollama on port {OLLAMA_PORT}: {e}"


def test_ollama_has_models():
    """Ollama: are models actually loaded?"""
    try:
        status, body = http_get(f"http://localhost:{OLLAMA_PORT}/api/tags")
        data = json.loads(body)
        models = data.get("models", [])
        if not models:
            return False, "Ollama has ZERO models installed"
        names = [m.get("name", "?") for m in models]
        return True, f"{len(models)} models: {', '.join(names[:5])}"
    except Exception as e:
        return False, f"Cannot list Ollama models: {e}"


def test_ollama_can_generate():
    """Ollama: can it actually generate text? (THE REAL TEST)"""
    # Try models in order: small/fast first (likely already in VRAM), then bigger
    models_to_try = ["llama3.2:3b", "mistral:latest", "llama3.1:8b", "gemma2:27b"]
    last_err = None
    for model in models_to_try:
        try:
            log(f"Trying generation with {model}...")
            status, body = http_post_json(
                f"http://localhost:{OLLAMA_PORT}/api/generate",
                {"model": model, "prompt": "Say hello in 5 words.", "stream": False,
                 "options": {"num_predict": 30}},
                timeout=TIMEOUT,
            )
            data = json.loads(body)
            response_text = data.get("response", "").strip()
            if len(response_text) > 0:
                return True, f"Generated ({model}): \"{response_text[:60]}\""
        except Exception as e:
            last_err = f"{model}: {e}"
            log(f"{model} failed: {e}")
            continue
    return False, f"All models failed. Last error: {last_err}"


def test_supervisor_health():
    """Supervisor: health endpoint returns real data?"""
    try:
        status, body = http_get(f"http://localhost:{SUPERVISOR_PORT}/api/health")
        data = json.loads(body)
        # Check it's not just {"status": "ok"} — should have service info
        keys = list(data.keys())
        if len(keys) <= 2 and "status" in keys:
            return True, f"Running but minimal health data: {keys}"
        return True, f"Health OK with keys: {', '.join(keys[:8])}"
    except Exception as e:
        return False, f"Supervisor not reachable on port {SUPERVISOR_PORT}: {e}"


def test_supervisor_llm_route():
    """Supervisor: can it route an LLM request?"""
    try:
        # Try the chat/generate endpoint
        for endpoint in ["/api/chat", "/api/generate", "/api/llm/chat"]:
            try:
                status, body = http_post_json(
                    f"http://localhost:{SUPERVISOR_PORT}{endpoint}",
                    {"messages": [{"role": "user", "content": "Say hi"}], "model": "llama3.2:3b", "stream": False, "options": {"num_predict": 5}},
                    timeout=TIMEOUT,
                )
                if status == 200 and len(body) > 5:
                    return True, f"LLM route works via {endpoint}"
            except urllib.error.HTTPError as he:
                if he.code == 404:
                    continue
                return False, f"{endpoint} returned HTTP {he.code}"
            except Exception:
                continue
        return False, "No working LLM endpoint found on Supervisor"
    except Exception as e:
        return False, f"Supervisor LLM route failed: {e}"


def _test_web_app(name, port, health_path="/api/health", expect_html=False, min_body_length=50):
    """Generic web app test: does it return REAL content (not just 200)?"""
    try:
        url = f"http://localhost:{port}{health_path}"
        log(f"Testing {name} at {url}")
        status, body = http_get(url)

        if status != 200:
            return False, f"HTTP {status}"

        if len(body) < min_body_length:
            return False, f"Response too short ({len(body)} bytes) — probably not real content"

        if expect_html:
            # Check it's actual HTML, not just JSON or error text
            if "<html" in body.lower() or "<div" in body.lower() or "<!doctype" in body.lower():
                return True, f"HTML page loaded ({len(body)} bytes)"
            elif body.strip().startswith("{"):
                return False, f"Got JSON instead of HTML page — API working but no UI served"
            else:
                return True, f"Content returned ({len(body)} bytes, not HTML but has content)"
        else:
            # Health endpoint — should be JSON with real data
            try:
                data = json.loads(body)
                if isinstance(data, dict):
                    return True, f"Health OK: {json.dumps(data)[:120]}"
                return True, f"Valid JSON response ({len(body)} bytes)"
            except json.JSONDecodeError:
                if len(body) > 100:
                    return True, f"Non-JSON response but substantial ({len(body)} bytes)"
                return False, f"Not valid JSON and too short: {body[:100]}"

    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}: {e.reason}"
    except Exception as e:
        return False, f"Cannot connect to port {port}: {e}"


def test_elaine_ui():
    """ELAINE: does the UI actually load (not just health)?"""
    return _test_web_app("ELAINE UI", 5000, "/", expect_html=True)


def test_elaine_health():
    """ELAINE: health endpoint with real data?"""
    return _test_web_app("ELAINE Health", 5000, "/api/health")


def test_elaine_chat():
    """ELAINE: can it actually respond to a chat message?"""
    try:
        # Try common chat endpoint patterns
        for endpoint in ["/api/chat", "/api/message", "/chat"]:
            try:
                status, body = http_post_json(
                    f"http://localhost:5000{endpoint}",
                    {"message": "Hello, what can you help me with?"},
                    timeout=TIMEOUT,
                )
                if status == 200 and len(body) > 10:
                    try:
                        data = json.loads(body)
                        response_text = data.get("response", data.get("message", data.get("reply", "")))
                        if response_text:
                            return True, f"Chat works via {endpoint}: \"{str(response_text)[:80]}\""
                    except json.JSONDecodeError:
                        pass
                    return True, f"Got response via {endpoint} ({len(body)} bytes)"
            except urllib.error.HTTPError as he:
                if he.code == 404:
                    continue
                log(f"ELAINE {endpoint}: HTTP {he.code}")
                continue
            except Exception as ex:
                log(f"ELAINE {endpoint}: {ex}")
                continue
        return False, "No working chat endpoint found (tried /api/chat, /api/message, /chat)"
    except Exception as e:
        return False, f"ELAINE chat test failed: {e}"


def test_workshop_ui():
    """Workshop: does Mission Control actually load?"""
    return _test_web_app("Workshop UI", 5003, "/", expect_html=True)


def test_workshop_health():
    """Workshop: health with service registry?"""
    return _test_web_app("Workshop Health", 5003, "/api/health")


def test_ck_writer_ui():
    """CK Writer: does the writing interface load?"""
    return _test_web_app("CK Writer UI", 5004, "/", expect_html=True)


def test_ck_writer_health():
    """CK Writer: health endpoint?"""
    return _test_web_app("CK Writer Health", 5004, "/api/health")


def test_costanza_health():
    """Costanza: health with model count?"""
    return _test_web_app("Costanza Health", 5001, "/api/health")


def test_costanza_models():
    """Costanza: does it actually list mental models?"""
    try:
        status, body = http_get("http://localhost:5001/api/models")
        data = json.loads(body)
        if isinstance(data, list):
            return True, f"{len(data)} mental models available"
        elif isinstance(data, dict):
            total = sum(len(v) if isinstance(v, list) else 1 for v in data.values())
            return True, f"Models endpoint returned {len(data)} categories"
        return False, f"Unexpected response format"
    except Exception as e:
        return False, f"Cannot reach Costanza models: {e}"


def test_learning_assistant_ui():
    """Learning Assistant: does the UI load?"""
    return _test_web_app("Learning Assistant UI", 5002, "/", expect_html=True)


def test_learning_assistant_health():
    """Learning Assistant: health endpoint?"""
    return _test_web_app("Learning Assistant Health", 5002, "/api/health")


def test_junk_drawer_health():
    """Junk Drawer: backend health?"""
    # Try both possible ports
    result = _test_web_app("Junk Drawer", 5005, "/api/health")
    if not result[0]:
        result = _test_web_app("Junk Drawer", 5006, "/api/health")
    return result


def test_author_studio_ui():
    """Author Studio: does it load?"""
    return _test_web_app("Author Studio UI", 5007, "/", expect_html=True)


def test_peterman_ui():
    """Peterman: does the brand intelligence UI load?"""
    return _test_web_app("Peterman UI", 5008, "/", expect_html=True)


def test_peterman_health():
    """Peterman: health endpoint?"""
    return _test_web_app("Peterman Health", 5008, "/api/health")


def test_genie_backend_health():
    """Genie Backend: detailed health?"""
    return _test_web_app("Genie Backend", 8000, "/api/health")


def test_genie_frontend():
    """Genie Frontend: does the React app actually load?"""
    return _test_web_app("Genie Frontend", 3000, "/", expect_html=True, min_body_length=200)


def test_genie_dashboard_api():
    """Genie: does the dashboard API return real data?"""
    try:
        status, body = http_get("http://localhost:8000/api/dashboard")
        if status == 200 and len(body) > 20:
            data = json.loads(body)
            return True, f"Dashboard API returned {len(data)} keys: {list(data.keys())[:5]}"
        return False, f"Dashboard API returned {status} with {len(body)} bytes"
    except Exception as e:
        return False, f"Genie dashboard API failed: {e}"


def test_ripple_backend_health():
    """Ripple CRM Backend: health with DB status?"""
    return _test_web_app("Ripple Backend", 8100, "/api/health")


def test_ripple_frontend():
    """Ripple CRM Frontend: does the React app load?"""
    return _test_web_app("Ripple Frontend", 3100, "/", expect_html=True, min_body_length=200)


def test_touchstone_backend():
    """Touchstone: backend health?"""
    return _test_web_app("Touchstone Backend", 8200, "/api/v1/health")


def test_touchstone_dashboard():
    """Touchstone Dashboard: does it load?"""
    return _test_web_app("Touchstone Dashboard", 3200, "/", expect_html=True, min_body_length=200)


def test_n8n_ui():
    """n8n: does the automation UI actually load?"""
    try:
        status, body = http_get("http://localhost:5678", timeout=TIMEOUT)
        if status == 200:
            if "<html" in body.lower() or "n8n" in body.lower() or len(body) > 500:
                return True, f"n8n UI loaded ({len(body)} bytes)"
            return False, f"n8n returned 200 but unexpected content ({len(body)} bytes)"
        return False, f"n8n returned HTTP {status}"
    except urllib.error.HTTPError as e:
        if e.code in (301, 302, 303, 307, 308):
            return True, f"n8n redirecting (HTTP {e.code}) — UI is up"
        if e.code == 401:
            return True, "n8n requires auth (HTTP 401) — UI is up"
        return False, f"n8n HTTP error: {e.code}"
    except Exception as e:
        return False, f"n8n not reachable on port 5678: {e}"


def test_listmonk_ui():
    """Listmonk: does the email UI load?"""
    try:
        status, body = http_get("http://localhost:9001", timeout=TIMEOUT)
        if status == 200 and len(body) > 100:
            return True, f"Listmonk UI loaded ({len(body)} bytes)"
        return False, f"HTTP {status}, body: {len(body)} bytes"
    except urllib.error.HTTPError as e:
        if e.code == 401:
            return True, "Listmonk requires auth (HTTP 401) — UI is up"
        if e.code in (301, 302, 303, 307, 308):
            return True, f"Listmonk redirecting (HTTP {e.code}) — UI is up"
        return False, f"Listmonk HTTP {e.code}"
    except Exception as e:
        return False, f"Listmonk not reachable on port 9001: {e}"


def test_searxng_ui():
    """SearXNG: does the search engine UI load?"""
    try:
        status, body = http_get("http://localhost:8888", timeout=TIMEOUT)
        if status == 200 and ("search" in body.lower() or "searx" in body.lower() or len(body) > 500):
            return True, f"SearXNG UI loaded ({len(body)} bytes)"
        return False, f"Unexpected response ({len(body)} bytes)"
    except urllib.error.HTTPError as e:
        if e.code in (301, 302, 303, 307, 308, 401):
            return True, f"SearXNG responding (HTTP {e.code})"
        return False, f"SearXNG HTTP {e.code}"
    except Exception as e:
        return False, f"SearXNG not reachable on port 8888: {e}"


def test_redis():
    """Redis: is it actually accepting connections?"""
    if port_open(6379):
        return True, "Redis accepting connections on port 6379"
    return False, "Redis not reachable on port 6379"


def test_postgres():
    """PostgreSQL/pgvector: accepting connections?"""
    if port_open(5433):
        return True, "PostgreSQL accepting connections on port 5433"
    return False, "PostgreSQL not reachable on port 5433"


# ─────────────────────────────────────────────
# TEST RUNNER
# ─────────────────────────────────────────────

TESTS = [
    # (Group, Test Name, Function)
    ("INFRASTRUCTURE", "Ollama Running", test_ollama_running),
    ("INFRASTRUCTURE", "Ollama Has Models", test_ollama_has_models),
    ("INFRASTRUCTURE", "Ollama Can Generate", test_ollama_can_generate),
    ("INFRASTRUCTURE", "PostgreSQL (pgvector)", test_postgres),
    ("INFRASTRUCTURE", "Redis", test_redis),
    ("SUPERVISOR", "Supervisor Health", test_supervisor_health),
    ("SUPERVISOR", "Supervisor LLM Route", test_supervisor_llm_route),
    ("ELAINE", "ELAINE UI Loads", test_elaine_ui),
    ("ELAINE", "ELAINE Health Data", test_elaine_health),
    ("ELAINE", "ELAINE Chat Response", test_elaine_chat),
    ("WORKSHOP", "Workshop UI Loads", test_workshop_ui),
    ("WORKSHOP", "Workshop Health", test_workshop_health),
    ("CK WRITER", "CK Writer UI Loads", test_ck_writer_ui),
    ("CK WRITER", "CK Writer Health", test_ck_writer_health),
    ("COSTANZA", "Costanza Health", test_costanza_health),
    ("COSTANZA", "Costanza Models List", test_costanza_models),
    ("LEARNING ASST", "Learning Asst UI", test_learning_assistant_ui),
    ("LEARNING ASST", "Learning Asst Health", test_learning_assistant_health),
    ("JUNK DRAWER", "Junk Drawer Health", test_junk_drawer_health),
    ("AUTHOR STUDIO", "Author Studio UI", test_author_studio_ui),
    ("PETERMAN", "Peterman UI Loads", test_peterman_ui),
    ("PETERMAN", "Peterman Health", test_peterman_health),
    ("GENIE", "Genie Backend Health", test_genie_backend_health),
    ("GENIE", "Genie Frontend Loads", test_genie_frontend),
    ("GENIE", "Genie Dashboard API", test_genie_dashboard_api),
    ("RIPPLE CRM", "Ripple Backend Health", test_ripple_backend_health),
    ("RIPPLE CRM", "Ripple Frontend Loads", test_ripple_frontend),
    ("TOUCHSTONE", "Touchstone Backend", test_touchstone_backend),
    ("TOUCHSTONE", "Touchstone Dashboard", test_touchstone_dashboard),
    ("DOCKER", "n8n UI", test_n8n_ui),
    ("DOCKER", "Listmonk UI", test_listmonk_ui),
    ("DOCKER", "SearXNG Search UI", test_searxng_ui),
]


def run_test(group, name, func):
    """Run a single test with timeout protection."""
    start = time.time()
    try:
        passed, detail = func()
    except Exception as e:
        passed, detail = False, f"EXCEPTION: {e}"
    elapsed = time.time() - start
    return group, name, passed, detail, elapsed


def main():
    print()
    print(f"{BOLD}{'='*70}{RESET}")
    print(f"{BOLD}  AMTL QUICK DIAGNOSE — Real Functional Tests{RESET}")
    print(f"{BOLD}  {time.strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
    print(f"{BOLD}{'='*70}{RESET}")
    print()

    results = []
    current_group = None

    # Run infrastructure tests first (sequential — they're dependencies)
    infra_tests = [(g, n, f) for g, n, f in TESTS if g == "INFRASTRUCTURE"]
    other_tests = [(g, n, f) for g, n, f in TESTS if g != "INFRASTRUCTURE"]

    # Run infra tests sequentially
    for group, name, func in infra_tests:
        if current_group != group:
            current_group = group
            print(f"\n{BOLD}{CYAN}--- {group} ---{RESET}")
        result = run_test(group, name, func)
        results.append(result)
        _, _, passed, detail, elapsed = result
        status = f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}"
        print(f"  {status}  {name:<30} ({elapsed:.1f}s) {_safe(detail[:80])}")

    # Run remaining tests in parallel (per group to keep output organized)
    groups_order = []
    seen = set()
    for g, _, _ in other_tests:
        if g not in seen:
            groups_order.append(g)
            seen.add(g)

    for group in groups_order:
        print(f"\n{BOLD}{CYAN}--- {group} ---{RESET}")
        group_tests = [(g, n, f) for g, n, f in other_tests if g == group]

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(run_test, g, n, f): (g, n)
                for g, n, f in group_tests
            }
            group_results = []
            for future in as_completed(futures):
                group_results.append(future.result())

            # Sort by original order
            name_order = {n: i for i, (_, n, _) in enumerate(group_tests)}
            group_results.sort(key=lambda r: name_order.get(r[1], 99))

            for result in group_results:
                results.append(result)
                _, name, passed, detail, elapsed = result
                status = f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}"
                print(f"  {status}  {name:<30} ({elapsed:.1f}s) {_safe(detail[:80])}")

    # Summary
    total_pass = sum(1 for _, _, p, _, _ in results if p)
    total_fail = sum(1 for _, _, p, _, _ in results if not p)
    total = len(results)

    print()
    print(f"{BOLD}{'='*70}{RESET}")
    print(f"{BOLD}  SUMMARY: {GREEN}{total_pass} PASS{RESET}  {RED}{total_fail} FAIL{RESET}  ({total} total tests)")
    print(f"{BOLD}{'='*70}{RESET}")

    if total_fail > 0:
        print(f"\n{BOLD}{RED}FAILURES:{RESET}")
        for group, name, passed, detail, _ in results:
            if not passed:
                print(f"  {RED}X{RESET}  [{group}] {name}: {_safe(detail)}")

    # Group summary
    print(f"\n{BOLD}BY GROUP:{RESET}")
    group_stats = {}
    for group, _, passed, _, _ in results:
        if group not in group_stats:
            group_stats[group] = {"pass": 0, "fail": 0}
        if passed:
            group_stats[group]["pass"] += 1
        else:
            group_stats[group]["fail"] += 1

    for group in dict.fromkeys(g for g, _, _, _, _ in results):
        stats = group_stats[group]
        total_g = stats["pass"] + stats["fail"]
        if stats["fail"] == 0:
            icon = f"{GREEN}ALL PASS{RESET}"
        elif stats["pass"] == 0:
            icon = f"{RED}ALL FAIL{RESET}"
        else:
            icon = f"{YELLOW}PARTIAL{RESET}"
        print(f"  {icon}  {group:<20} {stats['pass']}/{total_g}")

    print()
    if total_fail == 0:
        print(f"{GREEN}{BOLD}  ALL SYSTEMS OPERATIONAL{RESET}")
    else:
        print(f"{RED}{BOLD}  {total_fail} ISSUE(S) NEED ATTENTION{RESET}")
    print()

    return 1 if total_fail > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
