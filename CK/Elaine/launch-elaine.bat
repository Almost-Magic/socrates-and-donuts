@echo off
title ELAINE - Chief of Staff
cd /d "%~dp0"
echo.
echo   ==============================
echo   ELAINE - Chief of Staff
echo   Almost Magic Tech Lab
echo   Port: 5000
echo   ==============================
echo.

:: Check if already running
powershell -Command "if (Get-NetTCPConnection -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue) { exit 0 } else { exit 1 }" 2>nul
if %ERRORLEVEL% == 0 (
    echo   ELAINE already running on :5000
    echo   Opening in browser...
    start http://192.168.4.55:5000
    exit /b 0
)

echo   Starting ELAINE server...
start /MIN "ELAINE Server" python app.py

:: Wait for health
set /a count=0
:wait_loop
if %count% GEQ 30 goto timeout
timeout /t 1 /nobreak >nul
set /a count+=1
powershell -Command "try { $r = Invoke-WebRequest -Uri 'http://localhost:5000/api/health' -UseBasicParsing -TimeoutSec 3; if ($r.StatusCode -eq 200) { exit 0 } } catch { exit 1 }" 2>nul
if %ERRORLEVEL% == 0 goto healthy
echo   Waiting... (%count%s)
goto wait_loop

:healthy
echo.
echo   ELAINE is UP on :5000
echo   Opening in browser...
start http://192.168.4.55:5000
exit /b 0

:timeout
echo.
echo   WARNING: ELAINE did not respond within 30s
echo   Check the server window for errors
pause
