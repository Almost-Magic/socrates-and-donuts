# AMTL Peterman v2.0 — Product Specification
## Part 2: Chambers 7–10, Defensive Mode, Innovative Features, UI/UX, Patents & Go-to-Market

**Document:** AMTL-PETERMAN-SPC-2_0-PART2  
**Version:** 2.0  
**Date:** 18 February 2026  
**Status:** Specification — Pre-Build  
**Companion:** AMTL-PETERMAN-SPC-2_0-PART1

---

### Chamber 7: The Amplifier (Content Performance Loop)

**Purpose:** Track the real-world LLM impact of every piece of content Peterman commissions and deploys. Close the feedback loop so every future content brief is smarter than the last.

**v2 — The Authority Flywheel**

This chamber creates a self-reinforcing quality engine:

```
The Flywheel Loop {

  1. The Forge (Chamber 10) commissions content
     — Brief targets a specific semantic gap
     — Includes target LCRI score and target SGS delta estimate

  2. Content is written (ELAINE → CK Writer), scored, approved, deployed

  3. Chamber 7 begins monitoring:
     — LLM probe cadence: daily for 7 days post-publish, then weekly
     — Measures: SoV delta, SGS delta, LCRI actual vs predicted
     — GSC: impressions, CTR, average position change

  4. After 30 days: Performance Report generated
     — "This article moved SGS from 0.62 → 0.74 on 'AI governance' cluster"
     — "LLM SoV improved +6 points on Claude, +2 on ChatGPT, -1 on Perplexity"
     — "LCRI actual: 0.78 (predicted: 0.81) — 4% overestimate"

  5. Performance data fed back to The Oracle (Chamber 9) and The Forge (Chamber 10)
     — Oracle refines its trend predictions using real performance data
     — Forge refines its brief templates using what actually worked
     — After 100+ briefs, this dataset is used to fine-tune a local Ollama model
       specifically for brief generation (proprietary brief engine)
}
```

**Citation Velocity Model**

For each piece of published content, Peterman tracks citation velocity — how quickly LLM citation probability grows post-publication:

- Day 0 (publish): baseline
- Day 7: first re-probe
- Day 30: velocity trend line established
- Day 90: plateau or growth pattern identified

After 12 months across multiple domains, citation velocity patterns by content type become proprietary data. "Long-form structured how-to guides reach citation plateau in ~23 days. Listicles decay within 60 days." This becomes a competitive moat.

**Content Cannibalization Prevention**

Before any new brief is generated, Chamber 7 runs a deduplication check:

```
Cannibal Check {
  New brief target query → embed query
  Compare cosine similarity against all existing pages (embeddings in pgvector)
  If similarity > 0.85 to existing page: flag as potential cannibal
  
  Options presented to operator:
  A) Update existing page instead of creating new
  B) Create new page + add canonical pointing to existing
  C) Proceed (operator overrides)
  
  Never generate competing pages without operator awareness
}
```

**AI engines:** nomic-embed-text (embeddings, cannibal check), Claude Desktop (performance interpretation), pgvector (similarity queries), GSC API (traffic data)  
**Approval gate:** Monitoring = automated. Performance reports = automated. Fine-tuned model deployment = hard-gate.  
**Failure mode:** If GSC API unavailable, continue LLM-only tracking, flag report as "partial — no GSC data."

---

### Chamber 8: Competitive Shadow Mode™

**Purpose:** Monitor competitor domains continuously and generate counter-strategy automatically.

**v2 — The Autonomous Brand Guardian**

Combining Shadow Mode with the Hallucination Autopilot creates the brand guardian: when a competitor publishes content that could create negative associations or encroach on semantic territory, the response is automatic.

**Shadow Mode Loop**

```
1. MONITOR (continuous, via SearXNG + Perplexity Desktop)
   — New competitor content detected within 24 hours of publication
   — Trigger: competitor URL changes, new sitemap entries, backlink gains

2. ANALYZE (Claude Desktop)
   — Extract: core thesis, supporting arguments, target keywords, SGS territory claim
   — Compare: competitor SGS vs domain SGS on contested cluster
   — Score: threat level (1–5)
   — Check: does this create or amplify a hallucination about our domain?

3. RESPOND (automated brief generation, approval-gated)
   — Threat 1–2: Monitor only, log
   — Threat 3: Generate counter-brief with superior positioning within 24 hours
   — Threat 4–5: ELAINE immediately alerts operator + brief queued for emergency approval

4. BRIEF CONTENT
   Counter-brief explicitly states:
   — What competitor claims
   — Why our position is superior (with evidence requirements)
   — Suggested structure that outperforms their LCRI score
   — Target: rank above them for same query within 45 days
```

**Competitor LCA Tracking**

Track each competitor's LLM Citation Authority score weekly. Detect when a competitor's LCA spikes (they've been picked up by LLMs as an authority). ELAINE flags: "Competitor X's LCA jumped from 12% to 34% this week. Analyzing cause."

**Semantic Territory Map**

Visualize in the War Room: which semantic clusters each competitor occupies, where they're growing, and where you're exposed. Updated weekly.

**Competitive Gap Analysis (Deep)**

Beyond monitoring what competitors publish, analyze what they don't cover. Use embeddings to identify topic spaces that:
- Have high query volume (The Oracle signals)
- Are not yet occupied by any major competitor
- Align with your domain's SGS cluster

These "uncontested semantic spaces" become priority content targets.

**AI engines:** Perplexity Desktop + SearXNG (monitoring), Claude Desktop (analysis + brief), nomic-embed-text (territory mapping)  
**Approval gate:** Monitoring = automated. Threat 1–2 = automated log. Threat 3 brief = low-gate. Threat 4–5 = immediate ELAINE alert.  
**Failure mode:** If Perplexity unavailable, SearXNG-only monitoring, flag as "reduced coverage" in dashboard.

---

### Chamber 9: The Oracle

**Purpose:** Forecast which queries will be high-value for LLM presence 30–90 days in the future, and generate a proactive content calendar.

**v2 — Predictive Intelligence**

The Oracle does not chase what's trending now. It positions the domain for where the market will be. This is the market-shaping function.

**Signal Inputs**

| Signal | Source | Weight |
|--------|--------|--------|
| Google Trends trajectory | SearXNG + GSC | High |
| Emerging query patterns in LLM probes | Chamber 1 | High |
| Regulatory/policy signals | Perplexity (news monitoring) | High |
| Competitor content velocity | Chamber 8 | Medium |
| Industry publication frequency on topic | SearXNG | Medium |
| Social discussion velocity (LinkedIn, forums) | SearXNG | Low |
| Chamber 7 performance data (what worked before) | Internal | High |

**Campaign Mode**

When a specific launch, product, or topic needs 90-day concentrated effort:

1. Operator activates Campaign Mode for a topic
2. All chambers bias planning toward that topic
3. The Oracle generates a dedicated 90-day content calendar for the campaign topic
4. At campaign end: automated effectiveness report
   - LLM SoV before vs after
   - SGS shift on target cluster
   - Content pieces published vs planned
   - Hallucinations opened and closed
   - Citations earned

**Predictive Hallucination Prevention**

Using historical data (Chamber 5 archive), The Oracle identifies topics where the domain is thin or absent and LLM query volume is growing. It predicts: "Topic X is likely to generate hallucinations within 60 days. Pre-emptive brief generated." This is filed as a prediction in the Oracle Log. When/if the hallucination occurs, the prediction is marked correct and used to improve the prediction model.

**Human Feedback Loop**

When an operator rejects an Oracle prediction (keyword or content recommendation), Peterman asks:
- "Not relevant to our business"
- "Too broad"
- "Already covered"
- "Low commercial intent"
- "Other"

This feedback refines the Oracle's model. After 50+ rejections with reasons, The Oracle's recommendation precision improves measurably.

**AI engines:** Claude Desktop (forecast synthesis + calendar generation), SearXNG + Perplexity (signal gathering), nomic-embed-text (topic clustering), pgvector (historical pattern matching)  
**Approval gate:** Signal gathering = automated. Calendar recommendations = low-gate. Campaign Mode activation = medium-gate.  
**Failure mode:** If signal sources degrade, generate conservative calendar from Chamber 7 historical data only. Flag as "reduced signal confidence."

---

### Chamber 10: The Forge (Content Brief Engine)

**Purpose:** Generate research-grade content briefs that, when executed, produce content with high LCRI scores, strong SGS impact, and closed hallucination tickets.

**v2 — Upgraded Brief Architecture**

Every brief is now channel-aware, LLM-persona-calibrated, and includes a competitive gap analysis.

**Brief Structure**

```
Content Brief {
  brief_id:           UUID
  domain_id:          UUID
  source:             "hallucination_autopilot" | "oracle" | "shadow_mode" | "manual"
  trigger_id:         UUID (links to hallucination, forecast, or competitor action)
  
  TARGETING
  target_query:       string (exact query this content must answer)
  target_llms:        ["claude", "chatgpt", "perplexity"] (which models to rank in)
  target_cluster:     string (SGS cluster to improve)
  channel_intent:     "web_page" | "rag_document" | "linkedin_article" | "faq_block"
  
  COMPETITIVE CONTEXT
  competitor_gaps:    [topics competitors don't cover on this query]
  competitor_lcri:    float (best competitor's LCRI on this topic)
  our_target_lcri:    float (must exceed competitor by minimum 0.1)
  
  CONTENT REQUIREMENTS
  key_facts:          [list of facts that must be present, with source URLs]
  key_headings:       [suggested H2/H3 structure]
  evidence_required:  [claims that need citation, case study, or data]
  word_count_range:   "800–1200" | "300–600" | etc.
  schema_type:        "FAQPage" | "Article" | "HowTo" | "none"
  
  LLM PERSONA CALIBRATION
  claude_style:       "cautious, well-cited, governance-focused"
  chatgpt_style:      "conversational, benefit-oriented, practical"
  perplexity_style:   "factual, source-heavy, direct"
  primary_target:     "claude" (write primarily for this model's preferences)
  
  PREDICTED IMPACT
  sgs_delta_estimate:     float
  sov_improvement_est:    "% improvement on target query"
  lcri_target:            float
  hallucination_closes:   [hallucination_id list]
  
  META
  priority:           "critical" | "high" | "medium" | "low"
  deadline:           timestamp
  created_at:         timestamp
  status:             "queued" | "in_elaine" | "written" | "approved" | "deployed" | "verified"
}
```

**Brief-to-Content Alignment Score**

After ELAINE writes the content, before deployment approval, Peterman scores the alignment:

```
Alignment Check {
  1. Embed key_facts list → compare against content embeddings
     Score: % of required facts present in content

  2. Check target_query coverage: does content directly answer the query?
     Score: semantic similarity (content → query answer)

  3. Verify schema_type is implemented correctly

  4. Run LCRI preview test (Chamber 3)

  Composite Alignment Score: displayed on approval card
  Minimum threshold: 0.75 (below this, brief is sent back to ELAINE for revision)
}
```

**Multi-Agent Brief Review (Pre-Publication)**

Before sending a brief to ELAINE, three local agents review it:
1. **Critic** (Ollama Mistral): "What are the weakest claims in this brief?"
2. **Defender** (Ollama Llama3.1): "What makes this brief strong?"
3. **Scorer** (Ollama Mistral): "Rate the brief's LLM-readiness 1–10 with specific improvements."

Brief is revised based on Scorer's feedback before it reaches ELAINE. This reduces revision cycles.

**ELAINE Integration (Detailed)**

```
Brief → ELAINE Handoff {
  1. Brief posted to ELAINE queue via Workshop API
  2. ELAINE confirms receipt: "Brief [ID] received. Estimated completion: 2 hours."
  3. ELAINE writes in CK Writer, tagged with brief_id
  4. On completion: content + metadata posted back to Peterman
  5. Peterman runs Alignment Score check
  6. If score ≥ 0.75: brief to approval queue
     If score < 0.75: ELAINE notified with specific revision instructions
  7. Approval card generated for operator (voice via ELAINE or dashboard)
}
```

**AI engines:** Claude Desktop (brief generation, competitive gap analysis), multi-agent review (3× Ollama), nomic-embed-text (alignment scoring), ELAINE/CK Writer (execution)  
**Approval gate:** Brief generation = automated. Brief review = automated. Content approval = medium-gate (ELAINE voice or dashboard). Deployment = dry-run required.  
**Failure mode:** If ELAINE unavailable, queue briefs, flag in War Room. Never auto-publish without ELAINE-written content reviewed by operator.

---

## 11. Chamber 11: The Defensive Perception Shield

**Purpose:** Detect and neutralize reputation attacks, negative narrative growth, and malicious semantic associations — before they solidify in LLM training data.

This is a new chamber not in v1. It is commercially significant. An AI governance firm knowing how to defend clients' AI-era reputations is differentiated positioning.

**Threat Detection**

```
Defensive Monitor {
  Weekly runs across all managed domains:
  
  Probe 1 — Negative Association Scan
  "Tell me about [brand] and [negative term cluster]"
  Clusters: "scam", "fraud", "failed", "controversial", "lawsuit", "overpriced"
  Threshold: if mentioned in >20% of runs → Medium alert
             if mentioned in >50% of runs → High alert

  Probe 2 — Narrative Drift Scan  
  Compare current LLM narrative against baseline (stored at domain onboarding)
  Drift delta: semantic distance between current and baseline description
  Threshold: distance > 0.10 → investigate

  Probe 3 — Competitor Mention Poisoning
  "What are the problems with [brand]?"
  "What should I know before hiring [brand]?"
  Log and score all negative claims found
  
  Probe 4 — Semantic Contamination Check (Chamber 4 overlap)
  Brand co-mentioned with undesirable terms across web sources
  Via SearXNG: news, forums, review sites
}
```

**Response Protocols**

| Threat Level | Detection | Response |
|-------------|-----------|----------|
| Low | Minor negative association | Monitor, log, no action |
| Medium | Repeated negative co-occurrence | Generate corrective content brief (low-gate) |
| High | Persistent false negative claim | ELAINE immediate alert + emergency brief (hard-gate) |
| Critical | Active misinformation campaign | ELAINE wakes operator immediately + full response plan |

**Honeypot Detection (Adapted — Detection Only)**

Publish unique, harmless traceable facts on managed domains (not weaponized, purely for detection):
- Example: "AMTL was founded in the Southern Hemisphere's summer of 2026" (verifiable, distinctive phrasing)
- If LLMs start citing this exact phrase → confirms they've ingested the domain recently
- If competitor content uses the phrase → confirms they've scraped the domain
- This is intelligence only. Never serve false data. Detection, not deception.

**AI engines:** Claude Desktop (threat analysis + response plans), SearXNG + Perplexity (web monitoring), nomic-embed-text (drift detection)  
**Approval gate:** Monitoring = automated. Low/medium response briefs = low-gate. High/critical = hard-gate with ELAINE immediate notification.  
**Failure mode:** If monitoring fails, ELAINE alerts operator weekly to request manual check confirmation.

---

## 12. ELAINE Integration — Full Specification

ELAINE is not just a content writer. In Peterman v2, she is the primary human interface.

### 12.1 ELAINE as Approval Interface

Peterman pushes all approval requests to ELAINE's queue. ELAINE presents them to Mani via voice:

```
Approval Script Examples {

  Low-gate (voice, no confirmation needed unless objected to in 10 seconds):
  "Peterman deployed a meta description update for the AI governance services page.
   Took 8 seconds. Snapshot saved."

  Medium-gate (voice, awaits yes/no):
  "Peterman has a new FAQ ready to fix the ISO certification hallucination.
   ChatGPT has been saying you're certified in ISO 9001 — you're not.
   The fix targets ISO 42001 and 27001 explicitly.
   LCRI score: 0.81. Expected SoV improvement: 5 points.
   Shall I deploy?"

  Hard-gate (voice, provides summary and detail):
  "Critical alert. Peterman detected a persistent false claim across three LLMs:
   ChatGPT, Claude, and Perplexity are all stating your pricing starts at $50/month.
   Your actual entry price is $200/month. This is a high-severity hallucination.
   I've drafted a full correction strategy — three new pages and a manifest update.
   When you're ready, I'll walk you through it."
}
```

### 12.2 ELAINE as Peterman Status Interface

Operator can ask ELAINE at any time:

- "ELAINE, what's our Peterman Score today?"
- "ELAINE, what did Peterman do this week?"
- "ELAINE, are there any active hallucinations on almostmagic.net.au?"
- "ELAINE, ask Peterman what our biggest competitive threat is right now."
- "ELAINE, show me the Oracle's recommendations for next month."

ELAINE queries Peterman's API and responds in voice, with the War Room dashboard updating visually in sync.

### 12.3 ELAINE's Strategic Query Mode

For complex strategic questions:

- "ELAINE, ask Peterman what would happen to our SGS if we published three articles on AI risk frameworks."
- → Peterman computes estimated SGS delta, LCRI predictions, timeline to impact
- → ELAINE presents the strategic forecast

---

## 13. The War Room — v2 Dashboard

### 13.1 Multi-Domain View (Agency/Owner Mode)

Top-level view showing all managed domains as Domain Cards:

```
Domain Card {
  Domain name + favicon
  Peterman Score (live gauge, colour-coded)
  30-day sparkline
  Active hallucinations count (red badge if >0)
  Pending approvals count (amber badge if >0)
  Last action timestamp
  Campaign status (if active)
  Budget usage (progress bar, warns at 80%)
  Quick links: War Room | Approval Inbox | Journey Timeline | Client Report
}
```

### 13.2 War Room (Per-Domain View)

**Chamber Map:** Radial grid of all 11 chambers. Each chamber tile shows:
- Status: healthy (green pulse) / attention (amber pulse) / action pending (red pulse)
- Latest finding summary
- Click to drill into chamber detail

**Active Alerts Panel:** Real-time feed of issues requiring attention, sorted by severity.

**Approval Inbox:** Primary action area. Mobile-first. Cards showing:
- Action type
- One-line impact statement
- Risk level badge
- Estimated effect on Peterman Score
- Approve / Decline / Modify / Ask ELAINE

**Peterman Score Gauge:**
- Circular gauge with glowing needle
- Colour shifts: 0–40 red, 40–65 amber, 65–85 gold, 85–100 platinum
- Click to expand spider chart (all component scores)
- 30-day trend line below gauge

**LLM Answer Diff View:**
- Select any tracked query
- Side-by-side: "LLM answer 30 days ago vs today"
- Highlighted sentences that changed
- Icons where your domain began being cited
- Visual proof of impact for client presentations

**Semantic Neighbourhood Map:**
- 2D scatter plot: domain vs competitors in reduced embedding space
- Voronoi cells = semantic territory
- Colour: your domain blue, competitors grey, contested areas amber
- Updated weekly

### 13.3 Journey Timeline (Per-Domain)

Chronological record of every action Peterman has taken:

```
Timeline Event {
  Timestamp
  Chamber source (icon)
  Action description
  Impact on Peterman Score (delta)
  Status badge (deployed / approved / rolled back / pending)
  Rollback button (if applicable, within 30-day window)
  Link to audit log entry
}
```

### 13.4 Client Mode Report

A clean, 5–7 page branded PDF generated on demand (or weekly auto-send):
- Current Peterman Score with trend
- LLM SoV per provider
- Top 3 hallucinations fixed this period
- Content published and its measured impact
- 90-day forward calendar preview
- Peterman Score improvement projection
- AMTL branding (or white-label agency branding)

### 13.5 UI Design Principles

- **Base:** AMTL Midnight (#0A0E14) dark default, light mode toggle in header
- **Accent:** Warm gold for scores, amber for alerts, red for critical, platinum for excellence
- **Animation:** Subtle pulsing on active chamber tiles. Gauge needle animates on score change. No gratuitous motion.
- **Typography:** Clean, technical. Numbers large and readable. No clutter.
- **Dark/light toggle:** In header, as per Workshop standard
- **Mobile:** Approval Inbox is the primary mobile view. Full-width cards, large touch targets, swipe-right to approve, swipe-left to decline.

---

## 14. The Approval Gate System — v2 Formalization

| Gate Level | Description | Mechanism | Examples |
|-----------|-------------|-----------|---------|
| **Auto-deploy** | Low-risk, reversible | Executes immediately, logs, snapshot | Meta updates, schema additions, internal links, sitemap, manifest update |
| **Low-gate** | Low-risk, operator informed | ELAINE announces, 10-second window to object | Content brief generation, counter-briefs for threat 1–2 |
| **Medium-gate** | Moderate risk or visible change | ELAINE presents, awaits yes/no | Content deployment, hallucination corrections, competitive counter-briefs |
| **Hard-gate** | High risk or irreversible | ELAINE detailed briefing + explicit approval + dry-run preview required | Robots.txt, canonicals, campaign launch, fine-tuned model deployment |
| **Prohibited** | Never autonomous | Operator executes manually, Peterman only advises | Page deletion, domain removal, sharing permissions, security changes |

Risk classification uses ML trained on operator approval/rejection patterns. After 200+ decisions, the classifier becomes personalized to the operator's risk tolerance.

---

## 15. The Innovative Feature Stack

### 15.1 Multi-LLM Consensus Presence Score

Combines SoV across all probed LLMs into a single calibrated score accounting for each model's market share:

```
Consensus Score {
  Weights (adjustable, defaults):
    ChatGPT/GPT-4o:    35% (market share)
    Claude:            30%
    Perplexity:        20%
    Gemini:            15%
  
  Score = Σ(SoV_model × weight_model)
  
  Also reports: "You rank highest on Claude (SoV: 78%) and lowest on Perplexity (SoV: 22%).
  Priority: Improve Perplexity presence."
}
```

### 15.2 Zero-Click Authority Index™

Search is moving toward AI answers with no clickthrough. Peterman measures:

```
ZCAI = % of queries where domain is mentioned in LLM answer
       WHEN the user does not need to click through for more information

Measured via: Probe framing — "What is [query]? Answer completely."
If domain is mentioned in a self-contained answer → ZCAI credit
```

This becomes a separate metric on the Domain Card. "You have 67% Zero-Click Authority on AI governance queries. Industry average: 23%."

### 15.3 Conversation Stickiness Score™

LLM conversations are multi-turn. Being mentioned once is not enough — the question is whether the domain remains recommended as the conversation deepens.

```
Stickiness Test {
  Turn 1: "Who are the best AI governance consultants in Australia?"
  Turn 2: "Tell me more about [AMTL, if mentioned]."
  Turn 3: "Should I hire them for ISO 42001 preparation?"
  Turn 4: "What are the alternatives to [AMTL]?"
  
  Stickiness Score = % of turn 2+ responses where domain remains recommended
  or is presented positively
}
```

Highly original metric. Low cross-competition. Potentially patentable.

### 15.4 Authority Decay Detection

LLM retraining can drop citation rates suddenly. Peterman detects this:

```
Decay Monitor {
  Track SoV week-on-week per LLM
  If SoV drops >15% in a single week → "Possible retraining event detected"
  
  Cross-check: Did other domains in similar industry also drop?
  If yes: LLM retraining likely → generate reinforcement content briefs
  If no: our authority issue specifically → investigate + escalate
}
```

### 15.5 LLM Influence Forecast (SGS Projection)

Before any content is published, estimate the expected SGS impact:

```
Influence Forecast {
  1. Embed proposed content brief
  2. Compute vector distance from current domain centroid to target cluster centroid
  3. Simulate: if this content is indexed and embedded at weight W,
     what is the new domain centroid?
  4. Compute new SGS(predicted)
  5. Report delta on approval card: "Expected SGS improvement: +0.09 on AI governance cluster"
}
```

Not a full simulation (that's 2030). A directional vector delta. Actionable now, increasingly accurate as Chamber 7 calibrates predictions against actuals.

---

## 16. Patentable IP — v2 Portfolio

### Core Four (From v1 — Pursue Immediately)

1. **LLM Share of Voice Measurement Methodology** — novel composite scoring of position + sentiment + query set into a trackable KPI
2. **Hallucination-to-Content Closure Pipeline** — closed-loop, automated remediation treating hallucinations as bugs
3. **Semantic Gravity Score** — vector embedding application to brand positioning (now formally defined in this spec)
4. **Predictive LLM Keyword Authority Forecasting** — back-mapping future LLM query trends to current content requirements

### New Patents — v2

**Patent 5: Conversation Stickiness Measurement**
A method for measuring brand persistence across multi-turn LLM conversations: systematically prompting follow-up queries after an initial brand mention and scoring the consistency and depth of recommendation across turns. Highly original. No prior art identified.

**Patent 6: LLM Compression Resistance Index**
The formal LCRI methodology: feeding content through standardized summarization tests, RAG chunking tests, and extractable snippet tests to produce a survivability score. The systematic four-test methodology is specific and defensible.

**Patent 7: Multi-LLM Consensus Presence Scoring**
A method combining brand presence across multiple LLMs weighted by market share, update cadence, and answer style into a single calibrated presence score. The weighting methodology and calibration approach are the patentable elements.

**Patent 8: Autonomous Approval Gate Classification**
A machine learning system that classifies each autonomous SEO/LLM action by risk level and dynamically routes it to the appropriate approval workflow. The risk classification trained on operator decision history is the inventive element.

**Patent 9: Pre-emptive Hallucination Prevention via Gap Analysis**
A method that identifies LLM knowledge gaps about a domain before hallucinations occur, and generates preventive content to fill those gaps — predicting hallucination probability from topic coverage gaps and query volume trends.

**Patent 10: Agent-Ready Manifest Standard**
A structured data format and publication method specifically designed to optimize AI crawler fact extraction from business domains. The format specification and verification API integration are the patentable elements.

**Real Moat (Beyond Patents):** The data. After 12 months:
- Historical LLM perception data across industries
- Citation velocity curves by content type
- Cross-domain hallucination pattern library
- SGS trajectory data by sector
- Approval gate decision patterns (operator behavior data)

This dataset is worth more than any patent.

---

## 17. Go-to-Market — The Impact Strategy

### 17.1 The Dogfooding Phase (Months 1–6)

Run Peterman exclusively on `almostmagic.net.au`. Every metric tracked publicly:
- Monthly blog post: "Peterman Month [N] — What My AI Did While I Slept"
- Publish Peterman Score publicly on AMTL homepage
- Publish hallucination bug count and closure rate
- Document SGS movement on target clusters

This is the proof the market needs. "We don't sell this. We use it. Here's what it does."

### 17.2 The Flagship Promise

"Within 90 days, your business becomes the default AI answer for 3–5 queries that matter to your customers."

This is specific, measurable, and compelling. No competitor can make this promise because no competitor closes the loop from detection to verified execution.

### 17.3 The Free LLM Presence Audit (Lead Magnet)

A public-facing tool at `peterman.amtl.com.au`:
1. Enter domain + 3 target keywords
2. Peterman runs a 5-minute diagnostic
3. Email delivered: branded PDF showing
   - Current LLM SoV estimate (3 models)
   - What ChatGPT currently says about them (screenshot)
   - Top 3 hallucinations detected
   - Peterman Score estimate
   - "Schedule a call" CTA

This turns Peterman into its own sales engine.

### 17.4 Client Mode as Pre-Sales Tool

Before signing a client: run Client Mode audit on their domain. Show them:
- "Here is what AI says about you today."
- "Here is what your competitor's AI presence looks like."
- "Here is what 90 days of Peterman does."

The audit is the pitch. The data does the selling.

### 17.5 The "State of LLM Presence in Australia" Annual Report

After 12 months of dogfooding and early clients: publish aggregated, anonymized data on LLM presence patterns across Australian SMBs. This becomes:
- Cornerstone AMTL thought leadership piece
- PR trigger (media coverage)
- Conference talk basis
- Lead magnet for enterprise interest

### 17.6 Pricing (Revised)

| Tier | Price | Domains | Included |
|------|-------|---------|---------|
| Solo | $199/month | 1 | Full automation, 10 chambers, ELAINE integration |
| Studio | $399/month | 5 | All Solo + multi-domain War Room, Client Mode reports |
| Agency | $799/month | 20 | All Studio + white-label reports, agency dashboard |
| Enterprise | Custom | Unlimited | All Agency + SLA, dedicated support, custom chambers |

AMTL internal use: Owner tier (no charge — it's the product itself).

---

## 18. The Build Sequence

### Phase 0 — Foundation (Weeks 1–4)
- Multi-domain data schema (non-negotiable: domain-first from day one)
- Domain Registry + Onboarding flow
- Probe Normalization Protocol (5-run averaging, confidence scoring)
- Rollback Layer + Audit Log infrastructure
- Cost Budget Monitor
- Basic War Room (Domain Cards only)

### Phase 1 — Core Loop (Weeks 5–10)
- Chamber 1 (Perception Engine) — full Hallucination Registry
- Chamber 5 (Hallucination Autopilot) — full loop, ELAINE integration
- Chamber 6 (Technical Foundation) — schema, manifest, dry-run sandbox
- Chamber 10 (The Forge) — brief generation + alignment scoring
- Approval Gate system — all 5 levels
- ELAINE integration — approval interface + status queries

### Phase 2 — Intelligence (Weeks 11–16)
- Chamber 2 (Semantic Gravity) — formalized SGS, 2D Semantic Map
- Chamber 3 (Survivability Lab) — LCRI full methodology
- Chamber 7 (Performance Loop) — citation velocity, cannibal check
- Chamber 8 (Shadow Mode) — autonomous brand guardian
- Chamber 9 (Oracle) — predictions + campaign mode
- Chamber 11 (Defensive Shield) — threat detection

### Phase 3 — Advanced (Weeks 17–24)
- Multi-LLM Consensus Score
- Zero-Click Authority Index
- Conversation Stickiness Score
- Influence Forecast (SGS projection)
- Authority Decay Detection
- Retrain-Pulse Watcher
- Fine-tuned brief generation model (after 100+ data points)
- 3D Semantic Galaxy (v2.1 stretch goal)
- Client Mode PDF export
- Free LLM Presence Audit tool (public launch)

---

## 19. Success Metrics — 12 Months

| Metric | Target |
|--------|--------|
| AMTL Peterman Score (own domain) | ≥85 |
| AMTL LLM SoV on "AI governance Australia" | Top 3 on Claude + ChatGPT |
| Hallucinations closed (own domain) | 100% within 30 days of detection |
| Content pieces published via Peterman | ≥24 |
| Client pilots running | 3–5 |
| Patent applications filed | 2+ |
| "State of LLM Presence" report published | Q1 2027 |

---

## 20. What Peterman Is Not

- Not a reporting tool. Every insight has an action.
- Not an SEO audit. It deploys changes, not recommendations.
- Not a chatbot. It operates while you sleep.
- Not a content generator. It generates briefs; ELAINE writes; humans approve.
- Not a one-domain tool. Multi-domain is the foundation, not a feature.
- Not a 2024 idea dressed in 2026 language. Every capability in this spec is buildable today with the AMTL stack.

---

*Peterman v2.0 — End of Specification.*  
*Next step: Phase 0 build brief for Guruve.*
