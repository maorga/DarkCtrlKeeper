# DarkCtrlKeeper Quick Start Guide

Get up and running with DarkCtrlKeeper in 5 minutes!

---

## 🚀 Quick Start (For Users)

### Option 1: Download Pre-Built Executable (Easiest)

1. **Download the latest release:**
   - Go to [GitHub Releases](https://github.com/yourusername/DarkCtrlKeeper/releases)
   - Download `DarkCtrlKeeper_v1.0.0.zip`

2. **Extract the zip file:**
   ```powershell
   Expand-Archive -Path DarkCtrlKeeper_v1.0.0.zip -DestinationPath C:\Games\DarkCtrlKeeper
   ```

3. **Run the application:**
   - Double-click `DarkCtrlKeeper.exe`
   - Click "Yes" when Windows asks for administrator privileges
   - Done! The app is now running

4. **Using the app:**
   - **Lock CTRL:** Click "Lock" button
   - **Release CTRL:** Click "Release" button
   - **Close:** Click the red X in the top-right corner

---

### Option 2: Run from Source (For Developers)

1. **Clone the repository:**
   ```powershell
   git clone https://github.com/yourusername/DarkCtrlKeeper.git
   cd DarkCtrlKeeper
   ```

2. **Create virtual environment:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```powershell
   python src/main.py
   ```

---

## 🎮 Basic Usage

### Main Features

1. **Lock CTRL Key:**
   - Click the "Lock CTRL" button (left button)
   - Status changes to "CTRL IS PRESSED" (red)
   - CTRL key is now held down continuously

2. **Release CTRL Key:**
   - Click the "Release CTRL" button (right button)
   - Status changes to "CTRL IS RELEASED" (green)
   - CTRL key is no longer held

3. **Greater Fortitude Tracking:**
   - Select your hotkey: **4** or **5**
   - Press your selected key in MU Online
   - Countdown resets to 60.0 seconds
   - Timer counts down and alerts when buff expires

4. **Countdown Controls:**
   - **STOP:** Pause the countdown
   - **RESUME:** Continue counting from current time
   - **RESET:** Manually reset to 60.0 seconds

---

## 🎯 Typical MU Online Workflow

1. **Start the game:**
   - Launch MU Online
   - Launch DarkCtrlKeeper

2. **Lock CTRL for attack:**
   - Click "Lock CTRL" button to lock CTRL
   - Your character auto-attacks continuously
   - Status shows "CTRL IS PRESSED" (red)

3. **Cast Greater Fortitude:**
   - Press **4** or **5** (your buff hotkey)
   - Countdown resets to 60.0 seconds
   - Timer starts counting down

4. **Monitor buff duration:**
   - Green: 60-30 seconds (safe)
   - Yellow: 30-10 seconds (prepare to rebuff)
   - Red: 10-0 seconds (rebuff NOW!)
   - **BUFF** alert: Buff expired!

5. **Release CTRL when needed:**
   - Click "Release CTRL" button to release CTRL
   - Character stops auto-attacking
   - Status shows "CTRL IS RELEASED" (green)

---

## 🔧 Configuration (Optional)

### Enable Analytics (Optional)

1. **Copy the template:**
   ```powershell
   Copy-Item .env.example .env
   ```

2. **Edit .env file:**
   ```bash
   GA4_MEASUREMENT_ID=G-XXXXXXXXXX
   GA4_API_SECRET=your_secret_here
   ```

3. **Get credentials:**
   - See `docs/GA4_TRACKING_GUIDE.md` for detailed instructions

4. **Restart the app:**
   - Analytics will now track usage events

**Note:** Analytics is completely optional. The app works perfectly without it.

---

## ❓ Troubleshooting

### Application won't start

**Problem:** Double-clicking does nothing or shows error.

**Solutions:**
```powershell
# Check if Python is installed (for source version)
python --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Run from terminal to see error messages
python src/main.py
```

---

### "Administrator privileges required"

**Problem:** Windows blocks the application.

**Solutions:**
1. Right-click `DarkCtrlKeeper.exe` → Run as Administrator
2. This is normal - keyboard control requires admin access
3. Click "Yes" on the UAC prompt

---

### CTRL key is stuck

**Problem:** CTRL key stays pressed after closing the app.

**Solutions:**
```powershell
# Press CTRL key manually to reset
# OR run this PowerShell command:
[System.Windows.Forms.SendKeys]::SendWait("{CTRL}")

# To prevent: Always use the Release button before closing
```

---

### Antivirus blocks the app

**Problem:** Antivirus flags DarkCtrlKeeper as malware.

**Why:** Keyboard control is flagged as potential keylogger.

**Solutions:**
1. Add exception in your antivirus
2. Download from official GitHub releases only
3. Build from source yourself (see below)
4. Check SHA256 hash matches release notes

---

## 🏗️ Building from Source

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Windows OS (for full functionality)

### Build Steps

1. **Clone and setup:**
   ```powershell
   git clone https://github.com/yourusername/DarkCtrlKeeper.git
   cd DarkCtrlKeeper
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   pip install pyinstaller
   ```

2. **Build executable:**
   ```powershell
   python scripts/build.py
   ```

3. **Find executable:**
   ```
   dist/DarkCtrlKeeper/DarkCtrlKeeper.exe
   ```

4. **Distribute:**
   - Zip the entire `dist/DarkCtrlKeeper` folder
   - Share the zip file

---

## 📖 More Information

- **Full User Guide:** `USAGE.md`
- **Analytics Setup:** `docs/GA4_TRACKING_GUIDE.md`
- **Security:** `docs/SECURITY.md`
- **Development:** `README.md`
- **Changelog:** `CHANGELOG.md`

---

## 🆘 Getting Help

1. **Check documentation:**
   - Read `USAGE.md` for detailed instructions
   - Check troubleshooting sections

2. **Search existing issues:**
   - [GitHub Issues](https://github.com/yourusername/DarkCtrlKeeper/issues)

3. **Create new issue:**
   - Describe your problem clearly
   - Include error messages
   - Mention your Python/Windows version

4. **Community:**
   - (Add Discord/Reddit links if available)

---

## ⚡ Tips & Tricks

### Tip 1: Positioning the Window
- Drag the window anywhere on screen
- Stays on top of all windows
- Position near your MU Online window for easy visibility

### Tip 2: Countdown Strategy
- Start locking CTRL immediately after the first buff
- Rebuff at ~5 seconds remaining (yellow zone)
- Never let it reach red zone during combat

### Tip 3: Analytics Privacy
- Want analytics? Create `.env` file
- Don't want analytics? Don't create `.env`
- No performance difference either way

### Tip 4: Multiple Accounts
- Run multiple instances for multiple accounts
- Each window tracks its own buff timer
- Use different positions on screen

---

## 🎉 You're Ready!

DarkCtrlKeeper is now set up and ready to use. Enjoy your MU Online gaming!

**Lock CTRL → Cast Buff (4/5) → Watch Timer → Rebuff Before 0 → Profit! 🎮**

---

**Version:** 1.0.0  
**Last Updated:** November 12, 2025  
**License:** MIT
