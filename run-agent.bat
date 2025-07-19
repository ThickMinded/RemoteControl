@echo off
chcp 65001 >nul
title University Remote Control - Universal Setup

echo.
echo =========================================================
echo        UNIVERSITY REMOTE CONTROL - UNIVERSAL SETUP
echo =========================================================
echo.
echo This will set up remote control on ANY Windows computer
echo - No installation required
echo - No admin permissions needed  
echo - Works through university firewalls
echo - Automatically installs dependencies
echo - HIGH PERFORMANCE MODE (15 FPS, 1280x720, fast response)
echo.

REM Change to the directory where this batch file is located
cd /d "%~dp0"

echo Current directory: %CD%
echo.

REM Check if required files exist
if not exist "agent.py" (
    echo ERROR: agent.py not found in current directory
    echo Please ensure this batch file is in the same folder as agent.py
    echo.
    pause
    exit /b 1
)

echo ✓ Found agent.py
echo.

REM Load high-performance configuration
if exist "config-performance.json" (
    copy "config-performance.json" "config.json" >nul 2>&1
    echo ✓ High-performance configuration loaded (15 FPS, 1280x720)
) else (
    echo ✓ Using built-in high-performance settings
)
echo.

REM Check if Python is available
echo Checking for Python installation...

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

py -3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py -3
    goto :python_found
)

REM Try Python from common installation paths
"C:\Python39\python.exe" --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD="C:\Python39\python.exe"
    goto :python_found
)

"C:\Python310\python.exe" --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD="C:\Python310\python.exe"
    goto :python_found
)

"C:\Python311\python.exe" --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD="C:\Python311\python.exe"
    goto :python_found
)

"%LOCALAPPDATA%\Programs\Python\Python39\python.exe" --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python39\python.exe"
    goto :python_found
)

"%LOCALAPPDATA%\Programs\Python\Python310\python.exe" --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    goto :python_found
)

"%LOCALAPPDATA%\Programs\Python\Python311\python.exe" --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    goto :python_found
)

REM Try newer Python versions
"%LOCALAPPDATA%\Programs\Python\Python312\python.exe" --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    goto :python_found
)

REM Try portable Python in current directory
if exist "python\python.exe" (
    "python\python.exe" --version >nul 2>&1
    if not errorlevel 1 (
        set PYTHON_CMD="python\python.exe"
        goto :python_found
    )
)

REM Try Python on USB drives (common portable locations)
for %%d in (D E F G H I J K) do (
    if exist "%%d:\Python\python.exe" (
        "%%d:\Python\python.exe" --version >nul 2>&1
        if not errorlevel 1 (
            set PYTHON_CMD="%%d:\Python\python.exe"
            goto :python_found
        )
    )
    if exist "%%d:\PortablePython\python.exe" (
        "%%d:\PortablePython\python.exe" --version >nul 2>&1
        if not errorlevel 1 (
            set PYTHON_CMD="%%d:\PortablePython\python.exe"
            goto :python_found
        )
    )
)

REM If no Python found - attempt automatic installation
echo.
echo Python not found - attempting automatic installation...
echo.

REM Try to install Python from Microsoft Store (Windows 10/11)
echo Trying Microsoft Store Python installation...
start /wait ms-windows-store://pdp/?productid=9NRWMJP3717K
timeout /t 3 >nul

REM Check if Python is now available after Store installation
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
    echo ✓ Python installed successfully from Microsoft Store!
    goto :python_found
)

py --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py
    echo ✓ Python installed successfully from Microsoft Store!
    goto :python_found
)

REM If Store installation failed, try downloading Python directly
echo Microsoft Store installation not available or failed.
echo Attempting to download Python installer...

REM Create temp directory for Python installer
if not exist "%TEMP%\RemoteControlSetup" mkdir "%TEMP%\RemoteControlSetup"
cd /d "%TEMP%\RemoteControlSetup"

REM Download Python installer using PowerShell
echo Downloading Python 3.11 installer...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe' -OutFile 'python-installer.exe'}" 2>nul

if exist "python-installer.exe" (
    echo Python installer downloaded successfully.
    echo Installing Python... This may take a few minutes.
    echo.
    
    REM Install Python silently with pip and add to PATH
    start /wait python-installer.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 Include_launcher=1
    
    echo Python installation completed.
    echo.
    
    REM Refresh environment variables
    call refreshenv 2>nul
    
    REM Check if Python is now available
    python --version >nul 2>&1
    if not errorlevel 1 (
        set PYTHON_CMD=python
        echo ✓ Python installed and configured successfully!
        cd /d "%~dp0"
        goto :python_found
    )
    
    py --version >nul 2>&1
    if not errorlevel 1 (
        set PYTHON_CMD=py
        echo ✓ Python installed and configured successfully!
        cd /d "%~dp0"
        goto :python_found
    )
    
    REM Try specific path after installation
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" --version >nul 2>&1
    if not errorlevel 1 (
        set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
        echo ✓ Python found at local installation path!
        cd /d "%~dp0"
        goto :python_found
    )
)

REM If all automatic installation attempts failed
cd /d "%~dp0"
echo.
echo ================================================================
echo  AUTOMATIC PYTHON INSTALLATION FAILED
echo ================================================================
echo.
echo The system could not automatically install Python.
echo This may be due to:
echo   - Network restrictions
echo   - Group policy restrictions
echo   - Insufficient permissions
echo.
echo MANUAL INSTALLATION OPTIONS:
echo   1. Download from: https://python.org/downloads
echo   2. Use Microsoft Store: Search "Python 3.11"
echo   3. Ask IT department to install Python
echo   4. Try portable Python from: https://www.python.org/downloads/windows/
echo   5. Use Python from USB drive if available
echo.
echo After installing Python manually, run this script again.
echo.
pause
exit /b 1

:python_found
echo ✓ Python found: %PYTHON_CMD%

REM Get Python version
for /f "tokens=2" %%i in ('%PYTHON_CMD% --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✓ Python version: %PYTHON_VERSION%
echo.

REM Install required dependencies
echo Installing/upgrading dependencies for optimal performance...
echo.

echo Installing PIL/Pillow for screen capture...
%PYTHON_CMD% -m pip install --user pillow --quiet --disable-pip-version-check --upgrade
if errorlevel 1 (
    echo Warning: Failed to install pillow - screen capture may not work
    echo This is okay, the agent will still run in basic mode
) else (
    echo ✓ Pillow installed/upgraded successfully
)

echo.
echo Installing pynput for remote control...
%PYTHON_CMD% -m pip install --user pynput --quiet --disable-pip-version-check --upgrade
if errorlevel 1 (
    echo Warning: Failed to install pynput - remote control may not work
    echo This is okay, the agent will still run for screen sharing only
) else (
    echo ✓ pynput installed/upgraded successfully
)

echo.
echo =========================================================
echo              HIGH-PERFORMANCE SETUP COMPLETE
echo =========================================================

REM Run system check if available
if exist "check_system.py" (
    echo.
    echo Running system compatibility check...
    echo.
    %PYTHON_CMD% check_system.py
    echo.
)

echo =========================================================
echo.
echo STARTING HIGH-PERFORMANCE REMOTE CONTROL AGENT...
echo.
echo Performance optimizations active:
echo   - 15 FPS screen capture (vs 1 FPS standard)
echo   - 1280x720 resolution (vs 800x600 standard)
echo   - 50ms command response time (vs 100ms standard)
echo   - Smart change detection (only sends when screen changes)
echo   - Optimized compression and reduced delays
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
echo =========================================================
echo                  WATCH FOR SESSION ID!
echo =========================================================
echo.

REM Start the agent
%PYTHON_CMD% agent.py

echo.
echo.
echo ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
echo ★                                                                     ★
echo ★  Agent finished! The Session ID was displayed above.               ★
echo ★  Look for lines containing "Session ID:" in the output above.       ★
echo ★                                                                     ★
echo ★  Use it at: https://web-production-463b89.up.railway.app           ★
echo ★                                                                     ★
echo ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
echo.
echo Press any key to close this window...
pause >nul

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
echo   - Or double-click this batch file
echo.
echo TIP: You can copy this entire folder to a USB drive
echo      and run it on any Windows computer with Python!
echo.
pause
