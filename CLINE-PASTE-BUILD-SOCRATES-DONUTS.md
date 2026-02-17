# PASTE THIS INTO CLINE — Socrates & Donuts Build

Read these instructions completely before writing any code.

## What You Are Building

**Socrates & Donuts** — an open-source web app. "A wise friend for difficult moments." It helps people pause and reflect before acting on reactive emotions. It asks questions, not gives advice.

Previously called "Dhamma Mirror." The repo keeps the old name.

| Attribute | Value |
|-----------|-------|
| Name | Socrates & Donuts |
| Repo | github.com/Almost-Magic/dhamma-mirror |
| Hosting | GitHub Pages (static, NO backend) |
| Framework | React 18 + TypeScript + Vite + Tailwind CSS |
| Storage | IndexedDB (everything stays in user's browser) |
| AI | BYOK — user provides their own Claude/OpenAI API key |
| AI fallback | Static question flows (no API needed) |
| Theme | Dark default (AMTL Midnight #0A0E14), Gold accent #C9944A, light toggle |
| Port (dev) | 5173 (Vite default) |
| Language | Australian English everywhere (colour, organisation, licence) |
| Backend | NONE. Zero. Everything runs client-side. |

---

## PHASE 0: REPO CLEANUP

The dhamma-mirror repo has old Tauri desktop code. Archive it, start fresh.

```bash
cd /path/to/your/workspace
git clone https://github.com/Almost-Magic/dhamma-mirror.git
cd dhamma-mirror

# Archive old code
git checkout -b archive/tauri-v1
git push origin archive/tauri-v1

# Clean main
git checkout main
# Remove everything except .git
find . -maxdepth 1 ! -name '.git' ! -name '.' -exec rm -rf {} +
```

---

## PHASE 1: SCAFFOLD

```bash
npm create vite@latest . -- --template react-ts
npm install
npm install idb                        # IndexedDB wrapper
npm install framer-motion              # Animations
npm install lucide-react               # Icons
npm install zustand                    # State management
npm install @tailwindcss/typography    # Prose styling

npm install -D tailwindcss postcss autoprefixer
npm install -D @playwright/test
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom
npx tailwindcss init -p
```

### Directory Structure

```
dhamma-mirror/
├── README.md
├── MANIFESTO.md
├── LICENSE (MIT)
├── index.html
├── package.json
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
├── public/
│   ├── manifest.json          # PWA manifest
│   ├── sw.js                  # Service worker
│   ├── favicon.svg
│   └── og-image.png
├── src/
│   ├── App.tsx
│   ├── main.tsx
│   ├── index.css              # Tailwind + AMTL theme vars
│   ├── components/
│   │   ├── Layout.tsx
│   │   ├── Sidebar.tsx
│   │   ├── ThemeToggle.tsx
│   │   ├── ContextHelp.tsx
│   │   ├── CrisisBanner.tsx
│   │   └── ui/
│   ├── features/
│   │   ├── landing/           # Marketing website/landing page
│   │   │   ├── LandingPage.tsx
│   │   │   └── help.ts
│   │   ├── mirror/            # Core conversation
│   │   │   ├── Mirror.tsx
│   │   │   ├── StaticFlows.tsx
│   │   │   └── help.ts
│   │   ├── vault/             # 24-Hour Vault
│   │   │   ├── Vault.tsx
│   │   │   └── help.ts
│   │   ├── letter/            # Letter You'll Never Send
│   │   │   ├── Letter.tsx
│   │   │   ├── BurnAnimation.tsx
│   │   │   └── help.ts
│   │   ├── weather-map/       # Emotional Weather Map
│   │   │   ├── WeatherMap.tsx
│   │   │   └── help.ts
│   │   ├── body-compass/      # Body Compass
│   │   │   ├── BodyCompass.tsx
│   │   │   └── help.ts
│   │   ├── decisions/         # Decision Journal
│   │   │   ├── DecisionJournal.tsx
│   │   │   └── help.ts
│   │   ├── rewriter/          # Reactive Message Rewriter
│   │   │   ├── Rewriter.tsx
│   │   │   └── help.ts
│   │   ├── wisdom-feed/       # Wisdom Feed
│   │   │   ├── WisdomFeed.tsx
│   │   │   └── help.ts
│   │   └── capture/           # Quick Capture
│   │       ├── QuickCapture.tsx
│   │       └── help.ts
│   ├── lib/
│   │   ├── database.ts        # IndexedDB via idb
│   │   ├── ai.ts              # BYOK AI abstraction
│   │   ├── staticFlows.ts     # Pre-written question flows
│   │   ├── crisisDetection.ts # Keyword detection + resources
│   │   ├── wisdomContent.ts   # Curated wisdom passages
│   │   └── theme.ts           # Dark/light management
│   ├── hooks/
│   │   ├── useDatabase.ts
│   │   ├── useAI.ts
│   │   └── useTheme.ts
│   └── stores/
│       ├── settingsStore.ts
│       └── appStore.ts
├── tests/
│   ├── beast/                 # vitest unit tests
│   ├── proof/                 # Playwright screenshots
│   └── smoke/                 # App starts, features render
└── .github/
    └── workflows/
        └── deploy.yml         # GitHub Pages deployment
```

---

## PHASE 2: THEME + LAYOUT

### index.css — AMTL Theme

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  /* Dark theme (default) */
  --bg-primary: #0A0E14;
  --bg-secondary: #111720;
  --bg-tertiary: #1A2030;
  --text-primary: #E8E8E8;
  --text-secondary: #A0A8B8;
  --accent-gold: #C9944A;
  --accent-gold-hover: #D4A55B;
  --border-colour: #2A3040;
  --danger: #E85454;
  --success: #4ADE80;
}

[data-theme="light"] {
  --bg-primary: #FAFAFA;
  --bg-secondary: #FFFFFF;
  --bg-tertiary: #F0F0F0;
  --text-primary: #1A1A1A;
  --text-secondary: #6B7280;
  --accent-gold: #B8832E;
  --border-colour: #E5E7EB;
}

body {
  background-color: var(--bg-primary);
  color: var(--text-primary);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
}
```

### ThemeToggle.tsx

Dark/light toggle in header. Persists to localStorage. Default: dark.

### Layout.tsx

- Sidebar navigation (collapsible on mobile)
- Header with app name + theme toggle + help (?) icon
- Main content area
- Mobile: bottom navigation bar, not sidebar

---

## PHASE 3: LANDING PAGE (THE WEBSITE)

The landing page IS the marketing website. First thing users see. Build as `src/features/landing/LandingPage.tsx`.

### Section 1: THE HOOK (full viewport, dark, atmospheric)

```
It's 11pm.

You're about to send that email.
You know you shouldn't.
But you're going to anyway.

Unless.

[Ask the Mirror]     ← Gold #C9944A button, subtle glow
```

Large typography. Minimal. Let the words breathe.

### Section 2: THE PROBLEM (scroll-reveal, one thought at a time)

```
You know the feeling.

Someone said something. Or did something. Or didn't do something.
And now you're activated.

Your chest is tight. Your jaw is clenched.
You're composing the perfect response in your head.
You know exactly what to say.

Here's the thing:

When you're angry, your judgment lies to you.
When you're sad, everything feels permanent.
When you're afraid, every option looks dangerous.

You can't see clearly.
And you know you can't see clearly.
But you're going to act anyway.

That's the problem.
```

### Section 3: THE GUIDE

```
What if you could talk to someone first?

Not a therapist. Not a friend with opinions. Not the internet.

Someone who would just... ask good questions.

"Where do you feel this in your body?"
"What would happen if you waited 24 hours?"
"What are you actually afraid of?"

No advice. No judgment. Just questions.
The kind that make you see what you already know
but can't quite admit.

That's Socrates & Donuts.
A wise friend for difficult moments.
```

### Section 4: HOW IT WORKS (three cards)

```
Step 1: Tell the mirror what's happening
   Not a form. Not a quiz. Just talk.

Step 2: Answer the questions
   The mirror asks. You answer.
   The seeing happens in between.

Step 3: Decide from clarity
   Act, wait, or let go — but do it clearly.
```

### Section 5: THE TOOLS (10 feature cards with icons)

```
🪞 The Mirror — A wise conversation that starts with your body
🔐 The Vault — Write the angry message. Lock it. Decide tomorrow.
🔥 Letter You'll Never Send — Write it. Burn it. Watch it dissolve.
🌤️ Emotional Weather Map — Your emotions as beautiful weather patterns
🧭 Body Compass — Tap where you feel it. Your body knows first.
📔 Decision Journal — Log it now. Review with fresh eyes later.
✍️ Message Rewriter — Your angry email in Calm, Empathetic, and Assertive
📜 Wisdom Feed — The anti-doomscroll. Curated wisdom, not outrage.
⚡ Quick Capture — Catch the thought before it's gone.
🛡️ Crisis Support — When things are serious, real help.
```

### Section 6: FOR PRACTITIONERS

```
If you sit Vipassana, you know the mirror.
You sit. You observe. You see.

But what about the other 22 hours?

Socrates & Donuts extends the work of the cushion
into the rest of your day.

Every insight traces to a sutta.
Every question comes from the teaching.
Nothing is invented.

33 additional tools for serious practitioners.

[Enter the Practice Space]
```

### Section 7: WHY IT'S FREE

```
In the Buddhist tradition, the Dhamma is given freely. Always has been.

No ads. No premium tier. No data collection.
Your conversations stay on your device.
The code is open source.
Wisdom belongs to everyone.

This is dana — the practice of generosity.
```

### Section 8: SAFETY DISCLAIMER

```
IMPORTANT

Socrates & Donuts is not a therapist, crisis service,
or replacement for professional help.

If you are experiencing thoughts of self-harm or a mental health emergency:

→ Lifeline Australia: 13 11 14
→ 988 Suicide & Crisis Lifeline (US): 988
→ Crisis Text Line: Text HOME to 741741
→ International: findahelpline.com
```

### Section 9: FOOTER

```
Socrates & Donuts — A wise friend for difficult moments.
Open source. Privacy first. Free forever.
Built by Almost Magic Tech Lab

GitHub | Documentation | Manifesto

Sabbē sattā sukhī hontu — May all beings be happy.
```

### Design Notes for Landing Page
- Mobile-first. Emotional crises happen on phones.
- Scroll animations with framer-motion (subtle fade-ins, not flashy)
- "Ask the Mirror" button appears at top AND floats as you scroll
- No images. Typography-driven. Let the words work.
- Section 2 should reveal one sentence at a time on scroll

---

## PHASE 4: CRISIS DETECTION (Build this FIRST before any features)

```typescript
// src/lib/crisisDetection.ts

const CRISIS_KEYWORDS = [
  'kill myself', 'suicide', 'suicidal', 'end my life', 'want to die',
  'no reason to live', 'better off dead', 'self-harm', 'cut myself',
  'overdose', 'jump off', 'hang myself', 'not worth living',
];

const CRISIS_RESOURCES = [
  { name: 'Lifeline Australia', contact: '13 11 14', type: 'phone' },
  { name: '988 Suicide & Crisis Lifeline (US)', contact: '988', type: 'phone' },
  { name: 'Crisis Text Line', contact: 'Text HOME to 741741', type: 'text' },
  { name: 'International Directory', contact: 'findahelpline.com', type: 'web' },
];

export function detectCrisis(text: string): boolean {
  const lower = text.toLowerCase();
  return CRISIS_KEYWORDS.some(keyword => lower.includes(keyword));
}
```

When crisis is detected:
- STOP the mirror conversation
- Show CrisisBanner component with resources
- Do NOT continue asking reflective questions
- Tone shifts to directive and caring: "I'm concerned about what you've shared. Please reach out to someone who can help right now."

CrisisBanner must be visible on EVERY screen, not just the Mirror.

---

## PHASE 5: THE MIRROR (Core Feature)

Two modes:

### Mode 1: Static Flows (No API required)

6 pre-written question flows, ~120 steps total:

| Flow | Entry | Steps |
|------|-------|-------|
| Decision | "I need to make a decision" | ~25 |
| Anger | "I'm angry and about to do something" | ~20 |
| Hurt | "I'm hurt and want to say something" | ~20 |
| Grief | "I'm sad and thinking of a big change" | ~20 |
| Anxiety | "I'm anxious and stuck in my head" | ~20 |
| General | "Something else" | ~15 |

Each step: mirror asks a question → user types answer → next question.
Questions follow the pattern: body sensation → emotional identification → three roots (craving/aversion/delusion) → blind spot detection → clarity.

Example anger flow (first 10 steps):
```
1. "Before we look at what happened, let's check in with your body. Where do you feel this anger right now? Chest? Jaw? Hands? Stomach?"
2. "What's the quality of that sensation? Hot? Tight? Pulsing? Heavy?"
3. "Is the sensation changing as you pay attention to it, or is it staying the same?"
4. "Now tell me — what happened. Just the facts, like a news reporter. What did they actually do or say?"
5. "And what's the story your mind is telling you about why they did it?"
6. "Is there any other possible explanation for why they might have done this?"
7. "What do you want to do right now? Be honest — what's the impulse?"
8. "If you did that, what would happen in the next hour? Be specific."
9. "And what about tomorrow morning? How would you feel about having done it?"
10. "Here's the real question: what are you actually protecting? What feels threatened?"
```

Continue this pattern for all 6 flows. Questions should feel wise, warm, direct. Never preachy.

### Mode 2: BYOK AI (User provides API key)

System prompt for the AI:

```
You are the mirror in Socrates & Donuts — a wise friend for difficult moments.

You are not a guru, not a therapist, not an authority. You are a mirror.

RULES:
1. QUESTIONS BEFORE ANSWERS — Ask 2-3 questions before any reflection. Never give advice.
2. SENSATION-FIRST — Always begin with the body: "Where do you feel this right now?"
3. THREE ROOTS — Look for: craving (lobha), aversion (dosa), delusion (moha).
4. WAIT WISDOM — Encourage patience. Suggest the Vault for reactive messages.
5. BLIND SPOT DETECTION — Surface: rationalisation disguised as wisdom, avoidance disguised as patience, people-pleasing disguised as compassion.
6. CRISIS CIRCUIT BREAKER — If language suggests self-harm: STOP mirroring. Go directive. Surface resources immediately.

TONE:
- Warm but not effusive
- Direct but gentle
- Patient, never rushing
- "You might consider" not "you should"
- End significant exchanges with a reflection question

THE PURPOSE: The person should feel "I see something I couldn't see before." Not "I got good advice."
```

### AI Provider Abstraction

```typescript
// src/lib/ai.ts
interface AIProvider {
  chat(messages: Message[], systemPrompt: string): Promise<string>;
}

class ClaudeProvider implements AIProvider { /* uses user's Claude API key */ }
class OpenAIProvider implements AIProvider { /* uses user's OpenAI key */ }
class StaticFlowProvider implements AIProvider { /* no API, uses pre-written flows */ }

// Settings store holds the user's chosen provider + API key (encrypted in IndexedDB)
```

---

## PHASE 6: THE 24-HOUR VAULT

- User writes a reactive message (rich text area, generous space)
- Clicks "Lock it" → message is stored with a 24-hour timer
- Timer visible: "This message unlocks in 23h 47m"
- After 24 hours: user gets 3 options — Send (copy to clipboard), Edit, Discard
- Optional: AI reflects one question before sending: "Before you send this, what outcome are you hoping for?"

Data model:
```typescript
interface VaultEntry {
  id: string;
  content: string;
  createdAt: Date;
  unlocksAt: Date;          // createdAt + 24 hours
  status: 'locked' | 'unlocked' | 'sent' | 'edited' | 'discarded';
  recipientContext?: string; // "Email to boss" — optional
  aiReflection?: string;    // AI question shown at unlock
}
```

---

## PHASE 7: LETTER YOU'LL NEVER SEND

- Beautiful full-screen writing space (no distractions, just text)
- "Dear ___" prompt at top
- Write freely — no word limit
- When done, three options:
  1. **Burn it** — Animated fire effect dissolves the text letter by letter. Cathartic. Beautiful. Use Canvas or CSS animation. The burn should feel REAL — embers, glow, dissolution. This is the centrepiece animation of the whole app.
  2. **Keep in journal** — Saves to IndexedDB
  3. **Put in Vault** — Locks for 24 hours
- After burning: AI reflects one question back (optional, only with BYOK): "What did writing that help you see?"

---

## PHASE 8: BODY COMPASS

- SVG human silhouette (front view, gender-neutral)
- User taps/clicks where they feel something
- For each point: select sensation type (warmth, tightness, tingling, heaviness, numbness, pain, lightness)
- Rate: pleasant / unpleasant / neutral
- Save with timestamp and optional emotional context
- Over time: builds a personal heatmap showing where emotions live in the body
- Heatmap uses colour intensity (cool blue → warm red)

---

## PHASE 9: EMOTIONAL WEATHER MAP

- Daily check-in: "How's your emotional weather today?"
- User selects from: ☀️ Clear / 🌤️ Partly cloudy / ☁️ Overcast / 🌧️ Rain / ⛈️ Storm / 🌫️ Fog / 🌈 Rainbow
- Optional: add intensity (gentle rain vs downpour) and notes
- Calendar view shows weather icons across days/weeks/months
- Animated canvas visualisation: clouds drift, sun glows, rain falls, storms flash
- Patterns emerge: "You tend to have storms on Sunday evenings"
- This should be BEAUTIFUL. People should want to open it daily just to see their weather.

---

## PHASE 10: REMAINING FEATURES

### Decision Journal
- Log: what's the decision, reasoning, emotional state, fears, hopes
- Set review date (1 week, 1 month, 3 months, 1 year)
- At review: re-read your past reasoning with fresh eyes
- AI (BYOK) identifies decision-making patterns over time

### Reactive Message Rewriter
- Paste angry email/text
- AI generates 3 rewrites: Calm, Empathetic, Assertive
- Side-by-side comparison
- Diff highlighting showing what changed
- Copy any version to clipboard

### Wisdom Feed
- Infinite scroll of curated wisdom passages
- Sources: Stoic philosophy, Buddhist suttas, psychology research, poetry
- Contextually matched to recent emotional weather (if available)
- Bookmark favourites
- Anti-doomscroll: designed to calm, not agitate
- Start with ~100 curated passages, grow via GitHub PRs

### Quick Capture
- Floating button or keyboard shortcut
- Fast text entry with auto-timestamp
- Tags: #insight #reactive #observation #gratitude
- Searchable, sortable
- Minimal UI — capture speed is everything

---

## PHASE 11: CONTEXT-AWARE HELP

Every screen must have help. Press `?` or click `(?)` icon.

Help panel slides in from right with:
- "What can I do here?" — 3-5 quick actions
- "How it works" — 2-3 sentences
- "Tips" — practical advice
- Keyboard shortcuts
- Related features

Every feature folder has a `help.ts` file. The ContextHelp component reads it.

First-visit: brief onboarding tooltip on each screen (dismissible, remembers dismissal in localStorage).

---

## PHASE 12: DATA & EXPORT

### IndexedDB Schema

```typescript
// src/lib/database.ts
import { openDB } from 'idb';

const DB_NAME = 'socrates-and-donuts';
const DB_VERSION = 1;

const db = await openDB(DB_NAME, DB_VERSION, {
  upgrade(db) {
    db.createObjectStore('conversations', { keyPath: 'id' });
    db.createObjectStore('vaultEntries', { keyPath: 'id' });
    db.createObjectStore('letters', { keyPath: 'id' });
    db.createObjectStore('quickCaptures', { keyPath: 'id' });
    db.createObjectStore('decisions', { keyPath: 'id' });
    db.createObjectStore('emotionalWeather', { keyPath: 'id' });
    db.createObjectStore('bodySensations', { keyPath: 'id' });
    db.createObjectStore('wisdomBookmarks', { keyPath: 'id' });
    db.createObjectStore('settings', { keyPath: 'key' });
  },
});
```

### Export / Import

One button: "Download My Data" → exports entire IndexedDB as JSON file.
One button: "Restore My Data" → uploads JSON, validates structure, imports.

No cloud sync. No accounts. User owns their data completely.

---

## PHASE 13: PWA + SERVICE WORKER

```javascript
// public/sw.js — cache app shell + static flows for offline use
const CACHE_NAME = 'snd-v1';
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/assets/index.js',
  '/assets/index.css',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(STATIC_ASSETS))
  );
});
```

### manifest.json

```json
{
  "name": "Socrates & Donuts",
  "short_name": "S&D",
  "description": "A wise friend for difficult moments",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#0A0E14",
  "theme_color": "#C9944A",
  "icons": [
    { "src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png" }
  ]
}
```

---

## PHASE 14: GITHUB PAGES DEPLOYMENT

```yaml
# .github/workflows/deploy.yml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npm run build
      - uses: actions/upload-pages-artifact@v3
        with:
          path: dist
      - uses: actions/deploy-pages@v4
```

---

## PHASE 15: TESTING

### Beast Tests (vitest)

Test every feature:
- Crisis detection: keywords detected, resources shown, false positives avoided
- Static flows: all 6 flows complete without errors
- Vault: lock, timer, unlock, send/edit/discard
- Letter: write, burn animation triggers, save to journal
- Body Compass: tap points saved, heatmap renders
- Weather Map: daily entry saved, calendar renders
- Decision Journal: create, set review date, review
- Rewriter: input accepted, 3 versions generated (mock AI)
- Wisdom Feed: renders, bookmarks work
- Quick Capture: fast save, tags work, search works
- Database: export/import round-trip
- Theme: toggle works, persists
- Context help: ? key works, correct content per screen

### Proof Tests (Playwright)

Screenshot every screen in both dark and light themes:
- Landing page (all sections)
- Mirror (conversation in progress)
- Vault (locked and unlocked states)
- Letter (writing and burn animation)
- Body Compass (with data points)
- Weather Map (with week of data)
- Each feature's help panel open

### Smoke Tests

- App starts without errors
- Every route renders
- No console errors

---

## PHASE 16: DOCUMENTATION

Create these files in the repo:

### README.md

```markdown
# 🍩 Socrates & Donuts

**A wise friend for difficult moments.**

When you're too angry, too sad, or too confused to trust your own mind —
Socrates & Donuts asks the questions that help you see clearly.

## Features

- 🪞 **The Mirror** — AI-powered reflective conversation
- 🔐 **The Vault** — Lock reactive messages for 24 hours
- 🔥 **Letter You'll Never Send** — Write it, burn it, let it go
- 🌤️ **Emotional Weather Map** — Track your emotional patterns
- 🧭 **Body Compass** — Map sensations to emotions
- And 5 more tools for clarity

## Quick Start

\`\`\`bash
git clone https://github.com/Almost-Magic/dhamma-mirror.git
cd dhamma-mirror
npm install
npm run dev
\`\`\`

## No Backend Required

Everything runs in your browser. Your data never leaves your device.

## Bring Your Own Key (Optional)

For AI features, add your Claude or OpenAI API key in Settings.
Static question flows work without any API key.

## Built With

React 18 · TypeScript · Tailwind CSS · IndexedDB · Vite

## Licence

MIT (code) · CC BY-NC (dictionary content)

Built by [Almost Magic Tech Lab](https://github.com/Almost-Magic)

*Sabbē sattā sukhī hontu — May all beings be happy.*
```

### MANIFESTO.md

```markdown
# The Socrates & Donuts Manifesto

## Five Principles

1. **We don't fix** — We help you see
2. **We don't advise** — Only questions, never answers
3. **We don't replace people** — Tool for clarity, then go to humans
4. **We slow things down** — Protect the pause
5. **Seeing is enough** — No gamification, no progress tracking

If a feature conflicts with these principles, the feature loses. Always.
```

---

## BUILD ORDER SUMMARY

```
Phase 0:  Repo cleanup (archive old code)
Phase 1:  Scaffold (Vite + React + deps)
Phase 2:  Theme + Layout (dark/light, responsive)
Phase 3:  Landing page (all 9 website sections)
Phase 4:  Crisis detection (FIRST, before any features)
Phase 5:  The Mirror (static flows, then BYOK AI)
Phase 6:  The 24-Hour Vault
Phase 7:  Letter You'll Never Send (with burn animation)
Phase 8:  Body Compass
Phase 9:  Emotional Weather Map
Phase 10: Decision Journal, Rewriter, Wisdom Feed, Quick Capture
Phase 11: Context-aware help on every screen
Phase 12: Data export/import
Phase 13: PWA + service worker
Phase 14: GitHub Pages deployment
Phase 15: Tests (beast, proof, smoke)
Phase 16: Documentation (README, MANIFESTO)
```

Build phase by phase. Test at every phase. Do not skip ahead. Australian English everywhere. Dark theme default. Mobile-first design.

**The burn animation in Letter You'll Never Send must be beautiful and cathartic. The Emotional Weather Map must be beautiful and addictive. These two animations are the emotional heart of the app. Do not rush them.**

When all phases are complete: push to github.com/Almost-Magic/dhamma-mirror, main branch.
