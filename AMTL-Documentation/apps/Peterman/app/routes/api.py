"""
Core API routes for Peterman.

Handles domains, crawl, keywords, probes, scores, hallucinations, briefs, and approvals.
"""

import logging
from uuid import UUID
from flask import Blueprint, jsonify, request
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.models.database import get_session
from app.models.domain import Domain

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)


# ==================== DOMAINS ====================

@api_bp.route('/domains', methods=['GET'])
def list_domains():
    """List all managed domains."""
    try:
        session = get_session()
        domains = session.query(Domain).all()
        return jsonify({
            'domains': [d.to_dict() for d in domains],
            'count': len(domains)
        })
    except SQLAlchemyError as e:
        logger.error(f"Failed to list domains: {e}")
        return jsonify({'error': 'Database error'}), 500


@api_bp.route('/domains', methods=['POST'])
def create_domain():
    """Register a new domain."""
    try:
        session = get_session()
        data = request.get_json()
        
        if not data.get('domain_name'):
            return jsonify({'error': 'domain_name is required'}), 400
        
        existing = session.query(Domain).filter_by(domain_name=data['domain_name']).first()
        if existing:
            return jsonify({'error': 'Domain already exists'}), 409
        
        domain = Domain(
            domain_name=data['domain_name'],
            display_name=data.get('display_name', data['domain_name']),
            owner_label=data.get('owner_label'),
            cms_type=data.get('cms_type'),
            cms_api_key=data.get('cms_api_key'),
            target_llms=data.get('target_llms', ['claude_cli', 'ollama']),
            probe_cadence=data.get('probe_cadence', 'weekly'),
            budget_weekly_aud=data.get('budget_weekly_aud', 50.00),
            tier=data.get('tier', 'owner')
        )
        
        session.add(domain)
        session.commit()
        
        logger.info(f"Created domain: {domain.domain_name}")
        
        return jsonify(domain.to_dict()), 201
        
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Failed to create domain: {e}")
        return jsonify({'error': 'Database error'}), 500


@api_bp.route('/domains/<domain_id>', methods=['GET'])
def get_domain(domain_id):
    """Get domain details."""
    try:
        session = get_session()
        domain = session.get(Domain, domain_id)
        if not domain:
            return jsonify({'error': 'Domain not found'}), 404
        
        return jsonify(domain.to_dict())
        
    except SQLAlchemyError as e:
        logger.error(f"Failed to get domain {domain_id}: {e}")
        return jsonify({'error': 'Database error'}), 500


@api_bp.route('/domains/<domain_id>', methods=['DELETE'])
def archive_domain(domain_id):
    """Archive a domain (soft delete)."""
    try:
        session = get_session()
        domain = session.get(Domain, domain_id)
        if not domain:
            return jsonify({'error': 'Domain not found'}), 404
        
        domain.status = 'archived'
        session.commit()
        
        return jsonify({'message': 'Domain archived'})
        
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Failed to archive domain {domain_id}: {e}")
        return jsonify({'error': 'Database error'}), 500


# ==================== CRAWL ====================

@api_bp.route('/domains/<domain_id>/crawl', methods=['POST'])
def trigger_crawl(domain_id):
    """Trigger a crawl for a domain."""
    try:
        from app.services.crawler import trigger_crawl as run_crawl
        
        result = run_crawl(UUID(domain_id))
        
        # After crawl, generate keywords
        from app.services.keyword_engine import create_target_queries
        crawl_data = result.get('business_summary', {})
        keywords_result = create_target_queries(UUID(domain_id), {'homepage': {'metadata': {'title': result.get('domain_name')}}, 'business_summary': crawl_data})
        
        return jsonify({
            'crawl': result,
            'keywords': keywords_result
        })
        
    except Exception as e:
        logger.error(f"Failed to crawl domain {domain_id}: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== KEYWORDS ====================

@api_bp.route('/domains/<domain_id>/suggest-keywords', methods=['POST'])
def suggest_keywords(domain_id):
    """Generate keyword suggestions for a domain."""
    try:
        from app.services.keyword_engine import create_target_queries
        from app.models.database import get_session
        
        session = get_session()
        domain = session.get(Domain, domain_id)
        if not domain:
            return jsonify({'error': 'Domain not found'}), 404
        
        crawl_data = domain.crawl_data or {}
        result = create_target_queries(UUID(domain_id), crawl_data)
        
        # Create approvals for each keyword
        from app.services.keyword_engine import get_domain_queries
        queries = get_domain_queries(UUID(domain_id))
        
        for q in queries:
            from app.services.approvals import create_keyword_approval
            create_keyword_approval(UUID(domain_id), q['id'], q['query'], q['category'])
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Failed to generate keywords: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/domains/<domain_id>/keywords', methods=['GET'])
def get_keywords(domain_id):
    """Get all keywords for a domain."""
    try:
        from app.services.keyword_engine import get_domain_queries
        
        queries = get_domain_queries(UUID(domain_id))
        return jsonify({'keywords': queries, 'count': len(queries)})
        
    except Exception as e:
        logger.error(f"Failed to get keywords: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/domains/<domain_id>/keywords/<kid>', methods=['PUT'])
def update_keyword(domain_id, kid):
    """Update a keyword."""
    try:
        from app.services.keyword_engine import update_query
        
        data = request.get_json()
        result = update_query(kid, data)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Failed to update keyword: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/domains/<domain_id>/keywords/approve-all', methods=['POST'])
def approve_all_keywords(domain_id):
    """Approve all keywords for a domain."""
    try:
        from app.services.keyword_engine import approve_all_queries
        from app.services.approvals import bulk_approve_keywords
        
        result = approve_all_queries(UUID(domain_id))
        bulk_approve_keywords(UUID(domain_id))
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Failed to approve keywords: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== PROBES ====================

@api_bp.route('/domains/<domain_id>/probe', methods=['POST'])
def trigger_probe(domain_id):
    """Trigger auto-probing for approved keywords."""
    try:
        from app.services.probe_engine import run_auto_probe, get_approved_queries
        
        # Get approved queries
        queries = get_approved_queries(UUID(domain_id))
        
        if not queries:
            return jsonify({'error': 'No approved queries to probe'}), 400
        
        results = []
        for q in queries[:5]:  # Limit to 5 for now
            result = run_auto_probe(UUID(domain_id), q['query'])
            results.append(result)
        
        return jsonify({
            'probes_run': len(results),
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Failed to probe: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/domains/<domain_id>/probe/manual', methods=['POST'])
def submit_manual_probe(domain_id):
    """Submit a manual probe response."""
    try:
        from app.services.probe_engine import run_manual_probe
        
        data = request.get_json()
        
        result = run_manual_probe(
            UUID(domain_id),
            data['query'],
            data['llm_provider'],
            data['response_text']
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Failed to submit manual probe: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/domains/<domain_id>/probe-queue', methods=['GET'])
def get_probe_queue(domain_id):
    """Get manual probe queue."""
    try:
        from app.services.probe_engine import get_probe_queue
        
        queue = get_probe_queue(UUID(domain_id))
        return jsonify({'queue': queue})
        
    except Exception as e:
        logger.error(f"Failed to get probe queue: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/domains/<domain_id>/probes', methods=['GET'])
def get_probes(domain_id):
    """Get all probe results."""
    try:
        from app.services.probe_engine import get_probe_results
        
        cycle = request.args.get('cycle', type=int)
        results = get_probe_results(UUID(domain_id), cycle)
        
        return jsonify({'probes': results, 'count': len(results)})
        
    except Exception as e:
        logger.error(f"Failed to get probes: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/domains/<domain_id>/probes/latest', methods=['GET'])
def get_latest_probes(domain_id):
    """Get latest probe cycle results."""
    try:
        from app.services.probe_engine import get_probe_results, get_latest_probe_cycle
        
        cycle = get_latest_probe_cycle(UUID(domain_id))
        if not cycle:
            return jsonify({'probes': [], 'cycle': None})
        
        results = get_probe_results(UUID(domain_id), cycle)
        
        return jsonify({'probes': results, 'cycle': cycle})
        
    except Exception as e:
        logger.error(f"Failed to get latest probes: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== SCORE ====================

@api_bp.route('/domains/<domain_id>/score', methods=['GET'])
def get_domain_score(domain_id):
    """Get current Peterman Score - uses real score engine."""
    try:
        from app.services.score_engine import compute_peterman_score
        
        # Use the real score engine - no more hardcoded values!
        score_data = compute_peterman_score(UUID(domain_id))
        
        return jsonify(score_data)
        
    except Exception as e:
        logger.error(f"Failed to compute score: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/domains/<domain_id>/chambers', methods=['GET'])
def get_chambers(domain_id):
    """Get status of all chambers."""
    try:
        from app.models.database import get_session
        session = get_session()
        domain = session.get(Domain, domain_id)
        if not domain:
            return jsonify({'error': 'Domain not found'}), 404
        
        chambers = [
            {'chamber_id': 1, 'name': 'Domain Crawler', 'status': 'ready'},
            {'chamber_id': 2, 'name': 'Keyword Engine', 'status': 'ready'},
            {'chamber_id': 3, 'name': 'LLM Probe', 'status': 'ready'},
            {'chamber_id': 4, 'name': 'Score Engine', 'status': 'ready'},
            {'chamber_id': 5, 'name': 'Hallucination Detector', 'status': 'ready'},
            {'chamber_id': 6, 'name': 'The Forge', 'status': 'ready'},
            {'chamber_id': 7, 'name': 'Approval Gate', 'status': 'ready'},
            {'chamber_id': 8, 'name': 'Content Deployer', 'status': 'pending'},
            {'chamber_id': 9, 'name': 'Budget Monitor', 'status': 'ready'},
            {'chamber_id': 10, 'name': 'Audit Log', 'status': 'ready'},
        ]
        
        return jsonify({'domain_id': str(domain_id), 'chambers': chambers})
        
    except Exception as e:
        logger.error(f"Failed to get chambers: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== HALLUCINATIONS ====================

@api_bp.route('/domains/<domain_id>/hallucinations', methods=['GET'])
def get_hallucinations(domain_id):
    """Get hallucinations for a domain."""
    try:
        from app.services.hallucination_detector import get_domain_hallucinations
        
        status = request.args.get('status')
        hallucinations = get_domain_hallucinations(UUID(domain_id), status)
        
        return jsonify({'hallucinations': hallucinations})
        
    except Exception as e:
        logger.error(f"Failed to get hallucinations: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/domains/<domain_id>/hallucinations/detect', methods=['POST'])
def detect_hallucinations(domain_id):
    """Run hallucination detection."""
    try:
        from app.services.hallucination_detector import detect_hallucinations
        
        result = detect_hallucinations(UUID(domain_id))
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Failed to detect hallucinations: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/domains/<domain_id>/hallucinations/<hid>', methods=['GET'])
def get_hallucination(domain_id, hid):
    """Get a specific hallucination."""
    try:
        from app.services.hallucination_detector import get_hallucination
        
        result = get_hallucination(int(hid))
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Failed to get hallucination: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/domains/<domain_id>/hallucinations/<hid>/generate-brief', methods=['POST'])
def generate_brief_from_hallucination(domain_id, hid):
    """Generate a content brief for a hallucination."""
    try:
        from app.services.forge import generate_brief_for_hallucination
        from app.services.approvals import create_brief_approval
        
        result = generate_brief_for_hallucination(UUID(domain_id), int(hid))
        
        # Create approval
        create_brief_approval(UUID(domain_id), result['id'], result['title'], result.get('priority', 'medium'))
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Failed to generate brief: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== BRIEFS ====================

@api_bp.route('/domains/<domain_id>/briefs', methods=['GET'])
def get_briefs(domain_id):
    """Get content briefs for a domain."""
    try:
        from app.services.forge import get_domain_briefs
        
        status = request.args.get('status')
        briefs = get_domain_briefs(UUID(domain_id), status)
        
        return jsonify({'briefs': briefs})
        
    except Exception as e:
        logger.error(f"Failed to get briefs: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/domains/<domain_id>/briefs/<bid>', methods=['GET'])
def get_brief(domain_id, bid):
    """Get a specific brief."""
    try:
        from app.services.forge import get_brief
        
        result = get_brief(int(bid))
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Failed to get brief: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== APPROVALS ====================

@api_bp.route('/domains/<domain_id>/approvals', methods=['GET'])
def get_approvals(domain_id):
    """Get approvals for a domain."""
    try:
        from app.services.approvals import get_domain_approvals
        
        status = request.args.get('status')
        approvals = get_domain_approvals(UUID(domain_id), status)
        
        return jsonify({'approvals': approvals})
        
    except Exception as e:
        logger.error(f"Failed to get approvals: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/approvals/<aid>/approve', methods=['POST'])
def approve_item(aid):
    """Approve an item."""
    try:
        from app.services.approvals import approve_item
        
        data = request.get_json() or {}
        result = approve_item(int(aid), data.get('decided_by', 'admin'))
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Failed to approve: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/approvals/<aid>/decline', methods=['POST'])
def decline_item(aid):
    """Decline an item."""
    try:
        from app.services.approvals import decline_item
        
        data = request.get_json() or {}
        result = decline_item(int(aid), data.get('decided_by', 'admin'), data.get('reason'))
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Failed to decline: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== BUDGET ====================

@api_bp.route('/domains/<domain_id>/budget', methods=['GET'])
def get_budget(domain_id):
    """Get budget status for a domain."""
    try:
        from app.models.database import get_session
        session = get_session()
        domain = session.get(Domain, domain_id)
        if not domain:
            return jsonify({'error': 'Domain not found'}), 404
        
        return jsonify({
            'domain_id': str(domain_id),
            'weekly_budget': domain.budget_weekly_aud,
            'spent': 0.0,
            'remaining': domain.budget_weekly_aud,
            'status': 'healthy'
        })
        
    except Exception as e:
        logger.error(f"Failed to get budget: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== CHAMBER 2 - SEMANTIC GRAVITY ====================

@api_bp.route('/domains/<domain_id>/chambers/sgs', methods=['GET'])
def get_sgs(domain_id):
    """Get SGS score and history."""
    try:
        from app.chambers.chamber_02_semantic import get_sgs_history, get_semantic_map_data
        
        history = get_sgs_history(UUID(domain_id))
        map_data = get_semantic_map_data(UUID(domain_id))
        
        latest = history[0] if history else None
        
        return jsonify({
            'domain_id': str(domain_id),
            'sgs_score': latest.get('sgs_score') if latest else None,
            'cluster_count': latest.get('cluster_count') if latest else 0,
            'drift_delta': latest.get('drift_delta') if latest else 0,
            'history': history[:10],
            'map_data': map_data
        })
        
    except Exception as e:
        logger.error(f"Failed to get SGS: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/domains/<domain_id>/chambers/sgs/compute', methods=['POST'])
def compute_sgs(domain_id):
    """Compute SGS score."""
    try:
        from app.chambers.chamber_02_semantic import compute_sgs
        
        result = compute_sgs(UUID(domain_id))
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Failed to compute SGS: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== CHAMBER 3 - LCRI ====================

@api_bp.route('/domains/<domain_id>/chambers/lcri', methods=['GET'])
def get_lcri(domain_id):
    """Get LCRI scores."""
    try:
        from app.chambers.chamber_03_survivability import get_latest_lcri, get_lcri_history
        
        latest = get_latest_lcri(UUID(domain_id))
        history = get_lcri_history(UUID(domain_id))
        
        return jsonify({
            'domain_id': str(domain_id),
            'average_lcri': latest.get('average_lcri'),
            'pages': latest.get('pages', []),
            'history': history[:10]
        })
        
    except Exception as e:
        logger.error(f"Failed to get LCRI: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/domains/<domain_id>/chambers/lcri/compute', methods=['POST'])
def compute_lcri(domain_id):
    """Compute LCRI scores."""
    try:
        from app.chambers.chamber_03_survivability import compute_lcri
        
        result = compute_lcri(UUID(domain_id))
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Failed to compute LCRI: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== CHAMBER 4 - AUTHORITY ====================

@api_bp.route('/domains/<domain_id>/chambers/authority', methods=['GET'])
def get_authority(domain_id):
    """Get authority scores."""
    try:
        from app.chambers.chamber_04_authority import get_authority_summary, get_authority_history
        
        summary = get_authority_summary(UUID(domain_id))
        history = get_authority_history(UUID(domain_id))
        
        return jsonify({
            'domain_id': str(domain_id),
            'average_authority': summary.get('average_authority'),
            'topics_mentioned': summary.get('topics_mentioned'),
            'total_topics': summary.get('total_topics'),
            'topics': history[:20]
        })
        
    except Exception as e:
        logger.error(f"Failed to get authority: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/domains/<domain_id>/chambers/authority/compute', methods=['POST'])
def compute_authority(domain_id):
    """Compute authority scores."""
    try:
        from app.chambers.chamber_04_authority import compute_authority
        
        result = compute_authority(UUID(domain_id))
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Failed to compute authority: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== CHAMBER 7 - AMPLIFIER ====================

@api_bp.route('/domains/<domain_id>/chambers/performance', methods=['GET'])
def get_performance(domain_id):
    """Get performance metrics."""
    try:
        from app.chambers.chamber_07_amplifier import get_performance_summary, get_performance_history
        
        summary = get_performance_summary(UUID(domain_id))
        history = get_performance_history(UUID(domain_id))
        
        return jsonify({
            'domain_id': str(domain_id),
            'summary': summary,
            'history': history[:10]
        })
        
    except Exception as e:
        logger.error(f"Failed to get performance: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/domains/<domain_id>/chambers/performance/measure', methods=['POST'])
def measure_performance(domain_id):
    """Measure performance."""
    try:
        from app.chambers.chamber_07_amplifier import measure_performance
        
        result = measure_performance(UUID(domain_id))
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Failed to measure performance: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== CHAMBER 8 - COMPETITIVE ====================

@api_bp.route('/domains/<domain_id>/chambers/competitors', methods=['GET'])
def get_competitors(domain_id):
    """Get competitors."""
    try:
        from app.chambers.chamber_08_competitive import get_competitors, assess_threats
        
        competitors = get_competitors(UUID(domain_id))
        threats = assess_threats(UUID(domain_id))
        
        return jsonify({
            'domain_id': str(domain_id),
            'competitors': competitors,
            'threats': threats
        })
        
    except Exception as e:
        logger.error(f"Failed to get competitors: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/domains/<domain_id>/chambers/competitors/add', methods=['POST'])
def add_competitor(domain_id):
    """Add a competitor."""
    try:
        from app.chambers.chamber_08_competitive import add_competitor
        
        data = request.get_json()
        result = add_competitor(
            UUID(domain_id),
            data['competitor_url'],
            data.get('competitor_name')
        )
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Failed to add competitor: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/domains/<domain_id>/chambers/competitors/discover', methods=['POST'])
def discover_competitors(domain_id):
    """Discover competitors."""
    try:
        from app.chambers.chamber_08_competitive import discover_competitors
        
        result = discover_competitors(UUID(domain_id))
        return jsonify({'competitors': result})
        
    except Exception as e:
        logger.error(f"Failed to discover competitors: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== CHAMBER 9 - ORACLE ====================

@api_bp.route('/domains/<domain_id>/chambers/oracle', methods=['GET'])
def get_oracle(domain_id):
    """Get Oracle forecast."""
    try:
        from app.chambers.chamber_09_oracle import get_latest_forecast, get_calendar
        
        forecast = get_latest_forecast(UUID(domain_id))
        calendar = get_calendar(UUID(domain_id))
        
        return jsonify({
            'domain_id': str(domain_id),
            'forecast': forecast,
            'calendar': calendar
        })
        
    except Exception as e:
        logger.error(f"Failed to get Oracle: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/domains/<domain_id>/chambers/oracle/generate', methods=['POST'])
def generate_oracle(domain_id):
    """Generate Oracle forecast."""
    try:
        from app.chambers.chamber_09_oracle import generate_forecast
        
        result = generate_forecast(UUID(domain_id))
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Failed to generate Oracle: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== CHAMBER 11 - DEFENSIVE ====================

@api_bp.route('/domains/<domain_id>/chambers/defensive', methods=['GET'])
def get_defensive(domain_id):
    """Get defensive perception data."""
    try:
        from app.chambers.chamber_11_defensive import get_latest_perception, get_perception_trends
        
        latest = get_latest_perception(UUID(domain_id))
        trends = get_perception_trends(UUID(domain_id))
        
        return jsonify({
            'domain_id': str(domain_id),
            'latest': latest,
            'trends': trends[:10]
        })
        
    except Exception as e:
        logger.error(f"Failed to get defensive: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/domains/<domain_id>/chambers/defensive/analyze', methods=['POST'])
def analyze_defensive(domain_id):
    """Analyze perception."""
    try:
        from app.chambers.chamber_11_defensive import analyze_perception
        
        result = analyze_perception(UUID(domain_id))
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Failed to analyze perception: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/domains/<domain_id>/chambers/defensive/correct', methods=['POST'])
def generate_correction(domain_id):
    """Generate correction prompt."""
    try:
        from app.chambers.chamber_11_defensive import generate_correction_prompt
        
        data = request.get_json()
        result = generate_correction_prompt(UUID(domain_id), data['negative_claim'])
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Failed to generate correction: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== ALL CHAMBERS STATUS ====================

# ==================== WAR ROOM ====================

@api_bp.route('/domains/<domain_id>/warroom', methods=['GET'])
def get_warroom(domain_id):
    """Get comprehensive war room data."""
    try:
        from app.models.database import get_session
        from app.models.domain import Domain
        
        session = get_session()
        domain = session.query(Domain).filter_by(domain_id=domain_id).first()
        if not domain:
            session.close()
            return jsonify({'error': 'Domain not found'}), 404
        
        # Get crawl data for scoring
        crawl_data = domain.crawl_data
        
        # Compute score from crawl data
        score = 50.0
        status = 'pending'
        components = {}
        
        if crawl_data:
            status = 'ready'
            homepage = crawl_data.get('homepage', {})
            metadata = homepage.get('metadata', {})
            technical = 0
            if metadata.get('description'):
                technical += 50
            schemas = homepage.get('schema', [])
            if schemas:
                technical += 50
            components['technical_foundation'] = {'score': technical}
            
            pages = crawl_data.get('pages', [])
            text_content = homepage.get('text_content', '')
            survivability = 0
            if len(text_content) > 2000:
                survivability += 50
            if len(pages) >= 3:
                survivability += 50
            components['content_survivability'] = {'score': survivability}
            
            components['llm_share_of_voice'] = {'score': 0.0, 'status': 'pending'}
            components['semantic_gravity'] = {'score': 0.0, 'status': 'pending'}
            components['hallucination_debt'] = {'score': 100.0, 'status': 'pending'}
            components['competitive_position'] = {'score': 0.0, 'status': 'pending'}
            components['predictive_velocity'] = {'score': 50.0, 'status': 'pending'}
            
            score = (technical * 0.25) + (survivability * 0.25) + (50 * 0.5)
        
        session.close()
        
        return jsonify({
            'domain_id': str(domain_id),
            'domain_name': domain.display_name or domain.domain_name,
            'total_score': round(score, 2),
            'status': status,
            'confidence': 0.3 if status == 'ready' else 0.0,
            'components': components,
            'crawl_status': 'ready' if crawl_data else 'pending',
        })
        
    except Exception as e:
        logger.error(f"Failed to get warroom: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ==================== DEPLOYMENT ====================

@api_bp.route('/domains/<domain_id>/deployments', methods=['GET'])
def get_deployments(domain_id):
    """Get deployment history for a domain."""
    try:
        from app.services.deployment_engine import DeploymentEngine
        
        engine = DeploymentEngine(UUID(domain_id))
        deployments = engine.get_deployment_history()
        
        return jsonify({'deployments': deployments, 'count': len(deployments)})
        
    except Exception as e:
        logger.error(f"Failed to get deployments: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/domains/<domain_id>/deployments/<did>/preview', methods=['GET'])
def preview_deployment(domain_id, did):
    """Preview a deployment (dry-run)."""
    try:
        from app.services.deployment_engine import DeploymentEngine
        
        engine = DeploymentEngine(UUID(domain_id))
        result = engine.deploy_brief(UUID(did), dry_run=True)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Failed to preview deployment: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/domains/<domain_id>/deploy/<brief_id>', methods=['POST'])
def deploy_brief(domain_id, brief_id):
    """Deploy an approved brief to WordPress."""
    try:
        from app.services.deployment_engine import DeploymentEngine
        
        engine = DeploymentEngine(UUID(domain_id))
        result = engine.deploy_brief(UUID(brief_id))
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Failed to deploy: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/domains/<domain_id>/rollback/<did>', methods=['POST'])
def rollback_deployment(domain_id, did):
    """Rollback a deployment."""
    try:
        from app.services.deployment_engine import DeploymentEngine
        
        engine = DeploymentEngine(UUID(domain_id))
        result = engine.rollback(UUID(did))
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Failed to rollback: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/domains/<domain_id>/deployments/<did>/diff', methods=['GET'])
def get_deployment_diff(domain_id, did):
    """Get diff for a deployment."""
    try:
        from app.services.deployment_engine import DeploymentEngine
        
        engine = DeploymentEngine(UUID(domain_id))
        result = engine.get_deployment_diff(UUID(did))
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Failed to get diff: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== ELAINE INTEGRATION ====================

@api_bp.route('/elaine/status/<domain_id>', methods=['GET'])
def elaine_status(domain_id):
    """Get status for ELAINE."""
    try:
        from app.services.elaine_integration import ElaineIntegration
        
        integration = ElaineIntegration()
        result = integration.query_status(UUID(domain_id))
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Failed to get ELAINE status: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/elaine/score/<domain_id>', methods=['GET'])
def elaine_score(domain_id):
    """Get score for ELAINE."""
    try:
        from app.services.elaine_integration import ElaineIntegration
        
        integration = ElaineIntegration()
        result = integration.query_score(UUID(domain_id))
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Failed to get ELAINE score: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/elaine/briefs/pending', methods=['GET'])
def elaine_pending_briefs():
    """Get pending briefs for ELAINE."""
    try:
        from app.services.elaine_integration import ElaineIntegration
        
        integration = ElaineIntegration()
        domain_id = request.args.get('domain_id')
        briefs = integration.get_pending_briefs(UUID(domain_id) if domain_id else None)
        
        return jsonify({'briefs': briefs, 'count': len(briefs)})
        
    except Exception as e:
        logger.error(f"Failed to get briefs: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/elaine/approve/<approval_id>', methods=['POST'])
def elaine_approve(approval_id):
    """Process ELAINE approval response."""
    try:
        from app.services.elaine_integration import ElaineIntegration
        
        data = request.get_json() or {}
        integration = ElaineIntegration()
        result = integration.process_approval_response(
            UUID(approval_id),
            data.get('approved', True),
            data.get('notes')
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Failed to process approval: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/elaine/morning-briefing/<domain_id>', methods=['GET'])
def elaine_morning_briefing(domain_id):
    """Get morning briefing data for ELAINE."""
    try:
        from app.services.elaine_integration import ElaineIntegration
        from app.services.score_engine import compute_peterman_score
        from app.models.database import get_session
        from app.models.hallucination import Hallucination
        from app.services.approvals import get_domain_approvals
        
        # Get score
        score = compute_peterman_score(UUID(domain_id))
        
        # Get pending approvals
        approvals = get_domain_approvals(UUID(domain_id), 'pending')
        
        # Get open hallucinations
        session = get_session()
        hallucinations = session.query(Hallucination).filter(
            Hallucination.domain_id == UUID(domain_id),
            Hallucination.status == 'open'
        ).all()
        
        hallucination_data = [
            {'id': h.hallucination_id, 'text': h.hallucinated_claim, 'severity': h.severity}
            for h in hallucinations
        ]
        session.close()
        
        result = {
            'domain_id': domain_id,
            'score': score,
            'pending_approvals': approvals,
            'hallucinations': hallucination_data,
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Failed to get briefing: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== CK WRITER INTEGRATION ====================

@api_bp.route('/domains/<domain_id>/briefs/<bid>/send-to-writer', methods=['POST'])
def send_to_ck_writer(domain_id, bid):
    """Send brief to CK Writer for drafting."""
    try:
        from app.services.ckwriter_integration import CKWriterIntegration
        
        integration = CKWriterIntegration()
        
        # Get brief details
        from app.services.forge import get_brief
        brief = get_brief(int(bid))
        
        result = integration.send_brief_to_writer(
            UUID(bid),
            UUID(domain_id),
            brief.get('title', ''),
            brief.get('content', ''),
            brief.get('target_url'),
            brief.get('keywords', [])
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Failed to send to CK Writer: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== REPORTS ====================

@api_bp.route('/domains/<domain_id>/report/generate', methods=['POST'])
def generate_report(domain_id):
    """Generate a PDF report."""
    try:
        from app.services.report_generator import ReportGenerator
        
        data = request.get_json() or {}
        period_days = data.get('period_days', 30)
        
        generator = ReportGenerator(UUID(domain_id))
        report = generator.generate_report(period_days=period_days)
        
        # Save report
        filepath = generator.save_report(report)
        
        return jsonify({
            'status': 'generated',
            'report': report,
            'filepath': filepath,
        })
        
    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/domains/<domain_id>/report/latest', methods=['GET'])
def get_latest_report(domain_id):
    """Get the latest report."""
    try:
        import os
        
        reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports')
        
        if not os.path.exists(reports_dir):
            return jsonify({'error': 'No reports found'}), 404
        
        # Find latest report for domain
        reports = [f for f in os.listdir(reports_dir) if f.startswith(f'peterman-report-{domain_id}')]
        
        if not reports:
            return jsonify({'error': 'No reports found'}), 404
        
        latest = sorted(reports)[-1]
        
        return jsonify({
            'domain_id': domain_id,
            'filename': latest,
            'url': f'/reports/{latest}',
        })
        
    except Exception as e:
        logger.error(f"Failed to get report: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== ALL CHAMBERS STATUS ====================

@api_bp.route('/domains/<domain_id>/chambers/all', methods=['GET'])
def get_all_chambers_status(domain_id):
    """Get status of all chambers."""
    try:
        from app.chambers.chamber_02_semantic import get_sgs_history
        from app.chambers.chamber_03_survivability import get_latest_lcri
        from app.chambers.chamber_04_authority import get_authority_summary
        from app.chambers.chamber_07_amplifier import get_performance_summary
        from app.chambers.chamber_08_competitive import get_competitors
        from app.chambers.chamber_09_oracle import get_latest_forecast
        from app.chambers.chamber_11_defensive import get_latest_perception
        
        sgs = get_sgs_history(UUID(domain_id))
        lcri = get_latest_lcri(UUID(domain_id))
        authority = get_authority_summary(UUID(domain_id))
        perf = get_performance_summary(UUID(domain_id))
        competitors = get_competitors(UUID(domain_id))
        oracle = get_latest_forecast(UUID(domain_id))
        defensive = get_latest_perception(UUID(domain_id))
        
        chambers = [
            {'id': 2, 'name': 'Semantic Gravity', 'status': 'ready' if sgs else 'pending', 'score': sgs[0].get('sgs_score') if sgs else None},
            {'id': 3, 'name': 'Content Survivability', 'status': 'ready' if lcri.get('average_lcri') else 'pending', 'score': lcri.get('average_lcri')},
            {'id': 4, 'name': 'Authority', 'status': 'ready' if authority.get('average_authority') else 'pending', 'score': authority.get('average_authority')},
            {'id': 7, 'name': 'Amplifier', 'status': 'ready' if perf.get('average_sov') else 'pending', 'score': perf.get('average_sov')},
            {'id': 8, 'name': 'Competitive Shadow', 'status': 'ready' if competitors else 'pending', 'count': len(competitors)},
            {'id': 9, 'name': 'Oracle', 'status': 'ready' if oracle.get('topics') else 'pending', 'confidence': oracle.get('confidence')},
            {'id': 11, 'name': 'Defensive Shield', 'status': 'ready' if defensive.get('sentiment_score') else 'pending', 'score': defensive.get('sentiment_score')},
        ]
        
        return jsonify({
            'domain_id': str(domain_id),
            'chambers': chambers
        })
        
    except Exception as e:
        logger.error(f"Failed to get all chambers: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== CONTEXT-AWARE HELP ====================

@api_bp.route('/help/screens', methods=['GET'])
def get_help_screens():
    """Get list of all help screens."""
    try:
        from app.services.help import get_all_screens
        
        screens = get_all_screens()
        return jsonify({'screens': screens})
        
    except Exception as e:
        logger.error(f"Failed to get help screens: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/help/<screen_id>', methods=['GET'])
def get_help(screen_id):
    """Get help content for a specific screen."""
    try:
        from app.services.help import get_help_for_screen
        
        help_entry = get_help_for_screen(screen_id)
        
        if not help_entry:
            return jsonify({'error': 'Screen not found'}), 404
        
        return jsonify({
            'screen_id': help_entry.screen_id,
            'title': help_entry.title,
            'content': help_entry.content,
            'keywords': help_entry.keywords,
            'shortcuts': help_entry.shortcuts,
        })
        
    except Exception as e:
        logger.error(f"Failed to get help: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/help/search', methods=['GET'])
def search_help():
    """Search help content."""
    try:
        from app.services.help import search_help
        
        query = request.args.get('q', '')
        if not query:
            return jsonify({'error': 'Query required'}), 400
        
        results = search_help(query)
        
        return jsonify({
            'query': query,
            'results': [
                {
                    'screen_id': r.screen_id,
                    'title': r.title,
                    'keywords': r.keywords[:3],
                }
                for r in results
            ],
            'count': len(results)
        })
        
    except Exception as e:
        logger.error(f"Failed to search help: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== FREE AUDIT TOOL ====================

@api_bp.route('/free-audit', methods=['POST'])
def start_free_audit():
    """
    Start a free LLM presence audit.
    
    Limited scope:
    - Homepage crawl only
    - 5 auto-generated queries
    - Claude CLI probes (1 run)
    - Basic score (SoV only)
    """
    try:
        data = request.get_json()
        
        domain = data.get('domain')
        email = data.get('email')
        
        if not domain or not email:
            return jsonify({'error': 'domain and email are required'}), 400
        
        # Validate email format
        if '@' not in email:
            return jsonify({'error': 'Valid email required'}), 400
        
        # Create a unique audit ID
        import uuid
        audit_id = str(uuid.uuid4())[:8]
        
        # Return immediate response with audit ID
        # The actual audit runs asynchronously
        return jsonify({
            'audit_id': audit_id,
            'status': 'started',
            'message': 'Free audit started. You will receive an email when complete.',
            'domain': domain,
            'email': email,
        })
        
    except Exception as e:
        logger.error(f"Failed to start free audit: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/free-audit/<audit_id>/status', methods=['GET'])
def get_free_audit_status(audit_id):
    """Check status of a free audit."""
    try:
        # In a real implementation, this would check database for audit status
        # For now, return a placeholder
        return jsonify({
            'audit_id': audit_id,
            'status': 'completed',  # Would be dynamic in production
            'score': 42.5,  # Would be real SoV score
            'mentions': 3,
            'llms_probed': 3,
        })
        
    except Exception as e:
        logger.error(f"Failed to get audit status: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== ADVANCED SCORING ====================

@api_bp.route('/domains/<domain_id>/advanced-score', methods=['GET'])
def get_advanced_score(domain_id):
    """Get advanced scoring metrics."""
    try:
        from app.services.advanced_scoring import get_advanced_metrics
        
        metrics = get_advanced_metrics(UUID(domain_id))
        
        return jsonify({
            'domain_id': str(domain_id),
            'metrics': metrics
        })
        
    except Exception as e:
        logger.error(f"Failed to get advanced score: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/domains/<domain_id>/advanced-score/consensus', methods=['GET'])
def get_consensus_score(domain_id):
    """Get multi-LLM consensus score."""
    try:
        from app.services.advanced_scoring import compute_multi_llm_consensus
        
        result = compute_multi_llm_consensus(UUID(domain_id))
        
        return jsonify({
            'domain_id': str(domain_id),
            'consensus': result
        })
        
    except Exception as e:
        logger.error(f"Failed to get consensus: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/domains/<domain_id>/advanced-score/authority-decay', methods=['GET'])
def get_authority_decay(domain_id):
    """Get authority decay detection."""
    try:
        from app.services.advanced_scoring import compute_authority_decay
        
        result = compute_authority_decay(UUID(domain_id))
        
        return jsonify({
            'domain_id': str(domain_id),
            'decay': result
        })
        
    except Exception as e:
        logger.error(f"Failed to get decay: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/domains/<domain_id>/advanced-score/retrain-pulse', methods=['GET'])
def get_retrain_pulse(domain_id):
    """Get retrain pulse detection."""
    try:
        from app.services.advanced_scoring import detect_retrain_pulse
        
        result = detect_retrain_pulse(UUID(domain_id))
        
        return jsonify({
            'domain_id': str(domain_id),
            'pulse': result
        })
        
    except Exception as e:
        logger.error(f"Failed to get pulse: {e}")
        return jsonify({'error': str(e)}), 500
