# The Supervisor v1.0

Centralised runtime manager for Almost Magic Tech Lab. All apps talk to The Supervisor, not directly to Ollama.

## Quick Start

```bash
pip install -r requirements.txt
python supervisor.py
```

The Supervisor starts on port 9000.

## What It Does

1. **GPU Scheduler** — Tracks VRAM (12GB RTX 5070), prevents conflicts, manages model loading/unloading
2. **Model Registry** — Single YAML config (`config/models.yaml`), no hardcoded model names
3. **Service Graph** — Dependency ordering, health checks, startup/shutdown management
4. **LLM Router** — Ollama first, cloud API fallback (Anthropic/OpenAI) when local fails
5. **Health Guardian** — 30-second health checks, auto-restart (3 retries), alerting
6. **Boot Sequencer** — Phased startup: Docker → Ollama → Supervisor → Workshop → ELAINE

## API

### Management
- `GET /api/health` — Supervisor health
- `GET /api/status` — Full system status
- `GET /api/models` — Model registry
- `GET /api/gpu` — VRAM stats
- `GET /api/services` — All service health
- `POST /api/services/<id>/start` — Start a service
- `POST /api/services/<id>/restart` — Restart a service
- `GET /api/metrics` — Request metrics
- `GET /api/cloud/costs` — Cloud API costs

### Ollama Proxy (transparent drop-in)
- `POST /api/chat` — Chat completion
- `POST /api/generate` — Text generation
- `POST /api/embed` — Embeddings
- `GET /api/tags` — List models

Apps set `OLLAMA_URL=http://localhost:9000` and everything works.

## Boot

```powershell
powershell -ExecutionPolicy Bypass -File boot.ps1
```

## Tests

```bash
python tests/test_supervisor.py
```

## Config

- `config/models.yaml` — Model VRAM budgets, aliases, cloud fallback
- `config/services.yaml` — Service dependency graph, boot phases

---

*"The Supervisor is the backbone. Every AI request routes through it."*
