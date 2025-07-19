@echo off
chcp 65001 >nul
title Remote Control - High Performance Mode

echo.
echo =========================================================
echo         REMOTE CONTROL - HIGH PERFORMANCE MODE
echo =========================================================
echo.
echo This version is optimized for better real-time performance:
echo ✓ 15 FPS screen capture (vs 1 FPS default)
echo ✓ Higher resolution (1280x720)
echo ✓ Faster command processing (30ms vs 100ms)
echo ✓ Change detection (only sends frames when screen changes)
echo ✓ Reduced delays and optimized compression
echo.

cd /d "%~dp0"

if not exist "agent.py" (
    echo ERROR: agent.py not found!
    pause
    exit /b 1
)

echo ✓ Found agent.py
echo.

REM Copy performance config
if exist "config-performance.json" (
    copy "config-performance.json" "config.json" >nul
    echo ✓ Performance configuration loaded
) else (
    echo Warning: Performance config not found, using defaults
)

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    py --version >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Python not found! Please install Python first.
        echo Try running: run-agent.bat for automatic installation
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=py
    )
) else (
    set PYTHON_CMD=python
)

echo ✓ Python ready: %PYTHON_CMD%
echo.

echo Installing/updating dependencies for best performance...
%PYTHON_CMD% -m pip install --user pillow pynput --quiet --disable-pip-version-check --upgrade

echo.
echo =========================================================
echo            HIGH PERFORMANCE AGENT STARTING
echo =========================================================
echo.
echo Performance optimizations active:
echo - 15 FPS screen capture
echo - 1280x720 resolution  
echo - 30ms command response time
echo - Smart change detection
echo.
echo Look for your Session ID below:
echo.

%PYTHON_CMD% agent.py

echo.
echo Session ended. Press any key to exit...
pause >nul
