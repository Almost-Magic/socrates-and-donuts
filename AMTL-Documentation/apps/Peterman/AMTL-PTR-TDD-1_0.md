# AMTL — Peterman Technical Design Document
## Document Code: AMTL-PTR-TDD-1.0
## Almost Magic Tech Lab
## 18 February 2026

> *This document follows AMTL-ECO-STD v1.0. All conventions defined there apply unless explicitly overridden with a Decision Register entry.*

---

## 1. Overview

### 1.1 What Is Peterman?

Peterman is an autonomous SEO and LLM Presence Operating System. It takes domain names and objectives, then continuously monitors, analyses, plans, seeks approval, executes, verifies, and reports — running as a Flask application within the AMTL ecosystem.

### 1.2 Key Facts

| Fact | Value |
|------|-------|
| Application type | Flask web application (SPA frontend) |
| Port | 5008 |
| Database | PostgreSQL 17 + pgvector (port 5433) |
| Queue | Redis (port 6379) |
| Scheduler | APScheduler |
| Primary AI | Claude Desktop (via MCP / local socket) |
| Fallback AI | Manus Desktop → Perplexity Desktop → Ollama (via Supervisor :9000) |
| Embeddings | nomic-embed-text (Ollama, always local) |
| Search | SearXNG (port 8888) |
| CMS targets | WordPress REST API, Webflow API, Ghost Content API, GitHub API, custom webhook |
| Notifications | ntfy.sh (push) + ELAINE (conversational) |
| Frontend | HTML/CSS/JS SPA, dark theme default, AMTL branding |

### 1.3 Dependencies

| Dependency | Port | Hard/Soft | Impact If Down |
|------------|------|-----------|----------------|
| PostgreSQL + pgvector | 5433 | Hard | All persistent data unavailable — Peterman cannot function |
| Redis | 6379 | Soft | Content brief queue degraded — falls back to DB queue |
| Ollama via Supervisor | 9000/11434 | Hard | Embeddings and local inference unavailable |
| Claude Desktop | — | Soft | Complex reasoning degraded — falls to Manus → Perplexity → Ollama |
| SearXNG | 8888 | Soft | Competitor monitoring and trend detection unavailable |
| ELAINE | 5000 | Soft | Content commissioning and voice approvals unavailable |
| The Workshop | 5003 | Soft | Ecosystem status unavailable — Peterman runs independently |
| CMS API (per domain) | Varies | Soft | Autonomous deployment unavailable — queues changes |
| GSC API | HTTPS | Soft | Traffic data unavailable — LLM-only tracking continues |

---

## 2. System Architecture

### 2.1 Peterman in the AMTL Ecosystem

```mermaid
graph TB
    subgraph "User Layer"
        MANI[Mani - Operator]
    end

    subgraph "Interface Layer"
        ELAINE[ELAINE :5000]
        WR[War Room Dashboard :5008]
        MOBILE[Mobile - ntfy.sh]
    end

    subgraph "Peterman Core :5008"
        API[Flask API Layer]
        SCHED[APScheduler]
        CHAMBERS[Chamber Engine]
        APPROVE[Approval Gate System]
        DEPLOY[Deployment Engine]
        ROLLBACK[Rollback Layer]
        AUDIT[Audit Logger]
        BUDGET[Cost Budget Monitor]
    end

    subgraph "AI Layer"
        CLAUDE[Claude Desktop - Primary]
        MANUS[Manus Desktop - Fallback 1]
        PERP[Perplexity Desktop - Fallback 2]
        OLLAMA[Ollama via Supervisor :9000]
    end

    subgraph "Data Layer"
        PG[(PostgreSQL + pgvector :5433)]
        REDIS[(Redis :6379)]
        SEARX[SearXNG :8888]
    end

    subgraph "External"
        CMS[CMS APIs - WordPress/Webflow]
        GSC[Google Search Console]
        LLMAPI[LLM Probe APIs - OpenAI/Anthropic]
        NTFY[ntfy.sh]
    end

    subgraph "Ecosystem"
        WKS[The Workshop :5003]
        CKW[CK Writer :5004]
    end

    MANI --> ELAINE
    MANI --> WR
    MANI --> MOBILE

    ELAINE <--> API
    WR --> API
    MOBILE --> NTFY

    API --> CHAMBERS
    API --> APPROVE
    SCHED --> CHAMBERS
    CHAMBERS --> CLAUDE
    CHAMBERS --> MANUS
    CHAMBERS --> PERP
    CHAMBERS --> OLLAMA
    CHAMBERS --> PG
    CHAMBERS --> REDIS
    CHAMBERS --> SEARX
    CHAMBERS --> LLMAPI
    CHAMBERS --> GSC

    APPROVE --> ELAINE
    APPROVE --> DEPLOY
    DEPLOY --> CMS
    DEPLOY --> ROLLBACK
    ROLLBACK --> PG

    AUDIT --> PG
    BUDGET --> PG

    API --> WKS
    ELAINE --> CKW
```

### 2.2 Data Flow — The Core Loop

```mermaid
flowchart LR
    A[MONITOR] --> B[ANALYSE]
    B --> C[PLAN]
    C --> D[APPROVE]
    D --> E[EXECUTE]
    E --> F[VERIFY]
    F --> G[REPORT]
    G --> A

    D -- "Rejected" --> C
    F -- "Failed" --> H[ROLLBACK]
    H --> G
```

---

## 3. User Journey Flow

### 3.1 Domain Onboarding

```mermaid
sequenceDiagram
    actor Mani
    participant WR as War Room
    participant PTR as Peterman API
    participant C6 as Chamber 6
    participant C1 as Chamber 1
    participant DB as PostgreSQL
    participant ELAINE as ELAINE

    Mani->>WR: Enter domain URL
    WR->>PTR: POST /api/domains
    PTR->>DB: Create Domain Object
    PTR->>C6: Run technical baseline audit
    C6-->>PTR: Technical health score
    PTR->>C1: Run initial LLM probe set (5 queries × 5 runs)
    C1-->>PTR: Initial SoV scores
    PTR->>DB: Store baseline data
    PTR->>PTR: Compute initial Peterman Score
    PTR->>ELAINE: "Onboarding complete for [domain]. Initial score: [X]. Three priority actions queued."
    ELAINE->>Mani: Voice briefing
    PTR->>WR: Domain Card rendered
```

### 3.2 Autonomous Cycle (Daily/Weekly)

```mermaid
sequenceDiagram
    participant SCHED as Scheduler
    participant C1 as Chamber 1 (Perception)
    participant C2 as Chamber 2 (Semantic)
    participant C5 as Chamber 5 (Hallucination)
    participant C10 as Chamber 10 (Forge)
    participant APPROVE as Approval Gate
    participant ELAINE as ELAINE
    participant DEPLOY as Deployment Engine
    participant CMS as CMS API
    actor Mani

    SCHED->>C1: Run LLM probes
    C1-->>C1: Detect hallucinations, compute SoV
    C1->>C5: Hallucination detected
    C5->>C10: Generate correction brief
    C10->>APPROVE: Brief ready for approval
    APPROVE->>ELAINE: Present to operator (medium-gate)
    ELAINE->>Mani: "Peterman has a new FAQ ready to fix the ISO certification hallucination. Shall I deploy?"
    Mani->>ELAINE: "Yes"
    ELAINE->>APPROVE: Approved
    APPROVE->>DEPLOY: Deploy via dry-run
    DEPLOY->>DEPLOY: Generate HTML diff, snapshot pre-state
    DEPLOY->>CMS: Push changes
    DEPLOY->>DEPLOY: Verify deployment
    DEPLOY->>ELAINE: "Deployed. Snapshot saved. Verification in 48 hours."
```

---

## 4. Component Architecture

### 4.1 Module Map

```
peterman/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── routes/
│   │   ├── api.py               # Core REST API
│   │   ├── domains.py           # Domain CRUD + onboarding
│   │   ├── chambers.py          # Chamber status + trigger endpoints
│   │   ├── approvals.py         # Approval queue endpoints
│   │   ├── reports.py           # Peterman Score, Client Mode reports
│   │   ├── health.py            # /api/health endpoint
│   │   └── elaine.py            # ELAINE integration endpoints
│   ├── services/
│   │   ├── ai_engine.py         # AI routing (Claude → Manus → Perplexity → Ollama)
│   │   ├── probe_engine.py      # LLM probing with normalisation protocol
│   │   ├── embedding_engine.py  # nomic-embed-text via Ollama
│   │   ├── deployment_engine.py # CMS API integration + dry-run + rollback
│   │   ├── scheduler.py         # APScheduler configuration
│   │   ├── budget_monitor.py    # Per-domain cost tracking
│   │   └── notification.py      # ntfy.sh + ELAINE alerts
│   ├── chambers/
│   │   ├── base.py              # BaseChamber class
│   │   ├── chamber_01_perception.py
│   │   ├── chamber_02_semantic.py
│   │   ├── chamber_03_survivability.py
│   │   ├── chamber_04_authority.py
│   │   ├── chamber_05_hallucination.py
│   │   ├── chamber_06_technical.py
│   │   ├── chamber_07_amplifier.py
│   │   ├── chamber_08_competitive.py
│   │   ├── chamber_09_oracle.py
│   │   ├── chamber_10_forge.py
│   │   └── chamber_11_defensive.py
│   ├── models/
│   │   ├── domain.py            # Domain Object model
│   │   ├── hallucination.py     # Hallucination Registry model
│   │   ├── probe.py             # LLM probe results model
│   │   ├── brief.py             # Content Brief model
│   │   ├── deployment.py        # Deployment + snapshot model
│   │   ├── audit.py             # Audit log model
│   │   └── score.py             # Peterman Score model
│   ├── templates/
│   │   └── index.html           # SPA shell
│   ├── static/
│   │   ├── css/
│   │   │   └── peterman.css     # AMTL Midnight + Gold theme
│   │   ├── js/
│   │   │   ├── app.js           # SPA router + state
│   │   │   ├── war-room.js      # War Room dashboard
│   │   │   ├── domain-card.js   # Domain Card component
│   │   │   ├── approval-inbox.js # Approval queue component
│   │   │   ├── timeline.js      # Journey Timeline component
│   │   │   ├── score-gauge.js   # Peterman Score circular gauge
│   │   │   └── semantic-map.js  # 2D semantic neighbourhood
│   │   └── img/
│   │       └── favicon.svg
│   └── help.py                  # Context-aware help (AMTL-ECO-CTX standard)
├── tests/                       # See AMTL-PTR-BLD-1.0 for test types
│   ├── beast/
│   ├── inspector/
│   ├── four_percent/
│   ├── proof/
│   ├── smoke/
│   ├── regression/
│   └── integration/
├── docs/
├── logs/
├── electron/
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── CHANGELOG.md
├── README.md
└── USER-MANUAL.md
```

### 4.2 Chamber Architecture

Every chamber inherits from `BaseChamber`:

```python
class BaseChamber:
    """Base class for all Peterman chambers.

    Attributes:
        chamber_id: Integer identifier (1-11).
        name: Human-readable chamber name.
        domain_id: UUID of the domain being processed.
    """

    def __init__(self, chamber_id: int, name: str, domain_id: str):
        self.chamber_id = chamber_id
        self.name = name
        self.domain_id = domain_id

    def monitor(self) -> dict:
        """Run monitoring cycle. Returns findings dict."""
        raise NotImplementedError

    def analyse(self, findings: dict) -> dict:
        """Analyse findings. Returns analysis with recommendations."""
        raise NotImplementedError

    def plan(self, analysis: dict) -> list:
        """Generate action items from analysis. Returns list of actions."""
        raise NotImplementedError

    def get_approval_level(self, action: dict) -> str:
        """Classify action risk level. Returns gate level string."""
        raise NotImplementedError

    def execute(self, action: dict) -> dict:
        """Execute an approved action. Returns result dict."""
        raise NotImplementedError

    def verify(self, result: dict) -> dict:
        """Verify execution outcome. Returns verification dict."""
        raise NotImplementedError

    def report(self, verification: dict) -> dict:
        """Generate report from verification. Returns report dict."""
        raise NotImplementedError
```

---

## 5. API Reference

### 5.1 Exposed Endpoints (Peterman → External)

#### Health

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Health check with dependency status |

**Response:**
```json
{
  "status": "healthy",
  "app": "peterman",
  "version": "2.0.0",
  "port": 5008,
  "uptime_seconds": 86400,
  "dependencies": {
    "postgresql": { "status": "healthy", "latency_ms": 3 },
    "redis": { "status": "healthy", "latency_ms": 1 },
    "ollama": { "status": "healthy", "latency_ms": 12 },
    "searxng": { "status": "healthy", "latency_ms": 8 },
    "elaine": { "status": "healthy", "latency_ms": 5 },
    "claude_desktop": { "status": "healthy", "latency_ms": null }
  }
}
```

#### Domains

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/domains` | GET | List all managed domains |
| `/api/domains` | POST | Register new domain (triggers onboarding) |
| `/api/domains/<domain_id>` | GET | Get domain detail + Peterman Score |
| `/api/domains/<domain_id>` | PATCH | Update domain configuration |
| `/api/domains/<domain_id>` | DELETE | Archive domain (soft delete) |
| `/api/domains/<domain_id>/onboard` | POST | Re-run onboarding |
| `/api/domains/<domain_id>/score` | GET | Current Peterman Score with breakdown |
| `/api/domains/<domain_id>/score/history` | GET | Score history (daily, weekly, monthly) |

**POST `/api/domains` request:**
```json
{
  "domain_name": "almostmagic.net.au",
  "display_name": "Almost Magic Tech Lab",
  "owner_label": "AMTL Internal",
  "cms_type": "wordpress",
  "cms_api_key": "encrypted_key_here",
  "target_llms": ["openai", "anthropic", "ollama", "perplexity"],
  "probe_cadence": "weekly",
  "budget_weekly_aud": 50.00,
  "tier": "owner"
}
```

#### Chambers

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/domains/<domain_id>/chambers` | GET | Status of all 11 chambers |
| `/api/domains/<domain_id>/chambers/<chamber_id>` | GET | Detailed chamber data |
| `/api/domains/<domain_id>/chambers/<chamber_id>/run` | POST | Trigger chamber cycle manually |

#### Hallucinations

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/domains/<domain_id>/hallucinations` | GET | All hallucination records |
| `/api/domains/<domain_id>/hallucinations/<id>` | GET | Hallucination detail |
| `/api/domains/<domain_id>/hallucinations/<id>/status` | PATCH | Update status |

#### Content Briefs

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/domains/<domain_id>/briefs` | GET | All content briefs |
| `/api/domains/<domain_id>/briefs/<id>` | GET | Brief detail |
| `/api/domains/<domain_id>/briefs/<id>/approve` | POST | Approve brief |
| `/api/domains/<domain_id>/briefs/<id>/reject` | POST | Reject brief (with reason) |

#### Approvals

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/approvals` | GET | All pending approvals (cross-domain) |
| `/api/approvals/<id>/approve` | POST | Approve action |
| `/api/approvals/<id>/reject` | POST | Reject action |

#### Deployments

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/domains/<domain_id>/deployments` | GET | Deployment history |
| `/api/domains/<domain_id>/deployments/<id>/rollback` | POST | Rollback deployment |

#### Timeline

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/domains/<domain_id>/timeline` | GET | Journey Timeline events |

#### Reports

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/domains/<domain_id>/report/client` | GET | Client Mode PDF report |

#### Audit Log

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/domains/<domain_id>/audit` | GET | Audit log (append-only, exportable) |

### 5.2 Consumed Endpoints (External → Peterman)

#### ELAINE Integration

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/elaine/status` | GET | ELAINE queries Peterman status |
| `/api/elaine/score/<domain_id>` | GET | ELAINE asks for current Peterman Score |
| `/api/elaine/hallucinations/<domain_id>` | GET | ELAINE asks about active hallucinations |
| `/api/elaine/brief-queue/<domain_id>` | GET | ELAINE asks about pending briefs |
| `/api/elaine/approval/<approval_id>` | POST | ELAINE forwards operator's approval/rejection |
| `/api/elaine/content-complete` | POST | ELAINE notifies content is written |

**ELAINE content-complete payload:**
```json
{
  "brief_id": "uuid-here",
  "content": "Full written content from CK Writer",
  "metadata": {
    "word_count": 1150,
    "writer": "ck_writer",
    "completed_at": "2026-02-18T14:30:00+11:00"
  }
}
```

### 5.3 Peterman → ELAINE Outbound

| Endpoint (on ELAINE) | Method | Purpose |
|----------------------|--------|---------|
| `/api/integration/brief` | POST | Submit content brief to ELAINE queue |
| `/api/integration/alert` | POST | Send critical alert to ELAINE |
| `/api/integration/approval-request` | POST | Send approval request for ELAINE to present |

**Content brief submission payload:**
```json
{
  "source": "peterman",
  "request_type": "content_brief",
  "priority": "high",
  "domain_id": "uuid",
  "brief": {
    "brief_id": "uuid",
    "title": "What is ISO 42001 and Why Australian SMBs Need It Now",
    "target_query": "ISO 42001 Australia small business",
    "llm_intent": "answer the question 'what is ISO 42001' for an Australian SMB audience",
    "word_count_range": "800-1200",
    "schema_type": "Article + FAQPage",
    "key_headings": ["What is ISO 42001?", "Why Australian businesses need it", "How to get started", "FAQ"],
    "evidence_required": ["Chamber 1: ChatGPT has no response for this query", "Chamber 3: 280 estimated monthly searches"],
    "internal_links": ["almostmagic.net.au/services", "almostmagic.net.au/contact"],
    "lcri_target": 0.80,
    "sgs_delta_estimate": 0.09,
    "deadline": "2026-02-25"
  }
}
```

---

## 6. Data Model

### 6.1 Core Tables

All tables include `domain_id` as non-nullable foreign key. No cross-domain data leakage is architecturally possible.

#### domains
```sql
CREATE TABLE domains (
    domain_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain_name     VARCHAR(255) NOT NULL UNIQUE,
    display_name    VARCHAR(255) NOT NULL,
    owner_label     VARCHAR(255),
    cms_type        VARCHAR(50),
    cms_api_key     TEXT,  -- encrypted
    target_llms     JSONB DEFAULT '["openai", "anthropic", "ollama"]',
    probe_cadence   VARCHAR(20) DEFAULT 'weekly',
    budget_weekly_aud DECIMAL(10,2) DEFAULT 50.00,
    status          VARCHAR(20) DEFAULT 'onboarding',
    tier            VARCHAR(20) DEFAULT 'owner',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
```

#### peterman_scores
```sql
CREATE TABLE peterman_scores (
    score_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain_id       UUID NOT NULL REFERENCES domains(domain_id),
    computed_at     TIMESTAMPTZ DEFAULT NOW(),
    total_score     DECIMAL(5,2),
    confidence      DECIMAL(5,2),
    sov_score       DECIMAL(5,2),
    sov_confidence  DECIMAL(5,2),
    sgs_score       DECIMAL(5,2),
    sgs_confidence  DECIMAL(5,2),
    technical_score DECIMAL(5,2),
    survivability_score DECIMAL(5,2),
    hallucination_debt  DECIMAL(5,2),
    competitive_score   DECIMAL(5,2),
    predictive_velocity DECIMAL(5,2),
    component_detail    JSONB
);
CREATE INDEX idx_scores_domain_time ON peterman_scores(domain_id, computed_at DESC);
```

#### hallucinations
```sql
CREATE TABLE hallucinations (
    hallucination_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain_id       UUID NOT NULL REFERENCES domains(domain_id),
    detected_at     TIMESTAMPTZ DEFAULT NOW(),
    llm_source      VARCHAR(50) NOT NULL,
    query_triggered VARCHAR(500) NOT NULL,
    false_claim     TEXT NOT NULL,
    severity_score  INTEGER CHECK (severity_score BETWEEN 1 AND 10),
    status          VARCHAR(30) DEFAULT 'open',
    assigned_brief_id UUID,
    closed_at       TIMESTAMPTZ,
    resolution_evidence TEXT
);
CREATE INDEX idx_hallucinations_domain ON hallucinations(domain_id, status);
```

#### probe_results
```sql
CREATE TABLE probe_results (
    probe_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain_id       UUID NOT NULL REFERENCES domains(domain_id),
    probed_at       TIMESTAMPTZ DEFAULT NOW(),
    llm_provider    VARCHAR(50) NOT NULL,
    query           VARCHAR(500) NOT NULL,
    run_number      INTEGER NOT NULL,
    response_text   TEXT,
    brand_mentioned BOOLEAN DEFAULT FALSE,
    mention_position INTEGER,
    sentiment       VARCHAR(20),
    confidence      DECIMAL(5,2)
);
CREATE INDEX idx_probes_domain_time ON probe_results(domain_id, probed_at DESC);
```

#### content_briefs
```sql
CREATE TABLE content_briefs (
    brief_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain_id       UUID NOT NULL REFERENCES domains(domain_id),
    source          VARCHAR(50) NOT NULL,
    trigger_id      UUID,
    target_query    VARCHAR(500),
    target_llms     JSONB,
    target_cluster  VARCHAR(255),
    channel_intent  VARCHAR(50),
    key_facts       JSONB,
    key_headings    JSONB,
    word_count_range VARCHAR(20),
    schema_type     VARCHAR(100),
    lcri_target     DECIMAL(5,2),
    sgs_delta_estimate DECIMAL(5,4),
    priority        VARCHAR(20) DEFAULT 'medium',
    status          VARCHAR(30) DEFAULT 'queued',
    alignment_score DECIMAL(5,2),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    deadline        TIMESTAMPTZ
);
```

#### deployments
```sql
CREATE TABLE deployments (
    deployment_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain_id       UUID NOT NULL REFERENCES domains(domain_id),
    action_type     VARCHAR(100) NOT NULL,
    target_url      VARCHAR(500),
    html_before     TEXT,
    html_after      TEXT,
    diff            TEXT,
    metadata_before JSONB,
    metadata_after  JSONB,
    approval_id     UUID,
    deployed_at     TIMESTAMPTZ DEFAULT NOW(),
    rollback_status VARCHAR(20) DEFAULT 'available',
    rollback_expires_at TIMESTAMPTZ,
    peterman_score_delta DECIMAL(5,2)
);
```

#### audit_log
```sql
CREATE TABLE audit_log (
    entry_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain_id       UUID NOT NULL REFERENCES domains(domain_id),
    timestamp       TIMESTAMPTZ DEFAULT NOW(),
    action_type     VARCHAR(100) NOT NULL,
    action_detail   JSONB NOT NULL,
    initiated_by    VARCHAR(50) NOT NULL,
    approval_gate   VARCHAR(20),
    approved_by     VARCHAR(100),
    approved_at     TIMESTAMPTZ,
    outcome         VARCHAR(20) DEFAULT 'pending',
    snapshot_id     UUID,
    notes           TEXT
);
-- Append-only: no UPDATE or DELETE permissions granted to application role
CREATE INDEX idx_audit_domain_time ON audit_log(domain_id, timestamp DESC);
```

#### domain_embeddings (pgvector)
```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE domain_embeddings (
    embedding_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain_id       UUID NOT NULL REFERENCES domains(domain_id),
    page_url        VARCHAR(500),
    page_title      VARCHAR(255),
    content_snippet TEXT,
    embedding       vector(768),  -- nomic-embed-text dimension
    computed_at     TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_embeddings_domain ON domain_embeddings(domain_id);
CREATE INDEX idx_embeddings_vector ON domain_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

#### budget_tracking
```sql
CREATE TABLE budget_tracking (
    tracking_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain_id       UUID NOT NULL REFERENCES domains(domain_id),
    api_provider    VARCHAR(50) NOT NULL,
    cost_aud        DECIMAL(10,4) NOT NULL,
    incurred_at     TIMESTAMPTZ DEFAULT NOW(),
    description     VARCHAR(255)
);
CREATE INDEX idx_budget_domain_time ON budget_tracking(domain_id, incurred_at DESC);
```

---

## 7. Technology Stack

| Component | Technology | Version | Why |
|-----------|-----------|---------|-----|
| Backend framework | Flask | 3.0.x | AMTL standard, lightweight, proven |
| Database | PostgreSQL | 17.x | Robust, supports pgvector extension |
| Vector store | pgvector | 0.7.x | Semantic position storage, similarity queries |
| Queue | Redis | 7.x | Fast job queuing, brief pipeline |
| Scheduler | APScheduler | 3.10.x | No Celery overhead for single-user system |
| HTTP client | httpx | 0.27.x | Async-capable, modern Python HTTP |
| HTML parser | BeautifulSoup4 | 4.12.x | Reliable HTML parsing for crawling |
| AI inference | Ollama | 0.3.x | Local LLM inference (embeddings + light tasks) |
| Embedding model | nomic-embed-text | — | 768-dim embeddings, good quality/speed ratio |
| Inference model (local) | llama3.1:8b | — | Fast scoring, classification, brief variants |
| Deep analysis model | gemma2:27b | — | Precision when speed is secondary |
| CMS integration | WordPress REST API | v2 | Largest CMS market share |
| Search | SearXNG | — | Private, local meta-search |
| Notifications | ntfy.sh | — | Simple push notifications, already in AMTL stack |
| Frontend | HTML/CSS/JS (no framework) | — | AMTL standard: no framework overhead |
| Charts | Chart.js or D3.js | — | Peterman Score gauge, sparklines, semantic map |
| PDF generation | WeasyPrint | — | Client Mode report PDF generation |
| Testing | pytest + Playwright | — | AMTL standard testing stack |

---

## 8. Configuration & Environment Variables

```bash
# --- Core ---
AMTL_PTR_PORT=5008
AMTL_PTR_SECRET_KEY=<generated>
AMTL_PTR_DEBUG=false
AMTL_PTR_LOG_LEVEL=INFO

# --- Database ---
AMTL_PTR_DB_URL=postgresql://peterman:password@localhost:5433/peterman
AMTL_PTR_REDIS_URL=redis://localhost:6379/0

# --- AI Engines ---
AMTL_PTR_OLLAMA_URL=http://localhost:9000
AMTL_PTR_CLAUDE_DESKTOP_SOCKET=/path/to/claude/mcp
AMTL_PTR_OPENAI_API_KEY=<encrypted>
AMTL_PTR_ANTHROPIC_API_KEY=<encrypted>

# --- Search ---
AMTL_PTR_SEARXNG_URL=http://localhost:8888

# --- Ecosystem ---
AMTL_PTR_ELAINE_URL=http://localhost:5000
AMTL_PTR_WORKSHOP_URL=http://localhost:5003

# --- External ---
AMTL_PTR_GSC_CREDENTIALS_PATH=/path/to/gsc-credentials.json
AMTL_PTR_NTFY_TOPIC=peterman-alerts

# --- Budget ---
AMTL_PTR_DEFAULT_WEEKLY_BUDGET_AUD=50.00
```

---

## 9. Error Handling & Resilience

### 9.1 AI Engine Failure Chain
```
Claude Desktop unavailable
  → Auto-retry 3× (5-second intervals)
  → Failover to Manus Desktop
  → If Manus unavailable: Perplexity Desktop
  → If Perplexity unavailable: Ollama (llama3.1)
  → If all unavailable: Queue task, ELAINE alerts operator
  → Never execute with degraded confidence without flagging it
```

### 9.2 CMS API Failure
```
CMS API fails during deployment
  → Immediate halt (do not partially apply changes)
  → Rollback any partial changes
  → Log failure with full payload
  → Queue for retry (6-hour intervals, max 3 retries)
  → After 3 failures: escalate to ELAINE → operator
```

### 9.3 LLM Probe API Failure
```
External LLM probe API unavailable
  → Skip that model for this cycle
  → Log as "missed probe"
  → Do not compute SoV score for that model this cycle
  → Flag score as "partial data" in dashboard
  → Never present a score as complete when data is missing
```

### 9.4 Database Failure
```
PostgreSQL unavailable
  → Peterman enters read-only degraded mode
  → No new probes, no deployments, no audit entries
  → ELAINE immediately alerted
  → Workshop shows Peterman as red
  → Auto-retry connection every 30 seconds
```

---

## 10. Security Architecture

### 10.1 Local-First Principle
- All data processing happens locally on Mani's machine
- No telemetry, no analytics, no cloud sync
- CMS API keys encrypted at rest in PostgreSQL
- External API calls (OpenAI, Anthropic) limited to weekly probe cadence

### 10.2 Data Isolation
- All tables include `domain_id` as non-nullable foreign key
- No cross-domain data joins in application code
- Cross-domain analytics computed as views only
- Client-tier users can only access their own domain's data

### 10.3 Audit Immutability
- `audit_log` table: no UPDATE or DELETE permissions for application role
- Append-only by design
- Exportable as CSV/JSON for compliance review

---

## 11. Self-Healing Registration (Workshop)

```json
{
  "app": "peterman",
  "port": 5008,
  "health_endpoint": "http://localhost:5008/api/health",
  "launch_command": {
    "backend": "python -m flask run --port 5008",
    "frontend": "electron electron/main.js"
  },
  "recovery": {
    "tier_1_simple": "restart flask process",
    "tier_2_deep": "restart flask + verify postgresql + redis connections",
    "tier_3_full": "kill all peterman processes + clear redis queue + restart"
  },
  "dependencies": ["postgresql", "redis", "ollama", "supervisor"],
  "favicon": "static/img/favicon.svg"
}
```

---

## 12. Known Technical Debt

| Item | Description | Priority |
|------|-------------|----------|
| Claude Desktop MCP integration | Integration method depends on Claude Desktop MCP availability — may need clipboard bridge fallback | High |
| CMS integration beyond WordPress | Webflow, Ghost, and custom webhook integrations are Phase 3+ | Medium |
| 3D Semantic Galaxy | Phase 3 stretch goal — depends on three.js performance in Electron | Low |
| Fine-tuned brief model | Requires 100+ completed briefs before training — Phase 3 | Low |
| GSC API integration | Requires OAuth setup and domain verification | Medium |

---

## 13. Build Phase Status

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 0 | Foundation — multi-domain schema, onboarding, probe normalisation, rollback, audit, budget, basic War Room | ⬜ Not started |
| Phase 1 | Core Loop — Chambers 1, 5, 6, 10, approval gates, ELAINE integration | ⬜ Not started |
| Phase 2 | Intelligence — Chambers 2, 3, 7, 8, 9, 11, semantic map | ⬜ Not started |
| Phase 3 | Advanced — consensus score, stickiness, authority decay, fine-tuned model, client mode PDF, public audit tool | ⬜ Not started |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 18 February 2026 | Claude (Thalaiva) | Initial TDD — architecture, APIs, data model, technology stack |

---

*Almost Magic Tech Lab*
*"The blueprint. Could Guruve build it from this alone? That's the test."*
