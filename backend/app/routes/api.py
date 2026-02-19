"""Socrates & Donuts API Routes"""
from flask import Blueprint, jsonify, request
from datetime import datetime
import hashlib

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint - Phase 0 checkpoint requirement."""
    return jsonify({
        'status': 'healthy',
        'service': 'socrates-and-donuts',
        'version': '0.1.0',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })


@bp.route('/question/today', methods=['GET'])
def today_question():
    """Get the daily question based on deterministic date selection."""
    from app.data.questions import get_daily_question
    
    date = request.args.get('date')
    intensity = request.args.get('intensity', 'reflective')
    domain = request.args.get('domain')
    
    question = get_daily_question(date=date, intensity=intensity, domain=domain)
    return jsonify(question)


@bp.route('/question/random', methods=['GET'])
def random_question():
    """Get a random question filtered by intensity and domain."""
    from app.data.questions import get_random_question
    
    intensity = request.args.get('intensity', 'reflective')
    domain = request.args.get('domain')
    
    question = get_random_question(intensity=intensity, domain=domain)
    return jsonify(question)


@bp.route('/session/start', methods=['POST'])
def start_session():
    """Start a new reflection session."""
    data = request.get_json() or {}
    
    session_id = hashlib.sha256(
        f"{datetime.utcnow().isoformat()}".encode()
    ).hexdigest()[:16]
    
    return jsonify({
        'session_id': session_id,
        'started_at': datetime.utcnow().isoformat() + 'Z',
        'framework': data.get('framework', 'socratic'),
        'status': 'active'
    }), 201


@bp.route('/session/<session_id>/respond', methods=['POST'])
def session_respond(session_id):
    """Submit a response in an active session."""
    data = request.get_json() or {}
    user_input = data.get('content', '')
    
    # Check for crisis keywords
    from app.services.safety import check_crisis
    crisis_result = check_crisis(user_input)
    
    if crisis_result['is_crisis']:
        return jsonify({
            'session_id': session_id,
            'response': crisis_result['response'],
            'type': 'crisis',
            'resources': crisis_result['resources']
        })
    
    # Generate Socratic follow-up
    from app.services.llm import generate_response
    response = generate_response(
        user_input=user_input,
        session_id=session_id,
        framework=data.get('framework', 'socratic')
    )
    
    return jsonify({
        'session_id': session_id,
        'response': response,
        'type': 'question'
    })


@bp.route('/settings', methods=['GET', 'POST'])
def settings():
    """Get or update user settings."""
    if request.method == 'GET':
        from app.services.portability import load_settings
        return jsonify(load_settings())
    
    # POST - update settings
    data = request.get_json() or {}
    from app.services.portability import save_settings
    save_settings(data)
    return jsonify({'status': 'saved'})


@bp.route('/vault/export', methods=['GET'])
def export_vault():
    """Export all vault data as JSON."""
    from app.services.portability import export_vault_data
    return jsonify(export_vault_data())


@bp.route('/vault/import', methods=['POST'])
def import_vault():
    """Import vault data from JSON."""
    data = request.get_json() or {}
    from app.services.portability import import_vault_data
    result = import_vault_data(data)
    return jsonify(result)
