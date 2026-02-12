"""
Costanza — Mental Models Engine API
Port: 5001
Almost Magic Tech Lab

Flask wrapper around the Costanza thinking/communication/strategic engines.
"""

import sys
import os
import logging
from datetime import datetime, timezone
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

# Initialise engines
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


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": "costanza",
        "version": "2.0.0",
        "engines": {
            "thinking": thinking.status(),
            "communication": communication.status(),
            "strategic": strategic.status(),
        },
        "total_models": len(MODELS),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "app": "Costanza",
        "tagline": "Mental Models Engine - 166 models across 3 engines",
        "version": "2.0.0",
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

    result = thinking.analyse(situation, domain=domain, stakes=stakes)

    # result.results is a dict: FrameworkType → result object
    # result.frameworks_applied is a list of FrameworkType enums
    frameworks = [ft.value for ft in getattr(result, "frameworks_applied", [])]
    synthesis = getattr(result, "synthesis", "")
    action = getattr(result, "recommended_action", "")

    return jsonify({
        "situation": situation,
        "domain": domain.value,
        "stakes": stakes.value,
        "frameworks_applied": frameworks,
        "synthesis": synthesis,
        "recommended_action": action,
        "confidence": getattr(result, "confidence", 0),
    })


if __name__ == "__main__":
    logger.info(f"Costanza v2.0 starting on port 5001 | {len(MODELS)} models")
    app.run(host="0.0.0.0", port=5001, debug=False)
