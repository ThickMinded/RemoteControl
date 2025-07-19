# University Remote Control - Zero Installation Package

Access your university computer remotely from anywhere without needing admin permissions or software installation.

## 🚀 Quick Start

1. **Copy this entire folder** to your university computer (via USB drive, cloud storage, etc.)
2. **Double-click `university-setup.bat`** and follow the instructions
3. **Copy the Session ID** that appears
4. **Open the controller** at: https://web-production-463b89.up.railway.app
5. **Enter your Session ID** to connect

## 📁 Package Contents

| File | Purpose |
|------|---------|
| `university-setup.bat` | 🎯 **Main setup script** - Run this first |
| `quick-start.bat` | ⚡ Fast startup for repeated use |
| `agent.py` | 🤖 Core remote control agent |
| `check_system.py` | 🔧 System compatibility checker |
| `config.json` | ⚙️ Configuration settings |
| `README.md` | 📖 This documentation |

## 🎯 How It Works

1. **No Installation**: Everything runs from this folder
2. **Firewall Friendly**: Uses standard HTTPS connections
3. **University Safe**: No admin permissions required
4. **Session Based**: Secure temporary connections only

## 📋 Requirements

- **Windows computer** with Python installed
- **Internet connection** (works through university firewalls)
- **No admin permissions** needed

### Python Installation (if needed)

If Python isn't available:

1. **Microsoft Store**: Search "Python 3.11" and install
2. **Official Website**: Download from https://python.org/downloads
3. **Ask IT**: Request Python installation from IT department

## 🔧 Features Available

| Feature | Description | Requires |
|---------|-------------|----------|
| ✅ **Session Management** | Secure temporary connections | Python only |
| ✅ **Screen Sharing** | Real-time desktop viewing | `pillow` package |
| ✅ **Remote Control** | Mouse and keyboard control | `pynput` package |

## 📦 Optional Enhancements

For full functionality, install these packages (if allowed):

```bash
pip install pillow      # Enables screen capture
pip install pynput      # Enables mouse/keyboard control
```

**Note**: The system works without these packages, but with limited features.

## 🚨 Troubleshooting

### Python Not Found
- Install Python from Microsoft Store or python.org
- Or ask IT department to install Python

### Network Issues  
- Try on different university networks
- Check if HTTPS connections are allowed
- The system works through most university firewalls

### Permission Errors
- This package requires NO admin permissions
- If prompted for admin access, something is wrong
- Contact support if you encounter permission requests

## 💡 Usage Tips

### For Regular Use
1. Run `quick-start.bat` for faster subsequent connections
2. Keep this folder on a USB drive for portability
3. Each session gets a unique ID for security

### For IT Administrators
- This tool uses only standard Python libraries
- No system modifications or installations
- All connections are HTTPS encrypted
- Sessions are temporary and automatically expire

## 🔒 Security Features

- **Session-based access**: Each connection has a unique ID
- **HTTPS encryption**: All data is encrypted in transit
- **No permanent installation**: Nothing persists on the system
- **No admin rights**: Cannot modify system settings
- **Auto-expiring sessions**: Connections automatically timeout

## 🌐 Controller Access

**Web Interface**: https://web-production-463b89.up.railway.app

The controller works on any device with a web browser:
- 💻 Desktop computers
- 📱 Mobile phones  
- 📱 Tablets
- 🖥️ Other university computers

## 📞 Support

This is a zero-installation remote control system designed for university environments where traditional remote desktop solutions aren't available.

For technical issues:
1. Run `check_system.py` to diagnose problems
2. Check that Python is properly installed
3. Verify internet connectivity
4. Ensure university firewall allows HTTPS connections

---

**Version**: 1.0.0  
**Platform**: Windows  
**Requirements**: Python 3.6+  
**License**: Educational Use
