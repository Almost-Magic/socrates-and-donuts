"""
ELAINE Phase 5: Flask Routes
Morning Briefing v2, People of Interest, Self-Healing, Memory
"""

from flask import Blueprint, request, jsonify
import json

phase5_bp = Blueprint('phase5', __name__)

# ─── Lazy initialisation ───
_briefing = None
_resilience = None
_memory = None


def get_briefing():
    global _briefing
    if _briefing is None:
        from modules.phase5_briefing.morning_briefing import MorningBriefingEngine
        _briefing = MorningBriefingEngine()
    return _briefing


def get_resilience():
    global _resilience
    if _resilience is None:
        from modules.phase5_resilience.resilience import ResilienceEngine
        _resilience = ResilienceEngine()
    return _resilience


def get_memory():
    global _memory
    if _memory is None:
        from modules.phase5_memory.memory import MemoryEngine
        _memory = MemoryEngine()
    return _memory


# ═══════════════════════════════════════════
#  MORNING BRIEFING v2
# ═══════════════════════════════════════════

@phase5_bp.route('/api/briefing/full', methods=['GET'])
def morning_briefing_full():
    """Generate the full Phase 5 morning briefing (news, LinkedIn, POI, etc.)."""
    try:
        data = get_briefing().generate_briefing()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e), "greeting": "Good morning, Mani.",
                        "summary": "Briefing encountered an error. Check health status."}), 500


@phase5_bp.route('/api/briefing/config', methods=['GET', 'POST'])
def briefing_config():
    """Get or update briefing configuration."""
    b = get_briefing()
    if request.method == 'POST':
        data = request.get_json(force=True)
        b.config.update(data)
        b.save_config()
        return jsonify({"status": "saved", "config": b.config})
    return jsonify(b.config)


@phase5_bp.route('/api/briefing/history', methods=['GET'])
def briefing_history():
    limit = request.args.get('limit', 10, type=int)
    return jsonify(get_briefing().get_briefing_history(limit))


# ═══════════════════════════════════════════
#  PEOPLE OF INTEREST
# ═══════════════════════════════════════════

@phase5_bp.route('/api/poi', methods=['GET', 'POST'])
def people_of_interest():
    b = get_briefing()
    if request.method == 'POST':
        data = request.get_json(force=True)
        pid = b.add_person_of_interest(
            name=data.get('name'),
            role=data.get('role'),
            company=data.get('company'),
            linkedin_url=data.get('linkedin_url'),
            twitter_handle=data.get('twitter_handle'),
            website=data.get('website'),
            email_addr=data.get('email'),
            why_important=data.get('why_important'),
            category=data.get('category', 'general'),
            interest_level=data.get('interest_level', 5)
        )
        return jsonify({"id": pid, "status": "added"})

    category = request.args.get('category')
    min_level = request.args.get('min_level', 0, type=int)
    return jsonify(b.get_people_of_interest(category, min_level))


@phase5_bp.route('/api/poi/<int:person_id>', methods=['GET', 'PUT', 'DELETE'])
def person_detail(person_id):
    b = get_briefing()
    if request.method == 'DELETE':
        b.remove_person(person_id)
        return jsonify({"status": "removed"})
    if request.method == 'PUT':
        data = request.get_json(force=True)
        b.update_person(person_id, **data)
        return jsonify({"status": "updated"})
    # GET — return person with recent activity
    people = b.get_people_of_interest()
    person = next((p for p in people if p["id"] == person_id), None)
    if not person:
        return jsonify({"error": "Not found"}), 404
    return jsonify(person)


@phase5_bp.route('/api/poi/<int:person_id>/interaction', methods=['POST'])
def log_interaction(person_id):
    data = request.get_json(force=True)
    get_briefing().log_poi_interaction(
        person_id,
        data.get('type', 'general'),
        data.get('notes')
    )
    return jsonify({"status": "logged"})


@phase5_bp.route('/api/poi/scan', methods=['POST'])
def scan_poi():
    """Scan for People of Interest activity."""
    max_people = request.get_json(force=True).get('max_people', 10) if request.is_json else 10
    result = get_briefing().scan_poi_activity(max_people)
    return jsonify(result)


@phase5_bp.route('/api/poi/discover', methods=['POST'])
def discover_poi():
    """Run auto-discovery for People of Interest."""
    b = get_briefing()
    results = {
        "from_clients": b.discover_people_from_clients(),
        "from_meetings": b.discover_people_from_meetings(),
    }
    return jsonify(results)


@phase5_bp.route('/api/poi/stats', methods=['GET'])
def poi_stats():
    return jsonify(get_briefing().get_poi_stats())


# ═══════════════════════════════════════════
#  HEALTH & RESILIENCE
# ═══════════════════════════════════════════

@phase5_bp.route('/api/phase5/health', methods=['GET'])
def health_simple():
    """Phase 5 modules health check."""
    return jsonify({"status": "ok", "version": "3.5", "phase": 5})


@phase5_bp.route('/api/health/detailed', methods=['GET'])
def health_detailed():
    """Detailed health report for all modules."""
    return jsonify(get_resilience().get_health_report())


@phase5_bp.route('/api/health/check', methods=['POST'])
def run_health_checks():
    """Run active health checks on all modules."""
    return jsonify(get_resilience().run_health_checks())


@phase5_bp.route('/api/health/errors', methods=['GET'])
def error_log():
    module = request.args.get('module')
    limit = request.args.get('limit', 50, type=int)
    return jsonify(get_resilience().get_error_log(module, limit))


# ═══════════════════════════════════════════
#  MEMORY & CONVERSATION
# ═══════════════════════════════════════════

@phase5_bp.route('/api/memory/history', methods=['GET'])
def chat_history():
    limit = request.args.get('limit', 50, type=int)
    return jsonify(get_memory().get_history(limit))


@phase5_bp.route('/api/memory/search', methods=['GET'])
def search_history():
    q = request.args.get('q', '')
    return jsonify(get_memory().search_history(q))


@phase5_bp.route('/api/memory/stats', methods=['GET'])
def memory_stats():
    m = get_memory()
    return jsonify({
        "conversations": m.get_conversation_stats(),
        "storage": m.get_memory_size(),
        "active_topics": m.get_active_topics(),
        "frequent_commands": m.get_frequent_commands()
    })


@phase5_bp.route('/api/memory/context', methods=['GET'])
def last_context():
    return jsonify(get_memory().get_last_topic_context() or {})


@phase5_bp.route('/api/memory/preferences', methods=['GET', 'POST'])
def preferences():
    m = get_memory()
    if request.method == 'POST':
        data = request.get_json(force=True)
        for k, v in data.items():
            m.set_preference(k, v)
        return jsonify({"status": "saved"})
    return jsonify(m.get_all_preferences())


@phase5_bp.route('/api/memory/preferences/<key>', methods=['GET', 'PUT', 'DELETE'])
def preference_detail(key):
    m = get_memory()
    if request.method == 'DELETE':
        m.delete_preference(key)
        return jsonify({"status": "deleted"})
    if request.method == 'PUT':
        data = request.get_json(force=True)
        m.set_preference(key, data.get('value'))
        return jsonify({"status": "saved"})
    return jsonify({"key": key, "value": m.get_preference(key)})


@phase5_bp.route('/api/memory/state', methods=['GET', 'POST'])
def session_state():
    m = get_memory()
    if request.method == 'POST':
        data = request.get_json(force=True)
        for k, v in data.items():
            m.set_state(k, v)
        return jsonify({"status": "saved"})
    return jsonify(m.get_all_state())


@phase5_bp.route('/api/memory/export', methods=['GET'])
def export_memory():
    return jsonify(get_memory().export_all())


@phase5_bp.route('/api/memory/clear', methods=['POST'])
def clear_memory():
    data = request.get_json(force=True) if request.is_json else {}
    before = data.get('before')
    get_memory().clear_history(before)
    return jsonify({"status": "cleared"})
