<#
.SYNOPSIS
    AMTL Service Manager - start, stop, restart, status for all Almost Magic services.
.USAGE
    .\services.ps1 start all          # Start all services (dependency order)
    .\services.ps1 stop all           # Stop all services (reverse order)
    .\services.ps1 restart genie      # Restart single service
    .\services.ps1 status             # Show what's running
    .\services.ps1 stop elaine        # Stop single service
.NOTES
    Author: Guruve (Claude #2) for Mani Padisetti @ Almost Magic Tech Lab
    Uses temp script files for launching to avoid PowerShell escaping issues.
    Service names accept aliases: ck-writer, author-studio, junk-drawer, etc.
#>

param(
    [Parameter(Position=0)][string]$Action = "status",
    [Parameter(Position=1)][string]$Target = ""
)

$ErrorActionPreference = "SilentlyContinue"
$BASE = Split-Path -Parent $MyInvocation.MyCommand.Path

# ── Service Definitions (order = startup order) ──────────────
$Services = [ordered]@{
    supervisor = @{
        Name   = "Supervisor"
        Port   = 9000
        Dir    = "$BASE\Supervisor"
        Cmd    = "python supervisor.py"
        Health = "/api/health"
    }
    workshop = @{
        Name   = "Workshop"
        Port   = 5003
        Dir    = "$BASE\CK\workshop"
        Cmd    = "python app.py"
        Health = "/api/health"
    }
    elaine = @{
        Name   = "ELAINE"
        Port   = 5000
        Dir    = "$BASE\CK\Elaine"
        Cmd    = "python app.py"
        Health = "/api/health"
    }
    costanza = @{
        Name   = "Costanza"
        Port   = 5001
        Dir    = "$BASE\Costanza"
        Cmd    = "python app.py"
        Health = "/api/health"
    }
    learning = @{
        Name   = "Learning Assistant"
        Port   = 5002
        Dir    = "$BASE\CK\learning-assistant"
        Cmd    = "python app.py"
        Health = "/api/health"
    }
    writer = @{
        Name   = "CK Writer"
        Port   = 5004
        Dir    = "$BASE\CK\CK-Writer"
        Cmd    = "python app.py"
        Health = "/api/health"
    }
    junkdrawer = @{
        Name   = "Junk Drawer"
        Port   = 5006
        Dir    = "$BASE\CK\Junk Drawer file management system"
        Cmd    = "python app.py"
        Health = "/api/health"
    }
    authorstudio = @{
        Name   = "Author Studio"
        Port   = 5007
        Dir    = "$BASE\CK\Author Studio"
        Cmd    = "python main_flask.py"
        Health = "/api/health"
    }
    peterman = @{
        Name   = "Peterman"
        Port   = 5008
        Dir    = "$BASE\Peterman SEO"
        Cmd    = "python app.py"
        Health = "/api/health"
    }
    genie = @{
        Name   = "Genie Backend"
        Port   = 8000
        Dir    = "$BASE\Finance App\Genie\backend"
        Cmd    = "python -m uvicorn app:app --host 0.0.0.0 --port 8000"
        Health = "/api/health"
    }
    ripple = @{
        Name   = "Ripple Backend"
        Port   = 8100
        Dir    = "$BASE\Ripple CRM and Spark Marketing\backend"
        Cmd    = "python -m uvicorn app.main:app --host 0.0.0.0 --port 8100"
        Health = "/api/health"
    }
    touchstone = @{
        Name   = "Touchstone"
        Port   = 8200
        Dir    = "$BASE\Touchstone\backend"
        Cmd    = "python -m uvicorn app.main:app --host 0.0.0.0 --port 8200"
        Health = "/api/v1/health"
    }
    geniefe = @{
        Name   = "Genie Frontend"
        Port   = 3000
        Dir    = "$BASE\Finance App\Genie\frontend"
        Cmd    = "npm run dev"
        Health = "/"
    }
    ripplefe = @{
        Name   = "Ripple Frontend"
        Port   = 3100
        Dir    = "$BASE\Ripple CRM and Spark Marketing\frontend"
        Cmd    = "npm run dev"
        Health = "/"
    }
}

# ── Aliases ──────────────────────────────────────────────────
$Aliases = @{
    "ck-writer"           = "writer"
    "ckwriter"            = "writer"
    "ck_writer"           = "writer"
    "learning-assistant"  = "learning"
    "learningassistant"   = "learning"
    "author-studio"       = "authorstudio"
    "author_studio"       = "authorstudio"
    "author"              = "authorstudio"
    "junk-drawer"         = "junkdrawer"
    "junk_drawer"         = "junkdrawer"
    "junk"                = "junkdrawer"
    "genie-backend"       = "genie"
    "genie-be"            = "genie"
    "genie-frontend"      = "geniefe"
    "genie-fe"            = "geniefe"
    "ripple-backend"      = "ripple"
    "ripple-be"           = "ripple"
    "ripple-crm"          = "ripple"
    "ripple-frontend"     = "ripplefe"
    "ripple-fe"           = "ripplefe"
    "supe"                = "supervisor"
    "suze"                = "elaine"
}

function Resolve-Name([string]$ServiceName) {
    $key = $ServiceName.ToLower().Trim()
    if ($Aliases.ContainsKey($key)) { $key = $Aliases[$key] }
    if ($Services.Contains($key)) { return $key }
    # Fuzzy: partial match on key or name
    foreach ($k in $Services.Keys) {
        if ($k -like "*$key*" -or $Services[$k].Name -like "*$key*") { return $k }
    }
    return $null
}

# ── Helpers ──────────────────────────────────────────────────

function Get-PortPID([int]$Port) {
    $conn = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
            Where-Object { $_.OwningProcess -ne 0 } |
            Select-Object -First 1
    if ($conn) { return $conn.OwningProcess }
    return $null
}

function Test-Health([int]$Port, [string]$Path) {
    try {
        $url = "http://localhost:${Port}${Path}"
        $resp = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
        return ($resp.StatusCode -eq 200)
    } catch {
        return $false
    }
}

function Stop-Svc([string]$Key) {
    $svc = $Services[$Key]
    $name = $svc.Name
    $port = $svc.Port

    $svcPid = Get-PortPID $port
    if (-not $svcPid) {
        Write-Host ("  {0,-22} " -f $name) -NoNewline -ForegroundColor DarkGray
        Write-Host "not running" -ForegroundColor DarkGray
        return
    }

    taskkill /F /T /PID $svcPid 2>$null | Out-Null
    Start-Sleep -Milliseconds 800

    # Double-check
    $still = Get-PortPID $port
    if ($still) {
        taskkill /F /T /PID $still 2>$null | Out-Null
        Start-Sleep -Milliseconds 500
    }

    $gone = -not (Get-PortPID $port)
    if ($gone) {
        Write-Host ("  {0,-22} " -f $name) -NoNewline -ForegroundColor Cyan
        Write-Host "stopped (was PID $svcPid)" -ForegroundColor Green
    } else {
        Write-Host ("  {0,-22} " -f $name) -NoNewline -ForegroundColor Red
        Write-Host "FAILED to stop on :$port" -ForegroundColor Red
    }
}

function Start-Svc([string]$Key) {
    $svc = $Services[$Key]
    $name = $svc.Name
    $port = $svc.Port
    $dir  = $svc.Dir
    $cmd  = $svc.Cmd
    $health = $svc.Health

    # Already running and healthy?
    $existing = Get-PortPID $port
    if ($existing) {
        $ok = Test-Health $port $health
        if ($ok) {
            Write-Host ("  {0,-22} " -f $name) -NoNewline -ForegroundColor Green
            Write-Host "already running (PID $existing)" -ForegroundColor DarkGray
            return
        }
        # Running but unhealthy - kill and restart
        Write-Host ("  {0,-22} " -f $name) -NoNewline -ForegroundColor Yellow
        Write-Host "unhealthy - restarting..." -ForegroundColor Yellow
        Stop-Svc $Key
        Start-Sleep -Seconds 1
    }

    if (-not (Test-Path $dir)) {
        Write-Host ("  {0,-22} " -f $name) -NoNewline -ForegroundColor Red
        Write-Host "directory not found: $dir" -ForegroundColor Red
        return
    }

    # Write temp launch script - avoids all PowerShell escaping issues
    $tempFile = Join-Path $env:TEMP "amtl_launch_${Key}.ps1"
    "Set-Location -LiteralPath '$dir'`n$cmd" | Set-Content -Path $tempFile -Encoding UTF8

    Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -WindowStyle Minimized -File `"$tempFile`"" -WindowStyle Minimized

    Write-Host ("  {0,-22} " -f $name) -NoNewline -ForegroundColor Cyan
    Write-Host "launching on :$port" -NoNewline -ForegroundColor DarkGray

    # Wait for health
    $maxWait = 20
    for ($i = 1; $i -le $maxWait; $i++) {
        Start-Sleep -Seconds 1
        if (Test-Health $port $health) {
            $newPid = Get-PortPID $port
            Write-Host " UP (PID $newPid, ${i}s)" -ForegroundColor Green
            return
        }
    }
    # Check if at least port is open
    $svcPid = Get-PortPID $port
    if ($svcPid) {
        Write-Host " port open (PID $svcPid) but health not responding" -ForegroundColor Yellow
    } else {
        Write-Host " TIMEOUT (${maxWait}s)" -ForegroundColor Red
    }
}

function Show-Status {
    Write-Host ""
    Write-Host "  AMTL Service Status" -ForegroundColor White
    Write-Host "  ===================" -ForegroundColor DarkGray
    Write-Host ""

    # Infrastructure (external)
    foreach ($infra in @(
        @{ Name = "Ollama"; Port = 11434 },
        @{ Name = "Docker/n8n"; Port = 5678 },
        @{ Name = "PostgreSQL"; Port = 5433 },
        @{ Name = "Redis"; Port = 6379 }
    )) {
        $svcPid = Get-PortPID $infra.Port
        $label = ("{0,-22}" -f $infra.Name)
        if ($svcPid) {
            Write-Host "  $label " -NoNewline -ForegroundColor Green
            Write-Host "UP   :$($infra.Port)  PID $svcPid" -ForegroundColor DarkGray
        } else {
            Write-Host "  $label " -NoNewline -ForegroundColor Red
            Write-Host "DOWN :$($infra.Port)" -ForegroundColor DarkGray
        }
    }

    Write-Host ""
    $up = 0; $total = $Services.Count

    foreach ($key in $Services.Keys) {
        $svc = $Services[$key]
        $label = ("{0,-22}" -f $svc.Name)
        $port = $svc.Port
        $svcPid = Get-PortPID $port

        if ($svcPid) {
            $healthy = Test-Health $port $svc.Health
            if ($healthy) {
                $up++
                Write-Host "  $label " -NoNewline -ForegroundColor Green
                Write-Host "UP   :$port  PID $svcPid" -ForegroundColor DarkGray
            } else {
                Write-Host "  $label " -NoNewline -ForegroundColor Yellow
                Write-Host "SICK :$port  PID $svcPid" -ForegroundColor DarkGray
            }
        } else {
            Write-Host "  $label " -NoNewline -ForegroundColor Red
            Write-Host "DOWN :$port" -ForegroundColor DarkGray
        }
    }

    Write-Host ""
    $color = if ($up -eq $total) { "Green" } elseif ($up -gt ($total / 2)) { "Yellow" } else { "Red" }
    Write-Host "  $up/$total services running" -ForegroundColor $color
    Write-Host ""
}

# ── Main ─────────────────────────────────────────────────────

Write-Host ""
Write-Host "  AMTL Service Manager v2" -ForegroundColor Cyan
Write-Host ""

switch ($Action.ToLower()) {
    "status" {
        Show-Status
    }

    "start" {
        if ($Target -eq "all" -or $Target -eq "") {
            Write-Host "  Starting all services (dependency order)..." -ForegroundColor White
            Write-Host ""

            # Check Ollama first
            $ollamaPid = Get-PortPID 11434
            if ($ollamaPid) {
                Write-Host ("  {0,-22} " -f "Ollama") -NoNewline -ForegroundColor Green
                Write-Host "running (PID $ollamaPid)" -ForegroundColor DarkGray
            } else {
                Write-Host ("  {0,-22} " -f "Ollama") -NoNewline -ForegroundColor Yellow
                Write-Host "not running - start manually (ollama serve)" -ForegroundColor Yellow
            }
            Write-Host ""

            foreach ($key in $Services.Keys) {
                Start-Svc $key
            }
        } else {
            $resolved = Resolve-Name $Target
            if (-not $resolved) {
                Write-Host "  Unknown service: $Target" -ForegroundColor Red
                Write-Host "  Available: $($Services.Keys -join ', ')" -ForegroundColor DarkGray
                return
            }
            Start-Svc $resolved
        }
        Write-Host ""
    }

    "stop" {
        if ($Target -eq "all") {
            Write-Host "  Stopping all services (reverse order)..." -ForegroundColor White
            Write-Host ""
            $reversed = [array]$Services.Keys
            [array]::Reverse($reversed)
            foreach ($key in $reversed) {
                Stop-Svc $key
            }
        } elseif ($Target -eq "" -or $Target -eq $null) {
            Write-Host "  Usage: .\services.ps1 stop [service|all]" -ForegroundColor Yellow
        } else {
            $resolved = Resolve-Name $Target
            if (-not $resolved) {
                Write-Host "  Unknown service: $Target" -ForegroundColor Red
                Write-Host "  Available: $($Services.Keys -join ', ')" -ForegroundColor DarkGray
                return
            }
            Stop-Svc $resolved
        }
        Write-Host ""
    }

    "restart" {
        if ($Target -eq "all") {
            Write-Host "  Restarting all services..." -ForegroundColor White
            Write-Host ""
            $reversed = [array]$Services.Keys
            [array]::Reverse($reversed)
            foreach ($key in $reversed) { Stop-Svc $key }
            Write-Host ""
            Start-Sleep -Seconds 2
            Write-Host "  Starting all services..." -ForegroundColor White
            Write-Host ""
            foreach ($key in $Services.Keys) { Start-Svc $key }
        } elseif ($Target -eq "" -or $Target -eq $null) {
            Write-Host "  Usage: .\services.ps1 restart [service|all]" -ForegroundColor Yellow
        } else {
            $resolved = Resolve-Name $Target
            if (-not $resolved) {
                Write-Host "  Unknown service: $Target" -ForegroundColor Red
                Write-Host "  Available: $($Services.Keys -join ', ')" -ForegroundColor DarkGray
                return
            }
            Stop-Svc $resolved
            Start-Sleep -Seconds 2
            Start-Svc $resolved
        }
        Write-Host ""
    }

    default {
        Write-Host "  Usage: .\services.ps1 [start|stop|restart|status] [all|service-name]" -ForegroundColor White
        Write-Host ""
        Write-Host "  Services:" -ForegroundColor DarkGray
        foreach ($key in $Services.Keys) {
            $sn = $Services[$key].Name
            $sp = $Services[$key].Port
            $line = "    $key - $sn on port $sp"
            Write-Host $line -ForegroundColor DarkGray
        }
        Write-Host ""
        Write-Host '  Aliases: ck-writer, author-studio, junk-drawer, genie-fe, ripple-fe, suze' -ForegroundColor DarkGray
    }
}
