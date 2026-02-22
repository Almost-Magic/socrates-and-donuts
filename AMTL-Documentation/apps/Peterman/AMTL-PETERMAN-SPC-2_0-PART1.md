# AMTL Peterman v2.0 — Product Specification
## Part 1: Strategic Foundation, Multi-Domain Architecture & Chambers 1–6

**Document:** AMTL-PETERMAN-SPC-2_0-PART1  
**Version:** 2.0  
**Date:** 18 February 2026  
**Status:** Specification — Pre-Build  
**Author:** Mani Padisetti, Almost Magic Tech Lab  
**Ecosystem:** The Workshop (port 5003) → Peterman (port 5008)

---

## 1. Vision Statement

Peterman is the world's first **autonomous LLM Presence Operating System**.

It does not produce reports. It does not suggest actions. It detects, plans, commissions, deploys, verifies, and reports — across every domain it manages — while the operator sleeps.

The shift it addresses: Discovery is no longer won on Google. It is won inside the latent space of large language models. The business that structures its truth most effectively for AI ingestion wins the query. Peterman automates that structuring — continuously, intelligently, and with a human approval gate at every high-stakes decision.

**One-liner:** Peterman makes your domain the default answer when AI is asked about your niche.

**2026 positioning:** "Not a reporting tool. An execution engine."  
**2030 positioning:** "Not a presence tool. A reality architecture platform."

---

## 2. What's New in v2.0

v2 is not a cosmetic update. The following are structural changes from v1:

| Area | v1 | v2 |
|------|----|----|
| Domain model | Single domain | **Multi-domain, multi-tenant by design** |
| LLM probing | Basic mention tracking | Normalized, averaged, confidence-scored |
| Deployment | Auto-deploy with approval | Dry-run sandbox → diff preview → approval → deploy → rollback-ready |
| AI stack | Claude + Ollama + SearXNG | **Claude Desktop primary** + Manus/Perplexity/Ollama/ChatGPT/Gemini fallback chain |
| Defensive posture | None | Defensive Perception Shield Mode |
| Fault tolerance | Not specified | Explicit failure modes, graceful degradation, cost budgeting |
| Compliance | Not specified | Immutable audit log, per-domain governance trail |
| ELAINE integration | Content commissioning | **Full approval interface** — voice-driven approvals, status briefings |
| Knowledge layer | HTML content only | Agent-Ready Manifest (machine-first structured data layer) |

---

## 3. The Multi-Domain Architecture (Foundation Layer)

This is the most critical structural decision in v2. Every component is built domain-first. There is no single-domain mode — even the AMTL dogfooding instance runs as Domain #001 inside a multi-domain schema.

### 3.1 Domain Registry

Every managed domain is a **Domain Object** with its own isolated configuration, API keys, content queue, hallucination registry, budget, and audit log.

```
Domain Object {
  domain_id:          UUID (primary key across all tables)
  domain_name:        "almostmagic.net.au"
  display_name:       "Almost Magic Tech Lab"
  owner_label:        "AMTL Internal" | "Client: [Name]"
  cms_type:           "wordpress" | "webflow" | "custom" | "static"
  cms_api_key:        encrypted
  target_llms:        ["openai", "anthropic", "ollama", "perplexity"]
  probe_cadence:      "daily" | "weekly" | "campaign"
  budget_weekly_aud:  float (hard cap)
  status:             "active" | "paused" | "onboarding" | "archived"
  created_at:         timestamp
  tier:               "owner" | "agency" | "client"
}
```

### 3.2 Multi-Domain Data Isolation

All data tables include `domain_id` as a non-nullable foreign key. No cross-domain data leakage is architecturally possible. Cross-domain analytics (for agency dashboards) are computed views only — they never join raw data.

### 3.3 Domain Roles

| Role | Access |
|------|--------|
| **Owner (AMTL)** | All domains, all data, all settings |
| **Agency** | Assigned client domains only, reporting + approval |
| **Client (read-only)** | Their domain's Peterman Score, Journey Timeline, Client Mode report |

### 3.4 Domain Onboarding (One-Click Setup)

1. Operator enters domain URL
2. Peterman crawls and detects: CMS type, existing schema markup, sitemap presence, robots.txt, page count, language(s)
3. Runs Chamber 6 technical baseline audit
4. Runs first LLM probe set (5 queries, 5 runs each)
5. Generates Domain Health Card with initial Peterman Score
6. ELAINE briefs operator: *"Onboarding complete for [domain]. Initial score: [X]. Three priority actions queued for your approval."*

---

## 4. The Peterman Score v2

The composite domain health score. Rendered as a circular gauge, colour-shifting red → amber → gold as it improves. Clickable to reveal spider chart breakdown.

### 4.1 Component Scores

| Component | Weight | Source Chamber |
|-----------|--------|---------------|
| LLM Share of Voice | 25% | Chamber 1 |
| Semantic Gravity | 20% | Chamber 2 |
| Technical Foundation | 15% | Chamber 6 |
| Content Survivability | 15% | Chamber 5 |
| Hallucination Debt | 10% | Chamber 1 |
| Competitive Position | 10% | Chamber 8 |
| Predictive Velocity | 5% | Chamber 9 |

### 4.2 Score Confidence Interval

Every score component displays a confidence interval, not just a number. A score of 67 ± 4 means something different from 67 ± 19. Confidence is derived from probe run consistency and data recency.

---

## 5. The AI Stack — Primary and Fallback Chain

No cloud API fallback surprises. No paying twice. The stack is explicit.

### 5.1 Primary: Claude Desktop

Claude Desktop (local app, Claude Max subscription) is the primary reasoning engine for all Peterman intelligence tasks:
- Hallucination analysis
- Content brief generation
- Strategic rationale synthesis
- Approval summaries for ELAINE
- Semantic Gravity interpretation
- Oracle forecast narratives

**Integration method:** Claude Desktop MCP or local API socket via The Workshop.

### 5.2 Fallback Chain (in order)

When Claude Desktop is unavailable or unresponsive (3 auto-checks before failover):

| Priority | Engine | Use |
|----------|--------|-----|
| 1 | **Claude Desktop** | Primary — all reasoning tasks |
| 2 | **Manus Desktop** | Complex research, multi-document synthesis |
| 3 | **Perplexity Desktop** | Web-grounded research, current events, competitor monitoring |
| 4 | **Ollama (local)** | Embeddings (nomic-embed-text), light inference, brief variants, scoring |
| 5 | **ChatGPT (browser)** | Human-in-loop tasks only — ELAINE opens browser, flags for operator |
| 6 | **Gemini (browser)** | Last resort — ELAINE opens browser, flags for operator |

**Rule:** Ollama is always available for programmatic/batch tasks. Browser-based fallbacks (ChatGPT, Gemini) are flagged to the operator rather than auto-used — operator decides whether to proceed.

### 5.3 Task-to-Engine Routing Map

| Task | Primary | Fallback |
|------|---------|----------|
| Hallucination analysis | Claude Desktop | Manus Desktop → Ollama (llama3.1) |
| Content brief generation | Claude Desktop | Manus Desktop → Ollama (llama3.1) |
| Embeddings (all) | nomic-embed-text (Ollama) | — (always local) |
| LLM probing (external) | OpenAI API / Anthropic API | Perplexity Desktop |
| Competitor monitoring | Perplexity Desktop + SearXNG | SearXNG only |
| Trend forecasting | Claude Desktop + SearXNG | Perplexity Desktop |
| Schema / technical fixes | Ollama (Mistral) | Claude Desktop |
| Brief quality check | Claude Desktop | Ollama (llama3.1) |
| Approval summaries for ELAINE | Claude Desktop | Ollama (llama3.1) |

---

## 6. The Probe Normalization Protocol

LLM responses are not stable. Temperature drift, session variance, and training updates mean raw responses are noisy. The Peterman Score is worthless without normalization.

### 6.1 Standard Probe Specification

Every LLM probe run follows this spec:

```
Probe Spec {
  temperature:    0.0 (deterministic)
  top_p:          1.0
  runs_per_query: 5 (averaged)
  system_prompt:  PETERMAN_STANDARD_SYSTEM_PROMPT (versioned, immutable)
  timeout:        30 seconds
  models_probed:  as per domain config (default: openai-gpt4o, claude-3.5, ollama-llama3.1)
}
```

### 6.2 Confidence Scoring

After 5 runs per query, compute:
- **Mention consistency score:** % of runs that mention the brand
- **Position consistency score:** variance in mention position
- **Sentiment consistency score:** variance in detected sentiment
- **Composite confidence:** weighted average → reported alongside every metric

### 6.3 Retrain-Pulse Watcher

A background monitor that tracks public announcements of major LLM updates (via SearXNG + Perplexity). When a significant model update is detected:

1. Flag in War Room dashboard
2. Auto-schedule "Re-probe burst" within 48 hours for all active domains
3. Compute score delta: "Post-update shift: [domain] LLM SoV dropped 8 points on ChatGPT, stable on Claude."
4. ELAINE briefs operator

---

## 7. The Ten Chambers — v2

The chamber model is retained and deepened. Each chamber now explicitly declares: inputs, outputs, AI engines used, approval gate level, and failure mode.

---

### Chamber 1: The Perception Engine

**Purpose:** Track, normalize, and score how LLMs currently perceive the domain.

**v2 additions:**
- Multi-LLM Share of Voice: separate SoV score per LLM provider (OpenAI, Anthropic, Perplexity, Ollama)
- Cross-model comparison: "You rank 2nd on Claude, 5th on ChatGPT, not mentioned on Perplexity"
- LLM Preference Bias: each model's stylistic tendency (Claude values cautious, cited claims; ChatGPT prefers conversational benefit-oriented language) — used to brief content differently per target
- Persona Presence Metric: probes framed as "If you were explaining [topic] to an Australian SMB founder, who would you recommend?" — tracks brand appearance in persona-specific queries, not just generic

**Hallucination Registry (v2 — Jira-style)**

Hallucinations are bugs. Tracked as:

```
Hallucination Record {
  hallucination_id:    UUID
  domain_id:           UUID
  detected_at:         timestamp
  llm_source:          "openai" | "anthropic" | "ollama" | "perplexity"
  query_that_triggered: string
  false_claim:         string
  severity_score:      1–10 (composite: financial impact + LLM confidence + mention prominence + cross-LLM frequency)
  status:              "open" | "brief_generated" | "content_deployed" | "verified_closed" | "suppressed"
  assigned_brief_id:   UUID (nullable)
  closed_at:           timestamp (nullable)
  resolution_evidence: string (nullable)
}
```

Severity scoring uses four dimensions:
1. Financial/reputational impact of the false claim
2. Confidence language used by LLM (certainty phrases = higher severity)
3. Mention prominence (first paragraph = 10, buried = 2)
4. Cross-LLM frequency (same hallucination across 3 models = critical)

**AI engines:** Claude Desktop (primary analysis), nomic-embed-text (embeddings), Ollama Mistral (scoring variants)  
**Approval gate:** Hallucination detected = auto-log. Brief generation = low-gate (ELAINE approval via voice). Deployment = medium-gate.  
**Failure mode:** If probe APIs unavailable, skip cycle, log missed probe, ELAINE alerts operator. Never generate score from partial data.

---

### Chamber 2: Semantic Gravity

**Purpose:** Measure the domain's gravitational pull in vector space — how central it is to its target topic clusters versus competitors.

**v2 — Formalized Methodology**

Semantic Gravity Score is now formally defined (not marketing language):

```
Semantic Gravity Score (SGS) {

  Step 1 — Cluster Definition
  For each target topic cluster T:
    - Generate 50 representative query embeddings for T using nomic-embed-text
    - Compute cluster centroid C(T) as mean vector

  Step 2 — Domain Embedding
  For each domain D:
    - Embed all indexed pages (title + first 500 chars)
    - Compute domain centroid D_vec

  Step 3 — Gravity Score
  SGS(D, T) = 1 / cosine_distance(D_vec, C(T))
  (Higher SGS = closer to cluster centroid = stronger gravity)

  Step 4 — Drift Delta
  ΔSG = SGS(current) - SGS(previous_period)
  Alert threshold: |ΔSG| > 0.05

  Step 5 — Competitor Benchmarking
  SGS_relative(D, T) = SGS(D, T) / max(SGS(competitors, T))
  1.0 = category leader, <0.5 = significant gap
}
```

**Semantic Neighbourhood Visualization**

2D scatter plot (Phase 1): Domain and competitors plotted in reduced embedding space (UMAP). Voronoi cells show "semantic territory." Zoom to explore topic clusters.

3D Semantic Galaxy (Phase 2, v2.1): Brands as stars, topics as constellations, competitors orbiting clusters. Size = authority. Distance = relevance to cluster. This becomes the hero visualization in Client Mode.

**Vector Space Influence Projection**

Before publishing content, compute expected SGS delta: "This brief moves you from 0.62 → estimated 0.71 on the 'AI governance' cluster." This directional forecast is displayed on every content brief approval card.

**AI engines:** nomic-embed-text (all embeddings), Claude Desktop (interpretation), pgvector (storage + similarity queries)  
**Approval gate:** Visualization = automated. Score alerts = automated. Strategy pivots based on SGS drift = medium-gate.  
**Failure mode:** If pgvector unavailable, queue embeddings locally, process on recovery. Never skip embedding generation.

---

### Chamber 3: The Content Survivability Lab

**Purpose:** Score how well content survives compression, summarization, and RAG extraction by LLMs.

**v2 — LLM Compression Resistance Index (LCRI)**

This is formally defined IP. The methodology:

```
LCRI Methodology {

  Input: Content piece P

  Test 1 — Direct Summarization
  Feed P to LLM with: "Summarize the key facts in 5 bullet points."
  Score: % of pre-identified key facts retained in summary (0–1.0)

  Test 2 — Citation Probability
  Feed P in RAG context, ask 10 domain-relevant queries.
  Score: % of queries where P is cited as source

  Test 3 — Extractable Snippet Strength
  Feed P, ask: "What is the single most important takeaway from this?"
  Score: semantic similarity between LLM answer and intended message

  Test 4 — RAG Chunk Compatibility
  Chunk P at 512 tokens (standard RAG chunk size).
  For each chunk: test if standalone chunk remains meaningful and attributable.
  Score: % of chunks that are independently coherent and attributable

  Composite LCRI = weighted average(Test1 × 0.3, Test2 × 0.3, Test3 × 0.2, Test4 × 0.2)
}
```

**Adversarial Survivability Test**

A local "Hostile LLM" (Ollama Mistral) attempts to:
- Paraphrase the content
- Summarize it aggressively
- Answer questions about the domain using the content as context

If the hostile LLM hallucinates or misattributes, the content fails the adversarial test. Chamber 10 receives a brief to rewrite the failing sections.

**AI engines:** Claude Desktop (test 1, 3), Ollama Mistral (adversarial tests), nomic-embed-text (semantic similarity scoring)  
**Approval gate:** LCRI scoring = automated. Content rewrite briefs from low LCRI = low-gate.  
**Failure mode:** If adversarial tests unavailable, run Tests 1–3 only, flag LCRI as partial, annotate in score.

---

### Chamber 4: Authority & Backlink Intelligence

**Purpose:** Monitor and grow the domain's citation authority — both traditional backlinks and LLM citation frequency.

**v2 — LLM Citation Value Scoring**

Not all backlinks are equal. A link from a domain that LLMs frequently cite is worth more than ten from domains LLMs ignore. Peterman now scores backlink targets by their LLM citation frequency:

```
LLM Citation Authority (LCA) {
  For each candidate backlink domain B:
    Probe: "Who are the leading sources on [target topic]?"
    LCA(B) = % of probe runs that mention B as a source
  
  Target prioritization: sort by LCA(B) descending
  "Get a mention from [high-LCA domain] — it is cited by Claude 68% of the time on AI governance queries."
}
```

**Backlink Mini-CRM**

| Field | Description |
|-------|-------------|
| Target domain | URL + LCA score |
| Opportunity type | Guest post / Resource mention / Citation request |
| Status | Identified → Outreach suggested → Acquired → Verified |
| Acquired at | Timestamp |
| Impact on SGS | Delta after acquisition |

**Semantic Contamination Detector**

Monitors for brand co-mentions with undesirable terms. Runs weekly:
- Probe: "Tell me about [brand] and [negative term cluster]"
- If co-occurrence detected: log + alert + auto-generate counter-brief
- Alert level: Low (tangential), Medium (repeated), High (persistent co-occurrence across models)

**AI engines:** Perplexity Desktop (backlink research), Claude Desktop (LCA scoring), SearXNG (monitoring)  
**Approval gate:** Opportunity detection = automated. Outreach suggestions = low-gate. Counter-briefs = medium-gate.  
**Failure mode:** If Perplexity unavailable, use SearXNG only, flag coverage as partial.

---

### Chamber 5: Hallucination Autopilot™

**Purpose:** Close the loop from hallucination detection to verified content correction — autonomously.

**v2 — Hallucination Prediction Engine**

Don't just react to hallucinations — predict where they'll occur next.

Using historical hallucination records across all managed domains (anonymized, aggregated), Peterman trains a local prediction model:
- Input features: Topic coverage gaps, content age, LCRI score, competitor content volume on topic
- Output: "Topic X has 74% probability of generating a hallucination in next 60 days"
- Action: Pre-emptive content brief generated before the hallucination occurs

This shifts Chamber 5 from reactive remediation to proactive prevention.

**The Autopilot Loop**

```
1. DETECT
   Chamber 1 logs hallucination in Hallucination Registry
   Severity score computed

2. ANALYZE
   Claude Desktop: "What true content would prevent this hallucination?"
   Cross-reference existing content map (content cannibalization check)
   If existing content can fix it: generate update brief
   If gap: generate new content brief

3. BRIEF
   Content brief sent to The Forge (Chamber 10)
   Brief includes: target LLM, target query, desired answer structure,
   key facts to include, LCRI target score

4. COMMISSION
   The Forge → ELAINE queue
   ELAINE writes content via CK Writer
   Brief-to-content alignment score computed before approval

5. APPROVE
   Medium-gate: ELAINE presents to operator
   "Peterman: New FAQ to fix ISO certification hallucination.
    Estimated LLM SoV improvement: +5 points.
    LCRI score: 0.81. Ready to deploy?"

6. DEPLOY
   Dry-run first: HTML diff preview generated
   Operator approves diff
   CMS API deployment
   Snapshot stored (rollback-ready)

7. VERIFY
   48-hour wait
   Re-probe same query that triggered hallucination
   If hallucination persists: escalate, generate stronger content
   If resolved: Hallucination Registry status → "verified_closed"
   
8. REPORT
   Closure logged in audit trail
   Peterman Score updated
   ELAINE notifies: "Hallucination #[ID] closed. ISO cert now correctly stated in ChatGPT and Claude."
```

**AI engines:** Claude Desktop (steps 2–3), ELAINE/CK Writer (step 4), nomic-embed-text (alignment scoring), Ollama (adversarial verify)  
**Approval gate:** Steps 1–3 automated. Step 5 = medium-gate. Step 6 = dry-run required before live deploy.  
**Failure mode:** If CMS API fails mid-deploy: immediate rollback to snapshot. Log failure. ELAINE alerts. Never leave a partial deployment.

---

### Chamber 6: The Technical Foundation

**Purpose:** Maintain and improve all technical SEO and LLM-discoverability infrastructure. Runs silently. Low glamour, non-negotiable.

**v2 — The Agent-Ready Manifest**

This is new IP. Beyond standard schema markup, every managed domain gets a machine-readable structured data layer specifically designed for AI crawler ingestion.

```
/agent-manifest.json (public, at domain root)

{
  "manifest_version": "1.0",
  "entity": {
    "legal_name": "Almost Magic Tech Lab",
    "trading_name": "AMTL",
    "description": "[factual, dense, LLM-optimised]",
    "founding_year": 2026,
    "primary_location": "Sydney, Australia",
    "certifications": ["ISO 42001", "ISO 27001", "CGEIT"],
    "services": [...structured service objects...],
    "key_personnel": [...],
    "pricing_model": "subscription",
    "verified_claims": [...factual claims with source URLs...],
    "not_affiliated_with": [...disambiguation list...],
    "last_verified": "2026-02-18"
  },
  "fact_verification_api": "https://[domain]/verify/v1/"
}
```

This manifest is not hidden, not deceptive. It is a public, formal structured data declaration that makes fact extraction trivially easy for AI crawlers. Businesses that publish this win the "fact extraction game" by default. The verification API endpoint allows other AI systems to query for current facts (price, availability, certifications) rather than guessing.

**Peterman auto-generates and maintains this manifest.** It is updated whenever a relevant page changes.

**Autonomous Technical Actions (with approval gate levels)**

| Action | Risk | Gate |
|--------|------|------|
| Schema markup generation | Low | Auto-deploy |
| Meta description update | Low | Auto-deploy |
| Internal link addition | Low | Auto-deploy |
| Sitemap regeneration | Low | Auto-deploy |
| Agent-Ready Manifest update | Low | Auto-deploy |
| Robots.txt modification | **High** | Hard-gate: explicit approval + 24hr delay |
| Canonical tag change | **High** | Hard-gate: explicit approval + dry-run required |
| Page deletion or redirect | **Critical** | Prohibited: operator must execute manually |

**Dry-Run Sandbox**

All technical deployments run through dry-run first:
1. Generate HTML diff showing before/after
2. Render synthetic preview of live page after change
3. Present to operator for approval
4. Only after explicit approval does live deployment proceed
5. Snapshot of pre-change state stored (30-day retention for rollback)

**Automated A/B Testing (Meta)**

For high-traffic pages: Peterman deploys meta description variant A, monitors CTR via Google Search Console integration for 14 days, deploys variant B, monitors 14 days, permanently implements winner. Operator can override at any point.

**AI engines:** Ollama Mistral (schema generation, meta variants), Claude Desktop (manifest generation), GSC API (CTR data)  
**Approval gate:** See table above. Dry-run mandatory for all high-risk changes.  
**Failure mode:** If CMS API unavailable: queue all pending technical changes, retry every 6 hours, ELAINE alerts after 24 hours of failed retry.

---

## 8. The Rollback Layer (Cross-Chamber Requirement)

Every autonomous action that modifies the live domain is protected by the Rollback Layer. This is non-negotiable and applies to all chambers.

### 8.1 Snapshot Specification

```
Deployment Snapshot {
  snapshot_id:      UUID
  domain_id:        UUID
  action_id:        UUID (links to the action that triggered it)
  snapshot_type:    "pre_deploy" | "post_deploy"
  captured_at:      timestamp
  content:          {
    url:            string
    html_before:    string (full page HTML)
    html_after:     string (full page HTML)
    diff:           string (unified diff)
    metadata_before: object
    metadata_after:  object
  }
  rollback_status:  "available" | "used" | "expired"
  expires_at:       timestamp (30 days from capture)
}
```

### 8.2 One-Click Rollback

In the Journey Timeline, every deployed action has a Rollback button. Clicking it:
1. Presents diff of what will be reverted
2. Requires single confirmation click
3. Executes revert via CMS API
4. Logs rollback event in audit trail
5. Updates Peterman Score accordingly
6. ELAINE confirms: "Rollback complete. [Page] restored to pre-[date] state."

### 8.3 Automatic Rollback Trigger

If a deployment causes a measurable negative impact within 48 hours (Peterman Score drops >5 points, or GSC shows significant CTR drop), ELAINE alerts and offers one-tap rollback. The operator decides — Peterman never auto-rolls back without operator confirmation.

---

## 9. The Audit Log (Compliance & Governance)

Every action Peterman takes or recommends is immutably logged. This is critical for regulated-sector clients and for AMTL's AI governance positioning.

```
Audit Entry {
  entry_id:         UUID
  domain_id:        UUID
  timestamp:        timestamp (UTC, immutable)
  action_type:      string
  action_detail:    object (full payload)
  initiated_by:     "peterman_auto" | "operator_manual" | "elaine_voice"
  approval_gate:    "auto" | "low" | "medium" | "hard" | "prohibited"
  approved_by:      "system" | "operator:[id]"
  approved_at:      timestamp (nullable)
  outcome:          "success" | "failed" | "rolled_back" | "pending"
  snapshot_id:      UUID (nullable)
  notes:            string (nullable)
}
```

Audit log is append-only. No record can be modified or deleted. Exportable as CSV/JSON for client reporting or compliance review.

---

## 10. Fault Tolerance & Graceful Degradation

The system must degrade gracefully, never silently fail, and never corrupt live data.

### 10.1 AI Engine Failure

```
If Claude Desktop unavailable:
  → Auto-retry 3× (5-second intervals)
  → Failover to Manus Desktop
  → If Manus unavailable: Perplexity Desktop
  → If Perplexity unavailable: Ollama (llama3.1)
  → If all unavailable: Queue task, ELAINE alerts operator
  → Never execute with degraded confidence without flagging it
```

### 10.2 CMS API Failure

```
If CMS API fails during deployment:
  → Immediate halt (do not partially apply changes)
  → Rollback any partial changes
  → Log failure with full payload
  → Queue for retry (6-hour intervals, max 3 retries)
  → After 3 failures: escalate to ELAINE → operator
```

### 10.3 LLM Probe API Failure

```
If external LLM probe API unavailable:
  → Skip that model for this cycle
  → Log as "missed probe"
  → Do not compute SoV score for that model this cycle
  → Flag score as "partial data" in dashboard
  → Never present a score as complete when data is missing
```

### 10.4 Cost Budget Enforcement

Each domain has a hard weekly API spend cap (set in Domain Object). The Cost Budget Chamber runs as a background service:

```
Budget Monitor {
  Tracks:     cumulative API spend per domain per rolling 7 days
  At 80%:     ELAINE warns operator
  At 100%:    Auto-pause all non-critical probing
              Switch to Ollama-only for that domain
              ELAINE alerts: "Budget cap reached for [domain]. Probing paused until [date]."
  Override:   Operator can approve emergency extension
}
```

---

*End of Part 1. Part 2 covers Chambers 7–10, Defensive Mode, UI/UX, Go-to-Market, and Patents.*
