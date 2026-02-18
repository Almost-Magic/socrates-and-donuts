"""
Elaine v4 — Wisdom & Philosophy Routes
Embedded knowledge base (sitcom quotes, one-liners, world idioms, philosophy)
with optional proxy to Wisdom Quotes API (:3350) for additional content.

Accessible to all AMTL apps via /api/wisdom/* endpoints.

Almost Magic Tech Lab
"""

import logging
import urllib.request
import urllib.parse
import json

from flask import Blueprint, jsonify, request
from modules.wisdom_kb import WisdomKB

logger = logging.getLogger("elaine.wisdom")

WISDOM_API = "http://localhost:3350"

bp = Blueprint("wisdom", __name__)

# Single shared knowledge base instance
_kb = WisdomKB()


@bp.route("/api/wisdom", methods=["GET"])
def daily_wisdom():
    """Get the quote of the day (same all day, changes at midnight).
    Also tries the external Wisdom API for variety — falls back to embedded KB."""
    # Try external API first for variety
    try:
        req = urllib.request.Request(f"{WISDOM_API}/api/quotes/random", method="GET")
        with urllib.request.urlopen(req, timeout=2) as resp:
            data = json.loads(resp.read().decode())
            data["via"] = "wisdom-api"
            return jsonify(data)
    except Exception:
        pass

    # Embedded KB — always works
    quote = _kb.daily()
    return jsonify({**quote, "via": "embedded-kb"})


@bp.route("/api/wisdom/random", methods=["GET"])
def random_wisdom():
    """Get a random quote, optionally filtered by category.
    ?category=sitcom|one-liner|idiom|philosophy"""
    category = request.args.get("category", None)
    quote = _kb.random(category)
    return jsonify({**quote, "via": "embedded-kb"})


@bp.route("/api/wisdom/search", methods=["GET"])
def wisdom_search():
    """Search quotes by keyword.
    ?q=keyword&limit=10"""
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "q parameter required"}), 400
    limit = request.args.get("limit", 10, type=int)
    results = _kb.search(query, limit)

    # Also try external API
    external = []
    try:
        encoded = urllib.parse.quote(query)
        req = urllib.request.Request(
            f"{WISDOM_API}/api/quotes/search?q={encoded}", method="GET"
        )
        with urllib.request.urlopen(req, timeout=2) as resp:
            data = json.loads(resp.read().decode())
            external = data.get("results", [])
    except Exception:
        pass

    return jsonify({
        "query": query,
        "results": results,
        "external_results": external,
        "total": len(results) + len(external),
    })


@bp.route("/api/wisdom/sitcom", methods=["GET"])
def sitcom_quotes():
    """Get sitcom quotes. ?source=Seinfeld|The Office|Parks and Rec"""
    source = request.args.get("source", "")
    if source:
        quotes = _kb.by_source(source)
    else:
        quotes = [q for q in _kb.all_quotes if q.get("category") == "sitcom"]
    return jsonify({"quotes": quotes, "count": len(quotes)})


@bp.route("/api/wisdom/idioms", methods=["GET"])
def world_idioms():
    """Get world culture idioms. ?culture=Japanese|Chinese|African|Australian"""
    culture = request.args.get("culture", "")
    if culture:
        quotes = _kb.by_culture(culture)
    else:
        quotes = [q for q in _kb.all_quotes if q.get("category") == "idiom"]
    return jsonify({"idioms": quotes, "count": len(quotes)})


@bp.route("/api/wisdom/one-liners", methods=["GET"])
def one_liners():
    """Get one-liners and famous quotes."""
    quotes = [q for q in _kb.all_quotes if q.get("category") == "one-liner"]
    return jsonify({"quotes": quotes, "count": len(quotes)})


@bp.route("/api/wisdom/philosophy", methods=["GET"])
def philosophy():
    """Get philosophy quotes."""
    quotes = [q for q in _kb.all_quotes if q.get("category") == "philosophy"]
    return jsonify({"quotes": quotes, "count": len(quotes)})


@bp.route("/api/wisdom/stats", methods=["GET"])
def wisdom_stats():
    """Get knowledge base statistics."""
    return jsonify(_kb.stats())


# Legacy endpoint compatibility
@bp.route("/api/philosophy-search", methods=["GET"])
def philosophy_search():
    """Search quotes by keyword via embedded KB + external API."""
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "q parameter required"}), 400

    results = _kb.search(query)

    # Also try external API
    try:
        encoded = urllib.parse.quote(query)
        req = urllib.request.Request(
            f"{WISDOM_API}/api/quotes/search?q={encoded}", method="GET"
        )
        with urllib.request.urlopen(req, timeout=2) as resp:
            data = json.loads(resp.read().decode())
            return jsonify({
                "results": results + data.get("results", []),
                "query": query,
                "sources": ["embedded-kb", "wisdom-api"],
            })
    except Exception:
        return jsonify({
            "results": results,
            "query": query,
            "sources": ["embedded-kb"],
        })
