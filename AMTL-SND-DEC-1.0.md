# Socrates & Donuts — Decision Register
## Document Code: AMTL-SND-DEC-1.0
## Almost Magic Tech Lab
## 19 February 2026

> *This document follows AMTL-ECO-STD v1.0. All conventions defined there apply unless explicitly overridden with a Decision Register entry.*

---

## Active Decisions

### DEC-001: Dual-Mode Architecture (Website + Desktop)

| Field | Value |
|-------|-------|
| Date | 19 February 2026 |
| Context | S&D needs to be accessible as open-source (zero friction) AND as a full-featured desktop app with local storage and native LLM connections |
| Decision | Build two modes sharing the same question bank and UI: (1) static website on GitHub Pages using localStorage, (2) Electron + Flask desktop app using SQLite |
| Rationale | Website is the entry point — zero install, zero registration. Desktop is the "real" version — file system storage solves localStorage fragility, native Ollama connection solves LLM integration, privacy story becomes bulletproof ("data never leaves your machine, not even your browser") |
| Decided by | Mani Padisetti / Claude (Thalaiva) |
| Affects | AMTL-SND-TDD-1.0 (architecture), AMTL-SND-BLD-1.0 (phases 9-10) |

### DEC-002: Port 5010

| Field | Value |
|-------|-------|
| Date | 19 February 2026 |
| Context | S&D needs a port assignment for the Flask backend in desktop mode |
| Decision | Port 5010 for backend, 3010 for frontend dev server |
| Rationale | Next available in the 5000 range per AMTL-ECO-STD port registry |
| Decided by | Claude (Thalaiva) |
| Affects | AMTL-ECO-STD-1.0 (port registry), AMTL-SND-TDD-1.0, AMTL-SND-BLD-1.0, AMTL-SND-RUN-1.0 |

### DEC-003: User Brings Their Own LLM — Zero AI Cost to AMTL

| Field | Value |
|-------|-------|
| Date | 19 February 2026 |
| Context | S&D needs AI for advanced features (Socratic responses, The Other Side, Three Ways, Insight Extractor) but AMTL cannot incur API costs for a public open-source tool |
| Decision | Default mode has no AI (curated question bank only). User optionally connects their own LLM: Ollama (free, local), Anthropic API key, OpenAI API key, DeepSeek API key, or any OpenAI-compatible endpoint. All API calls go directly from user's device to provider — never through AMTL. |
| Rationale | Zero cost to AMTL. Privacy story stays airtight (we never see keys, prompts, or responses). S&D works beautifully without AI — the questions are that good. AI is an enhancement, not a requirement |
| Decided by | Mani Padisetti |
| Affects | AMTL-SND-SPC-1.0, AMTL-SND-TDD-1.0 (LLM connector), AMTL-SND-BLD-1.0 (Phase 6) |

### DEC-004: Fellow Traveller Tone — No Oracle Language

| Field | Value |
|-------|-------|
| Date | 19 February 2026 |
| Context | S&D's voice and positioning must be consistent across all user-facing text, AI system prompts, and documentation |
| Decision | S&D is a fellow traveller, never an oracle. Rejected language: oracle, guru, sage, master, teacher, coach, advisor, guide. Required language: fellow traveller, companion, thinking partner, "the other chair." AI never says "You should..." or "The answer is..." |
| Rationale | Philosophical commitment to non-hierarchical inquiry. Socrates didn't claim to know — he claimed to ask. S&D inherits this |
| Decided by | Mani Padisetti |
| Affects | All user-facing templates, AI system prompts, README, website copy, About page |

### DEC-005: Invisible Wisdom Frameworks

| Field | Value |
|-------|-------|
| Date | 19 February 2026 |
| Context | S&D uses nine wisdom traditions (Shadow, Stoic, Parts, Narrative, Logotherapy, Byron Katie, Clean Language, Immunity to Change, Appreciative Inquiry). Should users see which framework is being used? |
| Decision | Frameworks are always invisible. No icons, no labels, no mentions of tradition names in the UI. Users see questions — never framework names. "Three Ways to Look at This" presents three perspectives without naming the tradition behind each |
| Rationale | Naming creates resistance ("I'm not into Stoicism"), dates the tool ("that Stoic app"), and breaks the magic. Users should just notice the questions are unusually good |
| Decided by | Mani Padisetti / Claude (Thalaiva) — based on strategic review of LLM feedback |
| Affects | AMTL-SND-SPC-1.0 (frameworks section), AMTL-SND-TDD-1.0 (framework router), all templates |

### DEC-006: No Bio-Integration

| Field | Value |
|-------|-------|
| Date | 19 February 2026 |
| Context | Multiple reviewers suggested smartwatch/HRV integration during Forced Silence |
| Decision | Rejected. No bio-integration — no smartwatch, no HRV, no heart rate, no body sensors |
| Rationale | Adds hardware dependency, creates two-tier experience, adds complexity. The Forced Silence works without biometrics. Somatic awareness stays as a question ("Where in your body is this?"), not a sensor |
| Decided by | Mani Padisetti |
| Affects | AMTL-SND-SPC-1.0 (does NOT do), AMTL-SND-TDD-1.0 |

### DEC-007: No Gamification, No Streaks, No Ambient Atmosphere

| Field | Value |
|-------|-------|
| Date | 19 February 2026 |
| Context | Reviewers suggested backgrounds, ambient sounds, haptic breathing, gamification |
| Decision | Rejected. S&D is typography-first, not atmosphere-first. No ambient backgrounds, no particle effects, no streaks, no rewards, no leaderboards. Sound limited to a single chime when silence ends. UI is quiet, typographic, contemplative |
| Rationale | These make S&D feel like Calm or Headspace. S&D is NOT a meditation app. It's a thinking partner |
| Decided by | Mani Padisetti / Claude (Thalaiva) |
| Affects | AMTL-SND-TDD-1.0 (UI architecture), AMTL-SND-BLD-1.0 (all UI phases) |

### DEC-008: Feedback Signal — "Did That Land?"

| Field | Value |
|-------|-------|
| Date | 19 February 2026 |
| Context | Need a mechanism to validate whether framework routing helps users, without adding survey fatigue |
| Decision | After each session, display "Did that land?" with three options: Yes / Not sure / Not today. Stored locally per session. "Not today" acknowledges timing, not quality |
| Rationale | One bit of signal per session. Feeds framework routing improvement. Fellow traveller energy, not performance review energy. No reviewer suggested this but it's the critical missing piece |
| Decided by | Claude (Thalaiva) — adopted by Mani |
| Affects | AMTL-SND-TDD-1.0 (data model), AMTL-SND-BLD-1.0 (Phase 3) |

### DEC-009: Progressive Disclosure Menu Structure

| Field | Value |
|-------|-------|
| Date | 19 February 2026 |
| Context | S&D has many features (vault, letters, arcs, Vipassana, dialogues, settings) that could overwhelm a new user |
| Decision | Three-layer progressive disclosure: (1) Surface — Today's Question + Respond, (2) Secondary nav — My Reflections, Practices, Dialogues, (3) Tucked away — Settings, About, Export. Home screen shows ONLY the question and a text area. Everything else behind quiet nav |
| Rationale | The question IS the interface. Every reviewer agreed on this |
| Decided by | Mani Padisetti / Claude (Thalaiva) |
| Affects | AMTL-SND-TDD-1.0 (screen map), AMTL-SND-BLD-1.0 (UI phases), AMTL-SND-USR-1.0 |

### DEC-010: Red Flag Detection as Safety Baseline

| Field | Value |
|-------|-------|
| Date | 19 February 2026 |
| Context | S&D surfaces shadow, challenges beliefs, forces silence — powerful territory with real risk |
| Decision | On-device phrase matching for acute distress. When triggered: (1) pause Socratic challenge, (2) shift to grounding mode, (3) suggest professional support. Never continue normal questioning after trigger. Intensity dial gates access to heavier frameworks |
| Rationale | Non-negotiable for 2026. All five LLM reviewers flagged this independently as a launch blocker |
| Decided by | All reviewers + Mani Padisetti |
| Affects | AMTL-SND-TDD-1.0 (safety.py), AMTL-SND-BLD-1.0 (Phase 4) |

---

### DEC-011: "Donuts" Not "Doughnuts" — Deliberate Brand Spelling

| Field | Value |
|-------|-------|
| Date | 19 February 2026 |
| Context | Australian English uses "doughnuts." The product name uses the American spelling "Donuts." This needs to be a conscious decision, not an oversight |
| Decision | The product name is "Socrates & Donuts" — using the American spelling deliberately. It's punchier, more recognisable globally, and functions as a brand name rather than a dictionary word. All other text in the product uses Australian English |
| Rationale | "Donuts" is the brand. "Doughnuts" is the spelling. We're naming a product, not ordering breakfast. The short form reads better in logos, URLs (`socrates-and-donuts`), and conversation. This is the one and only American spelling permitted anywhere in the ecosystem |
| Decided by | Mani Padisetti |
| Affects | Product name, repository name, all branding, README, website copy |

### DEC-012: Australian Tone — No American Marketing Language

| Field | Value |
|-------|-------|
| Date | 19 February 2026 |
| Context | American marketing copy has a distinct tone: hyperbolic, salesy, "game-changer", "level up", "crushing it." S&D's voice must be understated, direct, and warm — not performative |
| Decision | All user-facing copy (website, app UI, notifications, About page, README) must use Australian English spelling AND Australian/neutral tone. No American marketing idioms. Cline/Guruve must be explicitly instructed to avoid American tone when generating any copy. A final tone review is required before any website or UI text goes live |
| Rationale | The product's philosophy is quiet intelligence, not loud salesmanship. The tone must match. American startup language ("disrupt", "10x", "unlock your potential") is antithetical to the fellow-traveller principle |
| Decided by | Mani Padisetti |
| Affects | All user-facing text in every document, template, website page, notification, and AI system prompt |

**Specific language rules:**

| Never Use (American) | Use Instead (Australian/Neutral) |
|---------------------|----------------------------------|
| Game-changer | Don't use — describe what it does instead |
| Level up | Don't use |
| Crushing it | Don't use |
| Awesome | Don't use |
| Check it out | Have a look |
| Gotten | Got |
| Reach out | Get in touch |
| Touch base | Don't use |
| Circle back | Don't use |
| Utilize | Use |
| Oftentimes | Often |
| Super excited | Don't use |
| Guys (addressing users) | Don't use |
| Unlock your potential | Don't use |
| Disrupt | Don't use |
| 10x your thinking | Don't use |
| Here's the thing | Don't use |
| At the end of the day | Don't use |

---

## Decision Template

```markdown
### DEC-XXX: [Title]

| Field | Value |
|-------|-------|
| Date | [DD Month YYYY] |
| Context | [What situation or question prompted this decision] |
| Decision | [What was decided] |
| Rationale | [Why this decision was made] |
| Decided by | [Who made the decision] |
| Affects | [Which document codes are affected] |
```

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 19 February 2026 | Claude (Thalaiva) | Initial register — 10 decisions from strategic review session |
| 1.1 | 19 February 2026 | Claude (Thalaiva) | Added DEC-011 (Donuts spelling) and DEC-012 (Australian tone rules) |

---

*Almost Magic Tech Lab*
*"Every decision has a home. If it's not here, it wasn't decided."*
