"""
ELAINE AI Engine — Claude CLI + Ollama fallback.
Shared utility for all modules that need AI inference.

Priority: Claude CLI (primary) -> Ollama via Supervisor (fallback) -> None
ELAINE handles AI routing SILENTLY. She never asks the user to open anything.
"""

import json
import logging
import os
import shutil
import subprocess

logger = logging.getLogger("elaine.ai_engine")

SUPERVISOR_URL = os.environ.get("SUPERVISOR_URL", "http://localhost:9000")
OLLAMA_MODEL = os.environ.get("ELAINE_CHAT_MODEL", "llama3.2:3b")

try:
    import requests as _requests
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False


def _is_claude_cli_available() -> bool:
    """Check if Claude CLI is installed and responsive."""
    if not shutil.which("claude"):
        return False
    try:
        result = subprocess.run(
            ["claude", "--version"],
            capture_output=True, text=True, timeout=5,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False


def _is_ollama_available() -> bool:
    """Check if Ollama is reachable (via Supervisor or direct)."""
    if not _HAS_REQUESTS:
        return False
    for url in [f"{SUPERVISOR_URL}/api/tags", "http://localhost:11434/api/tags"]:
        try:
            resp = _requests.get(url, timeout=2)
            if resp.status_code == 200:
                return True
        except Exception:
            continue
    return False


def _try_claude_cli(system_prompt: str, user_prompt: str, timeout: int) -> dict | None:
    """Use Claude CLI (claude -p). Returns {"text": ..., "engine": ...} or None."""
    if not shutil.which("claude"):
        logger.debug("Claude CLI not found in PATH")
        return None

    try:
        combined = f"{system_prompt}\n\n{user_prompt}" if system_prompt else user_prompt
        result = subprocess.run(
            ["claude", "-p", combined],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode == 0 and result.stdout.strip():
            logger.info("AI response via Claude CLI (%d chars)", len(result.stdout.strip()))
            return {"text": result.stdout.strip(), "engine": "claude-cli"}
        logger.warning("Claude CLI failed (rc=%d)", result.returncode)
    except subprocess.TimeoutExpired:
        logger.warning("Claude CLI timed out after %ds", timeout)
    except Exception as exc:
        logger.warning("Claude CLI call failed: %s", exc)

    return None


def _try_ollama(system_prompt: str, user_prompt: str, timeout: int) -> dict | None:
    """Use Ollama via Supervisor (port 9000) or direct (port 11434)."""
    if not _HAS_REQUESTS:
        return None

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    # Try Supervisor first (as per AMTL rules), then direct Ollama
    urls = [
        f"{SUPERVISOR_URL}/api/chat",
        "http://localhost:11434/api/chat",
    ]

    for url in urls:
        try:
            resp = _requests.post(
                url,
                json={
                    "model": OLLAMA_MODEL,
                    "messages": messages,
                    "stream": False,
                },
                timeout=timeout,
            )
            if resp.status_code == 200:
                data = resp.json()
                text = data.get("message", {}).get("content", "")
                if not text:
                    # Fallback for /api/generate format
                    text = data.get("response", "")
                if text:
                    logger.info("AI response via Ollama (%d chars)", len(text))
                    return {"text": text, "engine": "ollama"}
        except Exception as exc:
            logger.debug("Ollama at %s failed: %s", url, exc)
            continue

    return None


def query_ai(system_prompt: str, user_prompt: str, timeout: int = 60) -> dict | None:
    """
    Query AI engine. Returns {"text": "...", "engine": "..."} or None.
    Priority: Claude CLI -> Ollama -> None (never asks user to open anything)
    """
    # 1. Claude CLI (primary)
    result = _try_claude_cli(system_prompt, user_prompt, timeout)
    if result:
        return result

    # 2. Ollama (fallback)
    result = _try_ollama(system_prompt, user_prompt, timeout)
    if result:
        return result

    # 3. No AI available — return None, let caller handle gracefully
    logger.error("No AI engine available (Claude CLI and Ollama both failed)")
    return None


def query_ai_json(system_prompt: str, user_prompt: str, timeout: int = 60) -> dict | None:
    """Like query_ai but attempts to parse the response as JSON.
    Returns the parsed dict on success, or None."""
    result = query_ai(system_prompt, user_prompt, timeout)
    if not result:
        return None

    text = result["text"]
    # Try to extract JSON from the response (handle markdown code blocks)
    if "```json" in text:
        text = text.split("```json", 1)[1].split("```", 1)[0].strip()
    elif "```" in text:
        text = text.split("```", 1)[1].split("```", 1)[0].strip()

    try:
        parsed = json.loads(text)
        parsed["_engine"] = result["engine"]
        return parsed
    except (json.JSONDecodeError, ValueError):
        # Return raw text wrapped in a dict
        return {"_raw": result["text"], "_engine": result["engine"]}


def check_ai_status() -> dict:
    """Check AI engine availability. ELAINE handles this silently."""
    claude_available = _is_claude_cli_available()
    ollama_available = _is_ollama_available()

    status = {
        "claude_cli": claude_available,
        "claude_cli_version": None,
        "ollama": ollama_available,
        "ollama_model": OLLAMA_MODEL,
        "active_engine": "claude-cli" if claude_available else ("ollama" if ollama_available else "none"),
        "status": "ready" if (claude_available or ollama_available) else "no_ai_available",
    }

    # Get Claude CLI version if available
    if claude_available:
        try:
            r = subprocess.run(
                ["claude", "--version"],
                capture_output=True, text=True, timeout=5,
            )
            if r.returncode == 0:
                status["claude_cli_version"] = r.stdout.strip().split("\n")[0]
        except Exception:
            pass

    return status
