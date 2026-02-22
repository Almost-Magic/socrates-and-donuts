# AMTL — Peterman Operations Runbook
## Document Code: AMTL-PTR-RUN-1.0
## Almost Magic Tech Lab
## 18 February 2026

> *This document follows AMTL-ECO-STD v1.0. All conventions defined there apply unless explicitly overridden with a Decision Register entry.*

---

## Purpose

Day-to-day running of Peterman. Not how to build it (BLD), not how to fix it when broken (DGN), not what it does (SPC) — just how to operate it.

---

## 1. Daily Operations

### 1.1 Startup

Peterman starts automatically via The Workshop. Manual startup should never be required (see AMTL-ECO-STD Section 5.2 — "No Mani SSH").

**Normal flow:**
1. Open The Workshop (port 5003)
2. Click "Start" on Peterman's card
3. Workshop starts Flask backend (port 5008) + Electron frontend
4. Peterman checks all dependencies (PostgreSQL, Redis, Ollama, SearXNG)
5. Green status indicator in Workshop = healthy

**If Workshop is unavailable:**
- Ask ELAINE: "Start Peterman"
- ELAINE triggers Workshop's recovery procedure

### 1.2 Daily Autonomous Cycle

Peterman runs its chamber cycles automatically via APScheduler. The operator does not need to trigger anything.

**What happens daily (if configured for daily cadence):**
- Chamber 1 runs LLM probes for priority keywords
- Chamber 6 checks technical health
- Chamber 11 runs defensive scans
- Budget monitor checks spend against caps
- Peterman Score is recomputed
- ELAINE receives overnight summary for morning briefing

**What happens weekly (default cadence):**
- Full LLM probe set across all target queries (5 runs each)
- All chambers run full cycle
- Competitor monitoring (Chamber 8)
- Oracle forecast update (Chamber 9)
- Client Mode report regeneration
- Budget reconciliation

### 1.3 Reviewing the Approval Inbox

The primary daily operator task is reviewing pending approvals:

1. Open War Room dashboard (Electron app or `localhost:5008`)
2. Check **Approval Inbox** (bottom section)
3. For each pending item:
   - Read the one-line impact statement
   - Check the risk level badge
   - Review estimated Peterman Score impact
   - Click **Approve**, **Decline**, or **Modify**
4. Alternatively, ELAINE presents approvals via voice — respond verbally

**Approval timing:** Low-gate items auto-deploy with a 10-second objection window via ELAINE. Medium-gate items wait for explicit yes/no. Hard-gate items require dry-run preview review.

### 1.4 Shutdown

**Normal:** Click "Stop" in The Workshop. Peterman saves state and shuts down cleanly.
**No orphaned processes:** Workshop ensures all background tasks (scheduler, probes) terminate.

---

## 2. Service Management

| Item | Detail |
|------|--------|
| **Port** | 5008 |
| **Start** | Via Workshop "Start" button or ELAINE voice command |
| **Stop** | Via Workshop "Stop" button or ELAINE voice command |
| **Restart** | Via Workshop "Restart" button |
| **Logs** | `logs/peterman.log` — JSON format, INFO level by default |
| **Health check** | `GET http://localhost:5008/api/health` |
| **Process** | Flask backend managed by Workshop/Supervisor |
| **Electron** | Desktop wrapper connects to Flask backend |

---

## 3. How to Trigger Peterman

### 3.1 Through ELAINE (Voice)

| Command | What It Does |
|---------|-------------|
| "ELAINE, what's our Peterman Score today?" | Returns current score for primary domain |
| "ELAINE, are there any active hallucinations?" | Returns open hallucination count and top severity |
| "ELAINE, what did Peterman do this week?" | Returns weekly summary of actions taken |
| "ELAINE, ask Peterman what our biggest competitive threat is" | Triggers Chamber 8 summary |
| "ELAINE, show me the Oracle's recommendations for next month" | Returns Chamber 9 forecast |
| "ELAINE, run a probe on 'AI governance Australia' right now" | Triggers immediate probe for specific query |
| "ELAINE, onboard almostmagic.net.au" | Triggers domain onboarding flow |

### 3.2 Through the War Room Dashboard

- Navigate to `localhost:5008` in browser, or open the Peterman Electron app
- Use the War Room for visual monitoring, approval actions, and drill-down into chambers

### 3.3 Through Workshop

- Launch/stop/restart Peterman from The Workshop's app grid
- View health status alongside other ecosystem apps

---

## 4. Interpreting Results

### 4.1 The Peterman Score

| Range | Colour | Meaning |
|-------|--------|---------|
| 0–40 | Red | Critical — domain has significant SEO and LLM presence issues |
| 40–65 | Amber | Needs attention — some areas working, others have gaps |
| 65–85 | Gold | Healthy — domain is well-positioned with room for improvement |
| 85–100 | Platinum | Excellent — domain is a default answer for target queries |

**Confidence interval:** A score of "67 ± 4" is reliable. A score of "67 ± 19" means data is noisy — check probe consistency.

### 4.2 Chamber Status Indicators

| Indicator | Meaning |
|-----------|---------|
| Green pulse | Healthy — chamber is running normally |
| Amber pulse | Attention — chamber detected something worth reviewing |
| Red pulse | Action pending — chamber has flagged an issue requiring approval |

### 4.3 Hallucination Severity (1–10)

| Range | Level | Example |
|-------|-------|---------|
| 1–3 | Low | Minor factual error unlikely to affect business |
| 4–6 | Medium | Noticeable error that could mislead potential clients |
| 7–9 | High | Significant false claim with reputational or financial impact |
| 10 | Critical | Persistent false claim across multiple LLMs — emergency response |

### 4.4 Approval Risk Levels

| Level | What It Means |
|-------|---------------|
| Auto-deploy | Already done — low risk, reversible. You'll see it in the timeline. |
| Low-gate | ELAINE announced it. Object within 10 seconds if you disagree. |
| Medium-gate | Awaiting your yes/no. Review the approval card. |
| Hard-gate | High stakes. Review the dry-run preview before approving. |
| Prohibited | Peterman advises only. You must execute this yourself. |

---

## 5. Backup & Recovery

### 5.1 What to Back Up

| Data | Location | Backup Method |
|------|----------|---------------|
| PostgreSQL database | Port 5433 | `pg_dump peterman > peterman_backup.sql` (daily) |
| `.env` file | Peterman root folder | Manual copy to secure location |
| Deployment snapshots | In PostgreSQL (deployments table) | Included in pg_dump |
| Audit log | In PostgreSQL (audit_log table) | Included in pg_dump |

### 5.2 Recovery

1. **If the database is lost:** Restore from latest pg_dump. All probe results, hallucination records, and audit history are recovered.
2. **If Redis is lost:** Redis only holds ephemeral queue data. Restart Redis — pending briefs are also tracked in PostgreSQL.
3. **If the codebase is lost:** Clone from `Almost-Magic/peterman` on GitHub. Restore `.env` from secure backup. Run `pip install -r requirements.txt`. Start via Workshop.

---

## 6. Updates & Maintenance

### 6.1 Dependency Updates

- Quarterly: Review `requirements.txt` for security vulnerabilities
- After any update: Run full regression test suite before deploying
- Never update dependencies without running tests

### 6.2 LLM Model Updates

When Ollama models are updated:
- Peterman's Retrain-Pulse Watcher detects the update
- Re-probe burst scheduled within 48 hours for all active domains
- LCRI scores flagged for re-computation with new model version

### 6.3 Database Maintenance

- Monthly: `VACUUM ANALYZE` on all tables
- Monthly: Check pgvector index performance (if similarity queries >200ms, re-tune)
- Quarterly: Archive expired deployment snapshots (>30 days)
- Weekly: Budget tracking cleanup (archive records >90 days old)

---

## 7. Scheduled Tasks

| Task | Cadence | Trigger | Chamber |
|------|---------|---------|---------|
| LLM probes (priority keywords) | Daily or weekly (per domain config) | APScheduler | Chamber 1 |
| Technical health scan | Daily | APScheduler | Chamber 6 |
| Defensive perception scan | Weekly | APScheduler | Chamber 11 |
| Competitor monitoring | Weekly | APScheduler | Chamber 8 |
| Oracle forecast update | Weekly | APScheduler | Chamber 9 |
| Budget reconciliation | Hourly | APScheduler | Budget Monitor |
| Peterman Score recomputation | After any chamber cycle completes | Event-driven | Score Engine |
| Deployment snapshot expiry | Daily | APScheduler | Rollback Layer |
| ELAINE morning briefing data | Daily at 6:00am AEST | APScheduler | Notification Service |
| Client Mode report regeneration | Weekly (Monday 7:00am AEST) | APScheduler | Report Engine |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 18 February 2026 | Claude (Thalaiva) | Initial runbook — daily ops, service management, scheduling |

---

*Almost Magic Tech Lab*
*"The machine runs. You approve. The score goes up."*
