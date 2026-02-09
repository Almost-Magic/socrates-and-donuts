# BESIDEYOU

## Complete Specification for Development

**Version:** 1.0  
**Date:** January 2026  
**Author:** Almost Magic Tech Lab  
**For:** Replit Development

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Vision & Purpose](#2-vision--purpose)
3. [Target Users](#3-target-users)
4. [Core Features](#4-core-features)
5. [Medical Glossary](#5-medical-glossary)
6. [AI Companion](#6-ai-companion)
7. [Tracking Features](#7-tracking-features)
8. [Support Resources](#8-support-resources)
9. [Emotional Support Features](#9-emotional-support-features)
10. [Technical Architecture](#10-technical-architecture)
11. [Data Storage](#11-data-storage)
12. [Design Requirements](#12-design-requirements)
13. [Accessibility](#13-accessibility)
14. [Content Guidelines](#14-content-guidelines)

---

## 1. Executive Summary

BesideYou is a **free, comprehensive cancer support platform** for Australian patients and caregivers. It provides medical term explanations, appointment preparation guides, symptom tracking, and emotional support — all in plain language, with no registration required.

### Repository & Hosting

- **Source Code:** GitHub (public repository)
- **Website:** GitHub Pages
- **Repository:** github.com/almostmagic/beside-you
- **License:** MIT
- **Created by:** Mani Padisetti, Sydney, Australia

### Key Principles

- **100% Free** — No cost, no premium tiers, no ads
- **Privacy-First** — All data stored locally on user's device only
- **Plain Language** — Medical complexity translated to human understanding
- **Australian Focus** — Medicare, PBS, local support services
- **Compassionate** — Built by someone who understands the journey

### What It Is NOT

- Not medical advice (always consult your doctor)
- Not a replacement for professional support
- Not a data collection tool
- Not a commercial product

---

## 2. Vision & Purpose

### Vision Statement

> "No one facing cancer should feel alone, confused, or overwhelmed by information they can't understand."

### Why This Exists

When someone hears "you have cancer," they're thrown into a world of:
- Medical terminology they've never encountered
- Appointments they don't know how to prepare for
- Emotions they don't know how to process
- Systems they don't know how to navigate

BesideYou sits beside them through all of it.

### Goals

1. Help patients and caregivers understand what they're hearing
2. Prepare them for appointments so they can advocate for themselves
3. Track symptoms so they can communicate clearly with their care team
4. Connect them with support services they didn't know existed
5. Provide moments of comfort when everything feels overwhelming

---

## 3. Target Users

### Primary: Cancer Patients

**Who they are:**
- Recently diagnosed (overwhelmed, scared, confused)
- In treatment (exhausted, managing side effects)
- Post-treatment (navigating "new normal")
- Any cancer type, any stage

**What they need:**
- Understanding of what's happening to them
- Help preparing for appointments
- Tracking tools for symptoms and medications
- Emotional support at 3am when they can't sleep

### Secondary: Caregivers

**Who they are:**
- Partners, children, parents, friends supporting someone with cancer
- Often forgotten in the care system
- Exhausted, scared, trying to be strong

**What they need:**
- Understanding of what their person is going through
- Guidance on how to support effectively
- Permission to take care of themselves too
- Resources for caregiver-specific support

### Tertiary: Family Members

- Wanting to understand what's happening
- Wanting to help but not knowing how
- Processing their own grief and fear

---

## 4. Core Features

### Feature Overview

| Feature | Description | Priority |
|---------|-------------|----------|
| Medical Glossary | 1,499 terms in plain language | P0 |
| AI Companion | Conversational support with voice | P0 |
| Symptom Tracker | Log and export symptoms | P0 |
| Medication Tracker | Manage medications and schedules | P1 |
| Appointment Prep | Question lists by appointment type | P0 |
| Care Team Directory | Store contact details | P1 |
| My Journey Timeline | Track milestones | P2 |
| Hospital Bag Checklists | Practical preparation | P1 |
| Support Resources | Australian services directory | P0 |
| Good Days Jar | Capture positive moments | P2 |
| Moments of Peace | Breathing, quotes, gentle support | P1 |
| Emergency Mode | "I Need Help Right Now" | P0 |

---

## 5. Medical Glossary

### Overview

1,499 medical terms explained in plain, compassionate language. Organised by category with search functionality.

### Categories

1. **Cancer Types** (100+ terms)
   - Breast cancer, lung cancer, leukaemia, lymphoma, etc.
   - Each with plain-language explanation

2. **Treatment Terms** (200+ terms)
   - Chemotherapy, radiation, immunotherapy, surgery types
   - Side effects, protocols, cycles

3. **Medical Procedures** (150+ terms)
   - Scans (CT, MRI, PET)
   - Biopsies, blood tests
   - What to expect

4. **Anatomy & Body** (100+ terms)
   - Body parts mentioned in cancer care
   - Systems affected

5. **Medications** (200+ terms)
   - Common cancer drugs
   - Support medications
   - Side effect management

6. **Lab Results** (100+ terms)
   - Blood count terms
   - Tumour markers
   - What numbers mean

7. **Side Effects** (150+ terms)
   - Physical side effects
   - Emotional effects
   - Management strategies

8. **Care Team Roles** (50+ terms)
   - Oncologist, radiation therapist, etc.
   - What each person does

9. **Australian Healthcare** (50+ terms)
   - Medicare, PBS, private health
   - Hospital systems

### Term Structure

```typescript
interface GlossaryTerm {
  term: string;
  pronunciation?: string;
  plainLanguage: string;        // 2-3 sentences max
  longerExplanation?: string;   // Optional deeper detail
  relatedTerms: string[];
  category: TermCategory;
  tags: string[];
}
```

### Example Entry

```json
{
  "term": "Metastatic",
  "pronunciation": "meh-tah-STAT-ik",
  "plainLanguage": "When cancer has spread from where it started to another part of the body. For example, breast cancer that spreads to the bones is still breast cancer — it's called 'metastatic breast cancer' or 'breast cancer with bone metastases.'",
  "longerExplanation": "Cancer spreads through the bloodstream or lymphatic system. When it arrives somewhere new, it creates a 'metastasis' (plural: metastases). This changes treatment options but doesn't mean treatment isn't possible.",
  "relatedTerms": ["Primary cancer", "Secondary cancer", "Metastasis", "Stage 4"],
  "category": "basics",
  "tags": ["staging", "spread", "common term"]
}
```

---

## 6. AI Companion

### Overview

A conversational AI that helps users understand medical information, prepare for appointments, and feel supported. Uses Groq API (free tier) for responses.

### Key Capabilities

1. **Explain Medical Terms**
   - "What is HER2 positive?"
   - "What does 'margins' mean in my pathology report?"

2. **Appointment Preparation**
   - "I'm seeing my oncologist tomorrow about chemo. What should I ask?"
   - "Help me prepare for my radiation planning appointment"

3. **Side Effect Guidance**
   - "Is it normal to feel nauseous three days after chemo?"
   - "What can I do about mouth sores?"

4. **Emotional Support**
   - "I can't stop crying"
   - "I'm scared about my scan results"

5. **Caregiver Support**
   - "How do I support my wife through treatment?"
   - "I'm exhausted. Is that normal?"

### Voice Input (Critical Feature)

**Prominent voice input button** — because when you're exhausted or crying or your hands are shaking, typing is hard.

```
┌────────────────────────────────────┐
│  How can I help you today?         │
│                                    │
│  [────────────────────────────]    │
│                                    │
│         🎤 Tap to speak            │
│         (or type below)            │
│                                    │
└────────────────────────────────────┘
```

### AI Boundaries

**The AI will:**
- Explain medical terms in plain language
- Provide general information about treatments
- Suggest questions to ask doctors
- Offer emotional support and validation
- Direct to appropriate resources

**The AI will NOT:**
- Provide medical advice
- Interpret specific test results
- Recommend treatments
- Replace professional medical care
- Make prognoses

### System Prompt

```
You are BesideYou, a compassionate companion for people affected by cancer.

Your role:
- Explain medical terms in plain, warm language
- Help prepare for appointments
- Provide emotional support and validation
- Connect people with Australian support resources

Always:
- Use Australian English spelling
- Be warm, gentle, and human
- Acknowledge their feelings before providing information
- Remind them you're not a doctor when appropriate
- Keep responses concise (people are tired)

Never:
- Provide medical advice
- Interpret specific test results
- Make predictions about outcomes
- Minimise their feelings
- Use jargon without explaining it

If someone is in crisis:
- Acknowledge their distress
- Provide Lifeline (13 11 14) and Cancer Council (13 11 20)
- Stay with them, don't rush to solutions
```

### Technical Implementation

```typescript
// Groq API integration (free tier)
const GROQ_API_KEY = 'user-provided-optional';
const GROQ_MODEL = 'llama3-8b-8192';

async function getAIResponse(
  userMessage: string, 
  conversationHistory: Message[]
): Promise<string> {
  // Falls back to local responses if no API key
}
```

---

## 7. Tracking Features

### Symptom Tracker

**Purpose:** Help patients track symptoms to communicate clearly with their care team.

**Features:**
- Log symptoms with severity (1-10)
- Add notes
- Track over time
- Export as PDF for appointments
- Common symptom templates

**Data Model:**

```typescript
interface SymptomEntry {
  id: string;
  timestamp: Date;
  symptom: string;
  severity: number;          // 1-10
  notes?: string;
  duration?: string;
  triggers?: string;
  relief?: string;
}
```

**Common Symptoms (Pre-populated):**
- Fatigue
- Nausea
- Pain (with location)
- Appetite changes
- Sleep problems
- Mood changes
- Temperature
- Mouth sores
- Neuropathy (tingling/numbness)

### Medication Tracker

**Purpose:** Keep track of all medications, dosages, and schedules.

**Features:**
- Add medications with dosage and schedule
- Set reminders (optional)
- Track when taken
- Export current medication list for appointments

**Data Model:**

```typescript
interface Medication {
  id: string;
  name: string;
  dosage: string;
  frequency: string;
  purpose?: string;
  prescribedBy?: string;
  startDate?: Date;
  endDate?: Date;
  notes?: string;
  reminders: boolean;
}
```

### Exportable Reports

**PDF Export includes:**
- Date range
- Symptom summary with charts
- Current medications
- Notes for doctor
- Questions to ask

---

## 8. Support Resources

### Australian Resources Directory

**Cancer Council:**
- 13 11 20 (Cancer Council Helpline)
- State-specific services
- Financial assistance
- Transport to treatment
- Accommodation

**Financial Support:**
- Centrelink Cancer Support
- Pharmaceutical Benefits Scheme (PBS)
- Patient assistance programs
- State-specific grants

**Practical Support:**
- Transport services
- Accommodation near hospitals
- Home help services
- Meal delivery

**Emotional Support:**
- Counselling services
- Support groups (online and in-person)
- Peer support programs
- Caregiver support

**Specialist Services:**
- Canteen (young people)
- CanTeen Parents
- Breast Cancer Network Australia
- Prostate Cancer Foundation
- Leukaemia Foundation
- Etc. by cancer type

### Data Structure

```typescript
interface SupportResource {
  name: string;
  phone?: string;
  website?: string;
  description: string;
  category: 'financial' | 'practical' | 'emotional' | 'medical';
  cancerTypes?: string[];      // If specific
  states?: AustralianState[];  // If state-specific
  forPatients: boolean;
  forCaregivers: boolean;
}
```

---

## 9. Emotional Support Features

### Emergency Mode: "I Need Help Right Now"

**Always accessible button** — when everything is too much.

**What it shows:**
1. **Breathing exercise** — Simple, guided, immediate
2. **Crisis contacts** — Lifeline, Cancer Council, Beyond Blue
3. **Gentle reminders** — "You're still here. That matters."
4. **Option to call** — One-tap to Lifeline

### Good Days Jar

**Purpose:** Capture good moments to revisit on hard days.

**How it works:**
- Simple text entry: "What was good today?"
- Date stamped automatically
- Browse past entries when needed
- Gentle prompt: "Would you like to add something to your jar?"

### Moments of Peace

**Gentle micro-interactions:**
- Breathing exercises (various durations)
- Calming quotes
- Nature sounds (optional)
- "Just be here for a moment"

### Scanxiety Companion

**For the anxiety before scan results:**
- Acknowledgment: "Waiting is hard. Your feelings are valid."
- Distraction tools
- Grounding exercises
- Reminder: "Whatever the results, you'll face it. You've faced hard things before."

---

## 10. Technical Architecture

### Core Principle: Single-File PWA

BesideYou is a **single HTML file** that works completely offline. No installation, no app store, no accounts.

### Tech Stack

```
Core:
- Single HTML file with embedded CSS/JS
- Works offline after first load
- Progressive Web App (installable)

AI Integration:
- Groq API (free tier) for AI companion
- Falls back to local responses if offline
- API key stored locally (user provides)

Storage:
- localStorage for all user data
- IndexedDB for larger datasets (glossary)
- Export/import via JSON for backup
```

### Architecture

```
┌─────────────────────────────────────────────────────┐
│                    BROWSER                           │
│  ┌─────────────────────────────────────────────┐    │
│  │              BesideYou.html                  │    │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐       │    │
│  │  │ Glossary│ │Companion│ │ Tracker │       │    │
│  │  │  1,499  │ │  (AI)   │ │Symptoms │       │    │
│  │  │  terms  │ │         │ │  Meds   │       │    │
│  │  └─────────┘ └─────────┘ └─────────┘       │    │
│  │                    │                        │    │
│  │            ┌───────┴───────┐               │    │
│  │            │  localStorage │               │    │
│  │            │  (encrypted)  │               │    │
│  │            └───────────────┘               │    │
│  └─────────────────────────────────────────────┘    │
│                                                      │
│  Optional: Groq API for AI (user provides key)      │
└─────────────────────────────────────────────────────┘

All data stays on user's device. Nothing sent anywhere.
```

### File Structure (for development)

```
beside-you/
├── src/
│   ├── index.html          # Main entry
│   ├── styles/
│   │   └── main.css
│   ├── scripts/
│   │   ├── app.js          # Main app logic
│   │   ├── glossary.js     # Glossary functionality
│   │   ├── companion.js    # AI companion
│   │   ├── tracker.js      # Symptom/med tracking
│   │   └── storage.js      # Local storage handling
│   └── data/
│       ├── glossary.json   # 1,499 terms
│       └── resources.json  # Support resources
├── build/
│   └── beside-you.html     # Single-file output
└── package.json
```

### Build Process

Combine everything into a single HTML file:
- Inline all CSS
- Inline all JS
- Embed glossary data
- Result: One file, works anywhere

---

## 11. Data Storage

### Local Storage Schema

```typescript
// All stored in localStorage, never sent anywhere

interface BesideYouData {
  // User preferences
  preferences: {
    hasSeenWelcome: boolean;
    cancerType?: string;
    role: 'patient' | 'caregiver' | 'family';
    groqApiKey?: string;    // Optional, for AI
  };
  
  // Symptom tracking
  symptoms: SymptomEntry[];
  
  // Medications
  medications: Medication[];
  
  // Care team
  careTeam: CareTeamMember[];
  
  // Good days jar
  goodDays: GoodDayEntry[];
  
  // Journey timeline
  milestones: Milestone[];
  
  // Conversation history (limited)
  recentConversations: Message[];
}
```

### Backup & Restore

**Export:**
- One-click export to JSON file
- User saves to their device
- Encrypted option available

**Import:**
- Upload JSON file
- Validates data
- Merges or replaces

### Privacy

- **No accounts** — nothing to hack
- **No servers** — nothing to breach
- **No tracking** — no analytics
- **Your data is yours** — lives on your device only

---

## 12. Design Requirements

### Visual Design

**Colour Palette:**
- Primary: Soft Teal (#4A9B8F) — calming, healing
- Secondary: Warm Cream (#F5F0E6) — gentle, soft
- Accent: Soft Gold (#C9944A) — warmth, hope
- Text: Dark Grey (#2D2B27) — readable, not harsh
- Background: Warm White (#FAFAF7)
- Success: Soft Green (#6B9B7A)
- Alert: Soft Amber (#D4A04A)

**Typography:**
- Body: 18px minimum (people are tired, eyes may be strained)
- Line height: 1.8 (generous, easy to read)
- Font: Warm, readable sans-serif
- Headings: Friendly, not clinical

**Layout:**
- Generous whitespace (breathing room)
- Large touch targets (for shaky hands)
- Clear visual hierarchy
- No clutter, no overwhelm

### Tone of Voice

- **Warm** — like a friend sitting beside you
- **Clear** — no jargon, no confusion
- **Gentle** — soft, not clinical
- **Respectful** — of their intelligence and autonomy
- **Honest** — doesn't minimise, doesn't catastrophise

### Key UI Principles

1. **Voice input is prominent** — not hidden, not secondary
2. **Emergency help is always visible** — one tap away
3. **Nothing is mandatory** — use what helps, ignore what doesn't
4. **Progress is celebrated** — but not performatively
5. **It's okay to close the app** — no guilt, no streaks

---

## 13. Accessibility

### Requirements (WCAG 2.1 AA+)

- **Contrast:** 4.5:1 minimum (aim for 7:1)
- **Text size:** User-adjustable, minimum 18px
- **Touch targets:** 44x44px minimum
- **Keyboard:** Full navigation
- **Screen readers:** Complete compatibility
- **Reduced motion:** Respect user preference
- **Focus indicators:** Clear and visible

### Special Considerations

1. **Cognitive load** — People are exhausted. Keep it simple.
2. **Motor control** — Chemo affects fine motor skills. Large buttons.
3. **Vision** — Treatments can affect vision. High contrast option.
4. **Fatigue** — Short interactions, easy to pause and return.

---

## 14. Content Guidelines

### Writing for Cancer Patients

**Do:**
- Use plain language
- Be direct but gentle
- Acknowledge feelings first
- Keep it short (fatigue is real)
- Use "you" not "patients"

**Don't:**
- Use medical jargon without explanation
- Minimise ("at least it's not...")
- Be falsely cheerful
- Overwhelm with information
- Make assumptions about their journey

### Example Transformations

**Medical → Plain Language:**

Before: "The patient may experience myelosuppression as a result of cytotoxic therapy."

After: "Your white blood cells might drop during treatment. This is called myelosuppression — it's common and your team will monitor it."

**Clinical → Human:**

Before: "Nausea management strategies include anti-emetic medications."

After: "Feeling sick is one of the most common side effects. There are good medications to help, and your nurse can adjust them until you find what works for you."

---

## Appendix A: Appointment Preparation Guides

### First Oncology Appointment

**Questions to Consider:**
- What type of cancer do I have?
- What stage is it?
- What are my treatment options?
- What do you recommend, and why?
- What are the side effects?
- How long will treatment take?
- What should I do before my next appointment?

**Practical Tips:**
- Bring someone to take notes
- It's okay to record the conversation (ask first)
- You don't have to decide today
- Write down questions beforehand

### Chemotherapy Consultation

**Questions:**
- What drugs will I receive?
- How is it given and how long does it take?
- How often will I have treatment?
- What side effects should I expect?
- What can I do about side effects?
- Can I work during treatment?
- Who do I call if I have problems?

### And more... (Radiation, Surgery, Follow-up, etc.)

---

## Appendix B: Hospital Bag Checklists

### Day Treatment Checklist
- [ ] Medicare card and health fund card
- [ ] List of current medications
- [ ] Phone and charger
- [ ] Headphones
- [ ] Book or tablet
- [ ] Snacks
- [ ] Water bottle
- [ ] Warm layer (treatment rooms are cold)
- [ ] Lip balm (dry from treatment)
- [ ] Hand sanitiser

### Overnight Stay Checklist
*[Extended list...]*

---

## Appendix C: Launch Requirements

### MVP Features (Must Have)

1. ✅ Medical glossary (full 1,499 terms)
2. ✅ AI companion with voice input
3. ✅ Symptom tracker with export
4. ✅ Appointment preparation guides
5. ✅ Australian support resources
6. ✅ Emergency "I Need Help" mode
7. ✅ Works offline
8. ✅ Fully accessible

### Phase 2 Features

- Medication reminders
- Care team directory
- My Journey timeline
- Good Days Jar
- Peer connection (opt-in)

---

## Appendix D: GitHub Hosting & Deployment

### Repository Setup

**Repository Name:** `beside-you`  
**Owner:** Almost Magic Tech Lab  
**Visibility:** Public (open source)  
**License:** MIT

### Instructions for Replit

Please push the completed code to GitHub and set up GitHub Pages:

1. Create repository at `github.com/almostmagic/beside-you`
2. Push all code with proper `.gitignore`
3. Enable GitHub Pages (Settings → Pages → Deploy from branch: `main`, folder: `/docs` or root)
4. Include comprehensive README.md
5. The single HTML file should work directly on GitHub Pages

### GitHub Pages URL

Primary: `https://almostmagic.github.io/beside-you`  
Custom domain (optional): `beside-you.almostmagic.com.au`

### README.md Template

```markdown
# BesideYou

A free cancer support companion for patients and caregivers.

## What This Is

BesideYou helps people facing cancer understand their journey. Medical terms 
explained simply. Appointment preparation guides. Symptom tracking. Australian 
support resources. All in one place, all free, all private.

**No accounts. No tracking. No cost. Just support.**

## Live Site

[beside-you.almostmagic.com.au](https://beside-you.almostmagic.com.au)  
or [almostmagic.github.io/beside-you](https://almostmagic.github.io/beside-you)

## Features

- 📚 1,499 medical terms explained in plain language
- 💬 AI companion with voice input (for when you're too tired to type)
- 📊 Symptom tracker with printable reports
- 📋 Appointment preparation guides
- 🆘 Emergency "I Need Help Right Now" mode
- 🇦🇺 Australian support resources
- 🔒 100% private (all data stays on your device)
- 📴 Works offline

## How It Works

BesideYou is a single HTML file. Download it, open it in a browser, and 
everything works — even without internet. Your data never leaves your device.

## For Developers

### Running Locally

\`\`\`bash
# Clone repository
git clone https://github.com/almostmagic/beside-you.git
cd beside-you

# Open in browser
open index.html
# or
python -m http.server 8000
# then visit http://localhost:8000
\`\`\`

### Building from Source

\`\`\`bash
# Install dependencies
npm install

# Build single-file version
npm run build

# Output: dist/beside-you.html
\`\`\`

## Contributing

We welcome contributions! See [CONTRIBUTING.md](./CONTRIBUTING.md).

**We do not accept monetary contributions.** This is a gift.

## License

MIT License - see [LICENSE](./LICENSE)

## Created By

Created by Mani Padisetti at [Almost Magic Tech Lab](https://almostmagic.com.au), 
Sydney, Australia.

For those facing cancer: You are not alone.
```

---

## Appendix E: Contributing Guidelines

### CONTRIBUTING.md

```markdown
# Contributing to BesideYou

Thank you for wanting to help people facing cancer.

## Important Notes

**We do not accept monetary contributions.** This project exists to help 
people during one of the hardest times in their lives. If you want to 
support the mission, contribute your skills.

## Ways to Contribute

### 1. Cancer-Specific Extensions

Create specialised versions for specific cancers:

- **Breast cancer companion** — Specific terminology, resources, journey stages
- **Prostate cancer companion** — Male-specific guidance and resources
- **Childhood cancer companion** — Resources for parents, age-appropriate content
- **Blood cancer companion** — Leukaemia, lymphoma specific content
- **Lung cancer companion** — Specific terminology and resources
- **Other cancer types** — Colorectal, pancreatic, ovarian, etc.

**To contribute a cancer-specific extension:**
1. Fork the repository
2. Create a new branch: `cancer/[cancer-type]`
3. Add cancer-specific glossary terms
4. Add cancer-specific appointment guides
5. Add cancer-specific resources
6. Submit a pull request

### 2. Country/Region Adaptations

BesideYou is built for Australia. We welcome adaptations for other countries:

**Priority countries:**
- **New Zealand** — Similar healthcare system
- **United Kingdom** — NHS resources, UK terminology
- **United States** — Insurance considerations, US resources
- **Canada** — Provincial health systems
- **Ireland** — Irish Cancer Society resources

**To contribute a country adaptation:**
1. Fork the repository
2. Create a new branch: `country/[country-code]`
3. Replace Australian resources with local equivalents
4. Update terminology (e.g., "GP" → "PCP" for US)
5. Add country-specific support services
6. Ensure phone numbers and websites are correct
7. Submit a pull request

### 3. Language Translations

Help people access BesideYou in their language:

- Plain language medical explanations in other languages
- Cultural sensitivity in tone and approach
- Local idioms for comfort and support

**Note:** Medical translations should be reviewed by native speakers 
with medical knowledge.

### 4. Glossary Expansion

Add or improve medical terms:

- New terms (especially for specific cancer types)
- Better plain-language explanations
- Pronunciation guides
- Related terms linking

### 5. Accessibility Improvements

- Screen reader improvements
- High contrast themes
- Larger text options
- Simplified navigation for cognitive accessibility

### 6. AI Companion Improvements

- Better responses for specific situations
- Improved emotional support
- More accurate medical explanations
- Better crisis detection

### 7. Bug Fixes and Code Improvements

- Fix bugs
- Improve performance
- Better offline support
- Reduced file size

## Content Guidelines

When contributing content, please ensure:

1. **Plain language** — Explain like you're talking to a friend
2. **Compassionate tone** — Remember users are scared and tired
3. **Accuracy** — Medical information must be correct
4. **No medical advice** — We explain, we don't diagnose or recommend
5. **Australian English** — For the main version (use local spelling for adaptations)

## How to Contribute

1. **Fork** the repository
2. **Create a branch** for your contribution
3. **Make your changes** with clear commit messages
4. **Test** thoroughly (especially offline functionality)
5. **Submit a pull request** with a clear description

## Testing Contributions

Before submitting:

- [ ] Works offline
- [ ] Works on mobile
- [ ] Accessible (keyboard navigation, screen reader)
- [ ] Medical terms are accurate
- [ ] Tone is compassionate
- [ ] No broken links

## Questions?

Open an issue or contact us at contribute@almostmagic.com.au

## License

By contributing, you agree that your contributions will be licensed 
under the MIT License.

---

Created by Mani Padisetti at Almost Magic Tech Lab, Sydney, Australia.

For everyone facing cancer: You are not alone. We're beside you.
```

---

*Document Version: 1.0*  
*Last Updated: January 2026*  
*Created by: Mani Padisetti, Sydney, Australia*  
*Almost Magic Tech Lab*

*For those facing cancer: You are not alone. We're beside you.*

---

# APPENDIX D: GITHUB & DEPLOYMENT INSTRUCTIONS

## Repository Setup

### For Replit: Push to GitHub

```bash
# Initialize git if not already done
git init

# Add remote
git remote add origin https://github.com/almostmagic/beside-you.git

# Create .gitignore
cat > .gitignore << 'EOF'
node_modules/
dist/
.env
*.log
.DS_Store
EOF

# Initial commit
git add .
git commit -m "Initial commit: BesideYou"

# Push to GitHub
git push -u origin main
```

### Repository Structure

```
beside-you/
├── .github/
│   ├── workflows/
│   │   └── deploy.yml          # GitHub Actions for deployment
│   ├── CONTRIBUTING.md
│   ├── CODE_OF_CONDUCT.md
│   └── ISSUE_TEMPLATE/
│       ├── bug_report.md
│       ├── feature_request.md
│       ├── new_cancer_type.md
│       └── new_country.md
├── src/
│   ├── index.html
│   ├── styles/
│   ├── scripts/
│   └── data/
│       ├── glossary.json
│       └── resources/
│           ├── australia.json
│           └── [other countries]
├── docs/                        # Documentation
├── LICENSE                      # MIT License
└── README.md
```

## GitHub Pages Deployment

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    permissions:
      contents: read
      pages: write
      id-token: write
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          
      - name: Install dependencies
        run: npm ci
        
      - name: Build
        run: npm run build
          
      - name: Setup Pages
        uses: actions/configure-pages@v4
        
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: './dist'
          
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

### Custom Domain Setup

1. In GitHub repository settings → Pages
2. Set custom domain: `besideyou.com.au`
3. Enable "Enforce HTTPS"
4. Add DNS records:
   ```
   A     @     185.199.108.153
   A     @     185.199.109.153
   A     @     185.199.110.153
   A     @     185.199.111.153
   CNAME www   almostmagic.github.io
   ```

---

# APPENDIX E: CONTRIBUTION GUIDELINES

## CONTRIBUTING.md

```markdown
# Contributing to BesideYou

Thank you for your interest in contributing to BesideYou. This project helps 
cancer patients and caregivers navigate one of life's most difficult journeys, 
and we welcome contributions that extend its reach and usefulness.

## Created By

BesideYou was created by Mani Padisetti in Sydney, Australia, as part of 
Almost Magic Tech Lab.

## How You Can Contribute

### 1. Add Cancer-Specific Resources

Help us create dedicated sections for specific cancer types:

**Currently Needed:**
- Breast Cancer
- Prostate Cancer
- Lung Cancer
- Bowel/Colorectal Cancer
- Melanoma
- Leukaemia & Lymphoma
- Brain Cancer
- Pancreatic Cancer
- Ovarian Cancer
- And others...

**What's needed for each:**
- Cancer-specific glossary terms
- Treatment-specific side effects
- Relevant clinical trials information
- Cancer-specific support organisations
- Appointment preparation guides for specialists
- Common questions for oncologists

### 2. Adapt for Other Countries

BesideYou is currently Australia-focused. Help us create versions for:

**Priority Countries:**
- New Zealand
- United Kingdom
- United States
- Canada
- Ireland

**What's needed:**
- Local healthcare system information
- Country-specific support organisations
- Financial assistance programs
- Treatment access information
- Crisis support contacts
- Local terminology and spelling

### 3. Add Medical Terms to Glossary

Our glossary has 1,499 terms, but medicine is vast. Help us add:
- Missing cancer terms
- New treatment terminology
- Regional variations
- Plain-language explanations

**Requirements:**
- Terms must be explained in plain language
- No medical jargon in definitions
- Include pronunciation where helpful
- Cite medical sources

### 4. Translate Content

Help make BesideYou available in other languages:
- Mandarin
- Vietnamese
- Arabic
- Greek
- Italian
- Hindi
- And others...

### 5. Improve Accessibility

- Test with screen readers
- Report accessibility issues
- Improve keyboard navigation
- Test with low vision simulators

### 6. Add Support Resources

Help us maintain current information for:
- Financial assistance programs
- Transport services
- Accommodation
- Counselling services
- Peer support groups

### 7. Fix Bugs and Improve Code

- Report bugs via GitHub Issues
- Submit pull requests for fixes
- Improve documentation
- Optimise performance

## How to Contribute

1. **Fork the repository**
2. **Create a branch** for your contribution
3. **Make your changes**
4. **Test thoroughly** (especially accessibility)
5. **Submit a pull request**

## Contribution Standards

### Content Standards

**Language:**
- Plain, accessible language
- No medical jargon without explanation
- Warm, compassionate tone
- Never condescending

**Accuracy:**
- Cite sources for medical information
- Verify support organisation details
- Include "last verified" dates for resources
- Flag information that may change

**Sensitivity:**
- Remember readers may be exhausted, scared, or grieving
- Never give false hope or make promises
- Don't minimise the experience
- Include appropriate disclaimers

### Code Standards

- Follow existing code style
- Include tests for new features
- Ensure accessibility compliance (WCAG 2.1 AA)
- Test offline functionality
- Update documentation

### Pull Requests

- Clear description of changes
- Reference any related issues
- One feature/fix per pull request
- Include screenshots for UI changes

## What We Don't Accept

### No Monetary Contributions

We do not accept financial donations or sponsorships for this project. 
BesideYou is a free gift to people facing cancer and will remain so.

If you want to support this work, contribute your time and expertise instead.

### No Commercial Content

- No affiliate links
- No paid product placements
- No advertising
- No sponsored content

### No Medical Advice

- No treatment recommendations
- No prognosis information
- No "miracle cure" content
- No content that could delay proper medical care

### No Low-Quality Submissions

- No AI-generated content without human review
- No unverified medical information
- No placeholder or incomplete contributions
- No content that hasn't been sensitivity-reviewed

## Special Guidelines for Cancer-Specific Content

When adding content for specific cancer types:

1. **Consult reliable sources:**
   - Cancer Council Australia
   - Peter MacCallum Cancer Centre
   - Cancer Research UK
   - National Cancer Institute (US)
   - Peer-reviewed journals

2. **Include disclaimers:**
   - "This information is general and may not apply to your situation"
   - "Always consult your medical team for advice specific to you"

3. **Be sensitive to prognosis:**
   - Don't include survival statistics prominently
   - Focus on support and understanding, not outcomes
   - Remember people at all stages use this resource

4. **Consider caregivers:**
   - Include information relevant to those supporting patients
   - Acknowledge caregiver burden
   - Provide caregiver-specific resources

## Special Guidelines for Country Adaptations

When adapting for other countries:

1. **Research thoroughly:**
   - Healthcare system structure
   - Insurance/funding models
   - Patient rights and pathways
   - Local terminology

2. **Verify all resources:**
   - Phone numbers and websites
   - Opening hours and availability
   - Eligibility requirements
   - Geographic coverage

3. **Respect local context:**
   - Healthcare may work very differently
   - Don't assume Australian structures apply
   - Consult local cancer organisations

4. **Maintain the tone:**
   - Warm, human, supportive
   - Same philosophy, local details

## Code of Conduct

Be respectful. Be compassionate. Be patient.

Remember that contributors and users may themselves be affected by cancer. 
Approach all interactions with empathy.

We have zero tolerance for:
- Dismissive or insensitive comments about cancer
- Harassment of any kind
- Medical misinformation
- Commercial exploitation

## Questions?

Open an issue on GitHub or contact: contribute@almostmagic.com.au

---

Thank you for helping us support more people through cancer.
```

## Issue Templates

### New Cancer Type Template

```markdown
# .github/ISSUE_TEMPLATE/new_cancer_type.md

---
name: New Cancer Type Resources
about: Add resources for a specific cancer type
title: '[CANCER TYPE] Add resources for [Cancer Name]'
labels: enhancement, cancer-specific
---

## Cancer Type
[e.g., Breast Cancer, Prostate Cancer, Melanoma]

## Glossary Terms Needed
- [ ] List cancer-specific terms to add
- [ ] Include plain-language definitions

## Treatment-Specific Information
- [ ] Common treatments for this cancer
- [ ] Typical side effects
- [ ] What to expect during treatment

## Specialist Appointments
- [ ] Types of specialists patients will see
- [ ] Questions to ask each specialist

## Support Organisations (Australia)
- [ ] Cancer-specific support groups
- [ ] Phone numbers and websites
- [ ] What support they offer

## Clinical Trials
- [ ] Where to find trials for this cancer
- [ ] Questions to ask about trials

## Additional Resources
- [ ] Books, websites, apps
- [ ] Peer support communities

## Sources
- [ ] List sources for all information

## Your Background
[Optional: Your connection to this cancer type - patient, caregiver, 
healthcare worker, researcher]
```

### New Country Template

```markdown
# .github/ISSUE_TEMPLATE/new_country.md

---
name: New Country Adaptation
about: Adapt BesideYou for a new country
title: '[COUNTRY] Adapt for [Country Name]'
labels: enhancement, internationalisation
---

## Country
[e.g., New Zealand, United Kingdom, Canada]

## Healthcare System Overview
- [ ] Public/private system structure
- [ ] How cancer care is accessed
- [ ] Costs and funding

## Major Cancer Organisations
- [ ] National cancer charity/council
- [ ] Cancer-specific organisations
- [ ] Phone numbers and websites

## Crisis Support
- [ ] Mental health crisis lines
- [ ] Cancer-specific helplines
- [ ] 24/7 availability

## Financial Support
- [ ] Government assistance programs
- [ ] Charity grants
- [ ] Insurance considerations

## Practical Support
- [ ] Transport to treatment
- [ ] Accommodation near hospitals
- [ ] Home help services

## Language/Terminology
- [ ] Spelling preferences (UK/US English)
- [ ] Local medical terminology
- [ ] Healthcare system terms

## Sources
- [ ] Official health department
- [ ] Cancer organisations
- [ ] Patient advocacy groups

## Your Background
[Optional: Your connection to cancer care in this country]
```

---

# APPENDIX F: SECURITY REQUIREMENTS

## Two-Factor Authentication (2FA)

### GitHub Repository

All maintainers must have 2FA enabled:

```yaml
GitHub Repository:
  - All maintainers must have 2FA enabled
  - Branch protection requires 2FA
  - No exceptions for any collaborator
```

### Branch Protection Rules

```javascript
// Apply via GitHub Settings → Branches → Add rule
{
  "branch": "main",
  "required_status_checks": {
    "strict": true,
    "contexts": ["build", "test", "accessibility"]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true
  },
  "restrictions": null,
  "required_linear_history": true,
  "allow_force_pushes": false,
  "allow_deletions": false
}
```

### Content Security

Since BesideYou handles sensitive emotional content:

```yaml
Content Review:
  - All medical content reviewed by qualified person
  - Crisis resources verified quarterly
  - No user data collection whatsoever
  - No analytics that could identify users
```

---

## README.md

```markdown
# BesideYou

**Free cancer support platform for patients and caregivers.**

When you hear "you have cancer," you're thrown into a world of medical 
terminology, overwhelming appointments, and emotions you don't know how 
to process. BesideYou sits beside you through all of it.

🌐 **Website:** [besideyou.com.au](https://besideyou.com.au)

## What's Inside

- **Medical Glossary** — 1,499 terms explained in plain language
- **AI Companion** — Ask questions, get compassionate answers
- **Symptom Tracker** — Log symptoms, export for appointments
- **Appointment Prep** — Know what to ask before you go
- **Support Resources** — Australian services and organisations
- **Moments of Peace** — When you need to just breathe

## Privacy

- No registration required
- No data sent to servers
- Everything stored locally on your device
- Export and delete anytime

## Contributing

We welcome contributions! See [CONTRIBUTING.md](.github/CONTRIBUTING.md) for:

- **Adding cancer-specific resources** (breast, prostate, lung, etc.)
- **Adapting for other countries** (NZ, UK, US, Canada, etc.)
- **Expanding the glossary**
- **Improving accessibility**
- **Translating content**

**Note:** We do not accept monetary contributions.

## License

MIT License — see [LICENSE](LICENSE)

## Created By

**Mani Padisetti**  
Sydney, Australia  
[Almost Magic Tech Lab](https://almostmagic.com.au)

---

*For those facing cancer: You are not alone. We're beside you.*
```
