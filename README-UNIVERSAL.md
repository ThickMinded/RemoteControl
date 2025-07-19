# 🎓 University Remote Control - Universal Package

**Zero-installation remote control that works on ANY Windows computer!**

## 🚀 Super Simple Setup

### For First Time Use:
1. **Copy this entire folder** to any Windows computer
2. **Double-click `run-agent.bat`** 
3. **Copy the Session ID** that appears
4. **Go to**: https://web-production-463b89.up.railway.app
5. **Enter your Session ID** and click "Connect"

### For Quick Restart:
- **Double-click `quick-start-universal.bat`** for faster startup

## 📁 What's in This Package

| File | What It Does |
|------|--------------|
| `run-agent.bat` | 🎯 **Main setup** - Installs everything automatically |
| `quick-start-universal.bat` | ⚡ **Quick restart** - For repeat use |
| `agent.py` | 🤖 The remote control agent |
| `check_system.py` | 🔧 System compatibility checker |
| `config.json` | ⚙️ Settings file |
| `README-UNIVERSAL.md` | 📖 This guide |

## 🎯 How It Works

### Universal Python Detection
The batch file automatically finds Python on any computer by checking:
- `python` command
- `python3` command  
- `py` command
- Common installation paths like `C:\Python311\`
- User-specific installations

### Automatic Dependency Installation
The script automatically installs required packages:
- **Pillow**: For screen capture
- **pynput**: For mouse/keyboard control

### Works Everywhere
- ✅ **University computers** (no admin needed)
- ✅ **Home computers** 
- ✅ **Work computers**
- ✅ **Public computers** (with Python)
- ✅ **USB drive** (portable)

## 💡 Usage Examples

### University Lab Computer:
1. Copy folder from USB drive to Desktop
2. Double-click `run-agent.bat`
3. Use Session ID on your phone/laptop to control it

### Home Computer:
1. Download folder 
2. Run `run-agent.bat` once for setup
3. Use `quick-start-universal.bat` for daily use

### Remote Work:
1. Install on work computer before leaving office
2. Control from home using Session ID
3. Works through corporate firewalls

## 🔧 What Gets Installed

The script uses `pip install --user` which means:
- ✅ **No admin permissions** required
- ✅ **User-specific** installation only
- ✅ **No system changes**
- ✅ **Completely removable**

## 🎮 Remote Control Features

Once connected, you can:
- 👁️ **See the remote screen** in real-time
- 🖱️ **Click anywhere** on the remote screen
- ⌨️ **Type on the remote computer**
- 🔄 **Scroll and navigate**
- 📱 **Control from mobile** devices too

## 🚨 Troubleshooting

### "Python not found"
- Install Python from: https://python.org/downloads
- Or use Microsoft Store: Search "Python 3.11"
- Or ask IT to install Python

### "Permission denied" during installation
- The script uses `--user` flag which doesn't need admin
- If it still fails, dependencies aren't required for basic operation

### "Can't connect to server"
- Check internet connection
- Try different network (some block HTTPS)
- The Session ID is still generated for later use

## 🔒 Security & Privacy

- **Session-based**: Each connection uses unique temporary ID
- **HTTPS encrypted**: All data is secure in transit  
- **No permanent installation**: Nothing stays on the computer
- **No admin access**: Cannot modify system settings
- **Auto-expiring**: Sessions automatically timeout

## 📞 Support

**Controller Website**: https://web-production-463b89.up.railway.app

**For Problems**:
1. Try `run-agent.bat` first (does full setup)
2. Check that Python is installed
3. Verify internet connection works
4. Make sure Session ID is copied correctly

---

**This package works on ANY Windows computer with Python installed!** 🎉
