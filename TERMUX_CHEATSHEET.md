# 📋 Termux Quick Reference Card

## ❌ Your Error
```
Failed to find two consecutive MPEG audio frames
```

## ✅ The Fix (Copy & Paste)
```bash
mkdir -p assets && ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 30 -q:a 9 -acodec libmp3lame assets/music.mp3
```

---

## 📱 Full Setup (Just Copy Each Line)

```bash
# 1. Update and install basics
pkg update && pkg install python3 git ffmpeg imagemagick

# 2. Clone repo
git clone https://github.com/grahakchetna/cloud.git
cd cloud

# 3. FIX THE AUDIO ERROR (THIS IS THE KEY)
mkdir -p assets
ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 30 -q:a 9 -acodec libmp3lame assets/music.mp3

# 4. Install Python packages
pip install -r requirements.txt

# 5. Setup config
echo "GROQ_API_KEY=your-api-key" > .env

# 6. Run
python3 app.py
```

---

## 🔍 Verify Setup
```bash
python3 termux_verify_setup.py
```

---

## 🌐 Open App
```
http://localhost:5000
```

---

## 📚 Need More Help?

| Question | Read This |
|----------|-----------|
| Just want it working? | [TERMUX_ONE_LINERS.md](TERMUX_ONE_LINERS.md) |
| Getting audio errors? | [TERMUX_AUDIO_ERROR_FIX.md](TERMUX_AUDIO_ERROR_FIX.md) |
| Want full guide? | [TERMUX_SETUP.md](TERMUX_SETUP.md) |
| Setup broken? | Run `python3 termux_verify_setup.py` |

---

## ⚙️ Common Commands

```bash
# Check if music file is valid
ffmpeg -i assets/music.mp3

# Clear Python cache
pip cache purge

# Reinstall packages
pip install --force-reinstall -r requirements.txt

# Check storage
df -h

# Stop the app
Ctrl+C
```

---

**That's it! Your app will work after running the fix command.** 🎉
