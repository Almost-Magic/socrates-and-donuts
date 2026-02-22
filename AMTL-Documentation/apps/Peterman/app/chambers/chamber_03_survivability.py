"""
Chamber 3 — Content Survivability Lab

LCRI (LLM Compression Resistance Index) measures how well your content
survives when an LLM summarises, compresses, or extracts from it.

Four tests:
1. Direct Summarisation - what % of key facts survive?
2. Citation Probability - does LLM cite this domain?
3. Extractable Snippet Strength - can LLM extract clean answers?
4. RAG Chunk Compatibility - test retrieval quality

Per DEC-005: Uses Claude CLI for testing.
"""

import logging
import json
import re
from datetime import datetime
from typing import List, Dict, Optional
from uuid import UUID

from sqlalchemy import Column, Integer, Float, String, DateTime, JSON, Text, UUID as SQLUUID, ForeignKey

from app.models.database import Base, get_session
from app.models.domain import Domain

logger = logging.getLogger(__name__)


# LCRI storage model
class LCRIRecord(Base):
    """Stores LCRI measurements per page."""
    __tablename__ = 'lcri_records'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    domain_id = Column(SQLUUID(as_uuid=True), ForeignKey('domains.domain_id'), nullable=False)
    page_url = Column(Text, nullable=False)
    measured_at = Column(DateTime, default=datetime.utcnow)
    lcri_score = Column(Float, nullable=False)  # 0-100
    summarisation_score = Column(Float, default=0.0)
    citation_probability = Column(Float, default=0.0)
    snippet_strength = Column(Float, default=0.0)
    rag_compatibility = Column(Float, default=0.0)
    test_details = Column(JSON)
    model_version = Column(String(50), default='KNW-004')
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'domain_id': str(self.domain_id),
            'page_url': self.page_url,
            'measured_at': self.measured_at.isoformat() if self.measured_at else None,
            'lcri_score': self.lcri_score,
            'summarisation_score': self.summarisation_score,
            'citation_probability': self.citation_probability,
            'snippet_strength': self.snippet_strength,
            'rag_compatibility': self.rag_compatibility,
            'test_details': self.test_details,
            'model_version': self.model_version,
        }


def _get_ai_engine():
    from app.services.ai_engine import AIEngine
    return AIEngine()


def test_summarisation(content: str, key_facts: List[str]) -> Dict:
    """Test 1: Direct Summarisation.
    
    Feed page to Claude CLI, ask for summary.
    Score: what % of key facts survive?
    """
    engine = _get_ai_engine()
    
    # Extract key facts from content
    prompt = f"""Analyze this content and extract the 5-10 most important factual claims:

Content:
{content[:3000]}

List each factual claim as a brief statement."""

    try:
        result = engine.reason(prompt, "You are a content analysis expert.")
        if result.get('success'):
            # Simple scoring: count how many key facts appear in summary
            facts_found = 0
            for fact in key_facts[:5]:
                if fact.lower() in result['response'].lower():
                    facts_found += 1
            
            score = (facts_found / min(len(key_facts), 5)) * 100 if key_facts else 50
            return {
                'score': round(score, 2),
                'facts_extracted': result['response'][:500],
                'facts_matched': facts_found,
            }
    except Exception as e:
        logger.error(f"Summarisation test failed: {e}")
    
    return {'score': 0.0, 'error': str(e)}


def test_citation_probability(domain_name: str, topic: str) -> Dict:
    """Test 2: Citation Probability.
    
    Ask Claude "cite a source for [topic]" - 
    does it cite this domain?
    """
    engine = _get_ai_engine()
    
    prompt = f"""Give me a brief answer (2-3 sentences) about "{topic}" and cite your sources using [source] notation."""

    try:
        result = engine.reason(prompt, "You are a helpful assistant with knowledge up to 2025.")
        if result.get('success'):
            response = result['response'].lower()
            
            # Check if domain is mentioned
            domain_parts = domain_name.replace('.', ' ').replace('http://', '').replace('https://', '').split()
            mentioned = any(part in response for part in domain_parts if len(part) > 3)
            
            score = 100.0 if mentioned else 0.0
            return {
                'score': score,
                'response': result['response'][:500],
                'domain_mentioned': mentioned,
            }
    except Exception as e:
        logger.error(f"Citation test failed: {e}")
    
    return {'score': 0.0, 'error': str(e)}


def test_snippet_extraction(content: str, questions: List[str]) -> Dict:
    """Test 3: Extractable Snippet Strength.
    
    Ask Claude factual questions about the content -
    can it extract clean answers?
    """
    engine = _get_ai_engine()
    
    successful_extractions = 0
    
    for question in questions[:3]:
        prompt = f"""Based ONLY on this content, answer the question:

Content:
{content[:2000]}

Question: {question}

Provide a direct answer. If the content doesn't contain the answer, say "I don't have enough information." """

        try:
            result = engine.reason(prompt, "You are a helpful assistant.")
            if result.get('success'):
                response = result['response']
                # Check if it gave a valid answer vs "don't know"
                if "don't have enough information" not in response.lower() and \
                   "not specified" not in response.lower() and \
                   len(response) > 20:
                    successful_extractions += 1
        except:
            continue
    
    score = (successful_extractions / len(questions[:3])) * 100 if questions else 0
    return {
        'score': round(score, 2),
        'extractions': successful_extractions,
        'total_questions': len(questions[:3]),
    }


def test_rag_compatibility(content: str, target_queries: List[str]) -> Dict:
    """Test 4: RAG Chunk Compatibility.
    
    Split content into chunks, embed each,
    test retrieval quality against target queries.
    """
    # Simple chunk-based test without actual embeddings
    # In production, this would use actual embeddings
    
    # Split content into chunks
    chunk_size = 500
    chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
    
    # Check if chunks contain relevant info for queries
    relevant_chunks = 0
    for query in target_queries[:3]:
        query_terms = query.lower().split()
        for chunk in chunks:
            if any(term in chunk.lower() for term in query_terms if len(term) > 3):
                relevant_chunks += 1
                break
    
    score = (relevant_chunks / len(target_queries[:3])) * 100 if target_queries else 0
    return {
        'score': round(score, 2),
        'total_chunks': len(chunks),
        'relevant_chunks': relevant_chunks,
    }


def compute_lcri(domain_id: UUID) -> Dict:
    """Compute LCRI for all pages of a domain.
    
    Runs all 4 tests and computes weighted average.
    """
    session = get_session()
    
    try:
        domain = session.query(Domain).filter_by(domain_id=domain_id).first()
        if not domain:
            raise ValueError(f"Domain not found: {domain_id}")
        
        crawl_data = domain.crawl_data
        if not crawl_data:
            return {
                'status': 'error',
                'message': 'No crawl data available',
                'pages': [],
            }
        
        pages = crawl_data.get('pages', [crawl_data.get('homepage', {})])
        if not pages:
            pages = [crawl_data.get('homepage', {})]
        
        # Get target queries for testing
        from app.services.keyword_engine import TargetQuery
        keywords = session.query(TargetQuery).filter_by(
            domain_id=domain_id, 
            is_approved=True
        ).all()
        
        target_queries = [kw.query for kw in keywords[:10]]
        
        results = []
        
        for page in pages[:5]:  # Limit to 5 pages
            content = page.get('text_content', '')
            if not content:
                continue
            
            page_url = page.get('url', 'unknown')
            
            # Run tests
            summarisation = test_summarisation(content, target_queries)
            citation = test_citation_probability(domain.domain_name, target_queries[0] if target_queries else 'general')
            snippet = test_snippet_extraction(content, target_queries[:3])
            rag = test_rag_compatibility(content, target_queries[:5])
            
            # Weighted average: 25% each
            lcri_score = (
                summarisation.get('score', 0) * 0.25 +
                citation.get('score', 0) * 0.25 +
                snippet.get('score', 0) * 0.25 +
                rag.get('score', 0) * 0.25
            )
            
            # Save record
            record = LCRIRecord(
                domain_id=domain_id,
                page_url=page_url,
                lcri_score=round(lcri_score, 2),
                summarisation_score=summarisation.get('score', 0),
                citation_probability=citation.get('score', 0),
                snippet_strength=snippet.get('score', 0),
                rag_compatibility=rag.get('score', 0),
                test_details={
                    'summarisation': summarisation,
                    'citation': citation,
                    'snippet': snippet,
                    'rag': rag,
                },
                model_version='KNW-004',
            )
            session.add(record)
            results.append(record.to_dict())
        
        session.commit()
        
        # Calculate average LCRI
        avg_score = sum(r['lcri_score'] for r in results) / len(results) if results else 0
        
        return {
            'status': 'ready',
            'pages_tested': len(results),
            'average_lcri': round(avg_score, 2),
            'pages': results,
        }
        
    except Exception as e:
        logger.error(f"LCRI computation failed: {e}")
        session.rollback()
        return {
            'status': 'error',
            'message': str(e),
            'pages': [],
        }
    finally:
        session.close()


def get_lcri_history(domain_id: UUID) -> List[Dict]:
    """Get historical LCRI measurements."""
    session = get_session()
    
    try:
        records = session.query(LCRIRecord).filter_by(
            domain_id=domain_id
        ).order_by(LCRIRecord.measured_at.desc()).limit(30).all()
        
        return [r.to_dict() for r in records]
    finally:
        session.close()


def get_latest_lcri(domain_id: UUID) -> Dict:
    """Get the most recent LCRI scores."""
    session = get_session()
    
    try:
        # Get latest record per page
        records = session.query(LCRIRecord).filter_by(
            domain_id=domain_id
        ).order_by(LCRIRecord.measured_at.desc()).limit(5).all()
        
        if not records:
            return {
                'status': 'pending',
                'message': 'No LCRI data. Run LCRI scan.',
                'average_lcri': None,
                'pages': [],
            }
        
        avg_score = sum(r.lcri_score for r in records) / len(records)
        
        return {
            'status': 'ready',
            'average_lcri': round(avg_score, 2),
            'pages': [r.to_dict() for r in records],
            'measured_at': records[0].measured_at.isoformat() if records else None,
        }
    finally:
        session.close()
