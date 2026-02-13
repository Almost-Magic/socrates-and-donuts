$conn = Get-NetTCPConnection -LocalPort 8420 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if ($conn) {
    $svcPid = $conn.OwningProcess
    taskkill /F /T /PID $svcPid 2>$null | Out-Null
    Start-Sleep -Seconds 2
}
$still = Get-NetTCPConnection -LocalPort 8420 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if ($still) {
    taskkill /F /T /PID $still.OwningProcess 2>$null | Out-Null
    Start-Sleep -Seconds 1
}
Set-Location -LiteralPath (Split-Path -Parent $MyInvocation.MyCommand.Path)
Start-Process python -ArgumentList "-B app.py" -WindowStyle Minimized
Start-Sleep -Seconds 3
try {
    $r = Invoke-WebRequest -Uri "http://localhost:8420/api/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "Signal Hunter restarted - health OK ($($r.StatusCode))"
} catch {
    Write-Host "Signal Hunter started but health not responding yet"
}
