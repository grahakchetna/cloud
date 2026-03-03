# 🚀 Termux - One-Line Fixes

## Your Error
```
Failed to find two consecutive MPEG audio frames
```

## The Fix
```bash
# Copy ONE of these commands and run in your Termux terminal:

# QUICKEST FIX - Create silent MP3 placeholder
mkdir -p assets && ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 30 -q:a 9 -acodec libmp3lame assets/music.mp3

# Full setup from scratch
pkg update && pkg install python3 git ffmpeg imagemagick && git clone https://github.com/grahakchetna/cloud.git && cd cloud && mkdir -p assets && ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 30 -q:a 9 -acodec libmp3lame assets/music.mp3 && pip install -r requirements.txt && echo "GROQ_API_KEY=your-key" > .env && python3 app.py
```

---

## Step-by-Step in Termux

```bash
# Step 1: Install system deps
pkg update && pkg install ffmpeg imagemagick python3 git

# Step 2: Clean up old repo if needed
rm -rf cloud

# Step 3: Clone and enter
git clone https://github.com/grahakchetna/cloud.git
cd cloud

# Step 4: Fix the audio file (THIS IS THE MAIN FIX)
mkdir -p assets
ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 30 -q:a 9 -acodec libmp3lame assets/music.mp3

# Step 5: Install Python packages  
pip install -r requirements.txt

# Step 6: Create config
echo "GROQ_API_KEY=your-actual-api-key" > .env

# Step 7: Run!
python3 app.py
```

---

## One-Command Full Setup (Copy & Paste)
```bash
pkg update && pkg install python3 git ffmpeg && git clone https://github.com/grahakchetna/cloud.git && cd cloud && mkdir -p assets && ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 30 -q:a 9 -acodec libmp3lame assets/music.mp3 && pip install -r requirements.txt && echo "GROQ_API_KEY=your-key-here" > .env && python3 termux_verify_setup.py
```

---

## Verify It Works
```bash
python3 termux_verify_setup.py
```

---

## Run the App
```bash
python3 app.py
```

Then open: **http://localhost:5000**

---

✅ Done! Videos will generate without errors now.
