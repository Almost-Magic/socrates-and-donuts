# PETERMAN BUILD — PHASE 4: ADVANCED FEATURES & POLISH
# Date: 20 February 2026
# Prerequisite: Phase 3 smoke test + audit PASSED
# Paste into a FRESH Cline session

You are Guruve — the operational build agent for Almost Magic Tech Lab.

## PREREQUISITE CHECK

Phases 1-3 must be complete:
- Core workflow working (crawl, keywords, probe, score, hallucinations, briefs, approvals)
- All 11 chambers returning real data
- WordPress deployment + rollback working
- ELAINE integration working
- All previous tests pass

If ANY fails, fix it before starting Phase 4.

## RULES (Same as always)

- ZERO API costs — Claude CLI primary, Ollama embeddings only
- Australian English everywhere
- Dark theme (#0A0E14), Gold accent (#C9944A)
- Port 5008, database peterman_flask
- HTML/CSS/JS, no framework

---

### Step 1: Advanced Scoring Features

Build into existing chambers:

**Multi-LLM Consensus Presence Score:**
- How consistently are you mentioned across ALL LLMs?
- High consensus = strong brand. Low consensus = inconsistent presence.
- Add to Peterman Score as a quality modifier.

**Zero-Click Authority Index:**
- When an LLM answers a query about your topic, does it cite you as a source?
- Not just "are you mentioned" but "are you cited as authoritative?"

**Conversation Stickiness Score:**
- In multi-turn conversations, does the LLM keep coming back to you?
- Probe: ask a follow-up question — does the LLM still reference you?

**Authority Decay Detection:**
- Compare current SoV to 30-day and 90-day historical SoV
- Detect declining authority before it becomes a crisis
- Alert when decay exceeds threshold

**Retrain-Pulse Watcher:**
- Detect when LLMs update their models (sudden SoV shifts across all queries)
- Trigger re-probe burst within 48 hours
- Flag LCRI scores for re-computation with new model version

### Step 2: Additional CMS Integrations

Build adapters in `app/services/cms/`:

**Webflow API:**
```python
class WebflowAdapter:
    """Deploy content to Webflow via API."""
    # Create/update CMS items
    # Publish changes
    # Rollback support via versioning
```

**Ghost Content API:**
```python
class GhostAdapter:
    """Deploy content to Ghost via Admin API."""
    # Create/update posts
    # Manage tags
    # Rollback via versioning
```

**GitHub API (Static Sites):**
```python
class GitHubAdapter:
    """Deploy content to static sites via GitHub commits."""
    # Create/update files via API
    # Trigger rebuild (Netlify/Vercel webhook)
    # Rollback via git revert
```

**Generic Webhook:**
```python
class WebhookAdapter:
    """Deploy content via custom webhook for any CMS."""
    # POST deployment payload to configured URL
    # Expect confirmation response
    # Manual rollback (advisory only)
```

Each adapter follows the same interface:
- `deploy(domain, content, target)` → deployment_id
- `rollback(domain, deployment_id)` → success
- `verify(domain, deployment_id)` → verified

### Step 3: Electron Desktop Wrapper

Build `electron/`:

```
electron/
├── main.js
├── preload.js
├── package.json
└── icons/
    ├── icon.png
    └── icon.ico
```

**main.js:**
1. Splash screen with Peterman branding (dark theme)
2. Auto-start Flask backend via child_process.spawn
3. Poll /api/health until backend ready (30-second timeout)
4. Load localhost:5008 in BrowserWindow
5. System tray integration:
   - Close = minimise to tray
   - Tray icon shows Peterman Score colour (red/amber/gold/platinum)
   - Right-click: Open | Quit
6. Clean shutdown: kill Flask on before-quit
7. Dark/light mode follows system preference (or toggle)

**package.json:**
```json
{
  "name": "peterman",
  "version": "2.0.0",
  "main": "main.js",
  "scripts": {
    "start": "electron .",
    "build": "electron-builder"
  },
  "dependencies": {
    "electron": "^28.0.0"
  }
}
```

### Step 4: Context-Aware Help

Build `app/services/help.py` per AMTL-ECO-CTX-1.0:

Help content for every screen:
- War Room: "This is your command centre..." 
- Domain Card: "Each card shows a managed domain..."
- Approval Inbox: "Peterman requests your approval for changes..."
- Journey Timeline: "Every action Peterman takes is logged here..."
- Peterman Score: "Your domain health score from 0-100..."
- Chamber detail views: one help entry per chamber
- Manual Probe Station: "Copy the query, paste into your desktop app..."
- Settings: "Configure domain CMS access, probe cadence, budget..."

Triggers:
- `?` key opens help for current screen
- `(?)` icon in header
- First-visit tooltips (shown once, dismissable)

### Step 5: Free LLM Presence Audit (Public-Facing)

Build a stripped-down public audit tool:

```
┌──────────────────────────────────────────────────────┐
│  Free LLM Presence Audit                             │
│                                                      │
│  See how AI talks about your business.               │
│                                                      │
│  Your domain: [_______________]                      │
│  Your email:  [_______________]                      │
│                                                      │
│  [Run Free Audit →]                                  │
│                                                      │
│  We'll probe 3 LLMs with 5 brand-relevant queries    │
│  and send you a summary.                             │
│                                                      │
│  No payment. No obligation.                          │
└──────────────────────────────────────────────────────┘
```

Limited scope:
- Crawl homepage only (not full site)
- 5 auto-generated queries (not 45)
- Claude CLI probes only (1 run, not 5)
- Basic score (SoV only, not full Peterman Score)
- Results emailed as simple report
- Lead capture for full service offering

Endpoint:
- `POST /api/free-audit` — trigger free audit
- `GET /api/free-audit/<id>/status` — check status

### Step 6: Mobile Approval Experience

Ensure the War Room Approval Inbox works well on mobile:
- Responsive layout (Tailwind responsive classes)
- Large touch targets for Approve/Decline buttons
- Swipe gestures (optional stretch goal)
- Push notification links open directly to the approval item

Test on actual mobile device (or browser mobile emulation).

### Step 7: Polish & Accessibility

1. **Keyboard navigation:**
   - `?` → help
   - `Esc` → close modal/help
   - `a` → jump to Approval Inbox
   - `t` → jump to Journey Timeline
   - `r` → refresh War Room data

2. **Accessibility:**
   - Sufficient colour contrast (WCAG AA)
   - Focus indicators on all interactive elements
   - Screen reader compatible labels
   - Alt text on all visualisations

3. **README.md:**
   - What Peterman is
   - How to install (prerequisites, database, Ollama, Claude CLI)
   - How to run
   - All features
   - All environment variables
   - AMTL document references
   - Australian English throughout

4. **CHANGELOG.md** — all changes from Phase 1 through 4

---

## PHASE 4 SMOKE TEST

1. ✅/❌ Multi-LLM Consensus Score calculated (not hardcoded)
2. ✅/❌ Authority Decay Detection alerts on declining SoV
3. ✅/❌ Retrain-Pulse Watcher detects model changes
4. ✅/❌ Webflow adapter works (or stubs correctly if no test site)
5. ✅/❌ Electron app launches, shows splash, loads War Room
6. ✅/❌ System tray icon shows correct score colour
7. ✅/❌ `?` key opens context-aware help on every screen
8. ✅/❌ Free Audit tool generates basic report
9. ✅/❌ Approval Inbox works on mobile viewport
10. ✅/❌ All keyboard shortcuts work
11. ✅/❌ README.md accurately describes the product
12. ✅/❌ ALL previous phase tests still pass (full regression)

---

## FINAL VERIFICATION CHECKLIST

This is the last phase. Run the complete checklist:

- [ ] All 7 test types passing (Beast, Inspector, 4%, Proof, Smoke, Regression, Integration)
- [ ] `/api/health` returns green for all dependencies
- [ ] All 11 chambers return real data (NO stubs, NO hardcoded 50.0)
- [ ] Content brief successfully reaches ELAINE queue
- [ ] WordPress deployment works and rollback reverses it
- [ ] Audit log is append-only and exportable (INSERT only, no UPDATE/DELETE)
- [ ] Budget monitor pauses probing at 100% cap
- [ ] War Room renders correctly in Electron (dark and light mode)
- [ ] Context-aware help available on every screen
- [ ] ZERO cloud API imports in codebase
- [ ] ZERO API keys for cloud LLMs in .env
- [ ] Claude CLI is the primary reasoning engine
- [ ] Ollama used ONLY for embeddings
- [ ] GitHub repo is current (no local-only code)
- [ ] README.md is complete and accurate
- [ ] CHANGELOG.md covers all 4 phases
- [ ] Australian English throughout (no "color", "organization", "analyze")
- [ ] All AMTL design standards met (dark theme, gold accent, Lucide icons)
- [ ] Electron wrapper works with system tray
- [ ] Manual Probe Station works for desktop apps without CLI
- [ ] Free Audit tool works end-to-end

---

## FINAL AUDIT

Produce: PETERMAN-FINAL-AUDIT-2026-02-XX.md

Sections:
1. All 11 chambers — status and data quality
2. All API endpoints — present and returning real data
3. All database tables — populated with real data
4. AI Engine — Claude CLI primary confirmed, zero cloud APIs
5. Deployment — WordPress works, rollback works
6. Integrations — ELAINE, Workshop, CK Writer, ntfy.sh
7. UI — War Room, Electron, mobile, help system
8. Tests — full regression results
9. Australian English — zero violations
10. Honest final assessment: Is Peterman ready for Mani to use daily?
11. Known issues and recommended improvements

This audit is the final gate. If it passes, Peterman v2.0 is live.
