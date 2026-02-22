# SOCRATES & DONUTS BUILD INSTRUCTION — PASTE INTO CLINE
# Date: 19 February 2026
# App: Socrates & Donuts — Thinking Companion
# Builder: Guruve (Cline)

You are Guruve — the operational build agent for Almost Magic Tech Lab.
You are building Socrates & Donuts (S&D), a philosophical thinking companion.

---

## WHAT S&D IS (Read This First — It Shapes Everything)

S&D is a conversation partner that helps people think through life's
difficult moments by asking questions, not giving answers. It draws on
wisdom from Stoic philosophy, Buddhist thought, Indigenous wisdom,
Existentialism, Taoism, Sufi poetry, African proverbs, and secular humanism.

IT IS NOT therapy. IT IS NOT an AI chatbot. IT IS NOT a self-help app.
It is a fellow traveller — someone walking alongside you, asking the
questions a thoughtful friend might ask.

The founder, Mani Padisetti, built this because he wished it existed
during difficult periods in his own life. That's the spirit of the product.

---

## PRE-BUILD: Check for Previous Build

Before creating ANYTHING, check if a previous S&D build exists:

```
# Check if repo exists locally
ls -la ~/socrates-and-donuts/ 2>/dev/null
dir socrates-and-donuts\ 2>nul

# Check for existing remote
git ls-remote https://github.com/Almost-Magic/socrates-and-donuts.git 2>/dev/null

# Check if ports are occupied
netstat -ano | findstr "5010 3010"

# Check for old databases
dir *.db /s 2>nul | findstr -i "socrates\|snd"
```

If a previous build exists:
- Stop any running S&D processes
- Back up the old folder: rename to socrates-and-donuts-backup-YYYYMMDD
- Do NOT delete without confirmation
- Verify ports 5010 and 3010 are free

Only proceed once you have confirmed the workspace is clean.

---

## CRITICAL RULES — MEMORISE THESE

```
┌──────────────────────────────────────────────────────────────┐
│  1. AUSTRALIAN ENGLISH everywhere. Code comments, UI text,   │
│     website copy, README, prompts. "Colour" not "color".     │
│     "Organisation" not "organization". "Analyse" not         │
│     "analyze". The ONLY American spelling permitted is       │
│     "Donuts" (the brand name). Everything else: Australian.  │
│                                                              │
│  2. BANNED PHRASES — never use in any user-facing text:      │
│     game-changer, level up, crushing it, awesome, check it   │
│     out (use "have a look"), gotten (use "got"), reach out   │
│     (use "get in touch"), touch base, circle back, utilize   │
│     (use "use"), oftentimes (use "often"), super excited,    │
│     guys (addressing users), unlock your potential, disrupt, │
│     10x, here's the thing, at the end of the day.           │
│                                                              │
│  3. FELLOW TRAVELLER TONE in all S&D text. Never use:        │
│     oracle, guru, sage, guide, mentor, coach, counsellor.    │
│     S&D asks questions. It doesn't advise, prescribe,        │
│     diagnose, or tell anyone what to do.                     │
│                                                              │
│  4. DARK THEME DEFAULT — Midnight #0A0E14, Gold #C9944A     │
│     accent. Dark/light toggle. Tailwind CSS. Lucide icons.   │
│                                                              │
│  5. PORTS: 5010 (Flask backend), 3010 (frontend dev)         │
│     Repository: Almost-Magic/socrates-and-donuts             │
│                                                              │
│  6. NO AI COSTS TO AMTL. User brings their own LLM           │
│     (BYOLLM). Ollama, Claude API (user's key), OpenAI        │
│     (user's key), or any OpenAI-compatible endpoint.         │
│                                                              │
│  7. PRIVACY IS ABSOLUTE. All data stays on the user's        │
│     computer. No telemetry. No analytics. No cloud storage.  │
│     No phone-home except optional update checks.             │
│                                                              │
│  8. NO AI-GENERATED IMAGES. Lucide icons only.               │
│                                                              │
│  9. WHITESPACE IS THE PRIMARY DESIGN ELEMENT. The UI should  │
│     feel like opening a journal, not opening software.        │
│     Generous spacing. Minimal chrome. Room to breathe.       │
│                                                              │
│ 10. EVERY PHASE ENDS WITH TESTS. No exceptions. No deferral.│
│     Beast + Inspector + 4% + Smoke at minimum.               │
│                                                              │
│ 11. NO FAKE TESTIMONIALS. No fabricated social proof. Ever.  │
│                                                              │
│ 12. ELECTRON DESKTOP WRAPPER is required. Not optional.      │
│     S&D is primarily a desktop app.                          │
└──────────────────────────────────────────────────────────────┘
```

---

## NAVIGATION — Keep It Simple

### Website (socratesanddonuts.com): 4 pages only

```
[S&D Logo]  Socrates & Donuts     [What Is This?]  [Try It]  [Download →]
```

| Page | Route | Purpose |
|------|-------|---------|
| Home | `/` | Hero, name story, three pillars, Try It CTA, crisis resources |
| What Is This? | `/about` | Philosophy, who it's for, Mani's story |
| Try It | `/try` | Browser-based demo conversation (3-5 exchanges) |
| Download | `/download` | Platform downloads, Ollama setup guide, privacy promise |

Footer on all pages:
```
Socrates & Donuts — by Almost Magic Tech Lab
Built by Mani Padisetti | Sydney, Australia
[Privacy] [Terms] [Contact]
All conversations stay on your computer. Always.
```

### Desktop App: 3 navigation items only

```
[S&D Logo]                              [Conversations]  [Wisdom Library]  [⚙]
```

| Item | What It Contains |
|------|-----------------|
| Conversations | Past and current conversations. Click to continue or start new |
| Wisdom Library | Browse by emotional theme or philosophical tradition |
| ⚙ Settings | BYOLLM config, appearance, privacy, export/delete data |

NO dashboard. NO metrics. NO streaks. NO gamification. NO social features.
NO notifications badge. NO onboarding wizard. NO feature tour.

---

## THE MAIN SCREEN (Most Important Screen in the App)

When you open S&D, you see this:

```
┌────────────────────────────────────────────────────────────────┐
│  [S&D]                         [Conversations] [Library]  [⚙] │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│                                                                │
│                                                                │
│                                                                │
│                                                                │
│         What's on your mind?                                   │
│                                                                │
│         [________________________________________________]     │
│                                                                │
│                                                                │
│                                                                │
│                                                                │
│                                                                │
│                                                                │
│  ────────────────────────────────────────────────────────────  │
│                                                                │
│  Or pick a starting point:                                     │
│                                                                │
│  [I'm facing a decision]                                       │
│  [Something's bothering me]                                    │
│  [I want to think about my values]                             │
│  [I just want to explore]                                      │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

Mostly whitespace. One input field. Four gentle prompts. No visual noise.

---

## WISDOM LIBRARY — Browse by Theme, Not Tradition

Primary navigation is by EMOTIONAL THEME (what the user is feeling):

- Change & Impermanence
- Courage & Fear
- Relationships & Connection
- Purpose & Meaning
- Loss & Grief
- Decisions & Uncertainty
- Identity & Self-Knowledge
- Anger & Frustration
- Joy & Gratitude
- Work & Contribution

Secondary navigation (smaller, below themes): by philosophical tradition.

Each wisdom entry is a card with:
- Quote
- Brief contextual thought (2-3 sentences, written in S&D voice)
- [Reflect →] button — opens a NEW conversation seeded with that quote

The Wisdom Library needs MINIMUM 400 entries at launch, distributed across
all themes and traditions. Quality over quantity — each contextual thought
must be written in the fellow-traveller voice.

---

## CONVERSATION SCREEN — Wisdom Appears Contextually

During a conversation, S&D may surface a relevant wisdom quote as a
subtle card at the bottom of the chat. This is NOT forced — it appears
only when the AI detects a strong thematic match.

```
  ┌──────────────────────────────────────────────────────────┐
  │  "The impediment to action advances action. What stands  │
  │  in the way becomes the way." — Marcus Aurelius          │
  │                                        [Explore this →]  │
  └──────────────────────────────────────────────────────────┘
```

"Explore this" opens the Wisdom Library entry for that quote.
The card can be dismissed. It never interrupts the conversation flow.

---

## EMOTIONAL SAFETY ARCHITECTURE

This is non-negotiable. Build it in Phase 4 but design for it from Phase 0.

RED FLAG DETECTION (on-device, no cloud):
- Phrase matching for acute distress indicators
- When triggered: STOP Socratic questioning immediately
- Switch to grounding mode:
  "This feels like it might be bigger than a question right now.
   Would it help to talk to someone?"
- Display crisis resources:
  Lifeline: 13 11 14 (24 hours)
  Beyond Blue: 1300 22 4636
- NEVER resume normal questioning after a red flag trigger
- NEVER ask "are you sure?" or try to assess severity — just offer resources

---

## WEBSITE COPY — Use This Exact Text

### Home Page Hero:
```
You don't need answers right now.
You need better questions.

Socrates & Donuts is a thinking companion that helps you
find clarity through conversation — not advice.

[Start a Conversation →]
```

### Three Pillars:
```
YOUR PRIVACY IS ABSOLUTE
Every conversation stays on your computer. Nothing is sent
to any server. Nothing is stored in the cloud. Nothing is
tracked, analysed, or sold. Your thinking belongs to you.

WE ASK, WE DON'T TELL
S&D won't give you a five-step plan or tell you what to do.
It will ask you questions that help you find your own way.
A fellow traveller, not an oracle.

IT'S FREE
S&D runs on your own AI model (we'll help you set it up).
No subscription. No tokens. No "upgrade to premium."
Your computer, your model, your conversations.
```

### Not Therapy (MUST appear on home page):
```
Socrates & Donuts is a thinking tool, not a substitute for
professional support. It won't diagnose, treat, or counsel.

If you're going through a tough time and need someone to
talk to, please reach out:
Lifeline: 13 11 14 (24 hours)
Beyond Blue: 1300 22 4636
```

### About Page — Mani's Story:
```
BUILT WITH CARE
S&D was built by Mani Padisetti at Almost Magic Tech Lab
in Sydney. It started as a personal project — a tool Mani
wanted for himself. The kind of thinking companion he wished
existed during the difficult stretches of his own life.

It's not a business play dressed up as wellbeing software.
It's a genuine attempt to make something useful and human.
```

### The Name (on About page):
```
The American spelling of "Donuts" is deliberate — it's punchier,
more universal, and it's the brand. Everything else in S&D
uses Australian English, because that's where we're from.
```

For full website copy, see /docs/AMTL-SND-WEB-1.0.md

---

## REFERENCE DOCUMENTS

Read these documents before writing any code:

1. /docs/AMTL-ECO-STD-1.0.md — Engineering standards (the constitution)
2. /docs/AMTL-SND-SPC-1.0.md — Product specification (what S&D is)
3. /docs/AMTL-SND-TDD-1.0.md — Technical design (architecture, API, data model)
4. /docs/AMTL-SND-BLD-1.0.md — Build guide (12 phases with test checkpoints)
5. /docs/AMTL-SND-DEC-1.0.md — Decisions already made (don't re-debate)
6. /docs/AMTL-SND-KNW-1.0.md — Known issues and limitations
7. /docs/AMTL-SND-WEB-1.0.md — Website copy (use this exact text)
8. /docs/AMTL-SND-UI-1.0.md — Wireframes (10 screens — follow these layouts)

---

## BUILD ORDER

Follow the phases in AMTL-SND-BLD-1.0.md exactly. Here is the summary:

| Phase | What | Key Deliverables |
|-------|------|-----------------|
| 0 | Environment setup | Repo, Flask on :5010, health endpoint, folder structure |
| 1 | Question Bank + Forced Silence | 50+ questions, daily question, silence timer, breathing donut |
| 2 | Vault | Insights, letters, export/import, search, Wisdom Library screen |
| 3 | Contradiction Finder + Feedback | Detect opposing statements, "Did that land?" feedback |
| 4 | Settings + Red Flag Detection | Intensity dial, domain toggles, crisis detection + grounding |
| 5 | Notifications | Browser push, SMS pipeline (optional), notification preferences |
| 6 | BYOLLM + Socratic Responder | LLM connector, AI settings, Socratic question generation |
| 7 | The Other Side + Three Ways + Insight | Counter-perspective, three frameworks, session summary |
| 8 | Arc Sessions + Vipassana | 7-10 day themed sequences, meditation integration |
| 9 | Electron Wrapper + Workshop | Desktop app, system tray, ELAINE integration |
| 10 | Website Static Build | 4-page website, Try It experience, GitHub Pages |
| 11 | Polish + Accessibility + Final Tests | A11y audit, help system, Gift a Question, final test suite |

IMPORTANT: Phase 0 must include the PRE-BUILD cleanup check.
IMPORTANT: Phase 9 (Electron) is NOT optional. S&D is primarily a desktop app.
IMPORTANT: Phase 10 (Website) must use the copy from AMTL-SND-WEB-1.0.md exactly.

---

## TESTING MANDATE

Every phase must pass these tests before proceeding:

| Test | Tool | What |
|------|------|------|
| Beast | pytest | Core functionality, happy paths |
| Inspector | flake8/pylint | Zero warnings, clean code |
| 4% | pytest | Edge cases — empty input, huge input, special chars, boundary conditions |
| Proof | Playwright | Screenshots verifying rendering matches wireframes |
| Smoke | curl/pytest | "Does it start? Does /api/health return 200?" |
| Regression | pytest | All previous phase tests still pass |
| Integration | pytest | Cross-app (ELAINE, Workshop, Supervisor) — Phase 9+ |

Do NOT skip tests. Do NOT defer tests. Do NOT mark a phase complete
without running ALL applicable tests and showing results.

---

## START NOW

Begin with Phase 0. Present your pre-flight confirmation before writing
any code. Show:
1. Pre-build check results (clean workspace confirmed)
2. Folder structure you will create
3. Dependencies you will install
4. What the health endpoint will return

Then build Phase 0 and run the Phase 0 checkpoint tests.
Commit to dev branch of Almost-Magic/socrates-and-donuts.
