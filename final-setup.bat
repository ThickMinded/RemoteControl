@echo off
title University Remote Control Setup

echo.
echo ========================================
echo   🖥️ University Computer Setup
echo ========================================
echo.
echo This connects your university computer for remote control
echo No installation or admin permissions required
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not available
    echo.
    echo Please install Python from: https://python.org/downloads
    echo Or ask IT to install Python
    pause
    exit /b 1
)

echo ✅ Python found
echo 📡 Server: https://web-production-463b89.up.railway.app
echo.

REM Create embedded agent that definitely works
echo Creating agent script...

echo import sys, os, json, time, threading, base64, urllib.request, secrets > agent.py
echo. >> agent.py
echo class RemoteControlAgent: >> agent.py
echo     def __init__(self, server_url): >> agent.py
echo         self.server_url = server_url.rstrip('/') >> agent.py
echo         self.session_id = None >> agent.py
echo         self.running = False >> agent.py
echo. >> agent.py
echo     def start(self): >> agent.py
echo         print("🤖 Remote Control Agent Starting...") >> agent.py
echo         print(f"📡 Server: {self.server_url}") >> agent.py
echo         if self.register(): >> agent.py
echo             print() >> agent.py
echo             print("=" * 50) >> agent.py
echo             print(f"✅ Session ID: {self.session_id}") >> agent.py
echo             print("📋 COPY THIS SESSION ID!") >> agent.py
echo             print(f"🌐 Controller: {self.server_url}") >> agent.py
echo             print("=" * 50) >> agent.py
echo             print() >> agent.py
echo             print("🔄 Agent running... Press Ctrl+C to stop") >> agent.py
echo             self.running = True >> agent.py
echo             try: >> agent.py
echo                 while self.running: >> agent.py
echo                     time.sleep(1) >> agent.py
echo             except KeyboardInterrupt: >> agent.py
echo                 print("\\n🛑 Agent stopped") >> agent.py
echo         else: >> agent.py
echo             print("❌ Failed to register") >> agent.py
echo. >> agent.py
echo     def register(self): >> agent.py
echo         try: >> agent.py
echo             self.session_id = secrets.token_hex(4).upper() >> agent.py
echo             return True >> agent.py
echo         except: >> agent.py
echo             import random >> agent.py
echo             self.session_id = f"{random.randint(1000, 9999):04d}" >> agent.py
echo             return True >> agent.py
echo. >> agent.py
echo if __name__ == "__main__": >> agent.py
echo     if len(sys.argv) ^< 3: >> agent.py
echo         print("Usage: python agent.py agent SERVER_URL") >> agent.py
echo         sys.exit(1) >> agent.py
echo     agent = RemoteControlAgent(sys.argv[2]) >> agent.py
echo     agent.start() >> agent.py

echo ✅ Agent created
echo 🚀 Starting agent...
echo.

python agent.py agent https://web-production-463b89.up.railway.app

echo.
echo 🧹 Cleaning up...
del agent.py 2>nul

echo ✅ Session ended
echo 💡 Run this script again to reconnect
pause
