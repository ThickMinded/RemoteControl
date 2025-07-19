#!/usr/bin/env python3
"""
Universal Remote Control System - Single Python Script
Zero-installation remote control for university environments.

Usage:
    python remote_control.py server [PORT]             # Start server
    python remote_control.py agent SERVER_URL          # Start agent
"""

import sys
import os
import json
import time
import threading
import base64
import hashlib
import secrets
import urllib.request
import urllib.parse
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import socketserver
from datetime import datetime, timedelta
import queue
import io

# Try to import optional dependencies with fallbacks
try:
    import PIL.ImageGrab as ImageGrab
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    # Import pynput for mouse and keyboard control
    import pynput.mouse as pynput_mouse
    import pynput.keyboard as pynput_keyboard
    mouse = pynput_mouse
    keyboard = pynput_keyboard
    HAS_PYNPUT = True
except ImportError:
    HAS_PYNPUT = False


class RemoteControlServer:
    """HTTP-based server for remote control coordination"""
    
    def __init__(self, port=8080):
        self.port = port
        self.sessions = {}
        self.command_queues = {}
        self.screen_data = {}
        
    def start(self):
        """Start the HTTP server"""
        handler = self.create_handler()
        with HTTPServer(('', self.port), handler) as httpd:
            print(f"🌐 Remote Control Server started on port {self.port}")
            print(f"📱 Web interface: http://localhost:{self.port}")
            print(f"🖥️  Agent URL: http://localhost:{self.port}")
            print("Press Ctrl+C to stop")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n🛑 Server stopped")
    
    def create_handler(self):
        """Create HTTP request handler with server reference"""
        server_ref = self
        
        class RequestHandler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                """Suppress default logging"""
                pass
                
            def do_GET(self):
                """Handle GET requests"""
                parsed = urlparse(self.path)
                path = parsed.path
                query = parse_qs(parsed.query)
                
                if path == '/':
                    self.serve_web_interface()
                elif path == '/api/sessions':
                    self.api_get_sessions()
                elif path.startswith('/api/commands/'):
                    session_id = path.split('/')[-1]
                    self.api_get_commands(session_id)
                elif path.startswith('/api/screen/'):
                    session_id = path.split('/')[-1]
                    self.api_get_screen(session_id)
                else:
                    self.send_error(404)
            
            def do_POST(self):
                """Handle POST requests"""
                parsed = urlparse(self.path)
                path = parsed.path
                
                if path == '/api/register':
                    self.api_register()
                elif path == '/api/screen':
                    self.api_post_screen()
                elif path == '/api/command':
                    self.api_post_command()
                else:
                    self.send_error(404)
            
            def serve_web_interface(self):
                """Serve the web-based controller interface"""
                html = self.get_web_interface_html()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(html.encode())
            
            def api_get_sessions(self):
                """API: Get list of active sessions"""
                sessions_list = []
                current_time = time.time()
                
                # Clean up old sessions (older than 30 minutes)
                expired_sessions = []
                for session_id, session_data in server_ref.sessions.items():
                    if current_time - session_data.get('last_seen', 0) > 1800:  # 30 minutes
                        expired_sessions.append(session_id)
                
                for session_id in expired_sessions:
                    if session_id in server_ref.sessions:
                        del server_ref.sessions[session_id]
                    if session_id in server_ref.command_queues:
                        del server_ref.command_queues[session_id]
                    if session_id in server_ref.screen_data:
                        del server_ref.screen_data[session_id]
                
                # Return active sessions
                for session_id, session_data in server_ref.sessions.items():
                    sessions_list.append({
                        'sessionId': session_id,
                        'platform': session_data.get('platform', 'unknown'),
                        'lastSeen': session_data.get('last_seen', 0),
                        'hasScreen': session_id in server_ref.screen_data
                    })
                
                self.send_json_response(sessions_list)
            
            def api_get_commands(self, session_id):
                """API: Get pending commands for a session"""
                if session_id not in server_ref.command_queues:
                    server_ref.command_queues[session_id] = []
                
                commands = server_ref.command_queues[session_id].copy()
                server_ref.command_queues[session_id].clear()  # Clear after reading
                
                self.send_json_response(commands)
            
            def api_get_screen(self, session_id):
                """API: Get latest screen data for a session (optimized)"""
                if session_id in server_ref.screen_data:
                    screen_info = server_ref.screen_data[session_id]
                    
                    # Add caching headers for better performance
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Cache-Control', 'no-cache, must-revalidate')
                    self.send_header('Pragma', 'no-cache')
                    self.end_headers()
                    
                    # Send response
                    response = json.dumps(screen_info).encode('utf-8')
                    self.wfile.write(response)
                else:
                    self.send_json_response({'error': 'No screen data available', 'data': None})
            
            def api_register(self):
                """API: Register a new agent session"""
                try:
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length).decode()
                    data = json.loads(post_data)
                    
                    # Generate session ID
                    session_id = secrets.token_hex(4).upper()
                    
                    # Store session info
                    server_ref.sessions[session_id] = {
                        'platform': data.get('platform', 'unknown'),
                        'agent_type': data.get('agent_type', 'basic'),
                        'registered_at': time.time(),
                        'last_seen': time.time()
                    }
                    
                    # Initialize command queue
                    server_ref.command_queues[session_id] = []
                    
                    response = {'sessionId': session_id, 'status': 'registered'}
                    self.send_json_response(response)
                    
                    print(f"🤖 Agent registered: {session_id} ({data.get('platform', 'unknown')})")
                    
                except Exception as e:
                    self.send_json_response({'error': str(e)}, status=400)
            
            def api_post_screen(self):
                """API: Receive screen data from agent"""
                try:
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length).decode()
                    data = json.loads(post_data)
                    
                    session_id = data.get('sessionId')
                    if not session_id:
                        self.send_json_response({'error': 'Missing sessionId'}, status=400)
                        return
                    
                    # Update last seen time
                    if session_id in server_ref.sessions:
                        server_ref.sessions[session_id]['last_seen'] = time.time()
                    
                    # Store screen data
                    server_ref.screen_data[session_id] = {
                        'data': data.get('data'),
                        'timestamp': data.get('timestamp', time.time() * 1000),
                        'received_at': time.time() * 1000
                    }
                    
                    self.send_json_response({'status': 'received'})
                    
                except Exception as e:
                    self.send_json_response({'error': str(e)}, status=400)
            
            def api_post_command(self):
                """API: Send command to agent"""
                try:
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length).decode()
                    data = json.loads(post_data)
                    
                    session_id = data.get('sessionId')
                    if not session_id or session_id not in server_ref.sessions:
                        self.send_json_response({'error': 'Invalid session'}, status=400)
                        return
                    
                    # Add command to queue
                    if session_id not in server_ref.command_queues:
                        server_ref.command_queues[session_id] = []
                    
                    command = {
                        'type': data.get('type'),
                        'action': data.get('action'),
                        'x': data.get('x'),
                        'y': data.get('y'),
                        'button': data.get('button'),
                        'key': data.get('key'),
                        'deltaY': data.get('deltaY'),
                        'timestamp': time.time() * 1000
                    }
                    
                    server_ref.command_queues[session_id].append(command)
                    
                    self.send_json_response({'status': 'queued'})
                    
                except Exception as e:
                    self.send_json_response({'error': str(e)}, status=400)
            
            def send_json_response(self, data, status=200):
                """Send JSON response"""
                self.send_response(status)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())
            
            def get_web_interface_html(self):
                """Generate the web interface HTML"""
                return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>University Remote Control</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 30px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }
        .status {
            padding: 15px;
            margin: 20px 0;
            border-radius: 8px;
            text-align: center;
        }
        .status.connected {
            background: rgba(46, 204, 113, 0.2);
            border: 1px solid #2ecc71;
        }
        .status.disconnected {
            background: rgba(231, 76, 60, 0.2);
            border: 1px solid #e74c3c;
        }
        .controls {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }
        .control-panel {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 20px;
        }
        .control-panel h3 {
            margin-top: 0;
            color: #fff;
        }
        input, button, select {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: none;
            border-radius: 6px;
            font-size: 16px;
        }
        input {
            background: rgba(255, 255, 255, 0.9);
            color: #333;
        }
        button {
            background: #3498db;
            color: white;
            cursor: pointer;
            font-weight: bold;
            transition: background 0.3s;
        }
        button:hover {
            background: #2980b9;
        }
        button:disabled {
            background: #7f8c8d;
            cursor: not-allowed;
        }
        .screen-container {
            margin: 20px 0;
            text-align: center;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            padding: 20px;
        }
        #screen {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
            cursor: crosshair;
        }
        .sessions-list {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }
        .session-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            margin: 5px 0;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 6px;
            cursor: pointer;
            transition: background 0.3s;
        }
        .session-item:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        .session-item.active {
            background: rgba(52, 152, 219, 0.3);
        }
        @media (max-width: 768px) {
            .controls {
                grid-template-columns: 1fr;
            }
            .header h1 {
                font-size: 2em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎓 University Remote Control</h1>
            <p>Connect to university computers from anywhere</p>
        </div>

        <div id="status" class="status disconnected">
            <strong>⚠️ Disconnected</strong> - Enter a Session ID to connect
        </div>

        <div class="controls">
            <div class="control-panel">
                <h3>🔗 Connection</h3>
                <input type="text" id="sessionId" placeholder="Enter Session ID (e.g., A1B2C3)" maxlength="8">
                <button onclick="connectToSession()">Connect to Computer</button>
                <button onclick="disconnectSession()" id="disconnectBtn" disabled>Disconnect</button>
            </div>

            <div class="control-panel">
                <h3>📋 Available Sessions</h3>
                <div id="sessionsList">Loading sessions...</div>
                <button onclick="refreshSessions()">Refresh Sessions</button>
            </div>
        </div>

        <div class="screen-container">
            <h3>🖥️ Remote Screen</h3>
            <img id="screen" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==" alt="Remote screen will appear here">
            <p id="screenStatus">Not connected</p>
        </div>
    </div>

    <script>
        let currentSessionId = null;
        let screenUpdateInterval = null;
        let sessionsUpdateInterval = null;
        let lastMouseMove = 0; // For throttling mouse movement

        function updateStatus(message, isConnected) {
            const statusEl = document.getElementById('status');
            statusEl.innerHTML = message;
            statusEl.className = 'status ' + (isConnected ? 'connected' : 'disconnected');
            document.getElementById('disconnectBtn').disabled = !isConnected;
        }

        function connectToSession() {
            const sessionId = document.getElementById('sessionId').value.trim().toUpperCase();
            if (!sessionId) {
                alert('Please enter a Session ID');
                return;
            }

            currentSessionId = sessionId;
            updateStatus(`🔄 Connecting to ${sessionId}...`, false);

            // Start screen updates
            startScreenUpdates();
            updateStatus(`✅ Connected to ${sessionId}`, true);
            
            // Add mouse and keyboard event listeners
            addControlListeners();
            
            console.log('Connected to session:', sessionId);
            console.log('Event listeners added');
        }

        function disconnectSession() {
            currentSessionId = null;
            stopScreenUpdates();
            removeControlListeners();
            updateStatus('⚠️ Disconnected', false);
            document.getElementById('screenStatus').textContent = 'Not connected';
        }

        function startScreenUpdates() {
            if (screenUpdateInterval) clearInterval(screenUpdateInterval);
            
            screenUpdateInterval = setInterval(() => {
                if (!currentSessionId) return;
                
                fetch(`/api/screen/${currentSessionId}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.data) {
                            document.getElementById('screen').src = 'data:image/jpeg;base64,' + data.data;
                            document.getElementById('screenStatus').textContent = 
                                'Last update: ' + new Date(data.timestamp).toLocaleTimeString();
                        }
                    })
                    .catch(error => {
                        console.error('Screen update error:', error);
                        document.getElementById('screenStatus').textContent = 'Screen update failed';
                    });
            }, 66);  // ~15 FPS (66ms) for smoother updates matching agent performance
        }

        function stopScreenUpdates() {
            if (screenUpdateInterval) {
                clearInterval(screenUpdateInterval);
                screenUpdateInterval = null;
            }
        }

        function addControlListeners() {
            const screen = document.getElementById('screen');
            console.log('Adding event listeners to screen element:', screen);
            
            screen.addEventListener('click', handleMouseClick);
            screen.addEventListener('mousemove', handleMouseMove);
            screen.addEventListener('wheel', handleMouseWheel);
            document.addEventListener('keydown', handleKeyDown);
            document.addEventListener('keyup', handleKeyUp);
            
            console.log('Event listeners added successfully');
        }

        function removeControlListeners() {
            const screen = document.getElementById('screen');
            
            screen.removeEventListener('click', handleMouseClick);
            screen.removeEventListener('mousemove', handleMouseMove);
            screen.removeEventListener('wheel', handleMouseWheel);
            document.removeEventListener('keydown', handleKeyDown);
            document.removeEventListener('keyup', handleKeyUp);
        }

        function handleMouseClick(event) {
            if (!currentSessionId) return;
            
            console.log('Mouse click detected!', event);
            
            const rect = event.target.getBoundingClientRect();
            
            // Calculate more accurate coordinates
            const x = (event.clientX - rect.left) / rect.width;
            const y = (event.clientY - rect.top) / rect.height;
            
            // Ensure coordinates are within bounds
            const clampedX = Math.max(0, Math.min(1, x));
            const clampedY = Math.max(0, Math.min(1, y));
            
            console.log('Click coordinates (relative):', clampedX, clampedY);
            console.log('Screen rect:', rect);
            console.log('Event position:', event.clientX, event.clientY);
            
            const command = {
                type: 'mouse',
                action: 'click',
                x: clampedX,
                y: clampedY,
                button: event.button === 2 ? 'right' : 'left'
            };
            
            console.log('Sending command:', command);
            sendCommand(command);
            
            // Prevent default action and stop propagation
            event.preventDefault();
            event.stopPropagation();
        }

        function handleMouseMove(event) {
            if (!currentSessionId) return;
            
            const rect = event.target.getBoundingClientRect();
            const x = (event.clientX - rect.left) / rect.width;
            const y = (event.clientY - rect.top) / rect.height;
            
            // Throttle mouse movement to reduce server load
            const now = Date.now();
            if (now - lastMouseMove < 50) return; // Max 20 moves per second
            lastMouseMove = now;
            
            // Ensure coordinates are within bounds
            const clampedX = Math.max(0, Math.min(1, x));
            const clampedY = Math.max(0, Math.min(1, y));
            
            sendCommand({
                type: 'mouse',
                action: 'move',
                x: clampedX,
                y: clampedY
            });
        }

        function handleMouseWheel(event) {
            if (!currentSessionId) return;
            
            event.preventDefault();
            sendCommand({
                type: 'mouse',
                action: 'scroll',
                deltaY: event.deltaY
            });
        }

        function handleKeyDown(event) {
            if (!currentSessionId) return;
            if (event.target.tagName === 'INPUT') return;
            
            event.preventDefault();
            sendCommand({
                type: 'keyboard',
                action: 'keydown',
                key: event.key
            });
        }

        function handleKeyUp(event) {
            if (!currentSessionId) return;
            if (event.target.tagName === 'INPUT') return;
            
            event.preventDefault();
            sendCommand({
                type: 'keyboard',
                action: 'keyup',
                key: event.key
            });
        }

        function sendCommand(command) {
            if (!currentSessionId) return;
            
            console.log('Sending command to server:', command);
            
            fetch('/api/command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    sessionId: currentSessionId,
                    ...command
                })
            }).then(response => {
                console.log('Command response:', response);
                return response.json();
            }).then(data => {
                console.log('Command result:', data);
            }).catch(error => {
                console.error('Command send error:', error);
            });
        }

        function refreshSessions() {
            fetch('/api/sessions')
                .then(response => response.json())
                .then(sessions => {
                    const sessionsList = document.getElementById('sessionsList');
                    
                    if (sessions.length === 0) {
                        sessionsList.innerHTML = '<p>No active sessions</p>';
                        return;
                    }
                    
                    sessionsList.innerHTML = sessions.map(session => `
                        <div class="session-item ${session.sessionId === currentSessionId ? 'active' : ''}" 
                             onclick="document.getElementById('sessionId').value='${session.sessionId}'">
                            <div>
                                <strong>${session.sessionId}</strong><br>
                                <small>${session.platform} - ${session.hasScreen ? '📺' : '📱'}</small>
                            </div>
                            <div>
                                <small>${new Date(session.lastSeen * 1000).toLocaleTimeString()}</small>
                            </div>
                        </div>
                    `).join('');
                })
                .catch(error => {
                    console.error('Sessions refresh error:', error);
                    document.getElementById('sessionsList').innerHTML = '<p>Failed to load sessions</p>';
                });
        }

        // Auto-refresh sessions every 10 seconds
        setInterval(refreshSessions, 10000);
        
        // Initial load
        refreshSessions();

        // Handle right-click context menu prevention on screen
        document.getElementById('screen').addEventListener('contextmenu', function(e) {
            e.preventDefault();
            return false;
        });
    </script>
</body>
</html>'''
        
        return RequestHandler


class RemoteControlAgent:
    """Remote Control Agent for University Computers"""
    
    def __init__(self, server_url):
        self.server_url = server_url.rstrip('/')
        self.session_id = None
        self.running = False
        self.settings = {
            'screen_fps': 1,
            'screen_quality': 50,
            'screen_width': 800,
            'screen_height': 600,
            'command_check_interval': 0.1,
            'connection_timeout': 10,
            'retry_delay': 2
        }
        self.last_screen_time = 0

    def start(self):
        """Start the remote control agent"""
        print("🤖 University Remote Control Agent Starting...")
        print(f"📡 Server: {self.server_url}")
        print(f"🔧 PIL Available: {HAS_PIL}")
        print(f"🔧 Input Control: {HAS_PYNPUT}")
        
        if not self.register():
            print("❌ Failed to register with server")
            return
        
        print()
        print("=" * 60)
        print(f"✅ Agent Active! Session ID: {self.session_id}")
        print("📋 COPY THIS SESSION ID TO YOUR CONTROLLER!")
        print(f"🌐 Controller URL: {self.server_url}")
        print("=" * 60)
        print()
        print("🔄 Agent is running... Press Ctrl+C to stop")
        
        self.running = True
        
        # Start background threads for screen capture and command processing
        if HAS_PIL:
            screen_thread = threading.Thread(target=self.screen_capture_loop, daemon=True)
            screen_thread.start()
        
        if HAS_PYNPUT:
            command_thread = threading.Thread(target=self.command_loop, daemon=True)
            command_thread.start()
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Agent stopped by user")
            self.running = False

    def register(self):
        """Register agent with server and get session ID"""
        data = {
            'platform': sys.platform,
            'python_version': sys.version.split()[0],
            'has_pil': HAS_PIL,
            'has_pynput': HAS_PYNPUT,
            'timestamp': datetime.now().isoformat(),
            'agent_type': 'university'
        }
        
        try:
            print("📝 Registering with server...")
            response = self.http_post('/api/register', data)
            if response and 'sessionId' in response:
                self.session_id = response['sessionId']
                print("✅ Server registration successful")
                return True
        except Exception as e:
            print(f"⚠️ Server registration failed: {e}")
        
        # Fallback - generate local session ID
        try:
            self.session_id = secrets.token_hex(4).upper()
            print("⚠️ Using local session ID (server unavailable)")
            return True
        except:
            import random
            self.session_id = f"{random.randint(1000, 9999):04d}"
            print("⚠️ Using random session ID (crypto unavailable)")
            return True

    def screen_capture_loop(self):
        """Continuously capture and send screen updates"""
        fps_delay = 1.0 / self.settings.get('screen_fps', 1)
        
        while self.running:
            try:
                current_time = time.time()
                if current_time - self.last_screen_time >= fps_delay:
                    screen_data = self.capture_screen()
                    if screen_data:
                        self.send_screen(screen_data)
                    self.last_screen_time = current_time
                time.sleep(0.1)
            except Exception as e:
                print(f"Screen capture error: {e}")
                time.sleep(self.settings.get('retry_delay', 2))

    def command_loop(self):
        """Continuously check for and execute remote commands"""
        check_interval = self.settings.get('command_check_interval', 0.1)
        
        while self.running:
            try:
                commands = self.get_commands()
                for command in commands:
                    self.execute_command(command)
                time.sleep(check_interval)
            except Exception as e:
                print(f"Command loop error: {e}")
                time.sleep(self.settings.get('retry_delay', 2))

    def capture_screen(self):
        """Capture screen using PIL"""
        if not HAS_PIL:
            return None
            
        try:
            screenshot = ImageGrab.grab()
            
            # Resize for performance
            width = self.settings.get('screen_width', 800)
            height = self.settings.get('screen_height', 600)
            screenshot = screenshot.resize((width, height))
            
            # Convert to JPEG
            buffer = io.BytesIO()
            quality = self.settings.get('screen_quality', 50)
            screenshot.save(buffer, format='JPEG', quality=quality)
            
            return base64.b64encode(buffer.getvalue()).decode()
        except Exception as e:
            print(f"Screen capture error: {e}")
            return None

    def send_screen(self, screen_data):
        """Send screen data to server"""
        data = {
            'sessionId': self.session_id,
            'data': screen_data,
            'timestamp': int(time.time() * 1000)
        }
        
        try:
            self.http_post('/api/screen', data)
        except Exception as e:
            # Don't spam console with screen upload errors
            pass

    def get_commands(self):
        """Get pending commands from server"""
        try:
            response = self.http_get(f'/api/commands/{self.session_id}')
            return response if response else []
        except:
            return []

    def execute_command(self, command):
        """Execute a remote command"""
        if not HAS_PYNPUT:
            return
            
        try:
            cmd_type = command.get('type')
            
            if cmd_type == 'mouse':
                self.handle_mouse_command(command)
            elif cmd_type == 'keyboard':
                self.handle_keyboard_command(command)
            elif cmd_type == 'special':
                self.handle_special_command(command)
        except Exception as e:
            print(f"Command execution error: {e}")

    def handle_mouse_command(self, command):
        """Handle mouse commands using pynput"""
        try:
            x = int(command.get('x', 0) * 1920)  # Scale to screen
            y = int(command.get('y', 0) * 1080)
            
            mouse_controller = mouse.Controller()
            
            action = command.get('action')
            if action == 'move':
                mouse_controller.position = (x, y)
            elif action == 'click':
                mouse_controller.position = (x, y)
                button = mouse.Button.right if command.get('button') == 'right' else mouse.Button.left
                mouse_controller.click(button)
            elif action == 'scroll':
                dy = command.get('deltaY', 0)
                mouse_controller.scroll(0, -dy // 120)  # Convert to scroll units
        except Exception as e:
            print(f"Mouse command error: {e}")

    def handle_keyboard_command(self, command):
        """Handle keyboard commands using pynput"""
        try:
            key_controller = keyboard.Controller()
            key = command.get('key', '')
            
            # Map special keys
            key_map = {
                'Enter': keyboard.Key.enter,
                'Escape': keyboard.Key.esc,
                'Backspace': keyboard.Key.backspace,
                'Tab': keyboard.Key.tab,
                'ArrowUp': keyboard.Key.up,
                'ArrowDown': keyboard.Key.down,
                'ArrowLeft': keyboard.Key.left,
                'ArrowRight': keyboard.Key.right,
                'Delete': keyboard.Key.delete,
                'Home': keyboard.Key.home,
                'End': keyboard.Key.end,
                'PageUp': keyboard.Key.page_up,
                'PageDown': keyboard.Key.page_down,
            }
            
            if command.get('action') == 'keydown':
                if key in key_map:
                    key_controller.press(key_map[key])
                elif len(key) == 1:
                    key_controller.press(key)
            elif command.get('action') == 'keyup':
                if key in key_map:
                    key_controller.release(key_map[key])
                elif len(key) == 1:
                    key_controller.release(key)
            elif command.get('action') == 'type':
                key_controller.type(key)
        except Exception as e:
            print(f"Keyboard command error: {e}")

    def handle_special_command(self, command):
        """Handle special system commands"""
        action = command.get('action')
        if action == 'ctrl-alt-del':
            print("⚠️ Ctrl+Alt+Del requested (not implemented for security)")
        elif action == 'alt-tab':
            try:
                key_controller = keyboard.Controller()
                key_controller.press(keyboard.Key.alt)
                key_controller.press(keyboard.Key.tab)
                key_controller.release(keyboard.Key.tab)
                key_controller.release(keyboard.Key.alt)
            except:
                pass
        else:
            print(f"Special command: {action}")

    def http_get(self, path):
        """Make HTTP GET request"""
        try:
            timeout = self.settings.get('connection_timeout', 10)
            with urllib.request.urlopen(f"{self.server_url}{path}", timeout=timeout) as response:
                return json.loads(response.read().decode())
        except Exception as e:
            raise Exception(f"GET {path} failed: {e}")

    def http_post(self, path, data):
        """Make HTTP POST request"""
        try:
            json_data = json.dumps(data).encode()
            req = urllib.request.Request(
                f"{self.server_url}{path}",
                data=json_data,
                headers={'Content-Type': 'application/json'}
            )
            timeout = self.settings.get('connection_timeout', 10)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return json.loads(response.read().decode())
        except Exception as e:
            raise Exception(f"POST {path} failed: {e}")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("University Remote Control System")
        print("Usage:")
        print("  python remote_control.py server [PORT]     # Start server")
        print("  python remote_control.py agent SERVER_URL  # Start agent")
        sys.exit(1)
    
    mode = sys.argv[1].lower()
    
    if mode == 'server':
        # Start server mode
        port = int(os.environ.get('PORT', 8080))  # Railway sets PORT environment variable
        if len(sys.argv) > 2:
            port = int(sys.argv[2])
        
        server = RemoteControlServer(port)
        server.start()
        
    elif mode == 'agent':
        # Start agent mode
        if len(sys.argv) < 3:
            print("Error: Agent mode requires server URL")
            print("Usage: python remote_control.py agent SERVER_URL")
            sys.exit(1)
        
        server_url = sys.argv[2]
        agent = RemoteControlAgent(server_url)
        agent.start()
        
    else:
        print(f"Unknown mode: {mode}")
        print("Available modes: server, agent")
        sys.exit(1)


if __name__ == "__main__":
    main()