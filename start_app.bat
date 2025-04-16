@echo off
echo Starting SustainaTrend Application...
echo.
echo This window will remain open while the application is running.
echo To stop the application, close this window or press Ctrl+C.
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment not found. Using system Python.
)

REM Start the application
python start_app.py

REM Keep the window open if there's an error
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Application exited with error code %ERRORLEVEL%
    echo Press any key to close this window...
    pause > nul
) 