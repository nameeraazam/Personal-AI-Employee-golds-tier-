@echo off
REM Gold Tier FTE - Odoo Docker Management
REM Personal AI Employee - Gold Tier

echo ================================================================
echo   ODOO DOCKER MANAGEMENT
echo ================================================================
echo.
echo Choose an option:
echo.
echo 1. Start Odoo Docker containers
echo 2. Stop Odoo Docker containers
echo 3. Check status
echo 4. View logs
echo 5. Create backup
echo 6. Exit
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto start
if "%choice%"=="2" goto stop
if "%choice%"=="3" goto status
if "%choice%"=="4" goto logs
if "%choice%"=="5" goto backup
if "%choice%"=="6" goto end

echo Invalid choice!
pause
exit /b 1

:start
echo.
echo Starting Odoo Docker containers...
docker-compose -f odoo-docker\docker-compose.yml up -d
echo.
echo Containers started!
echo.
echo Odoo will be available at: http://localhost:8069
echo PgAdmin will be available at: http://localhost:8080
echo.
echo Default credentials:
echo   Odoo: admin / admin_secret_123
echo   PgAdmin: admin@example.com / admin_secret_123
echo.
pause
goto end

:stop
echo.
echo Stopping Odoo Docker containers...
docker-compose -f odoo-docker\docker-compose.yml down
echo.
echo Containers stopped!
pause
goto end

:status
echo.
echo Checking container status...
docker-compose -f odoo-docker\docker-compose.yml ps
pause
goto end

:logs
echo.
echo Viewing Odoo logs (press Ctrl+C to exit)...
docker-compose -f odoo-docker\docker-compose.yml logs -f odoo
goto end

:backup
echo.
echo Creating database backup...
docker exec gold-tier-odoo-db pg_dump -U odoo -F c -f /backups/backup_%date:~-4,4%%date:~3,2%%date:~0,2%.dump odoo
echo.
echo Backup created!
pause
goto end

:end
