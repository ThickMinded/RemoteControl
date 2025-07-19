@echo off
title University Setup

echo.
echo University Computer Remote Control Setup
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Please install Python first.
    pause
    exit /b 1
)

echo Python found
echo Server: https://web-production-463b89.up.railway.app
echo.

echo Creating agent...

REM Create a temporary Python file to build the agent
echo import urllib.request, json, sys, os > build_agent.py
echo. >> build_agent.py
echo script = '''#!/usr/bin/env python3 >> build_agent.py
echo import sys, os, json, time, threading, base64, urllib.request, secrets >> build_agent.py
echo. >> build_agent.py
echo class RemoteControlAgent: >> build_agent.py
echo     def __init__(self, server_url): >> build_agent.py
echo         self.server_url = server_url.rstrip("/") >> build_agent.py
echo         self.session_id = None >> build_agent.py
echo         self.running = False >> build_agent.py
echo. >> build_agent.py
echo     def start(self): >> build_agent.py
echo         print("Remote Control Agent Starting...") >> build_agent.py
echo         print(f"Server: {self.server_url}") >> build_agent.py
echo         if self.register(): >> build_agent.py
echo             print() >> build_agent.py
echo             print("=" * 50) >> build_agent.py
echo             print(f"Session ID: {self.session_id}") >> build_agent.py
echo             print("COPY THIS SESSION ID!") >> build_agent.py
echo             print(f"Controller: {self.server_url}") >> build_agent.py
echo             print("=" * 50) >> build_agent.py
echo             print("Agent running... Press Ctrl+C to stop") >> build_agent.py
echo             self.running = True >> build_agent.py
echo             try: >> build_agent.py
echo                 while self.running: >> build_agent.py
echo                     time.sleep(1) >> build_agent.py
echo             except KeyboardInterrupt: >> build_agent.py
echo                 print("Agent stopped") >> build_agent.py
echo                 self.running = False >> build_agent.py
echo         else: >> build_agent.py
echo             print("Failed to register") >> build_agent.py
echo. >> build_agent.py
echo     def register(self): >> build_agent.py
echo         data = {"platform": sys.platform, "agent_type": "basic"} >> build_agent.py
echo         try: >> build_agent.py
echo             response = self.http_post("/api/register", data) >> build_agent.py
echo             if response and "sessionId" in response: >> build_agent.py
echo                 self.session_id = response["sessionId"] >> build_agent.py
echo                 return True >> build_agent.py
echo         except Exception as e: >> build_agent.py
echo             print(f"Registration error: {e}") >> build_agent.py
echo         try: >> build_agent.py
echo             self.session_id = secrets.token_hex(4).upper() >> build_agent.py
echo             return True >> build_agent.py
echo         except: >> build_agent.py
echo             import random >> build_agent.py
echo             self.session_id = f"{random.randint(1000, 9999):04d}" >> build_agent.py
echo             return True >> build_agent.py
echo. >> build_agent.py
echo     def http_post(self, path, data): >> build_agent.py
echo         try: >> build_agent.py
echo             json_data = json.dumps(data).encode() >> build_agent.py
echo             req = urllib.request.Request(f"{self.server_url}{path}", data=json_data, headers={"Content-Type": "application/json"}) >> build_agent.py
echo             with urllib.request.urlopen(req, timeout=10) as response: >> build_agent.py
echo                 return json.loads(response.read().decode()) >> build_agent.py
echo         except Exception as e: >> build_agent.py
echo             raise Exception(f"POST {path} failed: {e}") >> build_agent.py
echo. >> build_agent.py
echo if __name__ == "__main__": >> build_agent.py
echo     if len(sys.argv) ^< 3: >> build_agent.py
echo         print("Usage: python remote_control.py agent SERVER_URL") >> build_agent.py
echo         sys.exit(1) >> build_agent.py
echo     agent = RemoteControlAgent(sys.argv[2]) >> build_agent.py
echo     agent.start()''' >> build_agent.py
echo. >> build_agent.py
echo with open('remote_control.py', 'w') as f: >> build_agent.py
echo     f.write(script) >> build_agent.py
echo print('Agent created') >> build_agent.py

python build_agent.py
del build_agent.py

echo Agent ready
echo Starting...
echo.

python remote_control.py agent https://web-production-463b89.up.railway.app

echo.
echo Cleaning up...
del remote_control.py 2>nul

echo Session ended
pause
