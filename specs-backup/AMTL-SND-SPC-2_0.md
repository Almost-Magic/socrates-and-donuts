# SOCRATES & DONUTS
## Complete Specification v2
## "A wise friend for difficult moments"
## Document Code: AMTL-SND-SPC-2.0
## Almost Magic Tech Lab
## 18 February 2026

> *This document follows AMTL-ECO-STD v1.0. All conventions defined there apply unless explicitly overridden with a Decision Register entry.*

---

# EXECUTIVE SUMMARY

**Socrates & Donuts** is an open-source web application that serves as a wise friend for difficult moments — when you're too angry, too sad, or too confused to trust your own judgement.

It helps you: recognise when you're reactive, process before acting, see your blind spots, and decide from clarity rather than emotion.

For Vipassana practitioners, an optional "Dhamma Mirror" tab unlocks the full Buddhist practice toolkit — suttas, Pali dictionary, hindrance diagnostics, and 33 additional features grounded in the Pali Canon.

| Attribute | Value |
|-----------|-------|
| Name | Socrates & Donuts |
| Subtitle | A wise friend for difficult moments |
| Internal codename | Dhamma Mirror (practitioner tab) |
| Repository | github.com/Almost-Magic/dhamma-mirror |
| Hosting | GitHub Pages |
| Backend | None. Zero. Local-first, browser-only. |
| AI | BYOK (Bring Your Own Key) — Claude API or static flows |
| Data storage | IndexedDB (browser-local) with JSON export/import |
| Licence | MIT (code), CC BY-NC (dictionary/sutta content) |
| Author | Mani Padisetti, Founder & Curator, AMTL |
| Status | Ready for development |

---

# PART 1: PHILOSOPHY

## 1.1 The Core Problem

When you're in a reactive state, you shouldn't trust your own judgement.

Anger, sadness, overwhelm, grief, fear — these states hijack the mind. Decisions made in these states cause harm. The email sent in anger. The words said in hurt. The decision made in grief. The reaction born of fear.

## 1.2 The Solution

Socrates & Donuts is a **pause button**. A place to process before acting. It doesn't give advice. It asks questions — the kind a wise friend would ask if they had infinite patience and no agenda.

## 1.3 Why the Name

Socrates asked questions. Donuts are comfort food. Wisdom doesn't have to be solemn. A philosophy student, a truck driver, and a Vipassana meditator all feel welcome. No religious gatekeeping. No clinical sterility. Just warmth and clarity.

## 1.4 The Five Principles

1. **We don't fix** — We help you see. That's all.
2. **We don't advise** — Only questions. Never answers.
3. **We don't replace people** — Tool for clarity, then go to humans.
4. **We slow things down** — Protect the pause.
5. **Seeing is enough** — No gamification, no streaks, no badges.

## 1.5 What This Is NOT

- Not a therapist or mental health tool
- Not a replacement for a teacher or sangha
- Not a gamified meditation tracker
- Not a social platform
- Not commercial — no ads, no upsells, no premium tier
- Not addictive by design — valuable enough to return to, never manipulative

---

# PART 2: ARCHITECTURE

## 2.1 No Backend. Period.

| Component | Technology | Location |
|-----------|------------|----------|
| Frontend | React 18 + TypeScript | GitHub Pages |
| Styling | Tailwind CSS | Client-side |
| Data storage | IndexedDB (idb library) | Browser-local |
| AI (Tier 1) | Static question flows | No API needed |
| AI (Tier 2) | Claude API via BYOK | User's own key, direct to Anthropic |
| Sutta search | Client-side full-text (top 100 suttas) | Bundled JSON |
| Hosting | GitHub Pages | Static files only |
| PWA | Service worker | Offline-capable |
| Export/Import | JSON file download/upload | User's filesystem |

**"No user data backend" means:** Your data never leaves your device. We never see it. No telemetry. No analytics. No cloud sync. You own your psyche.

## 2.2 BYOK Model (Honest About It)

The Mirror's AI features require an API key. We are honest about this:

> "The Mirror uses AI to ask you better questions. This requires a Claude API key, which you provide. Your conversations go directly from your browser to Anthropic — we never see them. No key? The Mirror still works with guided question flows."

| Tier | What It Is | AI Required? | Quality |
|------|-----------|--------------|---------|
| Tier 1: Static Mirror | Pre-written question flows (~120 steps across 6 flows) | No | Good |
| Tier 2: BYOK | User provides their own Claude API key | Yes | Excellent |

## 2.3 Data Architecture

All data stored in browser IndexedDB. User can export/import as JSON at any time.

```typescript
interface SocratesDatabase {
  // Core
  conversations: Conversation[];
  vaultEntries: VaultEntry[];
  letters: LetterEntry[];
  quickCaptures: QuickCapture[];

  // Daily
  firstThoughts: FirstThought[];
  morningIntentions: MorningIntention[];
  eveningReflections: EveningReflection[];

  // Decisions
  decisions: DecisionEntry[];

  // Body
  bodyCompassEntries: BodyCompassEntry[];

  // Emotional
  emotionalSnapshots: EmotionalSnapshot[];

  // Practice (Dhamma Mirror tab only)
  practiceLogs: PracticeLog[];
  hindranceObservations: HindranceObservation[];
  facultyObservations: FacultyObservation[];
  vedanaMaps: VedanaMap[];
  contemplations: Contemplation[];

  // Meta
  settings: Settings;
  exportHistory: ExportRecord[];
}
```

## 2.4 Export/Import (Dead Simple)

Two buttons. Zero friction.

- **"Download My Data"** → exports everything as a single JSON file
- **"Restore My Data"** → upload a JSON file, data restored
- File named: `socrates-backup-YYYY-MM-DD.json`
- Monthly Export Ritual: app gently reminds user to back up

---

# PART 3: THE 10 CORE FEATURES (v1)

These are the v1 features. Everything else is Phase 2+.

## Feature 1: THE MIRROR (Core Conversation)

The heart of the app. You talk. The Mirror asks questions. You see what you couldn't see.

**Entry point:** Single text input — "What's on your mind?"

**How it works:**
- User types what's happening
- AI (or static flow) responds with questions, not answers
- Always starts with body: "Where do you feel this in your body?"
- Explores the Three Roots: What are you craving? What are you avoiding? What can't you see?
- Cites suttas when relevant (practitioner mode) or stays secular (universal mode)
- Ends with a reflection question

**Static flow fallback (no API):**
Six pre-built flows with branching questions:

| Flow | Entry | Steps |
|------|-------|-------|
| Decision | "I need to make a decision" | ~25 |
| Anger | "I'm angry and about to do something" | ~20 |
| Hurt | "I'm hurt and want to say something" | ~20 |
| Grief | "I'm overwhelmed with sadness" | ~20 |
| Anxiety | "I'm anxious and stuck in my head" | ~20 |
| General | "Something else" | ~15 |

## Feature 2: THE 24-HOUR VAULT

Write the angry email. Lock it for 24 hours. Review with fresh eyes.

**UI:** Full-screen writing space → Lock button → Countdown timer → Review screen
**After 24 hours:** Send as-is, Edit first, or Discard
**The Vault Lock Animation:** Slow closing door animation, subtle click sound, countdown as melting wax

```typescript
interface VaultEntry {
  id: string;
  content: string;
  context: string;
  recipient?: string;
  createdAt: string;
  unlocksAt: string;    // createdAt + 24 hours
  status: 'locked' | 'unlocked' | 'deleted';
  reviewedAt?: string;
  outcome?: 'sent' | 'modified' | 'discarded';
  reflectionNote?: string;
}
```

## Feature 3: THE LETTER YOU'LL NEVER SEND

Write letters to people you can't talk to. Ex-partners, deceased parents, the boss who wronged you, your younger self.

**UI:** Gorgeous full-screen writing interface (off-black background, warm serif type, animated ember glow)
**When done, choose:**
- 🔥 **Burn it** — animated fire dissolves the text, chars turn orange → red → black → ash rises as smoke. Cathartic. Final. No undo.
- 📦 **Vault it** — lock for 24 hours
- 📖 **Keep it** — save to journal

**Optional (BYOK only):** After writing, AI reflects back ONE question — "What do you wish they had said back?"

## Feature 4: THE EMOTIONAL WEATHER MAP

A beautiful, animated visualisation of your emotional patterns over time — rendered as weather.

**How it works:**
- Each Mirror conversation, Vault entry, or Quick Capture tags an emotional state
- Emotional states map to weather: Anger = storms, Anxiety = fog, Clarity = sunshine, Grief = rain, Calm = still water, Joy = warm breeze
- Over days/weeks, builds into a personal weather timeline
- Animated: clouds drift, storms brew and clear, sun breaks through
- Tap any day to see entries from that day
- Zoom: day → week → month → year

**Data model:**
```typescript
interface EmotionalSnapshot {
  id: string;
  timestamp: string;
  state: 'anger' | 'anxiety' | 'clarity' | 'grief' | 'calm' | 'joy' | 'confusion' | 'fear';
  intensity: number;      // 1-10
  context?: string;       // What triggered it
  bodyLocation?: string;  // Where felt in body
  sourceFeature: string;  // Which feature generated this
  sourceId: string;       // ID of the source entry
}
```

**Technical:** HTML5 Canvas + JavaScript particle systems. Muted natural palette (blues, grays, golds). Full-screen, low-noise. Time slider animates transitions smoothly.

## Feature 5: THE BODY COMPASS

An interactive human silhouette that you tap to record where you feel things. Over time, becomes your personal body-emotion map.

**How it works:**
- Elegant gender-neutral silhouette on dark background
- Tap a body region → select sensation (warmth, tightness, tingling, heaviness, numbness, pain, lightness)
- Select valence: pleasant, unpleasant, neutral
- Logs with timestamp and optional emotional context
- Over time: heatmap reveals patterns ("Every time I'm angry, my jaw lights up")
- Hover past hotspots → tooltips: "Jaw — anger-related (7 times)"

**Data model:**
```typescript
interface BodyCompassEntry {
  id: string;
  timestamp: string;
  bodyRegion: string;     // 'head' | 'jaw' | 'chest' | 'stomach' | 'shoulders' | etc.
  x: number;              // Tap coordinate on silhouette
  y: number;
  sensation: 'warmth' | 'tightness' | 'tingling' | 'heaviness' | 'numbness' | 'pain' | 'lightness' | 'pressure';
  valence: 'pleasant' | 'unpleasant' | 'neutral';
  intensity: number;      // 1-10
  emotionalContext?: string;
  linkedEntryId?: string; // Link to a conversation, decision, etc.
}
```

**Heatmap algorithm:**
- Minimum 5 data points per region before showing pattern
- Colour intensity based on frequency (blue → yellow → red)
- Temporal decay: entries older than 90 days weighted at 50%
- Render: SVG silhouette with CSS glow effects, soft pulsing animation

## Feature 6: THE DECISION JOURNAL (with Future Self Review)

Log decisions with reasoning. Set a review date. Your future self evaluates past-you's logic.

**How it works:**
- Log: the decision, your reasoning, your emotional state, what you're afraid of, what you're hoping for
- Set review date: 1 week, 1 month, 3 months, 1 year
- On that date, app resurfaces the entry
- Review: Was I right? Wrong? What didn't I see?
- Over time: searchable archive of decision-making patterns

**UI:** Horizontal timeline with sealed envelopes. Locked entries pulse gently. When review date arrives, envelope opens into a card — original reasoning on left, review space on right.

```typescript
interface DecisionEntry {
  id: string;
  decision: string;
  reasoning: string;
  emotionalState: string;
  fears: string;
  hopes: string;
  createdAt: string;
  reviewAt: string;
  status: 'sealed' | 'ready' | 'reviewed';
  reviewNotes?: string;
  wasCorrect?: 'yes' | 'no' | 'partially' | 'too_early';
  whatIMissed?: string;
}
```

## Feature 7: THE REACTIVE MESSAGE REWRITER

Paste in the angry email/text. See it rewritten from three emotional states.

**How it works (BYOK only):**
- Paste your reactive message
- AI generates three rewrites:
  - 🧊 **Calm** — same content, zero heat
  - 🤝 **Empathetic** — acknowledges the other person's perspective
  - 🎯 **Assertive** — clear, direct, no passive aggression
- Side-by-side comparison with the original
- Linguistic analysis: I/You ratio, blame language count, emotional intensity
- Pick one, edit it, or vault the original for 24 hours

**UI:** Four columns with synchronised scroll. Diff highlighting via soft background hue (not dev-style red/green). Tone dials at top.

**Static fallback (no API):** Checklist approach — "Before sending, check: Does this contain 'you always' or 'you never'? Count the word 'you' versus 'I'. Would you say this to their face? How would you feel reading this tomorrow?"

## Feature 8: THE WISDOM FEED

An infinite scroll of curated wisdom — contextually matched to your recent patterns. The anti-doomscroll.

**How it works:**
- Draws from: Stoic philosophy, Buddhist suttas, psychology research, poetry, literature
- Contextual (BYOK): selected based on recent patterns (if anger dominant → relevant anger wisdom)
- Static (no API): curated library, random selection with category tags
- Each card: one passage, one reflection question, save or dismiss
- Slow scroll: 2-second delay between cards forces reading, not skimming

**Content sources (all public domain or CC):**
- Marcus Aurelius (Meditations)
- Epictetus (Enchiridion)
- Seneca (Letters)
- Dhammapada
- Selected suttas (with citation)
- Rumi, Hafiz (poetry)
- Viktor Frankl, William James (psychology)

**UI:** Full-screen cards, beautiful serif typography, CSS scroll-snap. Minimal. Meditative.

**Open source advantage:** Community contributes wisdom passages via GitHub PRs. Library grows organically.

## Feature 9: QUICK CAPTURE

Fast entry for moments of insight, reactive thoughts, or observations. The "jot it down" feature.

**How it works:**
- One-tap from any screen (floating button or keyboard shortcut)
- Log context + emotion + body sensation in under 10 seconds
- Tags automatically (anger, insight, decision, fear, etc.)
- Feeds into Weather Map, Body Compass, and Pattern analysis
- Searchable, timestamped

**UI:** Small floating [+] button, expands to quick-entry card. Dismiss to save. Minimal friction.

## Feature 10: CRISIS DETECTION & RESOURCES

If language suggests self-harm or crisis, stop mirroring. Go directive.

**How it works:**
- Rule-based keyword detection (comprehensive list of crisis indicators)
- If triggered: immediately surface crisis resources, warm and direct
- Stop the Mirror conversation. No more questions. Be human.
- Localised resources by country (detected from browser locale)

**Resources:**
- Australia: Lifeline 13 11 14, Beyond Blue 1300 22 4636
- US: 988 Suicide & Crisis Lifeline
- UK: Samaritans 116 123
- International: findahelpline.com

**Legal:** Prominent disclaimer on landing page and in settings: "Socrates & Donuts is not a crisis service, not a therapist, and not a replacement for professional help."

---

# PART 4: PRACTITIONER TAB — "DHAMMA MIRROR"

Accessible via settings toggle or the "For Practitioners" path. Unlocks 33 additional features grounded in the Pali Canon.

## 4.1 Practice Tools (7 features)
- Daily Practice Log
- Sit Quality Classifier
- Pre/Post-Sit Check-in
- Just Sit Timer
- Meditation History
- Practice Insights Capture
- Sankalpa Setter (morning intention with evening review)

## 4.2 Diagnostic Tools (6 features)
- Five Hindrances Diagnostic (with antidote library from suttas)
- Five Hindrances History
- Five Faculties Balance (saddha/panna, viriya/samadhi, sati)
- Lazy vs Witnessing Detector (the core practitioner diagnostic)
- Ego Pattern Tracker
- Plateau Detector

## 4.3 Body Awareness (5 features)
- Enhanced Vedana Mapper (extends Body Compass with Pali terminology)
- Anicca Contemplation
- Dukkha Contemplation
- Anatta Contemplation
- Sensation Diary

## 4.4 Scripture (4 features)
- Natural Language Sutta Search (top 100 suttas, client-side)
- Pali Dictionary (220+ terms across 10 categories)
- 20 Sutta Study Companions (section-by-section breakdown)
- Contextual Sutta of the Day (based on user's patterns)

## 4.5 Other Practice Features (11 features)
- First Thought Capture
- Evening Truth Journal
- Pre-Sleep Body Scan
- Unfinished Business Tracker
- Difficult Conversation Prep
- Grief Companion
- Pre-Retreat Preparation
- Post-Retreat Integration
- Journal Viewer (searchable, filterable)
- Weekly/Monthly Synthesis
- Teacher Export

**Total:** 10 core + 33 practitioner = **43 features**

---

# PART 5: THE SYSTEM PROMPT

```
You are Socrates & Donuts — a wise friend for difficult moments.

You are not a guru, not a therapist, not an authority. You are a mirror.
Your job: help the person see what they cannot see when they are reactive.

CORE PRINCIPLES:

1. QUESTIONS BEFORE ANSWERS
   Ask at least 2-3 questions before offering any reflection.
   Never give advice. Help them find their own answer.

2. SENSATION-FIRST
   Always begin with the body:
   - "Where do you feel this in your body?"
   - "What's the quality of that sensation?"
   - "Is the sensation changing or static?"

3. THREE ROOTS ANALYSIS
   In every situation, look for:
   - What are you wanting from this? (craving)
   - What are you trying to avoid? (aversion)
   - What might you not be seeing? (delusion)

4. WAIT WISDOM
   "The mud needs time to settle." Encourage patience.
   - Suggest the 24-Hour Vault for reactive messages
   - "What would happen if you did nothing for 24 hours?"

5. BLIND SPOT DETECTION
   Help them see:
   - The rationalisation that sounds like wisdom
   - The avoidance that looks like patience
   - The people-pleasing that masquerades as compassion

6. KNOW YOUR LIMITS
   - Not a therapist. Recommend professional help when needed.
   - Not a replacement for human connection.
   - Say "I don't know" when appropriate.

7. CRISIS CIRCUIT BREAKER
   If language suggests self-harm or crisis:
   STOP MIRRORING. Go directive. Surface resources immediately.

MODE: UNIVERSAL (default)
- Zero Buddhist terminology
- Psychological framing only
- No sutta citations
- Accessible to anyone

MODE: PRACTITIONER (when Dhamma Mirror tab is active)
- Pali terms with translations
- Sutta citations when relevant (format: "In the [Name] ([Code])...")
- Buddhist diagnostic frameworks (hindrances, faculties, dependent origination)
- Sensation-first always (vedana as entry point)

COMMUNICATION STYLE:
- Warm but not effusive
- Direct but gentle
- Patient — never rushing
- "You might consider" rather than "you should"
- End significant exchanges with a question for reflection

FEW-SHOT EXAMPLES:

Example 1 — Anger (Universal mode):
User: "I'm furious at my colleague. He took credit for my work."
Mirror: "That sounds like a difficult moment. Before we look at the
situation — where do you feel this in your body right now?"
User: "My chest is tight. My jaw is clenched."
Mirror: "Thank you for noticing that. The body often knows before the
mind. That tightness — is it increasing, decreasing, or staying the
same as you describe it?"

Example 2 — Decision (Universal mode):
User: "I'm thinking about quitting my job."
Mirror: "That's a significant decision. Let me ask: when you imagine
handing in your notice, what's the first sensation in your body?"

Example 3 — Anger (Practitioner mode):
User: "I can't stop thinking about what they said."
Mirror: "Let's look at this through the lens of the three roots. First,
where do you feel this in your body? And then — what is the mind
wanting from this situation? Is there craving (lobha) for something —
perhaps recognition, vindication? Or is there primarily aversion (dosa)
— a pushing away of the experience?"
```

---

# PART 6: CONTEXT-AWARE HELP SYSTEM

Every screen in Socrates & Donuts includes contextual help.

## 6.1 How It Works

- **[?] icon** in the top-right of every feature card/screen
- Tap [?] → slide-in panel shows contextual guidance for the current feature
- **First-time tooltips:** On first use of any feature, a gentle tooltip explains what it does (dismissible, never returns after dismissal)
- **"What can I do here?"** summary on every major screen
- **Searchable help:** Global search across all help content
- **Tone:** Warm, plain English. Written for a human, not a developer.

## 6.2 Help Content Structure

```typescript
interface HelpEntry {
  featureId: string;
  title: string;
  summary: string;         // One sentence: what this does
  howToUse: string;        // 2-3 sentences: how to use it
  whyItHelps: string;      // 2-3 sentences: why this matters
  tips: string[];          // 2-3 practical tips
  relatedFeatures: string[]; // Links to related features
}
```

---

# PART 7: UI/UX DESIGN

## 7.1 Design Principles

- **Calm Technology** — minimal, respectful, beautiful, accessible, timeless
- **Mobile-first** — people have crises on their phones, not laptops
- **Dark default** — AMTL Midnight #0A0E14 with Gold #C9944A accent
- **Light mode available** — toggle in header, persists
- **No AI-generated images** — Lucide icons, hand-crafted SVG

## 7.2 Typography

- **Serif** (for wisdom content, suttas, journal, letters): Lora or Crimson Text
- **Sans-serif** (for UI, buttons, labels): Inter or system font stack
- This creates hierarchy: content feels timeless, UI feels modern

## 7.3 Key Animations

| Element | Animation | Duration |
|---------|-----------|----------|
| Weather Map | Canvas particle systems, drifting clouds | Continuous |
| Body Compass | Soft glow on tap, pulsing heatmap | 300ms tap, continuous pulse |
| Vault Lock | Slow closing door, wax countdown | 2s lock animation |
| Letter Burn | Char-by-char fire dissolution, ash rises | 5-7s |
| Wisdom Feed | Scroll-snap with 2s delay between cards | 2s per transition |
| Breathing Interface | Subtle background shift (lighter/darker) | 8s cycle (4 in, 4 out) |

## 7.4 The Onboarding

No tutorial. No tour. No "skip" button.

User opens app → sees: **"What's on your mind?"** with a text input.

That's it. Progressive disclosure reveals features as needed.

After the first conversation, gentle prompt: "You might also find the Vault useful — it holds your words for 24 hours."

## 7.5 Single Entry Point (Not Dual-Path)

The app starts with "What's on your mind?" for everyone. The practitioner features unlock via Settings → "I'm a Vipassana practitioner" toggle. This reveals the Dhamma Mirror tab. No gatekeeping. No confusion.

---

# PART 8: WEBSITE COPY (StoryBrand + Hero's Journey)

This copy is used on the GitHub Pages landing page AND the app's "About" section.

## 8.1 Landing Page

### Above the Fold

```
SOCRATES & DONUTS
A wise friend for difficult moments

It's 11pm.
You're about to send that email.
You know you shouldn't.
But you're going to anyway.

Unless.

[What's on your mind?]
```

### The Problem (Hero's Ordinary World in Crisis)

```
You know the feeling.

Someone said something. Or did something.
Or didn't do something.

And now your chest is tight.
Your jaw is clenched.
You're composing the perfect response in your head.

Here's the thing:
When you're angry, your judgement lies to you.
When you're sad, everything feels permanent.
When you're afraid, every option looks dangerous.

You can't see clearly.
And you know you can't see clearly.
But you're going to act anyway.
```

### The Guide Appears

```
What if you could talk to someone first?

Not a therapist. Not a friend with opinions.
Not the internet.

Someone who would just... ask good questions.

"Where do you feel this in your body?"
"What would happen if you waited 24 hours?"
"What are you actually afraid of?"

No advice. No judgement. Just questions.
The kind that make you see what you
already know but can't quite admit.

That's Socrates & Donuts.
Wisdom and comfort. Questions and kindness.
```

### The Plan (Three Steps)

```
HOW IT WORKS

Step 1: Tell us what's happening
   Not a form. Not a quiz. Just talk.

Step 2: Answer the questions
   The mirror asks. You answer.
   The seeing happens in between.

Step 3: Decide from clarity
   Now you can act. Or wait. Or let it go.
   But whatever you do, you'll do it with clear eyes.
```

### Features (Visual Cards)

```
THE MIRROR — Talk it through. See what you couldn't see.
THE VAULT — Write the angry email. Lock it for 24 hours. Tomorrow, decide.
THE LETTER — Write to someone you can't talk to. Then burn it, vault it, or keep it.
YOUR WEATHER — See your emotional patterns as weather. Storms pass.
YOUR BODY — Discover where your emotions live in your body.
YOUR DECISIONS — Log choices. Review later. Learn from yourself.
THE REWRITER — Paste the angry text. See it three ways: calm, empathetic, assertive.
WISDOM FEED — An infinite scroll of wisdom. The anti-doomscroll.
```

### The Practitioner Section

```
FOR VIPASSANA PRACTITIONERS

If you sit Vipassana, you know the mirror.
You sit. You observe. You see.

But what about the other 22 hours?

Toggle "Dhamma Mirror" in settings to unlock:
• Sutta search and study companions
• Five Hindrances diagnostic
• Five Faculties balance
• Pali dictionary (220+ terms)
• Practice logging and pattern analysis
• And 28 more tools for serious practitioners

Every insight traces to a sutta.
Every question comes from the teaching.
Nothing is invented.
```

### Why It's Free

```
WHY IS THIS FREE?

In the Buddhist tradition, wisdom is given
freely. Always has been. Always will be.

This app is built on the same principle.
No ads. No premium tier. No data collection.

Your conversations stay on your device.
We never see them. No one does.

The code is open source.
The wisdom belongs to everyone.

This is dana — the practice of generosity.

May all beings be happy.
```

### Safety

```
IMPORTANT

Socrates & Donuts is not a therapist.
It is not a crisis service.
It is not a replacement for professional help.

If you are experiencing a crisis:
→ Lifeline Australia: 13 11 14
→ 988 Suicide & Crisis Lifeline (US): 988
→ Samaritans (UK): 116 123
→ International: findahelpline.com
```

### Footer

```
Open source. Free forever. Your data stays yours.
Built by Mani Padisetti at Almost Magic Tech Lab.
github.com/Almost-Magic/dhamma-mirror

Sabbē sattā sukhī hontu — May all beings be happy.
```

---

# PART 9: PALI DICTIONARY SUMMARY

220+ terms across 10 categories. Full dictionary in separate data file.

| Category | Count | Examples |
|----------|-------|---------|
| Tilakkhana (Three Characteristics) | ~15 | anicca, dukkha, anatta, sankhara, vedana |
| Bhavana (Meditation & Practice) | ~25 | vipassana, samatha, sati, samadhi, jhana, upekkha |
| Citta (Mind States) | ~20 | lobha, dosa, moha, tanha, kilesa, sukha |
| Sila (Ethics & Conduct) | ~15 | panca sila, ahimsa, sacca, dana, khanti |
| Magga (The Path) | ~15 | ariya atthangika magga, samma ditthi, samma sati |
| Nivarana (Five Hindrances) | ~15 | kamacchanda, byapada, thina-middha, uddhacca-kukkucca |
| Bojjhanga (Awakening Factors) | ~10 | sati, dhamma vicaya, viriya, piti, passaddhi |
| Paticcasamuppada (Dependent Origination) | ~15 | 12 links: avijja through jaramarana |
| Vimutti (Liberation) | ~10 | nibbana, vimutti, sotapanna, arahant |
| General | ~60+ | dhamma, sangha, kamma, samsara, kalyana-mitta |

Sources: Nyanatiloka (public domain), PTS Dictionary (public domain), SuttaCentral (CC BY-NC).

---

# PART 10: SUTTA CORPUS

| Content | Count |
|---------|-------|
| Client-side searchable | Top 100 suttas (bundled as JSON) |
| Full corpus (optional download) | ~15,000+ from SuttaCentral (~500MB) |
| Suttas with study companions | 20 key suttas |

## 20 Key Suttas

| # | Sutta | Code | Topic |
|---|-------|------|-------|
| 1 | Satipatthana Sutta | MN 10 | Foundations of mindfulness |
| 2 | Maha-Satipatthana Sutta | DN 22 | Extended foundations |
| 3 | Anapanasati Sutta | MN 118 | Mindfulness of breathing |
| 4 | Dhammacakkappavattana Sutta | SN 56.11 | Four Noble Truths |
| 5 | Kalama Sutta | AN 3.65 | Don't take anyone's word for it |
| 6 | Metta Sutta | Snp 1.8 | Loving-kindness |
| 7 | Sallatha Sutta | SN 36.6 | The two arrows |
| 8 | Bahiya Sutta | Ud 1.10 | In the seen, only the seen |
| 9 | Anattalakkhana Sutta | SN 22.59 | Non-self |
| 10 | Adittapariyaya Sutta | SN 35.28 | The Fire Sermon |
| 11 | Mahanidana Sutta | DN 15 | Dependent origination |
| 12 | Sabbasava Sutta | MN 2 | All the taints |
| 13 | Vitakkasanthana Sutta | MN 20 | Removing distracting thoughts |
| 14 | Dvedhavitakka Sutta | MN 19 | Two kinds of thought |
| 15 | Kayagatasati Sutta | MN 119 | Mindfulness of body |
| 16 | Culavedalla Sutta | MN 44 | Feeling, perception, consciousness |
| 17 | Indriya Samyutta | SN 48 | Spiritual faculties |
| 18 | Bojjhanga Samyutta | SN 46 | Awakening factors |
| 19 | Nivarana Vagga | SN 46.51-55 | Hindrances and antidotes |
| 20 | Girimanandasutta | AN 10.60 | Ten perceptions for healing |

---

# PART 11: IMPLEMENTATION PHASES

## Phase 1: Static Mirror (MVP) — 3 weeks

- [ ] Single entry point: "What's on your mind?"
- [ ] Static question flows (6 flows, ~120 steps)
- [ ] The 24-Hour Vault with lock animation
- [ ] Crisis detection and resources
- [ ] Quick Capture
- [ ] Dark/light theme toggle
- [ ] IndexedDB storage
- [ ] Export/Import (two buttons)
- [ ] PWA (offline capable)
- [ ] Context-aware help system
- [ ] Landing page / website (GitHub Pages)
- [ ] GitHub deployment

## Phase 2: AI + Visualisations — 3 weeks

- [ ] BYOK Claude API integration
- [ ] Full Mirror conversation (AI-powered)
- [ ] Letter You'll Never Send (with burn animation)
- [ ] Emotional Weather Map
- [ ] Body Compass
- [ ] Reactive Message Rewriter
- [ ] Wisdom Feed

## Phase 3: Decision Tools — 2 weeks

- [ ] Decision Journal with Future Self Review
- [ ] Weekly pattern synthesis (BYOK)
- [ ] Cross-feature linking

## Phase 4: Practitioner Tools — 4 weeks

- [ ] Dhamma Mirror tab (settings toggle)
- [ ] Practice logging (all 7 features)
- [ ] Diagnostic tools (all 6 features)
- [ ] Body awareness (all 5 features)
- [ ] Scripture integration (all 4 features)
- [ ] Remaining 11 practice features

---

# PART 12: FILE STRUCTURE

```
dhamma-mirror/                    # Repo name stays (SEO, existing links)
├── public/
│   ├── index.html                # Landing page / website
│   ├── manifest.json             # PWA manifest
│   ├── favicon.svg
│   ├── icons/
│   └── wisdom/                   # Static wisdom content (JSON)
├── src/
│   ├── App.tsx
│   ├── main.tsx
│   ├── components/
│   │   ├── Header.tsx            # Theme toggle, help search
│   │   ├── HelpPanel.tsx         # Context-aware help slide-in
│   │   ├── CrisisBanner.tsx      # Crisis detection UI
│   │   └── ui/                   # Reusable UI components
│   ├── features/
│   │   ├── mirror/               # The Mirror
│   │   ├── vault/                # 24-Hour Vault
│   │   ├── letter/               # Letter You'll Never Send
│   │   ├── weather/              # Emotional Weather Map
│   │   ├── bodycompass/          # Body Compass
│   │   ├── decisions/            # Decision Journal
│   │   ├── rewriter/             # Reactive Message Rewriter
│   │   ├── wisdom/               # Wisdom Feed
│   │   ├── capture/              # Quick Capture
│   │   ├── crisis/               # Crisis Detection
│   │   └── dhamma/               # Practitioner tab (all 33 features)
│   ├── help/
│   │   └── helpContent.ts        # All contextual help entries
│   ├── hooks/
│   │   ├── useDatabase.ts
│   │   ├── useAI.ts
│   │   ├── useHelp.ts
│   │   └── useTheme.ts
│   ├── lib/
│   │   ├── database.ts           # IndexedDB operations
│   │   ├── ai.ts                 # AI provider (BYOK abstraction)
│   │   ├── staticFlows.ts        # Pre-written question flows
│   │   ├── crisisDetection.ts    # Keyword detection + resources
│   │   ├── paliDictionary.ts     # 220+ terms
│   │   ├── suttaData.ts          # Top 100 suttas (JSON)
│   │   ├── wisdomLibrary.ts      # Curated wisdom passages
│   │   └── exportImport.ts       # JSON export/import
│   └── data/
│       ├── staticFlows.json      # 6 question flows (~120 steps)
│       ├── paliTerms.json        # Full dictionary data
│       ├── suttas.json           # Top 100 suttas
│       ├── wisdomPassages.json   # Curated wisdom library
│       ├── crisisKeywords.json   # Crisis detection keywords
│       ├── crisisResources.json  # Localised crisis resources
│       └── helpContent.json      # Context-aware help entries
├── .github/
│   └── workflows/
│       └── deploy.yml            # GitHub Pages deployment
├── README.md
├── MANIFESTO.md
├── CONTRIBUTING.md
├── ATTRIBUTION.md
├── LICENSE
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── vite.config.ts
```

---

# PART 13: PATENT FILING PRIORITIES

File provisional patents for these three (they're genuinely novel):

| # | Innovation | Claim Direction |
|---|-----------|-----------------|
| 1 | **Emotional Weather Map** | System for representing emotional state time-series as dynamic weather-based visualisations with temporal playback |
| 2 | **Body Compass** | Body-sensation mapping system with emotional correlation analysis generating personalised somatic heatmaps |
| 3 | **Letter Burn Ritual** | Interactive letter composition with symbolic destruction rituals (animated burning) and AI reflective questioning |

---

# PART 14: ECOSYSTEM STANDARD — CONTEXT-AWARE HELP

**New rule for AMTL-ECO-STD-1.0 (to be added as Section 17):**

Every AMTL application — internal or external, desktop or web — must include context-aware help:

1. [?] icon on every screen/feature showing contextual guidance
2. First-time tooltips (dismissible, never return after dismissal)
3. "What can I do here?" summary on every major screen
4. Help content searchable from any screen
5. Tone: warm, plain English, written for Mani
6. Help content in structured JSON/YAML for maintainability

**New rule for AMTL-ECO-STD-1.0 (to be added as Section 18):**

Every AMTL application must have a website/landing page:

1. Explains what the app does (plain English)
2. Written using StoryBrand framework (user is hero, app is guide)
3. Follows AMTL brand guidelines (Midnight + Gold)
4. Includes quick-start guidance
5. Links to User Manual
6. Even internal apps get a launch page — no app opens to a blank screen

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | December 2025 | Mani Padisetti / Claude (Thalaiva) | Initial Dhamma Mirror spec |
| 2.0 | 18 February 2026 | Mani Padisetti / Claude (Thalaiva) | Complete rewrite as Socrates & Donuts. Incorporated feedback from 5 LLM reviews. 10 core features. No backend. GitHub Pages. Context-aware help. Website copy. |

---

*Almost Magic Tech Lab*
*"Wisdom and comfort. Questions and kindness."*
