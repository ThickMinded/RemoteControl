@echo off
title Quick University Setup

echo.
echo ================================
echo   🖥️ Quick Remote Setup
echo ================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python first.
    pause
    exit /b 1
)

echo ✅ Python found
echo 📡 Server: https://web-production-463b89.up.railway.app
echo.

REM Create a temporary Python script and run it
echo import urllib.request, tempfile, subprocess, sys, os > temp_setup.py
echo server_url = 'https://web-production-463b89.up.railway.app' >> temp_setup.py
echo print('📥 Downloading agent...') >> temp_setup.py
echo try: >> temp_setup.py
echo     with urllib.request.urlopen(server_url + '/remote_control.py') as response: >> temp_setup.py
echo         content = response.read().decode() >> temp_setup.py
echo     with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f: >> temp_setup.py
echo         f.write(content) >> temp_setup.py
echo         temp_path = f.name >> temp_setup.py
echo     print('✅ Downloaded! Starting agent...') >> temp_setup.py
echo     print() >> temp_setup.py
echo     print('=' * 50) >> temp_setup.py
echo     print('📋 COPY THE SESSION ID BELOW!') >> temp_setup.py
echo     print('=' * 50) >> temp_setup.py
echo     subprocess.run([sys.executable, temp_path, 'agent', server_url]) >> temp_setup.py
echo     os.unlink(temp_path) >> temp_setup.py
echo except Exception as e: >> temp_setup.py
echo     print(f'❌ Error: {e}') >> temp_setup.py
echo     print('💡 Go to:', server_url, 'and download manually') >> temp_setup.py

python temp_setup.py
del temp_setup.py

echo.
echo ✅ Setup complete
pause
