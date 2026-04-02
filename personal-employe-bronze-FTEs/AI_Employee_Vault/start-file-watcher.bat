@echo off
REM AI Employee - Start File System Watcher
REM Usage: start-file-watcher.bat [vault_path]

set VAULT_PATH=%~1
if "%VAULT_PATH%"=="" set VAULT_PATH=%~dp0..

echo Starting File System Watcher...
echo Vault: %VAULT_PATH%
echo.

cd /d "%VAULT_PATH%"
python -m watchers.filesystem_watcher .

echo.
echo Watcher stopped.
pause
