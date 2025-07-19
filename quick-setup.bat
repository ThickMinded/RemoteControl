@echo off
REM ============================================================================
REM Quick Remote Control Setup - University Friendly
REM ============================================================================
REM Simple one-click setup for university computers
REM No admin rights, no installation, no configuration needed
REM ============================================================================

title Quick Remote Setup

echo.
echo ===============================
echo   🎯 Quick Remote Setup
echo ===============================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found
    echo.
    echo 📋 Please:
    echo   1. Go to: https://web-production-463b89.up.railway.app
    echo   2. Follow manual setup instructions
    echo.
    pause
    exit /b 1
)

echo ✅ Python found
echo 📥 Downloading agent...

REM Download and run in one command
python -c "
import urllib.request, tempfile, subprocess, sys, os

server_url = 'https://web-production-463b89.up.railway.app'
print(f'📡 Connecting to: {server_url}')

try:
    # Download agent script
    with urllib.request.urlopen(f'{server_url}/remote_control.py') as response:
        script_content = response.read().decode()
    
    # Save temporarily
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(script_content)
        temp_path = f.name
    
    print('✅ Agent downloaded')
    print('🚀 Starting agent...')
    print()
    print('===============================')
    print('   📋 IMPORTANT: COPY THE SESSION ID!')
    print('===============================')
    print()
    
    # Run agent
    subprocess.run([sys.executable, temp_path, 'agent', server_url])
    
    # Cleanup
    os.unlink(temp_path)
    
except Exception as e:
    print(f'❌ Error: {e}')
    print()
    print('💡 Manual method:')
    print('  1. Go to: https://web-production-463b89.up.railway.app')
    print('  2. Download remote_control.py')
    print('  3. Run: python remote_control.py agent https://web-production-463b89.up.railway.app')
"

echo.
echo ✅ Session ended
pause
