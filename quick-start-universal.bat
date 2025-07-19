@echo off
title Quick Start - Remote Control Agent

REM Change to the directory where this batch file is located
cd /d "%~dp0"

REM Try to find Python
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
    goto :start_agent
)

python3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python3
    goto :start_agent
)

py --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py
    goto :start_agent
)

echo Python not found. Please run run-agent.bat for full setup.
pause
exit /b 1

:start_agent
echo Starting Remote Control Agent...
echo.

%PYTHON_CMD% agent.py

echo.
echo Agent stopped.
pause
