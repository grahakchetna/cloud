# ⚡ Termux Quick Fix Guide

## 🔴 Your Current Error
```
MoviePy error: failed to read the duration of file assets/music.mp3
[mp3] Failed to find two consecutive MPEG audio frames
```

**This means:** Your `assets/music.mp3` file is corrupted or invalid.

---

## ✅ Solution (Copy & Paste in Termux)

### Step 1: Install Dependencies (if not already done)
```bash
pkg update && pkg upgrade
pkg install python3 git ffmpeg imagemagick libjpeg-turbo libpng
```

### Step 2: Clone the Repository (if not already done)
```bash
git clone https://github.com/grahakchetna/cloud.git
cd cloud
```

### Step 3: Create Valid Asset Files

**Option A: Quick Fix (Create Silent Placeholder)**
```bash
mkdir -p assets
# Create a simple silent MP3 file (app will use voice-only, which works fine)
ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 30 -q:a 9 -acodec libmp3lame assets/music.mp3
```

**Option B: Use Existing Valid MP3**
```bash
# If you have a valid MP3 file, copy it to assets/
cp /path/to/your/valid-music.mp3 assets/music.mp3
```

### Step 4: Install Python Dependencies
```bash
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt
```

### Step 5: Create .env File
```bash
cat > .env << 'EOF'
GROQ_API_KEY=your-api-key-here
EOF
chmod 600 .env
```

### Step 6: Run the App
```bash
python3 app.py
```

---

## 🛠️ Verify Your Setup

Run this script to check everything:
```bash
bash termux_verify_setup.sh
```

Or manually test the music file:
```bash
ffmpeg -i assets/music.mp3
```

---

## 📱 Common Termux Issues & Fixes

| Problem | Solution |
|---------|----------|
| `pip: command not found` | `apt install pip` or use `python3 -m pip` |
| `Pillow installation fails` | `pip install Pillow --no-binary :all: --force-reinstall` |
| `slow installation` | Add `--no-cache-dir` flag to pip commands |
| `Git LFS not available` | Manual download with curl/wget (see guide) |
| `ffmpeg timeout/hang` | Kill it with Ctrl+C, reduce video resolution |

---

## 🎬 Running Your First Video

Once setup is complete:
```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "headline": "Test Video",
    "description": "This is a test",
    "language": "english"
  }'
```

Or use the web UI:
```
http://localhost:5000
```

---

## ❓ Still Having Issues?

1. **Check the logs** - Look for error messages above
2. **Verify ffmpeg** - `ffmpeg -version`
3. **Test music.mp3** - `ffmpeg -i assets/music.mp3`
4. **Check storage** - `df -h` (need ~2GB free)
5. **Check RAM** - Devices with <2GB RAM may fail

---

## 📚 Full Documentation
- See [TERMUX_SETUP.md](TERMUX_SETUP.md) for detailed guide
- See [README.md](README.md) for feature list
