@echo off
echo Starting SustainaTrend Intelligence Platform...

REM Check for administrative privileges
NET SESSION >nul 2>&1
if %errorLevel% neq 0 (
    echo Requesting administrative privileges...
    powershell -Command "Start-Process '%~dpnx0' -Verb RunAs"
    exit /b
)

REM Get absolute paths
set "SCRIPT_DIR=%~dp0"
set "VENV_PATH=%SCRIPT_DIR%venv"
set "PYTHON_PATH=%VENV_PATH%\Scripts\python.exe"
set "APP_PATH=%SCRIPT_DIR%src\frontend\refactored\app.py"

REM Verify paths exist
if not exist "%PYTHON_PATH%" (
    echo Error: Python executable not found at %PYTHON_PATH%
    pause
    exit /b 1
)

if not exist "%APP_PATH%" (
    echo Error: Application file not found at %APP_PATH%
    pause
    exit /b 1
)

REM Activate virtual environment
call "%VENV_PATH%\Scripts\activate.bat"

REM Run the application
echo Starting application...
"%PYTHON_PATH%" "%APP_PATH%"

REM Keep the window open if there's an error
if %errorLevel% neq 0 (
    echo.
    echo Application exited with error code %errorLevel%
    pause
) 