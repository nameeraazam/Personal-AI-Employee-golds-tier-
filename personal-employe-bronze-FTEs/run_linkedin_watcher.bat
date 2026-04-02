@echo off
REM LinkedIn Watcher - Silver Tier
REM Quick Start Script for Windows

echo ================================================================
echo LINKEDIN WATCHER - SILVER TIER
echo ================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Check if Playwright is installed
python -c "import playwright" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing Playwright...
    pip install playwright python-dotenv
    echo [INFO] Installing browsers...
    playwright install chromium
    echo.
) else (
    echo [OK] Playwright found
)

REM Check if .env has credentials
findstr /C:"LINKEDIN_EMAIL=your.email" .env >nul 2>&1
if not errorlevel 1 (
    echo.
    echo [WARNING] LinkedIn credentials not configured!
    echo Please edit .env and add your LinkedIn email and password
    echo.
    echo Press any key to open .env file...
    pause >nul
    notepad .env
    echo.
    echo After saving .env, press any key to continue...
    pause >nul
)

echo.
echo ================================================================
echo Starting LinkedIn Watcher...
echo ================================================================
echo.
echo Monitoring will start in 3 seconds...
echo Press Ctrl+C to stop at any time
echo.
timeout /t 3 /nobreak >nul

REM Run the watcher
python scripts\linkedin_watcher.py

echo.
echo ================================================================
echo Watcher stopped
echo ================================================================
pause
