# Termux Audio File Error - Complete Fix Guide

## 🔴 Error Found in Your Logs

```
MoviePy error: failed to read the duration of file assets/music.mp3
[mp3 @ 0xb400007662980280] Failed to find two consecutive MPEG audio frames
Error opening input file assets/music.mp3
Invalid data found when processing input
```

---

## ✅ What This Means

Your `assets/music.mp3` file is **corrupted or invalid**. The FFmpeg audio codec can't parse the MP3 frames.

**Good news:** Your app handles this gracefully with the message:
```
INFO:video_service:Continuing with voice audio only
```

So videos will still be generated, just without background music.

---

## 🛠️ Quick Fixes (Choose One)

### **Fix 1: Create a Silent Placeholder MP3** (⭐ Recommended - Quickest)
```bash
cd /path/to/grahakchetna
mkdir -p assets
ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 30 -q:a 9 -acodec libmp3lame assets/music.mp3
```
✨ **Result:** App runs perfectly with voice-only audio (which is the fallback anyway)

---

### **Fix 2: Verify/Test Your Current Music File**
```bash
ffmpeg -i assets/music.mp3
```

If you see errors, the file is corrupted. Delete and recreate it using Fix 1.

---

### **Fix 3: Copy From Another Device**
If you have a valid MP3 file on your desktop:
```bash
# On your desktop/laptop:
scp /path/to/valid-music.mp3 termux-user@YOUR_PHONE_IP:/path/to/grahakchetna/assets/

# Or with rsync:
rsync -avz /path/to/valid-music.mp3 termux-user@YOUR_PHONE_IP:/path/to/grahakchetna/assets/
```

---

## 📋 Complete Termux Setup Checklist

```bash
# 1. Install system packages
pkg update && pkg upgrade
pkg install python3 git ffmpeg imagemagick libjpeg-turbo libpng

# 2. Clone repository
git clone https://github.com/grahakchetna/cloud.git
cd cloud

# 3. Create assets folder and fix music file
mkdir -p assets
ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 30 -q:a 9 -acodec libmp3lame assets/music.mp3

# 4. Install Python dependencies
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt

# 5. Create environment file
echo "GROQ_API_KEY=your-api-key-here" > .env
chmod 600 .env

# 6. Verify setup
python3 termux_verify_setup.py

# 7. Run the app
python3 app.py
```

---

## 🔍 Verification Scripts

We've created two verification scripts to help you:

### **Option A: Python Script** (Works on all systems)
```bash
python3 termux_verify_setup.py
```
Shows a detailed report of your setup status

### **Option B: Bash Script** (For Linux/Termux)  
```bash
bash termux_verify_setup.sh
```
Shows system info and asset status

---

## 🎬 Test Your Setup

Once fixed, test video generation:

```bash
# Method 1: Web UI
python3 app.py
# Then open: http://localhost:5000

# Method 2: Command line
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "headline": "Test Video",
    "description": "Testing the system",
    "language": "english"
  }'
```

---

## 🆘 If You Still Have Issues

1. **Check FFmpeg installation:**
   ```bash
   ffmpeg -version
   ```

2. **Clear pip cache:**
   ```bash
   pip cache purge
   ```

3. **Reinstall requirements:**
   ```bash
   pip install --force-reinstall --no-cache-dir -r requirements.txt
   ```

4. **Check available storage:**
   ```bash
   df -h
   # Need at least 2GB free
   ```

5. **Check RAM usage:**
   ```bash
   free -h
   # Movies process requires RAM, min 512MB recommended
   ```

---

## 📚 Additional Resources

- [Full Termux Setup Guide](TERMUX_SETUP.md) - Detailed installation
- [Quick Start Guide](QUICK_START.md) - General usage
- [Main README](README.md) - Features overview

---

## ✨ Summary

Your error is **easily fixed** by running:
```bash
ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 30 -q:a 9 -acodec libmp3lame assets/music.mp3
```

This creates a valid MP3 file, and your app will work perfectly! 🎉
