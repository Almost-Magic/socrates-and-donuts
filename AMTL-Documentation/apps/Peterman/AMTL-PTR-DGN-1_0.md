# AMTL — Peterman Diagnostic Playbook
## Document Code: AMTL-PTR-DGN-1.0
## Almost Magic Tech Lab
## 18 February 2026

> *This document follows AMTL-ECO-STD v1.0. All conventions defined there apply unless explicitly overridden with a Decision Register entry.*

---

## Purpose

Something broke — how do I fix it? This playbook covers symptom → likely cause → diagnosis steps → fix for every significant failure mode in Peterman.

---

## Escalation Levels

| Level | Who/What | Time |
|-------|----------|------|
| 0 | Peterman self-heal (health check + auto-restart) | 0 seconds |
| 1 | Workshop auto-recovery (simple restart) | 10 seconds |
| 2 | Workshop deep restart (restart + verify dependencies) | 30 seconds |
| 3 | Workshop full recovery (kill + clear + start) | 60 seconds |
| 4 | ELAINE diagnosis (reads MRD trees) | 1–5 minutes |
| 5 | Cline/Guruve (reads MRD, applies code fix) | 5–30 minutes |
| 6 | Mani notified (reviews proposed fix, approves or redirects) | Human decides |

**Rule:** You should never reach Level 6 for the same problem twice.

---

## Symptom Category 1: Peterman Won't Start

### Symptom 1.1: Flask process fails to start, port 5008 not listening

**Likely causes:**
1. Port 5008 already in use by another process
2. PostgreSQL not running (port 5433)
3. Missing or corrupt `.env` file
4. Python dependency missing or version conflict

**Diagnosis steps:**
1. Check port: `netstat -tlnp | grep 5008` — is something else using it?
2. Check PostgreSQL: `pg_isready -h localhost -p 5433` — is it responding?
3. Check `.env`: Does it exist? Are all required variables present?
4. Check dependencies: `pip check` — any conflicts?

**Fix:**

| Cause | Fix | Escalation |
|-------|-----|------------|
| Port conflict | Kill the competing process | Level 1 (Workshop restart) |
| PostgreSQL down | Start PostgreSQL container | Level 2 (Workshop deep restart) |
| `.env` missing | Restore from `.env.example` + secure backup | Level 5 (Guruve) |
| Dependency conflict | `pip install -r requirements.txt --force-reinstall` | Level 5 (Guruve) |

---

### Symptom 1.2: Electron app shows blank white screen

**Likely causes:**
1. Flask backend not running (Electron connects to localhost:5008)
2. Flask started but index.html has a JavaScript error
3. CORS issue between Electron and Flask

**Diagnosis steps:**
1. Open browser at `localhost:5008` — does the SPA load?
2. Check browser console (F12) for JavaScript errors
3. Check Flask logs at `logs/peterman.log`

**Fix:**

| Cause | Fix | Escalation |
|-------|-----|------------|
| Backend not running | Start Flask via Workshop | Level 1 |
| JS error | Check logs, fix frontend code | Level 5 (Guruve) |
| CORS issue | Verify flask-cors configuration in app factory | Level 5 (Guruve) |

---

## Symptom Category 2: Health Check Failures

### Symptom 2.1: `/api/health` returns dependency as unhealthy

**Diagnosis by dependency:**

| Dependency | Check | Likely Cause | Fix |
|------------|-------|-------------|-----|
| PostgreSQL | `pg_isready -h localhost -p 5433` | Docker container stopped | Restart Docker container |
| Redis | `redis-cli -p 6379 ping` | Docker container stopped | Restart Docker container |
| Ollama | `curl http://localhost:9000/api/tags` | Supervisor or Ollama process crashed | Restart Supervisor, then Ollama |
| SearXNG | `curl http://localhost:8888/healthz` | Docker container stopped | Restart Docker container |
| ELAINE | `curl http://localhost:5000/api/health` | ELAINE Flask process crashed | Restart ELAINE via Workshop |
| Claude Desktop | Check process list for Claude | App closed or crashed | Relaunch Claude Desktop |

**Escalation:** Level 2 (Workshop deep restart) for Docker dependencies. Level 4 (ELAINE diagnosis) if multiple dependencies fail simultaneously.

---

## Symptom Category 3: Probing Failures

### Symptom 3.1: LLM probes return no data or "missed probe" logged

**Likely causes:**
1. External API key expired or rate-limited (OpenAI, Anthropic)
2. Ollama model not loaded (nomic-embed-text, llama3.1)
3. Network connectivity issue to external APIs
4. Budget cap reached — probing paused automatically

**Diagnosis steps:**
1. Check `logs/peterman.log` for probe error messages
2. Check budget monitor: `GET /api/domains/<id>/budget` — is domain at 100%?
3. Test Ollama directly: `curl http://localhost:9000/api/generate -d '{"model":"llama3.1:8b","prompt":"test"}'`
4. Test external API: check API dashboard for rate limit or billing status

**Fix:**

| Cause | Fix | Escalation |
|-------|-----|------------|
| API key expired | Update key in `.env`, restart Flask | Level 6 (Mani — requires new key) |
| Rate limited | Wait for rate limit reset. Reduce probe frequency. | Level 0 (automatic — scheduler retries next cycle) |
| Ollama model missing | `ollama pull llama3.1:8b` via Supervisor | Level 2 |
| Budget cap reached | Approve budget extension or wait for weekly reset | Level 6 (Mani decision) |

---

### Symptom 3.2: Peterman Score shows "partial data" badge

**Likely cause:** One or more LLM providers were unavailable during the last probe cycle.

**Diagnosis steps:**
1. Check which provider(s) failed: `GET /api/domains/<id>/chambers/1` — look at per-model SoV
2. Models showing `null` or `confidence: 0` indicate missed probes

**Fix:** Not urgent. Score updates on next successful cycle. If persistent (3+ cycles), investigate the specific provider (see Symptom 3.1).

---

## Symptom Category 4: Deployment Failures

### Symptom 4.1: CMS deployment fails — change not applied to live site

**Likely causes:**
1. CMS API credentials expired or revoked
2. CMS API endpoint unreachable (site down, firewall, DNS)
3. Partial deployment — Peterman halted mid-operation
4. CMS rate limit exceeded

**Diagnosis steps:**
1. Check `logs/peterman.log` for deployment error details
2. Check audit log: `GET /api/domains/<id>/audit` — look for `outcome: "failed"` entries
3. Test CMS API directly: `curl -H "Authorization: Bearer <key>" https://[site]/wp-json/wp/v2/posts`
4. Check deployment queue: `GET /api/domains/<id>/deployments` — are items stuck?

**Fix:**

| Cause | Fix | Escalation |
|-------|-----|------------|
| Credentials expired | Update CMS API key in domain settings | Level 6 (Mani — requires new key) |
| Site unreachable | Wait for site recovery. Peterman auto-retries every 6 hours (max 3). | Level 0 |
| Partial deployment | Peterman auto-rolls back partial changes. Verify via timeline. | Level 0 |
| Rate limit | Wait and retry. Reduce deployment frequency. | Level 0 |

**Critical rule:** Peterman never leaves a partial deployment. If a CMS API call fails mid-deploy, the rollback layer restores the pre-change state automatically.

---

### Symptom 4.2: Rollback fails

**Likely causes:**
1. Rollback snapshot expired (>30 days)
2. CMS API unavailable (same as deployment failure)
3. Live site has been manually changed since the snapshot was taken

**Diagnosis steps:**
1. Check snapshot status: is it "available", "used", or "expired"?
2. If expired: snapshot data still exists in database but is marked non-rollbackable
3. If CMS API issue: same diagnosis as Symptom 4.1

**Fix:**

| Cause | Fix | Escalation |
|-------|-----|------------|
| Snapshot expired | Manual rollback — use the HTML diff from the snapshot to apply changes manually | Level 6 (Mani) |
| CMS API down | Wait for API recovery, retry rollback | Level 0 |
| Manual changes conflict | Review diff carefully. May need manual reconciliation. | Level 6 (Mani) |

---

## Symptom Category 5: AI Engine Failures

### Symptom 5.1: Claude Desktop unresponsive — tasks queuing

**Likely causes:**
1. Claude Desktop app not running
2. MCP socket unavailable or misconfigured
3. Claude Desktop is busy with another task (single-user app)

**Diagnosis steps:**
1. Check if Claude Desktop process is running
2. Check MCP socket availability (if using MCP)
3. Check `logs/peterman.log` for "Claude Desktop unavailable, failing over to..." messages

**Fix:**

| Cause | Fix | Escalation |
|-------|-----|------------|
| App not running | Relaunch Claude Desktop | Level 1 |
| MCP socket issue | Verify MCP configuration. If unreliable, switch to clipboard bridge (see KNW-001). | Level 5 (Guruve) |
| Busy/unresponsive | Fallback chain activates automatically: Manus → Perplexity → Ollama | Level 0 |

**Note:** If all AI engines in the fallback chain are unavailable, tasks are queued (not dropped) and ELAINE alerts the operator. No task is ever silently abandoned.

---

### Symptom 5.2: Embeddings failing — "embedding engine unavailable"

**Likely cause:** Ollama is down or nomic-embed-text model is not loaded.

**Diagnosis steps:**
1. Check Supervisor: `curl http://localhost:9000/api/tags`
2. Check if nomic-embed-text is in the model list
3. Check Ollama directly: `curl http://localhost:11434/api/tags`

**Fix:**

| Cause | Fix | Escalation |
|-------|-----|------------|
| Ollama down | Restart Ollama via Supervisor | Level 2 |
| Model not loaded | `ollama pull nomic-embed-text` | Level 2 |
| Supervisor down | Restart Supervisor, then Ollama registers | Level 2 |

---

## Symptom Category 6: ELAINE Integration Issues

### Symptom 6.1: Content briefs not reaching ELAINE

**Likely causes:**
1. ELAINE not running (port 5000 not responding)
2. ELAINE integration endpoint changed or misconfigured
3. Brief payload format mismatch

**Diagnosis steps:**
1. Check ELAINE health: `curl http://localhost:5000/api/health`
2. Check Peterman logs for "ELAINE brief submission failed" messages
3. Check ELAINE logs for "malformed brief" or "unknown source" errors

**Fix:**

| Cause | Fix | Escalation |
|-------|-----|------------|
| ELAINE down | Restart ELAINE via Workshop | Level 1 |
| Endpoint mismatch | Verify `AMTL_PTR_ELAINE_URL` in `.env` | Level 5 (Guruve) |
| Payload issue | Check brief format against AMTL-PTR-TDD-1.0 Section 5.3 | Level 5 (Guruve) |

---

### Symptom 6.2: ELAINE voice approvals not working

**Likely causes:**
1. ELAINE's voice pipeline is down (separate from ELAINE's API)
2. Approval request format has changed
3. ELAINE received the approval request but couldn't parse it

**Diagnosis steps:**
1. Check if ELAINE responds to other voice commands (test with "ELAINE, what time is it?")
2. Check Peterman logs for successful POST to ELAINE approval endpoint
3. Check ELAINE logs for Peterman-related errors

**Fix:** If ELAINE voice is down, use the War Room Approval Inbox as a fallback — all pending approvals are available there regardless of ELAINE status.

---

## Symptom Category 7: Database Issues

### Symptom 7.1: "Database connection failed" errors

**Likely causes:**
1. PostgreSQL container stopped
2. Connection pool exhausted
3. Database disk full
4. Network issue between Flask and PostgreSQL

**Diagnosis steps:**
1. Check PostgreSQL: `pg_isready -h localhost -p 5433`
2. Check disk space: `df -h` on the machine hosting PostgreSQL
3. Check active connections: `SELECT count(*) FROM pg_stat_activity WHERE datname = 'peterman';`

**Fix:**

| Cause | Fix | Escalation |
|-------|-----|------------|
| Container stopped | Restart Docker container | Level 2 |
| Pool exhausted | Restart Flask (releases connections). If recurring, increase pool size. | Level 2 / Level 5 |
| Disk full | Archive old data, expand storage | Level 6 (Mani) |

---

### Symptom 7.2: pgvector similarity queries very slow (>200ms)

**Likely cause:** IVFFlat index needs re-tuning for current data volume (see KNW-006).

**Diagnosis steps:**
1. Check row count: `SELECT count(*) FROM domain_embeddings;`
2. Check index health: `SELECT * FROM pg_stat_user_indexes WHERE relname = 'domain_embeddings';`
3. Test query time: `EXPLAIN ANALYZE SELECT ... ORDER BY embedding <=> '[...]' LIMIT 10;`

**Fix:**

| Data Volume | Fix |
|-------------|-----|
| <10,000 rows | Increase IVFFlat lists parameter to 200 |
| 10,000–100,000 rows | Switch to HNSW index |
| >100,000 rows | Consider separate pgvector instance or dedicated vector DB |

Escalation: Level 5 (Guruve) for index changes.

---

## Symptom Category 8: Budget & Cost Issues

### Symptom 8.1: Domain probing paused — "budget cap reached"

**This is expected behaviour, not a bug.** The budget monitor pauses probing when the per-domain weekly cap is reached.

**Options:**
1. Wait for weekly reset (resets every 7 days from domain creation)
2. Approve emergency budget extension: via ELAINE ("approve budget extension for [domain]") or War Room domain settings
3. Reduce probe frequency: switch from daily to weekly cadence
4. Reduce target LLMs: drop expensive external probes, keep Ollama (free)

---

## Symptom Category 9: Frontend/UI Issues

### Symptom 9.1: Peterman Score gauge not animating or showing wrong colour

**Likely causes:**
1. JavaScript error in score-gauge.js
2. Score data not loading (API call failing)
3. Browser cache serving old CSS/JS

**Diagnosis steps:**
1. Open browser developer tools (F12) — check Console for errors
2. Check Network tab — is the `/api/domains/<id>/score` call returning data?
3. Hard refresh: Ctrl+Shift+R

**Fix:** Clear browser cache. If in Electron, restart the Electron app. If score API is failing, check Flask logs.

---

### Symptom 9.2: Semantic Map not rendering

**Likely cause:** Chamber 2 (Semantic Gravity) hasn't completed its first cycle yet, so there's no embedding data to plot.

**Fix:** Wait for Chamber 2 to run (scheduled or manually trigger via `POST /api/domains/<id>/chambers/2/run`). The map appears after the first embedding cycle completes.

---

### Symptom 9.3: Dark/light mode toggle not persisting

**Likely cause:** Theme preference stored in localStorage. If Electron app data was cleared, preference resets.

**Fix:** Toggle again. If persistent, check that the Electron app has write access to its local storage directory.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 18 February 2026 | Claude (Thalaiva) | Initial playbook — 9 symptom categories, all escalation paths |

---

*Almost Magic Tech Lab*
*"Something broke. This is the repair manual. Start here."*
