"""
Peterman V4.1 — Ollama Service
Almost Magic Tech Lab

Handles all local LLM calls via Supervisor → Ollama.
Routes through Supervisor on port 9000 (GPU scheduling, model management).
Primary model: gemma2:27b (reasoning)
Embed model: nomic-embed-text (embeddings)
"""
import httpx
import json
import logging
from flask import current_app

logger = logging.getLogger(__name__)


class OllamaService:
    """Interface to Ollama for local LLM inference."""

    def __init__(self, base_url=None):
        self.base_url = base_url or "http://localhost:9000"

    def _get_url(self, endpoint):
        return f"{self.base_url}{endpoint}"

    # ----------------------------------------------------------
    # Core Generation
    # ----------------------------------------------------------

    def generate(self, prompt, model=None, system=None, temperature=0.3, max_tokens=2048):
        """Generate a completion from Ollama."""
        model = model or current_app.config.get("OLLAMA_PRIMARY_MODEL", "llama3.1:70b-instruct-q4_0")

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }
        if system:
            payload["system"] = system

        try:
            with httpx.Client(timeout=300.0) as client:  # 5 min timeout for 70B
                response = client.post(self._get_url("/api/generate"), json=payload)
                response.raise_for_status()
                result = response.json()
                return {
                    "text": result.get("response", ""),
                    "model": model,
                    "tokens_used": result.get("eval_count", 0),
                    "duration_ms": result.get("total_duration", 0) / 1_000_000,  # ns to ms
                    "cost": 0.0,  # local = free
                }
        except httpx.TimeoutException:
            logger.error(f"Ollama timeout for model {model}")
            return {"text": "", "model": model, "error": "timeout", "tokens_used": 0, "cost": 0.0}
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return {"text": "", "model": model, "error": str(e), "tokens_used": 0, "cost": 0.0}

    def generate_fast(self, prompt, system=None, temperature=0.3):
        """Generate using the fast model (gemma2:27b)."""
        model = current_app.config.get("OLLAMA_FAST_MODEL", "gemma2:27b")
        return self.generate(prompt, model=model, system=system, temperature=temperature)

    # ----------------------------------------------------------
    # Chat (multi-turn)
    # ----------------------------------------------------------

    def chat(self, messages, model=None, temperature=0.3):
        """Multi-turn chat with Ollama."""
        model = model or current_app.config.get("OLLAMA_PRIMARY_MODEL", "llama3.1:70b-instruct-q4_0")

        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
            }
        }

        try:
            with httpx.Client(timeout=300.0) as client:
                response = client.post(self._get_url("/api/chat"), json=payload)
                response.raise_for_status()
                result = response.json()
                return {
                    "text": result.get("message", {}).get("content", ""),
                    "model": model,
                    "tokens_used": result.get("eval_count", 0),
                    "cost": 0.0,
                }
        except Exception as e:
            logger.error(f"Ollama chat error: {e}")
            return {"text": "", "model": model, "error": str(e), "tokens_used": 0, "cost": 0.0}

    # ----------------------------------------------------------
    # Embeddings
    # ----------------------------------------------------------

    def embed(self, text, model=None):
        """Generate embedding vector for text."""
        model = model or current_app.config.get("OLLAMA_EMBED_MODEL", "nomic-embed-text")

        payload = {
            "model": model,
            "input": text,
        }

        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(self._get_url("/api/embed"), json=payload)
                response.raise_for_status()
                result = response.json()
                embeddings = result.get("embeddings", [[]])
                return {
                    "embedding": embeddings[0] if embeddings else [],
                    "model": model,
                    "dimensions": len(embeddings[0]) if embeddings else 0,
                    "cost": 0.0,
                }
        except Exception as e:
            logger.error(f"Ollama embed error: {e}")
            return {"embedding": [], "model": model, "error": str(e), "cost": 0.0}

    def embed_batch(self, texts, model=None):
        """Generate embeddings for multiple texts."""
        results = []
        for text in texts:
            result = self.embed(text, model=model)
            results.append(result)
        return results

    # ----------------------------------------------------------
    # Structured Output (JSON)
    # ----------------------------------------------------------

    def generate_json(self, prompt, model=None, system=None):
        """Generate structured JSON output."""
        system = system or "You are a precise analytical assistant. Always respond with valid JSON only. No markdown, no explanation, just JSON."
        prompt = f"{prompt}\n\nRespond with valid JSON only."

        result = self.generate(prompt, model=model, system=system, temperature=0.1)

        if result.get("error"):
            return result

        # Try to parse JSON from response
        text = result["text"].strip()
        # Remove markdown code fences if present
        if text.startswith("```"):
            text = text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

        try:
            parsed = json.loads(text)
            result["parsed"] = parsed
        except json.JSONDecodeError:
            result["parsed"] = None
            result["parse_error"] = "Failed to parse JSON from response"

        return result

    # ----------------------------------------------------------
    # Health Check
    # ----------------------------------------------------------

    def health_check(self):
        """Check if Ollama is running and models are available."""
        try:
            with httpx.Client(timeout=5.0) as client:
                # Check Ollama is running
                response = client.get(self._get_url("/api/tags"))
                response.raise_for_status()
                models = response.json().get("models", [])
                model_names = [m["name"] for m in models]

                return {
                    "status": "ok",
                    "models_available": model_names,
                    "model_count": len(models),
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "models_available": [],
            }


# Singleton
ollama = OllamaService()
