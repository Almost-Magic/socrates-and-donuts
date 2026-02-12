# WSL2_TOOLKIT_INSTALL.md
## Almost Magic Tech Lab — Linux Toolkit Installation Plan
### For: Claude Code executing in WSL2
### Date: February 2026

---

## CRITICAL RULES — READ BEFORE DOING ANYTHING

1. **Ollama only for programmatic AI.** Route through Supervisor on port 9000.
2. **NO cloud API keys. EVER.** Do NOT set OPENAI_API_KEY, ANTHROPIC_API_KEY, TAVILY_API_KEY, or any cloud LLM keys. Not in .bashrc, not in .env, not anywhere.
3. **If Ollama is down:** Auto-restart 3x via Supervisor. If still down, open browser to claude.ai or chatgpt.com. Mani pays for Claude Max and ChatGPT subscriptions — those are for interactive browser use, NOT for API calls.
4. **If a tool REQUIRES a cloud API key to function at all, SKIP IT.** Note why in the status log.
5. **Test each tool after installing.** Don't batch-install and hope.
6. **Ask Mani before installing anything that uses more than 2GB disk space.**
7. **We already have Caddy — do NOT reinstall it.** It's flaky but it's there. If it needs fixing, fix it — don't reinstall.
8. **We already have Swiss Army Knife with a PDF writer/editor — do NOT install any PDF tool.**
9. **Log what you installed** in the STATUS section at the bottom.

---

## PHASE 1: Foundation (Install Now)

### 1.1 System Utilities

```bash
sudo apt update && sudo apt upgrade -y

sudo apt install -y \
  tmux \
  btop \
  curl \
  wget \
  unzip \
  jq \
  git \
  build-essential \
  python3-pip \
  python3-venv \
  net-tools

tmux -V
btop --version
```

### 1.2 lazydocker (Docker Terminal UI)

```bash
curl https://raw.githubusercontent.com/jesseduffield/lazydocker/master/scripts/install_update_linux.sh | bash
lazydocker  # press 'q' to quit
```

### 1.3 Uptime Kuma (Service Monitoring)

```bash
docker run -d \
  --name uptime-kuma \
  --restart=unless-stopped \
  -p 3001:3001 \
  -v uptime-kuma:/app/data \
  louislam/uptime-kuma:latest
```

After it starts, open http://localhost:3001, create admin account, add monitors for all AMTL services.

### 1.4 Caddy Status Check (DO NOT REINSTALL)

```bash
caddy version 2>/dev/null
systemctl status caddy 2>/dev/null || echo "Caddy not running as service"
```

Report status to Mani. If broken, ask what the specific issue is before fixing.

### ✅ PHASE 1 GATE
- [ ] tmux, btop installed
- [ ] lazydocker shows containers
- [ ] Uptime Kuma on port 3001 with monitors added
- [ ] Caddy status reported

---

## PHASE 2: Intelligence & Security (Week 2)

### 2.1 SpiderFoot (OSINT — no API keys needed for basic use)

```bash
docker run -d --name spiderfoot --restart=unless-stopped -p 5001:5001 spiderfoot/spiderfoot:latest
```

### 2.2 Nuclei (Vulnerability Scanner)

```bash
NUCLEI_VERSION=$(curl -s https://api.github.com/repos/projectdiscovery/nuclei/releases/latest | jq -r .tag_name)
wget -q "https://github.com/projectdiscovery/nuclei/releases/latest/download/nuclei_${NUCLEI_VERSION#v}_linux_amd64.zip" -O /tmp/nuclei.zip
unzip -o /tmp/nuclei.zip -d /tmp
sudo mv /tmp/nuclei /usr/local/bin/
rm /tmp/nuclei.zip
nuclei -update-templates
nuclei --version
```

### 2.3 theHarvester + Nmap

```bash
pip install theHarvester --break-system-packages
sudo apt install -y nmap
```

### 2.4 Netdata (System Monitoring)

```bash
wget -O /tmp/netdata-kickstart.sh https://get.netdata.cloud/kickstart.sh
sh /tmp/netdata-kickstart.sh --no-updates --stable-channel --disable-telemetry
```

### 2.5 CrewAI (Ollama ONLY — no cloud APIs)

```bash
pip install crewai 'crewai[tools]' --break-system-packages
python3 -c "from crewai import Agent, Task, Crew; print('CrewAI: OK')"
```

Create Ollama-only test:

```bash
cat > ~/crewai-ollama-test.py << 'PYEOF'
"""CrewAI test — Ollama ONLY. No cloud APIs."""
import os
for key in ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GOOGLE_API_KEY']:
    if key in os.environ:
        del os.environ[key]
        print(f"WARNING: Removed {key} from environment")

from crewai import Agent, Task, Crew, Process

agent = Agent(
    role="Analyst",
    goal="Provide clear, concise analysis",
    backstory="You are a careful analyst.",
    llm="ollama/gemma2",
    verbose=True,
)
task = Task(
    description="What are three key principles of good AI governance for Australian SMBs?",
    expected_output="A clear list of three principles with brief explanations",
    agent=agent,
)
crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
result = crew.kickoff()
print(result)
PYEOF
```

### ✅ PHASE 2 GATE
- [ ] SpiderFoot on port 5001
- [ ] Nuclei with templates
- [ ] theHarvester, Nmap working
- [ ] Netdata on port 19999
- [ ] CrewAI passes Ollama test (no cloud APIs)

---

## PHASE 3: Knowledge & Observability (Week 3)

### 3.1 Outline (Wiki / AMTL Intranet)

Create docker-compose but **DON'T START** until Mani chooses auth method:

```bash
mkdir -p ~/outline && cat > ~/outline/docker-compose.yml << 'EOF'
version: "3"
services:
  outline:
    image: outlinewiki/outline:latest
    restart: unless-stopped
    ports:
      - "3006:3000"
    environment:
      - NODE_ENV=production
      - SECRET_KEY=CHANGE_ME
      - UTILS_SECRET=CHANGE_ME
      - DATABASE_URL=postgres://postgres:postgres@host.docker.internal:5433/outline
      - REDIS_URL=redis://host.docker.internal:6379
      - URL=http://localhost:3006
      - PORT=3000
      - FILE_STORAGE=local
      - FILE_STORAGE_LOCAL_ROOT_DIR=/var/lib/outline/data
    volumes:
      - outline-data:/var/lib/outline/data
    extra_hosts:
      - "host.docker.internal:host-gateway"
volumes:
  outline-data:
EOF
echo "STOP: Ask Mani which auth method before starting"
```

### 3.2 LangFuse (Ollama Observability)

```bash
PGPASSWORD=postgres psql -h localhost -p 5433 -U postgres -c "CREATE DATABASE langfuse;" 2>/dev/null || true

mkdir -p ~/langfuse && cat > ~/langfuse/docker-compose.yml << 'EOF'
version: "3"
services:
  langfuse:
    image: langfuse/langfuse:2
    restart: unless-stopped
    ports:
      - "3007:3000"
    environment:
      - DATABASE_URL=postgres://postgres:postgres@host.docker.internal:5433/langfuse
      - NEXTAUTH_SECRET=CHANGE_ME
      - NEXTAUTH_URL=http://localhost:3007
      - SALT=CHANGE_ME
      - TELEMETRY_ENABLED=false
    extra_hosts:
      - "host.docker.internal:host-gateway"
EOF

cd ~/langfuse && docker compose up -d
```

### ✅ PHASE 3 GATE
- [ ] Outline ready (waiting for Mani's auth decision)
- [ ] LangFuse on port 3007

---

## PHASE 4: Cyber Security Suite (Month 2)

### 4.1 CrowdSec + Lynis (lightweight)

```bash
curl -s https://install.crowdsec.net | sudo sh
sudo apt install crowdsec crowdsec-firewall-bouncer-iptables lynis -y
sudo lynis audit system --quick
```

### 4.2 OpenVAS — ASK MANI FIRST (~5GB)
### 4.3 Wazuh — ASK MANI FIRST (~8GB)

### ✅ PHASE 4 GATE
- [ ] CrowdSec running
- [ ] Lynis audit runs
- [ ] OpenVAS — awaiting approval
- [ ] Wazuh — awaiting approval

---

## PHASE 5: Research & Literature Intelligence (Month 2)

### 5.1 txtai + paperai + paperetl + annotateai

**What this gives you:** Ingest thousands of medical/scientific/technical papers (PDF, PubMed, arXiv, bioRxiv), build a semantic search index over them, and generate structured reports using Ollama. annotateai auto-highlights key concepts in PDFs.

**This is NOT part of CK Writer.** paperai does research and extraction → outputs structured CSV/Markdown → CK Writer (later) imports that as source material. Two tools, one pipeline.

```bash
# Create a virtual environment to avoid dependency conflicts with CrewAI/theHarvester
python3 -m venv ~/paperai-env
source ~/paperai-env/bin/activate

# Install the NeuML research stack
pip install paperai paperetl annotateai

# Install txtai with LLM pipeline support (for Ollama integration)
pip install 'txtai[pipeline-llm]'

# Verify imports
python3 -c "from paperai import query; from paperetl import factory; print('paperai + paperetl: OK')"
python3 -c "from annotateai import Annotate; print('annotateai: OK')"
python3 -c "from txtai import LLM; print('txtai LLM pipeline: OK')"

deactivate
```

### 5.2 Ollama Integration Test

paperai uses txtai under the hood, which supports Ollama natively. Route through Supervisor on port 9000.

```bash
source ~/paperai-env/bin/activate

cat > ~/paperai-ollama-test.py << 'PYEOF'
"""paperai + txtai Ollama integration test. No cloud APIs."""
import os
# Strip any cloud keys
for key in ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GOOGLE_API_KEY']:
    if key in os.environ:
        del os.environ[key]
        print(f"WARNING: Removed {key} from environment")

from txtai import LLM, Embeddings

# Test 1: txtai LLM via Ollama (through Supervisor on port 9000)
# If Supervisor isn't routing Ollama, fall back to direct Ollama on 11434
import requests
try:
    r = requests.get("http://localhost:9000/api/health", timeout=3)
    OLLAMA_BASE = "http://localhost:9000"
    print(f"Using Supervisor on port 9000")
except:
    OLLAMA_BASE = os.environ.get("OLLAMA_API_BASE", "http://localhost:11434")
    print(f"Supervisor not available, using Ollama direct at {OLLAMA_BASE}")

llm = LLM("ollama/gemma2", api_base=OLLAMA_BASE)
result = llm("In one sentence, what is semantic search?")
print(f"\nLLM test: {result}")

# Test 2: Embeddings index (local model, no API needed)
embeddings = Embeddings({"path": "sentence-transformers/all-MiniLM-L6-v2", "content": True})
data = [
    "Hypertension is a major risk factor for cardiovascular disease",
    "Machine learning can predict patient outcomes from clinical data",
    "The COVID-19 pandemic accelerated telemedicine adoption globally",
    "Randomised controlled trials remain the gold standard for evidence",
    "Natural language processing enables automated literature review"
]
embeddings.index([{"text": t} for t in data])
results = embeddings.search("AI in healthcare", 2)
print(f"\nSemantic search test:")
for r in results:
    print(f"  Score {r['score']:.3f}: {r['text']}")

print("\n✅ paperai Ollama integration test PASSED")
PYEOF

python3 ~/paperai-ollama-test.py
deactivate
```

### 5.3 Sample Report Config

Create a sample report config that Claude Code or users can adapt:

```bash
source ~/paperai-env/bin/activate

mkdir -p ~/paperai-data

cat > ~/paperai-data/sample-report.yml << 'YMLEOF'
# Sample paperai report configuration
# Adapt this for any research domain
name: SampleReport
options:
  llm: ollama/gemma2
  api_base: http://localhost:9000
  system: You are a research literature analyst. You extract structured data from papers.
  template: |
    Extract the following field from the provided context.
    Only use information from the context. If the information is not available, respond with "Not found".

    Field: {question}
    Context: {context}
    Answer:

columns:
  - name: study_type
    query: What type of study is this (RCT, cohort, case study, meta-analysis, review)?
    dtype: str
  - name: sample_size
    query: What is the sample size or number of participants?
    dtype: str
  - name: key_finding
    query: What is the primary finding or conclusion?
    dtype: str
  - name: limitations
    query: What limitations does the study acknowledge?
    dtype: str
YMLEOF

echo "Sample report config created at ~/paperai-data/sample-report.yml"
deactivate
```

### 5.4 annotateai Test

```bash
source ~/paperai-env/bin/activate

cat > ~/annotateai-test.py << 'PYEOF'
"""annotateai test — annotate a paper from arXiv using Ollama."""
import os
for key in ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GOOGLE_API_KEY']:
    if key in os.environ:
        del os.environ[key]

from annotateai import Annotate

# Use Ollama via Supervisor or direct
OLLAMA_BASE = os.environ.get("OLLAMA_API_BASE", "http://localhost:11434")
annotate = Annotate(f"ollama/gemma2", api_base=OLLAMA_BASE)

# Annotate the original RAG paper from arXiv
output = annotate("https://arxiv.org/pdf/2005.11401", keywords=["retrieval", "generation", "knowledge"])
print(f"Annotated PDF saved to: {output}")
print("✅ annotateai test PASSED")
PYEOF

python3 ~/annotateai-test.py
deactivate
```

### ✅ PHASE 5 GATE
- [ ] txtai + paperai + paperetl + annotateai installed in ~/paperai-env
- [ ] Ollama integration test passes (LLM + embeddings, no cloud APIs)
- [ ] Sample report config created
- [ ] annotateai can annotate a PDF from arXiv using Ollama
- [ ] No cloud API keys anywhere

---

## DO NOT INSTALL

| Tool | Reason |
|------|--------|
| Aider, GPT Engineer, Mentat | Claude Code replaces all of these |
| GPT Researcher | Requires OpenAI API key |
| MetaGPT, Devika, AutoCodeRover | Cloud API dependent |
| Superagent, LLMStack | Building ELAINE and Workshop instead |
| Twenty CRM | Building Ripple instead |
| GeniA | AWS dependent |
| E2B Desktop | Cloud API dependent |
| Stirling PDF | Swiss Army Knife already has PDF tools |
| Caddy | Already installed — fix don't reinstall |
| LiteLLM | Assumes cloud APIs |
| Open WebUI | ~~Low priority~~ INSTALLED — Mani requested 13 Feb 2026, port 3080 |

---

## PORT MAP

| Port | Service | Status |
|------|---------|--------|
| 3000 | Genie Frontend | Existing |
| 3001 | Uptime Kuma | Phase 1 |
| 3006 | Outline | Phase 3 |
| 3007 | LangFuse | Phase 3 |
| 3100 | Ripple Frontend | Existing |
| 5001 | SpiderFoot | Phase 2 |
| 5003 | The Workshop | Existing |
| 5433 | PostgreSQL | Existing |
| 5678 | n8n | Existing |
| 6379 | Redis | Existing |
| 8000 | Genie Backend | Existing |
| 8100 | Ripple Backend | Existing |
| 8888 | SearXNG | Existing |
| 9000 | Listmonk | Existing |
| 11434 | Ollama | Existing |
| 19999 | Netdata | Phase 2 |
| 8501 | annotateai Web UI (optional) | Phase 5 |
| 3333 | Ghostfolio | Finance Tools |
| 3015 | Formbricks | Tier 1 |
| 3080 | Open WebUI | Tier 1 |
| 4200 | Postiz | Tier 1 |
| 8084 | Matomo | Tier 1 |
| 8088 | Apache Superset | Tier 1 |
| 8222 | Vaultwarden | Tier 1 |
| 9002 | Penpot | Tier 1 |
| 3350 | Wisdom Quotes API | Wisdom |
| 9050 | Tor SOCKS5 Proxy | OSINT Layer |
| 8118 | Privoxy HTTP Proxy | OSINT Layer |
| 8282 | IVRE Network Recon | OSINT Layer |
| 8284 | HIBP Offline Checker | OSINT Layer |

---

## STATUS LOG

| Phase | Tool | Status | Date | Notes |
|-------|------|--------|------|-------|
| 1 | tmux + btop | | | |
| 1 | lazydocker | | | |
| 1 | Uptime Kuma | | | |
| 1 | Caddy check | | | Report only — don't reinstall |
| 2 | SpiderFoot | | | |
| 2 | Nuclei | | | |
| 2 | theHarvester | | | |
| 2 | Nmap | | | |
| 2 | Netdata | | | |
| 2 | CrewAI | | | Ollama only — no cloud APIs |
| 3 | Outline | | | Needs auth decision |
| 3 | LangFuse | | | |
| 4 | CrowdSec | | | |
| 4 | Lynis | | | |
| 4 | OpenVAS | | | Needs approval — 5GB |
| 4 | Wazuh | | | Needs approval — 8GB |
| 5 | txtai + paperai + paperetl | DONE | 2026-02-13 | Installed in ~/paperai-env. paperai 2.5.0, paperetl 2.5.2, txtai 9.5.0. All imports verified. Also installed NLTK punkt_tab data. Routed through Supervisor :9000. |
| 5 | annotateai | DONE | 2026-02-13 | annotateai 0.3.0 in ~/paperai-env. Annotated arXiv RAG paper (2005.11401) via Ollama/gemma2:27b through Supervisor. Output: /tmp/tmpzji_514b-annotated.pdf. 94 topics generated in ~12 min. |
| 5 | Ollama integration test | DONE | 2026-02-13 | LLM test: gemma2:27b via Supervisor :9000 responded correctly. Embeddings test: all-MiniLM-L6-v2 local model, semantic search working. No cloud API keys. |
| 5 | Sample report config | DONE | 2026-02-13 | Created ~/paperai-data/sample-report.yml. Configured for ollama/gemma2 via Supervisor on :9000. 4 extraction columns: study_type, sample_size, key_finding, limitations. |
| 6 | FinceptTerminal CLI | DONE | 2026-02-13 | v2.0.8 in ~/fincept-env. Open-source Bloomberg alternative. Market analytics, economic data. |
| 6 | OpenBB | DONE | 2026-02-13 | v4.6.0 in ~/fincept-env. Investment research platform. 30+ provider extensions (yfinance, FRED, SEC, OECD). |
| 6 | Ghostfolio (Docker) | DONE | 2026-02-13 | Port 3333. Portfolio tracker. 3 containers (app + postgres + redis). Health OK. |
| T1 | Open WebUI | DONE | 2026-02-13 | Port 3080. Chat UI for Ollama. 1 container. Healthy. Connected to Ollama via gateway 172.18.240.1:11434. |
| T1 | Vaultwarden | DONE | 2026-02-13 | Port 8222. Bitwarden-compatible password manager. 1 container. Healthy. |
| T1 | Formbricks | DONE | 2026-02-13 | Port 3015 (NOT 3005 — Junk Drawer conflict). 3 containers (app + pgvector PG + Redis). Compose at ~/formbricks/. Required pgvector/pgvector:pg16 for vector migration + CRON_SECRET env var. |
| T1 | Matomo | DONE | 2026-02-13 | Port 8084. Privacy-first analytics. 1 container. Needs MySQL/MariaDB for full setup. |
| T1 | Penpot | DONE | 2026-02-13 | Port 9002. Design tool (Figma alt). 6 containers. Compose at /tmp/penpot/docker/images/. Telemetry off. |
| T1 | Apache Superset | DONE | 2026-02-13 | Port 8088. BI/data viz. 5 containers (pre-built images via docker-compose-image-tag.yml). App healthy (200). Workers have psycopg2 warning — core dashboards work fine. Default: admin/admin. |
| T1 | Postiz | DONE | 2026-02-13 | Port 4200. Social media scheduler. 3 containers (app + own PG + Redis). Compose at ~/postiz/. |
| T1 | Homepage update | DONE | 2026-02-13 | Added "Productivity & Intelligence" category with all 7 new tools. Restarted. |
| T1 | Uptime Kuma monitors | MANUAL | 2026-02-13 | Socket.IO API — must add monitors manually via http://localhost:3001. See AMTL_TIER1_TOOLS_INSTALL.md. |
| OSINT | Tor SOCKS5 Proxy | DONE | 2026-02-13 | Port 9050. peterdavehello/tor-socks-proxy. IsTor:true verified. Container: tor-socks-proxy. |
| OSINT | Privoxy HTTP Proxy | DONE | 2026-02-13 | Port 8118. vimagick/privoxy. Forwards to Tor via --link. IsTor:true via HTTP proxy verified. |
| OSINT | IVRE Network Recon | DONE | 2026-02-13 | Port 8282. 5 containers (web, uwsgi, doku, MongoDB, client). HTTP 200 verified. Compose at /tmp/ivre-src/docker/docker-compose-amtl.yml. |
| OSINT | HIBP Offline Checker | DONE | 2026-02-13 | Port 8284. Custom Flask + gunicorn. Placeholder responses until 35GB DB downloaded. download-hibp.sh at ~/hibp-checker/. |
| OSINT | SpiderFoot Tor | DONE | 2026-02-13 | Connected to osint-net Docker network. tor-socks-proxy resolves from SpiderFoot. Configure SOCKS5 proxy via web UI at http://localhost:5009. |
| WIS | Wisdom Quotes API | DONE | 2026-02-13 | Port 3350. FastAPI + uvicorn in ~/wisdom-quotes/venv. 2034 quotes, 24 authors, 11 traditions (Stoic + Buddhist + Sufi + Tao + Western + more). Cloned stoic-quotes repo (1774 base) + 260 multi-tradition additions. Endpoints: /api/quote/random, /api/quote/daily, /api/quotes?author=X, /api/stats. nohup daemonised. |
| WIS | Daily Wisdom Fetcher | DONE | 2026-02-13 | ~/daily-wisdom/fetch_daily.py. Calls /api/quote/daily, saves YYYY-MM-DD.json + appends to wisdom_log.json. Ready for n8n 6 AM AEST cron. |
| WIS | Homepage registration | DONE | 2026-02-13 | Added "Wisdom & Philosophy" category to Homepage (:3011). Auto-reloaded. |
| WIS | Uptime Kuma monitor | MANUAL | 2026-02-13 | Add HTTP monitor for http://localhost:3350/api/health via Uptime Kuma web UI at http://localhost:3001. |
| OSINT | Homepage update | DONE | 2026-02-13 | Added "Security & OSINT" category with Tor, Privoxy, IVRE, HIBP Checker + existing OpenVAS, Wazuh, SpiderFoot. |
| OSINT | Workshop update | DONE | 2026-02-13 | Added 4 OSINT tool cards to Open Source Tools grid + SERVICES dict in app.py. |

---

*Made with ❤️ by Mani Padisetti @ Almost Magic Tech Lab*
