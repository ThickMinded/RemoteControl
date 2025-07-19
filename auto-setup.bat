@echo off
chcp 65001 >nul
title Remote Control - Automatic Setup

echo.
echo =========================================================
echo          REMOTE CONTROL - AUTOMATIC SETUP
echo =========================================================
echo.
echo This will automatically install everything needed:
echo ✓ Python (if not installed)
echo ✓ Required packages  
echo ✓ Remote control agent
echo.
echo No admin rights required!
echo.

cd /d "%~dp0"

if not exist "agent.py" (
    echo ERROR: agent.py not found!
    pause
    exit /b 1
)

echo ✓ Found agent.py
echo.

REM Check for Python
echo Checking for Python...

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

REM Try to install Python automatically
echo Python not found. Installing automatically...
echo.

REM Method 1: Try winget (Windows 10/11)
winget --version >nul 2>&1
if not errorlevel 1 (
    echo Installing Python via Windows Package Manager...
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

REM Method 2: Microsoft Store
echo Trying Microsoft Store installation...
start ms-windows-store://pdp/?productid=9NRWMJP3717K
echo.
echo Microsoft Store opened. Please install Python 3.11
echo Press any key after Python is installed...
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

REM Method 3: Direct download
echo Downloading Python installer...
powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe' -OutFile '$env:TEMP\python.exe'; Start-Process -FilePath '$env:TEMP\python.exe' -ArgumentList '/quiet', 'InstallAllUsers=0', 'PrependPath=1' -Wait"

timeout /t 5 >nul

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

echo.
echo Could not install Python automatically.
echo Please install Python manually from: https://python.org
pause
exit /b 1

:python_found
echo ✓ Python ready: %PYTHON_CMD%
echo.

echo Installing dependencies...
%PYTHON_CMD% -m pip install --user pillow pynput --quiet --disable-pip-version-check

echo.
echo =========================================================
echo              STARTING REMOTE CONTROL
echo =========================================================
echo.
echo Look for your Session ID below:
echo.

%PYTHON_CMD% agent.py

echo.
echo Session ended. Press any key to exit...
pause >nul
