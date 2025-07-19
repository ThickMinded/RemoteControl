@echo off
chcp 65001 >nul
title Remote Control - Network Restricted Setup

echo.
echo =========================================================
echo      REMOTE CONTROL - NETWORK RESTRICTED SETUP
echo =========================================================
echo.
echo This version works in restricted network environments
echo like universities and corporate networks.
echo.

cd /d "%~dp0"

if not exist "agent.py" (
    echo ERROR: agent.py not found!
    pause
    exit /b 1
)

echo ✓ Found agent.py
echo.

REM Check for Python in all possible locations
echo Checking for Python installation...

REM Standard PATH locations
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

python3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python3
    goto :python_found
)

REM Microsoft Store installation location
"%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe" --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD="%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe"
    goto :python_found
)

REM User installations
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

"%LOCALAPPDATA%\Programs\Python\Python310\python.exe" --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    goto :python_found
)

REM System-wide installations
"C:\Python311\python.exe" --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD="C:\Python311\python.exe"
    goto :python_found
)

"C:\Python312\python.exe" --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD="C:\Python312\python.exe"
    goto :python_found
)

REM Anaconda/Miniconda locations
"%USERPROFILE%\anaconda3\python.exe" --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD="%USERPROFILE%\anaconda3\python.exe"
    goto :python_found
)

"%USERPROFILE%\miniconda3\python.exe" --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD="%USERPROFILE%\miniconda3\python.exe"
    goto :python_found
)

REM Portable Python in current directory
if exist "python\python.exe" (
    "python\python.exe" --version >nul 2>&1
    if not errorlevel 1 (
        set PYTHON_CMD="python\python.exe"
        goto :python_found
    )
)

REM Check removable drives for portable Python
for %%d in (D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
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

REM Python not found - provide offline installation guide
echo.
echo ================================================================
echo            PYTHON NOT FOUND - OFFLINE INSTALLATION GUIDE
echo ================================================================
echo.
echo Python is required but not found on this system.
echo Since network access appears restricted, here are offline options:
echo.
echo METHOD 1 - Microsoft Store (Usually Works):
echo   1. Press Windows key + R
echo   2. Type: ms-windows-store://search/?query=python
echo   3. Press Enter
echo   4. Install "Python 3.11" or newer
echo   5. Run this script again
echo.
echo METHOD 2 - Portable Python (No Installation):
echo   1. On a computer with internet access:
echo      - Go to: https://www.python.org/downloads/windows/
echo      - Download "Windows embeddable package (64-bit)"
echo   2. Extract to USB drive as "Python" folder
echo   3. Put this script in same folder as the Python folder
echo   4. Run this script again
echo.
echo METHOD 3 - Ask IT Department:
echo   - Request Python 3.11+ installation
echo   - Mention it's for educational/development purposes
echo.
echo METHOD 4 - Use Lab Computers:
echo   - Many university computer labs have Python pre-installed
echo   - Try this script on different computers
echo.
echo Attempting to open Microsoft Store...
start ms-windows-store://search/?query=python >nul 2>&1
echo.
pause
exit /b 1

:python_found
echo ✓ Python ready: %PYTHON_CMD%

REM Get Python version
for /f "tokens=2" %%i in ('%PYTHON_CMD% --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✓ Python version: %PYTHON_VERSION%
echo.

REM Try to install dependencies
echo Installing dependencies (this may fail in restricted networks)...

%PYTHON_CMD% -m pip install --user pillow --quiet --disable-pip-version-check >nul 2>&1
if errorlevel 1 (
    echo Warning: Could not install pillow - using basic screen capture
) else (
    echo ✓ Pillow installed
)

%PYTHON_CMD% -m pip install --user pynput --quiet --disable-pip-version-check >nul 2>&1
if errorlevel 1 (
    echo Warning: Could not install pynput - limited remote control
) else (
    echo ✓ pynput installed
)

echo.
echo =========================================================
echo              STARTING REMOTE CONTROL
echo =========================================================
echo.
echo Looking for your Session ID below:
echo.

%PYTHON_CMD% agent.py

echo.
echo Session ended. Press any key to exit...
pause >nul
