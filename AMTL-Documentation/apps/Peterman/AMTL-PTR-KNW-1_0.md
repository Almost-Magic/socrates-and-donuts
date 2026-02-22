# AMTL — Peterman Known Issues Register
## Document Code: AMTL-PTR-KNW-1.0
## Almost Magic Tech Lab
## 18 February 2026

> *This document follows AMTL-ECO-STD v1.0. All conventions defined there apply unless explicitly overridden with a Decision Register entry.*

---

## Purpose

Living list of known bugs, limitations, workarounds, and technical debt for Peterman. Updated throughout the build and operational lifecycle.

---

## Status Codes

| Code | Meaning |
|------|---------|
| 🔴 Open | Known issue, no workaround, needs fixing |
| 🟡 Workaround Available | Known issue, workaround exists, fix planned |
| 🟢 Fixed | Resolved — kept here for history |
| ⚪ Deferred | Known limitation, accepted for now, not blocking |

---

## Known Issues

### KNW-001: Claude Desktop MCP Integration Uncertainty

| Field | Value |
|-------|-------|
| **ID** | KNW-001 |
| **Status** | 🟡 Workaround Available |
| **Severity** | High |
| **Description** | Claude Desktop is the primary AI engine for Peterman. The MCP (Model Context Protocol) integration path is the preferred method, but MCP socket availability and stability depend on Claude Desktop version and configuration. The integration method may need to change. |
| **Root Cause** | External dependency — Claude Desktop MCP is evolving. |
| **Workaround** | If MCP is unavailable, fall back to clipboard bridge pattern (ELAINE copies prompt to clipboard, focuses Claude Desktop window, pastes, waits for response). This is slower but proven in the ELAINE codebase. |
| **Fix Required** | Test MCP integration during Phase 0. If unreliable, implement clipboard bridge as primary with MCP as enhancement. Log decision in DEC register. |
| **Date Logged** | 18 February 2026 |

---

### KNW-002: LLM Probe API Rate Limits and Costs

| Field | Value |
|-------|-------|
| **ID** | KNW-002 |
| **Status** | 🟡 Workaround Available |
| **Severity** | Medium |
| **Description** | External LLM probe APIs (OpenAI, Anthropic) have rate limits and per-call costs. A domain with 20 target queries × 5 runs × 3 models = 300 API calls per probe cycle. At weekly cadence with 20 domains, this is 6,000 calls/week. |
| **Root Cause** | Fundamental constraint of external API-based probing. |
| **Workaround** | Budget monitor enforces per-domain weekly caps. Default cadence is weekly, not daily. Ollama probes (free) run more frequently. External probes batch to off-peak hours. Priority keywords can be probed more frequently at operator's discretion. |
| **Fix Required** | Phase 0: Implement budget monitor with 80%/100% warning/pause thresholds. Long-term: investigate caching of probe results to reduce redundant calls for similar queries. |
| **Date Logged** | 18 February 2026 |

---

### KNW-003: Semantic Gravity Accuracy with Limited Data

| Field | Value |
|-------|-------|
| **ID** | KNW-003 |
| **Status** | ⚪ Deferred |
| **Severity** | Low |
| **Description** | The Semantic Gravity Score (SGS) computes cluster centroids from 50 representative query embeddings per topic cluster. For niche or novel topics, 50 queries may not adequately represent the semantic space, leading to unreliable centroids. |
| **Root Cause** | Statistical: small sample sizes produce noisy centroids. |
| **Workaround** | SGS displays confidence intervals. Low-confidence scores are flagged in the dashboard. Operator can add custom queries to improve cluster definition. |
| **Fix Required** | After 6 months of operation, analyse SGS accuracy against actual LLM ranking changes. If correlation is weak for small clusters, increase query count or switch to adaptive sampling. |
| **Date Logged** | 18 February 2026 |

---

### KNW-004: Content Survivability Lab Depends on LLM Consistency

| Field | Value |
|-------|-------|
| **ID** | KNW-004 |
| **Status** | ⚪ Deferred |
| **Severity** | Low |
| **Description** | The LCRI (LLM Compression Resistance Index) feeds content to LLMs and scores how well key facts survive summarisation. LLM summarisation behaviour changes with model updates, meaning LCRI scores are only comparable within the same model version. |
| **Root Cause** | LLM non-determinism and training updates change summarisation behaviour. |
| **Workaround** | LCRI scores are tagged with model version. Retrain-Pulse Watcher triggers re-scoring after major model updates. Historical comparisons note model version differences. |
| **Fix Required** | None immediate. This is an inherent limitation of LLM-based scoring. Document in Client Mode reports. |
| **Date Logged** | 18 February 2026 |

---

### KNW-005: CMS Integration Limited to WordPress at Launch

| Field | Value |
|-------|-------|
| **ID** | KNW-005 |
| **Status** | 🟡 Workaround Available |
| **Severity** | Medium |
| **Description** | Autonomous deployment is built for WordPress REST API first. Webflow, Ghost, and custom webhook integrations are Phase 3+. Non-WordPress domains cannot use autonomous deployment at launch. |
| **Root Cause** | Build sequencing — WordPress is the highest-priority CMS (largest market share, AMTL's own site). |
| **Workaround** | Non-WordPress domains operate in Advisory Mode: Peterman generates deployment-ready code/markup, operator copies and pastes, Peterman verifies deployment. |
| **Fix Required** | Phase 3: Build Webflow API integration, Ghost Content API integration, GitHub API integration (static sites), and generic webhook interface. |
| **Date Logged** | 18 February 2026 |

---

### KNW-006: pgvector Index Performance at Scale

| Field | Value |
|-------|-------|
| **ID** | KNW-006 |
| **Status** | ⚪ Deferred |
| **Severity** | Low |
| **Description** | The IVFFlat index used for pgvector similarity queries (set to 100 lists) is optimised for Peterman's current expected scale (hundreds of domains, thousands of pages). At enterprise scale (10,000+ domains), the index may need re-tuning or migration to HNSW. |
| **Root Cause** | IVFFlat performance degrades with dataset size if list count is not adjusted. |
| **Workaround** | Monitor query latency. If similarity queries exceed 200ms, increase list count or switch to HNSW index. |
| **Fix Required** | None until scale requires it. Add monitoring for pgvector query latency in Phase 1 health checks. |
| **Date Logged** | 18 February 2026 |

---

### KNW-007: Google Search Console OAuth Setup Complexity

| Field | Value |
|-------|-------|
| **ID** | KNW-007 |
| **Status** | 🟡 Workaround Available |
| **Severity** | Medium |
| **Description** | GSC integration requires OAuth 2.0 setup with Google Cloud Console, domain verification, and service account credentials. This is a multi-step manual process that cannot be fully automated. |
| **Root Cause** | Google's authentication requirements. |
| **Workaround** | Peterman operates without GSC data — LLM-only tracking continues. Chamber 7 performance reports flag "partial — no GSC data" when GSC is unavailable. |
| **Fix Required** | Phase 2: Document GSC setup steps in User Manual. Provide a setup wizard in Peterman that guides the operator through OAuth configuration. |
| **Date Logged** | 18 February 2026 |

---

### KNW-008: Existing Codebase State Unknown

| Field | Value |
|-------|-------|
| **ID** | KNW-008 |
| **Status** | 🔴 Open |
| **Severity** | High |
| **Description** | An existing Peterman codebase exists at `/home/amtl/claudeman-cases/DSph2/peterman`. Its current state, test pass rate, and compatibility with v2 architecture are unknown. The v1 SPC referenced 103+/112 tests passing. |
| **Root Cause** | v2 is a major architectural change (multi-domain, new chambers, new AI stack). The existing codebase was built for v1. |
| **Fix Required** | Phase 0: Audit existing codebase. Determine what can be reused (AI engine, crawling, basic Flask structure) and what must be rebuilt (data model, chamber architecture, approval system). Log findings in DEC register. |
| **Date Logged** | 18 February 2026 |

---

## Summary

| Status | Count |
|--------|-------|
| 🔴 Open | 1 |
| 🟡 Workaround Available | 4 |
| 🟢 Fixed | 0 |
| ⚪ Deferred | 3 |
| **Total** | **8** |

---

## Template for New Entries

```markdown
### KNW-XXX: [Title]

| Field | Value |
|-------|-------|
| **ID** | KNW-XXX |
| **Status** | 🔴 Open / 🟡 Workaround / 🟢 Fixed / ⚪ Deferred |
| **Severity** | Critical / High / Medium / Low |
| **Description** | What the issue is |
| **Root Cause** | Why it exists |
| **Workaround** | How to work around it now |
| **Fix Required** | What needs to happen to resolve it |
| **Date Logged** | DD Month YYYY |
```

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 18 February 2026 | Claude (Thalaiva) | Initial register — 8 known issues from SPC and TDD creation |

---

*Almost Magic Tech Lab*
*"If it's known and not logged, it's a surprise waiting to happen."*
