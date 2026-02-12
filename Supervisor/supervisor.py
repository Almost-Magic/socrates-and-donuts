"""
The Supervisor — Centralised Runtime Manager
Almost Magic Tech Lab — February 2026
Port 9000

Components:
  1. GPU Scheduler     — VRAM tracking, conflict prevention, model loading
  2. Model Registry    — models.yaml, alias resolution, no hardcoded names
  3. Service Graph     — Dependency ordering, startup/shutdown, health checks
  4. LLM Router        — Local Ollama first, cloud fallback on failure
  5. Health Guardian    — 30s health checks, auto-restart (3 retries), alerting
  6. Cloud Fallback    — Anthropic/OpenAI transparent fallback

Usage:
    python supervisor.py              Start on port 9000
    python supervisor.py --boot       Run boot sequence then start
    python supervisor.py --status     Print status and exit
    python supervisor.py --port 9000  Custom port

"The Supervisor is the backbone. Every AI request routes through it."
— Almost Magic Tech Lab
"""

import argparse
import io
import json
import logging
import os
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

# Windows console encoding fix (guard against double-wrapping)
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "buffer") and getattr(sys.stdout, "encoding", "") != "utf-8":
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "buffer") and getattr(sys.stderr, "encoding", "") != "utf-8":
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except ValueError:
        pass  # Already wrapped or buffer closed

try:
    import yaml
except ImportError:
    print("PyYAML required: pip install pyyaml")
    sys.exit(1)

try:
    from flask import Flask, jsonify, request as flask_request
except ImportError:
    print("Flask required: pip install flask")
    sys.exit(1)

try:
    import requests as req_lib
except ImportError:
    print("Requests required: pip install requests")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
VERSION = "1.0.0"
DEFAULT_PORT = 9000
OLLAMA_URL = "http://localhost:11434"
CREATE_NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0

BASE_DIR = Path(__file__).parent
CONFIG_DIR = BASE_DIR / "config"
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

SOURCE_BASE = BASE_DIR.parent  # Source and Brand/

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger("supervisor")
logger.setLevel(logging.DEBUG)

# File handler — structured
fh = logging.FileHandler(LOGS_DIR / "supervisor.log", encoding="utf-8")
fh.setLevel(logging.DEBUG)
fh.setFormatter(logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
))
logger.addHandler(fh)

# Console handler — concise
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
ch.setFormatter(logging.Formatter("  %(levelname)-8s %(message)s"))
logger.addHandler(ch)


# ═══════════════════════════════════════════════════════════════════════════
# 1. MODEL REGISTRY
# ═══════════════════════════════════════════════════════════════════════════

class ModelRegistry:
    """Loads models.yaml — single source of truth for model names and VRAM."""

    def __init__(self, config_path=None):
        self.config_path = config_path or (CONFIG_DIR / "models.yaml")
        self.config = {}
        self.models = {}
        self.aliases = {}
        self.cloud_fallback = {}
        self.vram_total_gb = 12.0
        self.vram_reserved_gb = 0.5
        self.load()

    def load(self):
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f) or {}
        self.models = self.config.get("models", {})
        self.aliases = self.config.get("aliases", {})
        self.cloud_fallback = self.config.get("cloud_fallback", {})
        self.vram_total_gb = self.config.get("vram_total_gb", 12.0)
        self.vram_reserved_gb = self.config.get("vram_reserved_gb", 0.5)
        logger.info(f"Model registry loaded: {len(self.models)} models, {len(self.aliases)} aliases")

    def resolve(self, name):
        """Resolve a model name or alias to the actual Ollama model name.

        Accepts: alias ("reasoning"), registry key ("gemma2-27b"), or
        literal Ollama name ("gemma2:27b"). Returns the Ollama name.
        """
        # 1. Check aliases
        if name in self.aliases:
            registry_key = self.aliases[name]
            if registry_key in self.models:
                return self.models[registry_key]["ollama_name"]

        # 2. Check registry keys directly
        if name in self.models:
            return self.models[name]["ollama_name"]

        # 3. Check if it's already an Ollama name
        for key, model in self.models.items():
            if model.get("ollama_name") == name:
                return name

        # 4. Pass through as-is (backward compatible)
        return name

    def get_model_info(self, name):
        """Get full model info from registry. Returns None if not found."""
        # Try alias first
        if name in self.aliases:
            name = self.aliases[name]
        if name in self.models:
            return self.models[name]
        # Try by ollama_name
        for key, model in self.models.items():
            if model.get("ollama_name") == name:
                return model
        return None

    def get_default_model(self):
        """Get the default model's Ollama name."""
        for key, model in self.models.items():
            if model.get("default"):
                return model["ollama_name"]
        return "gemma2:27b"  # fallback

    def get_role_for_model(self, ollama_name):
        """Get the role (reasoning, embeddings, etc.) for a given Ollama model."""
        for key, model in self.models.items():
            if model.get("ollama_name") == ollama_name:
                return model.get("role", "unknown")
        return "unknown"

    def to_dict(self):
        """Return registry as a JSON-serializable dict."""
        return {
            "vram_total_gb": self.vram_total_gb,
            "vram_reserved_gb": self.vram_reserved_gb,
            "models": {
                k: {
                    "ollama_name": v["ollama_name"],
                    "role": v.get("role", ""),
                    "vram_gb": v.get("vram_gb", 0),
                    "default": v.get("default", False),
                    "always_loaded": v.get("always_loaded", False),
                    "on_demand": v.get("on_demand", False),
                }
                for k, v in self.models.items()
            },
            "aliases": self.aliases,
        }


# ═══════════════════════════════════════════════════════════════════════════
# 2. GPU SCHEDULER
# ═══════════════════════════════════════════════════════════════════════════

class GPUScheduler:
    """Tracks VRAM usage, manages model loading/unloading."""

    def __init__(self, registry):
        self.registry = registry
        self.loaded_models = {}  # {ollama_name: {"vram_gb": float, "last_used": float}}
        self._lock = threading.Lock()

    def get_gpu_stats(self):
        """Get actual GPU VRAM usage from nvidia-smi."""
        try:
            result = subprocess.run(
                ["nvidia-smi",
                 "--query-gpu=memory.total,memory.used,memory.free,temperature.gpu",
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=5,
                creationflags=CREATE_NO_WINDOW
            )
            if result.returncode == 0:
                parts = result.stdout.strip().split(",")
                return {
                    "vram_total_mb": int(parts[0].strip()),
                    "vram_used_mb": int(parts[1].strip()),
                    "vram_free_mb": int(parts[2].strip()),
                    "temperature_c": int(parts[3].strip()),
                    "source": "nvidia-smi",
                }
        except Exception as e:
            logger.debug(f"nvidia-smi failed: {e}")
        # Fallback to theoretical estimates
        used = sum(m["vram_gb"] for m in self.loaded_models.values())
        total = self.registry.vram_total_gb
        return {
            "vram_total_mb": int(total * 1024),
            "vram_used_mb": int(used * 1024),
            "vram_free_mb": int((total - used) * 1024),
            "temperature_c": -1,
            "source": "estimated",
        }

    def get_loaded_models(self):
        """Query Ollama for currently loaded models."""
        try:
            resp = req_lib.get(f"{OLLAMA_URL}/api/ps", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                models = data.get("models", [])
                with self._lock:
                    self.loaded_models = {}
                    for m in models:
                        name = m.get("name", "")
                        size_bytes = m.get("size", 0)
                        vram_gb = round(size_bytes / (1024 ** 3), 1) if size_bytes else 0
                        # Use registry estimate if available
                        info = self.registry.get_model_info(name)
                        if info:
                            vram_gb = info.get("vram_gb", vram_gb)
                        self.loaded_models[name] = {
                            "vram_gb": vram_gb,
                            "last_used": time.time(),
                        }
                return list(self.loaded_models.keys())
        except Exception as e:
            logger.debug(f"Failed to query Ollama /api/ps: {e}")
        return list(self.loaded_models.keys())

    def ensure_model_loaded(self, ollama_name):
        """Ensure a model is loaded in Ollama. Unload others if VRAM is tight.

        Returns True if model is ready, False if loading failed.
        """
        with self._lock:
            # Already loaded?
            if ollama_name in self.loaded_models:
                self.loaded_models[ollama_name]["last_used"] = time.time()
                return True

            # Check VRAM budget
            info = self.registry.get_model_info(ollama_name)
            needed_gb = info.get("vram_gb", 6.0) if info else 6.0
            available_gb = self._available_vram_gb()

            if available_gb < needed_gb:
                self._evict_for_vram(needed_gb - available_gb)

        # Load the model by sending a minimal request
        try:
            logger.info(f"Loading model {ollama_name}...")
            resp = req_lib.post(
                f"{OLLAMA_URL}/api/generate",
                json={"model": ollama_name, "prompt": "", "keep_alive": "10m"},
                timeout=120
            )
            if resp.status_code == 200:
                with self._lock:
                    self.loaded_models[ollama_name] = {
                        "vram_gb": needed_gb,
                        "last_used": time.time(),
                    }
                logger.info(f"Model {ollama_name} loaded successfully")
                return True
            else:
                logger.error(f"Failed to load {ollama_name}: HTTP {resp.status_code}")
                return False
        except Exception as e:
            logger.error(f"Failed to load {ollama_name}: {e}")
            return False

    def _available_vram_gb(self):
        """Calculate available VRAM from loaded models."""
        total = self.registry.vram_total_gb
        reserved = self.registry.vram_reserved_gb
        used = sum(m["vram_gb"] for m in self.loaded_models.values())
        return total - reserved - used

    def _evict_for_vram(self, needed_gb):
        """Unload least-recently-used models until we free enough VRAM."""
        # Sort by last_used, oldest first. Never evict always_loaded models.
        evictable = []
        for name, info in self.loaded_models.items():
            model_info = self.registry.get_model_info(name)
            if model_info and model_info.get("always_loaded"):
                continue
            evictable.append((name, info))
        evictable.sort(key=lambda x: x[1]["last_used"])

        freed = 0
        for name, info in evictable:
            if freed >= needed_gb:
                break
            logger.info(f"Unloading model {name} to free VRAM...")
            self._unload_model(name)
            freed += info["vram_gb"]
            del self.loaded_models[name]

    def _unload_model(self, ollama_name):
        """Tell Ollama to unload a model."""
        try:
            req_lib.post(
                f"{OLLAMA_URL}/api/generate",
                json={"model": ollama_name, "prompt": "", "keep_alive": "0"},
                timeout=30
            )
        except Exception as e:
            logger.warning(f"Failed to unload {ollama_name}: {e}")

    def to_dict(self):
        gpu = self.get_gpu_stats()
        return {
            "gpu": gpu,
            "loaded_models": {
                name: {"vram_gb": info["vram_gb"], "last_used": info["last_used"]}
                for name, info in self.loaded_models.items()
            },
            "vram_budget": {
                "total_gb": self.registry.vram_total_gb,
                "reserved_gb": self.registry.vram_reserved_gb,
                "used_gb": round(sum(m["vram_gb"] for m in self.loaded_models.values()), 1),
                "available_gb": round(self._available_vram_gb(), 1),
            },
        }


# ═══════════════════════════════════════════════════════════════════════════
# 3. CLOUD FALLBACK
# ═══════════════════════════════════════════════════════════════════════════

class CloudFallback:
    """Transparent fallback to Anthropic/OpenAI when Ollama fails."""

    def __init__(self, registry):
        self.registry = registry
        self.costs = deque(maxlen=1000)

    def chat(self, messages, model_role="reasoning", **kwargs):
        """Try cloud providers in order for a chat request."""
        fallback_chain = self.registry.cloud_fallback.get(model_role, [])
        errors = []

        for provider_config in fallback_chain:
            provider = provider_config["provider"]
            model = provider_config["model"]
            env_key = provider_config["env_key"]
            api_key = os.environ.get(env_key, "")

            if not api_key:
                errors.append(f"{provider}: no API key ({env_key})")
                continue

            try:
                if provider == "anthropic":
                    result = self._call_anthropic(api_key, model, messages, **kwargs)
                elif provider == "openai":
                    result = self._call_openai(api_key, model, messages, **kwargs)
                else:
                    continue

                if result:
                    logger.info(f"Cloud fallback succeeded: {provider}/{model}")
                    return result
            except Exception as e:
                errors.append(f"{provider}/{model}: {e}")
                logger.warning(f"Cloud fallback {provider}/{model} failed: {e}")

        return None, errors

    def _call_anthropic(self, api_key, model, messages, **kwargs):
        """Call Anthropic Messages API and return Ollama-format response."""
        system_msg = ""
        api_messages = []
        for msg in messages:
            if msg.get("role") == "system":
                system_msg = msg.get("content", "")
            else:
                api_messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", ""),
                })

        if not api_messages:
            api_messages = [{"role": "user", "content": "hello"}]

        payload = {
            "model": model,
            "max_tokens": kwargs.get("max_tokens", 4096),
            "messages": api_messages,
        }
        if system_msg:
            payload["system"] = system_msg

        resp = req_lib.post(
            "https://api.anthropic.com/v1/messages",
            json=payload,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()

        content = ""
        for block in data.get("content", []):
            if block.get("type") == "text":
                content += block.get("text", "")

        tokens = data.get("usage", {})
        self._log_cost("anthropic", model, tokens)

        return {
            "model": model,
            "message": {"role": "assistant", "content": content},
            "done": True,
            "eval_count": tokens.get("output_tokens", 0),
            "prompt_eval_count": tokens.get("input_tokens", 0),
            "_source": "cloud:anthropic",
        }

    def _call_openai(self, api_key, model, messages, **kwargs):
        """Call OpenAI Chat Completions and return Ollama-format response."""
        resp = req_lib.post(
            "https://api.openai.com/v1/chat/completions",
            json={
                "model": model,
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", 4096),
            },
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()

        choice = data.get("choices", [{}])[0]
        content = choice.get("message", {}).get("content", "")
        tokens = data.get("usage", {})
        self._log_cost("openai", model, tokens)

        return {
            "model": model,
            "message": {"role": "assistant", "content": content},
            "done": True,
            "eval_count": tokens.get("completion_tokens", 0),
            "prompt_eval_count": tokens.get("prompt_tokens", 0),
            "_source": "cloud:openai",
        }

    def _log_cost(self, provider, model, tokens):
        """Track cloud API costs."""
        COST_PER_1M = {
            "anthropic": {"input": 3.0, "output": 15.0},
            "openai": {"input": 0.15, "output": 0.60},
        }
        rates = COST_PER_1M.get(provider, {"input": 1.0, "output": 3.0})
        input_tokens = tokens.get("input_tokens", tokens.get("prompt_tokens", 0))
        output_tokens = tokens.get("output_tokens", tokens.get("completion_tokens", 0))
        cost = (input_tokens * rates["input"] + output_tokens * rates["output"]) / 1_000_000

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "provider": provider,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": round(cost, 6),
        }
        self.costs.append(entry)

        try:
            cost_log = LOGS_DIR / "cloud_costs.jsonl"
            with open(cost_log, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception:
            pass

    def get_costs_today(self):
        """Return cloud costs for today."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        today_costs = [c for c in self.costs if c["timestamp"].startswith(today)]
        total = sum(c["cost_usd"] for c in today_costs)
        return {
            "date": today,
            "total_usd": round(total, 4),
            "requests": len(today_costs),
            "breakdown": today_costs,
        }


# ═══════════════════════════════════════════════════════════════════════════
# 4. LLM ROUTER
# ═══════════════════════════════════════════════════════════════════════════

class LLMRouter:
    """Routes LLM requests: Ollama first, cloud fallback on failure."""

    def __init__(self, registry, gpu_scheduler, cloud_fallback):
        self.registry = registry
        self.gpu = gpu_scheduler
        self.cloud = cloud_fallback
        self.metrics = {
            "total_requests": 0,
            "local_success": 0,
            "cloud_fallback": 0,
            "errors": 0,
            "latencies_ms": deque(maxlen=100),
        }
        self._lock = threading.Lock()

    def proxy_chat(self, body):
        """Proxy /api/chat to Ollama with model resolution and fallback."""
        return self._proxy_request("/api/chat", body)

    def proxy_generate(self, body):
        """Proxy /api/generate to Ollama with model resolution and fallback."""
        return self._proxy_request("/api/generate", body)

    def proxy_embed(self, body):
        """Proxy /api/embed to Ollama (no cloud fallback for embeddings yet)."""
        model = body.get("model", "nomic-embed-text")
        body["model"] = self.registry.resolve(model)
        self.gpu.ensure_model_loaded(body["model"])
        try:
            resp = req_lib.post(f"{OLLAMA_URL}/api/embed", json=body, timeout=30)
            return resp.json(), resp.status_code
        except Exception as e:
            return {"error": f"Embedding failed: {e}"}, 503

    def _proxy_request(self, endpoint, body):
        """Core routing logic: resolve model, ensure loaded, try Ollama, fallback."""
        start = time.time()

        with self._lock:
            self.metrics["total_requests"] += 1

        # Resolve model name
        model = body.get("model", self.registry.get_default_model())
        ollama_name = self.registry.resolve(model)
        body["model"] = ollama_name

        # Ensure stream is false for Week 1
        body["stream"] = False

        # Ensure model is loaded
        self.gpu.ensure_model_loaded(ollama_name)

        # Try Ollama with retries
        last_error = None
        for attempt in range(3):
            try:
                resp = req_lib.post(
                    f"{OLLAMA_URL}{endpoint}",
                    json=body,
                    timeout=120,
                )
                if resp.status_code == 200:
                    result = resp.json()
                    result["_source"] = "local:ollama"
                    latency = int((time.time() - start) * 1000)
                    with self._lock:
                        self.metrics["local_success"] += 1
                        self.metrics["latencies_ms"].append(latency)
                    logger.info(f"LLM request served locally ({ollama_name}, {latency}ms)")
                    return result, 200
                else:
                    last_error = f"Ollama HTTP {resp.status_code}"
            except Exception as e:
                last_error = str(e)

            if attempt < 2:
                delay = (attempt + 1) * 2
                logger.warning(f"Ollama attempt {attempt + 1} failed: {last_error}. Retrying in {delay}s...")
                time.sleep(delay)

        # All Ollama attempts failed — try cloud
        logger.warning(f"Ollama failed after 3 attempts. Trying cloud fallback...")
        messages = body.get("messages", [])
        if not messages and "prompt" in body:
            messages = [{"role": "user", "content": body["prompt"]}]

        model_role = self.registry.get_role_for_model(ollama_name)
        cloud_result, errors = self.cloud.chat(messages, model_role=model_role)

        if cloud_result:
            latency = int((time.time() - start) * 1000)
            with self._lock:
                self.metrics["cloud_fallback"] += 1
                self.metrics["latencies_ms"].append(latency)
            logger.info(f"LLM request served via cloud ({cloud_result.get('_source')}, {latency}ms)")
            return cloud_result, 200

        # Everything failed
        with self._lock:
            self.metrics["errors"] += 1

        error_detail = {
            "error": "All AI backends unavailable",
            "tried": [f"ollama (3 attempts, last: {last_error})"] + (errors or []),
            "suggestion": "Check Ollama status or set ANTHROPIC_API_KEY / OPENAI_API_KEY",
        }
        logger.error(f"All backends failed for {ollama_name}: {error_detail}")
        return error_detail, 503

    def get_metrics(self):
        with self._lock:
            lats = list(self.metrics["latencies_ms"])
            return {
                "total_requests": self.metrics["total_requests"],
                "local_success": self.metrics["local_success"],
                "cloud_fallback": self.metrics["cloud_fallback"],
                "errors": self.metrics["errors"],
                "avg_latency_ms": round(sum(lats) / len(lats)) if lats else 0,
                "p95_latency_ms": round(sorted(lats)[int(len(lats) * 0.95)] if len(lats) >= 2 else 0),
            }


# ═══════════════════════════════════════════════════════════════════════════
# 5. SERVICE GRAPH
# ═══════════════════════════════════════════════════════════════════════════

class ServiceGraph:
    """Loads services.yaml — manages service lifecycle and health."""

    def __init__(self, config_path=None):
        self.config_path = config_path or (CONFIG_DIR / "services.yaml")
        self.config = {}
        self.services = {}
        self.docker_services = {}
        self.boot_phases = []
        self.restart_policy = {}
        self.health_results = {}  # {service_id: {"status": str, "last_check": str, ...}}
        self.processes = {}  # {service_id: subprocess.Popen}
        self.load()

    def load(self):
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f) or {}
        self.services = self.config.get("services", {})
        self.docker_services = self.config.get("docker_services", {})
        self.boot_phases = self.config.get("boot_phases", [])
        self.restart_policy = self.config.get("restart_policy", {
            "max_retries": 3, "retry_delay_seconds": 10,
            "backoff_multiplier": 2, "alert_after_exhaustion": True,
        })
        logger.info(f"Service graph loaded: {len(self.services)} services, "
                     f"{len(self.docker_services)} docker services")

    def check_health(self, service_id):
        """Check health of a single service. Returns dict."""
        svc = self.services.get(service_id) or self.docker_services.get(service_id)
        if not svc:
            return {"status": "unknown", "detail": f"Service '{service_id}' not found"}

        hc = svc.get("health_check", {})
        hc_type = hc.get("type", "tcp")
        port = svc.get("port", 0)

        result = {
            "service": service_id,
            "name": svc.get("name", service_id),
            "port": port,
            "status": "unknown",
            "detail": "",
            "last_check": datetime.now(timezone.utc).isoformat(),
        }

        if hc_type == "http":
            url = hc.get("url", f"http://localhost:{port}/")
            try:
                resp = req_lib.get(url, timeout=5)
                if resp.status_code < 500:
                    result["status"] = "healthy"
                    result["detail"] = f"HTTP {resp.status_code}"
                else:
                    result["status"] = "unhealthy"
                    result["detail"] = f"HTTP {resp.status_code}"
            except Exception as e:
                result["status"] = "unhealthy"
                result["detail"] = str(e)

        elif hc_type == "tcp":
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                r = sock.connect_ex(("localhost", port))
                sock.close()
                if r == 0:
                    result["status"] = "healthy"
                    result["detail"] = f"Port {port} open"
                else:
                    result["status"] = "unhealthy"
                    result["detail"] = f"Port {port} closed"
            except Exception as e:
                result["status"] = "unhealthy"
                result["detail"] = str(e)

        self.health_results[service_id] = result
        return result

    def check_all_health(self):
        """Check health of all services. Returns dict of results."""
        results = {}
        for sid in self.services:
            results[sid] = self.check_health(sid)
        for sid in self.docker_services:
            results[sid] = self.check_health(sid)
        return results

    def start_service(self, service_id):
        """Start a service via its configured command."""
        svc = self.services.get(service_id)
        if not svc:
            return {"error": f"Service '{service_id}' not found"}

        cmd = svc.get("start_command")
        if not cmd:
            return {"error": f"No start_command for '{service_id}'"}

        cwd = svc.get("cwd")
        full_cwd = str(SOURCE_BASE / cwd) if cwd else None

        # Check dependencies
        for dep in svc.get("depends_on", []):
            dep_health = self.check_health(dep)
            if dep_health["status"] != "healthy":
                return {"error": f"Dependency '{dep}' is not healthy: {dep_health['detail']}"}

        try:
            env = os.environ.copy()
            for k, v in svc.get("env", {}).items():
                env[k] = str(v)

            proc = subprocess.Popen(
                cmd, shell=True, cwd=full_cwd,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                creationflags=CREATE_NO_WINDOW,
                env=env,
            )
            self.processes[service_id] = proc
            logger.info(f"Started {svc['name']} (PID {proc.pid})")
            return {"status": "started", "service": service_id, "pid": proc.pid}
        except Exception as e:
            logger.error(f"Failed to start {service_id}: {e}")
            return {"error": str(e)}

    def stop_service(self, service_id):
        """Stop a managed service."""
        proc = self.processes.get(service_id)
        if proc:
            try:
                proc.terminate()
                proc.wait(timeout=10)
                del self.processes[service_id]
                logger.info(f"Stopped {service_id}")
                return {"status": "stopped", "service": service_id}
            except Exception as e:
                proc.kill()
                del self.processes[service_id]
                return {"status": "killed", "service": service_id, "detail": str(e)}
        return {"error": f"No managed process for '{service_id}'"}

    def restart_service(self, service_id):
        """Restart a service."""
        self.stop_service(service_id)
        time.sleep(2)
        return self.start_service(service_id)

    def to_dict(self):
        """Return all services with health status."""
        result = {}
        for sid, svc in self.services.items():
            health = self.health_results.get(sid, {"status": "unknown"})
            result[sid] = {
                "name": svc.get("name", sid),
                "port": svc.get("port", 0),
                "type": svc.get("type", ""),
                "critical": svc.get("critical", False),
                "on_demand": svc.get("on_demand", False),
                "status": health.get("status", "unknown"),
                "detail": health.get("detail", ""),
                "last_check": health.get("last_check", ""),
            }
        for sid, svc in self.docker_services.items():
            health = self.health_results.get(sid, {"status": "unknown"})
            result[sid] = {
                "name": svc.get("name", sid),
                "port": svc.get("port", 0),
                "type": "docker",
                "critical": False,
                "on_demand": False,
                "status": health.get("status", "unknown"),
                "detail": health.get("detail", ""),
                "last_check": health.get("last_check", ""),
            }
        return result


# ═══════════════════════════════════════════════════════════════════════════
# 6. HEALTH GUARDIAN
# ═══════════════════════════════════════════════════════════════════════════

class HealthGuardian:
    """Background thread: monitors critical services, auto-restarts on failure."""

    def __init__(self, service_graph):
        self.graph = service_graph
        self.failure_counts = {}
        self.restart_counts = {}
        self._running = False
        self._thread = None
        self.log_buffer = deque(maxlen=200)

    def start(self):
        """Start the guardian in a background thread."""
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True, name="HealthGuardian")
        self._thread.start()
        logger.info("Health Guardian started (30s interval)")

    def stop(self):
        self._running = False

    def _run(self):
        # Initial delay to let services start
        time.sleep(10)
        while self._running:
            try:
                self._check_cycle()
            except Exception as e:
                logger.error(f"Health Guardian error: {e}")
            time.sleep(30)

    def _check_cycle(self):
        """Run one health check cycle across all critical services."""
        policy = self.graph.restart_policy

        for sid, svc in self.graph.services.items():
            if svc.get("on_demand"):
                continue

            result = self.graph.check_health(sid)
            is_healthy = result["status"] == "healthy"
            entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "service": sid,
                "status": result["status"],
                "detail": result["detail"],
            }
            self.log_buffer.append(entry)

            if not is_healthy:
                self.failure_counts[sid] = self.failure_counts.get(sid, 0) + 1
                failures = self.failure_counts[sid]
                logger.warning(f"[Guardian] {svc['name']} unhealthy (#{failures}): {result['detail']}")

                if failures >= 3:
                    retries = self.restart_counts.get(sid, 0)
                    max_retries = policy.get("max_retries", 3)

                    if retries < max_retries:
                        delay = policy.get("retry_delay_seconds", 10) * (
                            policy.get("backoff_multiplier", 2) ** retries
                        )
                        logger.info(f"[Guardian] Restarting {svc['name']} (attempt {retries + 1}/{max_retries})...")
                        self.graph.restart_service(sid)
                        self.restart_counts[sid] = retries + 1
                        time.sleep(delay)
                    elif retries == max_retries:
                        logger.critical(
                            f"[Guardian] {svc['name']} failed after {max_retries} restart attempts. "
                            f"Manual intervention required."
                        )
                        self._write_alert(sid, svc)
                        self.restart_counts[sid] = retries + 1  # prevent spamming
            else:
                if self.failure_counts.get(sid, 0) > 0:
                    logger.info(f"[Guardian] {svc['name']} recovered")
                self.failure_counts[sid] = 0
                self.restart_counts[sid] = 0

    def _write_alert(self, service_id, svc):
        """Write alert to alerts.jsonl for ELAINE / friction-log."""
        alert = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "service_failure",
            "service": svc.get("name", service_id),
            "port": svc.get("port"),
            "message": f"{svc.get('name')} failed and could not be auto-restarted",
        }
        try:
            alerts_path = LOGS_DIR / "alerts.jsonl"
            with open(alerts_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(alert) + "\n")
        except Exception:
            pass

    def get_recent_logs(self, n=100):
        return list(self.log_buffer)[-n:]


# ═══════════════════════════════════════════════════════════════════════════
# 7. BOOT SEQUENCER
# ═══════════════════════════════════════════════════════════════════════════

class BootSequencer:
    """Orchestrates phased startup of all services."""

    def __init__(self, service_graph, gpu_scheduler, registry):
        self.graph = service_graph
        self.gpu = gpu_scheduler
        self.registry = registry

    def run_boot(self):
        """Execute the full boot sequence. Returns report."""
        report = {
            "started_at": datetime.now(timezone.utc).isoformat(),
            "phases": [],
            "errors": [],
        }
        logger.info("=" * 50)
        logger.info("BOOT SEQUENCE STARTED")
        logger.info("=" * 50)

        for phase_config in self.graph.boot_phases:
            phase_num = phase_config["phase"]
            phase_name = phase_config["name"]
            service_ids = phase_config.get("services", [])
            timeout = phase_config.get("timeout_seconds", 60)

            logger.info(f"Phase {phase_num}: {phase_name}")
            phase_report = {"phase": phase_num, "name": phase_name, "services": []}

            for sid in service_ids:
                svc = self.graph.services.get(sid)
                if not svc:
                    report["errors"].append(f"Unknown service in boot phase: {sid}")
                    continue

                # Check if already running
                health = self.graph.check_health(sid)
                if health["status"] == "healthy":
                    logger.info(f"  {svc['name']} already running")
                    phase_report["services"].append({"id": sid, "status": "already_running"})
                    continue

                # Start it
                result = self.graph.start_service(sid)
                if "error" in result:
                    report["errors"].append(f"{sid}: {result['error']}")
                    phase_report["services"].append({"id": sid, "status": "failed", "error": result["error"]})
                    continue

                # Wait for health
                healthy = self._wait_for_health(sid, timeout)
                if healthy:
                    phase_report["services"].append({"id": sid, "status": "started"})

                    # Run post_start actions
                    for action in svc.get("post_start", []):
                        if action.get("action") == "preload_model":
                            model_key = action["model"]
                            ollama_name = self.registry.resolve(model_key)
                            logger.info(f"  Preloading model: {ollama_name}")
                            self.gpu.ensure_model_loaded(ollama_name)
                else:
                    report["errors"].append(f"{sid}: did not become healthy within {timeout}s")
                    phase_report["services"].append({"id": sid, "status": "timeout"})

            report["phases"].append(phase_report)

        report["completed_at"] = datetime.now(timezone.utc).isoformat()
        logger.info("=" * 50)
        logger.info(f"BOOT SEQUENCE COMPLETE — {len(report['errors'])} errors")
        logger.info("=" * 50)
        return report

    def _wait_for_health(self, service_id, timeout):
        """Wait for a service to become healthy."""
        start = time.time()
        while time.time() - start < timeout:
            health = self.graph.check_health(service_id)
            if health["status"] == "healthy":
                return True
            time.sleep(2)
        return False


# ═══════════════════════════════════════════════════════════════════════════
# FLASK APPLICATION
# ═══════════════════════════════════════════════════════════════════════════

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

# Global instances — initialized in main()
registry = None
gpu_scheduler = None
cloud_fallback = None
llm_router = None
service_graph = None
health_guardian = None
boot_sequencer = None
START_TIME = None


# ── Management Endpoints ─────────────────────────────────────────────────

@app.route("/api/health")
def api_health():
    return jsonify({
        "status": "healthy",
        "service": "The Supervisor",
        "version": VERSION,
        "uptime_seconds": round(time.time() - START_TIME, 1) if START_TIME else 0,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


@app.route("/api/status")
def api_status():
    services = service_graph.check_all_health() if service_graph else {}
    gpu = gpu_scheduler.to_dict() if gpu_scheduler else {}
    return jsonify({
        "status": "healthy",
        "service": "The Supervisor",
        "version": VERSION,
        "uptime_seconds": round(time.time() - START_TIME, 1) if START_TIME else 0,
        "services": services,
        "gpu": gpu,
        "metrics": llm_router.get_metrics() if llm_router else {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


@app.route("/api/models")
def api_models():
    if not registry:
        return jsonify({"error": "Registry not loaded"}), 503
    data = registry.to_dict()
    # Add load status
    if gpu_scheduler:
        loaded = gpu_scheduler.loaded_models
        for key, model in data["models"].items():
            model["loaded"] = model["ollama_name"] in loaded
    return jsonify(data)


@app.route("/api/models/<role>")
def api_model_by_role(role):
    if not registry:
        return jsonify({"error": "Registry not loaded"}), 503
    ollama_name = registry.resolve(role)
    info = registry.get_model_info(ollama_name)
    if info:
        return jsonify({"role": role, "ollama_name": ollama_name, **info})
    return jsonify({"role": role, "ollama_name": ollama_name, "note": "Not in registry"})


@app.route("/api/models/load", methods=["POST"])
def api_load_model():
    body = flask_request.get_json(force=True, silent=True) or {}
    model = body.get("model", "")
    if not model:
        return jsonify({"error": "model required"}), 400
    ollama_name = registry.resolve(model)
    success = gpu_scheduler.ensure_model_loaded(ollama_name)
    return jsonify({"model": ollama_name, "loaded": success})


@app.route("/api/models/unload", methods=["POST"])
def api_unload_model():
    body = flask_request.get_json(force=True, silent=True) or {}
    model = body.get("model", "")
    if not model:
        return jsonify({"error": "model required"}), 400
    ollama_name = registry.resolve(model)
    gpu_scheduler._unload_model(ollama_name)
    with gpu_scheduler._lock:
        gpu_scheduler.loaded_models.pop(ollama_name, None)
    return jsonify({"model": ollama_name, "unloaded": True})


@app.route("/api/gpu")
def api_gpu():
    if not gpu_scheduler:
        return jsonify({"error": "GPU scheduler not loaded"}), 503
    return jsonify(gpu_scheduler.to_dict())


@app.route("/api/services")
def api_services():
    if not service_graph:
        return jsonify({"error": "Service graph not loaded"}), 503
    return jsonify(service_graph.to_dict())


@app.route("/api/services/<service_id>")
def api_service_detail(service_id):
    result = service_graph.check_health(service_id)
    return jsonify(result)


@app.route("/api/services/<service_id>/start", methods=["POST"])
def api_start_service(service_id):
    result = service_graph.start_service(service_id)
    status = 200 if "error" not in result else 500
    return jsonify(result), status


@app.route("/api/services/<service_id>/stop", methods=["POST"])
def api_stop_service(service_id):
    result = service_graph.stop_service(service_id)
    return jsonify(result)


@app.route("/api/services/<service_id>/restart", methods=["POST"])
def api_restart_service(service_id):
    result = service_graph.restart_service(service_id)
    status = 200 if "error" not in result else 500
    return jsonify(result), status


@app.route("/api/queue")
def api_queue():
    # Week 1: simple queue indicator
    return jsonify({"pending": 0, "note": "Queue tracking in v1.1"})


@app.route("/api/logs")
def api_logs():
    if health_guardian:
        return jsonify({"logs": health_guardian.get_recent_logs()})
    return jsonify({"logs": []})


@app.route("/api/metrics")
def api_metrics():
    if llm_router:
        return jsonify(llm_router.get_metrics())
    return jsonify({})


@app.route("/api/cloud/costs")
def api_cloud_costs():
    if cloud_fallback:
        return jsonify(cloud_fallback.get_costs_today())
    return jsonify({"total_usd": 0, "requests": 0})


@app.route("/api/boot", methods=["POST"])
def api_boot():
    if boot_sequencer:
        report = boot_sequencer.run_boot()
        return jsonify(report)
    return jsonify({"error": "Boot sequencer not initialized"}), 503


# ── Ollama-Compatible Proxy Endpoints ────────────────────────────────────

@app.route("/api/chat", methods=["POST"])
def proxy_chat():
    body = flask_request.get_json(force=True, silent=True) or {}
    result, status = llm_router.proxy_chat(body)
    return jsonify(result), status


@app.route("/api/generate", methods=["POST"])
def proxy_generate():
    body = flask_request.get_json(force=True, silent=True) or {}
    result, status = llm_router.proxy_generate(body)
    return jsonify(result), status


@app.route("/api/embed", methods=["POST"])
@app.route("/api/embeddings", methods=["POST"])
def proxy_embed():
    body = flask_request.get_json(force=True, silent=True) or {}
    result, status = llm_router.proxy_embed(body)
    return jsonify(result), status


@app.route("/api/tags")
def proxy_tags():
    """Proxy to Ollama /api/tags — list available models."""
    try:
        resp = req_lib.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": f"Ollama unavailable: {e}"}), 503


@app.route("/api/pull", methods=["POST"])
def proxy_pull():
    body = flask_request.get_json(force=True, silent=True) or {}
    try:
        resp = req_lib.post(f"{OLLAMA_URL}/api/pull", json=body, timeout=300)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 503


@app.route("/api/show", methods=["POST"])
def proxy_show():
    body = flask_request.get_json(force=True, silent=True) or {}
    try:
        resp = req_lib.post(f"{OLLAMA_URL}/api/show", json=body, timeout=30)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 503


@app.route("/api/ps")
def proxy_ps():
    """Proxy to Ollama /api/ps — list running models."""
    try:
        resp = req_lib.get(f"{OLLAMA_URL}/api/ps", timeout=5)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 503


# ═══════════════════════════════════════════════════════════════════════════
# CLI & MAIN
# ═══════════════════════════════════════════════════════════════════════════

def print_status():
    """Print current status to console and exit."""
    sg = ServiceGraph()
    results = sg.check_all_health()
    print("\n  The Supervisor — Status Check")
    print("  " + "-" * 40)
    for sid, r in results.items():
        icon = "\u2705" if r["status"] == "healthy" else "\u274c"
        name = r.get("name", sid)
        port = r.get("port", "")
        print(f"    {icon} {name} (:{port}) — {r.get('detail', r['status'])}")
    print()


def main():
    global registry, gpu_scheduler, cloud_fallback, llm_router
    global service_graph, health_guardian, boot_sequencer, START_TIME

    parser = argparse.ArgumentParser(
        description="The Supervisor — Centralised Runtime Manager (AMTL)",
    )
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port (default: 9000)")
    parser.add_argument("--boot", action="store_true", help="Run boot sequence before starting")
    parser.add_argument("--status", action="store_true", help="Print status and exit")
    args = parser.parse_args()

    if args.status:
        print_status()
        return

    print(f"\n  The Supervisor v{VERSION} — Almost Magic Tech Lab")
    print("  " + "-" * 50)

    # Initialize components
    logger.info("Initializing The Supervisor...")

    registry = ModelRegistry()
    gpu_scheduler = GPUScheduler(registry)
    cloud_fallback = CloudFallback(registry)
    llm_router = LLMRouter(registry, gpu_scheduler, cloud_fallback)
    service_graph = ServiceGraph()
    health_guardian = HealthGuardian(service_graph)
    boot_sequencer = BootSequencer(service_graph, gpu_scheduler, registry)

    # Sync loaded models from Ollama
    gpu_scheduler.get_loaded_models()

    # Run boot sequence if requested
    if args.boot:
        logger.info("Running boot sequence...")
        report = boot_sequencer.run_boot()
        if report["errors"]:
            for err in report["errors"]:
                logger.warning(f"Boot error: {err}")

    # Start Health Guardian
    health_guardian.start()

    START_TIME = time.time()

    print(f"  Port: {args.port}")
    print(f"  Models: {len(registry.models)} registered")
    print(f"  Services: {len(service_graph.services)} managed")
    print(f"  Health Guardian: active (30s interval)")
    print(f"  Ollama proxy: http://localhost:{args.port}/api/chat")
    print(f"  Dashboard: http://localhost:{args.port}/api/status")
    print(f"\n  \"The Supervisor is the backbone.\"\n")

    logger.info(f"The Supervisor starting on port {args.port}")
    app.run(host="0.0.0.0", port=args.port, debug=False, threaded=True)


if __name__ == "__main__":
    main()
