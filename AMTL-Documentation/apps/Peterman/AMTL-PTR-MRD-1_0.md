# AMTL — Peterman Machine-Readable Diagnostics
## Document Code: AMTL-PTR-MRD-1.0
## Almost Magic Tech Lab
## 18 February 2026

> *This document follows AMTL-ECO-STD v1.0. All conventions defined there apply unless explicitly overridden with a Decision Register entry.*

---

## Purpose

YAML diagnostic trees that ELAINE, Cline, and Workshop can execute programmatically to diagnose and fix Peterman issues without human intervention. These are the machine-readable equivalents of the human-readable Diagnostic Playbook (AMTL-PTR-DGN-1.0).

---

## Usage Instructions

### How ELAINE Reads This

ELAINE loads these YAML trees and walks them top-down:
1. Match current symptom to a tree's `symptom` field
2. Execute each `check` in order
3. If a check passes: move to `if_pass` (next check or "healthy")
4. If a check fails: read `if_fail` → attempt `auto_fix` if available → verify fix → escalate if fix fails

### How Cline/Guruve Reads This

Cline loads the tree, executes checks via shell commands, applies fixes, and verifies. If auto-fix fails or escalation level exceeds 5, Cline presents the situation to Mani for decision.

### How Workshop Reads This

Workshop uses these trees for its 3-tier auto-recovery:
- Tier 1 (simple restart): Execute Level 0–1 fixes
- Tier 2 (deep restart): Execute Level 2 fixes (restart + dependency verification)
- Tier 3 (full recovery): Execute Level 3 fixes (kill + clear + fresh start)

---

## Escalation Levels Reference

```
Level 0: Self-heal (app's own health check)              → 0 seconds
Level 1: Workshop auto-recovery (simple restart)          → 10 seconds
Level 2: Workshop deep restart (restart + deps)           → 30 seconds
Level 3: Workshop full recovery (kill + clear + start)    → 60 seconds
Level 4: ELAINE diagnosis (reads MRD trees)               → 1-5 minutes
Level 5: Cline/Guruve (reads MRD, applies code fix)       → 5-30 minutes
Level 6: Mani notified (shows diagnosis + fix option)     → Human decides
```

---

## Diagnostic Trees

### Tree 1: Peterman Service Health

```yaml
diagnostic_tree:
  id: PTR-DIAG-001
  name: "Peterman Service Health"
  symptom: "Peterman is not responding or /api/health returns error"
  severity: critical
  checks:
    - id: check_01
      description: "Is Flask process running on port 5008?"
      type: port_check
      target: "localhost:5008"
      expect: "listening"
      if_pass: check_02
      if_fail:
        diagnosis: "Flask process is not running"
        auto_fix:
          type: service_restart
          action: "cd /home/amtl/peterman && python -m flask run --port 5008 &"
          verify: "curl -s -o /dev/null -w '%{http_code}' http://localhost:5008/api/health"
          expect: "200"
          timeout_seconds: 15
        escalate:
          level: 1
          message: "Peterman Flask process failed to start after restart attempt"

    - id: check_02
      description: "Is PostgreSQL responding on port 5433?"
      type: command
      target: "pg_isready -h localhost -p 5433"
      expect: "accepting connections"
      if_pass: check_03
      if_fail:
        diagnosis: "PostgreSQL is not running — Peterman cannot function without database"
        auto_fix:
          type: docker_restart
          action: "docker start peterman-postgres"
          verify: "pg_isready -h localhost -p 5433"
          expect: "accepting connections"
          timeout_seconds: 30
        escalate:
          level: 2
          message: "PostgreSQL container failed to start"

    - id: check_03
      description: "Is Redis responding on port 6379?"
      type: command
      target: "redis-cli -p 6379 ping"
      expect: "PONG"
      if_pass: check_04
      if_fail:
        diagnosis: "Redis is not running — queue functionality degraded"
        auto_fix:
          type: docker_restart
          action: "docker start peterman-redis"
          verify: "redis-cli -p 6379 ping"
          expect: "PONG"
          timeout_seconds: 15
        escalate:
          level: 2
          message: "Redis container failed to start"

    - id: check_04
      description: "Is Ollama responding via Supervisor on port 9000?"
      type: http_check
      target: "http://localhost:9000/api/tags"
      expect: "status_200"
      if_pass: check_05
      if_fail:
        diagnosis: "Ollama/Supervisor not responding — AI inference and embeddings unavailable"
        auto_fix:
          type: service_restart
          action: "systemctl restart ollama && sleep 5"
          verify: "curl -s -o /dev/null -w '%{http_code}' http://localhost:9000/api/tags"
          expect: "200"
          timeout_seconds: 30
        escalate:
          level: 2
          message: "Ollama failed to restart via Supervisor"

    - id: check_05
      description: "Does /api/health return all dependencies healthy?"
      type: http_check
      target: "http://localhost:5008/api/health"
      expect: "status_200_body_contains_healthy"
      if_pass: "healthy"
      if_fail:
        diagnosis: "Peterman running but one or more dependencies unhealthy"
        auto_fix:
          type: none
          action: "Parse /api/health response to identify failing dependency, run targeted fix"
        escalate:
          level: 4
          message: "ELAINE should parse health response and diagnose specific failing dependency"
```

---

### Tree 2: LLM Probe Failure

```yaml
diagnostic_tree:
  id: PTR-DIAG-002
  name: "LLM Probe Failure"
  symptom: "Probe cycle completes with missed probes or Peterman Score shows partial data"
  severity: medium
  checks:
    - id: check_01
      description: "Is the budget cap reached for the affected domain?"
      type: api_check
      target: "http://localhost:5008/api/domains/{domain_id}/budget"
      expect: "budget_remaining > 0"
      if_pass: check_02
      if_fail:
        diagnosis: "Budget cap reached — probing paused by design"
        auto_fix:
          type: none
          action: "Notify operator — budget cap reached, probing paused until weekly reset"
        escalate:
          level: 6
          message: "Domain budget cap reached. Operator must approve extension or wait for reset."

    - id: check_02
      description: "Is Ollama available for local probes?"
      type: http_check
      target: "http://localhost:9000/api/tags"
      expect: "status_200"
      if_pass: check_03
      if_fail:
        diagnosis: "Ollama unavailable — local probes cannot run"
        auto_fix:
          type: service_restart
          action: "systemctl restart ollama && sleep 5"
          verify: "curl -s -o /dev/null -w '%{http_code}' http://localhost:9000/api/tags"
          expect: "200"
          timeout_seconds: 30
        escalate:
          level: 2
          message: "Ollama failed to restart — local probes and embeddings unavailable"

    - id: check_03
      description: "Are required Ollama models loaded?"
      type: command
      target: "curl -s http://localhost:9000/api/tags | grep nomic-embed-text"
      expect: "nomic-embed-text found in output"
      if_pass: check_04
      if_fail:
        diagnosis: "nomic-embed-text model not loaded in Ollama"
        auto_fix:
          type: command
          action: "ollama pull nomic-embed-text"
          verify: "curl -s http://localhost:9000/api/tags | grep nomic-embed-text"
          expect: "nomic-embed-text found"
          timeout_seconds: 120
        escalate:
          level: 2
          message: "Failed to pull nomic-embed-text model"

    - id: check_04
      description: "Check logs for external API errors (OpenAI, Anthropic)"
      type: log_check
      target: "logs/peterman.log"
      search: "probe.*error|api.*timeout|rate.*limit|401|403|429"
      expect: "no matches in last 24 hours"
      if_pass: "healthy"
      if_fail:
        diagnosis: "External LLM API errors detected — check API keys and rate limits"
        auto_fix:
          type: none
          action: "Parse log errors. If 401/403: API key issue (escalate). If 429: rate limit (auto-retry next cycle). If timeout: network issue (auto-retry)."
        escalate:
          level: 5
          message: "External API errors detected. Guruve to check API key validity and rate limit status."
```

---

### Tree 3: CMS Deployment Failure

```yaml
diagnostic_tree:
  id: PTR-DIAG-003
  name: "CMS Deployment Failure"
  symptom: "Deployment action logged as failed, change not applied to live site"
  severity: high
  checks:
    - id: check_01
      description: "Was a rollback automatically triggered?"
      type: api_check
      target: "http://localhost:5008/api/domains/{domain_id}/deployments/{deployment_id}"
      expect: "rollback_status is 'used' or deployment.outcome is 'rolled_back'"
      if_pass: check_02
      if_fail:
        diagnosis: "Deployment failed but rollback did not trigger — potential partial state"
        auto_fix:
          type: api_call
          action: "POST http://localhost:5008/api/domains/{domain_id}/deployments/{deployment_id}/rollback"
          verify: "GET deployment — check rollback_status is 'used'"
          expect: "rollback successful"
          timeout_seconds: 60
        escalate:
          level: 4
          message: "Manual rollback also failed — ELAINE should alert operator immediately"

    - id: check_02
      description: "Is the CMS API reachable?"
      type: http_check
      target: "{domain_cms_api_url}"
      expect: "status_200 or status_401"
      if_pass: check_03
      if_fail:
        diagnosis: "CMS API unreachable — site may be down"
        auto_fix:
          type: queue
          action: "Queue deployment for retry in 6 hours"
          verify: "Check queue entry created"
          expect: "retry scheduled"
          timeout_seconds: 5
        escalate:
          level: 0
          message: "CMS unreachable — deployment queued for automatic retry (3 retries, 6-hour intervals)"

    - id: check_03
      description: "Are CMS API credentials valid?"
      type: http_check
      target: "{domain_cms_api_url}/wp-json/wp/v2/posts"
      headers:
        Authorization: "Bearer {domain_cms_api_key}"
      expect: "status_200"
      if_pass: check_04
      if_fail:
        diagnosis: "CMS API credentials invalid or expired"
        auto_fix:
          type: none
          action: "Cannot auto-fix — operator must provide new CMS API credentials"
        escalate:
          level: 6
          message: "CMS API credentials expired for domain {domain_name}. Operator must update."

    - id: check_04
      description: "Check deployment error details in audit log"
      type: api_check
      target: "http://localhost:5008/api/domains/{domain_id}/audit?action_type=deployment&outcome=failed"
      expect: "recent failure entries found"
      if_pass: "diagnosed"
      if_fail:
        diagnosis: "No failure details in audit log — investigate Flask logs directly"
        auto_fix:
          type: none
          action: "Check logs/peterman.log for deployment-related errors"
        escalate:
          level: 5
          message: "Deployment failure with no audit trail — Guruve to investigate Flask logs"
```

---

### Tree 4: ELAINE Integration Failure

```yaml
diagnostic_tree:
  id: PTR-DIAG-004
  name: "ELAINE Integration Failure"
  symptom: "Content briefs not reaching ELAINE, approval requests not being presented, or status queries returning errors"
  severity: medium
  checks:
    - id: check_01
      description: "Is ELAINE running on port 5000?"
      type: http_check
      target: "http://localhost:5000/api/health"
      expect: "status_200"
      if_pass: check_02
      if_fail:
        diagnosis: "ELAINE is down — all ELAINE integration unavailable"
        auto_fix:
          type: workshop_action
          action: "Trigger Workshop restart for ELAINE"
          verify: "curl -s -o /dev/null -w '%{http_code}' http://localhost:5000/api/health"
          expect: "200"
          timeout_seconds: 30
        escalate:
          level: 2
          message: "ELAINE failed to restart — Workshop deep recovery needed"

    - id: check_02
      description: "Can Peterman reach ELAINE's integration endpoint?"
      type: http_check
      target: "http://localhost:5000/api/integration/brief"
      method: "OPTIONS"
      expect: "status_200 or status_405"
      if_pass: check_03
      if_fail:
        diagnosis: "ELAINE integration endpoint not available — may have changed or be misconfigured"
        auto_fix:
          type: none
          action: "Verify AMTL_PTR_ELAINE_URL in .env matches ELAINE's actual integration endpoint"
        escalate:
          level: 5
          message: "ELAINE integration endpoint mismatch — Guruve to verify URL configuration"

    - id: check_03
      description: "Are briefs being queued locally when ELAINE is unavailable?"
      type: api_check
      target: "http://localhost:5008/api/domains/{domain_id}/briefs?status=queued"
      expect: "queued briefs exist"
      if_pass: "diagnosed — briefs queued, ELAINE was temporarily unavailable"
      if_fail:
        diagnosis: "No briefs queued — brief generation may be the issue, not ELAINE integration"
        auto_fix:
          type: none
          action: "Check Chamber 10 (Forge) status and logs for brief generation errors"
        escalate:
          level: 4
          message: "Brief generation may have failed — ELAINE to run Chamber 10 diagnostics"
```

---

### Tree 5: Database Connection Failure

```yaml
diagnostic_tree:
  id: PTR-DIAG-005
  name: "Database Connection Failure"
  symptom: "Peterman reports database connection errors, data not persisting, or API calls returning 500 errors"
  severity: critical
  checks:
    - id: check_01
      description: "Is PostgreSQL accepting connections?"
      type: command
      target: "pg_isready -h localhost -p 5433"
      expect: "accepting connections"
      if_pass: check_02
      if_fail:
        diagnosis: "PostgreSQL not running"
        auto_fix:
          type: docker_restart
          action: "docker start peterman-postgres"
          verify: "pg_isready -h localhost -p 5433"
          expect: "accepting connections"
          timeout_seconds: 30
        escalate:
          level: 2
          message: "PostgreSQL container failed to start — check Docker logs"

    - id: check_02
      description: "Can the peterman_app user connect?"
      type: command
      target: "psql -h localhost -p 5433 -U peterman_app -d peterman -c 'SELECT 1;'"
      expect: "1 row returned"
      if_pass: check_03
      if_fail:
        diagnosis: "Database user authentication failed — credentials may have changed"
        auto_fix:
          type: none
          action: "Verify AMTL_PTR_DB_URL in .env matches actual database credentials"
        escalate:
          level: 5
          message: "Database authentication failure — Guruve to verify credentials"

    - id: check_03
      description: "Is pgvector extension enabled?"
      type: command
      target: "psql -h localhost -p 5433 -U peterman_app -d peterman -c 'SELECT extversion FROM pg_extension WHERE extname = $$vector$$;'"
      expect: "version returned"
      if_pass: check_04
      if_fail:
        diagnosis: "pgvector extension not enabled — embeddings will fail"
        auto_fix:
          type: command
          action: "psql -h localhost -p 5433 -U postgres -d peterman -c 'CREATE EXTENSION IF NOT EXISTS vector;'"
          verify: "psql -h localhost -p 5433 -U peterman_app -d peterman -c 'SELECT extversion FROM pg_extension WHERE extname = $$vector$$;'"
          expect: "version returned"
          timeout_seconds: 10
        escalate:
          level: 5
          message: "Failed to enable pgvector extension — Guruve to investigate"

    - id: check_04
      description: "Check disk space for PostgreSQL data directory"
      type: command
      target: "df -h /var/lib/postgresql/data | tail -1 | awk '{print $5}' | tr -d '%'"
      expect: "value < 90"
      if_pass: "healthy"
      if_fail:
        diagnosis: "Disk space critically low — database may stop accepting writes"
        auto_fix:
          type: command
          action: "psql -h localhost -p 5433 -U peterman_app -d peterman -c 'VACUUM FULL;'"
          verify: "df check again"
          expect: "space freed"
          timeout_seconds: 300
        escalate:
          level: 6
          message: "Disk space critically low. Operator must archive data or expand storage."
```

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 18 February 2026 | Claude (Thalaiva) | Initial MRD — 5 diagnostic trees covering service health, probing, deployment, ELAINE integration, database |

---

*Almost Magic Tech Lab*
*"Machines diagnose. Machines fix. Humans sleep."*
