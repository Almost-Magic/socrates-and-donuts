# Peterman Startup Script
# PowerShell version for modern Windows

$ErrorActionPreference = "SilentlyContinue"
Set-Location $PSScriptRoot

Write-Host "Starting Peterman v2.1..." -ForegroundColor Cyan

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found in PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Create venv if needed
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate venv
& ".\venv\Scripts\Activate.ps1"

# Install requirements
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet 2>$null

# Kill anything on port 5008
$process = Get-NetTCPConnection -LocalPort 5008 -State Listen -ErrorAction SilentlyContinue
if ($process) {
    Write-Host "Stopping existing Peterman on port 5008..." -ForegroundColor Yellow
    Stop-Process -Id $process.OwningProcess -Force
    Start-Sleep -Seconds 1
}

# Delete old database locks
Remove-Item -Force "peterman.db-wal" -ErrorAction SilentlyContinue
Remove-Item -Force "peterman.db-shm" -ErrorAction SilentlyContinue

# Start Flask
Write-Host ""
Write-Host "Peterman starting on http://localhost:5008" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

python run.py
