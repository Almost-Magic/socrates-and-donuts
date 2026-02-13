"""
Peterman V4.1 — SEO Ask + ELAINE Briefing Routes
Almost Magic Tech Lab

/api/seo/ask — Mani types what he wants, gets SEO output
/api/elaine-briefing — ELAINE calls for morning briefing data
"""
from datetime import datetime, timezone, timedelta
from flask import Blueprint, jsonify, request
from sqlalchemy import func
from ..services import ollama, searxng
from ..models import db, Brand, Scan, Hallucination, AuthorityResult, ContentBrief, TrendSignal

seo_ask_bp = Blueprint("seo_ask", __name__)


# ── SEO Ask ──────────────────────────────────────────────
@seo_ask_bp.route("/api/seo/ask", methods=["GET", "POST"])
def seo_ask():
    """
    Simple SEO interface: Mani types what he wants, gets SEO output.
    Combines keyword research, content analysis, meta tags, and scoring.
    """
    if request.method == "GET":
        return jsonify({
            "endpoint": "/api/seo/ask",
            "method": "POST",
            "description": "Type what you want — keyword research, content analysis, meta tags, SEO scoring",
            "body": {"query": "string (required)", "brand_id": "integer (optional)"},
            "example": {"query": "Analyse keywords for AI consulting Sydney", "brand_id": 1},
        })

    data = request.get_json(force=True, silent=True) or {}
    query = data.get("query", "").strip()
    brand_id = data.get("brand_id")

    if not query:
        return jsonify({"error": "Please provide a query"}), 400

    # Get brand context if provided
    brand_context = ""
    brand = None
    if brand_id:
        brand = db.session.get(Brand, brand_id)
        if brand:
            brand_context = f"Brand: {brand.name}. Domain: {brand.domain or 'N/A'}. Industry: {brand.industry or 'N/A'}."

    # Step 1: Keyword research via SearXNG
    serp_results = searxng.search_web(query, max_results=10)

    # Step 2: Build a comprehensive SEO prompt
    serp_context = ""
    if serp_results.get("results"):
        serp_context = "\n".join([
            f"- {r['title']} ({r['url']}): {r['content'][:120]}"
            for r in serp_results["results"][:8]
        ])

    system_prompt = (
        "You are Peterman, an expert SEO and brand intelligence analyst for Almost Magic Tech Lab. "
        "Provide actionable SEO output in structured JSON. Be specific and practical. "
        "All recommendations should be for the Australian market unless stated otherwise."
    )

    analysis_prompt = f"""Analyse this SEO request and provide comprehensive output.

Request: {query}
{f'Context: {brand_context}' if brand_context else ''}

Current SERP landscape for related terms:
{serp_context or 'No SERP data available'}

Respond with JSON containing:
{{
  "summary": "2-3 sentence overview of findings",
  "keywords": {{
    "primary": ["top 3-5 target keywords"],
    "long_tail": ["5-8 long-tail variations"],
    "questions": ["3-5 question-format keywords people search"]
  }},
  "content_analysis": {{
    "content_gaps": ["2-3 content gaps identified from SERP"],
    "competitor_themes": ["top themes competitors cover"],
    "recommended_topics": ["3-5 content pieces to create"]
  }},
  "meta_tags": {{
    "title": "recommended page title (50-60 chars)",
    "description": "recommended meta description (150-160 chars)",
    "h1": "recommended H1 heading",
    "og_title": "Open Graph title",
    "og_description": "Open Graph description"
  }},
  "content_score": {{
    "opportunity_score": 0-100,
    "competition_level": "low|medium|high",
    "estimated_difficulty": "easy|moderate|hard",
    "recommendation": "1-2 sentence action recommendation"
  }},
  "action_items": ["3-5 specific next steps"]
}}"""

    result = ollama.generate_json(analysis_prompt, system=system_prompt)

    if result.get("error"):
        # Return a useful response even if LLM is down
        return jsonify({
            "query": query,
            "serp_results": serp_results.get("results", [])[:5],
            "llm_status": "unavailable",
            "message": "LLM unavailable — showing raw SERP data. Start Supervisor/Ollama for AI analysis.",
            "keywords": {
                "from_serp": list(set(
                    word.lower()
                    for r in serp_results.get("results", [])
                    for word in (r.get("title", "") + " " + r.get("content", "")).split()
                    if len(word) > 4 and word.isalpha()
                )[:15])
            },
        })

    return jsonify({
        "query": query,
        "brand": brand.name if brand else None,
        "analysis": result.get("parsed", {}),
        "serp_results": serp_results.get("results", [])[:5],
        "model": result.get("model", ""),
        "tokens_used": result.get("tokens_used", 0),
        "cost": 0.0,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


# ── ELAINE Briefing ──────────────────────────────────────
@seo_ask_bp.route("/api/elaine-briefing", methods=["GET"])
def elaine_briefing():
    """
    Returns a summary for ELAINE's morning briefing.
    Brand health, recent scans, hallucinations, authority gaps, trend signals.
    """
    try:
        # Active brands — use db.session.query to avoid column name conflict
        brands = db.session.query(Brand).filter(Brand.is_active == True).all()
        brand_summaries = []
        total_hallucinations = 0
        total_authority_gaps = 0

        for brand in brands:
            # Recent scans
            recent_scan = (
                db.session.query(Scan)
                .filter(Scan.brand_id == brand.id)
                .order_by(Scan.created_at.desc())
                .first()
            )

            # Active hallucinations
            hallucination_count = (
                db.session.query(func.count(Hallucination.id))
                .filter(Hallucination.brand_id == brand.id, Hallucination.status == "active")
                .scalar()
            )
            total_hallucinations += hallucination_count

            # Authority gaps (keywords not in top 10)
            authority_gaps = (
                db.session.query(func.count(AuthorityResult.id))
                .filter(AuthorityResult.brand_id == brand.id, AuthorityResult.in_top_10 == False)
                .scalar()
            )
            total_authority_gaps += authority_gaps

            # Pending content briefs
            pending_briefs = (
                db.session.query(func.count(ContentBrief.id))
                .filter(ContentBrief.brand_id == brand.id, ContentBrief.status == "draft")
                .scalar()
            )

            brand_summaries.append({
                "id": brand.id,
                "name": brand.name,
                "domain": brand.domain,
                "industry": brand.industry,
                "tier": brand.tier,
                "is_client_zero": brand.is_client_zero,
                "last_scan": recent_scan.created_at.isoformat() if recent_scan else None,
                "last_scan_status": recent_scan.status if recent_scan else None,
                "active_hallucinations": hallucination_count,
                "authority_gaps": authority_gaps,
                "pending_briefs": pending_briefs,
            })

        # Recent trend signals (last 7 days)
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        urgent_signals = (
            db.session.query(func.count(TrendSignal.id))
            .filter(TrendSignal.urgency.in_(["critical", "high"]))
            .filter(TrendSignal.created_at >= week_ago)
            .scalar()
        )

        # System health
        ollama_health = ollama.health_check()
        searxng_health = searxng.health_check()

        return jsonify({
            "service": "peterman",
            "briefing_time": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "active_brands": len(brands),
                "total_hallucinations": total_hallucinations,
                "total_authority_gaps": total_authority_gaps,
                "urgent_trend_signals": urgent_signals,
            },
            "brands": brand_summaries,
            "system": {
                "ollama": ollama_health.get("status", "unknown"),
                "searxng": searxng_health.get("status", "unknown"),
                "models_available": ollama_health.get("models_available", []),
            },
            "recommendations": _generate_recommendations(brand_summaries, total_hallucinations, total_authority_gaps, urgent_signals),
        })
    except Exception as e:
        return jsonify({
            "service": "peterman",
            "briefing_time": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "summary": {"active_brands": 0},
            "brands": [],
            "system": {"status": "error"},
            "recommendations": ["Check database connection"],
        })


def _generate_recommendations(brands, hallucinations, gaps, signals):
    """Generate actionable recommendations for the briefing."""
    recs = []

    if not brands:
        recs.append("No active brands configured. Add your first brand to start monitoring.")
        return recs

    # Check for stale scans
    for b in brands:
        if not b.get("last_scan"):
            recs.append(f"Brand '{b['name']}' has never been scanned. Run a perception scan.")

    if hallucinations > 0:
        recs.append(f"{hallucinations} active hallucination(s) detected. Review and submit corrections via The Forge.")

    if gaps > 0:
        recs.append(f"{gaps} keyword(s) not ranking in top 10. Run authority scans to track progress.")

    if signals > 0:
        recs.append(f"{signals} urgent trend signal(s) in the last 7 days. Check The Oracle for details.")

    client_zero = [b for b in brands if b.get("is_client_zero")]
    if client_zero:
        for cz in client_zero:
            if cz.get("active_hallucinations", 0) > 0:
                recs.append(f"Client Zero '{cz['name']}' has {cz['active_hallucinations']} hallucination(s) — priority fix.")

    if not recs:
        recs.append("All systems nominal. No urgent actions required.")

    return recs
