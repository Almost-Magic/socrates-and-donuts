# Peterman V4.1 — Complete API Reference with Open Source Alternatives
## The Authority & Presence Engine
### Port: 5008 | Base URL: http://localhost:5008/api

---

## Legend

| Symbol | Meaning |
|--------|---------|
| 🟢 | Fully replaced by open source — no paid API needed |
| 🟡 | Hybrid — open source primary, paid API for specific features |
| 🔴 | Keep paid API — no quality-equivalent open source exists |
| ⚪ | No external API — internal/local only |

---

## Health & System

| # | Method | Endpoint | Description | Paid API | Open Source Alternative | Verdict |
|---|--------|----------|-------------|----------|----------------------|---------|
| 1 | GET | `/api/health` | Health check | None | N/A | ⚪ |
| 2 | GET | `/api/status` | System status, queue depth | None | N/A | ⚪ |
| 3 | POST | `/api/elaine/register` | Register with Elaine | Elaine (internal) | N/A | ⚪ |
| 4 | POST | `/api/elaine/webhook` | Receive tasks from Elaine | Elaine (internal) | N/A | ⚪ |
| 5 | GET | `/api/config` | Get configuration | None | N/A | ⚪ |
| 6 | PUT | `/api/config` | Update configuration | None | N/A | ⚪ |

---

## Brand Profiles

| # | Method | Endpoint | Description | Paid API | Open Source Alternative | Verdict |
|---|--------|----------|-------------|----------|----------------------|---------|
| 7 | GET | `/api/brands` | List all brands | None | N/A | ⚪ |
| 8 | POST | `/api/brands` | Create brand profile | ScrapingBee, Clearbit | Playwright+Crawlee (crawl), MaxMind GeoIP2 (company) | 🟢 |
| 9 | GET | `/api/brands/:id` | Get brand profile | None | N/A | ⚪ |
| 10 | PUT | `/api/brands/:id` | Update brand profile | None | N/A | ⚪ |
| 11 | DELETE | `/api/brands/:id` | Archive brand | None | N/A | ⚪ |
| 12 | POST | `/api/brands/:id/competitors` | Add competitors | ScrapingBee, Clearbit | Playwright+Crawlee, Wappalyzer, WHOIS | 🟢 |
| 13 | GET | `/api/brands/:id/competitors` | List competitors | None | N/A | ⚪ |
| 14 | POST | `/api/brands/:id/keywords` | Add keywords | Google Search API, OpenAI | SearXNG (volume), Ollama+Llama 3.3 (expansion) | 🟢 |
| 15 | GET | `/api/brands/:id/keywords` | List keywords | None | N/A | ⚪ |
| 16 | PUT | `/api/brands/:id/keywords/:kid/approve` | Approve keyword | None | N/A | ⚪ |
| 17 | GET | `/api/brands/:id/dashboard` | Full dashboard | None | N/A | ⚪ |

---

## Chamber 1: The Perception Scan

| # | Method | Endpoint | Description | Paid API | Open Source Alternative | Verdict |
|---|--------|----------|-------------|----------|----------------------|---------|
| 18 | POST | `/api/scan/perception/:brand_id` | Full perception scan | OpenAI, Anthropic, Gemini, Perplexity, Bing | Ollama+Llama 3.3 (primary), Ollama+Gemma 2 (replaces Gemini). Keep OpenAI+Claude+Perplexity for cross-model. | 🟡 |
| 19 | GET | `/api/scan/perception/:brand_id/latest` | Latest scan results | None | N/A | ⚪ |
| 20 | GET | `/api/scan/perception/:brand_id/history` | Historical scans | None | N/A | ⚪ |
| 21 | GET | `/api/hallucinations/:brand_id` | List hallucinations | None | N/A | ⚪ |
| 22 | GET | `/api/hallucinations/:brand_id/:id` | Hallucination detail | None | N/A | ⚪ |
| 23 | PUT | `/api/hallucinations/:brand_id/:id/status` | Update status | None | N/A | ⚪ |
| 24 | GET | `/api/hallucinations/:brand_id/inertia` | Inertia report | None | N/A (computed from historical data) | ⚪ |
| 25 | GET | `/api/sov/:brand_id` | Share of Voice | None | N/A | ⚪ |
| 26 | GET | `/api/sov/:brand_id/history` | SoV historical | None | N/A | ⚪ |
| 27 | GET | `/api/sov/:brand_id/velocity` | Mention velocity | None | N/A (computed) | ⚪ |
| 28 | GET | `/api/trust-class/:brand_id` | Trust-class analysis | OpenAI | Ollama+Llama 3.3 (classify citation context) | 🟢 |
| 29 | POST | `/api/scan/crisis/:brand_id` | Crisis scan | OpenAI, Anthropic, Perplexity | Keep OpenAI+Claude+Perplexity for crisis (accuracy critical). | 🔴 |

---

## Chamber 2: The Semantic Core

| # | Method | Endpoint | Description | Paid API | Open Source Alternative | Verdict |
|---|--------|----------|-------------|----------|----------------------|---------|
| 30 | POST | `/api/scan/semantic/:brand_id` | Semantic fingerprint | OpenAI Embeddings, Cohere | BGE-large-en-v1.5 via Sentence-Transformers (local, better quality) | 🟢 |
| 31 | GET | `/api/drift/:brand_id` | Drift status | None | N/A | ⚪ |
| 32 | GET | `/api/drift/:brand_id/history` | Drift history | None | N/A | ⚪ |
| 33 | GET | `/api/drift/:brand_id/alerts` | Drift alerts | Slack (free) | Gotify (self-hosted) or ntfy.sh (free) as backup | ⚪ |
| 34 | GET | `/api/silence/:brand_id` | Silence detection | None | N/A (computed from scan gaps) | ⚪ |
| 35 | GET | `/api/narrative/:brand_id` | Narrative consistency | OpenAI | Ollama+Llama 3.3 (contradiction detection) | 🟢 |
| 36 | GET | `/api/fingerprint/:brand_id` | Fingerprint per LLM | None | N/A | ⚪ |
| 37 | GET | `/api/fingerprint/:brand_id/compare` | Compare over time | None | pgvector cosine similarity (local) | ⚪ |

---

## Chamber 3: The Neural Vector Map

| # | Method | Endpoint | Description | Paid API | Open Source Alternative | Verdict |
|---|--------|----------|-------------|----------|----------------------|---------|
| 38 | POST | `/api/vectormap/:brand_id/generate` | Generate vector map | OpenAI, Anthropic, OpenAI Embeddings | Ollama+Llama 3.3 (probe), BGE-large (embeddings). Keep OpenAI/Claude for nuanced brand-attribute probing. | 🟡 |
| 39 | GET | `/api/vectormap/:brand_id` | Vector positions | None | N/A | ⚪ |
| 40 | GET | `/api/vectormap/:brand_id/competitors` | With competitors | None | N/A | ⚪ |
| 41 | GET | `/api/vectormap/:brand_id/trajectory` | Movement over time | None | N/A | ⚪ |
| 42 | GET | `/api/vectormap/:brand_id/neighbours` | Semantic neighbours | None | pgvector nearest neighbour (local) | ⚪ |
| 43 | GET | `/api/vectormap/:brand_id/ego-network` | Adjacency map | OpenAI | Ollama+Llama 3.3 (relationship probing) | 🟢 |

---

## Chamber 4: The Authority Engine

| # | Method | Endpoint | Description | Paid API | Open Source Alternative | Verdict |
|---|--------|----------|-------------|----------|----------------------|---------|
| 44 | POST | `/api/authority/:brand_id/scan` | Authority analysis | OpenAI, Google Search, Ahrefs | Ollama+Llama 3.3, SearXNG (SERP), CommonCrawl (backlink proxy) | 🟢 |
| 45 | GET | `/api/authority/:brand_id` | Authority scores | None | N/A | ⚪ |
| 46 | GET | `/api/authority/:brand_id/graph` | Topic authority graph | None | N/A | ⚪ |
| 47 | GET | `/api/authority/:brand_id/gaps` | Authority gaps | None | N/A | ⚪ |
| 48 | GET | `/api/authority/:brand_id/thin-zones` | Thin zones | None | N/A | ⚪ |
| 49 | GET | `/api/flywheel/:brand_id` | Flywheel status | None | Internal ML model (scikit-learn) | ⚪ |
| 50 | GET | `/api/flywheel/:brand_id/signals` | Signal scores | Search Console (free), GA4 (free) | Already free | ⚪ |
| 51 | GET | `/api/flywheel/:brand_id/recommendations` | Recommendations | OpenAI | Ollama+Llama 3.3 (generate recommendations) | 🟢 |
| 52 | GET | `/api/saturation/:brand_id` | Saturation warnings | None | N/A (computed) | ⚪ |
| 53 | GET | `/api/answer-worthiness/:brand_id` | A-W scores | OpenAI | Ollama+Llama 3.3 (score against 7 factors) | 🟢 |
| 54 | POST | `/api/answer-worthiness/score` | Score content | OpenAI | Ollama+Llama 3.3 | 🟢 |

---

## Chamber 5: The Survivability Lab

| # | Method | Endpoint | Description | Paid API | Open Source Alternative | Verdict |
|---|--------|----------|-------------|----------|----------------------|---------|
| 55 | POST | `/api/survivability/:brand_id/test` | Survivability test | OpenAI, Anthropic, OpenAI Embeddings | Ollama+Llama 3.3 (compression passes), BGE-large (preservation scoring) | 🟢 |
| 56 | POST | `/api/survivability/test-content` | Test specific content | OpenAI, Anthropic, OpenAI Embeddings | Same as above | 🟢 |
| 57 | GET | `/api/survivability/:brand_id` | All scores | None | N/A | ⚪ |
| 58 | GET | `/api/survivability/:brand_id/:content_id` | Content report | None | N/A | ⚪ |
| 59 | GET | `/api/preservation/:brand_id` | Preservation scores | None | N/A | ⚪ |
| 60 | POST | `/api/preservation/test` | Test preservation | OpenAI | Ollama+Llama 3.3 (intent comparison) | 🟢 |
| 61 | GET | `/api/first-answer/:brand_id` | First answer bias | OpenAI, Anthropic, Gemini | Ollama primary. Keep OpenAI+Claude for real cross-model check. | 🟡 |

---

## Chamber 6: The Machine Interface

| # | Method | Endpoint | Description | Paid API | Open Source Alternative | Verdict |
|---|--------|----------|-------------|----------|----------------------|---------|
| 62 | POST | `/api/technical/:brand_id/audit` | Technical audit | ScrapingBee, PageSpeed (free), Search Console (free) | Playwright+Crawlee, Wappalyzer, custom JSON-LD validator | 🟢 |
| 63 | GET | `/api/technical/:brand_id` | Audit results | None | N/A | ⚪ |
| 64 | GET | `/api/technical/:brand_id/checklist` | Checklist | None | N/A | ⚪ |
| 65 | POST | `/api/rag-packets/:brand_id/generate` | Generate RAG packets | OpenAI | Ollama+Llama 3.3 (extract atomic facts) | 🟢 |
| 66 | GET | `/api/rag-packets/:brand_id` | Get packets | None | N/A | ⚪ |
| 67 | POST | `/api/authority-protocol/:brand_id/generate` | Generate authority.json | OpenAI | Ollama+Llama 3.3 (structure declarations) | 🟢 |
| 68 | GET | `/api/authority-protocol/:brand_id` | Get authority.json | None | N/A | ⚪ |
| 69 | POST | `/api/agent-manifest/:brand_id/generate` | Generate agent manifest | OpenAI | Ollama+Llama 3.3 | 🟢 |
| 70 | GET | `/api/agent-manifest/:brand_id` | Get manifest | None | N/A | ⚪ |
| 71 | GET | `/api/token-density/:brand_id` | Token density | OpenAI tokenizer | tiktoken library (local, no API) | 🟢 |
| 72 | POST | `/api/token-density/analyse` | Analyse content | OpenAI tokenizer | tiktoken (local) | 🟢 |

---

## Chamber 7: The Amplifier

| # | Method | Endpoint | Description | Paid API | Open Source Alternative | Verdict |
|---|--------|----------|-------------|----------|----------------------|---------|
| 73 | POST | `/api/citation-magnet/score` | Citation probability | OpenAI | Ollama+Llama 3.3 (sentence-level scoring) | 🟢 |
| 74 | POST | `/api/citation-magnet/rewrite` | Optimised rewrites | OpenAI/Anthropic | Keep — client-facing content quality ceiling | 🔴 |
| 75 | GET | `/api/citation-magnet/:brand_id/scores` | Brand scores | None | N/A | ⚪ |
| 76 | POST | `/api/atomiser/generate` | Atomise content | OpenAI/Anthropic | Keep — multi-format generation needs quality | 🔴 |
| 77 | GET | `/api/atomiser/:brand_id/assets` | Atomised assets | None | N/A | ⚪ |
| 78 | GET | `/api/competitors/:brand_id/shadow` | Competitor patterns | ScrapingBee, Diffbot, NewsAPI | Playwright+Crawlee+Trafilatura, SearXNG news+RSS, Wayback Machine API | 🟢 |
| 79 | GET | `/api/competitors/:brand_id/citations` | Competitor citations | OpenAI, Anthropic, Perplexity | Ollama primary. Keep Perplexity for Perplexity-specific checks. | 🟡 |
| 80 | GET | `/api/competitors/:brand_id/structural` | Structural analysis | ScrapingBee | Playwright+Crawlee (crawl + parse) | 🟢 |
| 81 | GET | `/api/competitors/:brand_id/predictions` | Move predictions | OpenAI | Ollama+Llama 3.3 (ML prediction) | 🟢 |
| 82 | GET | `/api/competitors/:brand_id/counter-strategy` | Counter-strategy | OpenAI | Keep — strategic reasoning needs quality ceiling | 🔴 |
| 83 | GET | `/api/competitors/:brand_id/displacement` | Displacement report | None | N/A (computed from Ch 1) | ⚪ |

---

## Chamber 8: The Proof

| # | Method | Endpoint | Description | Paid API | Open Source Alternative | Verdict |
|---|--------|----------|-------------|----------|----------------------|---------|
| 84 | GET | `/api/proof/:brand_id/traffic` | AI-referred traffic | GA4 (free) | Already free | ⚪ |
| 85 | GET | `/api/proof/:brand_id/conversions` | Conversions | GA4 (free) | Already free | ⚪ |
| 86 | GET | `/api/proof/:brand_id/attribution` | Attribution model | GA4 (free), Search Console (free) | Already free + internal ML | ⚪ |
| 87 | GET | `/api/proof/:brand_id/roi` | ROI dashboard | None | N/A (computed) | ⚪ |
| 88 | GET | `/api/proof/:brand_id/intent` | Intent reconstruction | OpenAI | Ollama+Llama 3.3 (infer query from behaviour) | 🟢 |
| 89 | GET | `/api/leads/:brand_id` | Lead list | Clearbit, GA4 (free) | MaxMind GeoIP2 (free) or Snitcher ($39/mo). OpenCorporates (free). | 🟡 |
| 90 | GET | `/api/leads/:brand_id/:lead_id` | Lead detail | Clearbit, OpenAI | Snitcher ($39) + Ollama+Llama 3.3 (playbook) | 🟡 |
| 91 | GET | `/api/leads/:brand_id/hot` | Hot leads | None | N/A (filtered) | ⚪ |
| 92 | POST | `/api/leads/:brand_id/:lead_id/push-crm` | Push to CRM | HubSpot (free)/Salesforce (client) | Already free/client-provided | ⚪ |
| 93 | GET | `/api/visitors/:brand_id` | Visitor intelligence | Clearbit Reveal, GA4 (free) | MaxMind/Snitcher + GA4 | 🟡 |
| 94 | GET | `/api/visitors/:brand_id/competitors` | Competitor visits | Clearbit | MaxMind/Snitcher + internal matching | 🟡 |
| 95 | GET | `/api/proof/:brand_id/cta-performance` | CTA performance | GA4 (free) | Already free | ⚪ |

---

## Chamber 9: The Oracle

| # | Method | Endpoint | Description | Paid API | Open Source Alternative | Verdict |
|---|--------|----------|-------------|----------|----------------------|---------|
| 96 | POST | `/api/oracle/:brand_id/scan` | Predictive scan | SerpApi, NewsAPI, Twitter/X API + free APIs | pytrends, SearXNG news+RSS, Nitter/snscrape, GDELT, Semantic Scholar (free), arXiv (free), Reddit (free) | 🟢 |
| 97 | GET | `/api/oracle/:brand_id/opportunities` | Opportunities | None | N/A (computed) | ⚪ |
| 98 | GET | `/api/oracle/:brand_id/opportunities/:id` | Opportunity detail | OpenAI | Ollama primary. Keep OpenAI for high-stakes strategic planning. | 🟡 |
| 99 | GET | `/api/oracle/:brand_id/forecast` | 6-12 month forecast | None | Internal ML (scikit-learn/PyTorch) | ⚪ |
| 100 | GET | `/api/oracle/:brand_id/framing` | Category framing | OpenAI, Anthropic, Gemini | Ollama+Gemma 2 (local). Keep OpenAI+Claude for real model framing analysis. | 🟡 |
| 101 | GET | `/api/oracle/:brand_id/framing/shifts` | Framing shifts | None | N/A (computed) | ⚪ |
| 102 | GET | `/api/oracle/:brand_id/trends` | Trend detection | SerpApi, NewsAPI, Twitter/X | pytrends, SearXNG+RSS, Nitter, GDELT, Semantic Scholar, arXiv | 🟢 |
| 103 | GET | `/api/oracle/:brand_id/competitor-trajectory` | Competitor trajectory | None | Internal ML + Ch 7 data | ⚪ |

---

## Chamber 10: The Forge

| # | Method | Endpoint | Description | Paid API | Open Source Alternative | Verdict |
|---|--------|----------|-------------|----------|----------------------|---------|
| 104 | GET | `/api/forge/:brand_id/pipeline` | Pipeline status | None | N/A | ⚪ |
| 105 | GET | `/api/forge/:brand_id/pipeline/:id` | Workflow detail | None | N/A | ⚪ |
| 106 | POST | `/api/forge/:brand_id/trigger` | Trigger workflow | None | N/A | ⚪ |
| 107 | POST | `/api/forge/:brand_id/brief/:id` | Generate brief | OpenAI/Anthropic | Keep — content quality is client-facing | 🔴 |
| 108 | PUT | `/api/forge/:brand_id/brief/:id/approve` | Approve brief | Slack (free) | Already free | ⚪ |
| 109 | POST | `/api/forge/:brand_id/draft/:id` | Generate draft | OpenAI/Anthropic | Keep — content quality is the product | 🔴 |
| 110 | PUT | `/api/forge/:brand_id/draft/:id/approve` | Approve draft | Slack (free) | Already free | ⚪ |
| 111 | POST | `/api/forge/:brand_id/deploy/:id` | Deploy to channels | WordPress (free), LinkedIn (free), Medium (free) | All free/client-provided. Listmonk for email. | ⚪ |
| 112 | GET | `/api/forge/:brand_id/deploy/:id/status` | Deploy status | None | N/A | ⚪ |
| 113 | POST | `/api/forge/:brand_id/verify/:id` | Verification scan | OpenAI, Anthropic, Perplexity | Ollama primary. Keep paid APIs for cross-model verification. | 🟡 |
| 114 | GET | `/api/forge/:brand_id/verify/:id/result` | Verification result | None | N/A | ⚪ |
| 115 | GET | `/api/forge/:brand_id/history` | Completed cycles | None | N/A | ⚪ |
| 116 | GET | `/api/forge/:brand_id/metrics` | Forge metrics | None | N/A | ⚪ |

---

## Crisis Mode

| # | Method | Endpoint | Description | Paid API | Open Source Alternative | Verdict |
|---|--------|----------|-------------|----------|----------------------|---------|
| 117 | POST | `/api/crisis/:brand_id/activate` | Activate crisis | Slack (free) | Already free. Gotify as backup. | ⚪ |
| 118 | POST | `/api/crisis/:brand_id/deactivate` | Deactivate | Slack (free) | Already free | ⚪ |
| 119 | GET | `/api/crisis/:brand_id/status` | Status | None | N/A | ⚪ |
| 120 | GET | `/api/crisis/:brand_id/alerts` | Alerts | None | N/A | ⚪ |
| 121 | PUT | `/api/crisis/:brand_id/alerts/:id/acknowledge` | Acknowledge | Slack (free) | Already free | ⚪ |
| 122 | POST | `/api/crisis/:brand_id/respond/:id` | Deploy response | OpenAI/Anthropic, Twilio | Keep OpenAI/Claude (crisis content must be perfect). Gotify replaces Twilio for push; keep Twilio SMS only. | 🟡 |
| 123 | GET | `/api/crisis/templates` | Templates | None | N/A | ⚪ |

---

## Reports

| # | Method | Endpoint | Description | Paid API | Open Source Alternative | Verdict |
|---|--------|----------|-------------|----------|----------------------|---------|
| 124 | GET | `/api/reports/:brand_id` | List reports | None | N/A | ⚪ |
| 125 | GET | `/api/reports/:brand_id/:id` | Get report | None | N/A | ⚪ |
| 126 | POST | `/api/reports/:brand_id/generate` | Generate report | OpenAI | Ollama for data analysis. Keep OpenAI for executive narrative. | 🟡 |
| 127 | GET | `/api/reports/:brand_id/schedule` | Schedule | None | N/A | ⚪ |
| 128 | PUT | `/api/reports/:brand_id/schedule` | Update schedule | None | N/A | ⚪ |
| 129 | GET | `/api/reports/:brand_id/executive-summary` | Exec summary | OpenAI | Keep — narrative quality matters for client-facing | 🔴 |
| 130 | POST | `/api/reports/:brand_id/export/:format` | Export | SendGrid | WeasyPrint (PDF), python-docx (DOCX), Listmonk (email) — all local | 🟢 |

---

## Scanning & Client Zero

| # | Method | Endpoint | Description | Paid API | Open Source Alternative | Verdict |
|---|--------|----------|-------------|----------|----------------------|---------|
| 131 | GET | `/api/scans/:brand_id` | Scan history | None | N/A | ⚪ |
| 132 | GET | `/api/scans/:brand_id/schedule` | Schedule | None | N/A | ⚪ |
| 133 | PUT | `/api/scans/:brand_id/schedule` | Update schedule | None | N/A | ⚪ |
| 134 | POST | `/api/scans/:brand_id/full` | Full 10-chamber scan | All APIs | Open source for 80%+. See chambers. | 🟡 |
| 135 | GET | `/api/scans/:brand_id/queue` | Queue | None | N/A | ⚪ |
| 136 | GET | `/api/scans/:brand_id/costs` | Cost tracking | None | N/A | ⚪ |
| 137 | GET | `/api/client-zero/baseline` | Baseline | None | N/A | ⚪ |
| 138 | GET | `/api/client-zero/progress` | Progress | None | N/A | ⚪ |
| 139 | GET | `/api/client-zero/costs` | Costs | None | N/A | ⚪ |
| 140 | GET | `/api/client-zero/case-study` | Case study | OpenAI | Keep — case study narrative quality matters | 🔴 |

---

## Summary

| Verdict | Count | % | Description |
|---------|-------|---|-------------|
| ⚪ No external API | 88 | 63% | Internal/local only — zero cost |
| 🟢 Fully open source | 28 | 20% | Replaced entirely — zero ongoing cost |
| 🟡 Hybrid | 15 | 11% | Open source primary, paid for quality-critical features |
| 🔴 Keep paid API | 9 | 6% | Content generation, crisis, executive narratives |

**83% of endpoints need zero paid APIs. Only 9 endpoints (6%) require paid APIs — all for client-facing content where quality is the product.**

---

## Only 4 Paid APIs Retained

| API | Why Irreplaceable | Est. Monthly Cost | Endpoints |
|-----|-------------------|-------------------|-----------|
| **OpenAI GPT-4** | Content generation quality ceiling. Client-facing drafts, executive narratives, strategic analysis. Local models are ~75% quality — noticeable gap. | $30–$150 | Ch 9 (strategy), Ch 10 (drafts), Reports, Crisis |
| **Anthropic Claude** | Cross-model verification. Hallucination detection requires checking MULTIPLE DIFFERENT models. Cannot replace with local copy. | $20–$80 | Ch 1 (cross-verify), Ch 10 (drafts), Crisis |
| **Perplexity API** | Brand-specific citation tracking. Must see what PERPLEXITY specifically tells users. Cannot simulate locally. | $30–$100 | Ch 1 (Perplexity scans), Ch 7 (competitor citations) |
| **Snitcher** | IP-to-company at scale. Free MaxMind identifies ~40%. Snitcher ~65%. Gap matters for lead scoring. | $39 | Ch 8 (leads, visitors) |
| **TOTAL** | | **$119–$369/mo** | |

---

## Open Source Stack

### Local LLM Infrastructure
| Tool | Purpose | Replaces |
|------|---------|----------|
| Ollama | Local LLM runtime | 80% of OpenAI/Anthropic/Gemini calls |
| Llama 3.3 70B | Primary local LLM (Meta, free commercial) | GPT-4 for scanning, scoring, classification |
| Gemma 2 27B | Secondary local LLM (Google, free) | Gemini API entirely |
| BGE-large-en-v1.5 | Embeddings (MIT, runs on CPU) | OpenAI Embeddings + Cohere (better quality) |
| PostgreSQL + pgvector | Vector storage + database | Pinecone ($70+/mo) |

### Web Crawling & Search
| Tool | Purpose | Replaces |
|------|---------|----------|
| SearXNG | Self-hosted meta-search (70+ sources) | Google Search API, Bing API, NewsAPI |
| Playwright | Browser automation (Apache 2.0) | ScrapingBee ($49–$299/mo) |
| Crawlee | Web crawler framework (Apache 2.0) | ScrapingBee (anti-bot, retries) |
| Trafilatura | Article content extraction (GPL) | Diffbot ($299+/mo) |
| Newspaper3k | News article parsing | Import.io |

### OSINT & Intelligence (All Free)
| Tool | Purpose | Used By |
|------|---------|---------|
| Semantic Scholar API | Academic paper tracking | Chamber 9 |
| arXiv API | Research paper monitoring | Chamber 9 |
| pytrends | Google Trends data (replaces $250/mo SerpApi) | Chamber 9 |
| GDELT Project | Global news/event monitoring | Chamber 9 |
| Nitter + snscrape | Twitter/X read access (replaces $100+/mo API) | Chamber 9 |
| SpiderFoot | OSINT framework (200+ sources) | Chambers 7, 9 |
| Wappalyzer | Technology detection | Chamber 6 |
| Wayback Machine API | Historical competitor content | Chamber 7 |
| CommonCrawl | Web archive for authority analysis | Chambers 4, 7 |
| OpenCorporates | Company registration data | Chamber 8 |
| MaxMind GeoIP2 | IP-to-company (basic, free) | Chamber 8 |
| Shodan free tier | Tech stack detection | Chambers 6, 7 |
| Google Alerts | Brand/competitor monitoring | Chambers 1, 7 |
| Hunter.io free tier | Email verification (25/mo) | Chamber 8 |

### Communication & Reporting
| Tool | Purpose | Replaces |
|------|---------|----------|
| Gotify / ntfy.sh | Self-hosted push notifications | Twilio for non-SMS alerts |
| Listmonk | Self-hosted email + newsletters (AGPL) | SendGrid, Mailchimp |
| WeasyPrint | PDF generation (BSD, local) | External PDF services |
| python-docx | DOCX generation (MIT, local) | External doc services |
| tiktoken | Token counting (MIT, local) | OpenAI tokenizer API |

### Hardware for Local LLMs
| Setup | GPU | VRAM | Cost | ROI |
|-------|-----|------|------|-----|
| Minimum | RTX 4090 | 24GB | $1,600 | Pays for itself in 3 months |
| Recommended | RTX A6000 | 48GB | $4,500 | Pays for itself in 6 months |
| Scale (multi-client) | 2× A6000 | 96GB | $9,000 | Pays for itself in 9 months |
