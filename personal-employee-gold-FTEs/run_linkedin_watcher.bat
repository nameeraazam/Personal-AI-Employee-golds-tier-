@echo off
REM Start LinkedIn Watcher

echo ========================================
echo   AI Employee - LinkedIn Watcher
echo ========================================
echo.

cd /d "%~dp0"

python scripts\linkedin_watcher.py

pause
