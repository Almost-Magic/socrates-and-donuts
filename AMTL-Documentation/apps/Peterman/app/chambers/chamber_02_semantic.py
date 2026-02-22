"""
Chamber 2 — Semantic Gravity

Semantic Gravity Score (SGS) measures how close your domain is to being 
the "default answer" for target topic clusters in LLM vector space.

Per DEC-005: Uses Claude CLI for query generation, Ollama for embeddings.
"""

import logging
import json
import math
from datetime import datetime
from typing import List, Dict, Optional
from uuid import UUID

import httpx
from sqlalchemy import Column, Integer, Float, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.models.database import get_session, Base
from app.models.domain import Domain
from app.config import config

logger = logging.getLogger(__name__)


# Semantic Gravity storage model
class SemanticGravityRecord(Base):
    """Stores SGS measurements over time."""
    __tablename__ = 'semantic_gravity_records'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    domain_id = Column(PGUUID(as_uuid=True), ForeignKey('domains.domain_id'), nullable=False)
    measured_at = Column(DateTime, default=datetime.utcnow)
    sgs_score = Column(Float, nullable=False)  # 0-100
    cluster_count = Column(Integer, default=0)
    avg_similarity = Column(Float, default=0.0)
    drift_delta = Column(Float, default=0.0)  # Change from previous measurement
    cluster_details = Column(JSON)  # Per-cluster similarity scores
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'domain_id': str(self.domain_id),
            'measured_at': self.measured_at.isoformat() if self.measured_at else None,
            'sgs_score': self.sgs_score,
            'cluster_count': self.cluster_count,
            'avg_similarity': self.avg_similarity,
            'drift_delta': self.drift_delta,
            'cluster_details': self.cluster_details,
        }


# Lazy import to avoid circular issues
def _get_ollama_url():
    return config['OLLAMA_URL']

def _get_ai_engine():
    from app.services.ai_engine import AIEngine
    return AIEngine()


def generate_cluster_queries(topic: str, count: int = 50) -> List[str]:
    """Generate representative queries for a topic cluster using Claude CLI."""
    engine = _get_ai_engine()
    
    prompt = f"""Generate {count} diverse search queries about "{topic}". 
Include:
- Direct questions
- Informational queries
- Comparison queries
- How-to queries
- Best/top queries

Respond as JSON array of strings only, no other text."""

    try:
        result = engine.reason(prompt, "You are a keyword research expert. Generate diverse, realistic search queries.")
        if result.get('success'):
            queries = json.loads(result['response'])
            return queries[:count]
    except Exception as e:
        logger.error(f"Query generation failed: {e}")
    
    # Fallback queries
    return [f"{topic}", f"what is {topic}", f"best {topic}", f"{topic} Australia"]


def get_embedding(text: str) -> List[float]:
    """Get embedding using Ollama nomic-embed-text."""
    ollama_url = _get_ollama_url()
    
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


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if not a or not b:
        return 0.0
    
    dot_product = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    
    if mag_a == 0 or mag_b == 0:
        return 0.0
    
    return dot_product / (mag_a * mag_b)


def compute_centroid(embeddings: List[List[float]]) -> List[float]:
    """Compute centroid of multiple embeddings."""
    if not embeddings:
        return []
    
    dim = len(embeddings[0])
    centroid = [0.0] * dim
    
    for emb in embeddings:
        for i, val in enumerate(emb):
            centroid[i] += val
    
    for i in range(dim):
        centroid[i] /= len(embeddings)
    
    return centroid


def compute_sgs(domain_id: UUID) -> Dict:
    """Compute Semantic Gravity Score for a domain.
    
    Steps:
    1. Get approved keywords from domain
    2. Group by category to form topic clusters
    3. Generate 50 queries per cluster
    4. Embed domain content
    5. Embed all queries, compute cluster centroids
    6. Calculate SGS = avg similarity between domain and centroids
    """
    session = get_session()
    
    try:
        # Get domain and crawl data
        domain = session.query(Domain).filter_by(domain_id=domain_id).first()
        if not domain:
            raise ValueError(f"Domain not found: {domain_id}")
        
        crawl_data = domain.crawl_data
        if not crawl_data or not crawl_data.get('homepage', {}).get('text_content'):
            return {
                'status': 'error',
                'message': 'No crawl data available. Run crawl first.',
                'sgs_score': None,
            }
        
        # Get domain content for embedding
        domain_text = crawl_data.get('homepage', {}).get('text_content', '')
        domain_metadata = crawl_data.get('homepage', {}).get('metadata', {})
        
        if not domain_text:
            domain_text = f"{domain_metadata.get('title', '')} {domain_metadata.get('description', '')}"
        
        # Embed domain
        try:
            domain_embedding = get_embedding(domain_text)
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to embed domain: {e}',
                'sgs_score': None,
            }
        
        # Get keywords for topic clusters
        from app.services.keyword_engine import TargetQuery
        keywords = session.query(TargetQuery).filter_by(
            domain_id=domain_id, 
            is_approved=True
        ).all()
        
        if not keywords:
            # Use uncategorized keywords or generate from crawl
            keywords = session.query(TargetQuery).filter_by(domain_id=domain_id).all()
        
        # Group by category
        clusters = {}
        for kw in keywords:
            cat = kw.category or 'brand'
            if cat not in clusters:
                clusters[cat] = []
            clusters[cat].append(kw.query)
        
        # If no keywords, create a single cluster from domain
        if not clusters:
            clusters = {'general': [domain.domain_name]}
        
        # Calculate SGS
        cluster_similarities = []
        cluster_details = {}
        
        for cluster_name, queries in clusters.items():
            # Generate more queries if needed
            if len(queries) < 10:
                topic = queries[0] if queries else cluster_name
                queries = generate_cluster_queries(topic, 50)
            
            # Embed all queries
            query_embeddings = []
            for q in queries[:50]:  # Limit to 50
                try:
                    emb = get_embedding(q)
                    query_embeddings.append(emb)
                except:
                    continue
            
            if query_embeddings:
                # Compute cluster centroid
                centroid = compute_centroid(query_embeddings)
                
                # Similarity between domain and centroid
                sim = cosine_similarity(domain_embedding, centroid)
                cluster_similarities.append(sim)
                cluster_details[cluster_name] = {
                    'queries': len(query_embeddings),
                    'similarity': round(sim, 4),
                }
        
        if not cluster_similarities:
            return {
                'status': 'error',
                'message': 'Failed to compute similarities',
                'sgs_score': None,
            }
        
        # SGS = average similarity * 100
        avg_similarity = sum(cluster_similarities) / len(cluster_similarities)
        sgs_score = round(avg_similarity * 100, 2)
        
        # Get previous measurement for drift
        prev_record = session.query(SemanticGravityRecord).filter_by(
            domain_id=domain_id
        ).order_by(SemanticGravityRecord.measured_at.desc()).first()
        
        drift_delta = 0.0
        if prev_record:
            drift_delta = round(sgs_score - prev_record.sgs_score, 2)
        
        # Save record
        record = SemanticGravityRecord(
            domain_id=domain_id,
            sgs_score=sgs_score,
            cluster_count=len(clusters),
            avg_similarity=avg_similarity,
            drift_delta=drift_delta,
            cluster_details=cluster_details,
        )
        session.add(record)
        session.commit()
        
        return {
            'status': 'ready',
            'sgs_score': sgs_score,
            'cluster_count': len(clusters),
            'avg_similarity': round(avg_similarity, 4),
            'drift_delta': drift_delta,
            'cluster_details': cluster_details,
            'measured_at': datetime.utcnow().isoformat(),
        }
        
    except Exception as e:
        logger.error(f"SGS computation failed: {e}")
        session.rollback()
        return {
            'status': 'error',
            'message': str(e),
            'sgs_score': None,
        }
    finally:
        session.close()


def get_semantic_map_data(domain_id: UUID) -> Dict:
    """Get data for semantic neighbourhood visualisation.
    
    Returns JSON-ready data for D3.js scatter plot.
    """
    session = get_session()
    
    try:
        domain = session.query(Domain).filter_by(domain_id=domain_id).first()
        if not domain:
            raise ValueError(f"Domain not found: {domain_id}")
        
        crawl_data = domain.crawl_data or {}
        domain_text = crawl_data.get('homepage', {}).get('text_content', '')
        
        # Get domain embedding
        domain_emb = None
        if domain_text:
            try:
                domain_emb = get_embedding(domain_text[:5000])  # Limit text length
            except:
                pass
        
        # Get keyword clusters
        from app.services.keyword_engine import TargetQuery
        keywords = session.query(TargetQuery).filter_by(
            domain_id=domain_id
        ).all()
        
        # Group by category
        clusters = {}
        for kw in keywords:
            cat = kw.category or 'brand'
            if cat not in clusters:
                clusters[cat] = []
            clusters[cat].append(kw.query)
        
        # Build map data
        nodes = []
        links = []
        
        # Domain node
        if domain_emb:
            nodes.append({
                'id': 'domain',
                'label': domain.display_name,
                'type': 'domain',
                'embedding': domain_emb[:10],  # First 10 dims for display
                'x': domain_emb[0] if domain_emb else 0,
                'y': domain_emb[1] if len(domain_emb) > 1 else 0,
            })
        
        # Cluster centroids
        for cluster_name, queries in clusters.items():
            # Generate queries and embed
            query_embs = []
            for q in queries[:20]:
                try:
                    emb = get_embedding(q)
                    query_embs.append(emb)
                except:
                    continue
            
            if query_embs:
                centroid = compute_centroid(query_embs)
                nodes.append({
                    'id': f'cluster_{cluster_name}',
                    'label': cluster_name,
                    'type': 'cluster',
                    'query_count': len(query_embs),
                    'x': centroid[0] if centroid else 0,
                    'y': centroid[1] if len(centroid) > 1 else 0,
                })
                links.append({
                    'source': 'domain',
                    'target': f'cluster_{cluster_name}',
                    'type': 'similarity',
                })
        
        return {
            'status': 'ready',
            'nodes': nodes,
            'links': links,
            'domain_id': str(domain_id),
        }
        
    except Exception as e:
        logger.error(f"Semantic map failed: {e}")
        return {
            'status': 'error',
            'message': str(e),
            'nodes': [],
            'links': [],
        }
    finally:
        session.close()


def get_sgs_history(domain_id: UUID) -> List[Dict]:
    """Get historical SGS measurements."""
    session = get_session()
    
    try:
        records = session.query(SemanticGravityRecord).filter_by(
            domain_id=domain_id
        ).order_by(SemanticGravityRecord.measured_at.desc()).limit(30).all()
        
        return [r.to_dict() for r in records]
    finally:
        session.close()
