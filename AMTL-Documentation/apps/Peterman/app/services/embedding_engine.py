"""
Embedding engine for Peterman.

nomic-embed-text via Ollama through Supervisor per DEC-004.
"""

import logging
import json
from uuid import UUID
from typing import list, dict

import httpx

from app.config import config
from app.models.database import get_session
from app.models.embedding import DomainEmbedding

logger = logging.getLogger(__name__)

EMBEDDING_MODEL = 'nomic-embed-text'
OLLAMA_EMBED_URL = f"{config['OLLAMA_URL']}/api/embed"
OLLAMA_DIMENSION = 768


def get_embedding(text: str) -> list:
    """Get embedding for a single text using nomic-embed-text."""
    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                OLLAMA_EMBED_URL,
                json={'model': EMBEDDING_MODEL, 'text': text}
            )
            response.raise_for_status()
            data = response.json()
            return data['embeddings'][0]
    except Exception as e:
        logger.error(f"Embedding failed: {e}")
        raise


def get_embeddings_batch(texts: list) -> list:
    """Get embeddings for multiple texts."""
    try:
        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                OLLAMA_EMBED_URL,
                json={'model': EMBEDDING_MODEL, 'texts': texts}
            )
            response.raise_for_status()
            data = response.json()
            return data['embeddings']
    except Exception as e:
        logger.error(f"Batch embedding failed: {e}")
        raise


def embed_and_store(
    domain_id: UUID,
    page_url: str,
    page_title: str,
    content_snippet: str
) -> DomainEmbedding:
    """Embed content and store in database."""
    session = get_session()
    try:
        embedding_vector = get_embedding(content_snippet)
        embedding = DomainEmbedding(
            domain_id=domain_id,
            page_url=page_url,
            page_title=page_title,
            content_snippet=content_snippet,
            embedding=embedding_vector
        )
        session.add(embedding)
        session.commit()
        logger.info(f"Stored embedding for {page_url}")
        return embedding
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to embed and store: {e}")
        raise
    finally:
        session.close()


def find_similar(
    domain_id: UUID,
    query_text: str,
    limit: int = 5
) -> list:
    """Find similar content using cosine similarity."""
    session = get_session()
    try:
        query_embedding = get_embedding(query_text)
        results = (
            session.query(DomainEmbedding)
            .filter(DomainEmbedding.domain_id == domain_id)
            .order_by(DomainEmbedding.embedding.cosine_distance(query_embedding))
            .limit(limit)
            .all()
        )
        return [r.to_dict() for r in results]
    finally:
        session.close()
