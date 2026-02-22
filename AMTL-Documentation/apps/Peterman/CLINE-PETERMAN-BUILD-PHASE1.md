# PETERMAN BUILD — PHASE 1: CORE WORKFLOW
# Date: 20 February 2026
# Priority: Get the basic workflow actually working
# Paste into a FRESH Cline session

You are Guruve — the operational build agent for Almost Magic Tech Lab.

## CONTEXT

An audit of Peterman v2.0.0 (Flask, port 5011) has been completed.
Result: 2 REAL components, 6 STUBS returning hardcoded 50.0, 9 MISSING.
The core workflow does not work. Peterman is a skeleton.

The existing Flask codebase is at:
C:\Users\ManiPadisetti\Dropbox\Desktop DB\Books and Articles Mani\Books\
Almost Magic Tech Lab AMTL\Source and Brand\AMTL-Documentation\apps\Peterman\

DO NOT start from scratch. Build on top of what exists.
DO NOT create a new repo or new folder structure.

---

## STEP 0: CLEAN UP — ONE PETERMAN, ONE PORT

There are currently TWO Peterman instances running. This is wrong.

**Node.js Peterman v4.2.0** on port 5008 — OLD. Kill it permanently.
**Flask Peterman v2.0.0** on port 5011 — THIS IS THE REAL ONE. Move it to 5008.

Do this now:

```
# 1. Kill the Node.js Peterman on port 5008
netstat -ano | findstr ":5008"
# Note the PID, then:
taskkill /PID <pid> /F

# 2. If there's a Node.js Peterman start script, PM2 entry, or Windows service:
#    Remove it so it doesn't restart. Check:
pm2 list
pm2 delete peterman
# Or check Task Scheduler for any Peterman startup entries

# 3. Back up the old Node.js Peterman folder:
#    Rename to Peterman-nodejs-backup-20260220
#    Do NOT delete — just rename so it won't be confused with the real one

# 4. Change Flask Peterman to port 5008:
#    In app/config.py: change PORT default from 5011 to 5008
#    In .env: set PORT=5008
#    In run.py: verify it reads from config

# 5. If anything else was displaced (SpiderFoot was on 5009, Genie on 5010):
#    Verify those are still running on their correct ports

# 6. Restart Flask Peterman on port 5008:
python run.py

# 7. Verify:
curl http://localhost:5008/api/health
# Must return JSON with status healthy

# 8. Verify old port is free:
netstat -ano | findstr ":5011"
# Should return nothing
```

After this step: ONE Peterman. Port 5008. Flask. Database: peterman_flask.

---

## CRITICAL RULE: ZERO API COSTS

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  ZERO API COSTS. This is non-negotiable. (DEC-003, DEC-004) │
│                                                              │
│  Mani has desktop apps with paid subscriptions. USE THOSE.   │
│  Never call a paid cloud API. Never import openai, anthropic,│
│  google.generativeai, or any cloud SDK for API calls.        │
│  Never add LLM API keys to .env.                            │
│                                                              │
│  FOR PETERMAN'S OWN REASONING (analysis, briefs, scoring):   │
│                                                              │
│     Priority 1: Claude Desktop / Claude CLI                  │
│     Priority 2: Manus Desktop                                │
│     Priority 3: DeepSeek Desktop                             │
│     Priority 4: Perplexity Desktop                           │
│     Priority 5: Ollama (llama3.1:8b via Supervisor :9000)    │
│                                                              │
│  FOR PROBING LLMs (measuring Share of Voice):                │
│                                                              │
│     Use the SAME desktop apps. Claude CLI runs automatically.│
│     Other desktop apps: Mani pastes query → pastes response  │
│     back into Peterman's Manual Probe Station.               │
│                                                              │
│  FOR EMBEDDINGS:                                             │
│                                                              │
│     Ollama only. nomic-embed-text via Supervisor (:9000).    │
│     Always local. Always free.                               │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## HOW TO CALL DESKTOP APPS

### Claude CLI (PRIMARY)

Mani has Claude Max subscription. Claude CLI (`claude`) should be available.

```python
import subprocess

def call_claude(prompt: str, system_prompt: str = None) -> str:
    """Call Claude via CLI. Zero API cost — uses Max subscription."""
    cmd = ['claude', '-p', prompt]
    if system_prompt:
        cmd = ['claude', '-p', prompt, '--system', system_prompt]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120,
            encoding='utf-8', errors='replace'
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            raise Exception(f"Claude CLI error: {result.stderr}")
    except FileNotFoundError:
        raise Exception("Claude CLI not installed")
    except subprocess.TimeoutExpired:
        raise Exception("Claude CLI timed out")
```

Test immediately:
```
claude --version
claude -p "Hello, are you working?"
```
If not installed: `npm install -g @anthropic-ai/claude-code`

### Other Desktop Apps (Manual Probe via Paste)

Perplexity, Manus, DeepSeek, ChatGPT desktop apps don't have CLIs.
Peterman provides a **Manual Probe Station** in the UI:
1. Peterman shows the query to probe
2. Mani copies it, pastes into the desktop app
3. Mani copies the response, pastes back into Peterman
4. Peterman analyses the response

This is NOT a workaround — this IS the design. Desktop subscriptions 
are the cost model. Peterman orchestrates, Mani probes manually for 
apps without CLI access.

### Ollama (Embeddings ONLY)

```python
import requests

def get_embedding(text: str) -> list:
    """Embeddings from Ollama nomic-embed-text. Always local."""
    response = requests.post(
        'http://localhost:9000/api/embeddings',
        json={'model': 'nomic-embed-text', 'prompt': text},
        timeout=30
    )
    response.raise_for_status()
    return response.json()['embedding']
```

### The AI Engine Cascade

Build `app/services/ai_engine.py`:

```python
class AIEngine:
    """Cascading AI engine. ZERO cloud API costs."""
    
    def reason(self, prompt: str, system_prompt: str = None) -> dict:
        """Try Claude CLI first, then Ollama as last resort."""
        # Priority 1: Claude CLI
        try:
            result = call_claude(prompt, system_prompt)
            return {'engine': 'claude_cli', 'response': result, 'success': True}
        except Exception as e:
            logger.warning(f"Claude CLI failed: {e}")
        
        # Priority 2-4: Manus/DeepSeek/Perplexity
        # These require manual interaction — cannot be called programmatically
        # Skip in automated cascade, available via Manual Probe Station
        
        # Priority 5: Ollama (last resort for reasoning)
        try:
            result = call_ollama(prompt, system_prompt)
            return {'engine': 'ollama', 'response': result, 'success': True}
        except Exception as e:
            logger.warning(f"Ollama failed: {e}")
        
        return {'engine': None, 'response': 'All AI engines unavailable', 'success': False}
    
    def embed(self, text: str) -> list:
        """Embeddings ALWAYS via Ollama. No cascade needed."""
        return get_embedding(text)
```

---

## WHAT "WORKING" MEANS

Mani must be able to:
1. Open Peterman at localhost:5008
2. See the War Room dashboard (dark theme)
3. Add a domain (e.g., almostmagic.net.au)
4. Peterman crawls the site and shows what the business does
5. Peterman suggests target keywords/queries
6. Mani approves or edits the keywords
7. Peterman auto-probes via Claude CLI
8. Manual Probe Station shows queries for other desktop apps
9. Mani pastes responses from Perplexity/ChatGPT/etc.
10. Peterman shows real probe results (not hardcoded)
11. Peterman calculates a REAL Peterman Score (not 50.0)
12. Peterman detects hallucinations
13. Peterman generates content briefs to fix gaps
14. Mani approves the briefs in the Approval Inbox

Steps 1-14 must ALL work.

---

## BUILD STEPS — In exact sequence

### Step 1: Fix the AI Engine

Replace current ai_engine.py with the cascade above.
Test Claude CLI. If it works, proceed. If not, install it.
Verify Ollama has nomic-embed-text loaded.

### Step 2: Domain Crawler

Build `app/services/crawler.py`:
- Crawl homepage + up to 50 pages (requests + BeautifulSoup)
- Extract: titles, meta descriptions, H1/H2, body text, schema.org, links
- Detect CMS (WordPress, Webflow, Ghost, static)
- Store crawl data as JSONB in domains table
- Use Claude CLI to generate business summary from crawl data

Endpoint: `POST /api/domains/<id>/crawl`

### Step 3: Keyword/Query Suggestion Engine

Build `app/services/keyword_engine.py`:
- Use Claude CLI to generate 45 target queries from crawl data
  (20 brand + 10 comparison + 10 category + 5 reputation)
- Each tagged: category, priority, expected_answer

Create target_queries table:
```sql
CREATE TABLE target_queries (
    id SERIAL PRIMARY KEY,
    domain_id INTEGER REFERENCES domains(id) NOT NULL,
    query TEXT NOT NULL,
    category VARCHAR(50),
    priority VARCHAR(20) DEFAULT 'medium',
    expected_answer TEXT,
    is_approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

Endpoints:
- `POST /api/domains/<id>/suggest-keywords`
- `GET /api/domains/<id>/keywords`
- `PUT /api/domains/<id>/keywords/<kid>`
- `POST /api/domains/<id>/keywords/approve-all`

### Step 4: LLM Probing Engine

Build `app/services/probe_engine.py` (real implementation):

**Automatic probing (Claude CLI):**
- For each approved query, run via Claude CLI 5 times (DEC-010)
- Use Claude to analyse its own responses for domain mention, position, sentiment

**Manual probing (other desktop apps):**
- Create probe_queue: list of queries × desktop apps that need manual probing
- UI shows queries to copy, text area to paste responses
- On submit, Claude CLI analyses the pasted response

**Analysis prompt for each response:**
```
Given this query: "[query]"
And this response from [LLM name]:
"[response text]"

For the domain [domain name]:
1. Is the domain mentioned? (yes/no)
2. Position of first mention (1st, 2nd, 3rd... or not mentioned)
3. Sentiment (positive/neutral/negative)
4. Exact mention quote (if any)
5. Competing businesses mentioned instead?
Respond as JSON only.
```

Endpoints:
- `POST /api/domains/<id>/probe` (trigger auto-probe via Claude CLI)
- `POST /api/domains/<id>/probe/manual` (submit pasted response)
- `GET /api/domains/<id>/probe-queue` (queries needing manual probing)
- `GET /api/domains/<id>/probes` (all results)
- `GET /api/domains/<id>/probes/latest` (most recent cycle)

### Step 5: Real Peterman Score

Replace ALL hardcoded 50.0 values with real calculations:

| Component | Weight | Source |
|-----------|--------|--------|
| LLM Share of Voice | 25% | Avg mention rate across queries × LLMs |
| Semantic Gravity | 20% | Cosine similarity: domain vs topic embeddings (Ollama) |
| Technical Foundation | 15% | Crawl data: sitemap, robots.txt, schema, SSL |
| Content Survivability | 15% | Claude summarises pages, scores fact retention |
| Hallucination Debt | 10% | 100 - (active_hallucinations × severity) |
| Competitive Position | 10% | Domain mention rate vs top competitor |
| Predictive Velocity | 5% | SoV trend over last 4 cycles |

No data yet → show "Pending". Never show 50.0.

### Step 6: Hallucination Detection

Build `app/services/hallucination_detector.py`:
- After probing, use Claude CLI to compare LLM claims vs crawl data
- Flag mismatches as hallucinations with severity 1-10
- Status: open → brief_generated → content_deployed → verified_closed

Endpoints:
- `GET /api/domains/<id>/hallucinations`
- `GET /api/domains/<id>/hallucinations/<hid>`

### Step 7: Content Brief Generation (The Forge)

Build `app/services/forge.py`:
- For each hallucination or gap, use Claude CLI to generate briefs
- Brief includes: title, target query, key facts, content structure,
  where to publish, expected score impact

Endpoints:
- `POST /api/domains/<id>/hallucinations/<hid>/generate-brief`
- `GET /api/domains/<id>/briefs`

### Step 8: Approval System

Build `app/services/approvals.py`:

Create approvals table:
```sql
CREATE TABLE approvals (
    id SERIAL PRIMARY KEY,
    domain_id INTEGER REFERENCES domains(id) NOT NULL,
    approval_type VARCHAR(50) NOT NULL,
    item_id INTEGER NOT NULL,
    item_type VARCHAR(50) NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    impact_statement TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    decided_at TIMESTAMP,
    decided_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);
```

Endpoints:
- `GET /api/domains/<id>/approvals`
- `POST /api/approvals/<aid>/approve`
- `POST /api/approvals/<aid>/decline`

Keywords suggested → approval created.
Briefs generated → approval created.

### Step 9: War Room Dashboard

HTML/CSS/JS, no framework (DEC-007).
Dark theme (#0A0E14), Gold accent (#C9944A).
Tailwind CSS + Lucide icons via CDN.

`app/templates/war_room.html` — single page app with sections:

1. **Domain Cards** (top) — click to select, + Add Domain button
2. **Peterman Score** (left) — circular gauge, real number, grade A-F
3. **Approval Inbox** (right) — pending items with Approve/Decline buttons
4. **LLM Share of Voice** (middle) — bar chart per LLM
5. **Manual Probe Station** — queries to copy, paste-back text area
6. **Hallucinations** — active list with severity badges
7. **Content Briefs** — pending briefs with Review button

JavaScript:
- Fetch data from API on load and every 60s
- Domain card click loads that domain's data
- Add Domain modal: enter URL → triggers crawl + keyword suggestion
- Approval buttons call the approve/decline endpoints
- Manual Probe: copy-to-clipboard button + paste-back submit

### Step 10: Smoke Test

After building Steps 0-9, test end-to-end:

1. ✅/❌ localhost:5008 loads War Room (dark theme)
2. ✅/❌ No Node.js Peterman running anywhere
3. ✅/❌ Add almostmagic.net.au — crawl runs, summary appears
4. ✅/❌ Keywords suggested, visible in Approval Inbox
5. ✅/❌ Approve keywords
6. ✅/❌ Claude CLI auto-probe runs, results appear
7. ✅/❌ Manual Probe Station shows queries for other apps
8. ✅/❌ Paste a Perplexity response — it gets analysed
9. ✅/❌ Real Peterman Score (not 50.0)
10. ✅/❌ Hallucinations detected and listed
11. ✅/❌ Generate Brief on a hallucination
12. ✅/❌ Brief in Approval Inbox
13. ✅/❌ Approve the brief
14. ✅/❌ Audit log shows all actions

ALL 14 must pass. Fix failures before declaring done.

---

## STEP 11: DEEP AUDIT — Compare Code vs Spec

After the smoke test passes, run a full audit. Do NOT skip this.

### 11A: Core Workflow Audit

For each of the 17 components below, open the actual code file and verify
it is REAL working code, not a stub or placeholder:

| # | Component | File | Real Code? | Returns Real Data? |
|---|-----------|------|------------|-------------------|
| 1 | Domain onboarding + crawl + CMS detection | app/services/crawler.py | ? | ? |
| 2 | Keyword/query suggestion | app/services/keyword_engine.py | ? | ? |
| 3 | LLM probing (Claude CLI auto) | app/services/probe_engine.py | ? | ? |
| 4 | LLM probing (Manual Probe Station) | app/services/probe_engine.py | ? | ? |
| 5 | Probe normalisation (5 runs, averaging) | app/services/probe_engine.py | ? | ? |
| 6 | Peterman Score (7 components, weighted) | app/services/score_engine.py | ? | ? |
| 7 | Hallucination detection | app/services/hallucination_detector.py | ? | ? |
| 8 | Content brief generation (The Forge) | app/services/forge.py | ? | ? |
| 9 | Approval Gate system | app/services/approvals.py | ? | ? |
| 10 | AI Engine cascade (Claude CLI → Ollama) | app/services/ai_engine.py | ? | ? |
| 11 | Embeddings (Ollama nomic-embed-text) | app/services/ai_engine.py | ? | ? |
| 12 | Budget monitor | app/services/budget.py | ? | ? |
| 13 | Audit log (append-only) | ? | ? | ? |
| 14 | Semantic Gravity Score | app/services/score_engine.py | ? | ? |
| 15 | Content Survivability (LCRI) | app/services/score_engine.py | ? | ? |
| 16 | Competitive Position scoring | app/services/score_engine.py | ? | ? |
| 17 | Predictive Velocity scoring | app/services/score_engine.py | ? | ? |

For EACH item: state EXISTS WITH REAL CODE / STUB / MISSING.
If any component still returns hardcoded 50.0, report it as STUB.

### 11B: Database Audit

Run `\dt` and list every table. Compare against required:

Required tables:
- domains
- target_queries (NEW — created in Step 3)
- probe_results
- peterman_scores
- hallucinations
- content_briefs
- deployments
- audit_log
- budget_tracking
- domain_embeddings
- approvals (NEW — created in Step 8)
- competitor_domains
- scheduled_tasks

Show: Table | Exists? | Has Data?

### 11C: API Endpoints Audit

List every route in the Flask app:
```python
from app import create_app
app = create_app()
for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
    print(f"{','.join(rule.methods - {'HEAD','OPTIONS'}):8s} {rule.rule}")
```

Compare against required endpoints:

```
POST /api/domains                          — add domain
GET  /api/domains                          — list domains
GET  /api/domains/<id>                     — domain detail
DELETE /api/domains/<id>                   — remove domain
POST /api/domains/<id>/crawl              — trigger crawl
POST /api/domains/<id>/suggest-keywords   — generate keywords
GET  /api/domains/<id>/keywords           — list keywords
PUT  /api/domains/<id>/keywords/<kid>     — edit keyword
POST /api/domains/<id>/keywords/approve-all — bulk approve
POST /api/domains/<id>/probe              — trigger auto-probe
POST /api/domains/<id>/probe/manual       — submit manual probe
GET  /api/domains/<id>/probe-queue        — queries needing manual probe
GET  /api/domains/<id>/probes             — all probe results
GET  /api/domains/<id>/probes/latest      — most recent cycle
GET  /api/domains/<id>/score              — Peterman Score
GET  /api/domains/<id>/chambers           — chamber status
GET  /api/domains/<id>/hallucinations     — hallucination list
GET  /api/domains/<id>/hallucinations/<hid> — hallucination detail
POST /api/domains/<id>/hallucinations/<hid>/generate-brief — create brief
GET  /api/domains/<id>/briefs             — content briefs
GET  /api/domains/<id>/briefs/<bid>       — brief detail
GET  /api/domains/<id>/approvals          — pending approvals
POST /api/approvals/<aid>/approve         — approve
POST /api/approvals/<aid>/decline         — decline
GET  /api/domains/<id>/budget             — budget status
GET  /api/health                          — health check
```

Show: Endpoint | Exists? | Returns Real Data?

### 11D: AI Engine Audit

Verify:
1. Claude CLI is the PRIMARY reasoning engine (not Ollama)
2. Ollama is used ONLY for embeddings (nomic-embed-text)
3. No cloud API SDKs imported (no openai, no anthropic, no google.generativeai)
4. No API keys in .env for cloud LLM services
5. The cascade is: Claude CLI → Ollama (for automated), Manual Probe Station (for desktop apps)

Run these checks:
```
# Check for forbidden imports
grep -ri "import openai" app/ --include="*.py"
grep -ri "import anthropic" app/ --include="*.py"
grep -ri "import google.generativeai" app/ --include="*.py"
grep -ri "from openai" app/ --include="*.py"
grep -ri "from anthropic" app/ --include="*.py"

# Check .env for API keys that should NOT be there
grep -i "OPENAI_API_KEY" .env
grep -i "ANTHROPIC_API_KEY" .env
grep -i "PERPLEXITY_API_KEY" .env
grep -i "GOOGLE_AI_KEY" .env

# Check ai_engine.py — what does it actually call?
type app\services\ai_engine.py
```

If ANY cloud API imports or keys are found, report as VIOLATION.

### 11E: Australian English Audit

Search all code for American spellings:
```
grep -ri "behavior" app/ --include="*.py" --include="*.js" --include="*.html" --include="*.css"
grep -ri "analyze[^d]" app/ --include="*.py" --include="*.js" --include="*.html"
grep -ri "organize" app/ --include="*.py" --include="*.js" --include="*.html"
grep -ri "recognize" app/ --include="*.py" --include="*.js" --include="*.html"
grep -ri "center\b" app/ --include="*.py" --include="*.js" --include="*.html"
grep -ri "color[^:]" app/ --include="*.py" --include="*.js" --include="*.html"
grep -ri "defense" app/ --include="*.py" --include="*.js" --include="*.html"
grep -ri "license\b" app/ --include="*.py" --include="*.js" --include="*.html"
grep -ri "utilize" app/ --include="*.py" --include="*.js" --include="*.html"
```

Note: CSS property `color:` is fine. We mean UI text, comments, variable names.
Report every American spelling found with file and line number.

### 11F: Design Standards Audit

Check:
1. Dark theme default (Midnight #0A0E14) — open main CSS/template, verify
2. Gold accent (#C9944A) — verify it's used for CTAs and highlights
3. Dark/light toggle exists and works
4. Lucide icons used (not Font Awesome, not emoji in production)
5. Tailwind CSS loaded
6. Favicon exists
7. Responsive layout (check meta viewport tag)

### 11G: Electron Desktop Wrapper

Check:
- Is there an electron/ folder?
- Is there a main.js for Electron?
- Is there a package.json with electron dependency?
- Can it launch? (npm run electron or similar)

If Electron wrapper does NOT exist: report "MISSING — Electron wrapper not built."
This is expected for Phase 1 — it's Phase 9 in the full build. Just note it.

### 11H: Tests

Check:
- Is there a tests/ folder?
- How many test files?
- Run: `pytest tests/` (or `python -m pytest`)
- Show pass/fail results
- If no tests exist, report "NO TESTS — must be added"

---

## AUDIT OUTPUT

Produce ONE document: PETERMAN-POST-BUILD-AUDIT-2026-02-20.md

Sections:
1. Smoke Test Results (14 checks — pass/fail)
2. Core Workflow Audit (17 components — real/stub/missing)
3. Database Audit (tables present vs required)
4. API Endpoints Audit (present vs required)
5. AI Engine Audit (Claude CLI primary? No cloud APIs? Ollama embeddings only?)
6. Australian English Violations (list every American spelling found)
7. Design Standards Check
8. Electron Wrapper Status
9. Test Results
10. **Honest Summary: What is genuinely working vs what still has gaps**
11. **Remaining Work: Prioritised list of what's still needed**

---

## RULES REMINDER

- Australian English everywhere
- Dark theme default (#0A0E14), gold accent (#C9944A)
- ZERO API costs — desktop apps and CLI only
- Ollama ONLY for embeddings
- Port 5008 — ONE Peterman, Flask only
- HTML/CSS/JS frontend, no framework (DEC-007)
- Audit log is append-only (DEC-008)
- No hardcoded scores — real data or "Pending"

## START NOW

Step 0: Kill Node.js Peterman, move Flask to port 5008.
Step 1: Test Claude CLI.
Steps 2-10 in order.
Show smoke test results at the end.
