# ELAINE — AI Chief of Staff

> Almost Magic Tech Lab | AMTL-ELA-BLD-1.0

ELAINE is the AI Chief of Staff for Almost Magic Tech Lab. She manages morning briefings, ecosystem health, quality gates, voice interaction, and strategic prioritisation for Mani Padisetti.

## Quick Start

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your settings

# 4. Run ELAINE
python run.py
```

ELAINE runs on **port 5000** (sacred — never change).

## Architecture

- **Backend:** Flask 3.0.2 with `threaded=True`
- **AI Engine:** Claude CLI (primary) → Ollama via Supervisor :9000 (fallback)
- **Voice:** ElevenLabs → Kokoro-82M → pyttsx3 (fallback chain)
- **Database:** SQLite
- **Desktop:** Electron wrapper (connects to Flask :5000)

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | System health check |
| `/api/chat` | POST | Chat with ELAINE |
| `/api/voice/speak` | POST | Text-to-speech |
| `/api/voice/status` | GET | Voice engine status |
| `/api/briefing/morning` | GET/POST | Morning briefing |
| `/api/gatekeeper/check` | POST | Content gate check |
| `/api/sentinel/review` | POST | Quality gate review |
| `/api/gravity/priorities` | GET | Priority field |
| `/api/ecosystem/status` | GET | Ecosystem health |
| `/api/thinking/analyse` | POST | Costanza frameworks |
| `/` | GET | Dashboard |

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test type
pytest tests/beast/ -v      # Beast tests (core functionality)
pytest tests/smoke/ -v      # Smoke tests (startup verification)
pytest tests/four_percent/  # Edge case tests
pytest tests/integration/   # Cross-service tests

# Linting
flake8 app/ --max-line-length=120
```

## Non-Negotiable Rules

- **Port 5000** — sacred, never change
- **`threaded=True`** on Flask — critical for concurrent requests
- **No cloud API fallback** — never call Anthropic/OpenAI APIs directly
- **All AI via `ai_engine.py`** — no module calls Claude/Ollama directly
- **ElevenLabs voice_id `XQanfahzbl1YiUlZi5NW`** — hardcoded, NEVER change
- **Australian English** everywhere (colour, organisation, honour)

## Licence

Copyright 2026 Almost Magic Tech Lab. All rights reserved.
