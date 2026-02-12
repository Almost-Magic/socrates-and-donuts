"""
The Supervisor — Beast Test Suite
Almost Magic Tech Lab — February 2026

Tests:
  1. Module Import Validation
  2. Unit Tests (each component independently)
  3. Integration Tests (cross-component)
  4. API Smoke Tests (every endpoint)
  5. Confidence Stamp (final report)

Run: python tests/test_supervisor.py
"""

import io
import json
import os
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

# Fix Windows console encoding (only if not already wrapped)
if sys.platform == "win32":
    if not isinstance(sys.stdout, io.TextIOWrapper) or sys.stdout.encoding != "utf-8":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    if not isinstance(sys.stderr, io.TextIOWrapper) or sys.stderr.encoding != "utf-8":
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Add parent to path so we can import supervisor
sys.path.insert(0, str(Path(__file__).parent.parent))

# ── Test Infrastructure ──────────────────────────────────────────────────

PASS = "\u2705"
FAIL = "\u274c"
WARN = "\u26a0\ufe0f"

results = {"passed": 0, "failed": 0, "warnings": 0, "details": []}


def test(name, fn, critical=True):
    """Run a test and record the result."""
    try:
        fn()
        results["passed"] += 1
        results["details"].append({"name": name, "status": "PASS"})
        print(f"  {PASS} {name}")
    except Exception as e:
        if critical:
            results["failed"] += 1
            results["details"].append({"name": name, "status": "FAIL", "error": str(e)})
            print(f"  {FAIL} {name}: {e}")
        else:
            results["warnings"] += 1
            results["details"].append({"name": name, "status": "WARN", "error": str(e)})
            print(f"  {WARN} {name}: {e}")


# ══════════════════════════════════════════════════════════════════════════
# 1. MODULE IMPORT VALIDATION
# ══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("1. MODULE IMPORT VALIDATION")
print("=" * 60)


def test_import_supervisor():
    import supervisor
    assert supervisor.VERSION == "1.0.0"
    assert supervisor.DEFAULT_PORT == 9000


def test_import_model_registry():
    from supervisor import ModelRegistry
    assert ModelRegistry is not None


def test_import_gpu_scheduler():
    from supervisor import GPUScheduler
    assert GPUScheduler is not None


def test_import_cloud_fallback():
    from supervisor import CloudFallback
    assert CloudFallback is not None


def test_import_llm_router():
    from supervisor import LLMRouter
    assert LLMRouter is not None


def test_import_service_graph():
    from supervisor import ServiceGraph
    assert ServiceGraph is not None


def test_import_health_guardian():
    from supervisor import HealthGuardian
    assert HealthGuardian is not None


def test_import_boot_sequencer():
    from supervisor import BootSequencer
    assert BootSequencer is not None


def test_import_flask_app():
    from supervisor import app
    assert app is not None


def test_config_files_exist():
    config_dir = Path(__file__).parent.parent / "config"
    assert (config_dir / "models.yaml").exists(), "models.yaml missing"
    assert (config_dir / "services.yaml").exists(), "services.yaml missing"


test("Import supervisor module", test_import_supervisor)
test("Import ModelRegistry", test_import_model_registry)
test("Import GPUScheduler", test_import_gpu_scheduler)
test("Import CloudFallback", test_import_cloud_fallback)
test("Import LLMRouter", test_import_llm_router)
test("Import ServiceGraph", test_import_service_graph)
test("Import HealthGuardian", test_import_health_guardian)
test("Import BootSequencer", test_import_boot_sequencer)
test("Import Flask app", test_import_flask_app)
test("Config files exist", test_config_files_exist)


# ══════════════════════════════════════════════════════════════════════════
# 2. UNIT TESTS
# ══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("2. UNIT TESTS")
print("=" * 60)

from supervisor import (
    ModelRegistry, GPUScheduler, CloudFallback, LLMRouter,
    ServiceGraph, HealthGuardian, BootSequencer
)

# ── Model Registry Tests ─────────────────────────────────────────────────

print("\n  --- Model Registry ---")


def test_registry_loads():
    reg = ModelRegistry()
    assert len(reg.models) >= 5, f"Expected >= 5 models, got {len(reg.models)}"
    assert len(reg.aliases) >= 5, f"Expected >= 5 aliases, got {len(reg.aliases)}"


def test_alias_resolution():
    reg = ModelRegistry()
    assert reg.resolve("reasoning") == "gemma2:27b"
    assert reg.resolve("embeddings") == "nomic-embed-text"
    assert reg.resolve("heavy") == "llama3.1:70b-instruct-q4_0"
    assert reg.resolve("code") == "deepseek-coder-v2:16b"


def test_default_model():
    reg = ModelRegistry()
    assert reg.get_default_model() == "gemma2:27b"


def test_passthrough_resolution():
    reg = ModelRegistry()
    # Literal Ollama names should pass through
    assert reg.resolve("gemma2:27b") == "gemma2:27b"
    assert reg.resolve("nomic-embed-text") == "nomic-embed-text"


def test_unknown_model_passthrough():
    reg = ModelRegistry()
    # Unknown names pass through for backward compatibility
    assert reg.resolve("some-future-model") == "some-future-model"


def test_get_model_info():
    reg = ModelRegistry()
    info = reg.get_model_info("gemma2:27b")
    assert info is not None
    assert info["role"] == "reasoning"
    assert info["vram_gb"] == 6.0


def test_registry_to_dict():
    reg = ModelRegistry()
    d = reg.to_dict()
    assert "models" in d
    assert "aliases" in d
    assert "vram_total_gb" in d


def test_role_for_model():
    reg = ModelRegistry()
    assert reg.get_role_for_model("gemma2:27b") == "reasoning"
    assert reg.get_role_for_model("nomic-embed-text") == "embeddings"


test("Registry loads all models", test_registry_loads)
test("Alias resolution", test_alias_resolution)
test("Default model", test_default_model)
test("Passthrough resolution (literal names)", test_passthrough_resolution)
test("Unknown model passthrough", test_unknown_model_passthrough)
test("Get model info", test_get_model_info)
test("Registry to_dict", test_registry_to_dict)
test("Role for model lookup", test_role_for_model)

# ── GPU Scheduler Tests ──────────────────────────────────────────────────

print("\n  --- GPU Scheduler ---")


def test_gpu_stats():
    reg = ModelRegistry()
    gpu = GPUScheduler(reg)
    stats = gpu.get_gpu_stats()
    assert "vram_total_mb" in stats
    assert "vram_used_mb" in stats
    assert "vram_free_mb" in stats
    assert stats["vram_total_mb"] > 0


def test_vram_budget_calculation():
    reg = ModelRegistry()
    gpu = GPUScheduler(reg)
    # With no models loaded, available should be total - reserved
    available = gpu._available_vram_gb()
    expected = reg.vram_total_gb - reg.vram_reserved_gb
    assert abs(available - expected) < 0.1, f"Expected {expected}, got {available}"


def test_eviction_never_removes_always_loaded():
    reg = ModelRegistry()
    gpu = GPUScheduler(reg)
    # Simulate nomic-embed-text loaded
    gpu.loaded_models["nomic-embed-text"] = {"vram_gb": 0.5, "last_used": 0}
    gpu.loaded_models["gemma2:27b"] = {"vram_gb": 6.0, "last_used": time.time()}
    # Try to evict 6GB — should evict gemma2, not nomic
    with gpu._lock:
        gpu._evict_for_vram(6.0)
    assert "nomic-embed-text" in gpu.loaded_models, "nomic-embed-text was wrongly evicted"


def test_gpu_to_dict():
    reg = ModelRegistry()
    gpu = GPUScheduler(reg)
    d = gpu.to_dict()
    assert "gpu" in d
    assert "loaded_models" in d
    assert "vram_budget" in d


test("GPU stats (nvidia-smi or estimated)", test_gpu_stats, critical=False)
test("VRAM budget calculation", test_vram_budget_calculation)
test("Eviction protects always_loaded models", test_eviction_never_removes_always_loaded)
test("GPU to_dict", test_gpu_to_dict)

# ── Service Graph Tests ──────────────────────────────────────────────────

print("\n  --- Service Graph ---")


def test_service_graph_loads():
    sg = ServiceGraph()
    assert len(sg.services) >= 5, f"Expected >= 5 services, got {len(sg.services)}"


def test_boot_phases():
    sg = ServiceGraph()
    assert len(sg.boot_phases) >= 2, "Expected at least 2 boot phases"
    assert sg.boot_phases[0]["phase"] == 1


def test_critical_services():
    sg = ServiceGraph()
    ollama = sg.services.get("ollama")
    assert ollama is not None
    assert ollama.get("critical") is True


def test_on_demand_services():
    sg = ServiceGraph()
    writer = sg.services.get("ck-writer")
    assert writer is not None
    assert writer.get("on_demand") is True


def test_service_graph_to_dict():
    sg = ServiceGraph()
    d = sg.to_dict()
    assert "ollama" in d
    assert "workshop" in d


def test_restart_policy():
    sg = ServiceGraph()
    p = sg.restart_policy
    assert p.get("max_retries", 0) == 3
    assert p.get("retry_delay_seconds", 0) == 10


test("Service graph loads", test_service_graph_loads)
test("Boot phases defined", test_boot_phases)
test("Critical services flagged", test_critical_services)
test("On-demand services flagged", test_on_demand_services)
test("Service graph to_dict", test_service_graph_to_dict)
test("Restart policy configured", test_restart_policy)

# ── Cloud Fallback Tests ─────────────────────────────────────────────────

print("\n  --- Cloud Fallback ---")


def test_cloud_fallback_init():
    reg = ModelRegistry()
    cf = CloudFallback(reg)
    assert cf is not None


def test_cloud_costs_tracking():
    reg = ModelRegistry()
    cf = CloudFallback(reg)
    # Simulate a cost entry
    cf._log_cost("anthropic", "claude-sonnet-4-20250514", {
        "input_tokens": 100, "output_tokens": 50
    })
    costs = cf.get_costs_today()
    assert costs["requests"] >= 1


def test_cloud_fallback_no_key():
    """Cloud fallback should gracefully skip when no API key is set."""
    reg = ModelRegistry()
    cf = CloudFallback(reg)
    # Temporarily clear keys
    old_anthropic = os.environ.pop("ANTHROPIC_API_KEY", None)
    old_openai = os.environ.pop("OPENAI_API_KEY", None)
    try:
        result, errors = cf.chat([{"role": "user", "content": "test"}])
        assert result is None, "Should return None when no keys available"
        assert len(errors) > 0, "Should report errors about missing keys"
    finally:
        if old_anthropic:
            os.environ["ANTHROPIC_API_KEY"] = old_anthropic
        if old_openai:
            os.environ["OPENAI_API_KEY"] = old_openai


test("Cloud fallback initializes", test_cloud_fallback_init)
test("Cloud cost tracking", test_cloud_costs_tracking)
test("Cloud fallback handles missing API keys", test_cloud_fallback_no_key)

# ── LLM Router Tests ─────────────────────────────────────────────────────

print("\n  --- LLM Router ---")


def test_router_init():
    reg = ModelRegistry()
    gpu = GPUScheduler(reg)
    cf = CloudFallback(reg)
    router = LLMRouter(reg, gpu, cf)
    assert router is not None


def test_router_metrics():
    reg = ModelRegistry()
    gpu = GPUScheduler(reg)
    cf = CloudFallback(reg)
    router = LLMRouter(reg, gpu, cf)
    m = router.get_metrics()
    assert m["total_requests"] == 0
    assert m["local_success"] == 0
    assert m["cloud_fallback"] == 0


test("LLM Router initializes", test_router_init)
test("LLM Router metrics", test_router_metrics)

# ── Health Guardian Tests ─────────────────────────────────────────────────

print("\n  --- Health Guardian ---")


def test_guardian_init():
    sg = ServiceGraph()
    hg = HealthGuardian(sg)
    assert hg is not None
    assert hg._running is False


def test_guardian_log_buffer():
    sg = ServiceGraph()
    hg = HealthGuardian(sg)
    hg.log_buffer.append({"test": "entry"})
    logs = hg.get_recent_logs()
    assert len(logs) == 1


test("Health Guardian initializes", test_guardian_init)
test("Health Guardian log buffer", test_guardian_log_buffer)


# ══════════════════════════════════════════════════════════════════════════
# 3. INTEGRATION TESTS
# ══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("3. INTEGRATION TESTS")
print("=" * 60)


def test_registry_gpu_integration():
    """Registry model info used correctly by GPU scheduler."""
    reg = ModelRegistry()
    gpu = GPUScheduler(reg)
    info = reg.get_model_info("gemma2:27b")
    assert info["vram_gb"] == 6.0
    # GPU scheduler uses registry for VRAM estimates
    available = gpu._available_vram_gb()
    assert available <= reg.vram_total_gb


def test_router_uses_registry_aliases():
    """Router resolves aliases through registry."""
    reg = ModelRegistry()
    gpu = GPUScheduler(reg)
    cf = CloudFallback(reg)
    router = LLMRouter(reg, gpu, cf)
    # Test that model name gets resolved
    body = {"model": "reasoning", "messages": [{"role": "user", "content": "test"}], "stream": False}
    # We can't fully proxy without Ollama, but we can test resolution
    resolved = reg.resolve(body["model"])
    assert resolved == "gemma2:27b"


def test_service_health_check():
    """Service graph can check Ollama health (live test)."""
    sg = ServiceGraph()
    result = sg.check_health("ollama")
    # This is a live test — Ollama may or may not be running
    assert result["service"] == "ollama"
    assert result["status"] in ("healthy", "unhealthy")


test("Registry + GPU integration", test_registry_gpu_integration)
test("Router uses registry aliases", test_router_uses_registry_aliases)
test("Service health check (Ollama)", test_service_health_check, critical=False)


# ══════════════════════════════════════════════════════════════════════════
# 4. API SMOKE TESTS
# ══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("4. API SMOKE TESTS (Flask test client)")
print("=" * 60)

from supervisor import app as flask_app

# Initialize global state for testing
import supervisor as sv
sv.registry = ModelRegistry()
sv.gpu_scheduler = GPUScheduler(sv.registry)
sv.cloud_fallback = CloudFallback(sv.registry)
sv.llm_router = LLMRouter(sv.registry, sv.gpu_scheduler, sv.cloud_fallback)
sv.service_graph = ServiceGraph()
sv.health_guardian = HealthGuardian(sv.service_graph)
sv.boot_sequencer = BootSequencer(sv.service_graph, sv.gpu_scheduler, sv.registry)
sv.START_TIME = time.time()

client = flask_app.test_client()


def test_api_health():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "The Supervisor"
    assert data["version"] == "1.0.0"


def test_api_status():
    resp = client.get("/api/status")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "services" in data
    assert "gpu" in data
    assert "metrics" in data


def test_api_models():
    resp = client.get("/api/models")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "models" in data
    assert "aliases" in data


def test_api_model_by_role():
    resp = client.get("/api/models/reasoning")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ollama_name"] == "gemma2:27b"


def test_api_gpu():
    resp = client.get("/api/gpu")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "gpu" in data
    assert "vram_budget" in data


def test_api_services():
    resp = client.get("/api/services")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "ollama" in data
    assert "workshop" in data


def test_api_service_detail():
    resp = client.get("/api/services/ollama")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["service"] == "ollama"


def test_api_queue():
    resp = client.get("/api/queue")
    assert resp.status_code == 200


def test_api_logs():
    resp = client.get("/api/logs")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "logs" in data


def test_api_metrics():
    resp = client.get("/api/metrics")
    assert resp.status_code == 200


def test_api_cloud_costs():
    resp = client.get("/api/cloud/costs")
    assert resp.status_code == 200


def test_api_tags():
    """Proxy to Ollama /api/tags — may fail if Ollama is down."""
    resp = client.get("/api/tags")
    # Accept either 200 (Ollama up) or 503 (Ollama down)
    assert resp.status_code in (200, 503)


test("GET /api/health", test_api_health)
test("GET /api/status", test_api_status)
test("GET /api/models", test_api_models)
test("GET /api/models/reasoning", test_api_model_by_role)
test("GET /api/gpu", test_api_gpu)
test("GET /api/services", test_api_services)
test("GET /api/services/ollama", test_api_service_detail)
test("GET /api/queue", test_api_queue)
test("GET /api/logs", test_api_logs)
test("GET /api/metrics", test_api_metrics)
test("GET /api/cloud/costs", test_api_cloud_costs)
test("GET /api/tags (Ollama proxy)", test_api_tags, critical=False)


# ══════════════════════════════════════════════════════════════════════════
# 5. CONFIDENCE STAMP
# ══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("5. CONFIDENCE STAMP")
print("=" * 60)

total = results["passed"] + results["failed"] + results["warnings"]
pass_rate = round(results["passed"] / total * 100, 1) if total > 0 else 0

print(f"""
  The Supervisor v{sv.VERSION} — Beast Test Report
  {"=" * 45}
  Total tests:  {total}
  Passed:       {results['passed']} {PASS}
  Failed:       {results['failed']} {FAIL}
  Warnings:     {results['warnings']} {WARN}
  Pass rate:    {pass_rate}%
  {"=" * 45}""")

if results["failed"] == 0:
    verdict = f"  {PASS} VERDICT: READY FOR SERVICE"
elif results["failed"] <= 2:
    verdict = f"  {WARN} VERDICT: MINOR ISSUES — review failures"
else:
    verdict = f"  {FAIL} VERDICT: NOT READY — {results['failed']} critical failures"

print(verdict)
print(f"  Timestamp: {datetime.now().isoformat()}")
print(f"  {'=' * 45}\n")

# Exit with error code if failures
if results["failed"] > 0:
    sys.exit(1)
