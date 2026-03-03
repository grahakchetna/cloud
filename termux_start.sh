#!/bin/bash
# 🤖 Termux Startup Script for grahakchetna
# This script handles setup and launches the Flask app on Termux

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

# Configuration
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${APP_DIR}/termux_app.log"
PORT=${FLASK_PORT:-5002}
HOST="0.0.0.0"

print_header() {
    echo -e "${BOLD}${BLUE}================================================================${NC}"
    echo -e "${BOLD}${BLUE}🤖 TERMUX APPLICATION LAUNCHER${NC}"
    echo -e "${BOLD}${BLUE}================================================================${NC}"
}

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

check_requirements() {
    echo -e "\n${BOLD}Checking requirements...${NC}"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 not found. Run: pkg install python3"
        return 1
    fi
    print_status "Python3 available"
    
    # Check FFmpeg
    if ! command -v ffmpeg &> /dev/null; then
        print_error "FFmpeg not found. Run: pkg install ffmpeg"
        return 1
    fi
    print_status "FFmpeg available"
    
    # Check if app.py exists
    if [ ! -f "${APP_DIR}/app.py" ]; then
        print_error "app.py not found in ${APP_DIR}"
        return 1
    fi
    print_status "app.py found"
    
    # Check for assets
    if [ ! -d "${APP_DIR}/assets" ]; then
        print_warn "assets/ directory not found - will be created"
    fi
    
    return 0
}

setup_environment() {
    echo -e "\n${BOLD}Setting up environment...${NC}"
    
    # Create necessary directories
    mkdir -p "${APP_DIR}/assets"
    mkdir -p "${APP_DIR}/static"
    mkdir -p "${APP_DIR}/uploads"
    mkdir -p "${APP_DIR}/videos"
    mkdir -p "${APP_DIR}/output"
    
    print_status "Directories created"
    
    # Check .env file
    if [ ! -f "${APP_DIR}/.env" ]; then
        print_warn ".env file not found - creating minimal config"
        cat > "${APP_DIR}/.env" << 'EOF'
# Minimal Termux Configuration
FLASK_SECRET_KEY=termux_dev_secret_$(date +%s)
EMAIL_SUPPORT=admin@example.com
EOF
        chmod 600 "${APP_DIR}/.env"
        print_status ".env created with defaults"
    else
        print_status ".env file exists"
    fi
}

verify_python_packages() {
    echo -e "\n${BOLD}Checking Python packages...${NC}"
    
    local missing_packages=""
    
    # Check critical packages
    if ! python3 -c "import flask" 2>/dev/null; then
        missing_packages="${missing_packages} flask"
    else
        print_status "flask installed"
    fi
    
    if ! python3 -c "import moviepy" 2>/dev/null; then
        missing_packages="${missing_packages} moviepy"
    else
        print_status "moviepy installed"
    fi
    
    if ! python3 -c "from PIL import Image" 2>/dev/null; then
        missing_packages="${missing_packages} Pillow"
    else
        print_status "Pillow installed"
    fi
    
    if [ -n "$missing_packages" ]; then
        print_warn "Missing packages:$missing_packages"
        echo -e "${YELLOW}Installing missing packages...${NC}"
        pip install --no-cache-dir $missing_packages
    fi
}

show_network_info() {
    echo -e "\n${BOLD}Network Information:${NC}"
    
    # Get IP addresses
    if command -v hostname &> /dev/null; then
        local hostname=$(hostname -I 2>/dev/null || echo "N/A")
        print_status "Hostname: $hostname"
    fi
    
    # Try to get current IP
    if command -v ip &> /dev/null; then
        local ip=$(ip addr show | grep "inet " | grep -v "127.0.0.1" | awk '{print $2}' | cut -d'/' -f1 | head -1)
        if [ -n "$ip" ]; then
            print_status "Device IP: $ip"
        fi
    fi
    
    print_status "Flask will listen on: ${HOST}:${PORT}"
    print_status "Access from browser: http://localhost:${PORT} (on device)"
}

show_app_info() {
    echo -e "\n${BOLD}${GREEN}Application Ready!${NC}"
    echo -e "\n${BOLD}Access Points:${NC}"
    echo -e "  ${GREEN}http://127.0.0.1:${PORT}${NC} - Local device"
    echo -e "  ${GREEN}http://0.0.0.0:${PORT}${NC} - Network access"
    
    echo -e "\n${BOLD}Available Routes:${NC}"
    echo -e "  ${GREEN}/${NC} - Home page"
    echo -e "  ${GREEN}/short${NC} - Short video generator"
    echo -e "  ${GREEN}/long${NC} - Long video generator"
    echo -e "  ${GREEN}/videos${NC} - Video gallery"
    echo -e "  ${GREEN}/settings${NC} - Configuration"
    
    echo -e "\n${BOLD}Quick Actions:${NC}"
    echo -e "  Press ${BOLD}Ctrl+C${NC} to stop the server"
    echo -e "  View logs: ${BOLD}tail -f ${LOG_FILE}${NC}"
    
    echo -e "\n${YELLOW}⚠ NOTE:${NC} Keep this terminal open while using the app"
}

start_app() {
    echo -e "\n${BOLD}${GREEN}Starting Flask Application...${NC}"
    echo -e "${BLUE}Time: $(date)${NC}\n"
    
    # Ensure PORT is a number
    if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
        print_error "Invalid port: $PORT. Using default 5002"
        PORT=5002
    fi
    
    # Start Flask app with environment variables
    cd "${APP_DIR}"
    
    # Export Flask variables
    export FLASK_APP="app.py"
    export FLASK_ENV="production"
    export FLASK_PORT="${PORT}"
    export PORT="${PORT}"
    
    # Log startup info
    {
        echo "=== Termux Flask App Startup ==="
        echo "Time: $(date)"
        echo "Directory: ${APP_DIR}"
        echo "Port: ${PORT}"
        echo "Python: $(python3 --version)"
        echo "FFmpeg: $(ffmpeg -version | head -n1)"
        echo "================================"
    } | tee -a "${LOG_FILE}"
    
    # Run the Flask app
    python3 app.py 2>&1 | tee -a "${LOG_FILE}"
}

main() {
    print_header
    
    # Run all setup steps
    if ! check_requirements; then
        print_error "Requirements check failed"
        exit 1
    fi
    
    setup_environment
    verify_python_packages
    show_network_info
    show_app_info
    start_app
}

# Run main
main
