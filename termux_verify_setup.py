#!/usr/bin/env python3
"""
Termux Setup Verification Script
Run this to check if your Termux environment is properly configured.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

class TermuxVerifier:
    def __init__(self):
        self.passed = 0
        self.warnings = 0
        self.failed = 0
        
    def check(self, name, condition, error_msg=""):
        status = "✓" if condition else "✗"
        color = "\033[92m" if condition else "\033[91m"
        reset = "\033[0m"
        
        if condition:
            print(f"{color}{status}{reset} {name}")
            self.passed += 1
        else:
            print(f"{color}{status}{reset} {name}")
            if error_msg:
                print(f"  → {error_msg}")
            self.failed += 1
            
    def warn(self, name, msg):
        print(f"\033[93m⚠\033[0m {name}")
        if msg:
            print(f"  → {msg}")
        self.warnings += 1
        
    def command_exists(self, cmd):
        return shutil.which(cmd) is not None
    
    def test_music_file(self):
        """Test if music.mp3 is a valid audio file"""
        if not os.path.exists("assets/music.mp3"):
            return None
        
        try:
            result = subprocess.run(
                ["ffmpeg", "-i", "assets/music.mp3"],
                capture_output=True,
                timeout=5
            )
            stderr = result.stderr.decode('utf-8', errors='ignore')
            return "Duration:" in stderr or "Invalid data" not in stderr
        except:
            return None
    
    def run(self):
        print("\n" + "="*50)
        print("🔍 Termux Environment Verification")
        print("="*50 + "\n")
        
        # System commands
        print("📦 System Commands:")
        self.check("Python 3", self.command_exists("python3"))
        self.check("FFmpeg", self.command_exists("ffmpeg"), 
                  "Run: pkg install ffmpeg")
        self.check("Git", self.command_exists("git"),
                  "Run: pkg install git")
        self.check("ImageMagick", self.command_exists("convert"),
                  "Run: pkg install imagemagick")
        
        # Asset files
        print("\n🎵 Asset Files:")
        assets_exist = os.path.isdir("assets")
        self.check("assets/ folder", assets_exist)
        
        if assets_exist:
            bg_exists = os.path.exists("assets/bg.mp4")
            self.check("assets/bg.mp4", bg_exists,
                      "Download or copy your background video here")
            
            music_exists = os.path.exists("assets/music.mp3")
            if music_exists:
                music_valid = self.test_music_file()
                if music_valid is None:
                    self.warn("assets/music.mp3", 
                             "File may be corrupted. Try: ffmpeg -i assets/music.mp3")
                elif music_valid:
                    self.check("assets/music.mp3", True)
                    self.passed += 1
                else:
                    self.warn("assets/music.mp3",
                             "File is corrupted! Run this to fix:\n"
                             "  ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 30 -q:a 9 "
                             "-acodec libmp3lame assets/music.mp3")
            else:
                self.warn("assets/music.mp3",
                         "Missing (app will work with voice-only)\n"
                         "  Create with: ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 30 "
                         "-q:a 9 -acodec libmp3lame assets/music.mp3")
        
        # Python packages
        print("\n🐍 Python Packages:")
        required = ["flask", "moviepy", "edge_tts", "pillow", "requests"]
        for pkg in required:
            try:
                __import__(pkg.replace("-", "_"))
                self.check(pkg, True)
            except ImportError:
                self.check(pkg, False,
                          "Run: pip install -r requirements.txt")
        
        # Environment
        print("\n📝 Configuration:")
        self.check(".env file exists", os.path.exists(".env"),
                  "Create with: echo 'GROQ_API_KEY=your-key' > .env")
        self.check("requirements.txt exists", os.path.exists("requirements.txt"))
        self.check("app.py exists", os.path.exists("app.py"))
        
        # Storage
        print("\n💾 Storage:")
        try:
            result = subprocess.run(["df", "-h", "."], 
                                   capture_output=True, text=True)
            lines = result.stdout.strip().split("\n")
            if len(lines) > 1:
                parts = lines[1].split()
                free = parts[3] if len(parts) > 3 else "?"
                print(f"✓ Storage: {free} available")
                self.passed += 1
        except:
            print("⚠ Could not check storage")
            self.warnings += 1
        
        # Summary
        print("\n" + "="*50)
        print(f"Results: {self.passed} ✓  {self.warnings} ⚠  {self.failed} ✗")
        print("="*50)
        
        if self.failed > 0:
            print("\n❌ Some checks failed. Please fix the issues above.")
            return False
        elif self.warnings > 0:
            print("\n⚠️  Some warnings detected. See above for details.")
            return True
        else:
            print("\n✅ All checks passed! Ready to run the app.")
            print("   Start with: python3 app.py")
            return True

if __name__ == "__main__":
    verifier = TermuxVerifier()
    success = verifier.run()
    sys.exit(0 if success else 1)
