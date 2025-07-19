#!/usr/bin/env python3
"""
University Remote Control Agent
Zero-installation remote control for university computers.
"""

import sys
import os
import json
import time
import threading
import base64
import secrets
import urllib.request
import urllib.parse
import io
from datetime import datetime

# Try to import optional dependencies with fallbacks
try:
    import PIL.ImageGrab as ImageGrab
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    # Dynamic import to avoid automatic dependency detection
    import pynput.mouse as pynput_mouse
    import pynput.keyboard as pynput_keyboard
    mouse = pynput_mouse
    keyboard = pynput_keyboard
    HAS_PYNPUT = True
    print("✅ pynput imported successfully")
except ImportError as e:
    print(f"❌ pynput import failed: {e}")
    HAS_PYNPUT = False

# Load configuration
def load_config():
    """Load configuration from config.json"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception:
        # Default configuration
        return {
            "server_url": "https://web-production-463b89.up.railway.app",
            "settings": {
                "screen_fps": 10,  # Increased from 1 to 10 FPS for better responsiveness
                "screen_quality": 60,  # Increased quality slightly
                "screen_width": 1280,  # Higher resolution
                "screen_height": 720,
                "command_check_interval": 0.05,  # Reduced from 0.1 to 0.05 (50ms)
                "connection_timeout": 10,
                "retry_delay": 1  # Reduced retry delay
            }
        }

config = load_config()


class RemoteControlAgent:
    """Remote Control Agent for University Computers"""
    
    def __init__(self, server_url=None):
        self.server_url = (server_url or config.get('server_url')).rstrip('/')
        self.session_id = None
        self.running = False
        self.settings = config.get('settings', {})
        self.last_screen_time = 0
        self.command_queue = []
        self.last_screenshot_hash = None  # For change detection

    def start(self):
        """Start the remote control agent"""
        print("University Remote Control Agent Starting...")
        print(f"Server: {self.server_url}")
        print(f"PIL Available: {HAS_PIL}")
        print(f"Input Control: {HAS_PYNPUT}")
        
        if not self.register():
            print("FAILED to register with server")
            return
        
        print()
        print("=" * 60)
        print(f"SUCCESS! Agent Active! Session ID: {self.session_id}")
        print("=" * 60)
        print("COPY THIS SESSION ID TO YOUR CONTROLLER!")
        print(f"Session ID: {self.session_id}")
        print(f"Controller URL: {self.server_url}")
        print("=" * 60)
        print()
        print("Agent is running... Press Ctrl+C to stop")
        
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
        # Prepare registration data
        data = {
            'platform': sys.platform,
            'python_version': sys.version.split()[0],
            'has_pil': HAS_PIL,
            'has_pynput': HAS_PYNPUT,
            'timestamp': datetime.now().isoformat(),
            'agent_type': 'university'
        }
        
        try:
            # Try to register with server
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
            print("⚠️ Using random session ID (crypto unavailable)")
            return True

    def screen_capture_loop(self):
        """Continuously capture and send screen updates"""
        fps_delay = 1.0 / self.settings.get('screen_fps', 10)
        
        while self.running:
            try:
                current_time = time.time()
                if current_time - self.last_screen_time >= fps_delay:
                    screen_data = self.capture_screen()
                    if screen_data:
                        self.send_screen(screen_data)
                    self.last_screen_time = current_time
                time.sleep(0.01)  # Reduced sleep time for better responsiveness
            except Exception as e:
                print(f"Screen capture error: {e}")
                time.sleep(self.settings.get('retry_delay', 1))

    def command_loop(self):
        """Continuously check for and execute remote commands"""
        check_interval = self.settings.get('command_check_interval', 0.1)
        
        while self.running:
            try:
                commands = self.get_commands()
                if commands:
                    print(f"Received {len(commands)} commands")
                for command in commands:
                    print(f"Executing command: {command}")
                    self.execute_command(command)
                time.sleep(check_interval)
            except Exception as e:
                print(f"Command loop error: {e}")
                time.sleep(self.settings.get('retry_delay', 2))

    def capture_screen(self):
        """Capture screen using PIL with optimization"""
        if not HAS_PIL:
            return None
            
        try:
            screenshot = ImageGrab.grab()
            
            # Quick hash check for change detection
            import hashlib
            screen_hash = hashlib.md5(screenshot.tobytes()).hexdigest()
            
            # Only process if screen changed significantly
            if screen_hash == self.last_screenshot_hash:
                return None  # No change, skip this frame
            
            self.last_screenshot_hash = screen_hash
            
            # Resize for performance with better settings
            width = self.settings.get('screen_width', 1280)
            height = self.settings.get('screen_height', 720)
            screenshot = screenshot.resize((width, height), Image.LANCZOS if hasattr(Image, 'LANCZOS') else 1)
            
            # Convert to JPEG with optimizations
            buffer = io.BytesIO()
            quality = self.settings.get('screen_quality', 60)
            screenshot.save(buffer, format='JPEG', quality=quality, optimize=True)
            
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
            print(f"Handling mouse command: {command}")
            
            # Get actual screen dimensions
            if HAS_PIL:
                from PIL import ImageGrab
                screen = ImageGrab.grab()
                screen_width, screen_height = screen.size
            else:
                # Fallback to common resolution
                screen_width, screen_height = 1920, 1080
            
            # Convert relative coordinates (0-1) to actual screen pixels
            x = int(command.get('x', 0) * screen_width)
            y = int(command.get('y', 0) * screen_height)
            
            # Ensure coordinates are within screen bounds
            x = max(0, min(x, screen_width - 1))
            y = max(0, min(y, screen_height - 1))
            
            mouse_controller = mouse.Controller()
            
            action = command.get('action')
            if action == 'move':
                mouse_controller.position = (x, y)
                print(f"Mouse moved to ({x}, {y}) on {screen_width}x{screen_height} screen")
            elif action == 'click':
                mouse_controller.position = (x, y)
                button = mouse.Button.right if command.get('button') == 'right' else mouse.Button.left
                mouse_controller.click(button)
                print(f"Mouse clicked at ({x}, {y}) with {button} on {screen_width}x{screen_height} screen")
            elif action == 'scroll':
                dy = command.get('deltaY', 0)
                mouse_controller.scroll(0, -dy // 120)  # Convert to scroll units
                print(f"Mouse scrolled: {dy}")
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
    print("University Remote Control Agent v1.0")
    print("Zero-installation remote access for university computers")
    print("=" * 60)
    
    # Check for server URL argument
    server_url = None
    if len(sys.argv) > 1:
        # Handle different argument formats
        if sys.argv[1] == 'agent' and len(sys.argv) > 2:
            server_url = sys.argv[2]
        else:
            server_url = sys.argv[1]
    
    # Create and start agent
    agent = RemoteControlAgent(server_url)
    agent.start()


if __name__ == "__main__":
    main() 
