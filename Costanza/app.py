"""
Costanza — Mental Models Engine API
Port: 5001
Almost Magic Tech Lab

Flask wrapper around the Costanza thinking/communication/strategic engines.
AI synthesis via Ollama routed through The Supervisor (port 9000).
"""

import sys
import os
import json
import logging
import threading
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from flask import Flask, jsonify, request

# Add the library to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "AMTL Thinking", "costanza", "src"))

from costanza import (
    ThinkingFrameworksEngine, FrameworkType, StakesLevel, DecisionDomain,
    CommunicationEngine, CommunicationType, AudienceLevel,
    StrategicEngine,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ---------------------------------------------------------------------------
# LLM Configuration — route through Supervisor, fallback to direct Ollama
# ---------------------------------------------------------------------------
SUPERVISOR_URL = os.environ.get("SUPERVISOR_URL", "http://localhost:9000")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
COSTANZA_MODEL = os.environ.get("COSTANZA_MODEL", "llama3.2:3b")
LLM_TIMEOUT = 15
LLM_MAX_TOKENS = 200

# ---------------------------------------------------------------------------
# Initialise engines
# ---------------------------------------------------------------------------
thinking = ThinkingFrameworksEngine()
communication = CommunicationEngine()
strategic = StrategicEngine()

# Build model catalogue
MODELS = []

# Decision Intelligence (6 frameworks)
for ft in FrameworkType:
    MODELS.append({
        "id": ft.value,
        "name": ft.value.replace("_", " ").title(),
        "category": "decision_intelligence",
        "engine": "thinking",
    })

# Communication Frameworks (7 frameworks)
for ct in CommunicationType:
    MODELS.append({
        "id": f"comm_{ct.value}",
        "name": ct.value.replace("_", " ").title(),
        "category": "communication",
        "engine": "communication",
    })

# Strategic Analysis (8 frameworks)
for name in ["mece", "swot", "pestle", "three_cs", "seven_s", "bcg_matrix", "ansoff", "balanced_scorecard"]:
    MODELS.append({
        "id": f"strategic_{name}",
        "name": name.replace("_", " ").title(),
        "category": "strategic",
        "engine": "strategic",
    })


# ---------------------------------------------------------------------------
# LLM Helper — Supervisor first, Ollama fallback
# ---------------------------------------------------------------------------

def _call_llm(prompt):
    """Call Ollama via Supervisor for AI-enhanced synthesis. Falls back to direct Ollama."""
    payload = json.dumps({
        "model": COSTANZA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"num_predict": LLM_MAX_TOKENS},
    }).encode("utf-8")

    for base_url in [SUPERVISOR_URL, OLLAMA_URL]:
        try:
            req = Request(
                f"{base_url}/api/generate",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(req, timeout=LLM_TIMEOUT) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data.get("response", "").strip()
                if text:
                    return text
        except Exception as e:
            logger.warning(f"LLM call to {base_url} failed: {e}")
            continue

    return ""


def prewarm_model():
    """Prewarm LLM model with a tiny request so first real call is fast."""
    try:
        payload = json.dumps({
            "model": COSTANZA_MODEL,
            "prompt": "hi",
            "stream": False,
            "options": {"num_predict": 5},
        }).encode("utf-8")

        for base_url in [SUPERVISOR_URL, OLLAMA_URL]:
            try:
                req = Request(
                    f"{base_url}/api/generate",
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urlopen(req, timeout=10) as resp:
                    json.loads(resp.read())
                    logger.info(f"Model {COSTANZA_MODEL} pre-warmed via {base_url}")
                    return
            except Exception:
                continue
        logger.warning("Pre-warm failed — LLM may be unavailable (framework analysis still works)")
    except Exception as e:
        logger.warning(f"Pre-warm error: {e}")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health():
    # Quick LLM connectivity check
    llm_ok = False
    for base_url in [SUPERVISOR_URL, OLLAMA_URL]:
        try:
            req = Request(f"{base_url}/api/tags", method="GET")
            with urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    llm_ok = True
                    break
        except Exception:
            continue

    return jsonify({
        "status": "healthy",
        "service": "costanza",
        "version": "2.1.0",
        "engines": {
            "thinking": thinking.status(),
            "communication": communication.status(),
            "strategic": strategic.status(),
        },
        "llm": {"connected": llm_ok, "model": COSTANZA_MODEL, "supervisor": SUPERVISOR_URL},
        "total_frameworks": len(MODELS),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "app": "Costanza",
        "tagline": f"Mental Models Engine — {len(MODELS)} frameworks across 3 engines, AI-enhanced via Ollama",
        "version": "2.1.0",
        "endpoints": ["/api/health", "/api/models", "/api/analyze"],
        "engines": ["decision_intelligence", "communication", "strategic"],
    })


@app.route("/api/models", methods=["GET"])
def list_models():
    search = request.args.get("search", "").lower().strip()
    category = request.args.get("category", "").lower().strip()

    filtered = MODELS
    if search:
        filtered = [m for m in filtered if search in m["name"].lower() or search in m["id"].lower()]
    if category:
        filtered = [m for m in filtered if m["category"] == category]

    return jsonify({
        "models": filtered,
        "total": len(filtered),
        "categories": list(set(m["category"] for m in MODELS)),
    })


@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json() or {}
    situation = data.get("situation", "").strip()
    if not situation:
        return jsonify({"error": "No situation provided"}), 400

    domain_str = data.get("domain", "strategy")
    stakes_str = data.get("stakes", "medium")

    # Map strings to enums
    domain_map = {d.value: d for d in DecisionDomain}
    stakes_map = {s.value: s for s in StakesLevel}
    domain = domain_map.get(domain_str, DecisionDomain.STRATEGY)
    stakes = stakes_map.get(stakes_str, StakesLevel.MEDIUM)

    # Step 1: Pure Python framework analysis (always works)
    result = thinking.analyse(situation, domain=domain, stakes=stakes)

    frameworks = [ft.value for ft in getattr(result, "frameworks_applied", [])]
    synthesis = getattr(result, "synthesis", "")
    action = getattr(result, "recommended_action", "")
    confidence = getattr(result, "confidence", 0)

    # Step 2: AI-enhanced synthesis via Ollama/Supervisor
    ai_synthesis = ""
    if synthesis or frameworks:
        prompt = (
            f"You are Costanza, an AI mental models analyst. "
            f"Situation: \"{situation}\"\n"
            f"Domain: {domain.value}, Stakes: {stakes.value}\n"
            f"Frameworks applied: {', '.join(frameworks) if frameworks else 'none'}\n"
            f"Framework synthesis: {synthesis}\n"
            f"Recommended action: {action}\n\n"
            f"Enhance this analysis in 2-3 concise sentences. "
            f"Add practical insight the frameworks might miss. Be direct."
        )
        ai_synthesis = _call_llm(prompt)

    return jsonify({
        "situation": situation,
        "domain": domain.value,
        "stakes": stakes.value,
        "frameworks_applied": frameworks,
        "synthesis": synthesis,
        "ai_synthesis": ai_synthesis,
        "recommended_action": action,
        "confidence": confidence,
        "ai_enhanced": bool(ai_synthesis),
    })


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logger.info(f"Costanza v2.1 starting on port 5001 | {len(MODELS)} frameworks | LLM: {COSTANZA_MODEL}")
    # Prewarm LLM in background so it doesn't block startup
    threading.Thread(target=prewarm_model, daemon=True).start()
    app.run(host="0.0.0.0", port=5001, debug=False)
