@echo off
chcp 65001 >nul
title Performance Test - Remote Control

echo.
echo =========================================================
echo           PERFORMANCE TEST - REMOTE CONTROL
echo =========================================================
echo.
echo Testing optimized settings:
echo.

REM Check if performance config exists
if exist "config-performance.json" (
    echo ✓ Performance config found
    type config-performance.json | findstr "screen_fps\|command_check_interval"
) else (
    echo ❌ Performance config missing
)

echo.
echo Testing current settings:
echo.

python -c "
import json
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
    settings = config.get('settings', {})
    print(f'Screen FPS: {settings.get(\"screen_fps\", \"default\")}')
    print(f'Command Interval: {settings.get(\"command_check_interval\", \"default\")}ms')
    print(f'Screen Resolution: {settings.get(\"screen_width\", \"default\")}x{settings.get(\"screen_height\", \"default\")}')
    print(f'Screen Quality: {settings.get(\"screen_quality\", \"default\")}%')
except:
    print('Using default settings')
"

echo.
echo Press any key to run performance test...
pause >nul

echo.
echo Starting agent with performance monitoring...
python agent.py

pause
