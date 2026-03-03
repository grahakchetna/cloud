#!/bin/bash
# Termux Setup Verification & Fix Script
# Run this after cloning to verify everything is working

echo "🔍 Verifying Termux Setup..."
echo "================================"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo -n "✓ Python 3: "
if command -v python3 &> /dev/null; then
    python3 --version
else
    echo -e "${RED}NOT INSTALLED${NC}"
    echo "  Fix: pkg install python3"
fi

# Check FFmpeg
echo -n "✓ FFmpeg: "
if command -v ffmpeg &> /dev/null; then
    ffmpeg -version | head -n 1
else
    echo -e "${RED}NOT INSTALLED${NC}"
    echo "  Fix: pkg install ffmpeg"
fi

# Check Git
echo -n "✓ Git: "
if command -v git &> /dev/null; then
    git --version
else
    echo -e "${RED}NOT INSTALLED${NC}"
    echo "  Fix: pkg install git"
fi

# Check ImageMagick
echo -n "✓ ImageMagick: "
if command -v convert &> /dev/null; then
    convert --version | head -n 1
else
    echo -e "${RED}NOT INSTALLED${NC}"
    echo "  Fix: pkg install imagemagick"
fi

echo ""
echo "🎵 Asset Files Check:"
echo "================================"

# Check assets folder
if [ -d "assets" ]; then
    echo -e "${GREEN}✓${NC} assets/ folder exists"
    
    # Check bg.mp4
    if [ -f "assets/bg.mp4" ]; then
        size=$(du -h assets/bg.mp4 | cut -f1)
        echo -e "${GREEN}✓${NC} assets/bg.mp4 exists ($size)"
    else
        echo -e "${RED}✗${NC} assets/bg.mp4 MISSING"
    fi
    
    # Check music.mp3
    if [ -f "assets/music.mp3" ]; then
        size=$(du -h assets/music.mp3 | cut -f1)
        # Test if MP3 is valid
        if ffmpeg -i assets/music.mp3 -f null - 2>&1 | grep -q "Duration"; then
            echo -e "${GREEN}✓${NC} assets/music.mp3 exists and is VALID ($size)"
        else
            echo -e "${YELLOW}⚠${NC} assets/music.mp3 exists but may be CORRUPTED"
            echo "  Fix: ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 10 -q:a 9 -acodec libmp3lame assets/music.mp3"
        fi
    else
        echo -e "${YELLOW}⚠${NC} assets/music.mp3 MISSING (app will use voice-only)"
        echo "  Fix: ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 10 -q:a 9 -acodec libmp3lame assets/music.mp3"
    fi
else
    echo -e "${RED}✗${NC} assets/ folder MISSING"
    echo "  Creating assets folder..."
    mkdir -p assets
    echo "  Now create music.mp3:"
    echo "  ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 10 -q:a 9 -acodec libmp3lame assets/music.mp3"
fi

echo ""
echo "🐍 Python Dependencies Check:"
echo "================================"

if [ -f "requirements.txt" ]; then
    echo "Checking required packages..."
    
    packages=("flask" "moviepy" "pydub" "pillow" "requests" "edge-tts")
    
    for pkg in "${packages[@]}"; do
        if python3 -c "import ${pkg//-/_}" 2>/dev/null; then
            echo -e "${GREEN}✓${NC} $pkg"
        else
            echo -e "${RED}✗${NC} $pkg NOT INSTALLED"
        fi
    done
else
    echo "requirements.txt not found!"
fi

echo ""
echo "📝 Quick Fixes Available:"
echo "================================"

echo "1. Fix corrupted music.mp3:"
echo "   ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 10 -q:a 9 -acodec libmp3lame assets/music.mp3"
echo ""
echo "2. Install all dependencies:"
echo "   pip install --no-cache-dir -r requirements.txt"
echo ""
echo "3. Run the app:"
echo "   python3 app.py"
echo ""
echo "================================"
echo "✅ Verification Complete!"
