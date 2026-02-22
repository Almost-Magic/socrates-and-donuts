# PETERMAN STATUS AUDIT — PASTE INTO CLINE
# Date: 20 February 2026
# Priority: CRITICAL — Before Mani starts using the app

STOP. Do not build anything new yet.

Mani wants to know: "Is Peterman actually working as designed?"

The answer he needs is honest. Not "tasks completed" — but "does the 
product actually do what the spec says it should do?"

Here is what Peterman MUST do (from AMTL-PTR-SPC-1.0):

1. Mani enters a domain name (e.g., almostmagic.net.au)
2. Peterman crawls the site and understands what the business does
3. Peterman suggests target keywords/queries for that domain
4. Mani approves the keywords
5. Peterman probes ChatGPT, Claude, Perplexity, Gemini with those 
   queries to see if/how the domain is mentioned (LLM Share of Voice)
6. Peterman detects hallucinations (AI saying wrong things about the domain)
7. Peterman generates content briefs to fix gaps
8. Mani approves the briefs
9. Peterman deploys fixes to the website (WordPress API)
10. Peterman verifies the impact (re-probes, checks if ranking improved)
11. Repeat continuously — autonomous with approval gates

This is the CORE WORKFLOW. Without this, Peterman is just a config page.

---

## AUDIT PART 1: What exists vs what's needed

Check every item below. For each, open the actual code file and determine
if it is REAL CODE or a STUB/PLACEHOLDER.

### Core Workflow Components:

| # | Component | File(s) | Status | Real or Stub? |
|---|-----------|---------|--------|---------------|
| 1 | Domain onboarding (add domain, crawl, detect CMS) | ? | ? | ? |
| 2 | Keyword/query suggestion engine | ? | ? | ? |
| 3 | LLM probing engine (query ChatGPT/Claude/Perplexity/Gemini) | ? | ? | ? |
| 4 | Probe normalisation (5 runs per query, averaging) | ? | ? | ? |
| 5 | Peterman Score calculation (7 components, weighted) | ? | ? | ? |
| 6 | Hallucination detection | ? | ? | ? |
| 7 | Hallucination Autopilot (detect → brief → deploy → verify) | ? | ? | ? |
| 8 | Content brief generation (The Forge) | ? | ? | ? |
| 9 | Approval Gate system (5 levels) | ? | ? | ? |
| 10 | CMS deployment (WordPress REST API) | ? | ? | ? |
| 11 | Rollback layer (pre/post snapshots, one-click undo) | ? | ? | ? |
| 12 | Semantic Gravity Score (embedding-based positioning) | ? | ? | ? |
| 13 | Content Survivability Lab (LCRI scoring) | ? | ? | ? |
| 14 | Competitive Shadow Mode (monitor competitors) | ? | ? | ? |
| 15 | The Oracle (predictive forecasting) | ? | ? | ? |
| 16 | Defensive Perception Shield (reputation monitoring) | ? | ? | ? |
| 17 | Budget monitor (per-domain weekly caps) | ? | ? | ? |

### UI/Dashboard:

| # | Screen | Exists? | Functional? |
|---|--------|---------|-------------|
| 1 | War Room (main dashboard with domain cards) | ? | ? |
| 2 | Chamber Map (11 chambers with pulse indicators) | ? | ? |
| 3 | Approval Inbox (approve/decline/modify) | ? | ? |
| 4 | Journey Timeline (chronological action log) | ? | ? |
| 5 | Peterman Score gauge (circular, colour-shifting) | ? | ? |
| 6 | Hallucination Registry view | ? | ? |
| 7 | Semantic Neighbourhood Map (D3.js) | ? | ? |
| 8 | LLM Answer Diff View | ? | ? |
| 9 | Domain onboarding form | ? | ? |
| 10 | Settings page | ? | ? |

### AI Engine:

| # | Component | Status |
|---|-----------|--------|
| 1 | Claude Desktop as PRIMARY AI (per DEC-003) | ? |
| 2 | Fallback chain: Claude Desktop → Manus → Perplexity → Ollama | ? |
| 3 | Ollama for embeddings ONLY (nomic-embed-text, per DEC-004) | ? |
| 4 | LLM cascade implementation (not just Ollama for everything) | ? |

### Integrations:

| # | Integration | Status |
|---|-------------|--------|
| 1 | ELAINE (briefs, approvals, voice queries) | ? |
| 2 | CK Writer (content writing from briefs) | ? |
| 3 | Workshop (health, launch/stop) | ? |
| 4 | Supervisor (GPU scheduling for Ollama) | ? |
| 5 | WordPress REST API (deployment) | ? |
| 6 | Google Search Console (CTR data) | ? |
| 7 | ntfy.sh (mobile push notifications) | ? |

---

## AUDIT PART 2: AI Engine Configuration

This is CRITICAL. Per DEC-003 and DEC-004:

- Claude Desktop (via MCP or clipboard bridge) = PRIMARY for all complex 
  reasoning: hallucination analysis, content briefs, strategic synthesis
- Ollama (via Supervisor :9000) = ONLY for embeddings (nomic-embed-text)
  and light classification tasks
- External APIs (OpenAI, Anthropic) = for PROBING target LLMs to measure 
  Share of Voice, NOT for Peterman's own reasoning

Check the code:
1. Is there a Claude Desktop integration? (MCP socket or clipboard bridge)
2. Is there a fallback chain implemented? 
3. Is Ollama being used for reasoning tasks it shouldn't be doing?
4. Are external API calls (OpenAI, Anthropic) being used for probing 
   the target LLMs (correct) or for Peterman's own intelligence (incorrect)?

Show me the actual code that handles AI routing.

---

## AUDIT PART 3: Database Tables

The spec requires these tables (from TDD-1.0):
- domains
- target_queries (keywords per domain)
- probe_results (LLM responses, 5 runs per query)
- peterman_scores (composite scores over time)
- hallucinations (detected false claims)
- content_briefs (generated briefs)
- deployments (CMS changes with pre/post snapshots)
- audit_log (immutable, append-only)
- budget_tracking (per-domain spend)
- domain_embeddings (pgvector, semantic positioning)
- competitor_domains (shadow mode targets)
- scheduled_tasks (APScheduler jobs)

Run this:
```sql
\dt
```
Show me every table that exists. Compare against the list above.
Which tables are missing?

---

## AUDIT PART 4: API Endpoints

List every endpoint that exists in the Flask app:
```python
# Find all routes
from app import create_app
app = create_app()
for rule in app.url_map.iter_rules():
    print(f"{rule.methods} {rule.rule}")
```

Compare against what's needed:

Required endpoints (minimum):
- POST /api/domains — onboard a new domain
- GET /api/domains — list all domains
- GET /api/domains/<id> — domain detail
- GET /api/domains/<id>/score — current Peterman Score
- POST /api/domains/<id>/probe — trigger LLM probe
- GET /api/domains/<id>/probes — probe results
- GET /api/domains/<id>/hallucinations — hallucination list
- POST /api/domains/<id>/hallucinations/<id>/brief — generate correction brief
- GET /api/domains/<id>/briefs — content briefs
- POST /api/domains/<id>/briefs/<id>/approve — approve a brief
- POST /api/domains/<id>/deploy — deploy approved changes
- POST /api/domains/<id>/rollback/<deployment_id> — rollback a deployment
- GET /api/domains/<id>/timeline — journey timeline
- GET /api/domains/<id>/approvals — pending approvals
- POST /api/domains/<id>/approvals/<id>/approve — approve
- POST /api/domains/<id>/approvals/<id>/decline — decline
- GET /api/domains/<id>/budget — budget status
- GET /api/domains/<id>/competitors — competitor list
- GET /api/domains/<id>/chambers/<n> — chamber detail
- GET /api/health — health check

---

## OUTPUT

Produce a document called PETERMAN-AUDIT-2026-02-20.md with:

### Section 1: Core Workflow — What Works
For each of the 17 core components, state: EXISTS / STUB / MISSING

### Section 2: UI — What Works  
For each of the 10 screens, state: EXISTS / STUB / MISSING

### Section 3: AI Engine — Current vs Required
Show what the code currently does vs what DEC-003/DEC-004 require

### Section 4: Database — Tables Present vs Required
Show which tables exist and which are missing

### Section 5: API Endpoints — Present vs Required
Show which endpoints exist and which are missing

### Section 6: Honest Assessment
Answer this question directly: 
"Can Mani enter a domain name right now and have Peterman do anything 
useful with it?"

### Section 7: What Needs to Be Built
Prioritised list of what's missing, in build order.

DO NOT FIX ANYTHING. AUDIT ONLY. Be completely honest.
