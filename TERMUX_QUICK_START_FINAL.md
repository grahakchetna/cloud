# 🤖 Termux Quick Start Guide

**TL;DR - Get Running in 5 Minutes**

```bash
# 1. Install system packages (first time only)
pkg update && pkg install python3 git ffmpeg imagemagick

# 2. Clone the project
git clone https://github.com/gaathatech/grahakchetna.git
cd grahakchetna

# 3. Install Python packages (auto-downloads requirements)
pip install --no-cache-dir -r requirements.txt

# 4. Verify setup (optional but recommended)
python3 termux_check_complete.py

# 5. Start the app
./termux_start.sh

# 6. Open browser on your phone
# Visit: http://localhost:5002
```

---

## ✅ What Your App Needs on Termux

### System Tools (Essential)
```bash
pkg install python3      # Python runtime
pkg install ffmpeg       # Video encoding (CRITICAL)
pkg install git          # Version control
pkg install imagemagick  # Image processing
```

### Python Packages (Auto-installed)
The following are in `requirements.txt` and auto-install via `pip`:
- `flask` - Web server
- `moviepy` - Video composition  
- `Pillow` - Image processing
- `edge-tts` - Text-to-speech
- `requests` - HTTP client
- `python-dotenv` - Environment config

### Asset Files (In `assets/` folder)
```
assets/
├── bg.mp4        (Background video loop)
└── music.mp3     (Background music - optional)
```

### Static Files (In `static/` folder)
```
static/
├── anchor.png    (News anchor image)
└── logo.jpg      (Channel logo)
```

---

## 🚀 Startup Options

### Option 1: Automated Startup (Recommended)
```bash
./termux_start.sh
```
- ✅ Automatic environment setup
- ✅ Dependency verification
- ✅ Detailed logging
- ✅ Network info display

### Option 2: Manual Startup
```bash
python3 app.py
```
- Starts Flask on `localhost:5002`
- Less verbose output

### Option 3: Custom Port
```bash
FLASK_PORT=8080 python3 app.py
# or
PORT=8080 python3 app.py
```

---

## 🔍 System Verification

### Run Complete System Check
```bash
python3 termux_check_complete.py
```

This checks:
- ✓ System environment (Termux detection)
- ✓ Required commands (python3, ffmpeg, git, imagemagick)
- ✓ Python packages (flask, moviepy, etc.)
- ✓ Asset files (bg.mp4, music.mp3, logos)
- ✓ Font availability
- ✓ Directory structure
- ✓ Configuration (.env file)
- ✓ Network connectivity
- ✓ Disk space
- ✓ RAM availability

### Quick System Commands
```bash
# Check Python version
python3 --version

# Check FFmpeg version
ffmpeg -version

# Check available disk space
df -h .

# Check available RAM
free -h

# Test internet connection
ping -c 1 8.8.8.8
```

---

## 📱 Access Your App

### From Your TermuxDevice
```
http://localhost:5002
```

### From Another Device on Same Network
1. Find your phone's IP:
   ```bash
   hostname -I  # or  ip addr show
   ```
2. Visit from computer/tablet:
   ```
   http://YOUR_PHONE_IP:5002
   ```

### Network Troubleshooting
```bash
# If "Connection refused"
# - Check Flask is still running in the Termux window
# - Try http://127.0.0.1:5002 instead

# If "Network unreachable"
# - Both devices must be on same WiFi
# - Check phone's WiFi is connected
# - Check firewall isn't blocking port 5002
```

---

## 🎬 Using the App

### Short Videos (15 seconds)
1. Go to `http://localhost:5002/short`
2. Fill in:
   - **Headline**: Your news headline
   - **Description**: Detailed description
   - **Language**: English/Hindi/Gujarati
   - **Media** (optional): Upload images or videos
3. Click "Generate Video"
4. Wait 30-90 seconds
5. Download from `/videos/` directory

### Long Videos (30+ seconds)
1. Go to `http://localhost:5002/long`
2. Fill in same details as above
3. Generate and download

### View Gallery
- Go to `http://localhost:5002/videos`
- View all generated videos
- Download any video

---

## ⚠️ Common Issues & Fixes

### ❌ "FFmpeg not found"
```bash
pkg install ffmpeg
```

### ❌ "Pillow installation fails"
```bash
# Install system dependencies first
pkg install libjpeg-turbo libpng

# Then try again
pip install Pillow --no-cache-dir
```

### ❌ "Permission denied" on /data/data/com.termux
```bash
# This is normal - Termux handles permissions automatically
# If it persists, run:
termux-fix-permissions
```

### ❌ "Python: ModuleNotFoundError"
```bash
# Check which modules are missing
python3 -c "import flask"

# If missing, install from requirements.txt
pip install --no-cache-dir flask
```

### ❌ "Cannot allocate memory" during video generation
- Device has insufficient RAM
- Try closing other apps first
- Generate shorter videos
- Use smaller media files

### ❌ "Connection refused" when opening browser
```bash
# Check if Flask is still running
# It should show "Running on http://0.0.0.0:5002"

# If not shown:
# 1. Scroll up in Termux to see error message
# 2. Check system requirements (FFmpeg, Python)
# 3. Run: python3 termux_check_complete.py
```

### ❌ ".env file not found" warning
- Create it:
  ```bash
  cat > .env << 'EOF'
  FLASK_SECRET_KEY=your-secret-key-here
  EMAIL_SUPPORT=admin@example.com
  EOF
  ```

---

## 💡 Performance Tips

1. **Smaller is Faster**
   - Use smaller resolution images/videos
   - Keep video duration under 2 minutes
   - Compress media before uploading

2. **Device Management**
   - Close other apps before generating videos
   - Don't use device during encoding
   - Ensure good WiFi signal

3. **Background Processing**
   - Video generation blocks the device
   - Plan to run at non-busy times
   - Generate videos overnight if possible

4. **Storage Management**
   - Generated videos take 1-10 MB each
   - Check free space: `df -h .`
   - Clean up old videos: `rm videos/*.mp4`

---

## 📖 Directory Structure

```
grahakchetna/
├── termux_start.sh              ← Start script
├── termux_check_complete.py     ← System checker  
├── app.py                        ← Flask main app
├── requirements.txt              ← Python dependencies
├── .env                          ← Configuration (create if missing)
├── assets/
│   ├── bg.mp4                   ← Background video
│   └── music.mp3                ← Background music
├── static/
│   ├── anchor.png               ← Anchor image
│   └── logo.jpg                 ← Logo image
├── templates/
│   ├── short.html               ← Short video UI
│   ├── long.html                ← Long video UI
│   └── base.html                ← Base template
├── videos/                       ← Generated videos (auto-created)
├── uploads/                      ← Uploaded media (auto-created)
└── output/                       ← TTS audio (auto-created)
```

---

## 🔐 Security Notes

1. **Keep API Keys Private**
   - Never share your .env file
   - Never commit .env to Git
   - Change keys if exposed

2. **Network Access**
   - Your app is accessible to anyone on your WiFi
   - Consider hostname authentication for shared networks
   - Don't expose 5002 to public internet

3. **File Permissions**
   - Uploads directory is readable by web app
   - Videos directory should be writable
   - Use `termux-fix-permissions` if issues

---

## 📞 Support & Troubleshooting

### Get System Info (for debugging)
```bash
python3 << 'EOF'
import sys
import platform
import shutil

print("System Info:")
print(f"Python: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"FFmpeg: {shutil.which('ffmpeg')}")
print(f"ImageMagick: {shutil.which('convert')}")

# Test imports
try:
    import flask; print(f"Flask: installed")
except: print("Flask: NOT FOUND")

try:
    import moviepy; print("MoviePy: installed")  
except: print("MoviePy: NOT FOUND")
EOF
```

### View Application Logs
```bash
# Real-time logs
tail -f termux_app.log

# Last 50 lines
tail -n 50 termux_app.log

# Search for errors
grep -i error termux_app.log
```

---

## ✨ Features

- ✅ **Short Videos** (1080x1920, 15-30 sec)
- ✅ **Long Videos** (1920x1080, 30+ sec)
- ✅ **Multiple Languages** (English, Hindi, Gujarati)
- ✅ **TTS Narration** (AI-generated anchor)
- ✅ **Media Upload** (images and videos)
- ✅ **Auto Layout** (responsive design)
- ✅ **Video Gallery** (organized video management)
- ✅ **Social Export** (ready for Instagram/YouTube)

---

## 📝 Notes

- First startup takes **1-2 minutes** (dependency checks)
- Video generation takes **30-120 seconds** per video
- Generated videos are saved in `/videos/` directory
- Keep Termux running while accessing the app
- Press `Ctrl+C` to stop the server

---

**Last Updated:** March 3, 2026  
**Status:** ✅ Ready for Termux  
**Tested On:** Termux 0.x with Python 3.12, FFmpeg 8.0
