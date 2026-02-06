"""
Elaine v4 — Phase 10 API Routes
Chronicle v2: Meeting Intelligence + ElevenLabs Voice
Almost Magic Tech Lab
"""

from flask import Blueprint, jsonify, request

chronicle_bp = Blueprint("chronicle", __name__, url_prefix="/api/chronicle")
voice_bp = Blueprint("voice", __name__, url_prefix="/api/voice")


def create_chronicle_routes(meeting_engine):

    @chronicle_bp.route("/meetings", methods=["GET"])
    def list_meetings():
        limit = request.args.get("limit", 20, type=int)
        person = request.args.get("person", "")
        meetings = meeting_engine.list_meetings(limit=limit, person=person)
        return jsonify([
            {
                "id": m.meeting_id, "title": m.title,
                "date": m.date.isoformat(), "template": m.template.value,
                "participants": [p.name for p in m.participants],
                "commitments": len(m.commitments),
                "decisions": len(m.decisions),
                "score": m.score.overall,
            }
            for m in meetings
        ])

    @chronicle_bp.route("/meetings", methods=["POST"])
    def create_meeting():
        data = request.get_json() or {}
        from modules.chronicle.models import MeetingTemplate
        from datetime import datetime
        meeting = meeting_engine.create_meeting(
            title=data.get("title", ""),
            template=MeetingTemplate(data.get("template", "discovery_call")),
            participants=data.get("participants", []),
            date=datetime.fromisoformat(data["date"]) if data.get("date") else None,
            duration_minutes=data.get("duration_minutes", 0),
        )
        return jsonify({"meeting_id": meeting.meeting_id, "title": meeting.title})

    @chronicle_bp.route("/meetings/<meeting_id>", methods=["GET"])
    def get_meeting(meeting_id):
        m = meeting_engine.get_meeting(meeting_id)
        if not m:
            return jsonify({"error": "Meeting not found"}), 404
        return jsonify({
            "id": m.meeting_id, "title": m.title,
            "date": m.date.isoformat(), "template": m.template.value,
            "duration_minutes": m.duration_minutes,
            "participants": [{"name": p.name, "role": p.role, "company": p.company} for p in m.participants],
            "commitments": [
                {"id": c.commitment_id, "text": c.text, "owner": c.owner,
                 "type": c.commitment_type.value, "status": c.status.value,
                 "trust_stake": c.trust_stake.value, "overdue": c.is_overdue,
                 "due": c.due_date.isoformat() if c.due_date else None}
                for c in m.commitments
            ],
            "decisions": [
                {"id": d.decision_id, "text": d.text, "made_by": d.made_by,
                 "context": d.context.value, "outcome": d.outcome.value}
                for d in m.decisions
            ],
            "score": {"overall": m.score.overall, "percentile": m.score.percentile, "comparison": m.score.comparison},
            "follow_up": {"subject": m.follow_up.subject, "body": m.follow_up.body, "sent": m.follow_up.sent},
        })

    @chronicle_bp.route("/prep/<meeting_id>", methods=["GET"])
    def prep(meeting_id):
        brief = meeting_engine.generate_pre_meeting_brief(meeting_id)
        return jsonify({
            "relationship_context": brief.relationship_context,
            "what_you_owe": brief.what_you_owe,
            "what_they_might_need": brief.what_they_might_need,
            "preparation_gaps": brief.preparation_gaps,
            "suggested_opening": brief.suggested_opening,
            "prep_questions": brief.prep_questions,
        })

    @chronicle_bp.route("/commitments", methods=["GET"])
    def commitments():
        owner = request.args.get("owner", "")
        return jsonify(meeting_engine.get_active_commitments(owner=owner))

    @chronicle_bp.route("/commitments/overdue", methods=["GET"])
    def overdue():
        return jsonify(meeting_engine.get_overdue_commitments())

    @chronicle_bp.route("/commitments/<meeting_id>", methods=["POST"])
    def add_commitment(meeting_id):
        data = request.get_json() or {}
        from modules.chronicle.models import CommitmentType, TrustStake
        from datetime import datetime
        c = meeting_engine.add_commitment(
            meeting_id=meeting_id,
            text=data.get("text", ""),
            owner=data.get("owner", "mani"),
            commitment_type=CommitmentType(data.get("type", "explicit_deadline")),
            due_date=datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None,
            trust_stake=TrustStake(data.get("trust_stake", "high")),
        )
        return jsonify({"commitment_id": c.commitment_id})

    @chronicle_bp.route("/commitments/<meeting_id>/<commitment_id>/status", methods=["PUT"])
    def update_status(meeting_id, commitment_id):
        data = request.get_json() or {}
        from modules.chronicle.models import CommitmentStatus
        meeting_engine.update_commitment_status(
            meeting_id, commitment_id,
            CommitmentStatus(data.get("status", "completed")),
            data.get("notes", ""),
        )
        return jsonify({"updated": True})

    @chronicle_bp.route("/extract/<meeting_id>", methods=["POST"])
    def extract(meeting_id):
        """Extract commitments from text/transcript."""
        data = request.get_json() or {}
        commitments = meeting_engine.extract_commitments(meeting_id, data.get("text", ""))
        return jsonify([
            {"id": c.commitment_id, "text": c.text, "owner": c.owner,
             "type": c.commitment_type.value, "mass": c.default_mass}
            for c in commitments
        ])

    @chronicle_bp.route("/decisions/<meeting_id>", methods=["POST"])
    def add_decision(meeting_id):
        data = request.get_json() or {}
        from modules.chronicle.models import DecisionContext
        d = meeting_engine.add_decision(
            meeting_id=meeting_id,
            text=data.get("text", ""),
            made_by=data.get("made_by", "mani"),
            context=DecisionContext(data.get("context", "collaborative")),
            data_informed=data.get("data_informed", False),
            pressure_level=data.get("pressure", "moderate"),
        )
        return jsonify({"decision_id": d.decision_id})

    @chronicle_bp.route("/decisions/<meeting_id>/<decision_id>/outcome", methods=["PUT"])
    def record_outcome(meeting_id, decision_id):
        data = request.get_json() or {}
        from modules.chronicle.models import DecisionOutcome
        meeting_engine.record_decision_outcome(
            meeting_id, decision_id,
            DecisionOutcome(data.get("outcome", "unknown")),
            data.get("notes", ""),
        )
        return jsonify({"recorded": True})

    @chronicle_bp.route("/decisions/archaeology", methods=["GET"])
    def archaeology():
        return jsonify(meeting_engine.get_decision_archaeology())

    @chronicle_bp.route("/followup/<meeting_id>", methods=["GET"])
    def followup(meeting_id):
        draft = meeting_engine.generate_follow_up(meeting_id)
        return jsonify({"subject": draft.subject, "body": draft.body, "tone": draft.tone})

    @chronicle_bp.route("/trajectory/<person_name>", methods=["GET"])
    def trajectory(person_name):
        t = meeting_engine.get_relationship_trajectory(person_name)
        return jsonify({
            "person": t.person_name, "direction": t.direction.value,
            "meetings": t.meetings, "risk": t.risk, "action": t.suggested_action,
        })

    @chronicle_bp.route("/patterns", methods=["GET"])
    def patterns():
        return jsonify(meeting_engine.get_meeting_patterns())

    @chronicle_bp.route("/calendar", methods=["GET"])
    def calendar():
        intel = meeting_engine.get_calendar_intelligence()
        return jsonify({
            "meetings_this_week": intel.meeting_count,
            "deep_work_blocks": intel.deep_work_blocks,
            "buffer_warnings": intel.buffer_warnings,
            "insights": intel.pattern_insights,
            "productivity": intel.productivity_prediction,
        })

    @chronicle_bp.route("/innovator", methods=["GET"])
    def innovator():
        innovations = meeting_engine.detect_innovations()
        return jsonify([
            {"id": i.innovation_id, "title": i.title, "type": i.innovation_type.value,
             "description": i.description, "confidence": round(i.confidence, 2),
             "recommendation": i.recommendation}
            for i in innovations
        ])

    @chronicle_bp.route("/briefing", methods=["GET"])
    def chronicle_briefing():
        return jsonify(meeting_engine.get_morning_briefing_data())

    @chronicle_bp.route("/status", methods=["GET"])
    def chronicle_status():
        return jsonify(meeting_engine.status())

    return chronicle_bp


def create_voice_routes(voice_formatter):

    @voice_bp.route("/config", methods=["GET"])
    def config():
        from modules.chronicle.voice import get_voice_config
        return jsonify(get_voice_config())

    @voice_bp.route("/briefing", methods=["POST"])
    def voice_briefing():
        """Convert briefing data to voice-ready segments."""
        data = request.get_json() or {}
        segments = voice_formatter.format_morning_briefing(data)
        return jsonify({
            "segments": [
                {"text": s.text, "emotion": s.emotion.value, "pause_ms": s.pause_before_ms}
                for s in segments
            ],
            "plain_text": voice_formatter.segments_to_text(segments),
            "ssml": voice_formatter.segments_to_ssml(segments),
        })

    @voice_bp.route("/alert", methods=["POST"])
    def voice_alert():
        data = request.get_json() or {}
        segments = voice_formatter.format_alert(
            data.get("type", "discovery"),
            data.get("message", ""),
        )
        return jsonify({
            "segments": [{"text": s.text, "emotion": s.emotion.value} for s in segments],
            "plain_text": voice_formatter.segments_to_text(segments),
        })

    @voice_bp.route("/name/<name>", methods=["GET"])
    def name_response(name):
        seg = voice_formatter.format_name_response(name)
        return jsonify({"text": seg.text, "emotion": seg.emotion.value})

    @voice_bp.route("/status", methods=["GET"])
    def voice_status():
        from modules.chronicle.voice import get_voice_config
        return jsonify(get_voice_config())

    return voice_bp
