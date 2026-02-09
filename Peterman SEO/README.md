# Peterman V4.1 — The Authority & Presence Engine

**Almost Magic Tech Lab Pty Ltd**

10-chamber AI-powered brand authority monitoring. Tracks how brands are perceived across LLMs, detects hallucinations, measures Share of Voice, and analyses trust class positioning.

## Quick Start

```powershell
# Install dependencies
pip install -r requirements.txt

# Start Peterman (port 5008)
python app.py
```

Dashboard: http://localhost:5008
API docs: http://localhost:5008/api/health

## The 10 Chambers

1. **Perception Scan** — How LLMs perceive your brand (implemented)
2. **Semantic Core** — Fingerprinting and drift detection
3. **Neural Vector Map** — Embedding-based positioning
4. **Authority Engine** — SERP analysis via SearXNG
5. **Survivability Lab** — Content preservation testing
6. **Machine Interface** — Technical audits (JSON-LD, schema)
7. **Amplifier** — Citation probability, competitor shadow
8. **The Proof** — GA4 + Snitcher visitor intelligence
9. **The Oracle** — Predictive scanning and trends
10. **The Forge** — Content production pipeline

## Key Features

- Multi-LLM perception scanning (Ollama local + browser automation for ChatGPT, Claude, Perplexity, Gemini)
- Hallucination detection with inertia tracking
- Share of Voice measurement and velocity tracking
- Trust class analysis (authority | reference | passing | absent)
- Self-hosted search via SearXNG (zero API cost)
- Vector embeddings via pgvector (768-dim, nomic-embed-text)
- Visitor intelligence via Snitcher ($39/mo)
- AMTL design system: Sora font, Midnight #0A0E14, Gold #C9944A, dark-mode native

## Tests

```powershell
python tests/beast_tests.py    # Structure, security, code quality
pytest tests/test_app.py -v    # API integration tests (needs PostgreSQL)
```

## Tech Stack

Python/Flask backend, PostgreSQL + pgvector, Ollama (local LLMs), SearXNG (self-hosted search), Redis (task queue), Playwright (browser automation).

## Design System

Almost Magic Tech Lab: Sora font, Midnight #0A0E14, Gold #C9944A accent, dark-mode native.

## Licence

Proprietary — Almost Magic Tech Lab Pty Ltd.
