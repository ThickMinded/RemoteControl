@echo off
title University Remote Control Setup

echo.
echo ========================================
echo   🖥️ University Computer Setup  
echo ========================================
echo.
echo This will connect this computer for remote control
echo No installation or admin permissions required
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not available on this system
    echo.
    echo 💡 Solutions:
    echo    1. Install Python from: https://python.org/downloads
    echo    2. Or use Microsoft Store to install Python
    echo    3. Or ask IT to install Python
    echo.
    pause
    exit /b 1
)

echo ✅ Python found
echo 📡 Server: https://web-production-463b89.up.railway.app
echo.

REM Check if we already have the full remote_control.py
if exist "remote_control.py" (
    echo ✅ Full agent script found
) else (
    echo 📥 Creating agent...
    echo ⚠️ Note: Using basic agent - limited functionality
    echo.
    
    REM Create a basic working agent that actually communicates with server
    python -c "
import urllib.request, json, sys, os

# Create the embedded agent script
script_content = '''#!/usr/bin/env python3
import sys, os, json, time, threading, base64, hashlib, secrets, urllib.request, urllib.parse, io

class RemoteControlAgent:
    def __init__(self, server_url):
        self.server_url = server_url.rstrip(\"/\")
        self.session_id = None
        self.running = False

    def start(self):
        print(\"🤖 Starting Remote Control Agent...\")
        print(f\"📡 Server: {self.server_url}\")
        
        if not self.register():
            print(\"❌ Failed to register with server\")
            return
        
        print()
        print(\"=\" * 50)
        print(f\"✅ Agent registered! Session ID: {self.session_id}\")
        print(\"📋 COPY THIS SESSION ID!\")
        print(f\"🌐 Controller URL: {self.server_url}\")
        print(\"=\" * 50)
        print()
        print(\"🔄 Agent is running... Press Ctrl+C to stop\")
        
        self.running = True
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print(\"\\n🛑 Agent stopped\")
            self.running = False

    def register(self):
        data = {
            \"platform\": sys.platform,
            \"python_version\": sys.version,
            \"agent_type\": \"basic\"
        }
        
        try:
            response = self.http_post(\"/api/register\", data)
            if response and \"sessionId\" in response:
                self.session_id = response[\"sessionId\"]
                return True
        except Exception as e:
            print(f\"Registration error: {e}\")
        
        # Fallback - generate session ID anyway but warn user
        try:
            self.session_id = secrets.token_hex(4).upper()
            print(\"⚠️ Using local session ID - may not work with web interface\")
            return True
        except:
            import random
            self.session_id = f\"{random.randint(1000, 9999):04d}\"
            print(\"⚠️ Using random session ID - may not work with web interface\")
            return True

    def http_post(self, path, data):
        try:
            json_data = json.dumps(data).encode()
            req = urllib.request.Request(
                f\"{self.server_url}{path}\",
                data=json_data,
                headers={\"Content-Type\": \"application/json\"}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode())
        except Exception as e:
            raise Exception(f\"POST {path} failed: {e}\")

if __name__ == \"__main__\":
    if len(sys.argv) < 3:
        print(\"Usage: python remote_control.py agent SERVER_URL\")
        sys.exit(1)
    agent = RemoteControlAgent(sys.argv[2])
    agent.start()
'''

with open('remote_control.py', 'w') as f:
    f.write(script_content)

print('✅ Agent script created with server communication')
"
)

echo ✅ Agent script ready
echo 🚀 Starting agent...
echo.

python remote_control.py agent https://web-production-463b89.up.railway.app

echo.
echo 🧹 Cleaning up...
del remote_control.py 2>nul

echo ✅ Session ended  
echo 💡 Run this script again to reconnect
pause
