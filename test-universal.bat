@echo off
echo.
echo =========================================================
echo           TESTING UNIVERSAL BATCH FILE
echo =========================================================
echo.
echo This demonstrates that the batch file works from any location
echo by using relative paths instead of absolute paths.
echo.

echo Current directory: %CD%
echo Batch file location: %~dp0
echo.

REM Show that we can run from any directory
echo Testing directory independence...
cd %TEMP%
echo Now in: %CD%
echo.

echo Running agent from original location...
call "%~dp0run-agent.bat"

echo.
echo Test complete!
pause
