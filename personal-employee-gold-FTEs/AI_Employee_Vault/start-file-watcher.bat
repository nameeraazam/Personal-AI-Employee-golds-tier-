@echo off
REM Start File System Watcher

echo ========================================
echo   AI Employee - File System Watcher
echo ========================================
echo.

cd /d "%~dp0"

python -m watchers.filesystem_watcher .

pause
