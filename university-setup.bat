@echo off
chcp 65001 >nul
title University Remote Control - Professional Setup

echo.
echo =========================================================
echo        UNIVERSITY REMOTE CONTROL SETUP
echo =========================================================
echo.
echo This will set up remote control access for this computer
echo - No installation required
echo - No admin permissions needed  
echo - Works through university firewalls
echo.

REM Check if Python is available
echo Checking system requirements...

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

REM If no Python found
echo.
echo ERROR: PYTHON NOT FOUND
echo.
echo This system needs Python to run the remote control agent.
echo.
echo INSTALLATION OPTIONS:
echo    1. Download from: https://python.org/downloads
echo    2. Use Microsoft Store: "Python 3.11"
echo    3. Ask IT department to install Python
echo.
echo After installing Python, run this script again.
echo.
pause
exit /b 1

:python_found
echo Python found (%PYTHON_CMD%)
echo.

REM Run system check
echo Running system compatibility check...
echo.
%PYTHON_CMD% check_system.py
echo.

echo =========================================================
echo.
echo STARTING REMOTE CONTROL AGENT...
echo.
echo The agent will:
echo   - Connect to the remote control server
echo   - Generate a unique Session ID  
echo   - Display the Session ID for you to copy
echo   - Wait for remote connections
echo.
echo IMPORTANT: Copy the Session ID when it appears!
echo Use it at: https://web-production-463b89.up.railway.app
echo.
echo Press any key to start the agent...
pause >nul

echo.
echo Starting agent...
echo.

REM Start the agent
%PYTHON_CMD% agent.py

echo.
echo.
echo =========================================================
echo                   SESSION ENDED
echo =========================================================
echo.
echo The remote control session has ended.
echo.
echo To start a new session:
echo   - Run this script again
echo   - Or double-click "university-setup.bat"
echo.
echo TIP: You can copy this folder to a USB drive
echo      and run it on any Windows computer with Python!
echo.
pause
