# The Supervisor — Meta-Guardian
# Almost Magic Tech Lab — February 2026
#
# Runs via Windows Task Scheduler every 10 minutes.
# Checks if The Supervisor is alive. Restarts if not.
#
# To register:
#   $action = New-ScheduledTaskAction -Execute "powershell.exe" `
#     -Argument "-ExecutionPolicy Bypass -File `"$PWD\meta_guardian.ps1`""
#   $trigger = New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Minutes 10) `
#     -Once -At (Get-Date)
#   Register-ScheduledTask -TaskName "AMTL-MetaGuardian" -Action $action `
#     -Trigger $trigger -Description "Watches The Supervisor"

$ErrorActionPreference = "Continue"
$SourceBase = Split-Path -Parent $PSScriptRoot
if (-not $SourceBase) { $SourceBase = "C:\Users\ManiPadisetti\Dropbox\Desktop DB\Books and Articles Mani\Books\Almost Magic Tech Lab AMTL\Source and Brand" }
$SupervisorDir = Join-Path $SourceBase "Supervisor"
$LogFile = Join-Path $SupervisorDir "logs\meta_guardian.log"

function Log($msg) {
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "$ts | META-GUARDIAN | $msg"
    Add-Content -Path $LogFile -Value $line -Encoding UTF8
}

# Check Supervisor health
try {
    $resp = Invoke-WebRequest -Uri "http://localhost:9000/api/health" -UseBasicParsing -TimeoutSec 10 -ErrorAction Stop
    if ($resp.StatusCode -eq 200) {
        # Supervisor is alive — nothing to do
        exit 0
    }
} catch {
    # Supervisor not responding
}

Log "Supervisor not responding. Attempting restart..."

# Start Supervisor
Start-Process -FilePath "python" -ArgumentList "supervisor.py" -WorkingDirectory $SupervisorDir -WindowStyle Hidden

# Wait 15 seconds and check again
Start-Sleep -Seconds 15

try {
    $resp = Invoke-WebRequest -Uri "http://localhost:9000/api/health" -UseBasicParsing -TimeoutSec 10 -ErrorAction Stop
    if ($resp.StatusCode -eq 200) {
        Log "Supervisor restarted successfully"
        exit 0
    }
} catch {
    # Still not responding
}

Log "CRITICAL: Supervisor could not be restarted. Manual intervention required."

# Write alert
$alert = @{
    timestamp = (Get-Date -Format "o")
    type = "meta_guardian_failure"
    service = "The Supervisor"
    message = "Meta-Guardian could not restart The Supervisor"
} | ConvertTo-Json -Compress
$alertFile = Join-Path $SupervisorDir "logs\alerts.jsonl"
Add-Content -Path $alertFile -Value $alert -Encoding UTF8
