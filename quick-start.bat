@echo off
title Start University Remote Control

echo.
echo =========================================================
echo         🚀 QUICK START - UNIVERSITY REMOTE CONTROL
echo =========================================================
echo.

REM Check if we have the required files
if not exist "agent.py" (
    echo ❌ Agent files not found
    echo.
    echo Please ensure these files are in the same folder:
    echo   • agent.py
    echo   • config.json
    echo   • check_system.py
    echo.
    pause
    exit /b 1
)

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found
    echo.
    echo Install Python from: https://python.org/downloads
    echo Or use: university-setup.bat for full setup instructions
    echo.
    pause
    exit /b 1
)

echo ✅ Python found - Starting agent...
echo.

REM Start the agent directly
python agent.py

echo.
echo 🛑 Agent stopped
pause
