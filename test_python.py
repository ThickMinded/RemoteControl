# Test Script for Remote Control
import subprocess
import sys

print("Testing Python Remote Control System...")

# Test server start (will run for 5 seconds then stop)
try:
    print("Starting server...")
    proc = subprocess.Popen([sys.executable, "remote_control.py", "server"], 
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Let it run for a moment
    import time
    time.sleep(2)
    
    # Check if it's running
    if proc.poll() is None:
        print("✅ Server started successfully!")
        proc.terminate()
    else:
        stdout, stderr = proc.communicate()
        print(f"❌ Server failed to start: {stderr}")
        
except Exception as e:
    print(f"❌ Test failed: {e}")

print("Test complete!")
