@echo off
title ELAINE — Almost Magic Tech Lab
cd /d "%~dp0elaine-desktop-v2"
if not exist node_modules (
    echo Installing dependencies...
    npm install
)
echo Starting ELAINE Desktop...
npm start
