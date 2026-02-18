"""
Elaine v4 — Chat + Tool Registry + Service Health Routes
Claude CLI is the only AI engine.

Almost Magic Tech Lab
"""

from flask import Blueprint, jsonify, request, Response
import json
import logging
import os
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

logger = logging.getLogger("elaine.chat")

SUPERVISOR_URL = os.environ.get("SUPERVISOR_URL", "http://localhost:9000")
LAN_IP = os.environ.get("ELAINE_LAN_IP", "192.168.4.55")
CHAT_TIMEOUT = 10  # seconds — hard cap per user spec
CHAT_MAX_TOKENS = 150  # concise replies, not essays

# ── ElevenLabs Voice (TTS output) ─────────────────────────────
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "XQanfahzbl1YiUlZi5NW")
ELEVENLABS_MODEL = os.environ.get("ELEVENLABS_MODEL", "eleven_turbo_v2_5")
TTS_TIMEOUT = 10  # seconds

# ── Whisper STT (lazy-loaded on first request) ──────────────
WHISPER_MODEL_SIZE = os.environ.get("ELAINE_WHISPER_MODEL", "tiny")
_whisper_model = None


def _get_whisper():
    """Lazy-load the faster-whisper model. CPU int8 for speed (~75MB RAM)."""
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel
        _whisper_model = WhisperModel(
            WHISPER_MODEL_SIZE, device="cpu", compute_type="int8"
        )
        logger.info("Whisper '%s' loaded (CPU, int8)", WHISPER_MODEL_SIZE)
    return _whisper_model

# ── AMTL Tool Registry ─────────────────────────────────────────

TOOLS = [
    {
        "id": "workshop",
        "name": "The Workshop",
        "desc": "Central launcher — App 0",
        "port": 5003,
        "url": f"http://{LAN_IP}:5003",
        "health": "/api/health",
        "category": "core",
    },
    {
        "id": "supervisor",
        "name": "The Supervisor",
        "desc": "Runtime manager — GPU, models, health",
        "port": 9000,
        "url": f"http://{LAN_IP}:9000",
        "health": "/api/health",
        "category": "core",
    },
    {
        "id": "elaine",
        "name": "ELAINE",
        "desc": "Chief of Staff — 16 intelligence modules",
        "port": 5000,
        "url": f"http://{LAN_IP}:5000",
        "health": "/api/health",
        "category": "core",
    },
    {
        "id": "ripple",
        "name": "Ripple CRM",
        "desc": "Customer relationship management",
        "port": 3100,
        "url": f"http://{LAN_IP}:3100",
        "health": "/",
        "category": "business",
    },
    {
        "id": "ripple-api",
        "name": "Ripple CRM API",
        "desc": "CRM backend — contacts, deals, intelligence",
        "port": 8100,
        "url": f"http://{LAN_IP}:8100",
        "health": "/api/health",
        "category": "business",
    },
    {
        "id": "touchstone",
        "name": "Touchstone",
        "desc": "Marketing attribution engine",
        "port": 8200,
        "url": f"http://{LAN_IP}:8200",
        "health": "/api/v1/health",
        "category": "business",
    },
    {
        "id": "touchstone-dash",
        "name": "Touchstone Dashboard",
        "desc": "Attribution dashboard — 5 models, charts",
        "port": 3200,
        "url": f"http://{LAN_IP}:3200",
        "health": "/",
        "category": "business",
    },
    {
        "id": "writer",
        "name": "CK Writer",
        "desc": "8-mode writing studio",
        "port": 5004,
        "url": f"http://{LAN_IP}:5004",
        "health": "/",
        "category": "creative",
    },
    {
        "id": "author-studio",
        "name": "Author Studio",
        "desc": "Book authoring and publishing",
        "port": 5007,
        "url": f"http://{LAN_IP}:5007",
        "health": "/",
        "category": "creative",
    },
    {
        "id": "peterman",
        "name": "Peterman",
        "desc": "Brand intelligence — SEO, authority, presence",
        "port": 5008,
        "url": f"http://{LAN_IP}:5008",
        "health": "/api/health",
        "category": "business",
    },
    {
        "id": "genie",
        "name": "Genie",
        "desc": "AI bookkeeper — receipts, transactions, fraud guard",
        "port": 8000,
        "url": f"http://{LAN_IP}:8000",
        "health": "/api/health",
        "category": "finance",
    },
    {
        "id": "costanza",
        "name": "Costanza",
        "desc": "Mental models engine — 166 frameworks",
        "port": 5001,
        "url": f"http://{LAN_IP}:5001",
        "health": "/api/health",
        "category": "intelligence",
    },
    {
        "id": "learning",
        "name": "Learning Assistant",
        "desc": "Micro-skill training sessions",
        "port": 5002,
        "url": f"http://{LAN_IP}:5002",
        "health": "/api/health",
        "category": "learning",
    },
    {
        "id": "n8n",
        "name": "n8n",
        "desc": "Workflow automation backbone",
        "port": 5678,
        "url": f"http://{LAN_IP}:5678",
        "health": "/",
        "category": "infra",
    },
    {
        "id": "signal",
        "name": "Signal Hunter",
        "desc": "LinkedIn intelligence -- profile tracking, engagement analysis",
        "port": 8420,
        "url": f"http://{LAN_IP}:8420",
        "health": "/api/health",
        "category": "intelligence",
    },
    {
        "id": "junk-drawer",
        "name": "Junk Drawer",
        "desc": "Quick utilities, scratch pad, file management",
        "port": 3005,
        "url": f"http://{LAN_IP}:3005",
        "health": "/",
        "category": "core",
    },
    {
        "id": "junk-drawer-api",
        "name": "Junk Drawer API",
        "desc": "Junk Drawer backend — file operations, search",
        "port": 5005,
        "url": f"http://{LAN_IP}:5005",
        "health": "/api/health",
        "category": "core",
    },
]

# ── System Prompt for Claude CLI ───────────────────────────────

SYSTEM_PROMPT = """You are ELAINE, an AI Chief of Staff for Mani Padisetti at Almost Magic Tech Lab.
You are warm, witty, competent, and occasionally channel Seinfeld references.
You help manage his ecosystem of apps, schedule, priorities, and strategic thinking.
You speak in Australian English. You call him 'Mani' not 'Mr Padisetti'.
Direct, no waffle. Under 150 words unless asked for detail.
You have 16 intelligence modules: Gravity (priorities), Constellation (people), Cartographer (markets), Amplifier (content), Sentinel (quality), Chronicle (meetings), Innovator (opportunities), Learning Radar, Gatekeeper, Compassion, plus Thinking/Communication/Strategic frameworks.
Key AMTL tools: Workshop (:5003), Genie (:8000), CK Writer (:5004), Ripple CRM (:3100/:8100), Costanza (:5001), Learning Assistant (:5002), Peterman (:5008), Junk Drawer (:3005/:5005), Supervisor (:9000).
Reference Gravity for priorities, Constellation for people, Amplifier+Sentinel for content."""

# Patterns that indicate a thinking/strategy question
import re
_THINKING_PATTERNS = re.compile(
    r"(help me think|think through|what framework|should i|which approach|"
    r"analyse this|analyze this|pros and cons|first principles|"
    r"strategic|decision|trade.?off|weigh up|evaluate)",
    re.IGNORECASE,
)


def _ping_service(tool):
    """Ping a single tool's health endpoint. Returns (tool_id, status, latency_ms)."""
    url = f"http://localhost:{tool['port']}{tool['health']}"
    try:
        req = urllib.request.Request(url, method="GET")
        import time
        start = time.time()
        with urllib.request.urlopen(req, timeout=2) as resp:
            latency = int((time.time() - start) * 1000)
            if resp.status < 400:
                return (tool["id"], "running", latency)
    except Exception:
        pass
    return (tool["id"], "stopped", None)


def create_chat_routes():
    bp = Blueprint("chat", __name__)

    # ── POST /api/chat ────────────────────────────────────────────

    @bp.route("/api/chat", methods=["POST"])
    def chat():
        """
        Send a message to ELAINE. Uses Claude CLI as the only AI engine.
        Body: {"message": "...", "history": [...]}
        Thinking questions are auto-routed to Costanza/ThinkingFrameworksEngine.
        """
        from utils.ai_engine import query_ai
        import time as _time

        data = request.get_json(silent=True) or {}
        message = data.get("message", "").strip()
        if not message:
            return jsonify({"error": "message is required"}), 400

        history = data.get("history", [])
        start = _time.time()

        # Check if this is a thinking/strategy question → route to Costanza
        costanza_used = False
        costanza_prefix = ""
        if _THINKING_PATTERNS.search(message):
            try:
                from modules.thinking.engine import ThinkingFrameworksEngine
                tfe = ThinkingFrameworksEngine()
                analysis = tfe.analyse(message)
                if analysis and analysis.get("analysis"):
                    costanza_used = True
                    source = analysis.get("source", "unknown")
                    costanza_prefix = f"[Thinking analysis via {source}]\n{analysis['analysis']}\n\n[ELAINE's take]\n"
            except Exception as exc:
                logger.warning("Costanza routing failed: %s", exc)

        # Build conversation context
        context_lines = []
        for h in history[-10:]:
            role = h.get("role", "user")
            content = h.get("content", "")
            context_lines.append(f"{role}: {content}")
        context_lines.append(f"user: {message}")

        user_prompt = "\n".join(context_lines)
        if costanza_prefix:
            user_prompt = f"{costanza_prefix}Now respond to Mani as ELAINE, incorporating the analysis above:\n\n{user_prompt}"

        result = query_ai(SYSTEM_PROMPT, user_prompt, timeout=CHAT_TIMEOUT)

        if result:
            reply = result["text"]
            elapsed = round(_time.time() - start, 1)
            logger.info("Chat reply via %s in %ss (costanza=%s)", result["engine"], elapsed, costanza_used)
            return jsonify({
                "reply": reply,
                "via": result["engine"],
                "costanza_used": costanza_used,
                "elapsed_s": elapsed,
            })

        # All engines failed — NEVER tell user to open anything
        elapsed = round(_time.time() - start, 1)
        return jsonify({
            "error": "No AI engine available",
            "reply": "I can't reach any AI engine right now. Claude CLI and Ollama are both offline.",
            "via": "offline",
            "costanza_used": False,
            "elapsed_s": elapsed,
        }), 503

    # ── GET /api/tools ────────────────────────────────────────────

    @bp.route("/api/tools", methods=["GET"])
    def tools():
        """Return the AMTL tool registry."""
        return jsonify({
            "tools": TOOLS,
            "total": len(TOOLS),
            "lan_ip": LAN_IP,
        })

    # ── GET /api/tools/health ─────────────────────────────────────

    @bp.route("/api/tools/health", methods=["GET"])
    def tools_health():
        """Ping all tools and return health status."""
        results = {}
        running = 0

        with ThreadPoolExecutor(max_workers=10) as pool:
            futures = {pool.submit(_ping_service, t): t for t in TOOLS}
            for future in as_completed(futures):
                tool_id, status, latency = future.result()
                results[tool_id] = {
                    "status": status,
                    "latency_ms": latency,
                }
                if status == "running":
                    running += 1

        return jsonify({
            "services": results,
            "running": running,
            "total": len(TOOLS),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    # ── POST /api/stt ────────────────────────────────────────────

    @bp.route("/api/stt", methods=["POST"])
    def stt():
        """Transcribe audio to text via faster-whisper (local, no API key).
        Accepts multipart/form-data with 'audio' file field (webm/wav/ogg).
        Returns: {"text": "...", "language": "en", "elapsed_s": 0.5}"""
        if "audio" not in request.files:
            return jsonify({"error": "audio file required"}), 400

        audio_file = request.files["audio"]

        import tempfile
        import time as _time

        start = _time.time()

        # Determine file extension from content type
        ct = audio_file.content_type or ""
        ext = ".webm" if "webm" in ct else ".ogg" if "ogg" in ct else ".wav"

        # Save to temp file (faster-whisper needs a file path)
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                audio_file.save(tmp)
                tmp_path = tmp.name

            model = _get_whisper()
            segments, info = model.transcribe(tmp_path, language="en")
            text = " ".join(seg.text for seg in segments).strip()

            elapsed = round(_time.time() - start, 2)
            logger.info("STT: '%s' (%.2fs, lang=%s)", text[:80], elapsed, info.language)
            return jsonify({
                "text": text,
                "language": info.language,
                "elapsed_s": elapsed,
            })

        except ImportError:
            return jsonify({
                "error": "faster-whisper not installed. Run: pip install faster-whisper",
            }), 503
        except Exception as e:
            logger.warning("STT failed: %s", e)
            return jsonify({"error": f"Transcription failed: {e}"}), 500
        finally:
            if tmp_path:
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

    # ── GET /api/tts/status ───────────────────────────────────────

    @bp.route("/api/tts/status", methods=["GET"])
    def tts_status():
        """Report voice capability — is ElevenLabs configured?"""
        from utils.voice_engine import get_voice_status
        return jsonify(get_voice_status())

    # ── POST /api/tts ───────────────────────────────────────────────

    @bp.route("/api/tts", methods=["POST"])
    def tts():
        """Convert text to speech. Uses voice engine with fallback chain.
        Body: {"text": "..."} — max 500 chars for chat responses.
        Returns audio/mpeg or audio/wav depending on engine."""
        from utils.voice_engine import speak

        data = request.get_json(silent=True) or {}
        text = data.get("text", "").strip()
        if not text:
            return jsonify({"error": "text is required"}), 400

        # Cap length for chat — don't burn API credits on essays
        if len(text) > 500:
            text = text[:500] + "... that's the gist of it."

        audio = speak(text)
        if audio:
            return Response(audio, mimetype="audio/mpeg")

        return jsonify({
            "error": "All TTS engines failed",
            "detail": "ElevenLabs key may not be set. Check .env file.",
        }), 503

    # ── POST /api/voice/speak ────────────────────────────────────────

    @bp.route("/api/voice/speak", methods=["POST"])
    def voice_speak():
        """TTS via voice engine. Body: {"text": "..."}. Returns audio/mpeg."""
        from utils.voice_engine import speak

        data = request.get_json(silent=True) or {}
        text = data.get("text", "").strip()
        if not text:
            return jsonify({"error": "text is required"}), 400

        audio = speak(text)
        if audio:
            return Response(audio, mimetype="audio/mpeg")

        return jsonify({
            "error": "All TTS engines failed",
            "detail": "Check ELEVENLABS_API_KEY in .env",
        }), 503

    # ── GET /api/voice/engine-status ─────────────────────────────────

    @bp.route("/api/voice/engine-status", methods=["GET"])
    def voice_engine_status():
        """Voice engine status with connectivity check."""
        from utils.voice_engine import get_voice_status
        return jsonify(get_voice_status())

    return bp


