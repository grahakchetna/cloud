#!/usr/bin/env python3
"""
🤖 TERMUX COMPREHENSIVE SYSTEM CHECK
Complete validation for running grahakchetna on Termux
Author: Senior Dev Assistant
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path
from datetime import datetime

class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

class TermuxSystemValidator:
    def __init__(self):
        self.results = {"pass": [], "warn": [], "fail": []}
        self.is_termux = os.path.exists("/data/data/com.termux")
        self.passed = 0
        self.warned = 0
        self.failed = 0
        
    def log(self, level, message):
        """Log with color"""
        if level == "pass":
            print(f"{Colors.GREEN}✓{Colors.RESET} {message}")
            self.passed += 1
            self.results["pass"].append(message)
        elif level == "warn":
            print(f"{Colors.YELLOW}⚠{Colors.RESET} {message}")
            self.warned += 1
            self.results["warn"].append(message)
        elif level == "fail":
            print(f"{Colors.RED}✗{Colors.RESET} {message}")
            self.failed += 1
            self.results["fail"].append(message)
        elif level == "info":
            print(f"{Colors.BLUE}ℹ{Colors.RESET} {message}")
        elif level == "header":
            print(f"\n{Colors.BOLD}{Colors.BLUE}{message}{Colors.RESET}")

    def cmd_exists(self, cmd):
        """Check if command exists"""
        return shutil.which(cmd) is not None

    def get_cmd_version(self, cmd, flag="--version"):
        """Get version of a command"""
        try:
            result = subprocess.run(
                [cmd, flag],
                capture_output=True,
                timeout=5,
                text=True
            )
            return result.stdout.split('\n')[0] if result.stdout else "installed"
        except:
            return None

    def check_system_environment(self):
        """Check if running on Termux"""
        self.log("header", "📱 ENVIRONMENT DETECTION")
        
        if self.is_termux:
            self.log("pass", "Running on Termux (Android)")
        else:
            self.log("warn", "Not detected as Termux environment (might still work on native Linux)")

    def check_system_commands(self):
        """Verify all required system commands"""
        self.log("header", "📦 SYSTEM COMMANDS")
        
        commands = {
            "python3": "Python 3 runtime",
            "ffmpeg": "Video/Audio encoding (CRITICAL)",
            "git": "Version control",
            "convert": "ImageMagick image processor"
        }
        
        for cmd, desc in commands.items():
            if self.cmd_exists(cmd):
                version = self.get_cmd_version(cmd)
                self.log("pass", f"{cmd}: {version} - {desc}")
            else:
                if cmd == "ffmpeg":
                    self.log("fail", f"{cmd} NOT FOUND - {desc} - Run: pkg install ffmpeg")
                elif cmd == "python3":
                    self.log("fail", f"{cmd} NOT FOUND - {desc}")
                else:
                    self.log("warn", f"{cmd} not found - Optional: pkg install {cmd}")

    def check_python_packages(self):
        """Verify Python package installation"""
        self.log("header", "🐍 PYTHON PACKAGES")
        
        packages = {
            "flask": "Web framework",
            "moviepy": "Video composition (CRITICAL)",
            "Pillow": "Image processing",
            "edge_tts": "Text-to-speech",
            "requests": "HTTP requests",
            "python_dotenv": "Environment config"
        }
        
        for pkg, desc in packages.items():
            try:
                __import__(pkg)
                self.log("pass", f"{pkg}: installed - {desc}")
            except ImportError:
                if pkg in ["moviepy", "Pillow"]:
                    self.log("fail", f"{pkg}: NOT INSTALLED - {desc} - Run: pip install {pkg}")
                else:
                    self.log("warn", f"{pkg}: not found - {desc}")

    def check_asset_files(self):
        """Verify asset files exist and are valid"""
        self.log("header", "🎵 ASSET FILES")
        
        assets = {
            "assets/bg.mp4": "Background video",
            "assets/music.mp3": "Background music",
            "static/anchor.png": "Anchor image",
            "static/logo.jpg": "Logo image"
        }
        
        for path, desc in assets.items():
            if os.path.exists(path):
                size = os.path.getsize(path)
                if size > 0:
                    size_mb = size / 1024 / 1024
                    self.log("pass", f"{path}: {size_mb:.2f}MB - {desc}")
                else:
                    self.log("fail", f"{path}: EMPTY FILE - {desc}")
            else:
                self.log("warn", f"{path}: not found - {desc}")

    def check_fonts(self):
        """Verify font availability for text rendering"""
        self.log("header", "🔤 FONT AVAILABILITY")
        
        font_paths = [
            "/data/data/com.termux/files/usr/share/fonts/TTF",
            "/usr/share/fonts/truetype",
            "/system/fonts"
        ]
        
        found_fonts = []
        for path in font_paths:
            if os.path.exists(path) and os.path.isdir(path):
                fonts = [f for f in os.listdir(path) if f.endswith('.ttf')]
                if fonts:
                    found_fonts.extend(fonts)
        
        if found_fonts:
            self.log("pass", f"Found {len(found_fonts)} TrueType fonts")
        else:
            self.log("warn", "No TrueType fonts found - rendering may use fallbacks")

    def check_directories(self):
        """Verify required directories exist"""
        self.log("header", "📁 DIRECTORY STRUCTURE")
        
        dirs = [
            "assets",
            "static",
            "templates",
            "outputs",
            "uploads",
            "videos"
        ]
        
        for dir_name in dirs:
            if os.path.isdir(dir_name):
                self.log("pass", f"{dir_name}/: exists")
            else:
                os.makedirs(dir_name, exist_ok=True)
                self.log("pass", f"{dir_name}/: created")

    def check_env_file(self):
        """Verify .env file configuration"""
        self.log("header", "⚙️ CONFIGURATION")
        
        if os.path.exists(".env"):
            self.log("pass", ".env file: found")
            # Check if it has content
            with open(".env", "r") as f:
                env_content = f.read().strip()
                if len(env_content) > 20:
                    keys = [line.split('=')[0] for line in env_content.split('\n') if '=' in line]
                    self.log("pass", f".env has {len(keys)} configured keys")
                else:
                    self.log("warn", ".env file is mostly empty")
        else:
            self.log("warn", ".env file: not found - app may run with limited features")

    def check_network_connectivity(self):
        """Check internet connectivity"""
        self.log("header", "🌐 NETWORK CONNECTIVITY")
        
        try:
            result = subprocess.run(
                ["timeout", "3", "ping", "-c", "1", "8.8.8.8"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                self.log("pass", "Internet connectivity: available")
            else:
                self.log("warn", "Internet connectivity: may be limited")
        except:
            self.log("warn", "Could not test internet connectivity")

    def check_disk_space(self):
        """Check available disk space"""
        self.log("header", "💾 DISK SPACE")
        
        try:
            result = subprocess.run(
                ["df", "-h", "."],
                capture_output=True,
                text=True,
                timeout=5
            )
            lines = result.stdout.split('\n')
            if len(lines) > 1:
                info = lines[1].split()
                if len(info) >= 4:
                    available = info[3]
                    self.log("pass", f"Available space: {available}")
        except:
            self.log("warn", "Could not determine disk space")

    def check_memory(self):
        """Check available RAM"""
        self.log("header", "🧠 RAM MEMORY")
        
        try:
            result = subprocess.run(
                ["free", "-h"],
                capture_output=True,
                text=True,
                timeout=5
            )
            lines = result.stdout.split('\n')
            if len(lines) > 1:
                self.log("pass", f"Memory info: {lines[1]}")
        except:
            self.log("warn", "Could not determine available memory")

    def generate_report(self):
        """Generate summary report"""
        self.log("header", "📊 SUMMARY REPORT")
        
        total = self.passed + self.warned + self.failed
        print(f"\n{Colors.GREEN}✓ PASSED:{Colors.RESET} {self.passed}/{total}")
        print(f"{Colors.YELLOW}⚠ WARNING:{Colors.RESET} {self.warned}/{total}")
        print(f"{Colors.RED}✗ FAILED:{Colors.RESET} {self.failed}/{total}")
        
        if self.failed == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✅ YOUR SYSTEM IS READY!{Colors.RESET}")
            print(f"Start the app with: {Colors.BOLD}python3 app.py{Colors.RESET}")
            return 0
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ FIX THE ERRORS ABOVE{Colors.RESET}")
            return 1

    def run(self):
        """Run all checks"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
        print("🤖 TERMUX SYSTEM VERIFICATION")
        print(f"{'='*60}{Colors.RESET}\n")
        
        self.check_system_environment()
        self.check_system_commands()
        self.check_python_packages()
        self.check_asset_files()
        self.check_fonts()
        self.check_directories()
        self.check_env_file()
        self.check_network_connectivity()
        self.check_disk_space()
        self.check_memory()
        
        return self.generate_report()

def main():
    """Main entry point"""
    validator = TermuxSystemValidator()
    exit_code = validator.run()
    
    # Save report to file
    report_file = f"termux_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, "w") as f:
        json.dump(validator.results, f, indent=2)
    print(f"\n💾 Report saved: {report_file}")
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
