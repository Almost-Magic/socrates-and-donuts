# AMTL App Launcher — 2026-02-15
# Run in PowerShell to start all apps
# Usage: .\start-all.ps1
# To start specific apps: .\start-all.ps1 -Apps "ELAINE","Ripple CRM"

param(
    [string[]]$Apps = @()
)

$base = "C:\Users\ManiPadisetti\Dropbox\Desktop DB\Books and Articles Mani\Books\Almost Magic Tech Lab AMTL\Source and Brand\CK"

$allApps = @(
    @{Name="ELAINE"; Path="Elaine-git"; Port=5000; Cmd="python app.py"},
    @{Name="Ripple CRM"; Path="Ripple CRM"; Port=5001; Cmd="node server.js"},
    @{Name="Identity Atlas"; Path="Identity Atlas"; Port=5002; Cmd="node server.js"},
    @{Name="CK Writer"; Path="CK-Writer"; Port=5004; Cmd="node server.js"},
    @{Name="Junk Drawer"; Path="Junk Drawer file management system"; Port=5005; Cmd="python app.py"},
    @{Name="Opp Hunter"; Path="Opportunity Hunter\backend"; Port=5006; Cmd="python app.py"},
    @{Name="Peterman"; Path="Peterman"; Port=5008; Cmd="node server.js"},
    @{Name="Learning Assistant"; Path="Learning Assistant"; Port=5012; Cmd="node server.js"},
    @{Name="Swiss Army Knife"; Path="Swiss Army Knife"; Port=5014; Cmd="python app.py"},
    @{Name="AMTL TTS"; Path="amtl-tts"; Port=5015; Cmd="uvicorn src.app:create_app --port 5015"},
    @{Name="Genie"; Path="Finance App\Genie"; Port=8000; Cmd="python -m uvicorn app:app --port 8000"},
    @{Name="AMTL Security"; Path="amtl-security"; Port=8600; Cmd="uvicorn app:app --port 8600"}
)

# Filter if specific apps requested
if ($Apps.Count -gt 0) {
    $selectedApps = $allApps | Where-Object { $Apps -contains $_.Name }
} else {
    $selectedApps = $allApps
}

Write-Host "`n  AMTL App Launcher" -ForegroundColor Cyan
Write-Host "  ================`n" -ForegroundColor Cyan

foreach ($app in $selectedApps) {
    $port = $app.Port
    $busy = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($busy) {
        Write-Host "  [SKIP] $($app.Name) - port $port already in use" -ForegroundColor Yellow
    } else {
        Write-Host "  [START] $($app.Name) on port $port..." -ForegroundColor Green
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$base\$($app.Path)'; `$env:PORT=$port; $($app.Cmd)"
    }
}

Write-Host "`n  All apps launched. Check each PowerShell window for status." -ForegroundColor Cyan
Write-Host "  Ports: 5000-5015 (core apps), 8000+ (heavy services)`n" -ForegroundColor DarkGray
