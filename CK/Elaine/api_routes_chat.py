"""
Elaine v4 — Chat + Tool Registry + Service Health Routes
Connects to Ollama via The Supervisor (:9000).
Ollama only — no cloud APIs.

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
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
CHAT_MODEL = os.environ.get("ELAINE_CHAT_MODEL", "llama3.2:3b")
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
        "health": "/",
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
        "id": "ollama",
        "name": "Ollama",
        "desc": "Local LLM inference engine",
        "port": 11434,
        "url": f"http://{LAN_IP}:11434",
        "health": "/api/tags",
        "category": "infra",
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
]

# ── System Prompt for Ollama ────────────────────────────────────

SYSTEM_PROMPT = """You are Elaine, Chief of Staff for Mani Padisetti at Almost Magic Tech Lab.
Australian English. Direct, warm, no waffle. Under 150 words unless asked for detail.
You have 16 intelligence modules: Gravity (priorities), Constellation (people), Cartographer (markets), Amplifier (content), Sentinel (quality), Chronicle (meetings), Innovator (opportunities), Learning Radar, Gatekeeper, Compassion, plus Thinking/Communication/Strategic frameworks.
Key AMTL tools: Workshop (:5003), Genie (:8000), CK Writer (:5004), Ripple CRM (:3100/:8100), Supervisor (:9000), Ollama (:11434).
Reference Gravity for priorities, Constellation for people, Amplifier+Sentinel for content."""


def _ping_service(tool):
    """Ping a single tool's health endpoint. Returns (tool_id, status, latency_ms)."""
    url = f"http://localhost:{tool['port']}{tool['health']}"
    try:
        req = urllib.request.Request(url, method="GET")
        import time
        start = time.time()
        with urllib.request.urlopen(req, timeout=3) as resp:
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
        Send a message to Ollama via The Supervisor.
        Body: {"message": "...", "model": "llama3.2:3b"}
        """
        data = request.get_json(silent=True) or {}
        message = data.get("message", "").strip()
        if not message:
            return jsonify({"error": "message is required"}), 400

        model = data.get("model", CHAT_MODEL)
        history = data.get("history", [])

        # Build messages array for Ollama chat API
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for h in history[-10:]:  # Keep last 10 turns to fit context
            messages.append(h)
        messages.append({"role": "user", "content": message})

        # Build payload — cap response length for snappy chat
        payload = json.dumps({
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"num_predict": CHAT_MAX_TOKENS},
        }).encode("utf-8")

        # Route through Supervisor first (manages VRAM + model loading),
        # fall back to Ollama direct only if Supervisor is down.
        targets = [
            (f"{SUPERVISOR_URL}/api/chat", "supervisor"),
            (f"{OLLAMA_URL}/api/chat", "ollama-direct"),
        ]

        import time as _time
        start = _time.time()
        last_error = ""

        for url, via in targets:
            try:
                req = urllib.request.Request(
                    url,
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=CHAT_TIMEOUT) as resp:
                    result = json.loads(resp.read().decode("utf-8"))

                reply = ""
                if "message" in result:
                    reply = result["message"].get("content", "")
                elif "response" in result:
                    reply = result["response"]

                elapsed = round(_time.time() - start, 1)
                logger.info("Chat reply via %s in %ss (%s)", via, elapsed, model)
                return jsonify({
                    "reply": reply,
                    "model": model,
                    "via": via,
                    "elapsed_s": elapsed,
                })
            except Exception as e:
                last_error = str(e)
                logger.warning("Chat via %s failed: %s", via, last_error)
                continue

        # All targets failed
        elapsed = round(_time.time() - start, 1)
        if "timed out" in last_error.lower() or "timeout" in last_error.lower():
            return jsonify({
                "reply": "Still warming up — try again in a moment.",
                "model": model,
                "via": "warming-up",
                "elapsed_s": elapsed,
            })

        return jsonify({
            "error": "Cannot reach Ollama",
            "reply": "I can't reach Ollama right now. Check that Ollama (:11434) or The Supervisor (:9000) is running.",
            "via": "offline",
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
        has_key = bool(ELEVENLABS_API_KEY)
        return jsonify({
            "elevenlabs": has_key,
            "voice_id": ELEVENLABS_VOICE_ID if has_key else None,
            "model": ELEVENLABS_MODEL if has_key else None,
            "fallback": "browser-tts",
            "setup": None if has_key else (
                "Set ELEVENLABS_API_KEY environment variable or add it to CK/Elaine/.env. "
                "Get your key from https://elevenlabs.io/app/settings/api-keys"
            ),
        })

    # ── POST /api/tts ───────────────────────────────────────────────

    @bp.route("/api/tts", methods=["POST"])
    def tts():
        """Convert text to speech via ElevenLabs. Returns audio/mpeg.
        Body: {"text": "..."} — max 500 chars for chat responses.
        Falls back to 503 if no API key configured."""
        if not ELEVENLABS_API_KEY:
            return jsonify({
                "error": "ElevenLabs API key not configured",
                "setup": "Set ELEVENLABS_API_KEY env var. Get key: https://elevenlabs.io/app/settings/api-keys",
            }), 503

        data = request.get_json(silent=True) or {}
        text = data.get("text", "").strip()
        if not text:
            return jsonify({"error": "text is required"}), 400

        # Cap length for chat — don't burn API credits on essays
        if len(text) > 500:
            text = text[:500] + "... that's the gist of it."

        try:
            payload = json.dumps({
                "text": text,
                "model_id": ELEVENLABS_MODEL,
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0.3,
                },
            }).encode("utf-8")

            url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
            req = urllib.request.Request(
                url,
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "xi-api-key": ELEVENLABS_API_KEY,
                    "Accept": "audio/mpeg",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=TTS_TIMEOUT) as resp:
                audio_data = resp.read()
                logger.info("ElevenLabs TTS: %d bytes for %d chars", len(audio_data), len(text))
                return Response(audio_data, mimetype="audio/mpeg")

        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            logger.warning("ElevenLabs HTTP %d: %s", e.code, body[:200])
            return jsonify({"error": f"ElevenLabs error: HTTP {e.code}", "detail": body[:200]}), 502
        except Exception as e:
            logger.warning("ElevenLabs TTS failed: %s", e)
            return jsonify({"error": f"TTS failed: {e}"}), 502

    return bp


def prewarm_chat_model():
    """Send a tiny prompt to Ollama via Supervisor to pre-load the chat model into VRAM.
    Run in a background thread on startup so it doesn't block Flask."""
    import threading

    def _warm():
        logger.info("Pre-warming chat model %s via Supervisor...", CHAT_MODEL)
        payload = json.dumps({
            "model": CHAT_MODEL,
            "messages": [{"role": "user", "content": "hi"}],
            "stream": False,
            "options": {"num_predict": 5},
        }).encode("utf-8")
        targets = [
            f"{SUPERVISOR_URL}/api/chat",
            f"{OLLAMA_URL}/api/chat",
        ]
        for url in targets:
            try:
                req = urllib.request.Request(
                    url,
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=60) as resp:
                    resp.read()
                logger.info("Chat model %s pre-warmed via %s", CHAT_MODEL, url)
                return
            except Exception as e:
                logger.warning("Pre-warm via %s failed: %s", url, e)
                continue
        logger.warning("Could not pre-warm chat model %s -- first message will be slow", CHAT_MODEL)

    t = threading.Thread(target=_warm, daemon=True, name="chat-prewarm")
    t.start()
