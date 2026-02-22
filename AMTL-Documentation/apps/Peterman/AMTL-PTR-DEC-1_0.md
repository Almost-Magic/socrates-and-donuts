# AMTL — Peterman Decision Register
## Document Code: AMTL-PTR-DEC-1.0
## Almost Magic Tech Lab
## 18 February 2026

> *This document follows AMTL-ECO-STD v1.0. All conventions defined there apply unless explicitly overridden with a Decision Register entry.*

---

## Purpose

Every design choice made for Peterman, logged when it was made, why it was made, and what it affects. If a new developer joins tomorrow, this register explains every "why" without needing to search conversation history.

---

## Decision Log

### DEC-001: Multi-Domain Architecture from Day One

| Field | Value |
|-------|-------|
| **ID** | DEC-001 |
| **Date** | 18 February 2026 |
| **Context** | v1 was designed as single-domain. v2 needed to support AMTL's own domain plus client domains. Retrofitting multi-domain is always harder than building it in. |
| **Decision** | Every component is built domain-first. There is no single-domain mode. Even the AMTL dogfooding instance runs as Domain #001 inside a multi-domain schema. All data tables include `domain_id` as a non-nullable foreign key. |
| **Rationale** | Avoids the "v3 rewrite" problem. Multi-domain is the foundation, not a feature. The agency and enterprise pricing tiers depend on this being native. |
| **Decided by** | Mani + Thalaiva |
| **Affects** | AMTL-PTR-TDD-1.0 (all data models), AMTL-PTR-BLD-1.0 (Phase 0 schema) |

---

### DEC-002: Port Assignment — 5008

| Field | Value |
|-------|-------|
| **ID** | DEC-002 |
| **Date** | 18 February 2026 |
| **Context** | Port assignment for the Peterman Flask backend. Ports 5000–5005 were already allocated to ELAINE, Costanza, Learning Assistant, Workshop, CK Writer, and Junk Drawer. |
| **Decision** | Peterman runs on port 5008. |
| **Rationale** | Within the AMTL 5000–5099 application backend range. No conflict with existing assignments. Already confirmed in AMTL-ECO-STD-1.0 port registry. |
| **Decided by** | Mani |
| **Affects** | AMTL-ECO-STD-1.0 (port registry), AMTL-PTR-TDD-1.0, AMTL-PTR-BLD-1.0, AMTL-PTR-RUN-1.0, AMTL-PTR-MRD-1.0 |

---

### DEC-003: Claude Desktop as Primary AI Engine

| Field | Value |
|-------|-------|
| **ID** | DEC-003 |
| **Date** | 18 February 2026 |
| **Context** | v1 used Claude CLI as primary with Ollama fallback. v2 shifts to Claude Desktop (local app, Claude Max subscription) via MCP or local API socket through The Workshop. |
| **Decision** | Claude Desktop is the primary reasoning engine for all complex Peterman intelligence tasks. Fallback chain: Manus Desktop → Perplexity Desktop → Ollama → browser-based (human-in-loop). |
| **Rationale** | Aligns with AMTL-ECO-STD-1.0 Section 7.4 ("Claude Desktop is the default agent"). Avoids per-call API costs for reasoning-heavy tasks. Desktop apps are already running on Mani's machine. |
| **Decided by** | Mani + Thalaiva |
| **Affects** | AMTL-PTR-TDD-1.0 (AI stack), AMTL-PTR-BLD-1.0 (all phases using AI) |

---

### DEC-004: Ollama for All Embeddings (Always Local)

| Field | Value |
|-------|-------|
| **ID** | DEC-004 |
| **Date** | 18 February 2026 |
| **Context** | Embeddings are used extensively across chambers (semantic gravity, content alignment, cannibalization check, drift detection). Cost and latency matter. |
| **Decision** | All embeddings use nomic-embed-text via Ollama (through Supervisor). Embeddings are always local — no cloud embedding API calls. |
| **Rationale** | nomic-embed-text produces 768-dimension embeddings with good quality/speed ratio. Local-first avoids per-call costs on what is the most frequent API operation. Aligns with AMTL no-cloud-API-fallback rule. |
| **Decided by** | Thalaiva |
| **Affects** | AMTL-PTR-TDD-1.0 (embedding engine), all chamber implementations |

---

### DEC-005: PostgreSQL + pgvector for All Persistent Storage

| Field | Value |
|-------|-------|
| **ID** | DEC-005 |
| **Date** | 18 February 2026 |
| **Context** | Need to store probe results, hallucination records, content briefs, deployment snapshots, audit logs, and vector embeddings. Could split across multiple storage systems. |
| **Decision** | Single PostgreSQL 17 instance with pgvector extension (port 5433) for all persistent storage including vector embeddings. Redis (port 6379) only for ephemeral queuing. |
| **Rationale** | Simplicity. One database to back up, one to restore. pgvector handles similarity queries at Peterman's scale (hundreds of domains, not millions). Avoids introducing a separate vector database. |
| **Decided by** | Thalaiva |
| **Affects** | AMTL-PTR-TDD-1.0 (data model), AMTL-PTR-BLD-1.0 (Phase 0 database setup) |

---

### DEC-006: APScheduler Instead of Celery

| Field | Value |
|-------|-------|
| **ID** | DEC-006 |
| **Date** | 18 February 2026 |
| **Context** | Peterman needs a scheduler for periodic chamber cycles (daily probes, weekly reports, campaign schedules). Celery is the standard Python distributed task queue. |
| **Decision** | Use APScheduler, not Celery. |
| **Rationale** | Peterman is a single-user system running on one machine. Celery's distributed architecture is unnecessary overhead. APScheduler provides cron-like scheduling with no broker dependency beyond Redis (already in stack). |
| **Decided by** | Thalaiva |
| **Affects** | AMTL-PTR-TDD-1.0 (scheduler service), AMTL-PTR-BLD-1.0 |

---

### DEC-007: No Frontend Framework (HTML/CSS/JS SPA)

| Field | Value |
|-------|-------|
| **ID** | DEC-007 |
| **Date** | 18 February 2026 |
| **Context** | The War Room dashboard needs dynamic updates (score gauge, alert feed, approval inbox). React, Vue, or Svelte would simplify state management. |
| **Decision** | HTML/CSS/JS with no framework — matches other AMTL apps (ELAINE, Workshop). |
| **Rationale** | AMTL standard. Reduces build complexity and toolchain. Electron wraps the SPA for desktop delivery. The dashboard is data-display-heavy, not interaction-heavy — vanilla JS with fetch and DOM manipulation is sufficient. |
| **Decided by** | Mani |
| **Affects** | AMTL-PTR-TDD-1.0 (frontend architecture), AMTL-PTR-BLD-1.0 (frontend phases) |

---

### DEC-008: Immutable Audit Log (Append-Only)

| Field | Value |
|-------|-------|
| **ID** | DEC-008 |
| **Date** | 18 February 2026 |
| **Context** | Peterman makes autonomous changes to live websites. For compliance (especially regulated-sector clients) and for AMTL's AI governance positioning, every action must be provably recorded. |
| **Decision** | The audit_log table is append-only. The application database role has INSERT permission only — no UPDATE or DELETE. Exportable as CSV/JSON. |
| **Rationale** | Immutability is not just a nice-to-have for an autonomous deployment agent — it's a governance requirement. This positions AMTL's tooling as compliance-grade. |
| **Decided by** | Mani + Thalaiva |
| **Affects** | AMTL-PTR-TDD-1.0 (audit model), AMTL-PTR-BLD-1.0 (database permissions) |

---

### DEC-009: Five-Level Approval Gate System

| Field | Value |
|-------|-------|
| **ID** | DEC-009 |
| **Date** | 18 February 2026 |
| **Context** | Peterman operates autonomously. Without gates, it could make harmful changes. With too many gates, it becomes just another reporting tool that needs human action for everything. |
| **Decision** | Five gate levels: Auto-deploy (low-risk, reversible), Low-gate (ELAINE announces, 10-second objection window), Medium-gate (ELAINE presents, awaits yes/no), Hard-gate (detailed briefing + explicit approval + dry-run), Prohibited (operator executes manually). |
| **Rationale** | Balances autonomy with safety. Low-risk actions (schema, meta tags) don't need approval — they're reversible and standard. High-risk actions (robots.txt, canonicals) need human judgement. Page deletion is never autonomous. |
| **Decided by** | Mani + Thalaiva |
| **Affects** | AMTL-PTR-TDD-1.0 (approval system), AMTL-PTR-BLD-1.0 (Phase 1 approval gates), AMTL-PTR-USR-1.0 |

---

### DEC-010: Probe Normalisation — 5 Runs Per Query

| Field | Value |
|-------|-------|
| **ID** | DEC-010 |
| **Date** | 18 February 2026 |
| **Context** | LLM responses vary between calls even at temperature 0. Raw responses are noisy. The Peterman Score is meaningless without normalisation. |
| **Decision** | Every probe runs 5 times per query with temperature 0.0 and top_p 1.0. Scores are averaged with consistency metrics (mention consistency, position consistency, sentiment consistency) computed per batch. |
| **Rationale** | 5 runs balances statistical reliability against API cost. 3 runs is too noisy. 10 runs doubles cost for marginal improvement. Consistency scores give confidence intervals that distinguish "67 ± 4" from "67 ± 19". |
| **Decided by** | Thalaiva |
| **Affects** | AMTL-PTR-TDD-1.0 (probe engine), budget calculations, API cost projections |

---

### DEC-011: Rollback Layer with 30-Day Retention

| Field | Value |
|-------|-------|
| **ID** | DEC-011 |
| **Date** | 18 February 2026 |
| **Context** | Autonomous deployment to live websites needs a safety net. If a change causes harm, it must be reversible. |
| **Decision** | Every deployment creates a pre/post snapshot (full HTML, metadata, unified diff). Snapshots retained for 30 days. One-click rollback via Journey Timeline. If Peterman Score drops >5 points within 48 hours post-deploy, ELAINE offers one-tap rollback. Peterman never auto-rolls back without operator confirmation. |
| **Rationale** | 30 days covers most detection windows for SEO impact. One-click rollback removes the fear of approving autonomous changes. The "never auto-rollback" rule ensures operators stay in control. |
| **Decided by** | Mani + Thalaiva |
| **Affects** | AMTL-PTR-TDD-1.0 (rollback layer), AMTL-PTR-BLD-1.0 (Phase 0 rollback infrastructure) |

---

### DEC-012: Dark Theme Default with AMTL Midnight

| Field | Value |
|-------|-------|
| **ID** | DEC-012 |
| **Date** | 18 February 2026 |
| **Context** | AMTL branding standard. |
| **Decision** | Peterman launches in dark mode (AMTL Midnight #0A0E14) by default. Dark/light toggle in header. AMTL Gold (#C9944A) for accent, highlights, and the Peterman Score gauge. |
| **Rationale** | AMTL-ECO-STD-1.0 Section 4.2 — no exceptions. The War Room aesthetic benefits from a dark, mission-control feel. |
| **Decided by** | AMTL standard (non-negotiable) |
| **Affects** | AMTL-PTR-TDD-1.0 (frontend), AMTL-PTR-BLD-1.0 (frontend phases) |

---

## Template for New Entries

```markdown
### DEC-XXX: [Title]

| Field | Value |
|-------|-------|
| **ID** | DEC-XXX |
| **Date** | DD Month YYYY |
| **Context** | What situation or question prompted this decision |
| **Decision** | What was decided |
| **Rationale** | Why this option was chosen over alternatives |
| **Decided by** | Who made or approved this decision |
| **Affects** | Which document codes are impacted |
```

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 18 February 2026 | Claude (Thalaiva) | Initial register — 12 decisions logged from SPC v1.0 and v2.0 |

---

*Almost Magic Tech Lab*
*"Every decision has a home. No 'I think we decided...' — it's here or it didn't happen."*
