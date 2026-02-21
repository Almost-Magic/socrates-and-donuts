"""Socrates & Donuts API Routes"""
from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import hashlib
import json

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint - Phase 0 checkpoint requirement."""
    # Get vault entry count
    vault_entries = 0
    try:
        from app.services.portability import get_vault_entry_count
        vault_entries = get_vault_entry_count()
    except:
        pass
    
    # Get LLM connection status
    llm_provider = 'none'
    llm_connected = False
    try:
        from app.services.portability import load_settings
        settings = load_settings()
        llm_provider = settings.get('llm_provider', 'none')
        llm_connected = llm_provider != 'none' and bool(settings.get('llm_api_key', ''))
    except:
        pass
    
    # Get active arc
    active_arc = None
    try:
        from app.services.portability import get_active_arc
        active_arc = get_active_arc()
    except:
        pass
    
    return jsonify({
        'status': 'healthy',
        'app': 'Socrates & Donuts',
        'version': '1.0.0',
        'port': 5010,
        'vault_entries': vault_entries,
        'llm_connected': llm_connected,
        'llm_provider': llm_provider,
        'questions_in_bank': 60,  # 6 frameworks × 10 questions
        'active_arc': active_arc
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
    
    # Generate Socratic follow-up (or contradiction if detected)
    from app.services.llm import generate_response
    from app.services.contradiction import find_contradictions_in_session
    
    # Get session history for contradiction detection
    session_history = []
    try:
        from app.services.portability import get_db_connection
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT response_text FROM sessions WHERE id = ?", (session_id,))
        row = c.fetchone()
        if row and row['response_text']:
            session_history.append({'response_text': row['response_text']})
        conn.close()
    except:
        pass
    
    # Check for contradictions
    contradictions = find_contradictions_in_session(user_input, session_history)
    
    response = generate_response(
        user_input=user_input,
        session_id=session_id,
        framework=data.get('framework', 'socratic')
    )
    
    return jsonify({
        'session_id': session_id,
        'response': response,
        'type': 'question',
        'contradictions': contradictions
    })


@bp.route('/session/<session_id>/feedback', methods=['POST'])
def session_feedback(session_id):
    """Submit feedback after a session."""
    data = request.get_json() or {}
    feedback = data.get('feedback', '')
    
    if feedback not in ['yes', 'not_sure', 'not_today']:
        return jsonify({'error': 'Invalid feedback value'}), 400
    
    import uuid
    feedback_id = str(uuid.uuid4())
    
    try:
        from app.services.portability import get_db_connection
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("""
            INSERT INTO feedback_log (id, session_id, feedback, logged_at)
            VALUES (?, ?, ?, datetime('now'))
        """, (feedback_id, session_id, feedback))
        conn.commit()
        conn.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    return jsonify({'status': 'saved', 'feedback_id': feedback_id})


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


@bp.route('/vault/insights', methods=['POST', 'GET'])
def vault_insights():
    """Get or save insights to vault."""
    from app.services.portability import get_db_connection
    import uuid
    
    if request.method == 'GET':
        # Get all insights
        try:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("""
                SELECT id, title, content, tags, created_at
                FROM vault_entries
                WHERE entry_type = 'insight'
                ORDER BY created_at DESC
            """)
            insights = [dict(row) for row in c.fetchall()]
            conn.close()
            
            # Parse tags JSON
            for insight in insights:
                insight['tags'] = json.loads(insight.get('tags', '[]'))
            
            return jsonify(insights)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # POST - save insight
    data = request.get_json() or {}
    insight_id = str(uuid.uuid4())
    
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("""
            INSERT INTO vault_entries (id, entry_type, title, content, tags, created_at, updated_at)
            VALUES (?, 'insight', ?, ?, ?, datetime('now'), datetime('now'))
        """, (
            insight_id,
            data.get('title', ''),
            data.get('content', ''),
            json.dumps(data.get('tags', []))
        ))
        conn.commit()
        conn.close()
        
        return jsonify({'id': insight_id, 'status': 'saved'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/vault/letters', methods=['POST', 'GET'])
def vault_letters():
    """Get or save letters (unsent or one-year time-locked)."""
    from app.services.portability import get_db_connection
    import uuid
    
    if request.method == 'GET':
        # Get all letters
        try:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("""
                SELECT id, title, content, opens_at, created_at
                FROM vault_entries
                WHERE entry_type IN ('letter_unsent', 'letter_oneyear')
                ORDER BY created_at DESC
            """)
            letters = [dict(row) for row in c.fetchall()]
            conn.close()
            return jsonify(letters)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # POST - save letter
    data = request.get_json() or {}
    letter_type = data.get('type', 'unsent')
    letter_id = str(uuid.uuid4())
    opens_at = None
    
    if letter_type == 'oneyear':
        # Lock for exactly one year from today
        opens_at = (datetime.utcnow() + timedelta(days=365)).isoformat()
    
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("""
            INSERT INTO vault_entries (id, entry_type, title, content, tags, opens_at, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """, (
            letter_id,
            f'letter_{letter_type}',
            data.get('title', 'Letter'),
            data.get('content', ''),
            json.dumps(data.get('tags', [])),
            opens_at
        ))
        conn.commit()
        conn.close()
        
        return jsonify({'id': letter_id, 'opens_at': opens_at})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/vault/letters/<letter_id>', methods=['GET'])
def get_letter(letter_id):
    """Get a specific letter, checking time lock."""
    try:
        from app.services.portability import get_db_connection
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("""
            SELECT id, title, content, opens_at, entry_type
            FROM vault_entries
            WHERE id = ?
        """, (letter_id,))
        row = c.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'error': 'Not found'}), 404
        
        # Check time lock
        if row['opens_at']:
            opens_at = datetime.fromisoformat(row['opens_at'])
            if datetime.utcnow() < opens_at:
                return jsonify({
                    'locked': True,
                    'opens_at': row['opens_at'],
                    'message': 'This letter is sealed. It will open when the time comes.'
                }), 403
        
        return jsonify({
            'id': row['id'],
            'title': row['title'],
            'content': row['content'],
            'opens_at': row['opens_at']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/ai/test-connection', methods=['POST'])
def test_ai_connection():
    """Test LLM connection with provided credentials."""
    data = request.get_json() or {}
    provider = data.get('provider', 'none')
    
    if provider == 'none':
        return jsonify({'connected': False, 'error': 'No AI provider configured'})
    
    # For now, return a placeholder - actual connection testing would use the LLM service
    return jsonify({
        'connected': False,
        'provider': provider,
        'error': 'Connection test not yet implemented - configure API key in settings'
    })
