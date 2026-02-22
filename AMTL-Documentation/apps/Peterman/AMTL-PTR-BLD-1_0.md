# AMTL — Peterman Build Guide
## Document Code: AMTL-PTR-BLD-1.0
## Almost Magic Tech Lab
## 18 February 2026

> *This document follows AMTL-ECO-STD v1.0. All conventions defined there apply unless explicitly overridden with a Decision Register entry.*

---

## Critical Rules — Read Before Building

| Rule | Detail |
|------|--------|
| **Language** | Australian English everywhere — colour, organisation, licence, honour, defence |
| **No duplicates** | ONE root folder. Never create a "v2" alongside "v1". If unsure where something goes, STOP AND ASK. |
| **Dark default** | AMTL Midnight #0A0E14 default, dark/light toggle in header |
| **Port** | 5008 — do not change without Decision Register entry |
| **GitHub** | All code to Almost-Magic/peterman — every meaningful change committed |
| **Testing** | All 7 test types at every phase checkpoint. A failing test is a blocker, not a warning. |
| **Documentation** | Google-style docstrings on every module, class, and function. 30-second rule: if a developer can't understand a function in 30 seconds, docs are insufficient. |
| **No terminal noise** | Clean startup. No visible terminal windows. Errors in app UI, not stdout. |
| **Env vars** | All config in `.env`. Variable naming: `AMTL_PTR_[SETTING]` |

---

## Testing Mandate

**Do not skip any test type. Do not defer testing to the final phase.**

| Test Type | When to Run | What It Checks |
|-----------|-------------|----------------|
| **Beast** (pytest) | ✅ Every phase | Core functionality, happy paths |
| **Inspector** (flake8/pylint) | ✅ Every phase | Code quality, zero warnings |
| **4% Edge Cases** | ✅ Every phase | Unusual inputs, failures, empty data, boundaries |
| **Proof/Playwright** | UI phases only | Screenshots verifying rendering |
| **Smoke** | ✅ Every phase | "Does it start and respond?" |
| **Regression** | ✅ After Phase 1 | All previous tests still pass |
| **Integration** | When touching other apps | Cross-app communication works |

---

## Phase 0: Foundation (Weeks 1–4)

### 0.1 Environment Setup

1. **Audit existing codebase** at `/home/amtl/claudeman-cases/DSph2/peterman`
   - Run `python -m pytest tests/ -v` — record current pass rate
   - Identify reusable components (AI engine, crawling, Flask structure)
   - Identify components that must be rebuilt (data model, multi-domain schema)
   - Log findings in AMTL-PTR-DEC-1.0
2. **Create folder structure** per AMTL-ECO-STD Section 6.6 (see AMTL-PTR-TDD-1.0 Section 4.1 for Peterman-specific layout)
3. **Create `.env.example`** with all variables from AMTL-PTR-TDD-1.0 Section 8
4. **Create `.env`** with real values (gitignored)
5. **Create `requirements.txt`** with pinned versions:
   ```
   flask==3.0.2
   flask-cors==4.0.0
   psycopg2-binary==2.9.9
   sqlalchemy==2.0.25
   redis==5.0.1
   apscheduler==3.10.4
   httpx==0.27.0
   beautifulsoup4==4.12.3
   python-dotenv==1.0.1
   weasyprint==61.2
   ```
6. **Create `.gitignore`** — include `.env`, `logs/`, `__pycache__/`, `*.pyc`
7. **Initialise Git** — push to Almost-Magic/peterman

### 0.2 Database Setup

1. **Start PostgreSQL** (port 5433) — Docker container if not already running
2. **Create peterman database:**
   ```sql
   CREATE DATABASE peterman;
   CREATE USER peterman_app WITH PASSWORD 'secure_password';
   GRANT CONNECT ON DATABASE peterman TO peterman_app;
   ```
3. **Enable pgvector extension:**
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
4. **Create all tables** from AMTL-PTR-TDD-1.0 Section 6:
   - `domains`
   - `peterman_scores`
   - `hallucinations`
   - `probe_results`
   - `content_briefs`
   - `deployments`
   - `audit_log` (with INSERT-only permissions for peterman_app role)
   - `domain_embeddings`
   - `budget_tracking`
5. **Create indexes** as specified in TDD
6. **Verify pgvector** — test vector insertion and cosine similarity query
7. **Start Redis** (port 6379) — Docker container if not already running

### 0.3 Flask App Foundation

1. **Create Flask app factory** (`app/__init__.py`)
2. **Create health endpoint** (`app/routes/health.py`) — returns real dependency status for PostgreSQL, Redis, Ollama, SearXNG, ELAINE, Workshop
3. **Create domain routes** (`app/routes/domains.py`) — CRUD for Domain Object
4. **Create audit logger** (`app/services/audit.py`) — append-only logging to audit_log table
5. **Create budget monitor** (`app/services/budget_monitor.py`) — per-domain cost tracking with 80%/100% thresholds
6. **Create SPA shell** (`app/templates/index.html`) — AMTL Midnight theme, dark/light toggle, basic navigation
7. **Create favicon** (`app/static/img/favicon.svg`)

### 0.4 Probe Normalisation Protocol

1. **Create probe engine** (`app/services/probe_engine.py`)
   - Standard probe specification: temperature 0.0, top_p 1.0, runs_per_query 5
   - Versioned system prompt (PETERMAN_STANDARD_SYSTEM_PROMPT)
   - 30-second timeout per probe call
   - Compute: mention consistency, position consistency, sentiment consistency, composite confidence
2. **Create embedding engine** (`app/services/embedding_engine.py`)
   - Uses nomic-embed-text via Ollama (through Supervisor :9000)
   - Batch embedding support
   - Store results in domain_embeddings table

### 0.5 AI Engine with Fallback Chain

1. **Create AI engine** (`app/services/ai_engine.py`)
   - Primary: Claude Desktop (MCP or clipboard bridge — test during this phase)
   - Fallback chain: Manus → Perplexity → Ollama → queue + alert
   - Auto-retry 3× with 5-second intervals before failover
   - Log every engine switch in audit trail
   - Task-to-engine routing map (per AMTL-PETERMAN-SPC-2.0 Part 1 Section 5.3)

### 0.6 Rollback Layer

1. **Create deployment model** (`app/models/deployment.py`)
   - Snapshot specification: pre/post HTML, unified diff, metadata
   - 30-day retention with automatic expiry
   - Rollback status: available → used → expired
2. **Create rollback service** (`app/services/deployment_engine.py` — rollback portion)
   - One-click rollback logic
   - Audit trail logging for every rollback

### 0.7 Basic War Room (Domain Cards Only)

1. **Create War Room HTML/CSS/JS** — multi-domain view
   - Domain Card component showing: domain name, Peterman Score (placeholder), status, last action
   - AMTL colour scheme: Midnight background, Gold accents
   - Responsive layout (cards grid)
2. **Create Peterman Score gauge** (`app/static/js/score-gauge.js`)
   - Circular gauge with colour shift: 0–40 red, 40–65 amber, 65–85 gold, 85–100 platinum
   - Placeholder data for now — live data in Phase 1

### Phase 0 Checkpoint

| Test Type | Required | Details |
|-----------|----------|---------|
| Beast | ✅ | Domain CRUD, health endpoint, audit logger, budget monitor, probe engine, embedding engine, AI engine fallback chain |
| Inspector | ✅ | Zero warnings on all new code |
| 4% Edge Cases | ✅ | Empty domain name, invalid UUID, database connection failure, Ollama unavailable, budget at 0 |
| Proof/Playwright | ✅ | Screenshot: War Room with Domain Cards, dark theme, health endpoint JSON |
| Smoke | ✅ | Flask starts on 5008, /api/health responds, frontend loads |
| Regression | N/A | First phase |
| Integration | ✅ | PostgreSQL connection, Redis connection, Ollama ping, pgvector query |

**Gate:** All tests pass → GitHub push → Phase 1.

---

## Phase 1: Core Loop (Weeks 5–10)

### 1.1 Chamber 1 — Perception Engine

1. **Create Chamber 1** (`app/chambers/chamber_01_perception.py`)
   - Multi-LLM probing using probe_engine
   - SoV computation per LLM provider
   - Cross-model comparison
   - Persona Presence Metric (persona-framed queries)
2. **Create Hallucination Registry model** (`app/models/hallucination.py`)
   - Jira-style tracking: detected → brief_generated → content_deployed → verified_closed → suppressed
   - Four-dimension severity scoring: financial impact, LLM confidence language, mention prominence, cross-LLM frequency
3. **Hallucination detection logic** — auto-detect false claims by comparing LLM responses against domain facts

### 1.2 Chamber 5 — Hallucination Autopilot

1. **Create Chamber 5** (`app/chambers/chamber_05_hallucination.py`)
   - The Autopilot Loop: DETECT → ANALYSE → BRIEF → COMMISSION → APPROVE → DEPLOY → VERIFY → REPORT
   - Uses Claude Desktop for "What true content would prevent this hallucination?"
   - Cross-reference existing content map (cannibalization check via embeddings)
   - 48-hour verification cycle after deployment

### 1.3 Chamber 6 — Technical Foundation

1. **Create Chamber 6** (`app/chambers/chamber_06_technical.py`)
   - Crawl site: Core Web Vitals, robots.txt, sitemap.xml, schema markup, broken links
   - Agent-Ready Manifest generation (`/agent-manifest.json`)
   - Autonomous technical actions with risk-level classification
   - Dry-run sandbox: generate HTML diff, synthetic preview before live deploy

### 1.4 Chamber 10 — The Forge (Content Brief Engine)

1. **Create Chamber 10** (`app/chambers/chamber_10_forge.py`)
   - Full brief structure per AMTL-PETERMAN-SPC-2.0 Part 2 Section (Chamber 10)
   - Channel-aware, LLM-persona-calibrated briefs
   - Multi-agent brief review: Critic (Mistral), Defender (Llama3.1), Scorer (Mistral) via Ollama
   - Brief-to-content alignment scoring
2. **Create content brief model** (`app/models/brief.py`)

### 1.5 Approval Gate System

1. **Create approval routes** (`app/routes/approvals.py`)
   - Five gate levels: auto-deploy, low-gate, medium-gate, hard-gate, prohibited
   - Risk classification per action type
   - Approval/rejection with reason capture
   - Approval card generation for ELAINE

### 1.6 ELAINE Integration

1. **Create ELAINE routes** (`app/routes/elaine.py`)
   - Status endpoint: ELAINE queries Peterman status
   - Score endpoint: current Peterman Score
   - Brief queue endpoint: pending briefs
   - Approval forwarding: ELAINE sends operator's yes/no
   - Content-complete notification: ELAINE notifies when content is written
2. **Create outbound ELAINE service** (`app/services/notification.py`)
   - Submit content briefs to ELAINE queue
   - Send critical alerts
   - Send approval requests with voice scripts (low/medium/hard gate)

### 1.7 Domain Onboarding Flow

1. **Complete onboarding endpoint** (`POST /api/domains/<id>/onboard`)
   - Crawl domain: detect CMS, schema, sitemap, robots.txt, page count, language
   - Run Chamber 6 technical baseline
   - Run first LLM probe set (5 queries × 5 runs)
   - Generate Domain Health Card with initial Peterman Score
   - Notify ELAINE: "Onboarding complete for [domain]. Initial score: [X]."

### 1.8 Scheduler Integration

1. **Configure APScheduler** (`app/services/scheduler.py`)
   - Per-domain probe cadence (daily or weekly as configured)
   - Chamber cycle scheduling
   - Budget check schedule (hourly)

### Phase 1 Checkpoint

| Test Type | Required | Details |
|-----------|----------|---------|
| Beast | ✅ | All 4 chambers (monitor, analyse, plan, execute, verify), hallucination CRUD, approval CRUD, onboarding flow, ELAINE integration |
| Inspector | ✅ | Zero warnings |
| 4% Edge Cases | ✅ | Hallucination with severity 0 and 11, empty probe response, LLM timeout mid-probe, approval of nonexistent action, ELAINE unavailable during brief submission |
| Proof/Playwright | ✅ | Screenshot: War Room with live Domain Card, approval inbox, hallucination list |
| Smoke | ✅ | Full startup, all endpoints respond, scheduler runs |
| Regression | ✅ | All Phase 0 tests still pass |
| Integration | ✅ | ELAINE brief submission, Ollama probing, Claude Desktop AI call, CMS dry-run |

**Gate:** All tests pass → GitHub push → Phase 2.

---

## Phase 2: Intelligence (Weeks 11–16)

### 2.1 Chamber 2 — Semantic Gravity

1. **Create Chamber 2** (`app/chambers/chamber_02_semantic.py`)
   - Formalised SGS methodology: cluster definition (50 queries), domain embedding, gravity score, drift delta, competitor benchmarking
   - Semantic Neighbourhood Visualisation (2D scatter, UMAP reduction)
   - Vector Space Influence Projection (pre-publish SGS delta estimate)

### 2.2 Chamber 3 — Content Survivability Lab

1. **Create Chamber 3** (`app/chambers/chamber_03_survivability.py`)
   - LCRI four-test methodology: Direct Summarisation, Citation Probability, Extractable Snippet Strength, RAG Chunk Compatibility
   - Adversarial Survivability Test (Ollama Mistral as hostile LLM)
   - LCRI scores tagged with model version

### 2.3 Chamber 4 — Authority & Backlink Intelligence

1. **Create Chamber 4** (`app/chambers/chamber_04_authority.py`)
   - LLM Citation Authority (LCA) scoring for backlink targets
   - Backlink Mini-CRM
   - Semantic Contamination Detector

### 2.4 Chamber 7 — The Amplifier (Content Performance Loop)

1. **Create Chamber 7** (`app/chambers/chamber_07_amplifier.py`)
   - Authority Flywheel: track SoV delta, SGS delta, LCRI actual vs predicted, GSC data
   - Citation Velocity Model: Day 0 → Day 7 → Day 30 → Day 90 tracking
   - Content Cannibalization Prevention (embedding similarity check)

### 2.5 Chamber 8 — Competitive Shadow Mode

1. **Create Chamber 8** (`app/chambers/chamber_08_competitive.py`)
   - Shadow Mode Loop: monitor → analyse → respond (threat 1–5 levels)
   - Competitor LCA tracking (weekly)
   - Semantic Territory Map
   - Competitive Gap Analysis (uncontested semantic spaces)

### 2.6 Chamber 9 — The Oracle

1. **Create Chamber 9** (`app/chambers/chamber_09_oracle.py`)
   - Signal inputs: Google Trends, emerging LLM query patterns, regulatory signals, competitor velocity, social discussion, Chamber 7 performance data
   - 90-day content calendar generation
   - Campaign Mode activation
   - Human feedback loop for rejected predictions

### 2.7 Chamber 11 — Defensive Perception Shield

1. **Create Chamber 11** (`app/chambers/chamber_11_defensive.py`)
   - Threat detection: negative association scan, narrative drift scan, competitor mention poisoning, semantic contamination
   - Response protocols: Low → Medium → High → Critical
   - Honeypot detection (traceable facts, detection only)

### 2.8 War Room Enhancements

1. **Chamber Map** — radial grid of all 11 chambers with status (green/amber/red pulse)
2. **Active Alerts Panel** — real-time feed sorted by severity
3. **LLM Answer Diff View** — side-by-side 30-day comparison
4. **Semantic Neighbourhood Map** — 2D scatter plot (domain vs competitors)
5. **Journey Timeline** — chronological action record with rollback buttons

### Phase 2 Checkpoint

| Test Type | Required | Details |
|-----------|----------|---------|
| Beast | ✅ | All 11 chambers fully tested, SGS computation, LCRI scoring, competitive analysis, Oracle predictions |
| Inspector | ✅ | Zero warnings |
| 4% Edge Cases | ✅ | Empty competitor list, SGS with single data point, LCRI on 10-word page, Oracle with no signal data, defensive scan on clean domain |
| Proof/Playwright | ✅ | Screenshot: full War Room (chamber map, alerts, Semantic Map, Journey Timeline, LLM Diff View) |
| Smoke | ✅ | Full startup, all 11 chambers respond, scheduler runs all cycles |
| Regression | ✅ | All Phase 0 + Phase 1 tests still pass |
| Integration | ✅ | Full ELAINE integration (briefs, approvals, status), GSC API (if configured), SearXNG competitor monitoring |

**Gate:** All tests pass → GitHub push → Phase 3.

---

## Phase 3: Advanced (Weeks 17–24)

### 3.1 Innovative Feature Stack
1. Multi-LLM Consensus Presence Score
2. Zero-Click Authority Index
3. Conversation Stickiness Score
4. LLM Influence Forecast (SGS Projection)
5. Authority Decay Detection
6. Retrain-Pulse Watcher

### 3.2 Advanced Capabilities
1. Fine-tuned brief generation model (after 100+ data points from Chamber 7)
2. CMS integration: Webflow API, Ghost Content API, GitHub API (static sites), custom webhook
3. Client Mode PDF report export (WeasyPrint)
4. Free LLM Presence Audit tool (public-facing, limited probe)
5. Mobile approval experience refinement
6. 3D Semantic Galaxy (stretch goal)

### 3.3 Context-Aware Help

1. **Create help content** (`app/help.py`) per AMTL-ECO-CTX-1.0
   - Help for every screen: War Room, Domain Card, Approval Inbox, Journey Timeline, each Chamber detail view
   - `?` key trigger, `(?)` icon in header, first-visit tooltips
   - Keyboard shortcuts listed

### Phase 3 Checkpoint

| Test Type | Required | Details |
|-----------|----------|---------|
| Beast | ✅ | All new features tested |
| Inspector | ✅ | Zero warnings |
| 4% Edge Cases | ✅ | Consensus score with one model unavailable, stickiness test with brand not mentioned, PDF generation with missing data |
| Proof/Playwright | ✅ | Screenshot: Client Mode PDF, mobile approval view, help panel |
| Smoke | ✅ | Full startup, all features respond |
| Regression | ✅ | All previous phase tests still pass |
| Integration | ✅ | Full ecosystem integration: ELAINE, Workshop, CK Writer, all CMS integrations |

**Gate:** All tests pass → GitHub push → Workshop registration → Documentation final check → Peterman v2.0 live.

---

## Final Verification Checklist

- [ ] All 7 test types passing (Beast, Inspector, 4%, Proof, Smoke, Regression, Integration)
- [ ] `/api/health` returns green for all dependencies
- [ ] All 11 chambers return real data within 30 seconds of domain submission
- [ ] Content brief successfully reaches ELAINE queue
- [ ] Deployed change verifiable within 5 minutes of autonomous action
- [ ] Rollback works within 30 seconds of trigger
- [ ] Audit log is append-only and exportable
- [ ] Budget monitor pauses probing at 100% cap
- [ ] War Room renders correctly in Electron (dark and light mode)
- [ ] Context-aware help available on every screen
- [ ] GitHub repo is current (no local-only code)
- [ ] README.md is complete
- [ ] CHANGELOG.md is current
- [ ] USER-MANUAL.md is current
- [ ] Workshop registration is complete
- [ ] Australian English throughout (no "color", "organization")

---

## Cline Command Block

Paste this into Cline to start the build:

```
Read the following documents in order, then build Peterman Phase 0 exactly as specified:

1. AMTL-ECO-STD-1.0 — The engineering constitution. Follow all standards.
2. AMTL-PTR-SPC-1.0 — What Peterman does and why. Understand the product.
3. AMTL-PTR-TDD-1.0 — How it's designed. Architecture, APIs, data model. Follow this as the blueprint.
4. AMTL-PTR-DEC-1.0 — Decisions already made. Do not re-debate these.
5. AMTL-PTR-KNW-1.0 — Known issues to avoid and work around.
6. AMTL-PTR-BLD-1.0 — The build guide. Follow Phase 0 step by step.

Also reference the full product specifications for chamber detail:
- AMTL-PETERMAN-SPC-1.0 (original spec)
- AMTL-PETERMAN-SPC-2.0 Part 1 (v2 foundation, chambers 1–6)
- AMTL-PETERMAN-SPC-2.0 Part 2 (v2 chambers 7–10, defensive mode, UI, go-to-market)

Critical rules:
- Australian English everywhere (colour, organisation, licence)
- Port 5008 — do not change
- Dark theme default (AMTL Midnight #0A0E14)
- Google-style docstrings on every module, class, and function
- All config in .env (variable naming: AMTL_PTR_[SETTING])
- No duplicate folders. ONE canonical location for everything.
- Run ALL test types at the Phase 0 checkpoint before proceeding.
- Push to Almost-Magic/peterman on GitHub.

Start with Phase 0 Section 0.1: audit the existing codebase, then proceed through 0.2–0.7 in order.
```

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 18 February 2026 | Claude (Thalaiva) | Initial build guide — 4 phases, all test checkpoints, Cline command |

---

*Almost Magic Tech Lab*
*"Phase by phase. Test by test. No shortcuts. No bypasses."*
