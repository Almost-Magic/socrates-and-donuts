# Socrates & Donuts — Build Guide
## Document Code: AMTL-SND-BLD-1.0
## Almost Magic Tech Lab
## 19 February 2026

> *This document follows AMTL-ECO-STD v1.0. All conventions defined there apply unless explicitly overridden with a Decision Register entry.*

---

## Critical Rules

Before writing a single line of code:

- **Australian English** everywhere (colour, organisation, licence, honour)
- **Dark theme default** with light/dark toggle
- **Port 5010** for Flask backend, **3010** for frontend dev
- **GitHub:** `Almost-Magic/socrates-and-donuts`
- **No duplicate folders.** One home, one truth.
- **No AI costs to AMTL.** User brings their own LLM or uses no AI.
- **Fellow traveller tone** in all user-facing text. Never: oracle, guru, sage, guide.
- **Australian tone in all copy.** No American marketing language. See AMTL-SND-DEC-1.0 DEC-012 for the full banned-phrases list. "Donuts" is the one permitted American spelling (DEC-011). Everything else: Australian English, understated, direct, warm. Before any UI text or website copy goes live, do a final tone review.
- **No AI-generated images.** Lucide icons only.
- **Every phase ends with tests.** No exceptions. No deferral.

---

## Testing Mandate

| Test Type | Every Phase? | What It Covers |
|-----------|:---:|-------------|
| **Beast** (pytest) | ✅ | Core functionality, happy paths |
| **Inspector** (flake8/pylint) | ✅ | Zero warnings, clean code |
| **4%** (edge cases) | ✅ | Empty input, huge input, special characters, missing data, boundary conditions |
| **Proof/Playwright** | UI phases | Screenshots verifying rendering |
| **Smoke** | ✅ | "Does it start? Does /api/health return 200?" |
| **Regression** | ✅ (after Phase 1) | All previous phase tests still pass |
| **Integration** | When touching ELAINE/Supervisor/Workshop | Cross-app communication |

**Do not skip any test type. Do not defer testing to the final phase.**

---

## Phase 0: Environment Setup

### Steps
1. Create repository `Almost-Magic/socrates-and-donuts` if it doesn't exist
2. Create folder structure per AMTL-ECO-STD Section 6.6:
```
socrates-and-donuts/
├── app/
│   ├── __init__.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── api.py
│   │   └── dashboard.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── silence.py
│   │   ├── contradiction.py
│   │   ├── router.py
│   │   ├── vault.py
│   │   ├── feedback.py
│   │   ├── safety.py
│   │   ├── portability.py
│   │   ├── llm.py
│   │   ├── sms.py
│   │   └── push.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── database.py
│   ├── data/
│   │   └── questions.json
│   ├── templates/
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── session.html
│   │   ├── reflections.html
│   │   ├── settings.html
│   │   └── about.html
│   └── static/
│       ├── css/
│       ├── js/
│       └── img/
├── electron/
│   └── main.js
├── tests/
│   ├── beast/
│   ├── inspector/
│   ├── four_percent/
│   ├── smoke/
│   ├── regression/
│   ├── integration/
│   └── proof/
├── docs/
│   └── (all 9 AMTL documents)
├── logs/
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
├── CHANGELOG.md
└── package.json
```
3. Create `.env.example` with all AMTL_SND_* variables (see SPC Section Configuration)
4. Create `.gitignore` (include `.env`, `logs/`, `__pycache__/`, `*.db`, `node_modules/`, `*.egg-info/`)
5. Create `requirements.txt` with pinned versions:
   - flask==3.0.2
   - gunicorn==21.2.0
   - python-dotenv==1.0.1
   - requests==2.31.0
6. Create `package.json` with Electron dependency
7. Initialise Flask app with health endpoint

### Phase 0 Checkpoint

| Test | Command | Expected |
|------|---------|----------|
| Smoke | `python -m app` then `curl localhost:5010/api/health` | 200 with JSON status |
| Inspector | `flake8 app/ --max-line-length=120` | Zero warnings |
| Beast | `pytest tests/beast/test_health.py` | Health endpoint returns valid JSON |

---

## Phase 1: Question Bank + Daily Question + Forced Silence

### Steps
1. Create question bank (`app/data/questions.json`) — minimum 50 questions to start, tagged with:
   - `framework`: one of 9 wisdom traditions
   - `domain`: work|relationships|body|belief|money|grief|creativity|general
   - `intensity`: gentle|reflective|deep|confronting
   - `tags`: freeform array
2. Build `/api/question/today` — deterministic daily selection based on date
3. Build `/api/question/random` — filtered by user's intensity + domain settings
4. Build Forced Silence engine:
   - Timer configurable (default 300 seconds)
   - Input field locked during silence
   - Breathing donut visual (CSS animation — expanding/contracting circle)
   - Soft chime on completion (single tone, not ambient)
   - No countdown numbers — just the breathing circle
5. Build home screen template — question-first, minimal, typographic
6. Build session creation — `POST /api/session/start`
7. Build response submission — `POST /api/session/respond`

### Phase 1 Checkpoint

| Test | Expected |
|------|----------|
| Beast | Question bank loads, daily question returns consistently for same date, random respects filters |
| Inspector | Zero warnings |
| 4% | Empty question bank, invalid intensity, all domains disabled, question with no matching criteria |
| Smoke | App starts, home page renders with today's question |
| Proof | Screenshot of home screen with question, screenshot of forced silence state |

---

## Phase 2: Vault (Insights, Letters, Export/Import)

### Steps
1. Build vault CRUD — insights, one-year letters, unsent letters, aphorisms
2. Build tagging system — manual tags on any vault entry
3. Build search — keyword, tag, date range across all vault entries
4. Build one-year letter time-lock — cannot be opened before `opens_at` date
5. Build export as JSON — entire vault in one downloadable file
6. Build import from JSON — merge or replace vault from uploaded file
7. Build My Reflections screen — unified view of past sessions, insights, letters
8. Build Wisdom Library screen — saved aphorisms and insights with card-style display

### Phase 2 Checkpoint

| Test | Expected |
|------|----------|
| Beast | CRUD operations, search returns correct results, export/import round-trip |
| Inspector | Zero warnings |
| 4% | Empty vault export, import of malformed JSON, search with no results, time-locked letter access before date |
| Smoke | Vault endpoints respond correctly |
| Regression | Phase 1 tests still pass |
| Proof | Screenshot of reflections page, screenshot of export flow |

---

## Phase 3: Contradiction Finder + Feedback Signal

### Steps
1. Build rule-based Contradiction Finder:
   - Within session: detect opposing statements (positive/negative sentiment on same topic)
   - Across sessions: compare current response to past responses on similar questions
   - Surface gently: "You said X earlier. Now you're saying Y. What's between them?"
2. Build feedback signal:
   - After each session: "Did that land?" — Yes / Not sure / Not today
   - Store feedback linked to session and framework
   - Build feedback log for future routing improvements
3. Integrate contradiction display into session view
4. Integrate feedback prompt into session completion flow

### Phase 3 Checkpoint

| Test | Expected |
|------|----------|
| Beast | Contradiction detection triggers on opposing statements, feedback stores correctly |
| Inspector | Zero warnings |
| 4% | Session with no contradictions, single-word responses, identical repeated responses |
| Smoke | Session flow completes with contradiction check and feedback prompt |
| Regression | Phases 1-2 tests still pass |

---

## Phase 4: Settings (Intensity, Domains, Red Flag Detection)

### Steps
1. Build intensity dial — Gentle / Reflective / Deep / Confronting
   - Default: Reflective for new users
   - Affects which questions are served and which frameworks are available
2. Build domain toggles — Work, Relationships, Body, Belief, Money, Grief, Creativity
   - Default: all enabled
   - Questions from disabled domains are excluded
3. Build red flag detection:
   - On-device phrase matching for acute distress indicators
   - When triggered: pause Socratic challenge, shift to grounding mode
   - Display: "This feels like it might be bigger than a question right now. Would it help to talk to someone?" with support resource links
   - Never continue normal questioning after trigger
4. Build Settings screen with all controls
5. Build "When This Is Not Enough" section in About page

### Phase 4 Checkpoint

| Test | Expected |
|------|----------|
| Beast | Intensity filtering works, domain filtering works, red flag detection triggers correctly |
| Inspector | Zero warnings |
| 4% | All domains disabled (must show at least one general question), intensity set to confronting but user is new, red flag false positives, red flag edge phrases |
| Smoke | Settings save and persist across sessions |
| Regression | Phases 1-3 tests still pass |
| Proof | Screenshot of settings page, screenshot of red flag grounding mode |

---

## Phase 5: Browser Push Notifications + SMS Pipeline

### Steps
1. Build browser push notification system:
   - Request permission on first visit (gentle, non-blocking)
   - Daily question delivered at user's configured time
   - Zero cost, zero registration
2. Build SMS pipeline (optional, requires TextBee config):
   - Daily question via SMS at configured time
   - Configurable phone number in settings
   - Graceful degradation if TextBee unavailable
3. Build notification preferences in Settings:
   - Push enabled/disabled
   - Push time (default: 7:00am local)
   - SMS enabled/disabled
   - SMS time
   - SMS phone number

### Phase 5 Checkpoint

| Test | Expected |
|------|----------|
| Beast | Push notification registration, SMS sending (mock), schedule configuration |
| Inspector | Zero warnings |
| 4% | Push permission denied, invalid phone number, TextBee down, duplicate notifications |
| Smoke | Notification settings save correctly |
| Regression | Phases 1-4 tests still pass |

---

## Phase 6: BYOLLM — AI Connection + Socratic Responder

### Steps
1. Build LLM connector supporting:
   - Ollama (via Supervisor :9000 in desktop, direct in website)
   - Anthropic API (Claude) — user's own key
   - OpenAI API — user's own key
   - DeepSeek API — user's own key
   - Any OpenAI-compatible endpoint — user's own key + custom URL
2. Build AI settings page:
   - Provider dropdown
   - API key input (stored locally, never transmitted)
   - Model selection (if applicable)
   - Custom endpoint URL (for OpenAI-compatible)
   - Connection test button
3. Build Socratic Responder:
   - Takes user's text + selected framework + session context
   - Returns a follow-up question in fellow-traveller voice
   - System prompt enforces fellow-traveller tone, never prescriptive
4. Build AI-enhanced framework routing:
   - Use emotional state inference to select framework
   - Incorporate feedback history to weight framework selection
5. All API calls go directly from client to provider — never through AMTL

### Phase 6 Checkpoint

| Test | Expected |
|------|----------|
| Beast | LLM connection (mocked), Socratic response generation (mocked), framework routing logic |
| Inspector | Zero warnings |
| 4% | Invalid API key, provider down, empty response, extremely long user input, all providers unavailable |
| Smoke | AI settings page renders, connection test works (mock) |
| Regression | Phases 1-5 tests still pass |

---

## Phase 7: The Other Side + Three Ways + Insight Extractor

### Steps
1. Build "The Other Side" — counter-perspective generation
   - Input: user's stated position
   - Output: one fellow-traveller counter-perspective
   - System prompt: "You are a fellow traveller, not an adversary. Offer a different vantage point."
2. Build "Three Ways to Look at This"
   - Select three different frameworks for the same input
   - Generate one perspective per framework
   - Never label the framework — just present three angles
3. Build Insight Extractor
   - Reviews full session transcript
   - Proposes one-sentence summary: "It seems the core insight was: '...' Would you like to save this?"
   - User can edit, save, or dismiss
4. Integrate all three into session flow (visible only when AI connected)

### Phase 7 Checkpoint

| Test | Expected |
|------|----------|
| Beast | Other Side generation (mocked), Three Ways generation (mocked), Insight extraction (mocked) |
| Inspector | Zero warnings |
| 4% | Very short input, contradictory input, same perspective generated twice, AI returns empty |
| Regression | Phases 1-6 tests still pass |
| Proof | Screenshot of session with AI features visible |

---

## Phase 8: Arc Sessions + Vipassana Section

### Steps
1. Build Arc Sessions:
   - 7–10 day themed sequences (fear, money, choice, loss, work, relationships, creativity)
   - Each day's question builds on previous day's response
   - Arc tracks progress (current day, completion)
   - User can abandon an arc at any time
2. Build Vipassana section:
   - Pre-sit orientation question
   - Hindrance tracker (desire, aversion, sloth, restlessness, doubt)
   - Post-sit integration: "What did you notice? Where in your daily life does that appear?"
3. Build Practices screen with Forced Silence (standalone), Vipassana, somatic check-in

### Phase 8 Checkpoint

| Test | Expected |
|------|----------|
| Beast | Arc creation, progression, completion, abandonment. Vipassana log CRUD |
| Inspector | Zero warnings |
| 4% | Start arc with one already active, skip a day, abandon on last day, empty sit log |
| Regression | Phases 1-7 tests still pass |
| Proof | Screenshot of arc session day view, screenshot of Vipassana log |

---

## Phase 9: Desktop Electron Wrapper + Workshop Registration

### Steps
1. Build Electron main.js:
   - Auto-start Flask backend via spawn
   - Splash screen with S&D branding
   - Poll /api/health until backend ready
   - 30-second timeout with error dialog
   - Clean shutdown — kill Flask on before-quit
   - System tray integration (close = minimise, quit = exit)
2. Build dark/light theme toggle (persists across sessions)
3. Register in The Workshop:
   - Health endpoint
   - Favicon
   - Launch command
   - Recovery procedures
4. ELAINE integration:
   - Morning briefing includes S&D daily question theme (not raw content)
   - Voice command: "Open Socrates and Donuts"

### Phase 9 Checkpoint

| Test | Expected |
|------|----------|
| Beast | Electron starts, Flask starts, health check passes |
| Smoke | Workshop can launch and monitor S&D |
| Integration | ELAINE receives daily question theme, Workshop health monitoring works |
| Regression | Phases 1-8 tests still pass |

---

## Phase 10: Website Static Build + GitHub Pages

### Steps
1. Create static website version:
   - All HTML/CSS/JS in a `website/` directory
   - No build step — vanilla JS, no framework
   - localStorage for all data persistence
   - Service worker for offline capability (PWA)
   - All question bank embedded in JS
2. Implement client-side versions of:
   - Forced Silence engine
   - Contradiction Finder (rule-based)
   - Vault CRUD
   - Export/Import
   - Settings (intensity, domains)
   - Red flag detection
   - Browser push notifications
   - LLM connection (direct from browser to provider)
3. Deploy to GitHub Pages from `website/` directory

### Phase 10 Checkpoint

| Test | Expected |
|------|----------|
| Beast | All client-side logic works in browser tests |
| Proof | Screenshots of website version on desktop and mobile |
| Regression | Desktop mode (Phases 1-9) still works |

---

## Phase 11: Polish, Accessibility, Final Tests

### Steps
1. Accessibility audit:
   - Keyboard navigation for all features
   - Screen reader compatibility
   - Sufficient colour contrast
   - Focus indicators
2. Context-aware help for every screen (per AMTL-ECO-CTX-1.0)
3. About page with name story, principles, "When This Is Not Enough"
4. Gift a Question feature — shareable single-question link
5. Final comprehensive test run — all 7 test types
6. README.md with project description, setup instructions, philosophy
7. CHANGELOG.md with all changes
8. Final GitHub push

### Phase 11 Checkpoint — FINAL

| Test | Expected |
|------|----------|
| Beast | All core functionality |
| Inspector | Zero warnings across entire codebase |
| 4% | All edge cases |
| Proof | Full screenshot suite — every screen, both modes |
| Smoke | Both desktop and website modes start and respond |
| Regression | Everything passes |
| Integration | Workshop, ELAINE, Supervisor integration verified |

---

## Cline Command Block

Paste this into Cline to start the build:

```
Build Socrates & Donuts following these documents in order:

1. AMTL-ECO-STD-1.0 — Engineering standards (the constitution)
2. AMTL-ECO-STD-1.1-ODA — Operational discipline rules
3. AMTL-SND-SPC-1.0 — What S&D does and its principles
4. AMTL-SND-TDD-1.0 — How S&D is designed (architecture, API, data model)
5. AMTL-SND-DEC-1.0 — Decisions already made (don't re-debate these)
6. AMTL-SND-KNW-1.0 — Known issues and limitations to work around
7. AMTL-SND-BLD-1.0 — Build guide (follow phase by phase)

Start with Phase 0. Present your pre-flight confirmation before writing any code.
Do NOT skip any test type at any phase checkpoint.
Australian English everywhere. Dark theme default. Port 5010.
Fellow traveller tone in all user-facing text — never oracle, guru, sage, or guide.
No AI costs to AMTL — user brings their own LLM.
Commit to dev branch of Almost-Magic/socrates-and-donuts.
```

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 19 February 2026 | Claude (Thalaiva) | Initial build guide — 12 phases, full test mandate |

---

*Almost Magic Tech Lab*
*"Phase by phase. Test by test. No shortcuts."*
