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

REM Try different Python commands to find the best one
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
    goto :python_found
)

python3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python3
    goto :python_found
)

py --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py
    goto :python_found
)

echo ❌ Python not found
echo.
echo Install Python from: https://python.org/downloads
echo Or use: university-setup.bat for full setup instructions
echo.
pause
exit /b 1

:python_found
echo ✅ Python found (%PYTHON_CMD%) - Starting agent...
echo.

REM Start the agent directly
%PYTHON_CMD% agent.py

echo.
echo 🛑 Agent stopped
pause
