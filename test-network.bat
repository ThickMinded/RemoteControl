@echo off
chcp 65001 >nul
title Network Connection Test

echo.
echo =========================================================
echo               NETWORK CONNECTION TEST
echo =========================================================
echo.
echo Testing network connectivity for remote control setup...
echo.

REM Test basic internet connectivity
echo Testing basic internet connection...
ping google.com -n 1 >nul 2>&1
if errorlevel 1 (
    echo ❌ No internet connection detected
    echo This may be a restricted network environment
) else (
    echo ✅ Basic internet connection OK
)

echo.
echo Testing Python.org connectivity...
ping www.python.org -n 1 >nul 2>&1
if errorlevel 1 (
    echo ❌ Cannot reach python.org
    echo Python downloads will fail
) else (
    echo ✅ Can reach python.org
)

echo.
echo Testing Microsoft Store connectivity...
ping microsoft.com -n 1 >nul 2>&1
if errorlevel 1 (
    echo ❌ Cannot reach Microsoft services
) else (
    echo ✅ Microsoft services reachable
)

echo.
echo Testing our remote control server...
ping web-production-463b89.up.railway.app -n 1 >nul 2>&1
if errorlevel 1 (
    echo ❌ Cannot reach remote control server
    echo Remote control may not work
) else (
    echo ✅ Remote control server reachable
)

echo.
echo Testing PowerShell download capability...
powershell -Command "Test-NetConnection www.google.com -Port 443 -InformationLevel Quiet" >nul 2>&1
if errorlevel 1 (
    echo ❌ PowerShell network access blocked
    echo Downloads will fail
) else (
    echo ✅ PowerShell network access OK
)

echo.
echo =========================================================
echo                    RECOMMENDATIONS
echo =========================================================

REM Check if winget is available
winget --version >nul 2>&1
if errorlevel 1 (
    echo ❌ winget not available
) else (
    echo ✅ winget available - try auto-setup.bat
)

echo.
echo Based on the tests above:
echo.
echo If all tests PASS:
echo   → Use zero-install.bat or auto-setup.bat
echo.
echo If internet is BLOCKED:
echo   → Use network-restricted.bat
echo   → Try Microsoft Store installation
echo   → Ask IT department for Python installation
echo.
echo If only some sites are blocked:
echo   → Try network-restricted.bat first
echo   → Fall back to manual Python installation
echo.

pause
