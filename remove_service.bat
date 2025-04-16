@echo off
echo Removing SustainaTrend Windows Service...

REM Check for administrative privileges
NET SESSION >nul 2>&1
if %errorLevel% neq 0 (
    echo Requesting administrative privileges...
    powershell -Command "Start-Process '%~dpnx0' -Verb RunAs"
    exit /b
)

REM Check if service exists
sc query SustainaTrendService >nul 2>&1
if %errorLevel% neq 0 (
    echo Service does not exist.
    pause
    exit /b 0
)

REM Stop the service if it's running
echo Stopping service...
sc stop SustainaTrendService
timeout /t 5 >nul

REM Force stop the service using taskkill
echo Force stopping service...
taskkill /F /FI "SERVICES eq SustainaTrendService" /T
timeout /t 5 >nul

REM Delete the service
echo Deleting service...
sc delete SustainaTrendService
timeout /t 5 >nul

REM Try to delete using alternative method
echo Trying alternative deletion method...
powershell -Command "Remove-Service -Name 'SustainaTrendService' -Force"
timeout /t 5 >nul

REM Wait for service to be fully removed
echo Waiting for service to be fully removed...
timeout /t 10 >nul

REM Verify service is gone
sc query SustainaTrendService >nul 2>&1
if %errorLevel% equ 0 (
    echo Error: Service still exists after deletion attempt
    echo Please try the following steps manually:
    echo 1. Open Services (services.msc)
    echo 2. Find "SustainaTrend Intelligence Platform"
    echo 3. Right-click and select "Stop"
    echo 4. Right-click and select "Delete"
    echo 5. Wait a few minutes and try this script again
    pause
    exit /b 1
) else (
    echo Service successfully removed.
)

pause 