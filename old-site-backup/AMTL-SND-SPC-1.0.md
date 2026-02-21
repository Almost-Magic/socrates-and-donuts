# Socrates & Donuts — Specification Addendum
## Document Code: AMTL-SND-SPC-1.0
## Almost Magic Tech Lab
## 19 February 2026

> *This document follows AMTL-ECO-STD v1.0. All conventions defined there apply unless explicitly overridden with a Decision Register entry.*

---

## What It Is

Socrates & Donuts (S&D) is a daily companion for the examined life. It asks one Socratic question a day, forces you to sit with it before answering, remembers how you think over time, and surfaces contradictions and patterns you can't see yourself. It is rigour wrapped in warmth — the philosopher who asks hard questions and the friend who brings donuts.

## The Problem It Solves

The current landscape offers tools for crisis (therapy apps), tools for relaxation (meditation apps), and tools for logging (journaling apps). No tool exists for the daily practice of living an examined life — Socratic inquiry as a way of being, not a crisis intervention.

The original S&D was a "fire extinguisher" — used in moments of distress, then ignored. This version transforms it into a daily companion that reaches out to you, not the other way around.

## The Name

**Socrates** — the method. He didn't teach. He asked. He sat with people in the agora and asked questions until they discovered what they already knew. He was never the expert. He was the fellow traveller who happened to ask better questions.

**Donuts** — the warmth. Socrates without donuts is an interrogation. The donut is the reminder that this isn't clinical, isn't academic, isn't therapy. It's the comfort of sitting with a friend over coffee and something sweet, and somehow the conversation goes deeper than you expected. The donut is permission to be human while doing hard thinking.

---

## Core Capabilities

| Capability | What It Does | Why It Matters |
|-----------|-------------|----------------|
| **Daily Question** | Delivers one curated Socratic question per day via push notification, SMS, or ELAINE briefing | The question travels to you — you don't have to remember to reflect |
| **Forced Silence** | Locks the input field for a configurable period (default 5 minutes) after presenting a question | The answer after sitting is different from the first answer. This is the single most differentiating feature |
| **Contradiction Finder** | Detects logical inconsistencies within a session and across sessions, surfaces them gently | Makes every session genuinely Socratic — not just prompts, but real inquiry |
| **The Other Side** | Presents a counter-perspective to the user's stated position (requires AI connection) | Fellow traveller offering a different vantage point, not an adversary |
| **Three Ways to Look at This** | Presents three unlabelled framework perspectives on the same question (requires AI) | Draws from nine wisdom traditions without ever naming them |
| **Insight Extractor** | AI proposes a one-sentence summary of the session's key insight (requires AI) | Helps users consolidate learning without doing the articulation work |
| **Wisdom Library** | Stores saved insights, aphorisms, and past session summaries | A growing personal repository of wisdom, searchable and taggable |
| **One-Year Letters** | Write letters to your future self, sealed and time-locked | Longitudinal self-reflection with built-in anticipation |
| **Unsent Letters** | Write letters you'll never send — to people, to yourself, to situations | Therapeutic writing in a safe, private space |
| **Arc Sessions** | 7–10 day themed inquiry sequences (fear, money, choice, loss) | Deeper than one-off prompts, lighter than a course |
| **Vipassana Section** | Pre-sit orientation, hindrance tracker, post-sit integration questions | Bridges meditation practice and daily life |
| **Intensity Dial** | User-controlled depth: Gentle → Reflective → Deep → Confronting | Emotional safety without sacrificing depth for those who want it |
| **Domain Toggles** | User chooses which life domains are in play (Work, Relationships, Body, Belief, Money, Grief, Creativity) | Respects boundaries without requiring explanation |
| **Red Flag Detection** | On-device detection of acute distress language; shifts to grounding mode | Safety architecture that pauses challenge and suggests professional support |
| **Feedback Signal** | "Did that land?" — Yes / Not sure / Not today — after every session | Learning mechanism that improves framework routing over time |
| **Export/Import** | JSON vault export and import for data portability | The privacy promise made tangible — your data, your file, your control |

---

## What S&D Does NOT Do

- **Not therapy.** S&D is a thinking partner, not a clinician. It never diagnoses, never prescribes, never claims clinical authority.
- **Not a meditation app.** No guided meditations, no ambient sounds, no streaks, no gamification.
- **Not a journal.** It doesn't passively accept entries — it asks questions and challenges answers.
- **Not social.** No profiles, no followers, no likes, no comments. The optional anonymous commons is one-directional only.
- **Not cloud-dependent.** All data stays on device. No registration, no accounts, no server-side storage.
- **Not an AI product.** S&D works without AI. The curated question bank is the core. AI is an optional enhancement the user brings themselves.

---

## Delivery Modes

### 1. Open-Source Website (Primary Entry Point)
- Static site hosted on GitHub Pages
- Zero-friction access — no install, no registration
- Uses localStorage for data persistence
- All features except AI-powered ones work without any backend
- Progressive Web App (PWA) capable

### 2. Desktop Application (Full Experience)
- Electron wrapper connecting to Flask backend
- Available for Windows, macOS, and Linux
- File system storage (not localStorage) — data persists outside browser
- Native Ollama connection for local AI
- Native system tray integration
- SMS pipeline support via TextBee
- ELAINE morning briefing integration (AMTL internal only)

### 3. AMTL Internal (Ecosystem Integration)
- Registered in The Workshop
- Launched via Workshop or ELAINE voice command
- Port 5010
- Supervisor manages AI routing
- ELAINE integration for morning briefing question delivery

---

## Nine Wisdom Frameworks (Invisible)

S&D draws from nine psychological and philosophical traditions. The user never sees the framework name — they just notice the questions are unusually good.

1. **Shadow Work** — Surfacing what's hidden or denied
2. **Stoicism** — What's in your control vs what isn't
3. **Parts Work (IFS)** — Internal conflicts between different aspects of self
4. **Narrative Therapy** — The stories you tell about yourself and whether they're the only stories
5. **Logotherapy** — Meaning-finding, especially in suffering
6. **Byron Katie (The Work)** — "Is it true? Can you absolutely know it's true?"
7. **Clean Language** — Exploring metaphors without interpretation
8. **Immunity to Change** — Hidden commitments that block stated goals
9. **Appreciative Inquiry** — Strengths-based reflection

Framework selection is handled by the AI routing layer (when connected) or by curated question categorisation (default mode).

---

## Fellow Traveller Principle

S&D's voice is never authoritative. It is a fellow traveller — curious, gentle, occasionally challenging, but never superior.

**Language rules:**
- Never: Oracle, guru, sage, master, teacher, coach, advisor, guide
- Always: Fellow traveller, companion, thinking partner, "the other chair"
- Never: "You should...", "The answer is...", "Here's what I think..."
- Always: "What if...?", "You said X earlier — what's changed?", "I'm not sure either, but..."

---

## LLM Strategy — User Brings Their Own

**Default mode:** No AI. All questions are pre-written from the curated bank. Forced Silence, Contradiction Finder (rule-based), browser push — none need an LLM.

**Optional:** User connects their own AI in Settings:
- Ollama (local, free)
- Anthropic API key (Claude)
- OpenAI API key
- DeepSeek API key
- Any OpenAI-compatible endpoint

**Rules:**
- API connections go browser-direct (website) or local-direct (desktop) to the provider
- We never proxy, never see the key, never see prompts or responses
- Zero cost to AMTL for AI features

---

## Integration Points

| App | Integration | Direction |
|-----|------------|-----------|
| ELAINE | Morning briefing includes S&D daily question (themes only, not raw text) | S&D → ELAINE |
| The Workshop | Health monitoring, launch, status | Workshop → S&D |
| Supervisor | AI routing for Ollama-based inference (desktop mode) | S&D → Supervisor |
| Foreperson | Quality audit target | Foreperson → S&D |
| TextBee | SMS delivery of daily questions | S&D → TextBee |

---

## Port Assignment

| Environment | Port |
|-------------|------|
| Flask backend (desktop) | 5010 |
| Frontend dev server | 3010 |

---

## Configuration

Environment variables follow AMTL standard:

```
AMTL_SND_PORT=5010
AMTL_SND_SECRET_KEY=<generated>
AMTL_SND_DATA_DIR=~/.socrates-and-donuts/
AMTL_SND_SMS_ENABLED=false
AMTL_SND_TEXTBEE_API_KEY=<optional>
AMTL_SND_OLLAMA_URL=http://localhost:9000
AMTL_SND_LLM_PROVIDER=none  # none|ollama|anthropic|openai|deepseek|custom
AMTL_SND_LLM_API_KEY=<optional>
AMTL_SND_LLM_ENDPOINT=<optional, for custom providers>
```

---

## Personality

S&D has no persona, no avatar, no name for its "voice." It is not ELAINE. It is not an assistant. It is a quiet, typographic space that asks good questions. The closest metaphor is an empty chair across from you — present, attentive, but not performing.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 19 February 2026 | Claude (Thalaiva) | Initial specification — capabilities, delivery modes, frameworks, principles |

---

*Almost Magic Tech Lab*
*"Named after a philosopher who never wrote anything down and a pastry that asks nothing of you."*
