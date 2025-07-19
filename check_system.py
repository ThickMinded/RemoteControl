#!/usr/bin/env python3
"""
Dependency checker for University Remote Control Agent
Checks what features are available on this system.
"""

import sys
import platform

def check_python():
    """Check Python version"""
    version = sys.version_info
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    if version.major >= 3 and version.minor >= 6:
        return True
    else:
        print("⚠️ Python 3.6+ recommended")
        return False

def check_pil():
    """Check PIL/Pillow availability"""
    try:
        import PIL.ImageGrab
        print("✅ PIL/Pillow available - Screen capture enabled")
        return True
    except ImportError:
        print("❌ PIL/Pillow not available - No screen capture")
        print("   To enable: pip install pillow")
        return False

def check_pynput():
    """Check pynput availability"""
    try:
        import pynput.mouse
        import pynput.keyboard
        print("✅ pynput available - Remote control enabled")
        return True
    except ImportError:
        print("❌ pynput not available - No remote control")
        print("   To enable: pip install pynput")
        return False

def check_network():
    """Check network connectivity"""
    try:
        import urllib.request
        with urllib.request.urlopen('https://web-production-463b89.up.railway.app', timeout=5) as response:
            if response.status == 200:
                print("✅ Server connectivity - OK")
                return True
    except Exception as e:
        print(f"❌ Server connectivity failed: {e}")
        return False

def main():
    """Check all dependencies"""
    print("University Remote Control - System Check")
    print("=" * 50)
    print(f"Operating System: {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.machine()}")
    print()
    
    results = {
        'python': check_python(),
        'pil': check_pil(),
        'pynput': check_pynput(),
        'network': check_network()
    }
    
    print()
    print("=" * 50)
    
    if results['python']:
        print("✅ Agent can run (basic mode)")
    else:
        print("❌ Agent cannot run - Python too old")
        return
    
    if results['pil'] and results['pynput']:
        print("✅ Full functionality available")
    elif results['pil']:
        print("⚠️ Screen sharing only (no remote control)")
    elif results['pynput']:
        print("⚠️ Remote control only (no screen sharing)")
    else:
        print("⚠️ Limited functionality - install PIL and pynput")
    
    if results['network']:
        print("✅ Ready to connect")
    else:
        print("❌ Cannot connect to server")
    
    print()
    print("To install missing dependencies:")
    if not results['pil']:
        print("  pip install pillow")
    if not results['pynput']:
        print("  pip install pynput")

if __name__ == "__main__":
    main()
