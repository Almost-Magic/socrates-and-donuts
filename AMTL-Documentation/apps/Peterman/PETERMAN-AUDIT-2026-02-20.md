# PETERMAN STATUS AUDIT
**Date:** 20 February 2026  
**Status:** CRITICAL — Core Workflow NOT Functional

---

## SECTION 1: CORE WORKFLOW — WHAT WORKS

| # | Component | Status | Real or Stub? | Notes |
|---|-----------|--------|---------------|-------|
| 1 | Domain onboarding (add domain, crawl, detect CMS) | PARTIAL | REAL + STUB | POST /api/domains works but crawling/CMS detection not implemented |
| 2 | Keyword/query suggestion engine | MISSING | — | No endpoint to generate target keywords |
| 3 | LLM probing engine (query ChatGPT/Claude/Perplexity/Gemini) | PARTIAL | STUB | probe_engine.py exists but query_llm → ai_engine → Ollama fallback only |
| 4 | Probe normalisation (5 runs per query, averaging) | STUB | STUB | Code exists (run_probe_batch with num_runs=5) but analysis() is placeholder |
| 5 | Peterman Score calculation (7 components, weighted) | PARTIAL | STUB | Score engine exists but 5 of 7 components return hardcoded 50.0 |
| 6 | Hallucination detection | MISSING | — | Hallucination model exists but no detection logic |
| 7 | Hallucination Autopilot (detect → brief → deploy → verify) | MISSING | — | No automation loop |
| 8 | Content brief generation (The Forge) | MISSING | — | ContentBrief model exists but no generation logic |
| 9 | Approval Gate system (5 levels) | MISSING | — | No approval workflow implemented |
| 10 | CMS deployment (WordPress REST API) | MISSING | — | Deployment model exists but no WP API integration |
| 11 | Rollback layer (pre/post snapshots, one-click undo) | MISSING | — | No rollback logic |
| 12 | Semantic Gravity Score (embedding-based positioning) | STUB | STUB | Returns hardcoded 50.0 |
| 13 | Content Survivability Lab (LCRI scoring) | STUB | STUB | Returns hardcoded 50.0 |
| 14 | Competitive Shadow Mode (monitor competitors) | MISSING | — | No competitor tracking |
| 15 | The Oracle (predictive forecasting) | STUB | STUB | Returns hardcoded 50.0 |
| 16 | Defensive Perception Shield (reputation monitoring) | MISSING | — | No reputation monitoring |
| 17 | Budget monitor (per-domain weekly caps) | PARTIAL | REAL | Basic tracking exists, no enforcement |

**Summary:** 2 REAL, 6 STUB, 9 MISSING

---

## SECTION 2: UI — WHAT WORKS

| # | Screen | Status | Notes |
|---|--------|--------|-------|
| 1 | War Room (main dashboard with domain cards) | UNKNOWN | No frontend code examined yet |
| 2 | Chamber Map (11 chambers with pulse indicators) | STUB | Returns placeholder chambers with status='pending' |
| 3 | Approval Inbox (approve/decline/modify) | MISSING | No approval endpoints |
| 4 | Journey Timeline (chronological action log) | MISSING | No timeline endpoint |
| 5 | Peterman Score gauge (circular, colour-shifting) | MISSING | No frontend |
| 6 | Hallucination Registry view | MISSING | No hallucinations endpoint |
| 7 | Semantic Neighbourhood Map (D3.js) | MISSING | No frontend |
| 8 | LLM Answer Diff View | MISSING | No frontend |
| 9 | Domain onboarding form | PARTIAL | API exists, frontend unknown |
| 10 | Settings page | UNKNOWN | No frontend examined |

---

## SECTION 3: AI ENGINE — CURRENT VS REQUIRED

### What DEC-003/DEC-004 Require:
- **Claude Desktop** (via MCP) = PRIMARY for complex reasoning
- **Ollama** (via Supervisor :9000) = ONLY for embeddings (nomic-embed-text)
- **External APIs** (OpenAI, Anthropic) = for PROBING target LLMs (not Peterman's reasoning)

### What the Code Actually Does:

```python
# From ai_engine.py
AI_ENGINE_CHAIN = [
    {'name': 'claude_desktop', 'priority': 1, 'type': 'mcp'},
    {'name': 'manus_desktop', 'priority': 2, 'type': 'mcp'},
    {'name': 'perplexity_desktop', 'priority': 3, 'type': 'mcp'},
    {'name': 'ollama', 'priority': 4, 'type': 'http'},
]

def call_mcp(engine_name: str, prompt: str, system_prompt: str = None) -> str:
    """Call MCP-enabled engine - falls back to Ollama."""
    logger.warning(f"MCP for {engine_name} not implemented, using Ollama fallback")
    return call_ollama(prompt, system_prompt)
```

**Problems:**
1. ❌ MCP is NOT implemented — falls back to Ollama for everything
2. ❌ Ollama is being used for reasoning tasks (wrong — should only be embeddings)
3. ❌ No actual Claude Desktop integration
4. ❌ No external API calls for probing target LLMs
5. ❌ Embedding engine exists but Ollama not running (nomic-embed-text won't work)

---

## SECTION 4: DATABASE — TABLES PRESENT VS REQUIRED

### Tables Created (9):
```
✅ domains
✅ probe_results
✅ peterman_scores
✅ hallucinations
✅ content_briefs
✅ deployments
✅ audit_log
✅ budget_tracking
✅ domain_embeddings
```

### Tables Missing from TDD-1.0:
```
❌ target_queries (keywords per domain)
❌ competitor_domains (shadow mode targets)
❌ scheduled_tasks (APScheduler jobs)
```

---

## SECTION 5: API ENDPOINTS — PRESENT VS REQUIRED

### Endpoints That Exist:
```
GET  /api/domains                          ✅
POST /api/domains                          ✅
GET  /api/domains/<id>                    ✅
DELETE /api/domains/<id>                  ✅
GET  /api/domains/<id>/score             ✅
GET  /api/domains/<id>/chambers          ✅ (returns placeholders)
GET  /api/health                          ✅
```

### Endpoints Missing:
```
❌ POST /api/domains/<id>/probe           — trigger LLM probe
❌ GET  /api/domains/<id>/probes         — probe results
❌ GET  /api/domains/<id>/hallucinations — hallucination list
❌ POST /api/domains/<id>/hallucinations/<id>/brief — generate correction brief
❌ GET  /api/domains/<id>/briefs         — content briefs
❌ POST /api/domains/<id>/briefs/<id>/approve — approve a brief
❌ POST /api/domains/<id>/deploy         — deploy approved changes
❌ POST /api/domains/<id>/rollback/<deployment_id> — rollback
❌ GET  /api/domains/<id>/timeline       — journey timeline
❌ GET  /api/domains/<id>/approvals      — pending approvals
❌ POST /api/domains/<id>/approvals/<id>/approve — approve
❌ POST /api/domains/<id>/approvals/<id>/decline — decline
❌ GET  /api/domains/<id>/budget         — budget status
❌ GET  /api/domains/<id>/competitors    — competitor list
```

---

## SECTION 6: HONEST ASSESSMENT

### Can Mani enter a domain name right now and have Peterman do anything useful with it?

**NO.** 

Here's what happens if Mani adds a domain today:

1. ✅ Mani CAN add a domain via POST /api/domains
2. ❌ Peterman CANNOT crawl the site (no crawler implemented)
3. ❌ Peterman CANNOT suggest keywords (no keyword engine)
4. ❌ Peterman CANNOT probe LLMs (MCP not implemented, falls back to Ollama which isn't running)
5. ❌ Peterman CANNOT detect hallucinations (model exists but no detection logic)
6. ❌ Peterman CANNOT generate content briefs (no brief generation)
7. ❌ Peterman CANNOT deploy to WordPress (no WP API integration)
8. ❌ Peterman CANNOT calculate real scores (5 of 7 components are hardcoded 50.0)

**The Flask Peterman v2.0.0 is a skeleton with stub implementations.** It has:
- Database schema (partial)
- API endpoints for domain CRUD (partial)
- Score engine structure (but returns fake data)
- Budget tracking (basic)
- Audit logging (basic)

It does NOT have:
- Any actual crawling, probing, or deployment capability
- Real AI integration (Claude Desktop not connected)
- Approval workflow
- Automation loops

---

## SECTION 7: WHAT NEEDS TO BE BUILT

### Priority 1: Core Infrastructure (Before Anything Else)
1. **Claude Desktop MCP Integration** — Without this, no real AI reasoning
2. **Ollama Setup** — Need Supervisor running with nomic-embed-text
3. **Domain Crawler** — To understand what the business does

### Priority 2: Basic Workflow
4. **Keyword/Query Suggestion Engine** — Generate target queries from crawled content
5. **LLM Probing Implementation** — Actually query ChatGPT, Claude, Perplexity, Gemini
6. **Probe Result Storage** — Store 5 runs per query with proper analysis

### Priority 3: Intelligence
7. **Hallucination Detection** — Detect false claims in LLM responses
8. **Content Brief Generation** — Generate correction briefs using Claude Desktop
9. **Peterman Score Real Implementation** — Replace 50.0 stubs with real calculations

### Priority 4: Automation
10. **Approval Gate System** — 5-level approval workflow
11. **WordPress Deployment** — Deploy approved content via REST API
12. **Rollback System** — Pre/post snapshots, one-click undo

### Priority 5: Advanced Features
13. **Competitor Shadow Mode** — Track competitor mentions
14. **Semantic Gravity Scoring** — Real embedding-based positioning
15. **Content Survivability Lab** — LCRI scoring implementation
16. **The Oracle** — Predictive forecasting
17. **Defensive Perception Shield** — Reputation monitoring

---

## RECOMMENDATION

**Do not tell Mani Peterman is ready.** It is a prototype skeleton.

The honest answer: "Peterman has the database schema and basic API structure, but the core workflow — crawling, probing LLMs, detecting hallucinations, generating briefs, deploying to WordPress — is not implemented. We're looking at 2-4 weeks of development to get to a minimum viable state where you can add a domain and see actual probe results."

---

*Audit conducted on Flask Peterman v2.0.0 (port 5011)*
*Database: peterman_flask (PostgreSQL via Docker)*
