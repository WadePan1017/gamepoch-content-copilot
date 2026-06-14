@echo off
cd /d "%~dp0"

echo ========================================
echo   GamePoch Content Copilot
echo   Game publishing content demo
echo ========================================
echo.
echo Starting local server...
echo Demo URL: http://localhost:8000
echo.

start "GamePoch Content Copilot Server" /D "%~dp0" cmd /k "python app.py"

timeout /t 4 /nobreak >nul
start http://localhost:8000

echo Browser opened. Keep the server window running during the demo.
