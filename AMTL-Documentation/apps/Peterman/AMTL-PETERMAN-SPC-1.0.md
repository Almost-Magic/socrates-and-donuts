# AMTL-PETERMAN-SPC-1.0
## Peterman — Autonomous SEO & LLM Presence Engine
### Product Specification Document | Version 1.0
**Almost Magic Tech Lab | February 2026**  
**Status: APPROVED FOR BUILD**  
**Author: Mani Padisetti (Curator) + Thalaiva (Strategic Claude)**

---

## 1. THE NAME

**Peterman.** Named after J. Peterman from Seinfeld — the man who didn't sell products, he sold stories that made you believe. Peterman doesn't optimise keywords. It engineers how the world — human and machine — finds you, believes you, and chooses you.

Internally: *"Elaine, get me the ranking report."*  
Externally: Say nothing. It just works.

---

## 2. THE PROBLEM PETERMAN SOLVES

### 2.1 The Old Problem (SEO)
Search engine optimisation is a 30-year-old discipline. Most tools do it adequately. The problem is not the tools — it's that most businesses treat SEO as a one-time task or a periodic audit. They get a report. The report sits on a shelf. Nothing changes.

### 2.2 The New Problem (LLM Ranking)
When someone asks ChatGPT "Who is the best AI governance consultant in Australia?" — Google rankings are irrelevant. The LLM draws from its trained understanding of who is authoritative. If you are not in that understanding, you do not exist.

**This is not SEO. This is something new.** Traditional SEO optimises for crawlers. LLM presence engineering optimises for *trained beliefs* — a fundamentally different challenge.

### 2.3 The Operational Problem (The Loop Nobody Closes)
Every existing tool — Semrush, Ahrefs, Moz, BrightEdge, even new LLM monitoring tools like Brandwatch — produces reports. Reports require humans to:
- Read them
- Decide what to do
- Brief a writer
- Review the content
- Deploy it
- Remember to check again later

This loop takes weeks. Most businesses never close it at all.

### 2.4 What Peterman Does Differently
Peterman is not a reporting tool. It is an **autonomous agent** that:
1. Continuously monitors SEO and LLM ranking
2. Identifies what needs to change
3. Generates the plan
4. Seeks approval at defined decision gates
5. Executes the approved changes (content, meta tags, schema, on-page fixes)
6. Deploys via website API or CMS integration
7. Monitors the impact
8. Reports back to ELAINE with what to do next

The human stays in the loop at decision points — not at execution points.

---

## 3. PRODUCT DEFINITION

### 3.1 Core Identity
**Peterman is an autonomous SEO and LLM presence agent.**

It takes a domain name and an objective ("rank first when people ask AI about X") and works continuously to achieve and maintain that objective — making changes, commissioning content, monitoring results, and adapting.

### 3.2 What Peterman Is NOT
- Not a reporting dashboard (reports are by-products, not the product)
- Not a keyword tool (keywords are inputs, not outputs)
- Not a content writer (it briefs content, ELAINE and CK Writer write it)
- Not a one-shot audit (it runs continuously)
- Not a human replacement (humans approve strategy and content direction)

### 3.3 The Core Loop

```
MONITOR → ANALYSE → PLAN → APPROVE → EXECUTE → VERIFY → REPORT → MONITOR
```

Every cycle, Peterman:
1. **Monitors** — crawls site, checks LLM rankings, watches competitors
2. **Analyses** — identifies gaps, opportunities, threats
3. **Plans** — generates prioritised action items with expected impact
4. **Approves** — surfaces decisions that need human sign-off (strategy, new pages, major changes)
5. **Executes** — deploys approved changes directly to website
6. **Verifies** — confirms changes are live and correctly indexed
7. **Reports** — tells ELAINE what content needs to be created, sends status to operator
8. **Loops** — starts again on next cycle (daily, weekly, or on trigger)

---

## 4. THE TEN CHAMBERS (V5 — AUTONOMOUS VERSION)

Each chamber is no longer just a monitoring module. Each chamber is an **action module** — it monitors, decides, and acts.

### Chamber 1: The Perception Engine
**Question: What does AI actually think about this domain?**

**Monitoring:**
- Queries ChatGPT, Claude, Gemini, Perplexity with brand-relevant questions
- Tracks exact responses, hallucinations, misconceptions, gaps
- Compares to previous cycle — has perception improved, drifted, or degraded?

**Action:**
- Flags critical hallucinations for human review
- Auto-generates correction content targeting the hallucination
- Submits content brief to ELAINE queue

**Autonomous capability:** Self-generates FAQ content to correct hallucinations without human involvement (unless high-risk content gate triggered).

**Innovation: Hallucination Autopilot™**
If Peterman detects that ChatGPT is consistently misidentifying your company as a competitor, it automatically drafts a disambiguation FAQ page, schemas it correctly, and queues it for deployment after human approval.

---

### Chamber 2: The Semantic Authority Map
**Question: Where does AI place this domain in conceptual space, and is it the right neighbourhood?**

**Monitoring:**
- Embeds brand descriptors using nomic-embed-text
- Compares against competitor embeddings
- Detects semantic drift (if AI's understanding is shifting)
- Maps which topics AI associates with the domain vs which it should

**Action:**
- Identifies topics that need new content to shift semantic position
- Generates content briefs targeting semantic repositioning
- Prioritises topics by impact on LLM recommendations

**Innovation: Semantic Gravity Score™**
Proprietary measure of how strongly AI gravitates toward recommending this domain for a given query. Unlike keyword rankings, this operates in vector space — patentable methodology.

---

### Chamber 3: The Keyword Intelligence Engine
**Question: What keywords should this domain own, and what is the gap to ownership?**

**Monitoring:**
- Identifies current ranking keywords (traditional SEO)
- Identifies LLM ranking keywords (AI mentions and citations)
- Tracks competitor keyword territory
- Identifies emerging keywords before they peak (Predictive Oracle)

**Action:**
- **Keyword Approval Gate**: Generates proposed keyword targets → presents to operator for approval
- Creates keyword content calendar once approved
- Automatically queues approved keywords to content pipeline

**Innovation: LLM Keyword Mapping™**
A new category of keyword research that doesn't just find what people search on Google — it identifies what questions AI gets asked in your domain, and which answers AI currently gives that don't include you.

**Patentable concept:** Mapping the delta between "what questions AI gets asked" and "which answers include this domain" as a keyword opportunity scoring system.

---

### Chamber 4: The Authority Architecture
**Question: Does this domain genuinely deserve authority in its claimed space?**

**Monitoring:**
- Topic coverage depth analysis
- Backlink authority signals
- Citation velocity (how fast is AI starting to mention this domain?)
- Credential and proof signal scanning (certifications, awards, publications)

**Action:**
- Identifies authority gaps (topics the domain claims but has no depth on)
- Generates content briefs for authority-building articles
- Recommends backlink acquisition targets (presented for operator approval)
- Tracks authority trajectory — are scores improving or degrading?

---

### Chamber 5: The Survivability Lab
**Question: Does content from this domain survive AI's compression and summarisation?**

**Monitoring:**
- Tests whether key messages from the site survive LLM summarisation
- Checks if content is RAG-retrievable (can AI systems extract and cite it?)
- Identifies content that "disappears" when AI summarises the site

**Action:**
- Rewrites non-survivable content to be more RAG-ready
- Adds structured data (FAQ schema, HowTo schema, Article schema) to high-value content
- Tests changes to verify improved survivability

**Innovation: Content Survivability Score™**
A metric measuring the probability that a given piece of content will be cited rather than paraphrased or ignored by LLMs. Higher scores = more citations.

---

### Chamber 6: The Technical Foundation
**Question: Can search engines and AI systems actually access and understand this site?**

**Monitoring:**
- Core Web Vitals
- Crawlability (robots.txt, sitemap.xml status)
- Schema markup presence and validity
- Mobile performance
- Page speed
- Broken links and 404s
- Canonical and hreflang issues

**Action (Autonomous with low approval threshold):**
- Auto-fixes: adds/updates schema markup, fixes sitemap, corrects canonical URLs
- Auto-generates: sitemap.xml, robots.txt if missing
- Queues for human approval: structural page changes, new page creation

**Deployment capability:** If given CMS credentials or website API access, Peterman deploys these fixes directly without the operator needing to touch code.

---

### Chamber 7: The Amplifier
**Question: Are the right amplification signals growing?**

**Monitoring:**
- Citation velocity across LLMs (is the domain getting mentioned more?)
- Social signal tracking (LinkedIn, Twitter mentions)
- Press and earned media monitoring
- External link growth
- Brand mention sentiment

**Action:**
- Identifies amplification opportunities (publications, directories, PR opportunities)
- Generates content optimised for citation (list articles, statistics, original research angles)
- Reports to ELAINE: "We need a thought leadership piece on X — here's the brief"

---

### Chamber 8: The Competitive Intelligence Unit
**Question: What are competitors doing that's working, and how do we counter it?**

**Monitoring:**
- Competitor LLM mention frequency
- Competitor new content (SearXNG alerts)
- Competitor schema and technical changes
- Competitor keyword wins (terms where competitors outrank this domain)

**Action:**
- Gaps identified → content briefs generated
- Competitor wins → counter-strategy drafted for operator approval
- Competitor weaknesses → exploitation plan generated

**Innovation: Competitive Shadow Mode™**
Peterman subscribes to competitor domains and receives alerts the moment they publish new content. Automated competitive response briefs within 24 hours.

---

### Chamber 9: The Oracle
**Question: What keywords and topics will this domain need to own in the NEXT 90 days?**

**Monitoring:**
- Google Trends signals (SearXNG + Trends)
- Emerging terminology in industry publications
- Regulatory and legislative signals (for compliance-adjacent domains)
- AI model update signals (when LLMs are retrained, content requirements shift)

**Action:**
- Generates forward-looking keyword targets
- Presents 90-day content calendar draft for operator approval
- Identifies "plant now, harvest later" keywords — emerging terms that should be owned before competition arrives

**Patentable concept:** Predictive LLM keyword authority scoring — using current trend signals to forecast which queries an LLM will receive in 90 days, then back-mapping to content requirements.

---

### Chamber 10: The Forge
**Question: What content needs to be created, and exactly what should it contain?**

**Monitoring:**
- Content gap register (running list of needed content from all other chambers)
- Content calendar status
- Published content performance

**Action (The Centrepiece):**
- Generates detailed content briefs (not just topics — full specs: target query, LLM intent, word count, headings, schema type, internal links, evidence required)
- Sends briefs to ELAINE's content queue
- ELAINE routes to CK Writer or other content tools
- Tracks completion and deployment
- Verifies published content against brief requirements

**Innovation: The Content Loop™**
The first autonomous pipeline that takes a gap (identified in LLM ranking) and closes it without human operational involvement — from gap detection to published, indexed, verified content. Humans approve the content before publication, but the brief, routing, and verification are autonomous.

---

## 5. THE ELAINE INTEGRATION

This is what makes Peterman uniquely powerful in the AMTL ecosystem.

### 5.1 The Content Briefing API
Peterman sends content requests to ELAINE via the ELAINE integration API:

```json
{
  "source": "peterman",
  "request_type": "content_brief",
  "priority": "high",
  "brief": {
    "title": "What is ISO 42001 and Why Australian SMBs Need It Now",
    "target_query": "ISO 42001 Australia small business",
    "llm_intent": "answer the question 'what is ISO 42001' for an Australian SMB audience",
    "word_count": 1200,
    "schema_type": "Article + FAQPage",
    "headings": ["What is ISO 42001?", "Why Australian businesses need it", "How to get started", "FAQ"],
    "evidence_required": ["Peterman Chamber 1: ChatGPT currently has no response for this query", "Chamber 3: 280 estimated monthly searches, 0 current ranking"],
    "internal_links": ["almostmagic.net.au/services", "almostmagic.net.au/contact"],
    "deadline": "2026-02-25"
  }
}
```

ELAINE receives this, acknowledges it, routes it to CK Writer with appropriate context. When content is complete, ELAINE notifies Peterman. Peterman receives the content, validates it against the brief, and queues it for operator approval before deployment.

### 5.2 The Status Feed
ELAINE can query Peterman's status at any time:
- "What's our current LLM ranking for 'AI governance Australia'?"
- "Are there any critical hallucinations about AMTL right now?"
- "What's this week's content queue?"

Peterman responds to ELAINE with structured data that ELAINE can summarise in natural language for Mani.

### 5.3 Alert Routing
Peterman sends alerts to ELAINE for:
- Critical hallucination detected (requires immediate content response)
- LLM ranking dropped for a priority keyword
- Competitor published content in a key territory
- Technical issue detected (site down, critical schema error)

ELAINE decides how to surface these — proactively to Mani, as a morning briefing, or as an immediate notification.

---

## 6. WEBSITE ACCESS & DEPLOYMENT

### 6.1 Access Modes
Peterman operates in three access modes:

**Read-Only Mode (Default)**
- Crawls and audits only
- Produces recommendations but cannot deploy
- Human implements all changes

**Advisory Mode**
- Generates deployment-ready code/markup
- Operator copies and pastes to deploy
- Peterman verifies deployment and confirms

**Autonomous Mode** (Requires explicit activation per-domain)
- Direct CMS API integration (WordPress, Webflow, Ghost, custom)
- Deploys approved changes directly
- Requires human approval for: new pages, content changes, redirects
- Auto-deploys without approval: schema markup updates, meta tag optimisation, sitemap regeneration, robots.txt updates
- Full audit trail of every autonomous change made

### 6.2 CMS Integrations (V5 Target)
- WordPress (via REST API)
- Webflow (via Webflow API)
- Ghost (via Content API)
- Static sites (via GitHub API — commits directly to repo)
- Custom HTTP endpoint (webhook-based)

### 6.3 The Approval Gate System
Every action is classified by risk level:

| Risk Level | Examples | Approval Required |
|-----------|---------|------------------|
| Low | Schema markup, meta description update, sitemap refresh | Auto-deploy |
| Medium | New blog post, meta title change, new internal links | One-click approve in Peterman dashboard |
| High | New page creation, significant content edit, URL changes | Explicit approval + preview |
| Critical | Structural changes, redirects, robots.txt changes | Approval + 24-hour delay |

---

## 7. INNOVATIVE FEATURES

### 7.1 LLM Rank Tracker
The first tool to track a domain's ranking within LLM responses — not Google position, but:
- Which queries mention this domain
- How early in the response (position 1-7 in a list = different value)
- Sentiment of the mention
- Whether the mention is recommended, cited, or incidental
- Trend over time (rising, stable, falling)

This creates an entirely new KPI category: **LLM Share of Voice (SoV)**.

### 7.2 Hallucination Registry
A persistent, versioned record of every hallucination detected about a domain:
- What the LLM said (verbatim)
- Which LLM
- Date detected
- Severity classification
- Status: Active, Addressed, Resolved
- What content was deployed to address it
- Whether the hallucination has been corrected in subsequent LLM responses

This is the first tool to treat LLM hallucinations as **bugs to be tracked and closed**.

### 7.3 Semantic Drift Alerts
When an LLM's understanding of a domain shifts (positive or negative), Peterman detects and alerts. This matters because:
- LLM updates can change how AI perceives established brands
- Competitors can "pollute" your semantic space by associating you with negative terms
- Regulatory changes can shift how AI categorises businesses in a sector

### 7.4 The Content Performance Loop
After Peterman commissions content via ELAINE → CK Writer and it is published:
1. Peterman crawls and indexes the new content
2. Waits 2-4 weeks for LLM update cycles
3. Re-queries target LLMs to check if the new content changed responses
4. Reports: "Article on ISO 42001 published Feb 19 → LLM mention rate for 'ISO 42001 Australia' increased from 0% to 23% by March 15"
5. Feeds this data back into The Oracle for future content recommendations

This is **evidence-based content strategy** — not "we think this will work" but "here is proof it worked."

### 7.5 Approval Queue Dashboard
A clean, mobile-friendly approval interface where the operator sees:
- Items waiting for approval (content briefs, deployment actions)
- One-click approve/reject/modify
- Context for each decision (why Peterman is recommending this)
- Time sensitivity indicator
- Expected impact score

Designed for a founder who reviews things on their phone between meetings — not a 10-tab dashboard.

### 7.6 Competitor Watchlist
Add competitor domains. Peterman:
- Monitors their LLM mention rates
- Alerts when they outrank you for a priority keyword
- Identifies their content that is generating AI citations
- Generates counter-brief automatically for ELAINE

### 7.7 Client Mode
For AMTL's consulting use: run Peterman against a client's domain before an engagement. Generates a professional-grade pre-sales intelligence report showing:
- Current SEO and LLM health scores
- Top 5 critical issues
- Estimated improvement if issues are addressed
- AMTL's recommended engagement scope

This is a sales tool disguised as a diagnostic.

---

## 8. SEXY UI/UX CONCEPTS

### 8.1 The War Room View
The primary dashboard is a **live intelligence centre** — not a report page. Inspired by trading floors and mission control, not accounting software.

Key elements:
- **Top strip:** LLM ranking for priority keywords (right now, vs yesterday, vs last week)
- **Central panel:** The Content Queue — what needs to be created, what's in progress, what just deployed
- **Right panel:** Live alerts feed (competitor moves, LLM changes, technical issues)
- **Bottom:** Approval queue — items waiting for the operator's decision

No charts for the sake of charts. Every data point visible has an action attached to it.

### 8.2 The Domain Card
When you add a domain, Peterman generates a **Domain Card** — a single-screen summary of everything important:
- The Peterman Score (1-100) — a proprietary composite
- LLM Share of Voice for top 5 keywords
- Health indicators for all 10 chambers (green/amber/red)
- Next recommended action
- Trend arrows (improving/degrading)

Think of it as a vital signs monitor for a website.

### 8.3 The Journey Timeline
A chronological view of everything Peterman has done to a domain:
- When it first scanned
- What it found
- What was approved and deployed
- What content was commissioned
- How scores changed over time

This is the **evidence file** — proof that Peterman is working, useful for client reporting.

### 8.4 One-Signal Mobile Alerts
Integration with ntfy.sh (your existing notification setup) for:
- Daily morning briefing (LLM rankings, overnight changes)
- Immediate alerts (critical hallucination, domain unreachable)
- Weekly digest (content published this week, score changes, upcoming approvals)

### 8.5 The Peterman Score
A single, proprietary composite score (0-100) that combines:
- Traditional SEO health (30%)
- LLM Share of Voice (25%)
- Content authority depth (20%)
- Technical foundation (15%)
- Citation velocity trend (10%)

This becomes AMTL's anchor metric for client reporting — one number that clients can track over time. Increasing the Peterman Score is the product outcome.

---

## 9. AI INTELLIGENCES USED

### 9.1 Local (Ollama — Always Running)
| Model | Role |
|-------|------|
| nomic-embed-text | Semantic embeddings for Chamber 2 (position analysis) |
| llama3.1:8b (fast) | Quick scoring, classification, content brief generation |
| gemma2:27b | Deep analysis when precision matters more than speed |

### 9.2 Claude CLI (Primary for Complex Reasoning)
- Content brief writing (Chamber 10)
- Hallucination analysis and severity scoring (Chamber 1)
- Competitive counter-strategy (Chamber 8)
- Oracle predictions (Chamber 9)

### 9.3 SearXNG (Local Search)
- Competitor monitoring
- Trend detection
- Citation tracking across the web

### 9.4 LLM Probing (Via HTTP APIs — Minimal Cost)
For actual LLM ranking checks, Peterman queries:
- Ollama (free, local) — primary for development and testing
- OpenAI API (minimal calls — weekly ranking checks only, not continuous)
- Anthropic API (same — weekly cadence)

**Cost control:** LLM probing is the expensive part. Peterman batches probing calls to weekly cadence by default. Daily probing is available for priority keywords at operator's discretion.

### 9.5 pgvector (Semantic Position Storage)
All brand and competitor embeddings stored in pgvector for:
- Historical semantic position tracking
- Drift detection (compare current embedding to 30-day-ago embedding)
- Competitor proximity analysis

---

## 10. PATENTABLE CONCEPTS

The following are novel enough to warrant IP protection conversations:

### Patent 1: LLM Share of Voice Measurement Methodology
**Concept:** A system and method for measuring a domain's share of voice within LLM-generated responses by:
1. Defining a query set representative of a domain's competitive space
2. Querying multiple LLMs with these queries at regular intervals
3. Parsing responses for domain mentions, ranking position within responses, and sentiment
4. Aggregating into a Share of Voice score comparable across time and competitors

No existing tool does this systematically with the scoring methodology described.

### Patent 2: Hallucination-to-Content Closure Pipeline
**Concept:** A system for detecting LLM hallucinations about a specific entity, automatically generating correctional content, and verifying whether subsequent LLM responses have incorporated the correction — creating a closed-loop hallucination remediation system.

### Patent 3: Semantic Gravity Scoring for Brand Positioning in LLM Vector Space
**Concept:** Using embedding comparison techniques to measure the "gravitational pull" of a brand toward desired semantic clusters in LLM conceptual space, and tracking this over time as a brand health metric.

### Patent 4: Predictive LLM Keyword Authority Forecasting
**Concept:** Using current web trend signals (search trends, news velocity, regulatory activity) to forecast what queries LLMs will receive in a future period, then back-mapping to content requirements for a domain to achieve authority before the trend peaks.

---

## 11. WHAT MAKES A HUGE IMPACT

### 11.1 The January 2027 Scenario
By January 2027, LLM-generated answers will be the primary discovery mechanism for B2B services in Australia. A business without LLM presence will be as invisible as a business without a website was in 2005. Peterman is the tool that gets businesses LLM-ready before this becomes a crisis rather than an opportunity.

**AMTL's position:** The only Australian consulting firm offering this service, powered by the only tool that closes the full loop from analysis to published content. Not a report. A result.

### 11.2 The Compound Effect
Traditional SEO improvements decay if not maintained. Peterman's continuous operation creates a compound effect:
- Month 1: Foundation fixed, schema deployed
- Month 3: Content authority building, LLM mentions beginning
- Month 6: Citation velocity measurable, LLM SoV improving
- Month 12: Domain is the default answer for target queries

No other tool maintains and compounds this improvement autonomously.

### 11.3 The Data Moat
Every domain Peterman monitors builds proprietary data about:
- How LLMs respond to industry-specific queries
- Which content types generate the most LLM citations
- How long after publication content appears in LLM responses
- What hallucination patterns are common in specific industries

After 50 domains and 12 months, AMTL has industry-specific LLM intelligence that no one else has. This is a data moat — and it powers better results for each new client.

---

## 12. TECHNOLOGY STACK

### 12.1 Backend
- **Framework:** Python / Flask (confirmed)
- **Port:** 5008 (confirmed)
- **Database:** PostgreSQL 17 + pgvector (port 5433)
- **Queue:** Redis (port 6379) — for content brief queue and async jobs
- **Scheduler:** APScheduler (no Celery overhead needed for single-user)
- **Crawler:** httpx + BeautifulSoup (confirmed working)
- **Search:** SearXNG (port 8888, confirmed running)
- **AI (local):** Ollama (port 11434, confirmed running)
- **AI (primary):** Claude CLI → Ollama fallback (refactor confirmed done)

### 12.2 Frontend
- **Architecture:** Single-page application
- **Stack:** HTML/CSS/JS (no framework — matches other AMTL apps)
- **Theme:** Dark — AMTL Midnight (#0A0E14), Gold (#C9944A)
- **Mobile:** Responsive, approval queue must work on phone
- **Dark/light toggle:** Required (AMTL standard)

### 12.3 Integrations
- **ELAINE:** HTTP API (port 5000) — content brief submission, status queries
- **CMS:** WordPress REST API, Webflow API (V5.1+)
- **Notifications:** ntfy.sh (push) + ELAINE (conversational)
- **Git:** Automatic GitHub push after each significant milestone

---

## 13. PHASED BUILD PLAN

### Phase 0 (NOW): Foundation Fix
Start from current state at `/home/amtl/claudeman-cases/DSph2/peterman`.

1. Fix Claude CLI `--no-input` bug in `ai_engine.py`
2. Start PostgreSQL, create peterman database, enable pgvector
3. Run `python -m pytest tests/ -v` — confirm 103+/112 passing
4. Verify `/api/health` returns real dependency status
5. Verify frontend loads at localhost:5008

**Deliverable:** App that starts cleanly with all dependencies.

### Phase 1 (Week 1): The Core Loop
Build the autonomous monitoring cycle:

1. Domain registration and brand profile creation
2. Chamber 6 (Technical Foundation) — autonomous schema/meta deployment
3. Chamber 1 (Perception Engine) — real LLM probing with Ollama
4. Keyword approval gate — propose → approve → track
5. Basic SPA frontend with the War Room view
6. ELAINE integration stub (content brief API)

**Deliverable:** Working domain → audit → keyword approval → basic LLM monitoring loop.

### Phase 2 (Week 2): Content Pipeline
1. Chamber 10 (Forge) — content brief generation
2. ELAINE API integration (live content briefs sent and tracked)
3. Chamber 3 (Keyword Intelligence) — LLM keyword mapping
4. Approval queue dashboard
5. The Peterman Score (composite)

**Deliverable:** Full content commissioning loop from gap to ELAINE queue.

### Phase 3 (Week 3): Intelligence Depth
1. Chamber 2 (Semantic Authority Map) — pgvector embeddings
2. Chamber 4 (Authority Architecture) — topic coverage analysis
3. Chamber 5 (Survivability Lab) — RAG readiness scoring
4. Chamber 8 (Competitive Intelligence) — competitor watchlist
5. Chamber 9 (Oracle) — 90-day content calendar

**Deliverable:** Full 10-chamber functionality, all monitoring active.

### Phase 4 (Week 4): Autonomous Deployment
1. CMS integration — WordPress REST API
2. Auto-deploy for low-risk changes (schema, meta tags, sitemap)
3. Approval gate hardening
4. Content performance loop (track what was deployed, verify LLM impact)
5. Journey timeline view

**Deliverable:** Peterman deploys approved changes directly to WordPress sites.

### Phase 5 (V5.1): Polish & Scale
- Webflow integration
- Mobile approval experience
- Client Mode (pre-sales intelligence reports)
- Multi-domain support
- The Data Moat — industry-specific benchmarks

---

## 14. FOUR GATES (MANDATORY — ALL PHASES)

Every phase must pass all four gates before the next phase begins:

| Gate | Requirement |
|------|------------|
| Gate 1: Beast Tests | All endpoints tested, 95%+ passing |
| Gate 2: Proof/Playwright | End-to-end user journey verified |
| Gate 3: GitHub | Committed and pushed to Almost-Magic/peterman |
| Gate 4: Documentation | README updated, User Manual current |

No bypasses. Every bypass is a bug.

---

## 15. SUCCESS METRICS

### Technical
- `/api/health` returns green for all dependencies
- All 10 chambers return real data (not stubs) within 30 seconds of domain submission
- Content brief successfully reaches ELAINE queue
- Deployed change verifiable within 5 minutes of autonomous action

### Business (AMTL)
- Peterman successfully runs weekly cycle on almostmagic.net.au
- LLM mention rate for "AI governance Australia" measurably improves within 90 days
- At least one content brief successfully commissioned via ELAINE → CK Writer → published
- Pre-sales client report generated in under 5 minutes from domain input

---

## 16. OPEN QUESTIONS FOR OPERATOR DECISION

These need Mani's answer before build proceeds:

| Question | Options | Implication |
|---------|---------|------------|
| Autonomous deployment: activate for almostmagic.net.au now? | Yes / No / Phase 4 only | Determines when CMS integration is built |
| Content approval level: when does ELAINE need your sign-off on content? | All content / Only pages / Nothing under 500 words | Approval gate configuration |
| Competitor domains to monitor initially? | List up to 5 | Chamber 8 initialisation |
| Priority keywords for LLM ranking? | List 5-10 target phrases | Chamber 3 initialisation |
| ELAINE content queue: should ELAINE surface briefs proactively or wait until you ask? | Proactive daily briefing / On-demand only | ELAINE integration mode |

---

*"Elaine, mark this down. We don't audit anymore. We act."*

**Almost Magic Tech Lab Pty Ltd**  
*"Technology that serves people."*

---

**Document Status:** Draft — Awaiting Operator Confirmation  
**Next Step:** Operator reviews Open Questions (Section 16), then Guruve builds Phase 0  
**Guruve build instruction:** Will be generated as separate document (BLD) once SPC is confirmed
