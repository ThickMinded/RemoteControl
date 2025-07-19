#!/usr/bin/env python3
"""
Universal Remote Control System - Single Python Script
Works without installation, admin rights, or dependencies beyond Python standard library.

Usage:
    python remote_control.py server                    # Start server
    python remote_control.py agent SERVER_URL          # Start agent
    python remote_control.py controller SESSION_ID     # Start controller (CLI)
    python remote_control.py web                       # Start web interface
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

# Try to import GUI dependencies (not available on headless cloud servers)
try:
    import tkinter as tk
    from tkinter import messagebox
    HAS_TKINTER = True
except ImportError:
    HAS_TKINTER = False

# Try to import optional dependencies
try:
    import PIL.ImageGrab as ImageGrab
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    # Dynamic import to avoid automatic dependency detection by cloud platforms
    mouse = __import__('pynput.mouse', fromlist=[''])
    keyboard = __import__('pynput.keyboard', fromlist=[''])
    HAS_PYNPUT = True
except ImportError:
    HAS_PYNPUT = False

# Fallback Windows-specific imports
try:
    import ctypes
    import ctypes.wintypes
    HAS_WINDOWS_API = True
except ImportError:
    HAS_WINDOWS_API = False

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
            def do_GET(self):
                """Handle GET requests"""
                parsed = urlparse(self.path)
                path = parsed.path
                query = parse_qs(parsed.query)
                
                if path == '/':
                    self.serve_web_interface()
                elif path == '/agent':
                    self.serve_agent_interface()
                elif path.startswith('/control/'):
                    session_id = path.split('/')[-1]
                    self.serve_controller_interface(session_id)
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
                
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                
                try:
                    data = json.loads(post_data.decode('utf-8'))
                except:
                    data = {}
                
                if path == '/api/register':
                    self.api_register_agent(data)
                elif path.startswith('/api/command/'):
                    session_id = path.split('/')[-1]
                    self.api_send_command(session_id, data)
                elif path == '/api/screen':
                    self.api_receive_screen(data)
                else:
                    self.send_error(404)
            
            def serve_web_interface(self):
                """Serve main web interface"""
                html = """<!DOCTYPE html>
<html><head><title>Remote Control</title>
<style>
body{font-family:Arial,sans-serif;background:#1a1a1a;color:white;text-align:center;padding:2rem}
.container{max-width:600px;margin:0 auto;background:#2d2d2d;padding:2rem;border-radius:10px}
button{background:#007acc;color:white;border:none;padding:1rem 2rem;border-radius:5px;cursor:pointer;margin:0.5rem;font-size:1rem}
button:hover{background:#005a9e}
input{padding:0.75rem;margin:0.5rem;border:1px solid #555;border-radius:5px;background:#333;color:white;font-size:1rem;width:300px}
.session-list{background:#333;padding:1rem;border-radius:5px;margin:1rem 0}
.session-item{padding:0.5rem;border-bottom:1px solid #555;cursor:pointer}
.session-item:hover{background:#444}
</style></head><body>
<div class="container">
<h1>🖥️ Remote Control System</h1>
<h3>Connect to Computer</h3>
<input type="text" id="sessionId" placeholder="Enter Session ID">
<br><button onclick="connect()">Connect</button>

<h3>Active Sessions</h3>
<button onclick="refreshSessions()">Refresh</button>
<div class="session-list" id="sessions">Loading...</div>

<h3>Start Agent</h3>
<p>Run this command on the computer you want to control:</p>
<code>python remote_control.py agent http://YOUR_SERVER:8080</code>
</div>

<script>
function connect(){
    const sid = document.getElementById('sessionId').value;
    if(sid) window.open('/control/'+sid, '_blank');
}

function refreshSessions(){
    fetch('/api/sessions').then(r=>r.json()).then(data=>{
        const div = document.getElementById('sessions');
        if(data.length === 0){
            div.innerHTML = '<p>No active sessions</p>';
        } else {
            div.innerHTML = data.map(s => 
                `<div class="session-item" onclick="document.getElementById('sessionId').value='${s.id}'">
                Session ${s.id} - ${s.type} - ${new Date(s.timestamp).toLocaleTimeString()}
                </div>`
            ).join('');
        }
    });
}

setInterval(refreshSessions, 5000);
refreshSessions();
</script>
</body></html>"""
                
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(html.encode())
            
            def serve_agent_interface(self):
                """Serve agent setup interface"""
                html = """<!DOCTYPE html>
<html><head><title>Remote Agent Setup</title>
<style>
body{font-family:Arial,sans-serif;background:#1a1a1a;color:white;text-align:center;padding:2rem}
.container{max-width:600px;margin:0 auto;background:#2d2d2d;padding:2rem;border-radius:10px}
button{background:#007acc;color:white;border:none;padding:1rem 2rem;border-radius:5px;cursor:pointer;margin:0.5rem;font-size:1rem}
.code{background:#000;padding:1rem;border-radius:5px;margin:1rem 0;font-family:monospace;color:#00ff00}
</style></head><body>
<div class="container">
<h1>🤖 Remote Agent Setup</h1>
<p>Download and run the Python script on the computer you want to control:</p>

<h3>Method 1: Download Script</h3>
<button onclick="downloadScript()">Download remote_control.py</button>

<h3>Method 2: Command Line</h3>
<div class="code">python remote_control.py agent """ + self.headers.get('Host', 'localhost:8080') + """</div>

<h3>Method 3: Copy & Paste</h3>
<p>Copy the entire script content and save as 'remote_control.py', then run the command above.</p>
</div>

<script>
function downloadScript(){
    window.open('/download/remote_control.py', '_blank');
}
</script>
</body></html>"""
                
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(html.encode())
            
            def serve_controller_interface(self, session_id):
                """Serve controller interface"""
                html = f"""<!DOCTYPE html>
<html><head><title>Remote Control - {session_id}</title>
<style>
body{{margin:0;background:#000;color:white;font-family:Arial,sans-serif}}
.header{{background:#333;padding:1rem;display:flex;justify-content:space-between;align-items:center}}
.screen{{width:100vw;height:calc(100vh - 60px);position:relative;overflow:hidden}}
#screenImg{{max-width:100%;max-height:100%;cursor:crosshair}}
.status{{position:absolute;top:10px;left:50%;transform:translateX(-50%);background:rgba(0,0,0,0.8);padding:0.5rem 1rem;border-radius:20px}}
button{{background:#007acc;color:white;border:none;padding:0.5rem 1rem;border-radius:4px;cursor:pointer}}
</style></head><body>
<div class="header">
<div>Session: {session_id}</div>
<div>
<button onclick="sendSpecial('ctrl-alt-del')">Ctrl+Alt+Del</button>
<button onclick="disconnect()">Disconnect</button>
</div>
</div>
<div class="status" id="status">Connecting...</div>
<div class="screen">
<img id="screenImg" src="" alt="Remote Screen">
</div>

<script>
let sessionId = '{session_id}';
let connected = false;

function updateScreen(){{
    fetch('/api/screen/'+sessionId)
    .then(r => r.json())
    .then(data => {{
        if(data.image){{
            document.getElementById('screenImg').src = 'data:image/jpeg;base64,'+data.image;
            document.getElementById('status').textContent = 'Connected';
            connected = true;
        }}
    }})
    .catch(e => {{
        document.getElementById('status').textContent = 'Disconnected';
        connected = false;
    }});
}}

function sendCommand(cmd){{
    fetch('/api/command/'+sessionId, {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify(cmd)
    }});
}}

document.getElementById('screenImg').addEventListener('click', function(e){{
    if(!connected) return;
    const rect = this.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width;
    const y = (e.clientY - rect.top) / rect.height;
    sendCommand({{
        type: 'mouse',
        action: 'click',
        x: x,
        y: y,
        button: e.button === 2 ? 'right' : 'left'
    }});
}});

document.addEventListener('keydown', function(e){{
    if(!connected) return;
    e.preventDefault();
    sendCommand({{
        type: 'keyboard',
        action: 'press',
        key: e.key,
        code: e.code,
        ctrl: e.ctrlKey,
        alt: e.altKey,
        shift: e.shiftKey
    }});
}});

function sendSpecial(action){{
    sendCommand({{type: 'special', action: action}});
}}

function disconnect(){{
    window.close();
}}

// Update screen every 500ms
setInterval(updateScreen, 500);
updateScreen();
</script>
</body></html>"""
                
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(html.encode())
            
            def api_get_sessions(self):
                """API: Get active sessions"""
                sessions = [
                    {
                        'id': sid,
                        'type': session.get('type', 'unknown'),
                        'timestamp': session.get('timestamp', 0)
                    }
                    for sid, session in server_ref.sessions.items()
                ]
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(sessions).encode())
            
            def api_register_agent(self, data):
                """API: Register new agent"""
                session_id = secrets.token_hex(3).upper()
                server_ref.sessions[session_id] = {
                    'type': 'agent',
                    'timestamp': time.time() * 1000,
                    'info': data
                }
                server_ref.command_queues[session_id] = queue.Queue()
                
                print(f"🤖 Agent registered: {session_id}")
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'sessionId': session_id}).encode())
            
            def api_get_commands(self, session_id):
                """API: Get commands for agent"""
                commands = []
                if session_id in server_ref.command_queues:
                    q = server_ref.command_queues[session_id]
                    while not q.empty():
                        try:
                            commands.append(q.get_nowait())
                        except queue.Empty:
                            break
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(commands).encode())
            
            def api_send_command(self, session_id, command):
                """API: Send command to agent"""
                if session_id in server_ref.command_queues:
                    server_ref.command_queues[session_id].put(command)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True}).encode())
            
            def api_receive_screen(self, data):
                """API: Receive screen data from agent"""
                session_id = data.get('sessionId')
                if session_id:
                    server_ref.screen_data[session_id] = {
                        'image': data.get('data'),
                        'timestamp': time.time()
                    }
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True}).encode())
            
            def api_get_screen(self, session_id):
                """API: Get screen data for controller"""
                screen = server_ref.screen_data.get(session_id, {})
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(screen).encode())
            
            def log_message(self, format, *args):
                """Suppress default logging"""
                pass
        
        return RequestHandler

class RemoteControlAgent:
    """Agent that captures screen and executes commands"""
    
    def __init__(self, server_url):
        self.server_url = server_url.rstrip('/')
        self.session_id = None
        self.running = False
        
    def start(self):
        """Start the agent"""
        print("🤖 Starting Remote Control Agent...")
        print(f"📡 Server: {self.server_url}")
        
        # Register with server
        if not self.register():
            print("❌ Failed to register with server")
            return
        
        print(f"✅ Agent registered! Session ID: {self.session_id}")
        print("📋 Share this Session ID with your controller")
        print("🔄 Agent is running... Press Ctrl+C to stop")
        
        self.running = True
        
        # Start threads
        screen_thread = threading.Thread(target=self.screen_capture_loop)
        command_thread = threading.Thread(target=self.command_loop)
        
        screen_thread.daemon = True
        command_thread.daemon = True
        
        screen_thread.start()
        command_thread.start()
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Agent stopped")
            self.running = False
    
    def register(self):
        """Register agent with server"""
        data = {
            'platform': sys.platform,
            'python_version': sys.version,
            'has_pil': HAS_PIL,
            'has_pynput': HAS_PYNPUT,
            'has_windows_api': HAS_WINDOWS_API
        }
        
        try:
            response = self.http_post('/api/register', data)
            if response:
                self.session_id = response.get('sessionId')
                return True
        except Exception as e:
            print(f"Registration error: {e}")
        
        return False
    
    def screen_capture_loop(self):
        """Continuously capture and send screen"""
        while self.running:
            try:
                screen_data = self.capture_screen()
                if screen_data:
                    self.send_screen(screen_data)
                time.sleep(1)  # 1 FPS
            except Exception as e:
                print(f"Screen capture error: {e}")
                time.sleep(2)
    
    def command_loop(self):
        """Continuously check for and execute commands"""
        while self.running:
            try:
                commands = self.get_commands()
                for command in commands:
                    self.execute_command(command)
                time.sleep(0.1)  # Check every 100ms
            except Exception as e:
                print(f"Command loop error: {e}")
                time.sleep(1)
    
    def capture_screen(self):
        """Capture screen using available method"""
        if HAS_PIL:
            return self.capture_screen_pil()
        elif HAS_WINDOWS_API:
            return self.capture_screen_windows()
        else:
            return self.capture_screen_fallback()
    
    def capture_screen_pil(self):
        """Capture screen using PIL"""
        try:
            screenshot = ImageGrab.grab()
            # Resize for performance
            screenshot = screenshot.resize((800, 600))
            
            buffer = io.BytesIO()
            screenshot.save(buffer, format='JPEG', quality=50)
            return base64.b64encode(buffer.getvalue()).decode()
        except Exception as e:
            print(f"PIL capture error: {e}")
            return None
    
    def capture_screen_windows(self):
        """Capture screen using Windows API"""
        try:
            # This is a simplified version - would need full Windows API implementation
            print("Windows API screen capture not implemented in this example")
            return None
        except Exception as e:
            print(f"Windows API capture error: {e}")
            return None
    
    def capture_screen_fallback(self):
        """Fallback screen capture method"""
        print("⚠️  No screen capture method available")
        return None
    
    def send_screen(self, screen_data):
        """Send screen data to server"""
        data = {
            'sessionId': self.session_id,
            'data': screen_data,
            'timestamp': time.time() * 1000
        }
        
        try:
            self.http_post('/api/screen', data)
        except Exception as e:
            print(f"Screen send error: {e}")
    
    def get_commands(self):
        """Get commands from server"""
        try:
            response = self.http_get(f'/api/commands/{self.session_id}')
            return response if response else []
        except:
            return []
    
    def execute_command(self, command):
        """Execute a remote command"""
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
        """Handle mouse commands"""
        if HAS_PYNPUT:
            self.handle_mouse_pynput(command)
        elif HAS_WINDOWS_API:
            self.handle_mouse_windows(command)
        else:
            print(f"Mouse command not supported: {command}")
    
    def handle_mouse_pynput(self, command):
        """Handle mouse using pynput"""
        try:
            x = int(command.get('x', 0) * 1920)  # Assume 1920x1080
            y = int(command.get('y', 0) * 1080)
            
            mouse_controller = mouse.Controller()
            
            if command.get('action') == 'click':
                mouse_controller.position = (x, y)
                button = mouse.Button.right if command.get('button') == 'right' else mouse.Button.left
                mouse_controller.click(button)
        except Exception as e:
            print(f"Mouse pynput error: {e}")
    
    def handle_mouse_windows(self, command):
        """Handle mouse using Windows API"""
        # Simplified - would need full Windows API implementation
        print(f"Windows mouse command: {command}")
    
    def handle_keyboard_command(self, command):
        """Handle keyboard commands"""
        if HAS_PYNPUT:
            self.handle_keyboard_pynput(command)
        elif HAS_WINDOWS_API:
            self.handle_keyboard_windows(command)
        else:
            print(f"Keyboard command not supported: {command}")
    
    def handle_keyboard_pynput(self, command):
        """Handle keyboard using pynput"""
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
            
            if key in key_map:
                key_controller.press(key_map[key])
                key_controller.release(key_map[key])
            else:
                key_controller.type(key)
        except Exception as e:
            print(f"Keyboard pynput error: {e}")
    
    def handle_keyboard_windows(self, command):
        """Handle keyboard using Windows API"""
        # Simplified - would need full Windows API implementation
        print(f"Windows keyboard command: {command}")
    
    def handle_special_command(self, command):
        """Handle special commands"""
        action = command.get('action')
        if action == 'ctrl-alt-del':
            print("Ctrl+Alt+Del requested (not implemented for security)")
        else:
            print(f"Special command: {action}")
    
    def http_get(self, path):
        """Make HTTP GET request"""
        try:
            with urllib.request.urlopen(f"{self.server_url}{path}") as response:
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
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode())
        except Exception as e:
            raise Exception(f"POST {path} failed: {e}")

def print_usage():
    """Print usage information"""
    print("""
🖥️  Universal Remote Control System

Usage:
    python remote_control.py server [port]              # Start server (default port 8080)
    python remote_control.py agent <server_url>         # Start agent
    python remote_control.py web                        # Start web interface only
    python remote_control.py install-deps               # Install optional dependencies

Examples:
    python remote_control.py server                     # Start server on port 8080
    python remote_control.py server 9000                # Start server on port 9000
    python remote_control.py agent http://localhost:8080    # Connect agent to local server
    python remote_control.py agent https://my-server.com    # Connect agent to remote server

Dependencies (optional, improves functionality):
    pip install pillow pynput

Without dependencies:
    - Screen capture: Limited/not available
    - Mouse/Keyboard: Limited platform support
    - Still works for basic remote control via web interface
""")

def install_dependencies():
    """Install optional dependencies"""
    print("Installing optional dependencies...")
    try:
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pillow', 'pynput'])
        print("✅ Dependencies installed successfully!")
    except Exception as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("You can manually install with: pip install pillow pynput")

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print_usage()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'server':
        # Handle Railway's PORT environment variable
        if len(sys.argv) > 2:
            port = int(sys.argv[2])
        else:
            port = int(os.environ.get('PORT', 8080))
        
        server = RemoteControlServer(port)
        server.start()
    
    elif command == 'agent':
        if len(sys.argv) < 3:
            print("❌ Server URL required for agent mode")
            print("Usage: python remote_control.py agent <server_url>")
            return
        
        server_url = sys.argv[2]
        agent = RemoteControlAgent(server_url)
        agent.start()
    
    elif command == 'web':
        # Just start server and open browser
        port = 8080
        print(f"🌐 Starting web interface on http://localhost:{port}")
        server = RemoteControlServer(port)
        
        # Try to open browser
        try:
            import webbrowser
            webbrowser.open(f'http://localhost:{port}')
        except:
            pass
        
        server.start()
    
    elif command == 'install-deps':
        install_dependencies()
    
    else:
        print(f"❌ Unknown command: {command}")
        print_usage()

if __name__ == "__main__":
    main()
