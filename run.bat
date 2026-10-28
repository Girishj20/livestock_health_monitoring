@echo off
title Livestock Health Monitoring System
color 0A
cls
echo =====================================================================
echo    Livestock Health Monitoring ^& Disease Risk Assessment System
echo =====================================================================
echo.
cd /d "%~dp0"

echo [1/3] Checking Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not found in system PATH.
    echo Please ensure Python 3.10+ is installed and checked in PATH.
    echo.
    pause
    exit /b 1
)

echo [2/3] Checking database and trained ML models...
if not exist "instance\livestock.db" (
    echo Initializing database and seeding sample records...
    python scripts\seed_data.py
)

echo [3/3] Launching Livestock Health Monitoring System...
echo.
echo Application URL: http://127.0.0.1:5000
echo.
echo Demo Accounts:
echo   - System Administrator: admin@livestock.farm / Admin@123
echo   - Veterinarian:         vet.sharma@livestock.farm / Vet@12345
echo   - Dairy Farmer:         farmer.ramesh@livestock.farm / Farmer@123
echo.
echo Opening default web browser in 2 seconds...
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:5000"

echo Starting Flask server on port 5000 (Press Ctrl+C to stop)...
python app.py
pause
