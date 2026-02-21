# Socrates & Donuts — Technical Design Document
## Document Code: AMTL-SND-TDD-1.0
## Almost Magic Tech Lab
## 19 February 2026

> *This document follows AMTL-ECO-STD v1.0. All conventions defined there apply unless explicitly overridden with a Decision Register entry.*

---

## 1. Overview

| Field | Value |
|-------|-------|
| App Name | Socrates & Donuts (S&D) |
| App Code | SND |
| Type | Public open-source + AMTL desktop integration |
| Backend Port | 5010 |
| Frontend Dev Port | 3010 |
| Repository | `Almost-Magic/socrates-and-donuts` |
| Backend | Flask (Python 3.12+) |
| Frontend (website) | Static HTML/JS/CSS — no framework, vanilla JS |
| Frontend (desktop) | Electron wrapper → Flask backend |
| Data Storage (website) | localStorage + FileSystem Access API (optional) |
| Data Storage (desktop) | SQLite in `~/.socrates-and-donuts/` |
| AI | Optional — user-provided LLM via direct connection |

### Key Dependencies

| Dependency | Type | Required? |
|-----------|------|-----------|
| Flask | Backend framework | Desktop mode only |
| SQLite | Data storage | Desktop mode only |
| Electron | Desktop shell | Desktop mode only |
| Ollama (via Supervisor) | Local AI | Optional |
| TextBee | SMS delivery | Optional |
| ELAINE | Morning briefing integration | AMTL internal only |

---

## 2. System Architecture

### 2.1 Dual-Mode Architecture

S&D operates in two distinct modes sharing the same question bank and UI:

```
┌─────────────────────────────────────────────────────┐
│                    WEBSITE MODE                      │
│  (GitHub Pages — zero infrastructure)                │
│                                                      │
│  ┌──────────┐   ┌──────────┐   ┌────────────────┐  │
│  │ Static   │   │ Vanilla  │   │ localStorage   │  │
│  │ HTML/CSS │◄──│ JS Engine│──►│ (or OPFS)      │  │
│  └──────────┘   └────┬─────┘   └────────────────┘  │
│                      │                               │
│                      ▼ (optional, user's own key)    │
│               ┌──────────────┐                       │
│               │ LLM Provider │                       │
│               │ (direct call)│                       │
│               └──────────────┘                       │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                   DESKTOP MODE                       │
│  (Electron + Flask — full feature set)               │
│                                                      │
│  ┌──────────┐   ┌──────────┐   ┌────────────────┐  │
│  │ Electron │   │  Flask   │   │    SQLite      │  │
│  │ Shell    │◄──│ :5010    │──►│ ~/.snd/vault.db│  │
│  └──────────┘   └────┬─────┘   └────────────────┘  │
│                      │                               │
│          ┌───────────┼───────────┐                   │
│          ▼           ▼           ▼                   │
│  ┌────────────┐ ┌─────────┐ ┌─────────┐            │
│  │ Supervisor │ │ TextBee │ │ ELAINE  │            │
│  │ :9000      │ │  (SMS)  │ │ :5000   │            │
│  └────────────┘ └─────────┘ └─────────┘            │
└─────────────────────────────────────────────────────┘
```

### 2.2 Position in AMTL Ecosystem

```
                    ┌─────────────┐
                    │  Workshop   │
                    │   :5003     │
                    └──────┬──────┘
                           │ health monitoring
                    ┌──────▼──────┐
        ┌──────────►│    S&D      │◄──────────┐
        │           │   :5010     │            │
        │           └──────┬──────┘            │
        │                  │                   │
   ┌────┴─────┐    ┌──────▼──────┐    ┌───────┴───────┐
   │ ELAINE   │    │ Supervisor  │    │  Foreperson   │
   │ :5000    │    │   :9000     │    │    :9100      │
   │(briefing)│    │ (AI routing)│    │  (audit)      │
   └──────────┘    └──────┬──────┘    └───────────────┘
                          │
                   ┌──────▼──────┐
                   │   Ollama    │
                   │   :11434    │
                   └─────────────┘
```

---

## 3. Component Architecture

### 3.1 Shared Components (Both Modes)

| Component | Purpose | Location |
|-----------|---------|----------|
| **Question Bank** | 365+ curated Socratic questions, categorised by framework, domain, and intensity | `app/data/questions.json` |
| **Forced Silence Engine** | Timer that locks input, provides breathing donut visual | `app/services/silence.py` / `static/js/silence.js` |
| **Contradiction Finder** | Rule-based intra-session and cross-session inconsistency detection | `app/services/contradiction.py` |
| **Framework Router** | Selects question framework based on domain, intensity, history, and feedback | `app/services/router.py` |
| **Vault Manager** | CRUD for insights, letters, session summaries, tags | `app/services/vault.py` |
| **Feedback Collector** | "Did that land?" signal, stored per session | `app/services/feedback.py` |
| **Red Flag Detector** | On-device phrase matching for acute distress, triggers grounding mode | `app/services/safety.py` |
| **Export/Import Engine** | JSON vault serialisation and deserialisation | `app/services/portability.py` |

### 3.2 Desktop-Only Components

| Component | Purpose | Location |
|-----------|---------|----------|
| **Flask App** | HTTP backend serving API and templates | `app/__init__.py`, `app/routes/` |
| **SQLite Store** | Persistent vault storage on file system | `app/models/database.py` |
| **LLM Connector** | Connects to user's LLM (Ollama, Claude, OpenAI, DeepSeek, custom) | `app/services/llm.py` |
| **SMS Sender** | TextBee integration for daily question delivery | `app/services/sms.py` |
| **Push Scheduler** | Schedules and sends browser push notifications | `app/services/push.py` |
| **Electron Shell** | Desktop wrapper with tray integration | `electron/main.js` |

### 3.3 AI Intelligence Layers (When LLM Connected)

| Layer | Function | Input | Output |
|-------|----------|-------|--------|
| **Emotional State Inference** | Detects sentiment, intensity, distortion probability | User's text | State object |
| **Framework Selector** | Chooses which wisdom tradition to draw from | State + history + intensity setting | Framework tag |
| **Socratic Responder** | Generates follow-up questions in fellow-traveller voice | User text + framework + context | Question text |
| **The Other Side** | Generates counter-perspective | User's stated position | Counter-perspective text |
| **Three Ways** | Generates three unlabelled framework angles | User text + three selected frameworks | Three perspective texts |
| **Insight Extractor** | Proposes one-sentence session summary | Full session transcript | Summary sentence |
| **Metaphor Detector** | Identifies and flags metaphorical language for exploration | User text | Metaphor flags |
| **Depth Throttle** | Monitors session intensity, triggers shift to grounding | Session duration + intensity signals | Mode shift command |

---

## 4. API Reference

### 4.1 Core Endpoints (Flask Backend — Desktop Mode)

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| GET | `/` | Dashboard — today's question | None |
| GET | `/about` | About S&D — the name story, principles | None |
| GET | `/api/health` | Health check for Workshop integration | None |
| GET | `/api/question/today` | Get today's daily question | None |
| GET | `/api/question/random` | Get a random question (filtered by intensity + domains) | None |
| POST | `/api/session/start` | Start a new reflection session | None |
| POST | `/api/session/respond` | Submit a response to the current question | None |
| GET | `/api/session/<id>` | Get a past session by ID | None |
| GET | `/api/vault/insights` | List saved insights | None |
| POST | `/api/vault/insights` | Save a new insight | None |
| GET | `/api/vault/letters` | List letters (one-year and unsent) | None |
| POST | `/api/vault/letters` | Save a new letter | None |
| GET | `/api/vault/search` | Search vault by keyword, tag, or date range | None |
| GET | `/api/vault/export` | Export entire vault as JSON | None |
| POST | `/api/vault/import` | Import vault from JSON | None |
| GET | `/api/arc/active` | Get currently active arc session | None |
| POST | `/api/arc/start` | Start a new arc session (theme + duration) | None |
| GET | `/api/settings` | Get user settings (intensity, domains, LLM config) | None |
| PUT | `/api/settings` | Update user settings | None |
| GET | `/api/help/<screen_id>` | Context-aware help for current screen | None |
| POST | `/api/ai/respond` | Send text to connected LLM for Socratic response | None |
| POST | `/api/ai/other-side` | Get counter-perspective from connected LLM | None |
| POST | `/api/ai/three-ways` | Get three framework perspectives from connected LLM | None |
| POST | `/api/ai/extract-insight` | Get AI-proposed session summary | None |

**No authentication required** — all data is local, all API calls are localhost only.

### 4.2 Health Endpoint Response

```json
{
  "status": "healthy",
  "app": "Socrates & Donuts",
  "version": "1.0.0",
  "port": 5010,
  "uptime_seconds": 3600,
  "vault_entries": 47,
  "llm_connected": true,
  "llm_provider": "ollama",
  "questions_in_bank": 365,
  "active_arc": null
}
```

---

## 5. Data Model

### 5.1 SQLite Schema (Desktop Mode)

```sql
-- Questions bank (pre-loaded, read-only)
CREATE TABLE questions (
    id TEXT PRIMARY KEY,
    text TEXT NOT NULL,
    framework TEXT NOT NULL,        -- shadow|stoic|parts|narrative|logotherapy|byron_katie|clean|immunity|appreciative
    domain TEXT NOT NULL,           -- work|relationships|body|belief|money|grief|creativity|general
    intensity TEXT NOT NULL,        -- gentle|reflective|deep|confronting
    tags TEXT,                      -- JSON array of tags
    arc_theme TEXT                  -- NULL or arc theme name
);

-- Sessions
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    question_id TEXT NOT NULL,
    question_text TEXT NOT NULL,
    started_at TEXT NOT NULL,       -- ISO 8601
    completed_at TEXT,
    silence_duration_seconds INTEGER,
    response_text TEXT,
    ai_followups TEXT,              -- JSON array of AI follow-up exchanges
    contradictions_found TEXT,      -- JSON array of contradiction objects
    feedback TEXT,                  -- yes|not_sure|not_today|NULL
    intensity TEXT NOT NULL,
    FOREIGN KEY (question_id) REFERENCES questions(id)
);

-- Vault entries (insights, letters)
CREATE TABLE vault (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,             -- insight|one_year_letter|unsent_letter|aphorism
    content TEXT NOT NULL,
    session_id TEXT,                -- NULL if manually created
    tags TEXT,                      -- JSON array of tags
    created_at TEXT NOT NULL,
    opens_at TEXT,                  -- For one-year letters
    is_opened INTEGER DEFAULT 0,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

-- Arc sessions
CREATE TABLE arcs (
    id TEXT PRIMARY KEY,
    theme TEXT NOT NULL,
    started_at TEXT NOT NULL,
    duration_days INTEGER NOT NULL,
    current_day INTEGER DEFAULT 1,
    completed INTEGER DEFAULT 0
);

-- User settings
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- Feedback history (for framework learning)
CREATE TABLE feedback_log (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    framework TEXT NOT NULL,
    feedback TEXT NOT NULL,         -- yes|not_sure|not_today
    logged_at TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);
```

### 5.2 localStorage Schema (Website Mode)

Same logical model, stored as JSON objects in localStorage keys:

| Key | Value |
|-----|-------|
| `snd_sessions` | JSON array of session objects |
| `snd_vault` | JSON array of vault entry objects |
| `snd_arcs` | JSON array of arc session objects |
| `snd_settings` | JSON object of user settings |
| `snd_feedback` | JSON array of feedback log entries |

---

## 6. Technology Stack

| Technology | Version | Purpose | Why Chosen |
|-----------|---------|---------|------------|
| Python | 3.12+ | Backend language | AMTL standard |
| Flask | 3.0+ | Web framework | AMTL standard, lightweight |
| SQLite | 3.40+ | Local database | Zero-config, file-based, perfect for local-first |
| Electron | 28+ | Desktop shell | AMTL standard for desktop apps |
| Vanilla JS | ES2022 | Website frontend | No build step, no framework dependency, maximum simplicity |
| Tailwind CSS | 3.4+ | Styling | AMTL standard |
| Lucide Icons | Latest | Iconography | AMTL standard |

---

## 7. UI Architecture

### 7.1 Design Philosophy

**Typography-first, not atmosphere.** The interface is quiet, typographic, and contemplative. No ambient backgrounds, no particle effects, no gamification.

| Element | Treatment |
|---------|-----------|
| Questions | Serif font, generous whitespace, centred |
| User responses | Sans-serif, left-aligned |
| Forced Silence | Breathing donut (expanding/contracting circle), no countdown numbers |
| Insights | Distinct card style, gentle fade-in |
| Letters | Sealed envelope metaphor with reverence |
| Navigation | Minimal hamburger/side nav, never a dashboard |

### 7.2 Colour Palette

Inherits AMTL palette with S&D-specific additions:

| Name | Hex | Usage |
|------|-----|-------|
| AMTL Midnight | #0A0E14 | Default dark background |
| AMTL Gold | #C9944A | Accent, breathing donut |
| Warm White | #F5F0EB | Light mode background (warmer than pure white) |
| Ink | #2C2C2C | Dark text on light mode |
| Silence Blue | #1A2A3A | Forced silence background overlay |

### 7.3 Screen Map

```
Home (Today's Question)
├── [Respond] → Session View (with Forced Silence)
│   ├── [AI features if connected]
│   └── [Did that land?] → Feedback
├── [≡ Menu]
│   ├── My Reflections
│   │   ├── Past Sessions
│   │   ├── Saved Insights
│   │   ├── Letters (One-Year + Unsent)
│   │   └── Wisdom Library
│   ├── Practices
│   │   ├── Forced Silence (standalone)
│   │   ├── Vipassana Log
│   │   └── Somatic Check-in
│   ├── Dialogues (requires AI)
│   │   ├── The Other Side
│   │   └── Three Ways to Look at This
│   ├── Settings
│   │   ├── Intensity Dial
│   │   ├── Domain Toggles
│   │   ├── Notifications
│   │   ├── Connect AI
│   │   └── Export / Import
│   └── About S&D
└── [?] → Context Help
```

---

## 8. Error Handling & Resilience

### 8.1 Fallback Chain

| Component | If Down | Fallback |
|-----------|---------|----------|
| LLM connection | User's API key fails or Ollama down | Graceful degradation — AI features disabled, rule-based features continue |
| TextBee SMS | API fails | Skip SMS, rely on browser push and in-app |
| Browser push | Permission denied | In-app notification next time user opens S&D |
| SQLite | Database corrupted | Import from last JSON export |
| localStorage | Cleared by user | Import from downloaded JSON export |

### 8.2 No AI Required

All core features work without AI:
- Daily question ✅ (curated bank)
- Forced Silence ✅ (timer)
- Contradiction Finder ✅ (rule-based pattern matching)
- Vault ✅ (CRUD)
- Export/Import ✅ (JSON)
- Push notifications ✅ (browser API)
- Feedback signal ✅ (local storage)

---

## 9. Security Architecture

### 9.1 Local-First Principle

- Zero server-side data storage
- Zero telemetry, analytics, or tracking
- Zero registration or accounts
- All data on user's device (localStorage or SQLite file)
- API keys stored locally, never transmitted to AMTL
- LLM calls go directly from user's device to their chosen provider

### 9.2 Desktop Mode Security

- Flask binds to `127.0.0.1` only (no network exposure)
- SQLite file permissions set to user-only read/write
- No authentication needed (localhost-only access)
- Electron disables `nodeIntegration` in renderer, enables `contextIsolation`

---

## 10. Self-Healing Registration (Workshop)

```yaml
app:
  name: "Socrates & Donuts"
  code: SND
  port: 5010
  health_endpoint: "/api/health"
  startup_command: "python -m app"
  startup_directory: "Source and Brand/Socrates and Donuts"
  electron_main: "electron/main.js"
  recovery:
    level_1: "restart_backend"
    level_2: "kill_port_5010_then_restart"
    level_3: "full_clean_restart"
  dependencies:
    hard: []
    soft: ["supervisor"]
```

---

## 11. Known Technical Debt

| Item | Status | Priority |
|------|--------|----------|
| Website mode uses localStorage (fragile) | Accepted — mitigated by export/import | Low |
| No real-time sync between website and desktop modes | By design — they are separate instances | N/A |
| Contradiction Finder rule-based only (no AI enhancement yet) | Phase 2 | Medium |
| Question bank limited to English | Accepted for v1 | Low |

---

## 12. Build Phase Status

| Phase | Description | Status |
|-------|-------------|--------|
| 0 | Environment, folder structure, dependencies | ⬜ Not started |
| 1 | Question bank, daily question, Forced Silence | ⬜ Not started |
| 2 | Vault (insights, letters), export/import | ⬜ Not started |
| 3 | Contradiction Finder, feedback signal | ⬜ Not started |
| 4 | Settings (intensity, domains), red flag detection | ⬜ Not started |
| 5 | Browser push notifications, SMS pipeline | ⬜ Not started |
| 6 | BYOLLM — AI connection, Socratic responder | ⬜ Not started |
| 7 | The Other Side, Three Ways, Insight Extractor | ⬜ Not started |
| 8 | Arc sessions, Vipassana section | ⬜ Not started |
| 9 | Desktop Electron wrapper, Workshop registration | ⬜ Not started |
| 10 | Website static build, GitHub Pages deployment | ⬜ Not started |
| 11 | Polish, accessibility, final tests, documentation | ⬜ Not started |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 19 February 2026 | Claude (Thalaiva) | Initial TDD — dual-mode architecture, API, data model, UI, phases |

---

*Almost Magic Tech Lab*
*"The blueprint for a quiet space that asks good questions."*
