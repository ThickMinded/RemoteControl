@echo off
chcp 65001 >nul
title University Remote Control - SESSION ID DEMO

echo.
echo =========================================================
echo           UNIVERSITY REMOTE CONTROL
echo =========================================================
echo.
echo Testing Session ID visibility...
echo.

cd "c:\Users\Fahd6\Desktop\remoteControl project\cloud test\RemoteControl"

echo Starting agent for 10 seconds to show Session ID...
echo.

timeout /t 2 >nul

REM Start agent briefly
python agent.py &

echo.
echo The Session ID should be clearly visible above.
echo Copy it and use it at: https://web-production-463b89.up.railway.app
echo.
echo Press any key to continue...
pause >nul

REM Stop any running python processes
taskkill /f /im python.exe >nul 2>&1

echo.
echo Demo complete. Session ID was visible!
pause
