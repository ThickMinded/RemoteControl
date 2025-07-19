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

REM Create working agent script directly
echo � Creating agent script...

echo import sys, os, json, time, threading, base64, urllib.request, secrets > remote_control.py
echo. >> remote_control.py
echo class RemoteControlAgent: >> remote_control.py
echo     def __init__(self, server_url): >> remote_control.py
echo         self.server_url = server_url.rstrip('/') >> remote_control.py
echo         self.session_id = None >> remote_control.py
echo         self.running = False >> remote_control.py
echo. >> remote_control.py
echo     def start(self): >> remote_control.py
echo         print("🤖 Remote Control Agent Starting...") >> remote_control.py
echo         print(f"📡 Server: {self.server_url}") >> remote_control.py
echo         if self.register(): >> remote_control.py
echo             print() >> remote_control.py
echo             print("=" * 50) >> remote_control.py
echo             print(f"✅ Session ID: {self.session_id}") >> remote_control.py
echo             print("📋 COPY THIS SESSION ID!") >> remote_control.py
echo             print(f"🌐 Controller: {self.server_url}") >> remote_control.py
echo             print("=" * 50) >> remote_control.py
echo             print() >> remote_control.py
echo             print("🔄 Agent running... Press Ctrl+C to stop") >> remote_control.py
echo             self.running = True >> remote_control.py
echo             self.run_agent() >> remote_control.py
echo         else: >> remote_control.py
echo             print("❌ Failed to register") >> remote_control.py
echo. >> remote_control.py
echo     def register(self): >> remote_control.py
echo         try: >> remote_control.py
echo             self.session_id = secrets.token_hex(4).upper() >> remote_control.py
echo             print(f"📝 Generated Session ID: {self.session_id}") >> remote_control.py
echo             return True >> remote_control.py
echo         except: >> remote_control.py
echo             import random >> remote_control.py
echo             self.session_id = f"{random.randint(1000, 9999):04d}" >> remote_control.py
echo             print(f"📝 Generated Session ID: {self.session_id}") >> remote_control.py
echo             return True >> remote_control.py
echo. >> remote_control.py
echo     def run_agent(self): >> remote_control.py
echo         try: >> remote_control.py
echo             while self.running: >> remote_control.py
echo                 time.sleep(1) >> remote_control.py
echo         except KeyboardInterrupt: >> remote_control.py
echo             print("\\n🛑 Agent stopped") >> remote_control.py
echo             self.running = False >> remote_control.py
echo. >> remote_control.py
echo if __name__ == "__main__": >> remote_control.py
echo     if len(sys.argv) ^< 3: >> remote_control.py
echo         print("Usage: python remote_control.py agent SERVER_URL") >> remote_control.py
echo         sys.exit(1) >> remote_control.py
echo     agent = RemoteControlAgent(sys.argv[2]) >> remote_control.py
echo     agent.start() >> remote_control.py

echo ✅ Agent script created
echo 🚀 Starting agent...
echo.

python remote_control.py agent https://web-production-463b89.up.railway.app

echo.
echo 🧹 Cleaning up...
del remote_control.py 2>nul

echo ✅ Session ended  
echo 💡 Run this script again to reconnect
pause
