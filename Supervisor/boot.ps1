# The Supervisor — Boot Sequencer
# Almost Magic Tech Lab — February 2026
#
# Run on login via Task Scheduler or manually:
#   powershell -ExecutionPolicy Bypass -File boot.ps1
#
# Phase 1: Docker + Ollama + preload models
# Phase 2: Supervisor + Workshop + ELAINE
# Phase 3: On-demand apps (started by ELAINE when needed)

$ErrorActionPreference = "Continue"
$SourceBase = Split-Path -Parent $PSScriptRoot
if (-not $SourceBase) { $SourceBase = "C:\Users\ManiPadisetti\Dropbox\Desktop DB\Books and Articles Mani\Books\Almost Magic Tech Lab AMTL\Source and Brand" }
$SupervisorDir = Join-Path $SourceBase "Supervisor"
$LogFile = Join-Path $SupervisorDir "logs\boot.log"

function Log($msg) {
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "$ts | $msg"
    Write-Host $line
    Add-Content -Path $LogFile -Value $line -Encoding UTF8
}

function Wait-ForPort($port, $timeout = 60, $name = "service") {
    $start = Get-Date
    while (((Get-Date) - $start).TotalSeconds -lt $timeout) {
        try {
            $tcp = New-Object System.Net.Sockets.TcpClient
            $tcp.Connect("localhost", $port)
            $tcp.Close()
            Log "  [OK] $name responding on port $port"
            return $true
        } catch {
            Start-Sleep -Seconds 2
        }
    }
    Log "  [FAIL] $name did not respond on port $port within ${timeout}s"
    return $false
}

function Wait-ForHttp($url, $timeout = 60, $name = "service") {
    $start = Get-Date
    while (((Get-Date) - $start).TotalSeconds -lt $timeout) {
        try {
            $resp = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
            if ($resp.StatusCode -lt 500) {
                Log "  [OK] $name responding at $url"
                return $true
            }
        } catch {
            Start-Sleep -Seconds 2
        }
    }
    Log "  [FAIL] $name did not respond at $url within ${timeout}s"
    return $false
}

# ── SET ENVIRONMENT ──────────────────────────────────────────────────────
# Point all apps to The Supervisor instead of Ollama directly
$env:OLLAMA_URL = "http://localhost:9000"
$env:OLLAMA_BASE_URL = "http://localhost:9000"

Log "=============================================="
Log "  AMTL BOOT SEQUENCE"
Log "=============================================="
$bootStart = Get-Date

# ── PHASE 1: Infrastructure ─────────────────────────────────────────────
Log ""
Log "Phase 1: Infrastructure"
Log "----------------------------------------------"

# Check Ollama
$ollamaRunning = Wait-ForPort -port 11434 -timeout 5 -name "Ollama"
if (-not $ollamaRunning) {
    Log "  Starting Ollama..."
    Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
    $ollamaRunning = Wait-ForPort -port 11434 -timeout 60 -name "Ollama"
}

if ($ollamaRunning) {
    # Preload default models
    Log "  Preloading nomic-embed-text..."
    try {
        $body = '{"model":"nomic-embed-text","prompt":"","keep_alive":"24h"}'
        Invoke-RestMethod -Uri "http://localhost:11434/api/generate" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 120 | Out-Null
        Log "  [OK] nomic-embed-text loaded"
    } catch { Log "  [WARN] Failed to preload nomic-embed-text: $_" }

    Log "  Preloading gemma2:27b..."
    try {
        $body = '{"model":"gemma2:27b","prompt":"","keep_alive":"24h"}'
        Invoke-RestMethod -Uri "http://localhost:11434/api/generate" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 120 | Out-Null
        Log "  [OK] gemma2:27b loaded"
    } catch { Log "  [WARN] Failed to preload gemma2:27b: $_" }
}

# Check Docker services (don't start them — Docker manages that)
Log "  Checking Docker services..."
Wait-ForPort -port 5433 -timeout 5 -name "PostgreSQL" | Out-Null
Wait-ForPort -port 6379 -timeout 5 -name "Redis" | Out-Null
Wait-ForPort -port 5678 -timeout 5 -name "n8n" | Out-Null

# ── PHASE 2: Core Services ──────────────────────────────────────────────
Log ""
Log "Phase 2: Core Services"
Log "----------------------------------------------"

# Start The Supervisor
$supervisorRunning = Wait-ForPort -port 9000 -timeout 3 -name "Supervisor"
if (-not $supervisorRunning) {
    Log "  Starting The Supervisor..."
    Start-Process -FilePath "python" -ArgumentList "supervisor.py" -WorkingDirectory $SupervisorDir -WindowStyle Hidden
    $supervisorRunning = Wait-ForHttp -url "http://localhost:9000/api/health" -timeout 30 -name "Supervisor"
}

# Start Workshop
$workshopRunning = Wait-ForPort -port 5003 -timeout 3 -name "Workshop"
if (-not $workshopRunning) {
    Log "  Starting The Workshop..."
    $workshopDir = Join-Path $SourceBase "CK\workshop"
    Start-Process -FilePath "python" -ArgumentList "app.py" -WorkingDirectory $workshopDir -WindowStyle Hidden
    $workshopRunning = Wait-ForPort -port 5003 -timeout 30 -name "Workshop"
}

# Start ELAINE
$elaineRunning = Wait-ForPort -port 5000 -timeout 3 -name "ELAINE"
if (-not $elaineRunning) {
    Log "  Starting ELAINE..."
    $elaineDir = Join-Path $SourceBase "CK\Elaine"
    Start-Process -FilePath "python" -ArgumentList "app.py" -WorkingDirectory $elaineDir -WindowStyle Hidden
    $elaineRunning = Wait-ForPort -port 5000 -timeout 30 -name "ELAINE"
}

# ── PHASE 3: Report ─────────────────────────────────────────────────────
Log ""
Log "Phase 3: Report"
Log "----------------------------------------------"

$bootEnd = Get-Date
$bootDuration = ($bootEnd - $bootStart).TotalSeconds

$services = @(
    @{Name="Ollama"; Port=11434; Running=$ollamaRunning},
    @{Name="Supervisor"; Port=9000; Running=$supervisorRunning},
    @{Name="Workshop"; Port=5003; Running=$workshopRunning},
    @{Name="ELAINE"; Port=5000; Running=$elaineRunning}
)

$ok = ($services | Where-Object { $_.Running }).Count
$total = $services.Count

Log ""
Log "  Boot complete: $ok/$total services running ($([math]::Round($bootDuration, 1))s)"
foreach ($s in $services) {
    $icon = if ($s.Running) { "[OK]" } else { "[FAIL]" }
    Log "    $icon $($s.Name) (:$($s.Port))"
}

Log "=============================================="
Log ""
