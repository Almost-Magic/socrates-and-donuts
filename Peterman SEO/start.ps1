# Peterman V4.1 — Local Setup
# Run in PowerShell from the peterman directory

# Install dependencies
pip install flask flask-cors flask-sqlalchemy psycopg2-binary pgvector sqlalchemy python-dotenv httpx pytest --break-system-packages

# Verify infrastructure
Write-Host "Checking infrastructure..." -ForegroundColor Cyan

# Ollama
try { (Invoke-WebRequest -Uri "http://localhost:11434" -UseBasicParsing -ErrorAction Stop).StatusCode | Out-Null; Write-Host "[OK] Ollama" -ForegroundColor Green } catch { Write-Host "[!!] Ollama not running" -ForegroundColor Red }

# PostgreSQL
try { docker exec pgvector pg_isready -U postgres 2>&1 | Out-Null; Write-Host "[OK] PostgreSQL+pgvector" -ForegroundColor Green } catch { Write-Host "[!!] pgvector not running" -ForegroundColor Red }

# SearXNG
try { (Invoke-WebRequest -Uri "http://localhost:8888" -UseBasicParsing -ErrorAction Stop).StatusCode | Out-Null; Write-Host "[OK] SearXNG" -ForegroundColor Green } catch { Write-Host "[!!] SearXNG not running" -ForegroundColor Red }

# Redis
try { docker exec redis redis-cli ping 2>&1 | Out-Null; Write-Host "[OK] Redis" -ForegroundColor Green } catch { Write-Host "[!!] Redis not running" -ForegroundColor Red }

Write-Host "`nStarting Peterman..." -ForegroundColor Cyan
python app.py
