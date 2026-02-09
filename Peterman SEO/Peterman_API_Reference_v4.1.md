# Peterman V4.1 — Complete API Reference with Open Source Alternatives
## The Authority & Presence Engine
### Port: 5008 | Base URL: http://localhost:5008/api

### Hardware: Windows 11 | RTX 5070 (12GB VRAM) | 128GB RAM | 200GB+ Free Disk

---

## Your Local AI Stack

| Model | Ollama Command | Size | Role | Speed |
|-------|---------------|------|------|-------|
| **Llama 3.3 70B Q4** | `ollama pull llama3.3:70b-instruct-q4_K_M` | ~40GB RAM + GPU | Heavy: scanning, scoring, analysis, classification | 5–10 tok/s |
| **Gemma 2 27B** | `ollama pull gemma2:27b` | ~16GB RAM + GPU | Fast: extraction, quick scoring, replaces Gemini | 15–25 tok/s |
| **Qwen** | Already installed | Varies | Utility: lightweight tasks | Fast |
| **nomic-embed-text** | `ollama pull nomic-embed-text` ✅ Done | 274MB | All embeddings and vector work | Instant |

### Infrastructure
| Tool | Purpose | Replaces |
|------|---------|----------|
| **Ollama** (localhost:11434) | Local LLM runtime | 80% of OpenAI/Anthropic/Gemini API calls |
| **PostgreSQL 17 + pgvector** (localhost:5432) | Database + vector storage | Pinecone ($70+/mo) |
| **SearXNG** (Docker, localhost:8888) | Self-hosted meta-search | Google Search API + Bing API + NewsAPI ($300+/mo) |
| **Playwright + Crawlee** | Browser automation + crawling | ScrapingBee + Diffbot ($350–$600/mo) |

---

## Legend

| Symbol | Meaning |
|--------|---------|
| 🟢 | Fully replaced by open source — zero cost |
| 🟡 | Hybrid — local primary, paid API for specific features |
| 🔴 | Keep paid API — no quality-equivalent alternative |
| ⚪ | No external API — internal/local only |

---

## Health & System

| # | Method | Endpoint | Paid API | Local/Open Source Alternative | Verdict |
|---|--------|----------|----------|-------------------------------|---------|
| 1 | GET | `/api/health` | None | N/A | ⚪ |
| 2 | GET | `/api/status` | None | N/A | ⚪ |
| 3 | POST | `/api/elaine/register` | Elaine (internal) | N/A | ⚪ |
| 4 | POST | `/api/elaine/webhook` | Elaine (internal) | N/A | ⚪ |
| 5 | GET | `/api/config` | None | N/A | ⚪ |
| 6 | PUT | `/api/config` | None | N/A | ⚪ |

---

## Brand Profiles

| # | Method | Endpoint | Paid API | Local/Open Source Alternative | Verdict |
|---|--------|----------|----------|-------------------------------|---------|
| 7 | GET | `/api/brands` | None | N/A | ⚪ |
| 8 | POST | `/api/brands` | ScrapingBee, Clearbit | Playwright+Crawlee (crawl), MaxMind GeoIP2 (company) | 🟢 |
| 9 | GET | `/api/brands/:id` | None | N/A | ⚪ |
| 10 | PUT | `/api/brands/:id` | None | N/A | ⚪ |
| 11 | DELETE | `/api/brands/:id` | None | N/A | ⚪ |
| 12 | POST | `/api/brands/:id/competitors` | ScrapingBee, Clearbit | Playwright+Crawlee, Wappalyzer, python-whois | 🟢 |
| 13 | GET | `/api/brands/:id/competitors` | None | N/A | ⚪ |
| 14 | POST | `/api/brands/:id/keywords` | Google Search, OpenAI | SearXNG (volume check), Ollama+Llama 3.3 (keyword expansion) | 🟢 |
| 15 | GET | `/api/brands/:id/keywords` | None | N/A | ⚪ |
| 16 | PUT | `/api/brands/:id/keywords/:kid/approve` | None | N/A | ⚪ |
| 17 | GET | `/api/brands/:id/dashboard` | None | N/A | ⚪ |

---

## Chamber 1: The Perception Scan

| # | Method | Endpoint | Paid API | Local/Open Source Alternative | Verdict |
|---|--------|----------|----------|-------------------------------|---------|
| 18 | POST | `/api/scan/perception/:brand_id` | OpenAI, Anthropic, Gemini, Perplexity, Bing | Ollama+Llama 3.3 (primary), Gemma 2 (replaces Gemini), SearXNG (replaces Bing). **Keep OpenAI+Claude+Perplexity** — must query real commercial models to see what they tell users. | 🟡 |
| 19 | GET | `/api/scan/perception/:brand_id/latest` | None | N/A | ⚪ |
| 20 | GET | `/api/scan/perception/:brand_id/history` | None | N/A | ⚪ |
| 21 | GET | `/api/hallucinations/:brand_id` | None | N/A | ⚪ |
| 22 | GET | `/api/hallucinations/:brand_id/:id` | None | N/A | ⚪ |
| 23 | PUT | `/api/hallucinations/:brand_id/:id/status` | None | N/A | ⚪ |
| 24 | GET | `/api/hallucinations/:brand_id/inertia` | None | Computed from historical scan data | ⚪ |
| 25 | GET | `/api/sov/:brand_id` | None | N/A | ⚪ |
| 26 | GET | `/api/sov/:brand_id/history` | None | N/A | ⚪ |
| 27 | GET | `/api/sov/:brand_id/velocity` | None | Computed from history | ⚪ |
| 28 | GET | `/api/trust-class/:brand_id` | OpenAI | Ollama+Llama 3.3 (classify citation context) | 🟢 |
| 29 | POST | `/api/scan/crisis/:brand_id` | OpenAI, Anthropic, Perplexity | **Keep all three** — crisis accuracy is non-negotiable. Must query real models. | 🔴 |

---

## Chamber 2: The Semantic Core

| # | Method | Endpoint | Paid API | Local/Open Source Alternative | Verdict |
|---|--------|----------|----------|-------------------------------|---------|
| 30 | POST | `/api/scan/semantic/:brand_id` | OpenAI Embeddings, Cohere | **nomic-embed-text via Ollama** (already installed, local, zero cost) | 🟢 |
| 31 | GET | `/api/drift/:brand_id` | None | N/A | ⚪ |
| 32 | GET | `/api/drift/:brand_id/history` | None | N/A | ⚪ |
| 33 | GET | `/api/drift/:brand_id/alerts` | Slack (free) | Slack (free). Backup: Gotify/ntfy.sh | ⚪ |
| 34 | GET | `/api/silence/:brand_id` | None | Computed from scan gaps | ⚪ |
| 35 | GET | `/api/narrative/:brand_id` | OpenAI | Ollama+Llama 3.3 (contradiction detection) | 🟢 |
| 36 | GET | `/api/fingerprint/:brand_id` | None | N/A | ⚪ |
| 37 | GET | `/api/fingerprint/:brand_id/compare` | None | pgvector cosine similarity (local) | ⚪ |

---

## Chamber 3: The Neural Vector Map

| # | Method | Endpoint | Paid API | Local/Open Source Alternative | Verdict |
|---|--------|----------|----------|-------------------------------|---------|
| 38 | POST | `/api/vectormap/:brand_id/generate` | OpenAI, Anthropic, OpenAI Embeddings | Ollama+Llama 3.3 (probe), nomic-embed-text (vectors). **Keep OpenAI+Claude** for nuanced brand-attribute probing on real commercial models. | 🟡 |
| 39 | GET | `/api/vectormap/:brand_id` | None | N/A | ⚪ |
| 40 | GET | `/api/vectormap/:brand_id/competitors` | None | N/A | ⚪ |
| 41 | GET | `/api/vectormap/:brand_id/trajectory` | None | N/A | ⚪ |
| 42 | GET | `/api/vectormap/:brand_id/neighbours` | None | pgvector nearest neighbour (local) | ⚪ |
| 43 | GET | `/api/vectormap/:brand_id/ego-network` | OpenAI | Ollama+Llama 3.3 (relationship probing) | 🟢 |

---

## Chamber 4: The Authority Engine

| # | Method | Endpoint | Paid API | Local/Open Source Alternative | Verdict |
|---|--------|----------|----------|-------------------------------|---------|
| 44 | POST | `/api/authority/:brand_id/scan` | OpenAI, Google Search, Ahrefs | Ollama+Llama 3.3 (analysis), SearXNG (SERP), CommonCrawl (link data) | 🟢 |
| 45 | GET | `/api/authority/:brand_id` | None | N/A | ⚪ |
| 46 | GET | `/api/authority/:brand_id/graph` | None | N/A | ⚪ |
| 47 | GET | `/api/authority/:brand_id/gaps` | None | N/A | ⚪ |
| 48 | GET | `/api/authority/:brand_id/thin-zones` | None | N/A | ⚪ |
| 49 | GET | `/api/flywheel/:brand_id` | None | Internal ML (scikit-learn on stored data) | ⚪ |
| 50 | GET | `/api/flywheel/:brand_id/signals` | Search Console (free), GA4 (free) | Already free | ⚪ |
| 51 | GET | `/api/flywheel/:brand_id/recommendations` | OpenAI | Ollama+Llama 3.3 (generate recommendations) | 🟢 |
| 52 | GET | `/api/saturation/:brand_id` | None | Computed from velocity + signal data | ⚪ |
| 53 | GET | `/api/answer-worthiness/:brand_id` | OpenAI | Ollama+Llama 3.3 (score against 7 factors) | 🟢 |
| 54 | POST | `/api/answer-worthiness/score` | OpenAI | Ollama+Llama 3.3 | 🟢 |

---

## Chamber 5: The Survivability Lab

| # | Method | Endpoint | Paid API | Local/Open Source Alternative | Verdict |
|---|--------|----------|----------|-------------------------------|---------|
| 55 | POST | `/api/survivability/:brand_id/test` | OpenAI, Anthropic, Embeddings | Ollama+Llama 3.3 (compression passes), nomic-embed-text (preservation scoring) | 🟢 |
| 56 | POST | `/api/survivability/test-content` | OpenAI, Anthropic, Embeddings | Same as above | 🟢 |
| 57 | GET | `/api/survivability/:brand_id` | None | N/A | ⚪ |
| 58 | GET | `/api/survivability/:brand_id/:content_id` | None | N/A | ⚪ |
| 59 | GET | `/api/preservation/:brand_id` | None | N/A | ⚪ |
| 60 | POST | `/api/preservation/test` | OpenAI | Ollama+Llama 3.3 (intent comparison) | 🟢 |
| 61 | GET | `/api/first-answer/:brand_id` | OpenAI, Anthropic, Gemini | Ollama+Gemma 2 (local). **Keep OpenAI+Claude** — must test real commercial models. | 🟡 |

---

## Chamber 6: The Machine Interface

| # | Method | Endpoint | Paid API | Local/Open Source Alternative | Verdict |
|---|--------|----------|----------|-------------------------------|---------|
| 62 | POST | `/api/technical/:brand_id/audit` | ScrapingBee, PageSpeed (free), Search Console (free) | Playwright+Crawlee (crawl), Wappalyzer (tech detect), custom JSON-LD validator | 🟢 |
| 63 | GET | `/api/technical/:brand_id` | None | N/A | ⚪ |
| 64 | GET | `/api/technical/:brand_id/checklist` | None | N/A | ⚪ |
| 65 | POST | `/api/rag-packets/:brand_id/generate` | OpenAI | Ollama+Llama 3.3 (extract atomic facts) | 🟢 |
| 66 | GET | `/api/rag-packets/:brand_id` | None | N/A | ⚪ |
| 67 | POST | `/api/authority-protocol/:brand_id/generate` | OpenAI | Ollama+Llama 3.3 | 🟢 |
| 68 | GET | `/api/authority-protocol/:brand_id` | None | N/A | ⚪ |
| 69 | POST | `/api/agent-manifest/:brand_id/generate` | OpenAI | Ollama+Llama 3.3 | 🟢 |
| 70 | GET | `/api/agent-manifest/:brand_id` | None | N/A | ⚪ |
| 71 | GET | `/api/token-density/:brand_id` | OpenAI tokenizer | tiktoken library (local, zero cost) | 🟢 |
| 72 | POST | `/api/token-density/analyse` | OpenAI tokenizer | tiktoken (local) | 🟢 |

---

## Chamber 7: The Amplifier

| # | Method | Endpoint | Paid API | Local/Open Source Alternative | Verdict |
|---|--------|----------|----------|-------------------------------|---------|
| 73 | POST | `/api/citation-magnet/score` | OpenAI | Ollama+Llama 3.3 (sentence-level scoring) | 🟢 |
| 74 | POST | `/api/citation-magnet/rewrite` | OpenAI/Anthropic | **Keep** — client-facing content quality ceiling | 🔴 |
| 75 | GET | `/api/citation-magnet/:brand_id/scores` | None | N/A | ⚪ |
| 76 | POST | `/api/atomiser/generate` | OpenAI/Anthropic | **Keep** — multi-format content generation needs quality | 🔴 |
| 77 | GET | `/api/atomiser/:brand_id/assets` | None | N/A | ⚪ |
| 78 | GET | `/api/competitors/:brand_id/shadow` | ScrapingBee, Diffbot, NewsAPI | Playwright+Crawlee+Trafilatura (crawl+extract), SearXNG news+RSS, Wayback Machine API | 🟢 |
| 79 | GET | `/api/competitors/:brand_id/citations` | OpenAI, Anthropic, Perplexity | Ollama primary. **Keep Perplexity** for Perplexity-specific citation tracking. | 🟡 |
| 80 | GET | `/api/competitors/:brand_id/structural` | ScrapingBee | Playwright+Crawlee | 🟢 |
| 81 | GET | `/api/competitors/:brand_id/predictions` | OpenAI | Ollama+Llama 3.3 (ML prediction from patterns) | 🟢 |
| 82 | GET | `/api/competitors/:brand_id/counter-strategy` | OpenAI | **Keep** — strategic reasoning needs quality ceiling | 🔴 |
| 83 | GET | `/api/competitors/:brand_id/displacement` | None | Computed from Chamber 1 history | ⚪ |

---

## Chamber 8: The Proof

| # | Method | Endpoint | Paid API | Local/Open Source Alternative | Verdict |
|---|--------|----------|----------|-------------------------------|---------|
| 84 | GET | `/api/proof/:brand_id/traffic` | GA4 (free) | Already free | ⚪ |
| 85 | GET | `/api/proof/:brand_id/conversions` | GA4 (free) | Already free | ⚪ |
| 86 | GET | `/api/proof/:brand_id/attribution` | GA4 (free), Search Console (free) | Already free + internal ML | ⚪ |
| 87 | GET | `/api/proof/:brand_id/roi` | None | Computed | ⚪ |
| 88 | GET | `/api/proof/:brand_id/intent` | OpenAI | Ollama+Llama 3.3 (infer query from behaviour) | 🟢 |
| 89 | GET | `/api/leads/:brand_id` | Clearbit, GA4 (free) | MaxMind GeoIP2 (free) + OpenCorporates (free). Snitcher ($39/mo) for scale. | 🟡 |
| 90 | GET | `/api/leads/:brand_id/:lead_id` | Clearbit, OpenAI | Snitcher ($39) + Ollama+Llama 3.3 (sales playbook) | 🟡 |
| 91 | GET | `/api/leads/:brand_id/hot` | None | Filtered from lead data | ⚪ |
| 92 | POST | `/api/leads/:brand_id/:lead_id/push-crm` | HubSpot (free) / Salesforce (client) | Already free/client-provided | ⚪ |
| 93 | GET | `/api/visitors/:brand_id` | Clearbit Reveal, GA4 (free) | MaxMind/Snitcher + GA4 | 🟡 |
| 94 | GET | `/api/visitors/:brand_id/competitors` | Clearbit | MaxMind/Snitcher + internal matching | 🟡 |
| 95 | GET | `/api/proof/:brand_id/cta-performance` | GA4 (free) | Already free | ⚪ |

---

## Chamber 9: The Oracle

| # | Method | Endpoint | Paid API | Local/Open Source Alternative | Verdict |
|---|--------|----------|----------|-------------------------------|---------|
| 96 | POST | `/api/oracle/:brand_id/scan` | SerpApi, NewsAPI, Twitter/X + free APIs | pytrends (free), SearXNG news+RSS (free), Nitter/snscrape (free), GDELT (free), Semantic Scholar (free), arXiv (free), Reddit (free) | 🟢 |
| 97 | GET | `/api/oracle/:brand_id/opportunities` | None | Computed | ⚪ |
| 98 | GET | `/api/oracle/:brand_id/opportunities/:id` | OpenAI | Ollama+Llama 3.3 primary. **Keep OpenAI** for high-stakes strategic action plans. | 🟡 |
| 99 | GET | `/api/oracle/:brand_id/forecast` | None | Internal ML (scikit-learn/PyTorch, local) | ⚪ |
| 100 | GET | `/api/oracle/:brand_id/framing` | OpenAI, Anthropic, Gemini | Ollama+Gemma 2 (local). **Keep OpenAI+Claude** — must query real commercial models to see real framing. | 🟡 |
| 101 | GET | `/api/oracle/:brand_id/framing/shifts` | None | Computed | ⚪ |
| 102 | GET | `/api/oracle/:brand_id/trends` | SerpApi, NewsAPI, Twitter/X | pytrends, SearXNG+RSS, Nitter, GDELT, Semantic Scholar, arXiv | 🟢 |
| 103 | GET | `/api/oracle/:brand_id/competitor-trajectory` | None | Internal ML + Ch 7 data | ⚪ |

---

## Chamber 10: The Forge

| # | Method | Endpoint | Paid API | Local/Open Source Alternative | Verdict |
|---|--------|----------|----------|-------------------------------|---------|
| 104 | GET | `/api/forge/:brand_id/pipeline` | None | N/A | ⚪ |
| 105 | GET | `/api/forge/:brand_id/pipeline/:id` | None | N/A | ⚪ |
| 106 | POST | `/api/forge/:brand_id/trigger` | None | N/A | ⚪ |
| 107 | POST | `/api/forge/:brand_id/brief/:id` | OpenAI/Anthropic | **Keep** — content quality is client-facing | 🔴 |
| 108 | PUT | `/api/forge/:brand_id/brief/:id/approve` | Slack (free) | Already free | ⚪ |
| 109 | POST | `/api/forge/:brand_id/draft/:id` | OpenAI/Anthropic | **Keep** — content quality IS the product | 🔴 |
| 110 | PUT | `/api/forge/:brand_id/draft/:id/approve` | Slack (free) | Already free | ⚪ |
| 111 | POST | `/api/forge/:brand_id/deploy/:id` | WordPress (free), LinkedIn (free), Medium (free) | All free/client-provided. Listmonk for email. | ⚪ |
| 112 | GET | `/api/forge/:brand_id/deploy/:id/status` | None | N/A | ⚪ |
| 113 | POST | `/api/forge/:brand_id/verify/:id` | OpenAI, Anthropic, Perplexity | Ollama primary. **Keep paid APIs** for accurate cross-model verification. | 🟡 |
| 114 | GET | `/api/forge/:brand_id/verify/:id/result` | None | N/A | ⚪ |
| 115 | GET | `/api/forge/:brand_id/history` | None | N/A | ⚪ |
| 116 | GET | `/api/forge/:brand_id/metrics` | None | N/A | ⚪ |

---

## Crisis Mode

| # | Method | Endpoint | Paid API | Local/Open Source Alternative | Verdict |
|---|--------|----------|----------|-------------------------------|---------|
| 117 | POST | `/api/crisis/:brand_id/activate` | Slack (free) | Already free. Gotify as backup. | ⚪ |
| 118 | POST | `/api/crisis/:brand_id/deactivate` | Slack (free) | Already free | ⚪ |
| 119 | GET | `/api/crisis/:brand_id/status` | None | N/A | ⚪ |
| 120 | GET | `/api/crisis/:brand_id/alerts` | None | N/A | ⚪ |
| 121 | PUT | `/api/crisis/:brand_id/alerts/:id/acknowledge` | Slack (free) | Already free | ⚪ |
| 122 | POST | `/api/crisis/:brand_id/respond/:id` | OpenAI/Anthropic, Twilio | **Keep OpenAI/Claude** (crisis content must be perfect). Gotify for push; keep Twilio for SMS only. | 🟡 |
| 123 | GET | `/api/crisis/templates` | None | N/A | ⚪ |

---

## Reports

| # | Method | Endpoint | Paid API | Local/Open Source Alternative | Verdict |
|---|--------|----------|----------|-------------------------------|---------|
| 124 | GET | `/api/reports/:brand_id` | None | N/A | ⚪ |
| 125 | GET | `/api/reports/:brand_id/:id` | None | N/A | ⚪ |
| 126 | POST | `/api/reports/:brand_id/generate` | OpenAI | Ollama+Llama 3.3 for data analysis. **Keep OpenAI** for executive narrative prose. | 🟡 |
| 127 | GET | `/api/reports/:brand_id/schedule` | None | N/A | ⚪ |
| 128 | PUT | `/api/reports/:brand_id/schedule` | None | N/A | ⚪ |
| 129 | GET | `/api/reports/:brand_id/executive-summary` | OpenAI | **Keep** — narrative quality matters for client-facing | 🔴 |
| 130 | POST | `/api/reports/:brand_id/export/:format` | SendGrid | WeasyPrint (PDF), python-docx (DOCX), Listmonk (email) — all local | 🟢 |

---

## Scanning & Client Zero

| # | Method | Endpoint | Paid API | Local/Open Source Alternative | Verdict |
|---|--------|----------|----------|-------------------------------|---------|
| 131 | GET | `/api/scans/:brand_id` | None | N/A | ⚪ |
| 132 | GET | `/api/scans/:brand_id/schedule` | None | N/A | ⚪ |
| 133 | PUT | `/api/scans/:brand_id/schedule` | None | N/A | ⚪ |
| 134 | POST | `/api/scans/:brand_id/full` | All APIs | Open source for 80%+. See individual chambers. | 🟡 |
| 135 | GET | `/api/scans/:brand_id/queue` | None | N/A | ⚪ |
| 136 | GET | `/api/scans/:brand_id/costs` | None | N/A | ⚪ |
| 137 | GET | `/api/client-zero/baseline` | None | N/A | ⚪ |
| 138 | GET | `/api/client-zero/progress` | None | N/A | ⚪ |
| 139 | GET | `/api/client-zero/costs` | None | N/A | ⚪ |
| 140 | GET | `/api/client-zero/case-study` | OpenAI | **Keep** — case study narrative quality matters | 🔴 |

---

## Summary

| Verdict | Count | % | Description |
|---------|-------|---|-------------|
| ⚪ No external API | 88 | 63% | Internal/local only — zero cost |
| 🟢 Fully open source | 28 | 20% | Replaced entirely — zero ongoing cost |
| 🟡 Hybrid | 15 | 11% | Local primary, paid for quality-critical features |
| 🔴 Keep paid API | 9 | 6% | Content generation, crisis, executive narratives |

**83% of endpoints cost nothing. Only 9 endpoints (6%) require paid APIs.**

---

## Only 4 Paid APIs Retained

| API | Why Irreplaceable | Est. Monthly Cost |
|-----|-------------------|-------------------|
| **OpenAI GPT-4** | Content generation quality ceiling. Client-facing drafts, executive narratives, strategic analysis. Llama 3.3 is ~75% quality — noticeable gap. | $30–$150 |
| **Anthropic Claude** | Cross-model verification. Must check MULTIPLE DIFFERENT commercial models. Can't replace real Claude with local model. | $20–$80 |
| **Perplexity API** | Brand-specific citation tracking. Must see what Perplexity specifically tells users about brands. Cannot simulate locally. | $30–$100 |
| **Snitcher** | IP-to-company at scale. Free MaxMind identifies ~40% of visitors. Snitcher ~65%. Gap matters for lead scoring. | $39 |
| **TOTAL** | | **$119–$369/mo** |

---

## OSINT Tools (All Free)

| Tool | What It Provides | Used By |
|------|-----------------|---------|
| Semantic Scholar API | Academic paper tracking | Chamber 9 |
| arXiv API | Research paper monitoring | Chamber 9 |
| pytrends | Google Trends data (replaces $250/mo SerpApi) | Chamber 9 |
| GDELT Project | Global news/event monitoring | Chamber 9 |
| Nitter + snscrape | Twitter/X read access (replaces $100+/mo API) | Chamber 9 |
| SpiderFoot | OSINT framework (200+ sources) | Chambers 7, 9 |
| Wappalyzer | Technology detection on websites | Chamber 6 |
| Wayback Machine API | Historical competitor content | Chamber 7 |
| CommonCrawl | Web archive for authority analysis | Chambers 4, 7 |
| OpenCorporates | Company registration data | Chamber 8 |
| MaxMind GeoIP2 | IP-to-company (basic, free) | Chamber 8 |
| Shodan free tier | Tech stack detection (100 queries/mo) | Chambers 6, 7 |
| Google Alerts | Brand/competitor monitoring | Chambers 1, 7 |
| Hunter.io free tier | Email verification (25/mo) | Chamber 8 |

---

## Cost Impact on Your Hardware

| Category | If All Paid APIs | With Your Local Stack | Saving |
|----------|-----------------|----------------------|--------|
| LLM inference | $140–$700/mo | $30–$150/mo (OpenAI+Claude only for 9 endpoints) | 75–80% |
| Search & web | $300–$600/mo | $0 (SearXNG + Playwright local) | 100% |
| Embeddings & vectors | $70–$100/mo | $0 (nomic-embed-text + pgvector local) | 100% |
| Research & intelligence | $150–$5,700/mo | $0 (all free OSINT tools) | 100% |
| Technical SEO | $100–$1,200/mo | $0 (Playwright + custom scripts) | 100% |
| Visitor intelligence | $99–$999/mo | $39/mo (Snitcher only) | 60–96% |
| Communication | $15–$110/mo | $0–$5 (Twilio SMS only for crisis) | 95% |
| **TOTAL PER CLIENT** | **$874–$9,409/mo** | **$69–$194/mo** | **92–98%** |

### Revised Margins

| Tier | Revenue | Your Actual Cost | Margin |
|------|---------|-----------------|--------|
| Growth ($4,995/mo) | $4,995 | $69–$100 | **98–99%** |
| Authority ($7,995/mo) | $7,995 | $100–$150 | **98–99%** |
| Enterprise ($12,995/mo) | $12,995 | $150–$194 | **98–99%** |

Your hardware investment: $0 additional (you already own it). Electricity: ~$20–$40/mo extra when running scans.
