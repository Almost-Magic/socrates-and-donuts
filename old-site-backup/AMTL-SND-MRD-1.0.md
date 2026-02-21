# Socrates & Donuts — Machine-Readable Diagnostics
## Document Code: AMTL-SND-MRD-1.0
## Almost Magic Tech Lab
## 19 February 2026

> *This document follows AMTL-ECO-STD v1.0. All conventions defined there apply unless explicitly overridden with a Decision Register entry.*

---

## Purpose

YAML diagnostic trees that ELAINE, Cline, Workshop, and Supervisor can parse and execute automatically when S&D has issues.

---

## Usage

### ELAINE
Reads these trees when asked "What's wrong with Socrates and Donuts?" or when Workshop reports S&D as unhealthy. ELAINE executes checks in order, applies auto-fixes where available, and reports results to Mani.

### Cline/Guruve
Reads these trees when given a fix instruction. Uses the `auto_fix` blocks to understand what needs to change and where.

### Workshop
Uses the startup and health trees for automated recovery (Levels 1–3).

---

## Diagnostic Trees

```yaml
# =============================================================
# TREE 1: S&D Startup Failure
# =============================================================
- id: snd-startup-failure
  name: "S&D Startup Failure"
  symptom: "S&D desktop app fails to start or health endpoint unreachable"
  severity: high
  checks:
    - id: check-port-available
      description: "Is port 5010 free?"
      type: port_check
      target: 5010
      expect: "free"
      if_pass: "next"
      if_fail:
        diagnosis: "Port 5010 is occupied by another process"
        auto_fix:
          type: kill_port
          action: "Kill process on port 5010"
          command: "fuser -k 5010/tcp"
          verify: "Port 5010 is now free"
        escalate: 1

    - id: check-python-available
      description: "Is Python 3.12+ available?"
      type: command_check
      target: "python3 --version"
      expect: "Python 3.12"
      if_pass: "next"
      if_fail:
        diagnosis: "Python 3.12+ not found in PATH"
        auto_fix:
          type: none
          action: "Python installation required — cannot auto-fix"
        escalate: 5

    - id: check-requirements
      description: "Are Python dependencies installed?"
      type: command_check
      target: "python3 -c 'import flask; import dotenv'"
      expect: "exit code 0"
      if_pass: "next"
      if_fail:
        diagnosis: "Missing Python dependencies"
        auto_fix:
          type: command
          action: "pip install -r requirements.txt --break-system-packages"
          verify: "python3 -c 'import flask' exits with 0"
        escalate: 2

    - id: check-flask-starts
      description: "Does Flask start successfully?"
      type: process_start
      target: "python3 -m app"
      expect: "Process running, port 5010 listening within 10 seconds"
      if_pass: "next"
      if_fail:
        diagnosis: "Flask application crashes on startup"
        auto_fix:
          type: log_analysis
          action: "Read logs/snd.log for traceback, identify failing module"
        escalate: 5

    - id: check-health-endpoint
      description: "Does /api/health return 200?"
      type: http_check
      target: "http://localhost:5010/api/health"
      expect: "HTTP 200 with JSON body containing status field"
      if_pass: "resolved"
      if_fail:
        diagnosis: "Flask is running but health endpoint failing"
        auto_fix:
          type: restart
          action: "Full restart of S&D backend"
          command: "kill Flask process, wait 2s, start again"
          verify: "GET /api/health returns 200"
        escalate: 3

# =============================================================
# TREE 2: S&D LLM Connection Failure
# =============================================================
- id: snd-llm-failure
  name: "S&D LLM Connection Failure"
  symptom: "AI features unavailable or LLM connection test fails"
  severity: medium
  checks:
    - id: check-llm-configured
      description: "Is an LLM provider configured?"
      type: config_check
      target: "AMTL_SND_LLM_PROVIDER"
      expect: "not 'none' and not empty"
      if_pass: "next"
      if_fail:
        diagnosis: "No LLM provider configured — this is normal if user hasn't set one up"
        auto_fix:
          type: none
          action: "Inform user: AI features require connecting an LLM in Settings → Connect AI"
        escalate: 0

    - id: check-ollama-if-provider
      description: "If provider is Ollama, is Supervisor reachable?"
      type: conditional_http_check
      condition: "AMTL_SND_LLM_PROVIDER == 'ollama'"
      target: "http://localhost:9000/api/health"
      expect: "HTTP 200"
      if_pass: "next"
      if_fail:
        diagnosis: "Supervisor is down — Ollama routing unavailable"
        auto_fix:
          type: restart_dependency
          action: "Restart Supervisor via Workshop"
          verify: "GET http://localhost:9000/api/health returns 200"
        escalate: 2

    - id: check-api-key-valid
      description: "Is the API key valid? (for cloud providers)"
      type: conditional_api_check
      condition: "AMTL_SND_LLM_PROVIDER in ['anthropic', 'openai', 'deepseek', 'custom']"
      target: "Send minimal test request to provider"
      expect: "HTTP 200 or valid error (not 401/403)"
      if_pass: "resolved"
      if_fail:
        diagnosis: "API key is invalid or expired"
        auto_fix:
          type: none
          action: "Inform user: API key appears invalid. Please update in Settings → Connect AI"
        escalate: 0

# =============================================================
# TREE 3: S&D Data Integrity
# =============================================================
- id: snd-data-integrity
  name: "S&D Data Integrity Issue"
  symptom: "Sessions, insights, or vault entries are missing or corrupted"
  severity: high
  checks:
    - id: check-database-exists
      description: "Does the SQLite database file exist?"
      type: file_check
      target: "~/.socrates-and-donuts/vault.db"
      expect: "File exists and size > 0"
      if_pass: "next"
      if_fail:
        diagnosis: "Database file missing or empty"
        auto_fix:
          type: restore
          action: "If JSON export exists, import it. Otherwise, create fresh database"
          verify: "vault.db exists and is readable"
        escalate: 4

    - id: check-database-readable
      description: "Can SQLite open the database?"
      type: command_check
      target: "sqlite3 ~/.socrates-and-donuts/vault.db 'SELECT count(*) FROM sessions;'"
      expect: "Returns a number (0 or more)"
      if_pass: "next"
      if_fail:
        diagnosis: "Database is corrupted"
        auto_fix:
          type: rebuild
          action: "Backup corrupted file, create fresh database, import from last JSON export if available"
          verify: "sqlite3 query succeeds"
        escalate: 4

    - id: check-question-bank
      description: "Is the question bank loaded?"
      type: http_check
      target: "http://localhost:5010/api/question/today"
      expect: "HTTP 200 with question object"
      if_pass: "resolved"
      if_fail:
        diagnosis: "Question bank not loaded — questions.json may be missing or malformed"
        auto_fix:
          type: file_restore
          action: "Restore questions.json from Git repository"
          command: "git checkout HEAD -- app/data/questions.json"
          verify: "GET /api/question/today returns 200"
        escalate: 3

# =============================================================
# TREE 4: S&D Notification Failure
# =============================================================
- id: snd-notification-failure
  name: "S&D Notification Delivery Failure"
  symptom: "Daily question not delivered via push or SMS"
  severity: low
  checks:
    - id: check-push-enabled
      description: "Are push notifications enabled in settings?"
      type: config_check
      target: "push_enabled setting"
      expect: "true"
      if_pass: "next"
      if_fail:
        diagnosis: "Push notifications are disabled in S&D settings"
        auto_fix:
          type: none
          action: "Inform user: Push notifications are disabled. Enable in Settings → Notifications"
        escalate: 0

    - id: check-service-worker
      description: "Is the service worker registered?"
      type: browser_check
      target: "navigator.serviceWorker.getRegistration()"
      expect: "Registration object exists"
      if_pass: "next"
      if_fail:
        diagnosis: "Service worker not registered"
        auto_fix:
          type: reinstall
          action: "Hard refresh the page (Ctrl+Shift+R) to re-register service worker"
          verify: "Service worker registration exists"
        escalate: 0

    - id: check-sms-if-enabled
      description: "If SMS is enabled, is TextBee reachable?"
      type: conditional_http_check
      condition: "sms_enabled == true"
      target: "TextBee API health endpoint"
      expect: "HTTP 200"
      if_pass: "resolved"
      if_fail:
        diagnosis: "TextBee API is unreachable"
        auto_fix:
          type: none
          action: "TextBee is an external service — wait for it to recover. Push notifications still work independently"
        escalate: 0
```

---

## Escalation Levels

```
Level 0: Self-heal (S&D's own health check)                → 0 seconds
Level 1: Workshop auto-recovery (simple restart)            → 10 seconds
Level 2: Workshop deep restart (restart + dependencies)     → 30 seconds
Level 3: Workshop full recovery (kill + clear + start)      → 60 seconds
Level 4: ELAINE diagnosis (reads MRD trees)                 → 1–5 minutes
Level 5: Cline/Guruve (reads MRD, applies code fix)         → 5–30 minutes
Level 6: Mani notified (shows diagnosis + fix option)       → Human decides
```

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 19 February 2026 | Claude (Thalaiva) | Initial MRD — 4 diagnostic trees covering startup, LLM, data, notifications |

---

*Almost Magic Tech Lab*
*"YAML that machines can read, execute, and fix — automatically."*
