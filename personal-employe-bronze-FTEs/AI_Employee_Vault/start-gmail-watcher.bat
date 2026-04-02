@echo off
REM AI Employee - Start Gmail Watcher
REM Usage: start-gmail-watcher.bat [vault_path]

set VAULT_PATH=%~1
if "%VAULT_PATH%"=="" set VAULT_PATH=%~dp0..

echo Starting Gmail Watcher...
echo Vault: %VAULT_PATH%
echo.

cd /d "%VAULT_PATH%"
python -m watchers.gmail_watcher .

echo.
Watcher stopped.
pause
