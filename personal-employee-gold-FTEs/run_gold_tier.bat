@echo off
REM Gold Tier FTE - Run Orchestrator
REM Personal AI Employee - Gold Tier

echo ================================================================
echo   GOLD TIER FTE - ORCHESTRATOR
echo   Starting unified monitoring...
echo ================================================================
echo.

REM Check if .env exists
if not exist .env (
    echo ERROR: .env file not found!
    echo Please run setup.bat first or create .env from .env.example
    pause
    exit /b 1
)

REM Run the orchestrator
python scripts\gold_tier_orchestrator.py --start

echo.
echo ================================================================
echo   Orchestrator stopped.
echo ================================================================
pause
