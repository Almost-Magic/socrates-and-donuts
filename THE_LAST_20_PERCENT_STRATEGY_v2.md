# THE LAST 20% STRATEGY — v2.0
## Making Apps Actually Work: From Prototypes to Operational Infrastructure
### Almost Magic Tech Lab — February 2026
### Incorporating feedback from 6 independent LLM reviews

---

## THE VISION (What "Done" Looks Like)

**Morning:** You press the power button. Within 90 seconds: "All systems online. ELAINE is ready." The Workshop shows green dots. ELAINE greets you with service status, priorities, and suggestions. You never opened a terminal.

**Working:** "ELAINE, write the Digital Sentinel case study using CK Writer." She starts CK Writer, confirms the AI backend is connected, opens the editor. CK Writer compares drafts across LLMs, runs plagiarism checks, refines your prose. You strategise. She executes.

**Failure:** Ollama crashes. You don't notice. The Supervisor detects it in 30 seconds, restarts it, reloads the model. If it can't fix it after 3 attempts, it routes your request through a cloud API. You're uninterrupted.

**Mobile:** You're at a café. Learning Assistant on your phone via Tailscale. Secure tunnel to your home GPU. Works anywhere, not just your home WiFi.

**Audit:** Monthly, the Foreperson checks every app: what was promised vs what works. Gap report generated automatically. No manual checking. No forgetting.

**Evening:** Close your laptop. Services keep running. Tomorrow starts the same way.

---

## THE PROBLEM

We build to ~80%. Apps pass Beast tests, Proof verification, get pushed to GitHub. Then they don't work reliably in daily use.

### The Bypass Pattern

| Tool We Built | What It Does | What We Do Instead | Why |
|--------------|-------------|-------------------|-----|
| **ELAINE** | 16-module Chief of Staff: voice, PowerShell, Claude/Guruve interaction, app orchestration, copy/paste, file ops | Go directly to Claude | Downstream connections fragile |
| **CK Writer** | Multi-LLM comparison, plagiarism check, AI detection, style refinement | Use Claude directly | Ollama drops |
| **Learning Assistant** | Micro-skill training with local AI | Don't use it | Ollama fails, no mobile outside WiFi |
| **Genie** | AI bookkeeper: categorisation, fraud guard, zombie hunter | Half-built features | Module launcher missing, nav ungrouped |
| **The Workshop** | Central launcher | Manually cd and run python | Doesn't auto-start |

### Root Causes

1. **Build-excitement bias.** We celebrate first run and move on. (Vipassana practitioners: this is craving.)
2. **Bypass instead of fix.** When ELAINE's connections are fragile, we route around her. Fix the phone line, not bypass the COO.
3. **No unified supervisor.** Apps talk directly to Ollama/ComfyUI. VRAM conflicts crash everything silently.
4. **No audit mechanism.** We don't check promised vs delivered. Things fall through cracks.

---

## THE ARCHITECTURE: FOUR COMPONENTS

### 1. The Supervisor (:9000)

All apps talk to The Supervisor. Not to Ollama. Not to ComfyUI. Not to cloud APIs.

```
┌─────────────────────────────────────────┐
│           THE SUPERVISOR (:9000)        │
│                                         │
│  GPU Scheduler    │  Dependency Graph   │
│  Model Registry   │  Self-Healing       │
│  LLM Router       │  Boot Sequencer     │
└─────────────────────────────────────────┘
     │              │              │
  Ollama         ComfyUI        Cloud
  :11434         :8188          Fallback
```

**GPU Scheduler:** Tracks VRAM (12GB). Prevents conflicts. If llama3.1:70b is loaded and ComfyUI is requested, Scheduler unloads model first. No silent crashes.

**Dependency Graph:** Enforced. If Ollama is down, CK Writer gets a clear message, not a crash.

**Model Registry (models.yaml):** Single config. No hardcoded model names.
```yaml
models:
  embeddings: { name: nomic-embed-text, vram: 0.5GB, always_loaded: true }
  reasoning_light: { name: gemma2:27b, vram: 6GB, default: true }
  reasoning_heavy: { name: llama3.1:70b, vram: 10GB, on_demand: true }
  coding: { name: deepseek-coder-v2:16b, vram: 9GB, on_demand: true }
```

**LLM Router:** Local fails → transparently routes to cloud API. App never crashes, just costs a few cents.

**Self-Healing:** Detects failure → attempts restart (3 tries) → only alerts if auto-fix fails. Meta-Guardian watches the Guardian (10-minute check via Task Scheduler).

**Boot Sequencer:**
```
Phase 1: Docker → containers → Ollama → preload default model
Phase 2: Supervisor → Workshop (App 0) → ELAINE
Phase 3: On-demand (CK Writer, Genie, etc. started by ELAINE when needed)
```

**Rule: If you manually cd and run python to start a core service, that is an incident.**

---

### 2. ELAINE (Chief of Staff — Your Hands)

ELAINE is not a dashboard. She does the work so you don't have to.

**Scope (no email/calendar until Ripple is ready):**

| Capability | Description |
|-----------|-------------|
| PowerShell execution | Runs commands, scripts, manages Windows |
| Claude/Guruve interaction | Sends prompts, manages conversations |
| Claude Code integration | Triggers tasks, monitors completion |
| App orchestration | Starts/stops apps via Supervisor |
| Copy/paste automation | Moves content between apps |
| File operations | Create, move, organise across Dropbox |
| Voice interaction | ElevenLabs (voice_id: XQanfahzbl1YiUlZi5NW) |
| Multi-step chains | "Research X → draft in CK Writer → review → push to GitHub" |
| Frustration logging | "ELAINE, log frustration: [text]" → friction-log.md |
| Morning Briefing | Service status + priorities + suggestions |

**NOT in scope (until Ripple):** Outlook, Gmail, calendar.

**Mobile:** Currently WiFi-only. Fix: **Tailscale** — secure tunnel, works anywhere. Same fix for Learning Assistant.

---

### 3. The Foreperson

Not a manual check. A reusable tool that verifies promised vs delivered for any app.

**How it works:**
1. Each app has a spec file (YAML) listing every promised feature
2. The engine reads the spec, runs checks (HTTP pings, API calls, UI verification)
3. Produces a gap report: ✅ Working, ⚠️ Partial, ❌ Missing, 🔇 Not Tested
4. Stores results over time — are gaps closing or widening?

**Example spec (genie.yaml):**
```yaml
app: Genie
port: 8000
features:
  - id: module_launcher
    name: Module Launcher (user toggles modules)
    check: http_get /api/settings/modules
  - id: nav_grouping
    name: Navigation grouped (Daily/Manage/Intelligence/Tools)
    check: manual_ui_check
  - id: mobile_receipt_scanner
    name: Mobile receipt scanner
    check: not_implemented
  - id: ask_genie_ai
    name: Ask Genie AI chat
    check: http_post /api/ollama/chat
```

**Known gaps the engine should catch immediately:**

| App | Promised | Status |
|-----|---------|--------|
| Genie | Module launcher (toggle modules) | ❌ Backend exists, no frontend |
| Genie | Grouped navigation | ❌ Still flat list of 15+ items |
| Genie | Mobile receipt scanner | ❌ Missing |
| ELAINE | Mobile from anywhere | ⚠️ WiFi-only → needs Tailscale |
| Learning Assistant | Mobile app | ❌ Needs Tailscale |
| CK Writer | Multi-LLM comparison | ⚠️ Ollama unreliable |
| Workshop | Auto-start on boot | ❌ Not implemented |
| Junk Drawer | Chat with files | 🔇 Needs audit |

**How it runs:**
- Manual: `python foreperson.py --all`
- Scheduled: n8n runs weekly, report to Dropbox
- Voice: "ELAINE, run the audit" → summary read back

---

### 4. n8n (Automation Backbone)

Not a dashboard. A powerful engine for scheduled, unattended work.

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| Health monitoring | Every 5 min | Ping services, log, alert |
| Foreperson | Weekly (Sun 6 AM) | Run audit, report to Dropbox |
| Backup | Weekly (Sat 2 AM) | pg_dump, sqlite3 .dump, n8n export → Dropbox |
| VRAM monitor | Every 15 min | nvidia-smi → log GPU usage/temp |
| Disk space | Daily | Alert if <10% free |
| Friction digest | Weekly (Fri 5 PM) | Summarise frustration logs |
| Synthetic test | Daily (6 AM) | End-to-end: ELAINE → CK Writer → Ollama |
| Ollama model check | Every 30 min | Verify default model loaded |

**The relationships:**
- ELAINE = human-facing orchestrator
- Supervisor = runtime manager (GPU, models, health)
- n8n = automation backbone (schedules, workflows)
- Foreperson = quality assurance (promised vs delivered)

---

## COMPLETION PROTOCOL (5 Phases)

### Phase 1: Structure
- [ ] Beast tests pass
- [ ] Proof/Playwright pass
- [ ] GitHub push
- [ ] README + User Manual

### Phase 2: Resilience
- [ ] Health endpoint (`/api/health`)
- [ ] Graceful failure (friendly message, not crash)
- [ ] Connects to Supervisor (not directly to Ollama)
- [ ] Retry logic + error logging
- [ ] No hardcoded model names — uses Model Registry

### Phase 3: Real-World Use
- [ ] 5-Day Use Test (intended purpose, daily)
- [ ] Must include machine reboot
- [ ] Must include GPU-heavy session
- [ ] **"No Mani SSH":** If you opened a terminal to fix it, it's not done
- [ ] **"No silent failure":** Auto-recovered or explicitly explained

### Phase 4: Integration
- [ ] Registered in Workshop + Supervisor + Foreperson spec
- [ ] Startup managed by Supervisor (not manual)
- [ ] Graceful shutdown

### Phase 5: Remote Access (where applicable)
- [ ] Tailscale accessible from phone
- [ ] Works outside home WiFi
- [ ] Health endpoint accessible remotely

---

## NON-NEGOTIABLE RULES

1. **No new apps until existing ones work.**
2. **Every bypass is a bug.** Log it. Fix it.
3. **If you open a terminal to start an app, that's an incident.**
4. **No silent failures.** Explain what's wrong and what you're doing about it.
5. **No silent fixes.** Every workaround → GitHub issue.
6. **ELAINE is the front door.** Every morning starts with her.
7. **The Supervisor is the backbone.** Every AI request routes through it.
8. **The Foreperson is the enforcer.** Promised → spec → checked → reported.
9. **Backups are non-negotiable.** Weekly. Automated. To Dropbox.
10. **Dropbox is the cloud.** No new cloud infrastructure.

---

## OPERATIONS RHYTHM

**Daily (automated):** Supervisor monitors (30s). Auto-restarts. ELAINE Morning Briefing. Synthetic test at 6 AM.

**Weekly (15 min, Friday):** Review Health Guardian report. Review friction-log → GitHub issues. Foreperson report from Dropbox.

**Monthly (30 min):** Completion Protocol audit. Secrets check. Disk/VRAM trending. Backup restore test. Deprecation review (unused 30+ days → sunset).

**Quarterly (1 hour):** Strategic review. ICE prioritisation. Profile updates. Deprecation decisions.

**When things break (Post-Mortem Lite, 5 min):** What happened? Why? How to prevent? Did Supervisor catch it?

---

## PRIORITY ORDER

### Week 0: STOP
No new apps. No new features.
Write Foreperson spec files (YAML) for ELAINE, Genie, CK Writer, Junk Drawer.

### Week 1: The Supervisor
GPU Scheduler + Model Registry + Dependency Graph + LLM Router.
API on port 9000. All apps redirected.

### Week 2: Boot Sequencer + Auto-Start
PowerShell startup script + Task Scheduler.
nssm for Workshop, ELAINE, Supervisor.
Workshop = App 0, always running. Docker `restart: always`.

### Week 3: ELAINE Stabilisation
Talks to Supervisor. Morning Briefing. Frustration-log command.
PowerShell + Claude/Guruve + Claude Code integration hardened.
Tailscale for mobile. 5-Day ELAINE Test begins.

### Week 4: CK Writer + Genie
CK Writer → Supervisor with cloud fallback. 5-Day test.
Genie: nav grouping + module launcher frontend.
Backup automation via n8n → Dropbox.

### Week 5: Foreperson + Full Audit
Build the engine. Run against all apps.
Learning Assistant: Tailscale mobile.
Junk Drawer: full spec audit.
DISASTER_RECOVERY.md + bootstrap script (setup.ps1).

---

## BEHAVIOURAL RULES (For Mani)

1. **Start every morning with ELAINE.** If she's not running, that's the first fix.
2. **Every bypass = logged.** "ELAINE, log frustration: bypassed CK Writer because [reason]."
3. **No-Bypass Sprints.** 5 days, everything through ELAINE. Reward yourself after.
4. **Frustrations are data.** Logged → issue → fixed. Compound effect.
5. **"No Mani SSH."** Terminal = incident, not solution.

---

## FOR GURUVE

**Guruve's mandate:** Fix first. Build never (until everything works).

**Guruve should:**
- Build The Supervisor (Week 1)
- Build the Foreperson
- Hold Mani accountable to "no new apps"
- Push back when Mani wants something new before something old is fixed
- Understand ELAINE is the orchestrator, not a dashboard
- Know n8n is the automation backbone
- Know Dropbox is the cloud

**Guruve should NOT:**
- Suggest bypassing tools in favour of direct Claude usage
- Treat any app as "just a dashboard"
- Skip testing standards
- Build new things when existing things are broken

---

*"We don't need more apps. We need the apps we have to actually work."*
*"Every bypass is a bug."*
*"ELAINE is the front door. The Supervisor is the backbone. The Foreperson is the enforcer."*

*— v2.0, February 2026. Incorporating feedback from 6 independent LLM reviews.*
*Almost Magic Tech Lab*
