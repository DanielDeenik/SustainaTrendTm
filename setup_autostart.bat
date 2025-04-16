@echo off
echo Setting up SustainaTrend™ to start automatically with Windows...

REM Get the full path to the start script
set "SCRIPT_PATH=%~dp0start_sustainatrend.bat"
set "SCRIPT_PATH=%SCRIPT_PATH:\=/%"

REM Create a shortcut in the Startup folder
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_PATH=%STARTUP_FOLDER%\SustainaTrend.lnk"

REM Create the shortcut using PowerShell
powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%SHORTCUT_PATH%'); $SC.TargetPath = '%SCRIPT_PATH%'; $SC.WorkingDirectory = '%~dp0'; $SC.Save()"

echo SustainaTrend™ has been set up to start automatically with Windows.
echo The shortcut has been created at: %SHORTCUT_PATH%
echo.
echo To disable autostart, simply delete the shortcut from the Startup folder.
pause 