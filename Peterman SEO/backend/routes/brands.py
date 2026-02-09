"""
Peterman V4.1 — Brand Profile Routes
Endpoints 7-17
"""
from flask import Blueprint, jsonify, request
from ..models import db, Brand, Keyword, Competitor

brands_bp = Blueprint("brands", __name__)


# ----------------------------------------------------------
# Brand CRUD
# ----------------------------------------------------------

@brands_bp.route("/api/brands", methods=["GET"])
def list_brands():
    """Endpoint 7: List all brands."""
    brands = Brand.query.filter_by(is_active=True).all()
    return jsonify({"brands": [b.to_dict() for b in brands], "total": len(brands)})


@brands_bp.route("/api/brands", methods=["POST"])
def create_brand():
    """Endpoint 8: Create brand profile."""
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "Brand name is required"}), 400

    brand = Brand(
        name=data["name"],
        domain=data.get("domain"),
        industry=data.get("industry"),
        description=data.get("description"),
        tier=data.get("tier", "growth"),
        tagline=data.get("tagline"),
        value_propositions=data.get("value_propositions", []),
        target_audience=data.get("target_audience", []),
        differentiators=data.get("differentiators", []),
        is_client_zero=data.get("is_client_zero", False),
        scan_frequency=data.get("scan_frequency", "weekly"),
    )
    db.session.add(brand)
    db.session.commit()

    return jsonify({"brand": brand.to_dict(), "message": "Brand created"}), 201


@brands_bp.route("/api/brands/<int:brand_id>", methods=["GET"])
def get_brand(brand_id):
    """Endpoint 9: Get brand profile."""
    brand = Brand.query.get_or_404(brand_id)
    return jsonify({"brand": brand.to_dict()})


@brands_bp.route("/api/brands/<int:brand_id>", methods=["PUT"])
def update_brand(brand_id):
    """Endpoint 10: Update brand profile."""
    brand = Brand.query.get_or_404(brand_id)
    data = request.get_json()

    for field in ["name", "domain", "industry", "description", "tier", "tagline",
                  "value_propositions", "target_audience", "differentiators",
                  "scan_frequency", "llm_models", "notification_channels"]:
        if field in data:
            setattr(brand, field, data[field])

    db.session.commit()
    return jsonify({"brand": brand.to_dict(), "message": "Brand updated"})


@brands_bp.route("/api/brands/<int:brand_id>", methods=["DELETE"])
def archive_brand(brand_id):
    """Endpoint 11: Archive brand (soft delete)."""
    brand = Brand.query.get_or_404(brand_id)
    brand.is_active = False
    db.session.commit()
    return jsonify({"message": f"Brand '{brand.name}' archived"})


# ----------------------------------------------------------
# Competitors
# ----------------------------------------------------------

@brands_bp.route("/api/brands/<int:brand_id>/competitors", methods=["POST"])
def add_competitor(brand_id):
    """Endpoint 12: Add competitor."""
    Brand.query.get_or_404(brand_id)
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "Competitor name is required"}), 400

    competitor = Competitor(
        brand_id=brand_id,
        name=data["name"],
        domain=data.get("domain"),
        relationship=data.get("relationship", "direct"),
        notes=data.get("notes"),
    )
    db.session.add(competitor)
    db.session.commit()

    return jsonify({"competitor": competitor.to_dict(), "message": "Competitor added"}), 201


@brands_bp.route("/api/brands/<int:brand_id>/competitors", methods=["GET"])
def list_competitors(brand_id):
    """Endpoint 13: List competitors."""
    Brand.query.get_or_404(brand_id)
    competitors = Competitor.query.filter_by(brand_id=brand_id).all()
    return jsonify({"competitors": [c.to_dict() for c in competitors], "total": len(competitors)})


# ----------------------------------------------------------
# Keywords
# ----------------------------------------------------------

@brands_bp.route("/api/brands/<int:brand_id>/keywords", methods=["POST"])
def add_keywords(brand_id):
    """Endpoint 14: Add keywords."""
    Brand.query.get_or_404(brand_id)
    data = request.get_json()

    if not data:
        return jsonify({"error": "Keyword data required"}), 400

    # Accept single keyword or list
    keywords_data = data.get("keywords", [data]) if "keywords" in data else [data]
    added = []

    for kw in keywords_data:
        if not kw.get("keyword"):
            continue
        keyword = Keyword(
            brand_id=brand_id,
            keyword=kw["keyword"],
            category=kw.get("category", "primary"),
            status=kw.get("status", "pending"),
            search_volume=kw.get("search_volume"),
            difficulty=kw.get("difficulty"),
        )
        db.session.add(keyword)
        added.append(keyword)

    db.session.commit()
    return jsonify({
        "keywords": [k.to_dict() for k in added],
        "total_added": len(added),
        "message": f"{len(added)} keywords added"
    }), 201


@brands_bp.route("/api/brands/<int:brand_id>/keywords", methods=["GET"])
def list_keywords(brand_id):
    """Endpoint 15: List keywords."""
    Brand.query.get_or_404(brand_id)
    status = request.args.get("status")
    query = Keyword.query.filter_by(brand_id=brand_id)
    if status:
        query = query.filter_by(status=status)
    keywords = query.all()
    return jsonify({"keywords": [k.to_dict() for k in keywords], "total": len(keywords)})


@brands_bp.route("/api/brands/<int:brand_id>/keywords/<int:kid>/approve", methods=["PUT"])
def approve_keyword(brand_id, kid):
    """Endpoint 16: Approve keyword."""
    keyword = Keyword.query.filter_by(id=kid, brand_id=brand_id).first_or_404()
    keyword.status = "approved"
    db.session.commit()
    return jsonify({"keyword": keyword.to_dict(), "message": "Keyword approved"})


@brands_bp.route("/api/brands/<int:brand_id>/dashboard", methods=["GET"])
def brand_dashboard(brand_id):
    """Endpoint 17: Full brand dashboard."""
    brand = Brand.query.get_or_404(brand_id)
    from ..models import Scan, Hallucination

    recent_scans = Scan.query.filter_by(brand_id=brand_id).order_by(Scan.created_at.desc()).limit(5).all()
    active_hallucinations = Hallucination.query.filter_by(brand_id=brand_id).filter(
        Hallucination.status.in_(["detected", "confirmed", "correcting"])
    ).count()
    total_keywords = Keyword.query.filter_by(brand_id=brand_id, status="approved").count()
    total_competitors = Competitor.query.filter_by(brand_id=brand_id).count()

    return jsonify({
        "brand": brand.to_dict(),
        "stats": {
            "approved_keywords": total_keywords,
            "competitors": total_competitors,
            "active_hallucinations": active_hallucinations,
            "recent_scans": len(recent_scans),
        },
        "recent_scans": [s.to_dict() for s in recent_scans],
    })
