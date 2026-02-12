# THE LAST 20% — Making Apps Actually Work
## A Strategy for Sustained Operations, Not Just Successful Demos
### Almost Magic Tech Lab — February 2026

---

## The Problem (Stated Honestly)

We build apps to ~80% completion. They pass Beast tests. They pass Proof verification. They get pushed to GitHub. And then... they don't work reliably in daily use.

**Specific patterns:**
- CK Writer has multi-LLM comparison, plagiarism checking, AI detection — but we stopped using it and defaulted to Claude directly
- Learning Assistant fails because Ollama connections drop
- ELAINE's app-opening and email features work intermittently
- n8n is underutilised because it's been treated as "just a dashboard" instead of the powerful automation engine it actually is
- Port conflicts between apps cause silent failures
- No one is monitoring whether services are actually running day-to-day

**The root cause:** We optimise for *building* but not for *operating*. We celebrate the first successful run and move to the next project. Nobody's watching the factory floor.

**A deeper root cause:** We keep bypassing the tools we've built. ELAINE is an AI Chief of Staff with 16 modules — voice interaction, email management, calendar control, multi-step command chains, desktop app orchestration. But when her connections to downstream services are fragile, instead of fixing the plumbing, we route around her and go directly to the tools. That's like hiring a brilliant COO and walking past her desk because her phone line is crackly. The fix is the phone line, not the bypass. The same pattern applies to CK Writer — we stopped using it and went straight to Claude, abandoning the plagiarism checking, AI detection, and multi-LLM refinement we built.

---

## The Solution: Three Layers

### Layer 1: The Health Guardian (Automated Monitoring)
### Layer 2: The Completion Protocol (Finishing What's Built)
### Layer 3: The Operations Rhythm (Sustained Daily Use)

---

## LAYER 1: THE HEALTH GUARDIAN

### What It Is

A lightweight Python service (or n8n workflow) that runs continuously and monitors every app in The Workshop ecosystem. Not a new product — a utility. Like a building's fire alarm system.

### What It Does

**Every 5 minutes:**
1. Pings every registered port (from the Workshop SERVICES registry)
2. Checks if each service responds with HTTP 200 (or appropriate health endpoint)
3. Logs the result to a local SQLite database
4. If a service that was UP is now DOWN → sends a desktop notification (Windows toast)
5. If a service has been DOWN for 15+ minutes → sends an SMS via TextBee.dev
6. If Ollama is running but a specific model isn't loaded → flags it

**Daily at 8 AM:**
1. Generates a health report: which services ran, which crashed, uptime percentages
2. Writes it to a markdown file in a `health-reports/` folder
3. Optionally sends via ELAINE or email

**Weekly:**
1. Trend analysis: which apps crash most, which ports conflict, which dependencies fail
2. Flags any app that hasn't been accessed in 30+ days (zombie detection)

### Architecture

```
health-guardian/
├── guardian.py              → Main monitoring loop
├── config.yaml              → Service registry (pulled from Workshop)
├── notifier.py              → Windows toast + TextBee SMS
├── db/
│   └── health.db            → SQLite history
├── reports/
│   └── 2026-02-12.md        → Daily reports
├── tests/
│   └── test_guardian.py      → Beast tests
├── Dockerfile
├── docker-compose.yml
└── README.md
```

### The Service Registry (config.yaml)

```yaml
services:
  # CK Apps
  - name: ELAINE
    port: 5000
    health_endpoint: /
    critical: true
    restart_command: "cd C:\\...\\CK\\Elaine && python app.py"

  - name: The Workshop
    port: 5003
    health_endpoint: /api/health
    critical: true

  - name: CK Writer
    port: 5004
    health_endpoint: /
    critical: true

  - name: Junk Drawer Frontend
    port: 3005
    health_endpoint: /
    critical: false

  - name: Junk Drawer Backend
    port: 5005
    health_endpoint: /api/health
    critical: false

  - name: Genie Backend
    port: 8000
    health_endpoint: /api/health
    critical: true

  # Infrastructure
  - name: Ollama
    port: 11434
    health_endpoint: /api/tags
    critical: true
    check_models:
      - llama3.1:70b
      - gemma2:27b
      - nomic-embed-text

  - name: pgvector
    port: 5433
    type: tcp  # no HTTP, just TCP ping
    critical: true

  - name: Redis
    port: 6379
    type: tcp
    critical: false

  - name: n8n
    port: 5678
    health_endpoint: /healthz
    critical: true

  - name: SearXNG
    port: 8888
    health_endpoint: /
    critical: false

  - name: Listmonk
    port: 9000
    health_endpoint: /api/health
    critical: false

notifications:
  desktop: true
  sms:
    enabled: true
    textbee_api_key: ${TEXTBEE_API_KEY}
    phone: ${MANI_PHONE}
    only_critical: true  # Only SMS for critical services
```

### Why This Works

- Runs as a background service (or Docker container)
- Costs nothing (local, no cloud)
- Takes 30 minutes to build
- Catches failures BEFORE you discover them mid-session
- History lets us spot patterns (e.g., "Ollama crashes every time RTX goes to sleep mode")

### n8n Alternative

If you'd prefer, this ENTIRE thing can run as an n8n workflow:
- HTTP Request nodes ping each service
- IF nodes check for failures
- Function nodes log to SQLite
- Cron trigger every 5 minutes
- Email/SMS nodes for alerts
- Dashboard node for visual status

This is what I mean about underestimating n8n. It can literally do all of this with zero Python code.

---

## LAYER 2: THE COMPLETION PROTOCOL

### The Problem

Apps are "done" but not *done*. Beast tests pass, but the app doesn't work reliably for its intended purpose. We need a checklist that goes BEYOND testing.

### The Completion Checklist (For Every App)

Before any app is declared "complete," it must pass ALL of these:

#### Phase 1: Structure (Current — Beast + Proof)
- [ ] Beast tests pass (unit tests)
- [ ] Proof/Playwright verification pass (integration tests)
- [ ] GitHub push to Almost-Magic org
- [ ] README exists
- [ ] User Manual exists

#### Phase 2: Resilience (NEW — What's Been Missing)
- [ ] **Health endpoint** exists (`/api/health` returning JSON with status, version, uptime)
- [ ] **Graceful failure** — if Ollama is down, app shows friendly message, not crash
- [ ] **Dependency check on startup** — app checks its dependencies and reports what's missing
- [ ] **Port conflict detection** — app checks if its port is already in use before binding
- [ ] **Auto-retry logic** — for Ollama, API calls, and external services (3 retries, exponential backoff)
- [ ] **Error logging** — errors written to `logs/` folder with timestamp, not just console
- [ ] **Configuration validation** — .env checked on startup, missing vars flagged clearly

#### Phase 3: Real-World Use (NEW — The "Actually Use It" Test)
- [ ] **5-Day Use Test** — Mani uses the app for its intended purpose for 5 consecutive days
- [ ] **Edge case log** — Any failures during the 5-day test are logged and fixed
- [ ] **Restart resilience** — App works after machine reboot without manual intervention
- [ ] **Multi-app coexistence** — App works when other apps are also running (no port conflicts)
- [ ] **Ollama model availability** — If app needs Ollama, it specifies which model and checks it's loaded

#### Phase 4: Integration (NEW — Ecosystem Connectivity)
- [ ] **Registered in Workshop** — App appears in The Workshop with correct port and favicon
- [ ] **Health Guardian entry** — App added to Health Guardian's config.yaml
- [ ] **Startup script** — App can be started with a single command (documented in README)
- [ ] **Shutdown gracefully** — Ctrl+C doesn't leave zombie processes

### The "Definition of Done" (Revised)

An app is NOT done until it passes all four phases. Phase 1 (current Beast + Proof) is necessary but not sufficient.

---

## LAYER 3: THE OPERATIONS RHYTHM

### Daily (Automated)
- Health Guardian monitors all services every 5 minutes
- Desktop notifications for any failures
- SMS for critical failures (ELAINE, Genie, Ollama)

### Weekly (15 Minutes, Manual)
- Review Health Guardian weekly report
- Check: Which apps crashed? Why? Fix root causes.
- Check: Which apps haven't been used? Are they still needed?
- Update any config changes (new ports, new apps)

### Monthly (30 Minutes, Manual)
- Review all apps against Completion Checklist
- Update Workshop registry if anything changed
- Check Ollama models — any updates needed?
- Check Docker containers — any that need rebuilding?
- Check for dependency updates (pip/npm)

### Quarterly (1 Hour, Strategic)
- Which apps are earning their keep?
- Which should be deprecated?
- What's the next priority for the 20% completion work?
- Update the profile document for Guruve/Thalaiva

---

## THE BYPASS PATTERN (The Honest Diagnosis)

Before the specific fixes, let's name the pattern clearly — because it applies to more than just ELAINE.

### What We Keep Doing

| Tool We Built | What It Does | What We Do Instead | Why |
|--------------|-------------|-------------------|-----|
| **ELAINE** | Orchestrates everything — voice, email, calendar, app launching, multi-step chains | Go directly to Claude, ChatGPT, or Outlook | Her downstream connections are fragile |
| **CK Writer** | Multi-LLM comparison, plagiarism check, AI detection, style refinement, structured writing | Use Claude directly | Ollama connections drop, so the multi-LLM features fail |
| **Learning Assistant** | Just-in-time micro-skill training with local AI | Don't use it | Ollama keeps failing |
| **Costanza** | 150+ mental models, structured thinking frameworks | Think through problems manually or ask Claude | Haven't integrated into daily workflow |
| **n8n** | Powerful automation — HTTP requests, cron, webhooks, conditional logic, code nodes | Build custom Python scripts | Underestimated its capabilities |

### Why This Happens

1. **Fragile connections** — The apps work in isolation but fail when they need to talk to each other or to Ollama
2. **No retry logic** — One failure = total failure. No graceful degradation.
3. **No monitoring** — We don't know something is broken until we try to use it
4. **Path of least resistance** — When ELAINE can't open Claude, it's faster to open Claude yourself than to debug ELAINE. But every bypass makes ELAINE less central.
5. **Build-excitement bias** — Building the next thing is more exciting than fixing the last thing. This is a craving. (Vipassana practitioners will recognise it.)

### How to Break the Pattern

**Rule 1: Use your own tools first.** Before going to Claude directly, try ELAINE. Before writing in Claude, try CK Writer. Log every failure.

**Rule 2: Fix, don't bypass.** When a tool fails, the task becomes "fix this tool" not "work around it." Every bypass is technical debt.

**Rule 3: Failures are data.** Log them. The Health Guardian and the 5-Day Use Tests turn frustration into actionable fix lists.

**Rule 4: One tool at a time.** Don't try to fix everything at once. Pick the most impactful tool (ELAINE), stabilise it, use it for a week, then move to the next.

---

## SPECIFIC FIXES FOR CURRENT APPS

### CK Writer — What's Actually Wrong and How to Fix It

**The issue:** We stopped using CK Writer because multi-LLM comparison wasn't working reliably. But CK Writer has real capabilities: plagiarism check, AI detection, multi-LLM refinement, style consistency.

**The fix:**
1. Add health endpoint
2. Fix Ollama connection with retry logic (3 attempts, exponential backoff)
3. Add fallback: if local Ollama fails, offer to use API-based model
4. Add dependency check on startup: "Ollama running? ✅ Model loaded? ✅ API keys set? ✅"
5. Run the 5-Day Use Test specifically for case study writing
6. Document what CK Writer does that Claude Code doesn't (comparison, plagiarism, AI detection, style)

**Time estimate:** 2-3 hours to fix, 5 days to validate

### Learning Assistant — Why Ollama Keeps Failing

**The issue:** Ollama drops connections. Model loading takes too long. No retry logic.

**The fix:**
1. Pre-load required model on app startup (don't wait for first request)
2. Add connection pooling / keep-alive
3. Add retry with exponential backoff (500ms → 1s → 2s)
4. Add timeout handling (if model takes >30s, show "still thinking..." not error)
5. Add fallback: "Ollama is warming up, try again in 30 seconds" message
6. Health Guardian monitors Ollama specifically: model loaded? responsive?

### ELAINE — The Chief of Staff We Keep Walking Past

**The issue:** ELAINE is a 16-module AI Chief of Staff with voice interaction (ElevenLabs), Outlook email/calendar management, desktop app orchestration, multi-step chained commands with approval gates, and file operations. She is the ORCHESTRATOR — the single entry point that delegates to the right tool.

But we keep bypassing her. When her downstream connections are fragile (Ollama dropping, Outlook COM objects failing, app launches timing out), instead of fixing ELAINE's plumbing, Thalaiva kept saying "just use Claude directly" or "just open it yourself." This defeats the entire purpose of having a Chief of Staff.

**What ELAINE actually can do (and should be doing):**

| Capability | What It Means | Current State |
|-----------|--------------|---------------|
| Voice interaction | Talk to ELAINE, she executes | ElevenLabs voice_id configured, needs reliability testing |
| Desktop app launching | "Open Claude" / "Open Perplexity" | Works intermittently — path resolution issues |
| Outlook email | Read, compose, send, search emails | COM object fragility on Windows |
| Outlook calendar | Create, read, manage meetings | Same COM issue |
| Multi-step chains | "Research X, draft email, schedule follow-up" | Approval gates work, but downstream steps fail if services are down |
| File operations | Move, copy, organise files | Works but underutilised |
| Task orchestration | Coordinate across Workshop apps | The vision — not yet reliable |
| CK Writer delegation | "Write case study using CK Writer" | Should work but ELAINE→Writer connection untested |

**The fix (in priority order):**
1. **Dependency health check on ELAINE startup** — Before ELAINE says "ready," she pings every service she depends on and reports: "Ollama ✅, Outlook ✅, CK Writer ❌ (port 5004 not responding)"
2. **Explicit app path resolution** — Don't rely on system PATH. Store full executable paths for every app ELAINE launches (Claude.exe, ChatGPT.exe, etc.) in her config
3. **Process verification after launch** — After launching an app, ELAINE checks if the process is actually running (not just that the launch command succeeded)
4. **Retry logic with user feedback** — If first attempt fails: "Couldn't open Claude. Trying again..." (3 attempts, 2-second gaps)
5. **Outlook COM hardening** — Wrap every Outlook call in try/catch with specific COM error handling. If Outlook isn't open, ELAINE opens it first, waits for ready state, then proceeds
6. **Graceful degradation** — If a downstream service is down, ELAINE says "CK Writer isn't running. Want me to start it, or shall I help you directly?" instead of crashing
7. **Health Guardian integration** — ELAINE subscribes to Health Guardian alerts. If Ollama goes down, ELAINE knows before you ask her to do something that needs it
8. **The 5-Day ELAINE Test** — Use ELAINE as the PRIMARY interface for 5 consecutive days. Every task goes through her. Log every failure. Fix each one.

**The philosophical shift:** ELAINE should be the first thing you open in the morning. Not Claude. Not ChatGPT. ELAINE. She checks what's running, tells you what needs attention, and orchestrates your day. That's what a Chief of Staff does.

**Time estimate:** 4-6 hours for fixes 1-6, then 5 days for validation

### n8n — Powerful AND Underutilised

**The issue:** n8n is a genuinely powerful automation engine that we've been underusing. It's not just a dashboard — but it's also not the tool that was being dismissed. (That was ELAINE. See above.)

**What n8n can actually do that we should be leveraging:**

| Capability | How It Applies |
|-----------|---------------|
| HTTP Request nodes | Health monitoring for all services |
| Cron triggers | Scheduled checks every 5 minutes |
| Webhook triggers | Services can push status TO n8n |
| Error workflows | Automatic alerts when any workflow fails |
| Sub-workflows | Modular, reusable automation components |
| Code nodes | Custom JS/Python logic inline |
| SQLite nodes | Log health data without separate database |
| IF/Switch nodes | Conditional routing (critical vs non-critical) |
| Email nodes | Daily health reports via Listmonk |
| HTTP Response | Dashboard endpoints for Health Guardian |
| Ollama nodes | Direct integration with local LLMs |
| File nodes | Read/write/move files as part of workflows |

**Recommendation:** Build the Health Guardian AS an n8n workflow. It's faster, visual, already running on port 5678, and you can monitor the monitor through n8n's built-in execution log. No new code needed.

**The ELAINE + n8n relationship:** ELAINE is the front-end orchestrator (voice, human interaction, decision-making). n8n is the back-end automation engine (scheduled tasks, monitoring, data flows). They complement each other — ELAINE talks to humans, n8n runs the machinery. Neither is "just a dashboard."

---

## THE PRIORITY ORDER

The logic: fix the orchestrator first (ELAINE), then add monitoring (Health Guardian), then fix individual tools. If ELAINE works reliably, she can help you manage everything else.

### Week 1: ELAINE Stabilisation
- Fix dependency health check on startup
- Fix app path resolution (store full paths in config)
- Add retry logic with user feedback
- Harden Outlook COM handling
- Add graceful degradation ("CK Writer isn't running. Want me to start it?")
- Begin 5-Day ELAINE Test — every task goes through her

### Week 2: Health Guardian (via n8n)
- Build n8n workflow that pings all services every 5 minutes
- Add desktop notifications for failures
- Add SMS via TextBee for critical failures
- Register all current services
- Start collecting baseline data
- Connect Health Guardian alerts to ELAINE — she knows what's up and what's down

### Week 3: CK Writer Revival
- Fix Ollama connectivity with retry logic
- Add health endpoint + dependency check
- Test ELAINE → CK Writer delegation ("Write a case study using CK Writer")
- Run 5-Day Use Test specifically for writing tasks
- Document CK Writer's unique capabilities vs raw Claude

### Week 4: Learning Assistant + Completion Audit
- Fix Ollama retry logic in Learning Assistant
- Pre-load required models on startup
- Run every app through the full Completion Checklist
- Fix gaps identified
- Update Workshop registry
- Update Health Guardian config

### Ongoing: Operations Rhythm
- Weekly 15-minute health review
- Monthly 30-minute audit
- Quarterly strategic review

---

## THE AUTO-START PROBLEM (The Daily Frustration)

### What Should Happen Every Morning

You turn on your machine. You open a browser. Everything is already running. ELAINE greets you. The Workshop shows all green dots. You start working.

### What Actually Happens

You turn on your machine. Nothing is running. You open The Workshop — it's not running either. You open a terminal. You `cd` into a deeply nested Dropbox folder. You run `python app.py`. Something crashes because Ollama isn't running yet. You start Ollama. You start Docker. You wait. You start The Workshop again. Now it shows red dots everywhere because nothing else is running. You start ELAINE. Then Genie. Then whatever else you need. 20 minutes gone. Frustrated before you've done anything.

**This is unacceptable for a one-person AI-native firm.** The infrastructure should serve you, not the other way around.

### The Fix: AMTL Startup Engine

A single Windows service (or startup script) that boots everything in the correct order with dependency awareness.

**Startup sequence (order matters):**

```
PHASE 1: Infrastructure (must be first)
  1. Docker Desktop           → Wait until Docker daemon is ready
  2. Docker containers        → pgvector, Redis, SearXNG, n8n, Listmonk
  3. Ollama                   → Start service, wait for /api/tags to respond
  4. Ollama model preload     → Pull required models into memory

PHASE 2: Core Services
  5. The Workshop (5003)      → Central launcher
  6. ELAINE (5000)            → Chief of Staff
  7. Genie (8000)             → Bookkeeper

PHASE 3: On-Demand Services (started by ELAINE when needed)
  8. CK Writer (5004)         → Started when writing tasks requested
  9. Costanza (5001)          → Started when thinking frameworks needed
  10. Learning Assistant (5002) → Started when learning requested
  11. Junk Drawer (3005/5005)  → Started when file management needed
  12. Peterman (5008)          → Started when brand intelligence needed
  13. ComfyUI (8188)           → Started when image generation needed
  14. Author Studio (5007)     → Started when book work requested
```

**Implementation options:**

**Option A: Windows Task Scheduler + PowerShell Script**
```powershell
# amtl-startup.ps1 — runs on Windows login
# Phase 1: Infrastructure
Start-Process "Docker Desktop" -ErrorAction SilentlyContinue
do { Start-Sleep 5 } until (docker info 2>$null)
docker-compose -f "$AMTL_BASE\docker-compose.yml" up -d
Start-Process ollama serve
do { Start-Sleep 3 } until ((Invoke-WebRequest http://localhost:11434/api/tags -UseBasicParsing -ErrorAction SilentlyContinue).StatusCode -eq 200)

# Phase 2: Core Services
Start-Process python -ArgumentList "$CK_BASE\workshop\app.py" -WindowStyle Minimized
Start-Process python -ArgumentList "$CK_BASE\Elaine\app.py" -WindowStyle Minimized
Start-Process python -ArgumentList "$FINANCE_BASE\Genie\backend\main.py" -WindowStyle Minimized

# Phase 3: Health check
Start-Sleep 10
# Ping all services, report status
```

**Option B: Docker Compose for EVERYTHING**

Move all Python apps into Docker containers. One `docker-compose.yml` to rule them all. `docker compose up -d` starts everything with correct dependency ordering, restart policies, and health checks built in.

```yaml
# docker-compose.yml (simplified)
services:
  postgres:
    image: pgvector/pgvector
    ports: ["5433:5432"]
    restart: always
    healthcheck:
      test: pg_isready
      interval: 10s

  redis:
    image: redis:alpine
    ports: ["6379:6379"]
    restart: always

  ollama:
    image: ollama/ollama
    ports: ["11434:11434"]
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]
    restart: always
    healthcheck:
      test: curl -f http://localhost:11434/api/tags
      interval: 30s

  workshop:
    build: ./CK/workshop
    ports: ["5003:5003"]
    depends_on:
      ollama:
        condition: service_healthy
    restart: always

  elaine:
    build: ./CK/Elaine
    ports: ["5000:5000"]
    depends_on:
      - workshop
      - ollama
    restart: always

  genie:
    build: ./Finance-App/Genie/backend
    ports: ["8000:8000"]
    depends_on:
      - postgres
    restart: always

  n8n:
    image: n8nio/n8n
    ports: ["5678:5678"]
    restart: always

  # ... etc for all services
```

**Option B is the better long-term solution** because:
- `restart: always` means services auto-recover from crashes
- `depends_on` with health checks means correct startup order
- `docker compose up -d` is ONE command to start everything
- `docker compose ps` shows status of everything
- Health Guardian becomes trivial — just check Docker health status
- Works the same on any machine (portable)

**Option A is faster to implement** (30 minutes vs half a day for Dockerising all apps).

**Recommendation:** Start with Option A this week (immediate relief), plan Option B as a proper infrastructure project.

### The Workshop Auto-Start Specifically

The Workshop was supposed to start on boot. It doesn't because:
1. No Windows Task Scheduler entry was created
2. Even if it was, it would fail because Docker/Ollama aren't ready yet
3. No dependency chain — it just tries to start and crashes silently

**Quick fix (10 minutes):**
1. Create `amtl-startup.bat` that starts Docker → waits → starts Ollama → waits → starts Workshop
2. Add to Windows Task Scheduler: trigger on user login, run `amtl-startup.bat`
3. Workshop then shows accurate status dots because infrastructure is already running

---

## THE TOOLS ECOSYSTEM PROBLEM

### ComfyUI, Ollama Models, and the Learning Chain

The Learning Assistant, CK Writer, and other apps depend on a chain of tools that must ALL be working:

```
User Request
    → ELAINE (orchestrator)
        → CK Writer or Learning Assistant (app)
            → Ollama (local LLM inference)
                → Specific model (llama3.1:70b, gemma2:27b, etc.)
                    → GPU (RTX 5070 — must have VRAM available)

User wants image generation
    → ELAINE
        → ComfyUI (port 8188)
            → Stable Diffusion model
                → GPU (same RTX 5070 — VRAM conflict with Ollama?)
```

**The chain breaks if ANY link fails.** And right now, nobody's checking the chain — just the individual links.

### Specific Tool Issues

**Ollama:**
- Models unload from memory after idle timeout → first request after idle is slow or fails
- Running a 70b model + ComfyUI simultaneously may exceed 12GB VRAM
- No automatic model preloading after restart
- No health check that verifies a specific model is loaded (not just that Ollama is running)

**Fix:**
- Set `OLLAMA_KEEP_ALIVE=-1` (never unload models) or a longer timeout
- Create model priority list: which models are always loaded vs on-demand
- Add VRAM monitoring to Health Guardian: if VRAM > 90%, warn before launching another model
- Startup script preloads the primary model: `ollama run llama3.1:70b ""` (empty prompt to load)

**ComfyUI:**
- Needs to be running for image generation tasks
- Competes with Ollama for GPU VRAM
- No health endpoint that we're monitoring
- Workflows need to be pre-configured

**Fix:**
- Add ComfyUI to Health Guardian monitoring (ping port 8188)
- Make ComfyUI an on-demand service: ELAINE starts it when needed, shuts it down when done (freeing VRAM for Ollama)
- Document VRAM budget: "If Ollama has 70b loaded, ComfyUI can't run simultaneously. Either use a smaller model or stop Ollama temporarily."

**SearXNG (port 8888):**
- Used for web search in various apps
- Docker container — should auto-restart
- Verify it's in docker-compose with `restart: always`

**pgvector (port 5433):**
- Vector database for embeddings
- Critical for semantic search in Junk Drawer, potentially others
- Docker container — verify `restart: always`

**Redis (port 6379):**
- Cache and queue
- Docker container — verify `restart: always`

### The VRAM Budget (RTX 5070 — 12GB)

This is a real constraint that nobody's managing:

| Model/Tool | Approx VRAM | Notes |
|-----------|-------------|-------|
| llama3.1:70b (Q4) | ~8-10 GB | Primary reasoning model |
| gemma2:27b | ~5-6 GB | Alternative model |
| nomic-embed-text | ~0.5 GB | Embeddings (lightweight) |
| ComfyUI + SD model | ~4-8 GB | Depends on model loaded |

**You cannot run llama3.1:70b AND ComfyUI simultaneously.** This needs to be managed explicitly.

**VRAM management strategy:**
1. Default state: Ollama with nomic-embed-text loaded (lightweight, always available for embeddings)
2. When reasoning needed: load gemma2:27b (fits alongside embeddings)
3. When heavy reasoning needed: load llama3.1:70b (uses most VRAM, unload when done)
4. When image generation needed: unload large Ollama model, start ComfyUI
5. Health Guardian tracks VRAM usage and warns before conflicts

---

## INFRASTRUCTURE RELIABILITY CHECKLIST

Before we fix any apps, ALL infrastructure should pass this:

### Docker Containers
- [ ] All containers have `restart: always` in docker-compose.yml
- [ ] `docker compose ps` shows all containers as "running"
- [ ] Health checks configured for each container
- [ ] Containers start automatically when Docker Desktop starts
- [ ] Docker Desktop starts on Windows login

### Ollama
- [ ] Starts automatically (Windows service or startup script)
- [ ] Primary model preloaded after start
- [ ] `OLLAMA_KEEP_ALIVE` configured appropriately
- [ ] Health endpoint responds: `http://localhost:11434/api/tags`
- [ ] VRAM usage monitored

### The Workshop
- [ ] Starts automatically on boot (via startup script)
- [ ] Shows accurate status dots for all services
- [ ] Can launch any registered app
- [ ] Health endpoint: `http://localhost:5003/api/health`

### Network
- [ ] No port conflicts (run port scan on startup)
- [ ] All services accessible on localhost
- [ ] Firewall not blocking local ports

---

## THE DESIGN PRINCIPLE

> **"We don't need more apps. We need the apps we have to actually work."**

> **"ELAINE is not a dashboard. She's the Chief of Staff. Start every morning with her."**

This isn't about building something new. It's about finishing what we've started. The Health Guardian is the only new component — and it exists to protect everything else.

The real shift is philosophical: from "build and move on" to "build, stabilise, operate, and maintain." From bypassing our tools to trusting them. From treating ELAINE as a launcher to treating her as the orchestrator she was designed to be.

From a Vipassana perspective: we've been craving the next build. Time for equanimity with what exists. The apps are already built. Now we sit with them, observe what's failing, and fix it with patience — not excitement.

---

*Document created for Mani Padisetti, February 2026*
*Almost Magic Tech Lab*
*"The last 20% is where the magic becomes real."*
