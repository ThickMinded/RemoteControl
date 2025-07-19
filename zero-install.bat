@echo off
chcp 65001 >nul
title University Remote Control - Zero Installation Setup

echo.
echo =========================================================
echo     UNIVERSITY REMOTE CONTROL - ZERO INSTALLATION
echo =========================================================
echo.
echo This will automatically set up remote control with:
echo - Automatic Python installation if needed
echo - No admin permissions required  
echo - Works through university firewalls
echo - Automatic dependency installation
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
"%LOCALAPPDATA%\Programs\Python\Python311\python.exe" --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    goto :python_found
)

"%LOCALAPPDATA%\Programs\Python\Python312\python.exe" --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    goto :python_found
)

"C:\Python311\python.exe" --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD="C:\Python311\python.exe"
    goto :python_found
)

REM If no Python found - attempt automatic installation
echo.
echo Python not found - attempting automatic installation...
echo This may take a few minutes...
echo.

REM Method 1: Try winget first (modern Windows package manager)
echo Trying Windows Package Manager (winget)...
winget --version >nul 2>&1
if not errorlevel 1 (
    echo Installing Python via winget...
    winget install Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements >nul 2>&1
    if not errorlevel 1 (
        echo ✓ Python installed via winget!
        timeout /t 3 >nul
        python --version >nul 2>&1
        if not errorlevel 1 (
            set PYTHON_CMD=python
            goto :python_found
        )
        py --version >nul 2>&1
        if not errorlevel 1 (
            set PYTHON_CMD=py
            goto :python_found
        )
    )
)

REM Method 2: Try Microsoft Store
echo winget not available. Trying Microsoft Store...
start ms-windows-store://pdp/?productid=9NRWMJP3717K
echo.
echo Microsoft Store opened for Python installation.
echo Please install Python and press any key when done...
pause >nul

python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
    goto :python_found
)

py --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py
    goto :python_found
)

REM Method 3: Try PowerShell download with better error handling
echo Trying direct download...
powershell -ExecutionPolicy Bypass -Command "& { try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Write-Host 'Testing connection...'; Test-NetConnection www.python.org -Port 443 -InformationLevel Quiet; if ($?) { Write-Host 'Connection OK, downloading...'; $url = 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe'; $output = '$env:TEMP\python-installer.exe'; Invoke-WebRequest -Uri $url -OutFile $output -UseBasicParsing -TimeoutSec 30; if (Test-Path $output) { Write-Host 'Download completed, installing...'; Start-Process -FilePath $output -ArgumentList '/quiet', 'InstallAllUsers=0', 'PrependPath=1', 'Include_test=0', 'Include_launcher=1' -Wait; Write-Host 'Installation completed' } else { Write-Host 'Download failed - file not found' } } else { Write-Host 'Cannot reach python.org - network blocked' } } catch { Write-Host 'Error:' $_.Exception.Message } }"

REM Wait a moment for installation to complete
timeout /t 5 >nul

REM Check if Python is now available
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
    echo ✓ Python installed and configured successfully!
    goto :python_found
)

py --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py
    echo ✓ Python installed and configured successfully!
    goto :python_found
)

"%LOCALAPPDATA%\Programs\Python\Python311\python.exe" --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    echo ✓ Python found at installation path!
    goto :python_found
)

REM Method 4: Check if Python is available from Windows Apps folder (Microsoft Store install location)
"%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe" --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD="%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe"
    echo ✓ Python found in Windows Apps!
    goto :python_found
)

REM Final method: Provide manual instructions with specific network troubleshooting
echo.
echo ================================================================
echo  AUTOMATIC INSTALLATION FAILED - NETWORK RESTRICTIONS DETECTED
echo ================================================================
echo.
echo Your network appears to block external downloads.
echo This is common in university/corporate environments.
echo.
echo SOLUTIONS:
echo.
echo 1. EASIEST - Use Microsoft Store (usually allowed):
echo    - Press Windows key, search "Microsoft Store"
echo    - Search for "Python 3.11"
echo    - Click "Get" or "Install"
echo.
echo 2. Ask IT Department:
echo    - Request Python 3.11 installation
echo    - Show them: https://www.python.org/downloads/
echo.
echo 3. Use University Computers with Python:
echo    - Many computer labs have Python pre-installed
echo    - Try running: python --version in Command Prompt
echo.
echo 4. Portable Python (if USB allowed):
echo    - Download on personal computer: 
echo      https://www.python.org/downloads/windows/
echo    - Look for "Windows embeddable package"
echo    - Copy to USB and run from there
echo.
echo After getting Python installed, run this script again.
echo.
echo Press any key to open Microsoft Store as a backup...
pause >nul
start ms-windows-store://search/?query=python
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
    echo Warning: Failed to install pillow - trying alternative method...
    %PYTHON_CMD% -m pip install pillow --quiet --disable-pip-version-check --upgrade
    if errorlevel 1 (
        echo Warning: Pillow installation failed - screen capture may be limited
    ) else (
        echo ✓ Pillow installed/upgraded successfully (system-wide)
    )
) else (
    echo ✓ Pillow installed/upgraded successfully
)

echo.
echo Installing pynput for remote control...
%PYTHON_CMD% -m pip install --user pynput --quiet --disable-pip-version-check --upgrade
if errorlevel 1 (
    echo Warning: Failed to install pynput - trying alternative method...
    %PYTHON_CMD% -m pip install pynput --quiet --disable-pip-version-check --upgrade
    if errorlevel 1 (
        echo Warning: pynput installation failed - remote control may be limited
    ) else (
        echo ✓ pynput installed/upgraded successfully (system-wide)
    )
) else (
    echo ✓ pynput installed/upgraded successfully
)

echo.
echo =========================================================
echo        HIGH-PERFORMANCE SETUP COMPLETE - STARTING AGENT
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
echo   - Display the Session ID prominently
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
echo TIP: This script can be copied to any Windows computer
echo      and will automatically install everything needed!
echo.
pause
