"""
AI Engine for Peterman.

Claude CLI primary with Ollama fallback per DEC-003.
ZERO cloud API costs - uses desktop subscriptions only.
"""

import logging
import subprocess
from typing import Optional
import json

import httpx

from app.config import config

logger = logging.getLogger(__name__)

# AI Engine priority chain per DEC-003
AI_ENGINE_CHAIN = [
    {'name': 'claude_cli', 'priority': 1, 'type': 'cli', 'reasoning': True},
    {'name': 'manus_desktop', 'priority': 2, 'type': 'manual', 'reasoning': True},
    {'name': 'perplexity_desktop', 'priority': 3, 'type': 'manual', 'reasoning': True},
    {'name': 'deepseek_desktop', 'priority': 4, 'type': 'manual', 'reasoning': True},
    {'name': 'ollama', 'priority': 5, 'type': 'http', 'reasoning': True},
]


def call_claude_cli(prompt: str, system_prompt: Optional[str] = None, timeout: int = 120) -> str:
    """Call Claude CLI for reasoning. Zero API cost - uses Max subscription."""
    # Combine system prompt with main prompt if provided
    full_prompt = prompt
    if system_prompt:
        full_prompt = f"{system_prompt}\n\n---\n\n{prompt}"
    
    cmd = ['claude', '-p', full_prompt]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            error_msg = result.stderr or "Unknown Claude CLI error"
            logger.error(f"Claude CLI error: {error_msg}")
            raise Exception(f"Claude CLI error: {error_msg}")
            
    except FileNotFoundError:
        raise Exception("Claude CLI not installed")
    except subprocess.TimeoutExpired:
        raise Exception("Claude CLI timed out")
    except Exception as e:
        raise Exception(f"Claude CLI failed: {str(e)}")


def call_ollama(prompt: str, system_prompt: Optional[str] = None, 
                model: str = 'llama3.1:8b', timeout: int = 120) -> str:
    """Call Ollama via Supervisor for reasoning (last resort)."""
    ollama_url = config['OLLAMA_URL']
    messages = []
    if system_prompt:
        messages.append({'role': 'system', 'content': system_prompt})
    messages.append({'role': 'user', 'content': prompt})
    
    payload = {
        'model': model,
        'messages': messages,
        'temperature': 0.0,
        'options': {'num_predict': 2000}
    }
    
    try:
        with httpx.Client(timeout=float(timeout)) as client:
            response = client.post(f"{ollama_url}/api/chat", json=payload)
            response.raise_for_status()
            return response.json()['message']['content']
    except Exception as e:
        logger.error(f"Ollama call failed: {e}")
        raise


def get_embedding(text: str) -> list:
    """Get embeddings from Ollama nomic-embed-text."""
    ollama_url = config['OLLAMA_URL']
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{ollama_url}/api/embeddings",
                json={'model': 'nomic-embed-text', 'prompt': text}
            )
            response.raise_for_status()
            return response.json()['embedding']
    except Exception as e:
        logger.error(f"Embedding failed: {e}")
        raise


def cosine_similarity(a: list, b: list) -> float:
    """Compute cosine similarity between two vectors."""
    import math
    
    dot_product = sum(x * y for x, y in zip(a, b))
    magnitude_a = math.sqrt(sum(x * x for x in a))
    magnitude_b = math.sqrt(sum(x * x for x in b))
    
    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0
    
    return dot_product / (magnitude_a * magnitude_b)


class AIEngine:
    """Cascading AI engine. ZERO cloud API costs per DEC-003, DEC-004."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def reason(self, prompt: str, system_prompt: Optional[str] = None):
        """Try Claude CLI first, then Ollama as last resort."""
        # Priority 1: Claude CLI
        try:
            result = call_claude_cli(prompt, system_prompt)
            self.logger.info("Claude CLI succeeded")
            return {'engine': 'claude_cli', 'response': result, 'success': True}
        except Exception as e:
            self.logger.warning(f"Claude CLI failed: {e}")
        
        # Priority 5: Ollama (last resort for reasoning)
        try:
            result = call_ollama(prompt, system_prompt)
            self.logger.info("Ollama succeeded")
            return {'engine': 'ollama', 'response': result, 'success': True}
        except Exception as e:
            self.logger.warning(f"Ollama failed: {e}")
        
        return {'engine': None, 'response': 'All AI engines unavailable', 'success': False}
    
    def embed(self, text: str) -> list:
        """Embeddings ALWAYS via Ollama."""
        return get_embedding(text)


def query_ai(prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.0, max_tokens: int = 2000):
    """Query AI engine with automatic fallback."""
    engine = AIEngine()
    result = engine.reason(prompt, system_prompt)
    
    return {
        'text': result['response'],
        'provider': result['engine'],
        'fallback_used': result['engine'] == 'ollama'
    }
