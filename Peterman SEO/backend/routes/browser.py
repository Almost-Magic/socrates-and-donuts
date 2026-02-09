"""
Peterman V4.1 — Browser Automation Routes
Almost Magic Tech Lab

Manages browser-based LLM queries using existing subscriptions.
Eliminates $80-330/mo in API costs.
"""
import asyncio
from flask import Blueprint, jsonify, request
from ..services.browser_llm_service import browser_llm

browser_bp = Blueprint("browser", __name__)


def _run_async(coro):
    """Run async function from sync Flask context."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                return pool.submit(asyncio.run, coro).result()
        else:
            return asyncio.run(coro)
    except RuntimeError:
        return asyncio.run(coro)


# ----------------------------------------------------------
# Session Management
# ----------------------------------------------------------

@browser_bp.route("/api/browser/status", methods=["GET"])
def browser_status():
    """Check which LLM services have active browser sessions."""
    result = _run_async(browser_llm.health_check())
    return jsonify(result)


@browser_bp.route("/api/browser/login/<model_name>", methods=["POST"])
def open_login(model_name):
    """
    Open login page for a service.
    User logs in manually in the browser window.
    Models: chatgpt, claude, perplexity, gemini
    """
    valid = ["chatgpt", "claude", "perplexity", "gemini"]
    if model_name not in valid:
        return jsonify({"error": f"Unknown model. Valid: {valid}"}), 400

    result = _run_async(browser_llm.open_login_page(model_name))
    return jsonify(result)


@browser_bp.route("/api/browser/save-session/<model_name>", methods=["POST"])
def save_session(model_name):
    """Save browser session after manual login."""
    result = _run_async(browser_llm.save_current_session(model_name))
    return jsonify(result)


# ----------------------------------------------------------
# Single Model Queries
# ----------------------------------------------------------

@browser_bp.route("/api/browser/query/chatgpt", methods=["POST"])
def query_chatgpt():
    """Query ChatGPT via browser."""
    data = request.get_json()
    if not data or not data.get("prompt"):
        return jsonify({"error": "prompt required"}), 400

    result = _run_async(browser_llm.query_chatgpt(
        data["prompt"],
        timeout=data.get("timeout", 120)
    ))
    return jsonify(result)


@browser_bp.route("/api/browser/query/claude", methods=["POST"])
def query_claude():
    """Query Claude via browser."""
    data = request.get_json()
    if not data or not data.get("prompt"):
        return jsonify({"error": "prompt required"}), 400

    result = _run_async(browser_llm.query_claude(
        data["prompt"],
        timeout=data.get("timeout", 120)
    ))
    return jsonify(result)


@browser_bp.route("/api/browser/query/perplexity", methods=["POST"])
def query_perplexity():
    """Query Perplexity via browser — includes citations."""
    data = request.get_json()
    if not data or not data.get("prompt"):
        return jsonify({"error": "prompt required"}), 400

    result = _run_async(browser_llm.query_perplexity(
        data["prompt"],
        timeout=data.get("timeout", 120)
    ))
    return jsonify(result)


@browser_bp.route("/api/browser/query/gemini", methods=["POST"])
def query_gemini():
    """Query Gemini via browser."""
    data = request.get_json()
    if not data or not data.get("prompt"):
        return jsonify({"error": "prompt required"}), 400

    result = _run_async(browser_llm.query_gemini(
        data["prompt"],
        timeout=data.get("timeout", 120)
    ))
    return jsonify(result)


# ----------------------------------------------------------
# Multi-Model Query (for perception scans)
# ----------------------------------------------------------

@browser_bp.route("/api/browser/query/all", methods=["POST"])
def query_all():
    """
    Query all commercial models with the same prompt.
    Used by perception scans to compare responses.

    Body: {"prompt": "...", "models": ["chatgpt", "claude", "perplexity", "gemini"]}
    """
    data = request.get_json()
    if not data or not data.get("prompt"):
        return jsonify({"error": "prompt required"}), 400

    models = data.get("models", ["chatgpt", "claude", "perplexity", "gemini"])
    results = _run_async(browser_llm.query_all_commercial(data["prompt"], models))

    return jsonify({
        "prompt": data["prompt"],
        "results": results,
        "models_queried": len(results),
        "total_cost": 0.0,
        "source": "browser_subscriptions",
    })
