"""
ELAINE Voice Engine — ElevenLabs is PRIMARY (non-negotiable).
Fallback chain: ElevenLabs -> pyttsx3 (last resort)

Voice identity:
  - Provider: ElevenLabs
  - voice_id: XQanfahzbl1YiUlZi5NW
  - Description: Custom Australian female voice
  - This is Elaine's voice. Do NOT change.

Almost Magic Tech Lab
"""

import logging
import os

logger = logging.getLogger("elaine.voice_engine")

ELAINE_VOICE_ID = "XQanfahzbl1YiUlZi5NW"
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
ELEVENLABS_MODEL = os.environ.get("ELEVENLABS_MODEL", "eleven_flash_v2_5")

try:
    import requests as _requests
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False


def speak(text: str, voice_id: str = None, model: str = None) -> bytes | None:
    """
    Generate speech audio. Returns MP3 bytes or None.
    Priority: ElevenLabs (PRIMARY) -> pyttsx3 (last resort)
    """
    voice_id = voice_id or ELAINE_VOICE_ID
    model = model or ELEVENLABS_MODEL

    # 1. Try ElevenLabs (PRIMARY — this is Elaine's real voice)
    audio = _try_elevenlabs(text, voice_id, model)
    if audio:
        return audio

    # 2. Last resort: pyttsx3 (offline, robotic but functional)
    audio = _try_pyttsx3(text)
    if audio:
        return audio

    logger.error("All TTS engines failed")
    return None


def _try_elevenlabs(text: str, voice_id: str, model: str) -> bytes | None:
    """ElevenLabs TTS — Elaine's REAL voice."""
    if not ELEVENLABS_API_KEY or ELEVENLABS_API_KEY.startswith("sk_your_"):
        logger.warning("ELEVENLABS_API_KEY not set or is placeholder — skipping ElevenLabs")
        return None

    if not _HAS_REQUESTS:
        logger.warning("requests library not available for ElevenLabs")
        return None

    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY,
        }
        payload = {
            "text": text,
            "model_id": model,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.3,
                "use_speaker_boost": True,
            },
        }
        resp = _requests.post(url, json=payload, headers=headers, timeout=30)
        if resp.status_code == 200:
            logger.info("TTS: ElevenLabs (Elaine's voice, %d bytes)", len(resp.content))
            return resp.content
        else:
            logger.warning("ElevenLabs returned %d: %s", resp.status_code, resp.text[:200])
            return None
    except Exception as e:
        logger.warning("ElevenLabs failed: %s", e)
        return None


def _try_pyttsx3(text: str) -> bytes | None:
    """Offline TTS — last resort. Returns WAV bytes."""
    try:
        import pyttsx3
        import tempfile
        engine = pyttsx3.init()
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            tmp_path = f.name
        engine.save_to_file(text, tmp_path)
        engine.runAndWait()
        with open(tmp_path, "rb") as audio_file:
            data = audio_file.read()
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
        if data:
            logger.info("TTS: pyttsx3 (offline fallback, %d bytes)", len(data))
            return data
        return None
    except Exception as e:
        logger.warning("pyttsx3 failed: %s", e)
        return None


def get_voice_status() -> dict:
    """Return current voice engine status."""
    api_key_set = bool(ELEVENLABS_API_KEY) and not ELEVENLABS_API_KEY.startswith("sk_your_")

    status = {
        "primary": "ElevenLabs",
        "voice_id": ELAINE_VOICE_ID,
        "model": ELEVENLABS_MODEL,
        "api_key_set": api_key_set,
        "fallback": "pyttsx3 (offline)",
        "elevenlabs_connected": False,
    }

    if not api_key_set:
        status["warning"] = (
            "ELEVENLABS_API_KEY is not set or is a placeholder. "
            "Set it in CK/Elaine/.env to enable Elaine's real voice. "
            "Get key: https://elevenlabs.io/app/settings/api-keys"
        )
        return status

    # Test ElevenLabs connectivity
    if _HAS_REQUESTS:
        try:
            resp = _requests.get(
                f"https://api.elevenlabs.io/v1/voices/{ELAINE_VOICE_ID}",
                headers={"xi-api-key": ELEVENLABS_API_KEY},
                timeout=2,
            )
            status["elevenlabs_connected"] = resp.status_code == 200
            if resp.status_code == 200:
                voice_data = resp.json()
                status["voice_name"] = voice_data.get("name", "Unknown")
        except Exception:
            status["elevenlabs_connected"] = False

    return status
