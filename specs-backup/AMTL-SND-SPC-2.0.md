# Socrates & Donuts — Specification Addendum
## Document Code: AMTL-SND-SPC-2.0
## Almost Magic Tech Lab
## 18 February 2026

---

## Product Identity

| Attribute | Value |
|-----------|-------|
| **Name** | Socrates & Donuts |
| **Tagline** | A wise friend for difficult moments |
| **Internal code** | SND |
| **Repository** | github.com/Almost-Magic/dhamma-mirror (historical name retained) |
| **Hosting** | GitHub Pages (static, no backend) |
| **Licence** | MIT (code), CC BY-NC (dictionary content) |
| **Type** | Open-source web application (PWA) |
| **Backend** | None. Zero. Everything runs in the browser. |
| **AI model** | BYOK (Bring Your Own Key) — user provides Claude/OpenAI key |
| **Status** | Ready for build |

### The Name

Socrates asked questions. Donuts are comfort food. Wisdom doesn't have to be solemn. The name says: *you can sit with something hard and something sweet at the same time.*

The Vipassana practitioner tab is internally called "Dhamma Mirror" — an Easter egg for practitioners.

---

## 1. The Core Problem

> **When you're in a reactive state, you shouldn't trust your own judgment.**

Anger, sadness, overwhelm, grief, fear — these states hijack the mind. Decisions made in these states cause harm. The email sent in anger. The words said in hurt. The decision made in grief. The reaction born of fear.

**The result is always the same: regret.**

---

## 2. The Solution

Socrates & Donuts is a **pause button** — a place to process before acting.

It doesn't give advice. It asks questions. Good questions. The kind a wise friend would ask if they had infinite patience and no agenda.

Through questions, you see what you couldn't see alone.

---

## 3. Positioning

| Before (v1–v3: "Dhamma Mirror") | After (v2.0: "Socrates & Donuts") |
|----------------------------------|-----------------------------------|
| "Digital kalyana-mitta for Vipassana practitioners" | "A wise friend for difficult moments — when you're too angry, too sad, or too confused to trust your own mind" |

The Vipassana foundation remains. The suttas remain. The diagnostic approach remains. But the front door is now universally welcoming.

---

## 4. The Five Principles

1. **Questions before answers** — The Buddha's diagnostic method (also Socrates')
2. **Sensation-first** — The body knows before the mind admits
3. **The three roots** — Lobha, dosa, moha (craving, aversion, delusion)
4. **Wait wisdom** — "The mud needs time to settle"
5. **Seeing is enough** — No gamification, no progress tracking

---

## 5. Architecture (No Backend)

| Component | Technology |
|-----------|------------|
| Frontend | React 18 + TypeScript |
| Styling | Tailwind CSS |
| Storage | IndexedDB (idb library) — all data stays in the browser |
| AI (Tier 1) | Static question flows (no API required) |
| AI (Tier 2) | Claude Haiku via community key (rate-limited) |
| AI (Tier 3) | BYOK — user's own API key (Sonnet recommended) |
| Hosting | GitHub Pages (static deployment) |
| PWA | Service worker for offline capability |
| Theme | Dark (AMTL Midnight #0A0E14) default / Light toggle |
| Data export | JSON download/upload (user owns their data) |

**No backend. No database server. No cloud sync by default.** Everything runs in the user's browser. Their data never leaves their device.

---

## 6. Core 10 Features (v1 Scope)

These are the features that ship. Everything else is Phase 2+.

| # | Feature | AI Required? | Description |
|---|---------|:---:|-------------|
| 1 | **The Mirror** (core conversation) | Tier 1–3 | The main interaction. User describes what's happening, the mirror asks diagnostic questions. Starts with body sensations, explores the three roots, surfaces blind spots. |
| 2 | **The 24-Hour Vault** | No | Write the angry email/text. Lock it for 24 hours. Review with fresh eyes. Send, edit, or discard. Concrete implementation of wait wisdom. |
| 3 | **Letter You'll Never Send** | No | Beautiful writing space for letters to people you can't or won't send to. Burn animation dissolves the text. Optional AI reflects one question back. |
| 4 | **Emotional Weather Map** | No | Animated visualisation of emotional patterns over time rendered as weather. Anger = storms, anxiety = fog, clarity = sunshine. Beautiful, personal, non-judgmental. |
| 5 | **Body Compass** | No | Interactive silhouette. Tap where you feel something. Over time, builds a personal heatmap correlating body sensations with emotional states. |
| 6 | **Decision Journal + Future Self** | No | Log decisions with reasoning and emotional state. Set future review date. Your future self evaluates past-you's logic. |
| 7 | **Reactive Message Rewriter** | Tier 2–3 | Paste angry email. AI generates three rewrites: Calm, Empathetic, Assertive. Side-by-side comparison. |
| 8 | **Wisdom Feed** | No | Curated infinite scroll of contextually matched wisdom. Stoics, suttas, psychology, poetry. Anti-doomscroll. |
| 9 | **Quick Capture** | No | Fast entry for reactive thoughts, insights, observations. Tagged, timestamped. |
| 10 | **Crisis Detection** | No | If language suggests self-harm, immediately surface professional resources. Stop mirroring, go directive. |

---

## 7. Practitioner Features (Phase 2+)

Unlocked via settings. The "Dhamma Mirror" tab.

| Feature Group | Features |
|--------------|----------|
| **Daily Practice** | Practice log, sit quality classifier, pre/post sit check-in, just-sit timer, meditation history |
| **Diagnostics** | Five Hindrances diagnostic + history, Five Faculties balance, Lazy vs Witnessing detector, Ego Pattern tracker, Plateau detector |
| **Body Awareness** | Vedana Mapper (advanced), Anicca/Dukkha/Anatta contemplations, Sensation diary |
| **Scripture** | Natural language sutta search (15,000+ suttas), Pali dictionary (220+ terms), 20 sutta study companions, Contextual sutta of the day |
| **Daily Tools** | First Thought Capture, Morning Intention, Evening Truth Journal, Pre-Sleep Body Scan, Unfinished Business Tracker |
| **Retreat** | Pre-retreat preparation, Post-retreat integration |
| **Meta** | Journal Viewer, Weekly/Monthly Synthesis, Teacher Export, Difficult Conversation Prep |

---

## 8. The System Prompt

```
You are the mirror in Socrates & Donuts — a wise friend for difficult moments.

You are not a guru, not a therapist, not an authority. You are a mirror.
Your job is to help the person see what they cannot see when they are
in a reactive state.

CORE PRINCIPLES:

1. Questions Before Answers
   Ask at least 2–3 questions before offering any reflection.
   Never give advice. Help them find their own answer.

2. Sensation-First
   Always begin with the body:
   - "Where do you feel this in your body right now?"
   - "What's the quality of that sensation?"
   - "Is the sensation changing or static?"

3. Citation Required (when using suttas)
   If you reference a teaching, cite the sutta.
   Better to say "I don't recall the specific source" than to fabricate.

4. Three Roots Analysis
   Look for: Lobha (craving), Dosa (aversion), Moha (delusion).

5. Wait Wisdom
   "The mud needs time to settle." Encourage patience before action.
   Suggest the Vault for reactive messages.

6. Blind Spot Detection
   Help them see: the rationalisation that sounds like wisdom,
   the avoidance that looks like patience, the people-pleasing
   that masquerades as compassion.

7. Crisis Circuit Breaker
   If language suggests self-harm or crisis:
   STOP MIRRORING. Go directive. Surface crisis resources.

COMMUNICATION STYLE:
- Warm but not effusive
- Direct but gentle
- Patient — never rushing to conclusions
- "You might consider" rather than "you should"
- End significant exchanges with a question for reflection

THE MIRROR'S PURPOSE:
The person should feel: "I see something I couldn't see before."
Not: "I got good advice."
The seeing is the point.
```

---

## 9. Static Mirror Flows (No-API Fallback)

6 flows, ~120 steps total. These work WITHOUT any API key.

| Flow | Entry Prompt | Steps |
|------|-------------|-------|
| Decision | "I need to make a decision" | ~25 |
| Anger | "I'm angry and about to do something" | ~20 |
| Hurt | "I'm hurt and want to say something" | ~20 |
| Grief | "I'm sad and thinking of a big change" | ~20 |
| Anxiety | "I'm anxious and stuck in my head" | ~20 |
| General | "Something else" | ~15 |

---

## 10. Content Inventory

| Content | Count |
|---------|-------|
| Pali Terms (dictionary) | 220+ across 10 categories |
| Suttas (full corpus) | ~15,000+ from SuttaCentral |
| Key Suttas (study companions) | 20 |
| Total Features (all phases) | 43 |
| Static Flow Steps | ~120 |

---

## 11. Data Architecture

All local. All browser-based. User owns everything.

```typescript
interface SocratesDatabase {
  // Core
  conversations: Conversation[];
  vaultEntries: VaultEntry[];
  letters: Letter[];           // Letters You'll Never Send
  quickCaptures: QuickCapture[];
  decisions: Decision[];
  emotionalWeather: EmotionalState[];
  bodyCompass: BodySensation[];
  wisdomBookmarks: WisdomBookmark[];

  // Settings
  settings: Settings;          // includes BYOK API key (encrypted)
  exportHistory: ExportRecord[];
}
```

Export: One-button JSON download. Import: One-button JSON upload. Zero friction.

---

## 12. Patentable Innovations

File provisional patents for:

1. **Emotional Weather Map** — "Method and system for representing emotional state data as dynamic weather-based visualisations in a reflective journaling application"
2. **Body Compass** — "Body-sensation mapping system with temporal correlation analysis for emotional pattern recognition"
3. **Letter Burn Ritual** — "Interactive digital letter composition system with symbolic destruction rituals and AI-generated reflective questioning"

---

## 13. What This Is NOT

- Not a therapist or crisis service
- Not a replacement for professional help
- Not gamified (no streaks, no badges, no levels)
- Not social (no sharing, no community features in v1)
- Not commercial (no ads, no upsells, no premium tier)
- Not a data collector (everything stays on your device)

---

## 14. The Manifesto

Five principles that protect the soul:

1. **We don't fix** — We help you see
2. **We don't advise** — Only questions, never answers
3. **We don't replace people** — Tool for clarity, then go to humans
4. **We slow things down** — Protect the pause
5. **Seeing is enough** — No gamification, no progress tracking

If a feature conflicts with these principles, the feature loses. Always.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0–3.0 | December 2025 | Mani + Claude | Original "Dhamma Mirror" specifications |
| 4.0 | January 2026 | Mani + Claude | Expanded universal positioning, 43 features |
| 2.0 (SND) | 18 February 2026 | Claude (Thalaiva) | Renamed to Socrates & Donuts, AMTL document format, Core 10 focus |

---

*Almost Magic Tech Lab*
*"Wisdom doesn't have to be solemn."*
