# Peterman

**Autonomous SEO & LLM Presence Engine**

Version 2.0.0 | Almost Magic Tech Lab

---

## Overview

Peterman is an autonomous agent that continuously monitors, analyses, plans, approves, executes, verifies, and reports on a domain's SEO and LLM (Large Language Model) presence.

## Features

- **Multi-domain management** — Manage unlimited domains from a single instance
- **LLM Share of Voice tracking** — Monitor how often AI models mention your brand
- **Semantic Gravity scoring** — Measure brand positioning in AI conceptual space
- **Technical Foundation auditing** — Automated site health checks
- **Content Survivability testing** — Verify content survives AI summarisation
- **Hallucination detection** — Track and resolve AI misconceptions about your brand
- **Competitive analysis** — Benchmark against competitors
- **Predictive velocity** — Track forward momentum

## Peterman Score

The Peterman Score is a composite 0-100 metric:

| Component | Weight |
|-----------|--------|
| LLM Share of Voice | 25% |
| Semantic Gravity | 20% |
| Technical Foundation | 15% |
| Content Survivability | 15% |
| Hallucination Debt | 10% |
| Competitive Position | 10% |
| Predictive Velocity | 5% |

**Score colours:** 0-40 (red), 40-65 (amber), 65-85 (gold), 85-100 (platinum)

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 16 + pgvector
- Redis 7

### Setup

```bash
# 1. Clone and install dependencies
pip install -r requirements.txt

# 2. Copy environment template
cp .env.example .env

# 3. Edit .env with your configuration
# Required: DB credentials, API keys

# 4. Start infrastructure
docker-compose up -d

# 5. Initialize database
python -m app.init_db

# 6. Run development server
python run.py
```

Peterman will be available at `http://localhost:5008`

### Production

```bash
# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5008 "app:create_app()"
```

## Architecture

Peterman uses an 11-chamber architecture for continuous improvement:

1. **Chamber 1 — Audit** — Technical baseline
2. **Chamber 2 — Analysis** — Gap identification
3. **Chamber 3 — Strategy** — Action planning
4. **Chamber 4 — Approval** — Human-in-the-loop
5. **Chamber 5 — Execution** — Implementation
6. **Chamber 6 — Deployment** — CMS integration
7. **Chamber 7 — Verification** — Quality assurance
8. **Chamber 8 — Reporting** — Stakeholder updates
9. **Chamber 9 — Probing** — LLM monitoring
10. **Chamber 10 — Detection** — Hallucination tracking
11. **Chamber 11 — Learning** — Continuous improvement

## Configuration

Environment variables (all prefixed with `AMTL_PTR_`):

| Variable | Description | Default |
|----------|-------------|---------|
| PORT | Server port | 5008 |
| DEBUG | Debug mode | false |
| DB_URL | PostgreSQL connection | postgresql://... |
| REDIS_URL | Redis connection | redis://... |
| OLLAMA_URL | Ollama via Supervisor | http://localhost:9000 |
| SEARXNG_URL | SearXNG instance | http://localhost:8888 |
| ELAINE_URL | ELAINE API | http://localhost:5000 |

## API

### Endpoints

- `GET /api/domains` — List all domains
- `POST /api/domains` — Create domain
- `GET /api/domains/<id>` — Get domain details
- `GET /api/domains/<id>/score` — Get Peterman Score
- `GET /api/health` — Health check

## Tech Stack

- **Backend:** Flask 3.0, SQLAlchemy 2.0, PostgreSQL, pgvector
- **Queue:** Redis + APScheduler
- **Frontend:** Vanilla JS SPA, AMTL Midnight theme
- **AI:** Ollama (via Supervisor), Claude Desktop, Manus, Perplexity

## License

Proprietary — Almost Magic Tech Lab

---

Built with 🦉 by Almost Magic Tech Lab
