# GURUVE INSTRUCTION #002: BUILD SOCRATES & DONUTS
## Priority: After ELAINE
## Almost Magic Tech Lab
## 18 February 2026

---

## Who You Are

You are **Guruve** — Claude Desktop agent. You build what Thalaiva designs.

---

## What You Are Building

**Socrates & Donuts** — An open-source web application. A wise friend for difficult moments. Hosted on GitHub Pages. No backend. Everything in the browser.

| Attribute | Value |
|-----------|-------|
| Name | Socrates & Donuts |
| Repository | github.com/Almost-Magic/dhamma-mirror (keep historical repo name) |
| Hosting | GitHub Pages |
| Backend | NONE |
| Framework | React 18 + TypeScript + Tailwind CSS |
| AI | BYOK (user provides their own API key) + static flows |

---

## PHASE 0: REPOSITORY CLEANUP

The `dhamma-mirror` repo currently contains old Tauri desktop app code. We are starting fresh but keeping the repo.

```powershell
# Clone existing repo
cd C:\Users\mani.padisetti
git clone https://github.com/Almost-Magic/dhamma-mirror.git
cd dhamma-mirror

# Create a backup branch of old code
git checkout -b archive/tauri-v1
git push origin archive/tauri-v1

# Switch back to main and clean everything
git checkout main

# Delete all existing files except .git
Get-ChildItem -Exclude .git | Remove-Item -Recurse -Force

# Confirm clean
dir
# Should only show .git folder
```

**Do NOT delete the repo or create a new one. The repo history is preserved in the archive branch.**

---

## PHASE 1: PROJECT SCAFFOLDING

```powershell
# Still in C:\Users\mani.padisetti\dhamma-mirror

# Create React app with Vite
npm create vite@latest . -- --template react-ts

# Install dependencies
npm install
npm install idb                    # IndexedDB wrapper
npm install framer-motion          # Animations (weather map, burn ritual)
npm install lucide-react           # Icons
npm install @tailwindcss/typography # Prose styling
npm install zustand                # State management (lightweight)

# Dev dependencies
npm install -D tailwindcss postcss autoprefixer
npm install -D @playwright/test    # Proof tests
npm install -D vitest @testing-library/react # Beast tests
npx tailwindcss init -p

# Create directory structure
```

### Directory Structure

```
dhamma-mirror/
├── README.md
├── MANIFESTO.md
├── CONTRIBUTING.md
├── ATTRIBUTION.md
├── LICENSE
├── index.html
├── package.json
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
│
├── docs/
│   ├── AMTL-SND-SPC-2.0.md          # Specification
│   ├── AMTL-SND-TDD-1.0.md          # Technical Design
│   ├── AMTL-SND-BLD-1.0.md          # Build Guide
│   ├── AMTL-SND-DEC-1.0.md          # Decision Register
│   ├── AMTL-SND-RUN-1.0.md          # Operations Runbook
│   ├── AMTL-SND-USR-1.0.md          # User Manual
│   ├── AMTL-SND-DGN-1.0.md          # Diagnostic Playbook
│   ├── AMTL-SND-KNW-1.0.md          # Known Issues
│   ├── AMTL-SND-MRD-1.0.yaml        # Machine-Readable Diagnostics
│   ├── SYSTEM_PROMPT.md
│   ├── PALI_DICTIONARY.md
│   └── STATIC_FLOWS.md
│
├── public/
│   ├── manifest.json
│   ├── sw.js                          # Service worker
│   ├── icons/
│   └── og-image.png
│
├── src/
│   ├── App.tsx
│   ├── main.tsx
│   ├── index.css                      # Tailwind imports + AMTL theme
│   │
│   ├── components/
│   │   ├── Layout.tsx
│   │   ├── Sidebar.tsx
│   │   ├── Settings.tsx
│   │   ├── ThemeToggle.tsx
│   │   ├── ContextHelp.tsx            # Context-aware help system
│   │   ├── CrisisBanner.tsx
│   │   └── ui/                        # Shared UI primitives
│   │
│   ├── features/
│   │   ├── mirror/                    # Core conversation
│   │   ├── vault/                     # 24-Hour Vault
│   │   ├── letter/                    # Letter You'll Never Send
│   │   ├── weather-map/               # Emotional Weather Map
│   │   ├── body-compass/              # Body Compass
│   │   ├── decisions/                 # Decision Journal + Future Self
│   │   ├── rewriter/                  # Reactive Message Rewriter
│   │   ├── wisdom-feed/               # Wisdom Feed
│   │   ├── capture/                   # Quick Capture
│   │   └── landing/                   # Website landing page
│   │
│   ├── lib/
│   │   ├── database.ts               # IndexedDB operations
│   │   ├── ai.ts                      # AI provider abstraction (BYOK)
│   │   ├── staticFlows.ts            # Pre-written question flows
│   │   ├── paliDictionary.ts         # Dictionary data
│   │   ├── wisdomContent.ts          # Curated wisdom passages
│   │   ├── crisisDetection.ts        # Keyword detection + resources
│   │   └── theme.ts                  # Dark/light theme management
│   │
│   ├── hooks/
│   │   ├── useDatabase.ts
│   │   ├── useAI.ts
│   │   └── useTheme.ts
│   │
│   └── stores/
│       ├── settingsStore.ts
│       └── appStore.ts
│
├── tests/
│   ├── beast/                         # Unit/integration tests (vitest)
│   ├── proof/                         # Playwright screenshots
│   └── smoke/                         # Startup verification
│
└── .github/
    └── workflows/
        └── deploy.yml                 # GitHub Pages deployment
```

---

## PHASE 2: THE WEBSITE (Landing Page + Marketing)

**The landing page IS the website.** When someone visits the GitHub Pages URL, they see the marketing page. When they click "Ask the Mirror," they enter the app.

### Website Sections (Build as React components in `src/features/landing/`)

Create `LandingPage.tsx` with these sections, using the StoryBrand + Hero's Journey framework:

---

### Section 1: THE HOOK (Hero's Ordinary World in Crisis)

```
It's 11pm.

You're about to send that email.
You know you shouldn't.
But you're going to anyway.

Unless.

[Ask the Mirror]
```

Design: Full-viewport, dark background (AMTL Midnight), minimal text, large typography. The button glows subtly with Gold #C9944A. Atmospheric. No clutter.

---

### Section 2: THE PROBLEM (The Call to Adventure)

```
You know the feeling.

Someone said something. Or did something.
Or didn't do something.

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

Design: Scroll-reveal, one sentence at a time. Typography-driven. No images. Let the words do the work.

---

### Section 3: THE GUIDE APPEARS

```
What if you could talk to someone first?

Not a therapist. Not a friend with opinions.
Not the internet.

Someone who would just... ask good questions.

"Where do you feel this in your body?"
"What would happen if you waited 24 hours?"
"What are you actually afraid of?"

No advice. No judgment. Just questions.
The kind that make you see what you
already know but can't quite admit.

That's Socrates & Donuts.
A wise friend for difficult moments.
```

---

### Section 4: THE PLAN (Three Steps)

```
HOW IT WORKS

Step 1: Tell the mirror what's happening
   Not a form. Not a quiz. Just talk.

Step 2: Answer the questions
   The mirror asks. You answer.
   The seeing happens in between.

Step 3: Decide from clarity
   Now you can act. Or wait. Or let it go.
   But whatever you do, you'll do it clearly.
```

Design: Three cards, clean layout. Icons from lucide-react. Minimal.

---

### Section 5: THE TOOLS (Feature Showcase)

Display the Core 10 features as elegant cards:

```
THE TOOLS

🪞 The Mirror — A wise conversation that starts with your body
🔐 The Vault — Write the angry message. Lock it for 24 hours. Decide tomorrow.
🔥 Letter You'll Never Send — Write it. Burn it. Watch it dissolve.
🌤️ Emotional Weather Map — See your emotional patterns as beautiful weather
🧭 Body Compass — Where do you feel it? Your body knows before your mind.
📔 Decision Journal — Log it now. Review with fresh eyes in 30 days.
✍️ Message Rewriter — See your angry email in Calm, Empathetic, and Assertive.
📜 Wisdom Feed — The anti-doomscroll. Curated wisdom, not outrage.
⚡ Quick Capture — Catch the thought before it's gone.
🛡️ Crisis Support — If things are serious, we'll help you find real help.
```

---

### Section 6: FOR VIPASSANA PRACTITIONERS

```
FOR PRACTITIONERS

If you sit Vipassana, you know the mirror.
You sit. You observe. You see.

But what about the other 22 hours?

When someone cuts you off in traffic
and you observe yourself being equanimous,
but actually you're just suppressing...

When you skip your evening sit and tell yourself
you'll make it up tomorrow,
and something in you knows you won't...

Socrates & Donuts extends the work of the cushion
into the rest of your day.

Every insight traces to a sutta.
Every question comes from the teaching.
Nothing is invented.

33 additional tools for serious practitioners.

[Enter the Practice Space]
```

---

### Section 7: WHY IT'S FREE

```
WHY IS THIS FREE?

In the Buddhist tradition, the Dhamma
is given freely. Always has been.

This app is built on the same principle.
No ads. No premium tier. No data collection.

Your conversations stay on your device.
We never see them. No one does.

The code is open source.
The wisdom belongs to everyone.

This is dana — the practice of generosity.
```

---

### Section 8: SAFETY DISCLAIMER

```
IMPORTANT

Socrates & Donuts is not a therapist.
It is not a crisis service.
It is not a replacement for professional help.

If you are experiencing:
→ Thoughts of self-harm or suicide
→ A mental health emergency
→ Ongoing psychological distress

Please contact:
→ Lifeline Australia: 13 11 14
→ 988 Suicide & Crisis Lifeline (US): 988
→ Crisis Text Line: Text HOME to 741741
→ International: findahelpline.com
```

---

### Section 9: FOOTER

```
Socrates & Donuts
A wise friend for difficult moments.

Open source. Privacy first. Free forever.

Built by Almost Magic Tech Lab
GitHub | Documentation | Manifesto

Sabbē sattā sukhī hontu — May all beings be happy.
```

---

## PHASE 3: BUILD THE CORE 10 FEATURES

Follow the specification in `AMTL-SND-SPC-2.0`. Build in this order:

1. **Crisis Detection** (safety first — must be in every screen)
2. **The Mirror** (static flows first, then BYOK AI)
3. **The 24-Hour Vault**
4. **Quick Capture**
5. **Letter You'll Never Send** (with burn animation)
6. **Body Compass**
7. **Emotional Weather Map**
8. **Decision Journal**
9. **Wisdom Feed**
10. **Reactive Message Rewriter**

### Testing at Every Feature

| Test | Required |
|------|----------|
| Beast (vitest) | Every feature |
| Proof (Playwright screenshots) | Every feature |
| Smoke (app starts, feature renders) | Every feature |
| Accessibility | Every feature |
| Mobile-first responsive | Every feature |

---

## PHASE 4: CONTEXT-AWARE HELP

**Every screen must have context-aware help.** This is an AMTL-wide standard.

Implementation:

```typescript
// src/components/ContextHelp.tsx
// Press ? or click (?) icon → shows help for CURRENT screen
// Help content is stored per-feature in markdown
// Rendered as a slide-out panel
// Includes "What can I do here?" quick reference

interface HelpContent {
  featureId: string;
  title: string;
  quickActions: string[];      // "What can I do here?"
  howItWorks: string;          // Brief explanation
  tips: string[];              // Pro tips
  relatedFeatures: string[];   // Links to related features
}
```

Every feature folder must include a `help.ts` file with its help content.

---

## PHASE 5: PWA + GITHUB PAGES DEPLOYMENT

### Service Worker

```typescript
// public/sw.js
// Cache the app shell for offline use
// The Mirror's static flows must work offline
// BYOK AI features gracefully degrade when offline
```

### GitHub Actions Deploy

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

## PHASE 6: DOCUMENTATION

Create all 9 AMTL-mandated documents in the `docs/` folder:

| # | Document | Code | Focus |
|---|----------|------|-------|
| 1 | Specification Addendum | AMTL-SND-SPC-2.0 | ✅ Already created (this instruction references it) |
| 2 | Technical Design Document | AMTL-SND-TDD-1.0 | React architecture, IndexedDB schema, AI abstraction layer |
| 3 | Build Guide | AMTL-SND-BLD-1.0 | Phase-by-phase construction steps |
| 4 | Decision Register | AMTL-SND-DEC-1.0 | Log every build decision |
| 5 | Operations Runbook | AMTL-SND-RUN-1.0 | How to deploy, update, manage |
| 6 | User Manual | AMTL-SND-USR-1.0 | Plain English for end users |
| 7 | Diagnostic Playbook | AMTL-SND-DGN-1.0 | Symptom → fix guide |
| 8 | Known Issues Register | AMTL-SND-KNW-1.0 | Honest limitations list |
| 9 | Machine-Readable Diagnostics | AMTL-SND-MRD-1.0 | YAML for automated checks |

---

## PHASE 7: FINAL CHECKLIST

Before declaring Socrates & Donuts v1 done:

| Deliverable | Status |
|-------------|--------|
| Landing page (website) with StoryBrand copy | Required |
| Core 10 features working | Required |
| Static flows working (no API) | Required |
| BYOK AI working (user provides key) | Required |
| Crisis detection on every screen | Required |
| Dark/light theme toggle | Required |
| Context-aware help on every screen | Required |
| PWA working offline (static flows) | Required |
| GitHub Pages deployment | Required |
| All Beast tests passing | Required |
| Proof/Playwright screenshots | Required |
| Mobile-first responsive design | Required |
| README.md | Required |
| MANIFESTO.md | Required |
| All 9 AMTL documents | Required |
| Data export/import (JSON) | Required |
| Accessibility (WCAG 2.1 AA) | Required |

---

## Design Guidelines

| Element | Value |
|---------|-------|
| Dark theme | AMTL Midnight `#0A0E14` |
| Light theme | Clean white `#FAFAFA` |
| Accent | Gold `#C9944A` |
| Typography | System fonts (no custom font loading for speed) |
| Animations | Subtle, meaningful, never distracting. Framer Motion. |
| Mobile-first | Design for phone screens first, desktop second |
| Icons | lucide-react |
| The burn animation | CSS/Canvas fire effect dissolving text — this must feel *cathartic* |
| The weather map | Canvas-based, animated clouds/sun/storms — this must be *beautiful* |

---

## Summary

```
Clean repo → Scaffold React app → Build landing page (website) →
Build Core 10 features → Add context-aware help → Deploy to GitHub Pages →
Create all 9 documents → Push to GitHub → Share with the world
```

---

*Almost Magic Tech Lab*
*"Wisdom doesn't have to be solemn. Sometimes it comes with donuts."*
