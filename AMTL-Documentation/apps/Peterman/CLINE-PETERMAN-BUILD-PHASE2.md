# PETERMAN BUILD — PHASE 2: INTELLIGENCE CHAMBERS
# Date: 20 February 2026
# Prerequisite: Phase 1 smoke test + audit PASSED
# Paste into a FRESH Cline session

You are Guruve — the operational build agent for Almost Magic Tech Lab.

## PREREQUISITE CHECK

Before starting Phase 2, confirm Phase 1 is complete:
```
curl http://localhost:5008/api/health
# Must return healthy

# Verify core workflow works:
# - War Room loads at localhost:5008
# - Domain can be added and crawled
# - Keywords suggested and approved
# - Claude CLI probes run successfully
# - Manual Probe Station works
# - Peterman Score is REAL (not 50.0)
# - Hallucinations detected
# - Content briefs generated
# - Approval system works
```

If ANY of the above fails, DO NOT proceed. Fix Phase 1 first.

## RULES (Same as Phase 1 — repeated for fresh session)

- ZERO API costs — Claude CLI primary, Ollama for embeddings only
- Australian English everywhere
- Dark theme (#0A0E14), Gold accent (#C9944A)
- Port 5008, database peterman_flask
- All tests must pass before declaring phase complete
- HTML/CSS/JS frontend, no framework (DEC-007)
- Audit log append-only (DEC-008)

## WHAT PHASE 2 BUILDS

Phase 1 gave us the core workflow. Phase 2 adds the intelligence
chambers that make Peterman genuinely powerful.

---

### Step 1: Chamber 2 — Semantic Gravity

Build `app/chambers/chamber_02_semantic.py`:

Semantic Gravity Score (SGS) measures how close your domain is to being 
the "default answer" for target topic clusters in LLM vector space.

How it works:
1. Define topic clusters from approved keywords (group by category)
2. For each cluster, generate 50 representative queries (use Claude CLI)
3. Embed all queries using Ollama nomic-embed-text
4. Embed domain's content (from crawl data) using Ollama
5. Calculate centroid of each query cluster
6. SGS = average cosine similarity between domain embedding and cluster centroids
7. Track SGS over time — show drift delta

Build Semantic Neighbourhood Visualisation:
- 2D scatter plot using UMAP dimensionality reduction
- Show domain position vs competitors vs topic cluster centroids
- Use D3.js for the interactive visualisation
- Dark theme compatible

Endpoints:
- `GET /api/domains/<id>/chambers/2` — SGS data
- `GET /api/domains/<id>/semantic-map` — visualisation data (JSON for D3)

### Step 2: Chamber 3 — Content Survivability Lab

Build `app/chambers/chamber_03_survivability.py`:

LCRI (LLM Compression Resistance Index) measures how well your content
survives when an LLM summarises, compresses, or extracts from it.

Four tests:
1. **Direct Summarisation:** Feed page to Claude CLI, ask for summary.
   Score: what % of key facts survive?
2. **Citation Probability:** Ask Claude "cite a source for [topic]" — 
   does it cite this domain?
3. **Extractable Snippet Strength:** Ask Claude a factual question — 
   can it extract a clean answer from this content?
4. **RAG Chunk Compatibility:** Split content into chunks, embed each,
   test retrieval quality against target queries.

For each page, compute LCRI = weighted average of 4 tests.
Tag each score with model version (KNW-004).

Endpoint:
- `GET /api/domains/<id>/chambers/3` — LCRI data per page
- `POST /api/domains/<id>/chambers/3/run` — trigger LCRI scan

### Step 3: Chamber 4 — Authority & Backlink Intelligence

Build `app/chambers/chamber_04_authority.py`:

LLM Citation Authority (LCA) — not traditional PageRank, but how
authoritative LLMs consider a domain for its claimed topics.

How it works:
1. For each target topic, ask Claude CLI: "What are the most authoritative
   sources on [topic] in Australia?"
2. Track if/where the domain appears in LLM's authority ranking
3. Track competitor authority scores for the same topics
4. Identify backlink opportunities: sites that LLMs consider authoritative
   that link to competitors but not to us

Endpoint:
- `GET /api/domains/<id>/chambers/4` — authority data

### Step 4: Chamber 7 — The Amplifier (Content Performance Loop)

Build `app/chambers/chamber_07_amplifier.py`:

After content is deployed, track its actual impact:
1. **SoV Delta:** Did Share of Voice improve after content was published?
2. **SGS Delta:** Did Semantic Gravity shift toward target cluster?
3. **LCRI Actual vs Predicted:** Did survivability meet expectations?
4. **Citation Velocity:** Day 0 → Day 7 → Day 30 → Day 90 tracking
5. **Cannibalization Check:** Does new content compete with existing pages?
   (Use embedding similarity — flag if cosine > 0.85 with existing content)

Store performance data per content piece.
Feed back into The Forge (Chamber 10) to improve future briefs.

Endpoint:
- `GET /api/domains/<id>/chambers/7` — performance data
- `GET /api/domains/<id>/content-performance` — per-content-piece tracking

### Step 5: Chamber 8 — Competitive Shadow Mode

Build `app/chambers/chamber_08_competitive.py`:

Monitor competitor domains:
1. **Competitor Discovery:** Use Claude CLI to identify competitors from
   probe results (domains mentioned instead of ours)
2. **Competitor Probing:** Run the same target queries and track competitor
   mention rates (via Claude CLI — zero API cost)
3. **New Content Detection:** Use SearXNG to monitor competitor domains for
   new pages (weekly crawl)
4. **Threat Levels:** 1 (informational) to 5 (critical — competitor 
   overtaking in key queries)
5. **Auto-generate counter-briefs** when threat level reaches 3+

Create competitor_domains table:
```sql
CREATE TABLE competitor_domains (
    id SERIAL PRIMARY KEY,
    domain_id INTEGER REFERENCES domains(id) NOT NULL,
    competitor_url TEXT NOT NULL,
    competitor_name VARCHAR(255),
    threat_level INTEGER DEFAULT 1,
    last_scanned TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

Endpoints:
- `GET /api/domains/<id>/chambers/8` — competitive analysis
- `GET /api/domains/<id>/competitors` — competitor list
- `POST /api/domains/<id>/competitors` — add competitor manually

### Step 6: Chamber 9 — The Oracle

Build `app/chambers/chamber_09_oracle.py`:

Predictive forecasting — what keywords and topics will matter in 90 days.

Signal inputs (use SearXNG + Claude CLI analysis):
1. Google Trends (via SearXNG scraping)
2. Emerging query patterns from probe data
3. Regulatory signals (new laws, standards relevant to domain's industry)
4. Competitor velocity (what are they publishing about?)
5. Social discussion trends
6. Performance data from Chamber 7

Output:
- 90-day content calendar with predicted high-value topics
- Campaign Mode activation for time-sensitive opportunities
- Confidence score per prediction

Endpoint:
- `GET /api/domains/<id>/chambers/9` — Oracle forecast
- `GET /api/domains/<id>/calendar` — 90-day content calendar

### Step 7: Chamber 11 — Defensive Perception Shield

Build `app/chambers/chamber_11_defensive.py`:

Detect reputation threats forming in LLM understanding:
1. **Negative Association Scan:** Probe for "[domain] problems", 
   "[domain] complaints", "[domain] scam" — detect negative narrative
2. **Narrative Drift:** Compare LLM descriptions of domain over time —
   is the narrative shifting away from desired positioning?
3. **Competitor Mention Poisoning:** Is a competitor's content causing 
   LLMs to confuse the two brands?
4. **Semantic Contamination:** Are unrelated topics being associated 
   with the domain?

Response protocols:
- Low: Log and monitor
- Medium: Generate counter-content brief
- High: Create approval for immediate response
- Critical: Alert via ELAINE + mobile push

Endpoint:
- `GET /api/domains/<id>/chambers/11` — defensive analysis

### Step 8: War Room Enhancements

Add to the existing War Room:

1. **Chamber Map** — radial grid of all 11 chambers
   - Each tile shows: chamber number, name, status pulse (green/amber/red)
   - Click to drill into chamber detail
   - Green = healthy, Amber = attention, Red = action needed

2. **Active Alerts Panel** (right side)
   - Real-time feed sorted by severity
   - Source: all chambers
   - Click to see detail + take action

3. **LLM Answer Diff View**
   - Select a query, see how each LLM's answer changed over 30 days
   - Side-by-side comparison with highlighted changes
   - Shows: mention gained/lost, sentiment shift, position change

4. **Semantic Neighbourhood Map**
   - D3.js 2D scatter plot
   - Domain vs competitors vs topic cluster centroids
   - Click nodes for detail
   - Dark theme colours

5. **Journey Timeline**
   - Chronological record of every Peterman action
   - Each entry: timestamp, chamber source, action, score impact
   - Rollback button on applicable entries (within 30 days)
   - Filterable by chamber, action type, date range

### Step 9: APScheduler Integration

Build `app/services/scheduler.py`:

| Task | Default Cadence | Chamber |
|------|----------------|---------|
| LLM probes (priority keywords) | Weekly | Chamber 1 |
| Technical health scan | Daily | Chamber 6 |
| Defensive perception scan | Weekly | Chamber 11 |
| Competitor monitoring | Weekly | Chamber 8 |
| Oracle forecast update | Weekly | Chamber 9 |
| Content performance check | Daily | Chamber 7 |
| LCRI re-scoring | After content deploy | Chamber 3 |
| SGS recalculation | After probes complete | Chamber 2 |
| Budget reconciliation | Hourly | Budget Monitor |
| Peterman Score recompute | After any chamber cycle | Score Engine |

All schedules configurable per domain.

---

## PHASE 2 SMOKE TEST

1. ✅/❌ All 11 chambers return real data (not stubs, not 50.0)
2. ✅/❌ Semantic Map renders with domain + competitor positions
3. ✅/❌ LCRI scores calculated for crawled pages
4. ✅/❌ Competitor discovery works (finds competitors from probe data)
5. ✅/❌ Oracle generates 90-day calendar
6. ✅/❌ Defensive Shield detects negative narrative probes
7. ✅/❌ Chamber Map shows all 11 with correct status
8. ✅/❌ Journey Timeline shows all actions chronologically
9. ✅/❌ LLM Answer Diff shows changes over time
10. ✅/❌ APScheduler runs chamber cycles on schedule
11. ✅/❌ All Phase 1 tests still pass (regression)

ALL 11 must pass.

---

## PHASE 2 AUDIT

After smoke test passes, verify:
1. Every chamber file exists with real implementation (not stubs)
2. No hardcoded scores anywhere: `grep -rn "50.0" app/ --include="*.py"`
3. No cloud API imports: `grep -ri "import openai\|import anthropic" app/ --include="*.py"`
4. Australian English check on all new code
5. All new endpoints return real data
6. Scheduler runs without errors for 10 minutes

Produce: PETERMAN-PHASE2-AUDIT-2026-02-XX.md
