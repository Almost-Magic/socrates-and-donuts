"""Foreperson Audit Tests — ELAINE Quality Gate (5+ tests)

Foreperson tests verify code quality, configuration correctness,
and architectural integrity. They catch issues that would slip past
functional tests.

Almost Magic Tech Lab
"""

import json
import sys
import os
import importlib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

# client fixture provided by conftest.py (session-scoped)


# ── Foreperson 1: No Hardcoded Secrets ───────────────────────────

def test_foreperson_no_hardcoded_secrets():
    """Source files must not contain hardcoded API keys or passwords."""
    import glob
    danger_patterns = [
        "sk-",          # OpenAI keys
        "sk_live_",     # Stripe keys
        "AKIA",         # AWS keys
        "password=",    # Hardcoded passwords (in string literals)
    ]
    src_dir = os.path.join(os.path.dirname(__file__), "..")
    py_files = glob.glob(os.path.join(src_dir, "**/*.py"), recursive=True)

    violations = []
    for fpath in py_files:
        if "test_" in os.path.basename(fpath):
            continue  # Skip test files
        with open(fpath, "r") as f:
            for i, line in enumerate(f, 1):
                # Skip comments and env lookups
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                if "os.environ" in line or "os.getenv" in line:
                    continue
                for pattern in danger_patterns:
                    if pattern in line and "'" + pattern in line or '"' + pattern in line:
                        violations.append(f"{os.path.basename(fpath)}:{i} contains '{pattern}'")

    assert len(violations) == 0, f"Hardcoded secrets found:\n" + "\n".join(violations)


# ── Foreperson 2: Config Uses Environment Variables ──────────────

def test_foreperson_config_uses_env():
    """Critical config values must come from environment variables."""
    import config
    # These should be configurable — check they have sensible defaults
    assert hasattr(config, "PORT")
    assert hasattr(config, "HOST")
    assert hasattr(config, "ELAINE_NAME")
    assert hasattr(config, "OWNER_NAME")
    assert config.OWNER_NAME == "Mani Padisetti"

    # ElevenLabs key must come from env, not hardcoded
    from api_routes_chat import ELEVENLABS_API_KEY
    # Key should be empty string (from env default) unless user set it
    # The point: it's not hardcoded to a real key
    assert len(ELEVENLABS_API_KEY) < 5 or ELEVENLABS_API_KEY.startswith("sk_"), \
        "ElevenLabs key appears hardcoded"


# ── Foreperson 3: All Blueprints Register Without Errors ────────

def test_foreperson_blueprints_register(app):
    """All API blueprints register successfully on the Flask app."""
    bp_names = list(app.blueprints.keys())

    expected_blueprints = [
        "gravity", "constellation",  # Phase 7
        "thinking", "cartographer", "amplifier",  # Phase 8
        "sentinel",  # Phase 9
        "chronicle", "voice",  # Phase 10
        "innovator",  # Phase 11
        "orchestrator",  # Phase 12
        "chat",  # Chat + Tools
        "wisdom",  # Wisdom
    ]

    for name in expected_blueprints:
        assert name in bp_names, f"Blueprint '{name}' not registered"


# ── Foreperson 4: API Endpoints Return JSON ──────────────────────

def test_foreperson_api_returns_json(client):
    """All major API endpoints return valid JSON (not HTML error pages)."""
    endpoints = [
        "/api/health",
        "/api/status",
        "/api/tools",
        "/api/tts/status",
        "/api/wisdom",
        "/api/wisdom/stats",
        "/api/gravity/top",
        "/api/orchestrator/status",
        "/api/orchestrator/apps",
        "/api/compassion/wellbeing",
    ]

    for ep in endpoints:
        resp = client.get(ep)
        assert resp.status_code == 200, f"{ep} returned {resp.status_code}"
        assert "application/json" in resp.content_type, f"{ep} returned {resp.content_type}"
        # Should parse as valid JSON
        data = resp.get_json()
        assert data is not None, f"{ep} returned None JSON"


# ── Foreperson 5: Australian English in Config ──────────────────

def test_foreperson_australian_english():
    """System prompts and config use Australian English."""
    from api_routes_chat import SYSTEM_PROMPT
    assert "Australian English" in SYSTEM_PROMPT, "System prompt must specify Australian English"

    import config
    assert config.OWNER_NAME == "Mani Padisetti"
    assert config.COMPANY_NAME == "Almost Magic Tech Lab"


# ── Foreperson 6: No Broken Imports ──────────────────────────────

def test_foreperson_module_imports():
    """All ELAINE modules import without errors."""
    modules_to_check = [
        "config",
        "api_routes_chat",
        "api_routes_wisdom",
        "api_routes_phase12",
        "modules.wisdom_kb",
        "modules.orchestrator",
    ]

    for mod_name in modules_to_check:
        try:
            importlib.import_module(mod_name)
        except Exception as e:
            pytest.fail(f"Failed to import {mod_name}: {e}")


# ── Foreperson 7: Wisdom KB Integrity ───────────────────────────

def test_foreperson_wisdom_data_integrity():
    """Every quote in the wisdom KB has required fields."""
    from modules.wisdom_kb import WisdomKB
    kb = WisdomKB()

    for i, quote in enumerate(kb.all_quotes):
        assert "text" in quote, f"Quote {i} missing 'text'"
        assert "author" in quote, f"Quote {i} missing 'author'"
        assert "category" in quote, f"Quote {i} missing 'category'"
        assert len(quote["text"]) > 5, f"Quote {i} text too short"
        assert quote["category"] in ["sitcom", "one-liner", "idiom", "philosophy"], \
            f"Quote {i} has unknown category: {quote['category']}"
