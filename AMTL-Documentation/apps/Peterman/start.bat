@echo off
title Peterman v2.1
echo Starting Peterman...

cd /d "%~dp0"

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    pause
    exit /b 1
)

:: Install dependencies if needed
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat

:: Install requirements
pip install -r requirements.txt --quiet 2>nul

:: Kill anything on port 5008
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5008 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)

:: Delete old database lock if exists
del /f peterman.db-wal 2>nul
del /f peterman.db-shm 2>nul

:: Start Flask
echo Peterman starting on http://localhost:5008
python run.py
