# Peterman V4.1 — Infrastructure Setup Commands
# Windows 11 | RTX 5070 | 128GB RAM
# Run in PowerShell as Administrator

# ============================================================
# 1. POSTGRESQL 17 + PGVECTOR
# ============================================================

# Download and install PostgreSQL 17 from:
# https://www.postgresql.org/download/windows/
# During install: set password, keep port 5432, include pgAdmin 4

# After install, add PostgreSQL to PATH (adjust version if needed):
$env:Path += ";C:\Program Files\PostgreSQL\17\bin"
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Program Files\PostgreSQL\17\bin", "Machine")

# Verify PostgreSQL is running:
pg_isready

# Connect and configure for 128GB RAM:
psql -U postgres

# --- Run these SQL commands inside psql ---
# CREATE DATABASE peterman;
# CREATE DATABASE workshop;
# \c peterman
# CREATE EXTENSION IF NOT EXISTS vector;
# \q
# --- End SQL commands ---

# Optimise PostgreSQL for 128GB RAM
# Edit: C:\Program Files\PostgreSQL\17\data\postgresql.conf
# Change these settings:
#   shared_buffers = 8GB
#   effective_cache_size = 96GB
#   maintenance_work_mem = 2GB
#   work_mem = 256MB
#   max_worker_processes = 8
#   max_parallel_workers_per_gather = 4
#   max_parallel_workers = 8

# Restart PostgreSQL after config changes:
Restart-Service postgresql-x64-17


# ============================================================
# 2. SEARXNG (Self-Hosted Meta-Search Engine)
# Replaces: Google Search API, Bing API, NewsAPI ($300+/mo)
# ============================================================

# First, install Docker Desktop if not already installed:
# Download from: https://www.docker.com/products/docker-desktop/
# After install, restart your machine

# Verify Docker is running:
docker --version

# Create SearXNG directory:
mkdir C:\searxng
cd C:\searxng

# Create settings file:
@"
use_default_settings: true
server:
  secret_key: "peterman-searxng-$(Get-Random)"
  bind_address: "0.0.0.0"
  port: 8888
  limiter: false
search:
  safe_search: 0
  autocomplete: "google"
  default_lang: "en-AU"
  formats:
    - html
    - json
engines:
  - name: google
    engine: google
    shortcut: g
    disabled: false
  - name: bing
    engine: bing
    shortcut: b
    disabled: false
  - name: duckduckgo
    engine: duckduckgo
    shortcut: ddg
    disabled: false
  - name: google news
    engine: google_news
    shortcut: gn
    disabled: false
  - name: bing news
    engine: bing_news
    shortcut: bn
    disabled: false
  - name: reddit
    engine: reddit
    shortcut: r
    disabled: false
  - name: wikipedia
    engine: wikipedia
    shortcut: w
    disabled: false
  - name: google scholar
    engine: google_scholar
    shortcut: gs
    disabled: false
"@ | Out-File -FilePath C:\searxng\settings.yml -Encoding UTF8

# Run SearXNG container:
docker run -d `
  --name searxng `
  --restart always `
  -p 8888:8888 `
  -v C:\searxng\settings.yml:/etc/searxng/settings.yml `
  searxng/searxng:latest

# Verify SearXNG is running:
# Open browser: http://localhost:8888
# Test JSON API: http://localhost:8888/search?q=test&format=json

# SearXNG will now be available at:
#   Web UI:  http://localhost:8888
#   JSON API: http://localhost:8888/search?q={query}&format=json&categories={category}
#
# Categories: general, news, science, it, images
# Example API call from Peterman:
#   http://localhost:8888/search?q=AI+governance+Australia&format=json&categories=general


# ============================================================
# 3. PLAYWRIGHT + CRAWLEE (Web Crawling)
# Replaces: ScrapingBee, Diffbot, Screaming Frog ($350-$600/mo)
# ============================================================

# Install Node.js if not already installed:
# Download from: https://nodejs.org/ (LTS version)
# Verify:
node --version
npm --version

# Install Playwright globally:
npm install -g playwright
npx playwright install chromium

# Install Crawlee (we'll use this in the Peterman project):
# This will be done in the project directory when we build, but to test:
mkdir C:\peterman-test
cd C:\peterman-test
npm init -y
npm install crawlee playwright

# Test Playwright is working:
@"
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto('https://almostmagic.ai');
  const title = await page.title();
  console.log('Page title:', title);
  await browser.close();
  console.log('Playwright is working!');
})();
"@ | Out-File -FilePath C:\peterman-test\test-playwright.js -Encoding UTF8

node C:\peterman-test\test-playwright.js

# Install Trafilatura (Python content extraction):
pip install trafilatura

# Test Trafilatura:
python -c "import trafilatura; result = trafilatura.fetch_url('https://almostmagic.ai'); print('Trafilatura working!' if result else 'Check URL')"


# ============================================================
# 4. PYTHON PACKAGES FOR PETERMAN
# ============================================================

# Core packages:
pip install flask flask-cors flask-sqlalchemy
pip install psycopg2-binary
pip install pgvector
pip install sqlalchemy

# LLM integration:
pip install openai anthropic
pip install ollama
pip install tiktoken

# Web crawling & extraction:
pip install playwright trafilatura newspaper3k
pip install beautifulsoup4 lxml
pip install requests httpx

# Search & OSINT:
pip install pytrends
pip install python-whois
pip install feedparser

# Data processing:
pip install pandas numpy scikit-learn
pip install sentence-transformers

# Reporting:
pip install weasyprint python-docx
pip install jinja2 markdown

# Communication:
pip install slack-sdk

# Task scheduling:
pip install celery redis
pip install apscheduler


# ============================================================
# 5. REDIS (Task Queue for Background Scans)
# ============================================================

# Option A: Docker (recommended since you already have Docker for SearXNG):
docker run -d `
  --name redis `
  --restart always `
  -p 6379:6379 `
  redis:alpine

# Verify Redis:
docker exec redis redis-cli ping
# Should return: PONG


# ============================================================
# 6. VERIFY EVERYTHING IS RUNNING
# ============================================================

Write-Host "=== Peterman Infrastructure Check ===" -ForegroundColor Cyan

# Ollama
try {
    $ollamaResponse = Invoke-WebRequest -Uri "http://localhost:11434" -UseBasicParsing -ErrorAction Stop
    Write-Host "[OK] Ollama is running on port 11434" -ForegroundColor Green
} catch {
    Write-Host "[!!] Ollama is NOT running" -ForegroundColor Red
}

# Check Ollama models
Write-Host "`nOllama models installed:" -ForegroundColor Yellow
ollama list

# PostgreSQL
try {
    $pgResult = pg_isready 2>&1
    Write-Host "[OK] PostgreSQL is running on port 5432" -ForegroundColor Green
} catch {
    Write-Host "[!!] PostgreSQL is NOT running" -ForegroundColor Red
}

# SearXNG
try {
    $searxResponse = Invoke-WebRequest -Uri "http://localhost:8888" -UseBasicParsing -ErrorAction Stop
    Write-Host "[OK] SearXNG is running on port 8888" -ForegroundColor Green
} catch {
    Write-Host "[!!] SearXNG is NOT running" -ForegroundColor Red
}

# Redis
try {
    $redisResult = docker exec redis redis-cli ping 2>&1
    if ($redisResult -eq "PONG") {
        Write-Host "[OK] Redis is running on port 6379" -ForegroundColor Green
    }
} catch {
    Write-Host "[!!] Redis is NOT running" -ForegroundColor Red
}

# Docker
try {
    docker --version | Out-Null
    Write-Host "[OK] Docker is installed" -ForegroundColor Green
} catch {
    Write-Host "[!!] Docker is NOT installed" -ForegroundColor Red
}

# Node.js
try {
    node --version | Out-Null
    Write-Host "[OK] Node.js is installed" -ForegroundColor Green
} catch {
    Write-Host "[!!] Node.js is NOT installed" -ForegroundColor Red
}

# Python
try {
    python --version | Out-Null
    Write-Host "[OK] Python is installed" -ForegroundColor Green
} catch {
    Write-Host "[!!] Python is NOT installed" -ForegroundColor Red
}

Write-Host "`n=== Port Map ===" -ForegroundColor Cyan
Write-Host "Ollama:      http://localhost:11434"
Write-Host "PostgreSQL:  localhost:5432"
Write-Host "SearXNG:     http://localhost:8888"
Write-Host "Redis:       localhost:6379"
Write-Host "Peterman:    http://localhost:5008 (when built)"
Write-Host "Elaine:      http://localhost:5000 (when built)"

Write-Host "`n=== Monthly Cost ===" -ForegroundColor Cyan
Write-Host "OpenAI API:    ~$30-150/mo (9 quality-critical endpoints only)"
Write-Host "Claude API:    ~$20-80/mo (cross-model verification)"
Write-Host "Perplexity:    ~$30-100/mo (brand-specific citation tracking)"
Write-Host "Snitcher:      $39/mo (IP-to-company, add later)"
Write-Host "Electricity:   ~$20-40/mo (GPU inference)"
Write-Host "EVERYTHING ELSE: $0 (your hardware + open source)"
Write-Host "TOTAL:         ~$139-409/mo" -ForegroundColor Green
