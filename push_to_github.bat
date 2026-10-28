@echo off
title Push Livestock Health Monitoring to GitHub
color 0B
cls
echo =====================================================================
echo    1-Click GitHub Publisher - Livestock Health Monitoring System
echo =====================================================================
echo.
cd /d "%~dp0"

echo Step 1: Opening GitHub in your browser to create a new repository...
timeout /t 2 /nobreak >nul
start https://github.com/new

echo.
echo =====================================================================
echo Instructions on the GitHub web page that just opened:
echo   1. Repository name: livestock-health-monitoring
echo   2. Leave README, .gitignore, and License UNCHECKED.
echo   3. Click "Create repository".
echo   4. Copy the repository URL (e.g. https://github.com/YourName/livestock-health-monitoring.git)
echo =====================================================================
echo.
set /p REPO_URL="Paste your GitHub repository URL here and press Enter: "

if "%REPO_URL%"=="" (
    echo.
    echo [ERROR] No URL was entered.
    pause
    exit /b 1
)

echo.
echo [2/3] Configuring remote origin...
git remote remove origin >nul 2>&1
git remote add origin %REPO_URL%
git branch -M main

echo.
echo [3/3] Uploading code to GitHub...
git push -u origin main

if errorlevel 1 (
    echo.
    echo [NOTE] If a GitHub sign-in window popped up, please complete the login.
) else (
    echo.
    echo =====================================================================
    echo   SUCCESS! Your project is now live on GitHub!
    echo =====================================================================
)

echo.
pause
