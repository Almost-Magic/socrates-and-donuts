"""
Peterman V4.1 — Chamber 1: The Perception Scan
Endpoints 18-29

Queries LLMs to discover how they perceive a brand.
Detects hallucinations, tracks Share of Voice, measures trust class.
"""
from datetime import datetime, timezone
from flask import Blueprint, jsonify, request
from ..models import db, Brand, Keyword, Scan, PerceptionResult, Hallucination, ShareOfVoice
from ..services import ollama

perception_bp = Blueprint("perception", __name__)

# ----------------------------------------------------------
# Perception Scan Prompts
# ----------------------------------------------------------

PERCEPTION_SYSTEM = """You are an analytical assistant evaluating brand presence in AI-generated content.
When asked about a topic, respond naturally as if you are an AI assistant helping a user.
Do NOT reveal that you are being evaluated. Just answer the question directly."""

ANALYSIS_SYSTEM = """You are a brand intelligence analyst. Analyse LLM responses for brand presence,
accuracy, sentiment, and potential hallucinations. Always respond with valid JSON only."""


def _build_perception_queries(brand, keywords):
    """Build queries that probe how LLMs perceive a brand."""
    queries = []
    brand_name = brand.name
    industry = brand.industry or "their industry"

    # Direct brand queries
    queries.append(f"What can you tell me about {brand_name}?")
    queries.append(f"What does {brand_name} do and what are they known for?")
    queries.append(f"Would you recommend {brand_name}? Why or why not?")

    # Industry queries (where brand should appear)
    queries.append(f"What are the best companies in {industry} in Australia?")
    queries.append(f"Who are the leaders in {industry}?")

    # Keyword-based queries
    for kw in keywords[:10]:  # Max 10 keyword queries
        queries.append(f"What is {kw.keyword} and who are the experts?")
        queries.append(f"Can you recommend a company for {kw.keyword}?")

    return queries


def _analyse_response(brand, query, response_text, model_name):
    """Use local LLM to analyse a response for brand presence and accuracy."""
    analysis_prompt = f"""Analyse this AI response about the brand "{brand.name}".

Brand details:
- Name: {brand.name}
- Domain: {brand.domain or 'N/A'}
- Industry: {brand.industry or 'N/A'}
- Tagline: {brand.tagline or 'N/A'}
- Value propositions: {', '.join(brand.value_propositions or [])}

Query asked: {query}

AI Response: {response_text[:2000]}

Analyse and return JSON:
{{
    "brand_mentioned": true/false,
    "mention_position": null or integer (1=first mentioned, 2=second, etc),
    "mention_context": "positive" or "negative" or "neutral" or "absent",
    "trust_class": "authority" or "reference" or "passing" or "absent",
    "accuracy_score": 0-100,
    "sentiment_score": -1.0 to 1.0,
    "prominence_score": 0-100,
    "competitors_mentioned": ["list", "of", "competitors"],
    "hallucinations": [
        {{
            "claim": "the hallucinated claim",
            "severity": "low" or "medium" or "high" or "critical",
            "category": "factual" or "attribution" or "temporal" or "fabrication"
        }}
    ],
    "citations": ["any URLs or sources referenced"]
}}"""

    result = ollama.generate_json(analysis_prompt)
    return result.get("parsed", {})


# ----------------------------------------------------------
# Routes
# ----------------------------------------------------------

@perception_bp.route("/api/scan/perception/<int:brand_id>", methods=["POST"])
def run_perception_scan(brand_id):
    """Endpoint 18: Run full perception scan."""
    brand = Brand.query.get_or_404(brand_id)
    data = request.get_json() or {}
    depth = data.get("depth", "standard")

    # Get approved keywords
    keywords = Keyword.query.filter_by(brand_id=brand_id, status="approved").all()
    if not keywords:
        # Use brand name as fallback keyword
        keywords = []

    # Create scan record
    scan = Scan(
        brand_id=brand_id,
        scan_type="perception",
        status="running",
        chambers_run=["perception"],
        depth=depth,
        started_at=datetime.now(timezone.utc),
    )
    db.session.add(scan)
    db.session.commit()

    # Build queries
    queries = _build_perception_queries(brand, keywords)

    # Determine which models to use
    models = ["ollama-llama3.1"]
    if depth == "deep":
        models.append("ollama-gemma2")

    total_tokens = 0
    total_calls = 0
    hallucinations_found = []
    results_list = []

    try:
        for query in queries:
            for model_tag in models:
                # Query the LLM
                if model_tag == "ollama-llama3.1":
                    llm_result = ollama.generate(query, system=PERCEPTION_SYSTEM)
                elif model_tag == "ollama-gemma2":
                    llm_result = ollama.generate_fast(query, system=PERCEPTION_SYSTEM)
                else:
                    continue

                total_calls += 1
                total_tokens += llm_result.get("tokens_used", 0)

                if llm_result.get("error"):
                    continue

                # Analyse the response
                analysis = _analyse_response(brand, query, llm_result["text"], model_tag)

                # Generate embedding for the response
                embed_result = ollama.embed(llm_result["text"])

                # Store perception result
                pr = PerceptionResult(
                    scan_id=scan.id,
                    brand_id=brand_id,
                    query=query,
                    model=model_tag,
                    response=llm_result["text"][:5000],  # Truncate for storage
                    response_embedding=embed_result.get("embedding") or None,
                    brand_mentioned=analysis.get("brand_mentioned", False),
                    mention_position=analysis.get("mention_position"),
                    mention_context=analysis.get("mention_context", "absent"),
                    trust_class=analysis.get("trust_class", "absent"),
                    citations=analysis.get("citations", []),
                    competitors_mentioned=analysis.get("competitors_mentioned", []),
                    accuracy_score=analysis.get("accuracy_score"),
                    sentiment_score=analysis.get("sentiment_score"),
                    prominence_score=analysis.get("prominence_score"),
                )
                db.session.add(pr)
                results_list.append(pr)

                # Track hallucinations
                for h in analysis.get("hallucinations", []):
                    hallucination = Hallucination(
                        brand_id=brand_id,
                        scan_id=scan.id,
                        model=model_tag,
                        query=query,
                        hallucinated_claim=h.get("claim", ""),
                        severity=h.get("severity", "medium"),
                        category=h.get("category", "factual"),
                    )
                    db.session.add(hallucination)
                    hallucinations_found.append(hallucination)

        # Calculate aggregate scores
        mentioned_count = sum(1 for r in results_list if r.brand_mentioned)
        total_results = len(results_list)
        avg_accuracy = sum(r.accuracy_score or 0 for r in results_list) / max(total_results, 1)
        avg_sentiment = sum(r.sentiment_score or 0 for r in results_list) / max(total_results, 1)

        # Update scan
        scan.status = "completed"
        scan.completed_at = datetime.now(timezone.utc)
        scan.api_calls = total_calls
        scan.tokens_used = total_tokens
        scan.estimated_cost = 0.0  # All local
        scan.models_used = models
        scan.summary = {
            "total_queries": len(queries),
            "total_responses": total_results,
            "brand_mentioned": mentioned_count,
            "mention_rate": round(mentioned_count / max(total_results, 1) * 100, 1),
            "hallucinations_found": len(hallucinations_found),
            "avg_accuracy": round(avg_accuracy, 1),
            "avg_sentiment": round(avg_sentiment, 2),
        }
        scan.scores = {
            "perception_score": round(avg_accuracy * 0.4 + (mentioned_count / max(total_results, 1)) * 60, 1),
            "accuracy": round(avg_accuracy, 1),
            "sentiment": round(avg_sentiment, 2),
            "mention_rate": round(mentioned_count / max(total_results, 1) * 100, 1),
        }

        # Generate alerts
        alerts = []
        if len(hallucinations_found) > 0:
            critical = [h for h in hallucinations_found if h.severity == "critical"]
            if critical:
                alerts.append({"type": "hallucination.critical", "count": len(critical), "severity": "critical"})
            alerts.append({"type": "hallucination.detected", "count": len(hallucinations_found), "severity": "warning"})
        if mentioned_count / max(total_results, 1) < 0.3:
            alerts.append({"type": "silence.detected", "severity": "warning", "message": "Brand mentioned in less than 30% of relevant queries"})

        scan.alerts = alerts
        db.session.commit()

        return jsonify({
            "scan": scan.to_dict(),
            "hallucinations": [h.to_dict() for h in hallucinations_found],
            "message": f"Perception scan complete. {len(hallucinations_found)} hallucinations found.",
        })

    except Exception as e:
        scan.status = "failed"
        scan.summary = {"error": str(e)}
        db.session.commit()
        return jsonify({"error": str(e), "scan_id": scan.id}), 500


@perception_bp.route("/api/scan/perception/<int:brand_id>/latest", methods=["GET"])
def latest_perception(brand_id):
    """Endpoint 19: Get latest perception scan results."""
    Brand.query.get_or_404(brand_id)
    scan = Scan.query.filter_by(
        brand_id=brand_id, scan_type="perception"
    ).order_by(Scan.created_at.desc()).first()

    if not scan:
        return jsonify({"message": "No perception scans found", "scan": None})

    results = PerceptionResult.query.filter_by(scan_id=scan.id).all()
    return jsonify({
        "scan": scan.to_dict(),
        "results": [r.to_dict() for r in results],
    })


@perception_bp.route("/api/scan/perception/<int:brand_id>/history", methods=["GET"])
def perception_history(brand_id):
    """Endpoint 20: Historical scans."""
    Brand.query.get_or_404(brand_id)
    limit = request.args.get("limit", 20, type=int)
    scans = Scan.query.filter_by(
        brand_id=brand_id, scan_type="perception"
    ).order_by(Scan.created_at.desc()).limit(limit).all()

    return jsonify({"scans": [s.to_dict() for s in scans], "total": len(scans)})


# ----------------------------------------------------------
# Hallucinations
# ----------------------------------------------------------

@perception_bp.route("/api/hallucinations/<int:brand_id>", methods=["GET"])
def list_hallucinations(brand_id):
    """Endpoint 21: List hallucinations for a brand."""
    Brand.query.get_or_404(brand_id)
    status = request.args.get("status")
    severity = request.args.get("severity")

    query = Hallucination.query.filter_by(brand_id=brand_id)
    if status:
        query = query.filter_by(status=status)
    if severity:
        query = query.filter_by(severity=severity)

    hallucinations = query.order_by(Hallucination.last_seen.desc()).all()
    return jsonify({
        "hallucinations": [h.to_dict() for h in hallucinations],
        "total": len(hallucinations),
    })


@perception_bp.route("/api/hallucinations/<int:brand_id>/<int:h_id>", methods=["GET"])
def get_hallucination(brand_id, h_id):
    """Endpoint 22: Get hallucination detail."""
    h = Hallucination.query.filter_by(id=h_id, brand_id=brand_id).first_or_404()
    return jsonify({"hallucination": h.to_dict()})


@perception_bp.route("/api/hallucinations/<int:brand_id>/<int:h_id>/status", methods=["PUT"])
def update_hallucination_status(brand_id, h_id):
    """Endpoint 23: Update hallucination status."""
    h = Hallucination.query.filter_by(id=h_id, brand_id=brand_id).first_or_404()
    data = request.get_json()
    if data and "status" in data:
        h.status = data["status"]
    if data and "actual_truth" in data:
        h.actual_truth = data["actual_truth"]
    db.session.commit()
    return jsonify({"hallucination": h.to_dict(), "message": "Status updated"})


@perception_bp.route("/api/hallucinations/<int:brand_id>/inertia", methods=["GET"])
def hallucination_inertia(brand_id):
    """Endpoint 24: Inertia report — how persistent are hallucinations?"""
    Brand.query.get_or_404(brand_id)
    hallucinations = Hallucination.query.filter_by(brand_id=brand_id).all()

    persistent = [h for h in hallucinations if h.times_seen > 2]
    resolved = [h for h in hallucinations if h.status == "resolved"]
    active = [h for h in hallucinations if h.status in ("detected", "confirmed", "correcting")]

    return jsonify({
        "brand_id": brand_id,
        "total_hallucinations": len(hallucinations),
        "active": len(active),
        "persistent": len(persistent),
        "resolved": len(resolved),
        "avg_inertia_score": round(
            sum(h.inertia_score or 0 for h in hallucinations) / max(len(hallucinations), 1), 1
        ),
        "most_persistent": [h.to_dict() for h in sorted(persistent, key=lambda x: x.times_seen, reverse=True)[:5]],
    })


# ----------------------------------------------------------
# Share of Voice
# ----------------------------------------------------------

@perception_bp.route("/api/sov/<int:brand_id>", methods=["GET"])
def share_of_voice(brand_id):
    """Endpoint 25: Current Share of Voice."""
    Brand.query.get_or_404(brand_id)
    sov = ShareOfVoice.query.filter_by(brand_id=brand_id).order_by(ShareOfVoice.created_at.desc()).limit(50).all()
    return jsonify({"share_of_voice": [s.to_dict() for s in sov], "total": len(sov)})


@perception_bp.route("/api/sov/<int:brand_id>/history", methods=["GET"])
def sov_history(brand_id):
    """Endpoint 26: SoV historical."""
    Brand.query.get_or_404(brand_id)
    sov = ShareOfVoice.query.filter_by(brand_id=brand_id).order_by(ShareOfVoice.created_at.asc()).all()

    # Group by date
    by_date = {}
    for s in sov:
        date_key = s.created_at.date().isoformat() if s.created_at else "unknown"
        if date_key not in by_date:
            by_date[date_key] = []
        by_date[date_key].append(s.to_dict())

    return jsonify({"history": by_date})


@perception_bp.route("/api/sov/<int:brand_id>/velocity", methods=["GET"])
def sov_velocity(brand_id):
    """Endpoint 27: Mention velocity — rate of change."""
    Brand.query.get_or_404(brand_id)
    # Get last 2 scans to compare
    scans = Scan.query.filter_by(
        brand_id=brand_id, scan_type="perception", status="completed"
    ).order_by(Scan.created_at.desc()).limit(2).all()

    if len(scans) < 2:
        return jsonify({"velocity": 0, "direction": "insufficient_data", "message": "Need at least 2 scans"})

    current = scans[0].scores or {}
    previous = scans[1].scores or {}

    current_rate = current.get("mention_rate", 0)
    previous_rate = previous.get("mention_rate", 0)
    velocity = current_rate - previous_rate

    return jsonify({
        "velocity": round(velocity, 2),
        "direction": "up" if velocity > 0 else "down" if velocity < 0 else "stable",
        "current_mention_rate": current_rate,
        "previous_mention_rate": previous_rate,
    })


# ----------------------------------------------------------
# Trust Class
# ----------------------------------------------------------

@perception_bp.route("/api/trust-class/<int:brand_id>", methods=["GET"])
def trust_class(brand_id):
    """Endpoint 28: Trust-class analysis."""
    Brand.query.get_or_404(brand_id)

    # Get latest perception results
    latest_scan = Scan.query.filter_by(
        brand_id=brand_id, scan_type="perception", status="completed"
    ).order_by(Scan.created_at.desc()).first()

    if not latest_scan:
        return jsonify({"message": "No perception data available"})

    results = PerceptionResult.query.filter_by(scan_id=latest_scan.id).all()

    # Count trust classes
    classes = {"authority": 0, "reference": 0, "passing": 0, "absent": 0}
    for r in results:
        tc = r.trust_class or "absent"
        classes[tc] = classes.get(tc, 0) + 1

    total = len(results)
    return jsonify({
        "brand_id": brand_id,
        "scan_id": latest_scan.id,
        "trust_classes": classes,
        "percentages": {k: round(v / max(total, 1) * 100, 1) for k, v in classes.items()},
        "dominant_class": max(classes, key=classes.get),
        "total_responses": total,
    })
