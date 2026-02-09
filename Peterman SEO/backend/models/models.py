"""
Peterman V4.1 — Database Models
Almost Magic Tech Lab

All models for the 10-chamber architecture.
Uses PostgreSQL + pgvector for embeddings.
"""
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from pgvector.sqlalchemy import Vector

db = SQLAlchemy()


# ============================================================
# BRAND PROFILES
# ============================================================

class Brand(db.Model):
    """Core brand profile — the entity we monitor across all chambers."""
    __tablename__ = "brands"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    domain = db.Column(db.String(512))
    industry = db.Column(db.String(255))
    description = db.Column(db.Text)
    tier = db.Column(db.String(50), default="growth")  # growth | authority | enterprise
    is_client_zero = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)

    # Brand identity
    tagline = db.Column(db.String(512))
    value_propositions = db.Column(db.JSON, default=list)
    target_audience = db.Column(db.JSON, default=list)
    differentiators = db.Column(db.JSON, default=list)

    # Configuration
    scan_frequency = db.Column(db.String(50), default="weekly")  # daily | weekly | monthly
    llm_models = db.Column(db.JSON, default=lambda: ["ollama-llama3.1", "ollama-gemma2"])
    notification_channels = db.Column(db.JSON, default=list)

    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    keywords = db.relationship("Keyword", backref="brand", lazy="dynamic", cascade="all, delete-orphan")
    competitors = db.relationship("Competitor", backref="brand", lazy="dynamic", cascade="all, delete-orphan")
    scans = db.relationship("Scan", backref="brand", lazy="dynamic", cascade="all, delete-orphan")
    hallucinations = db.relationship("Hallucination", backref="brand", lazy="dynamic", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "domain": self.domain,
            "industry": self.industry,
            "description": self.description,
            "tier": self.tier,
            "is_client_zero": self.is_client_zero,
            "is_active": self.is_active,
            "tagline": self.tagline,
            "value_propositions": self.value_propositions,
            "target_audience": self.target_audience,
            "differentiators": self.differentiators,
            "scan_frequency": self.scan_frequency,
            "llm_models": self.llm_models,
            "keyword_count": self.keywords.count(),
            "competitor_count": self.competitors.count(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Keyword(db.Model):
    """Keywords tracked for a brand across LLMs."""
    __tablename__ = "keywords"

    id = db.Column(db.Integer, primary_key=True)
    brand_id = db.Column(db.Integer, db.ForeignKey("brands.id"), nullable=False)
    keyword = db.Column(db.String(512), nullable=False)
    category = db.Column(db.String(100))  # primary | secondary | long-tail | question
    status = db.Column(db.String(50), default="pending")  # pending | approved | rejected
    search_volume = db.Column(db.Integer)
    difficulty = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "brand_id": self.brand_id,
            "keyword": self.keyword,
            "category": self.category,
            "status": self.status,
            "search_volume": self.search_volume,
            "difficulty": self.difficulty,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Competitor(db.Model):
    """Competitors tracked for a brand."""
    __tablename__ = "competitors"

    id = db.Column(db.Integer, primary_key=True)
    brand_id = db.Column(db.Integer, db.ForeignKey("brands.id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    domain = db.Column(db.String(512))
    relationship = db.Column(db.String(100), default="direct")  # direct | indirect | aspirational
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "brand_id": self.brand_id,
            "name": self.name,
            "domain": self.domain,
            "relationship": self.relationship,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ============================================================
# SCANS & RESULTS
# ============================================================

class Scan(db.Model):
    """A scan run — can be single-chamber or full 10-chamber."""
    __tablename__ = "scans"

    id = db.Column(db.Integer, primary_key=True)
    brand_id = db.Column(db.Integer, db.ForeignKey("brands.id"), nullable=False)
    scan_type = db.Column(db.String(50), nullable=False)  # perception | semantic | full | crisis
    status = db.Column(db.String(50), default="queued")  # queued | running | completed | failed
    chambers_run = db.Column(db.JSON, default=list)  # which chambers were included
    depth = db.Column(db.String(50), default="standard")  # standard | deep | crisis

    # Results summary
    summary = db.Column(db.JSON)
    scores = db.Column(db.JSON)
    alerts = db.Column(db.JSON, default=list)

    # Cost tracking
    api_calls = db.Column(db.Integer, default=0)
    tokens_used = db.Column(db.Integer, default=0)
    estimated_cost = db.Column(db.Float, default=0.0)
    models_used = db.Column(db.JSON, default=list)

    # Timing
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    hallucinations = db.relationship("Hallucination", backref="scan", lazy="dynamic")
    perception_results = db.relationship("PerceptionResult", backref="scan", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "brand_id": self.brand_id,
            "scan_type": self.scan_type,
            "status": self.status,
            "chambers_run": self.chambers_run,
            "depth": self.depth,
            "summary": self.summary,
            "scores": self.scores,
            "alerts": self.alerts,
            "api_calls": self.api_calls,
            "tokens_used": self.tokens_used,
            "estimated_cost": self.estimated_cost,
            "models_used": self.models_used,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ============================================================
# CHAMBER 1: PERCEPTION SCAN
# ============================================================

class PerceptionResult(db.Model):
    """Individual LLM response for a perception scan query."""
    __tablename__ = "perception_results"

    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey("scans.id"), nullable=False)
    brand_id = db.Column(db.Integer, db.ForeignKey("brands.id"), nullable=False)

    # Query
    query = db.Column(db.Text, nullable=False)
    keyword_id = db.Column(db.Integer, db.ForeignKey("keywords.id"))

    # Response
    model = db.Column(db.String(100), nullable=False)  # ollama-llama3.1 | openai-gpt4 | etc
    response = db.Column(db.Text)
    response_embedding = db.Column(Vector(768))  # nomic-embed-text dimension

    # Analysis
    brand_mentioned = db.Column(db.Boolean, default=False)
    mention_position = db.Column(db.Integer)  # 1st, 2nd, 3rd mentioned
    mention_context = db.Column(db.String(100))  # positive | negative | neutral | hallucination
    trust_class = db.Column(db.String(50))  # authority | reference | passing | absent
    citations = db.Column(db.JSON, default=list)
    competitors_mentioned = db.Column(db.JSON, default=list)

    # Scores
    accuracy_score = db.Column(db.Float)  # 0-100 factual accuracy
    sentiment_score = db.Column(db.Float)  # -1 to 1
    prominence_score = db.Column(db.Float)  # 0-100 how prominently featured

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "scan_id": self.scan_id,
            "query": self.query,
            "model": self.model,
            "response": self.response,
            "brand_mentioned": self.brand_mentioned,
            "mention_position": self.mention_position,
            "mention_context": self.mention_context,
            "trust_class": self.trust_class,
            "citations": self.citations,
            "competitors_mentioned": self.competitors_mentioned,
            "accuracy_score": self.accuracy_score,
            "sentiment_score": self.sentiment_score,
            "prominence_score": self.prominence_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Hallucination(db.Model):
    """Detected hallucination about a brand."""
    __tablename__ = "hallucinations"

    id = db.Column(db.Integer, primary_key=True)
    brand_id = db.Column(db.Integer, db.ForeignKey("brands.id"), nullable=False)
    scan_id = db.Column(db.Integer, db.ForeignKey("scans.id"))

    # What was hallucinated
    model = db.Column(db.String(100), nullable=False)
    query = db.Column(db.Text)
    hallucinated_claim = db.Column(db.Text, nullable=False)
    actual_truth = db.Column(db.Text)
    severity = db.Column(db.String(50), default="medium")  # low | medium | high | critical
    category = db.Column(db.String(100))  # factual | attribution | temporal | fabrication

    # Status tracking
    status = db.Column(db.String(50), default="detected")  # detected | confirmed | correcting | resolved | persistent
    first_detected = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_seen = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    times_seen = db.Column(db.Integer, default=1)

    # Inertia tracking
    inertia_score = db.Column(db.Float)  # 0-100, higher = more persistent
    correction_attempts = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "brand_id": self.brand_id,
            "scan_id": self.scan_id,
            "model": self.model,
            "query": self.query,
            "hallucinated_claim": self.hallucinated_claim,
            "actual_truth": self.actual_truth,
            "severity": self.severity,
            "category": self.category,
            "status": self.status,
            "first_detected": self.first_detected.isoformat() if self.first_detected else None,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "times_seen": self.times_seen,
            "inertia_score": self.inertia_score,
            "correction_attempts": self.correction_attempts,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ============================================================
# CHAMBER 2: SEMANTIC CORE
# ============================================================

class SemanticFingerprint(db.Model):
    """Brand's semantic fingerprint from a specific LLM at a point in time."""
    __tablename__ = "semantic_fingerprints"

    id = db.Column(db.Integer, primary_key=True)
    brand_id = db.Column(db.Integer, db.ForeignKey("brands.id"), nullable=False)
    scan_id = db.Column(db.Integer, db.ForeignKey("scans.id"))
    model = db.Column(db.String(100), nullable=False)

    # The fingerprint
    embedding = db.Column(Vector(768))
    key_themes = db.Column(db.JSON, default=list)
    narrative_summary = db.Column(db.Text)

    # Drift from previous
    drift_score = db.Column(db.Float)  # cosine distance from previous fingerprint
    drift_direction = db.Column(db.String(50))  # positive | negative | neutral | concerning

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "brand_id": self.brand_id,
            "model": self.model,
            "key_themes": self.key_themes,
            "narrative_summary": self.narrative_summary,
            "drift_score": self.drift_score,
            "drift_direction": self.drift_direction,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ============================================================
# SHARE OF VOICE
# ============================================================

class ShareOfVoice(db.Model):
    """Brand's share of voice for a keyword at a point in time."""
    __tablename__ = "share_of_voice"

    id = db.Column(db.Integer, primary_key=True)
    brand_id = db.Column(db.Integer, db.ForeignKey("brands.id"), nullable=False)
    scan_id = db.Column(db.Integer, db.ForeignKey("scans.id"))
    keyword_id = db.Column(db.Integer, db.ForeignKey("keywords.id"))

    model = db.Column(db.String(100), nullable=False)
    keyword = db.Column(db.String(512))
    brand_mentions = db.Column(db.Integer, default=0)
    total_mentions = db.Column(db.Integer, default=0)
    share_percentage = db.Column(db.Float, default=0.0)
    position = db.Column(db.Integer)  # where brand appears in response order

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "brand_id": self.brand_id,
            "model": self.model,
            "keyword": self.keyword,
            "brand_mentions": self.brand_mentions,
            "total_mentions": self.total_mentions,
            "share_percentage": self.share_percentage,
            "position": self.position,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
