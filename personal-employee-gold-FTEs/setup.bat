@echo off
REM Gold Tier FTE - Quick Start Script
REM Personal AI Employee - Gold Tier

echo ================================================================
echo   GOLD TIER FTE - QUICK START
echo   Personal AI Employee System
echo ================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/5] Python found...
echo.

REM Check if .env file exists
if not exist .env (
    echo [2/5] Creating .env file from template...
    copy .env.example .env
    echo.
    echo ================================================================
    echo   IMPORTANT: Edit .env file with your credentials
    echo ================================================================
    echo.
    echo Please edit the .env file and add:
    echo   - LinkedIn credentials
    echo   - Facebook credentials (or API tokens)
    echo   - Odoo credentials
    echo.
    echo Then run this script again.
    echo.
    pause
    exit /b 0
) else (
    echo [2/5] .env file found...
    echo.
)

REM Install dependencies
echo [3/5] Installing Python dependencies...
pip install -r scripts\requirements.txt
echo.

REM Install Playwright browsers
echo [4/5] Installing Playwright browsers...
playwright install chromium
echo.

echo ================================================================
echo   INSTALLATION COMPLETE!
echo ================================================================
echo.
echo Next steps:
echo.
echo 1. Start Odoo Docker (optional):
echo    docker-compose -f odoo-docker\docker-compose.yml up -d
echo.
echo 2. Run Gold Tier Orchestrator:
echo    python scripts\gold_tier_orchestrator.py --start
echo.
echo 3. Or use quick commands:
echo    - Post to all platforms: python scripts\gold_tier_orchestrator.py --post "Your message"
echo    - Check status: python scripts\gold_tier_orchestrator.py --status
echo.
echo ================================================================
echo.
pause
