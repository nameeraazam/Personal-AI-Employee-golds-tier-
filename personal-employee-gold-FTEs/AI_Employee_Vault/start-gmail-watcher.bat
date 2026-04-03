@echo off
REM Start Gmail Watcher

echo ========================================
echo   AI Employee - Gmail Watcher
echo ========================================
echo.

cd /d "%~dp0"

python -m watchers.gmail_watcher .

pause
