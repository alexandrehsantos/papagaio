#!/bin/bash
#
# Papagaio - Professional Linux Installer
# Supports: Ubuntu, Debian, Fedora, Arch Linux, openSUSE
#

set -e

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Installation directories
INSTALL_DIR="$HOME/.local/bin/papagaio"
BIN_DIR="$HOME/.local/bin"
CONFIG_DIR="$HOME/.config/papagaio"
CACHE_DIR="$HOME/.cache/whisper-models"
SERVICE_DIR="$HOME/.config/systemd/user"

# Script directory (where installer is run from)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default configuration
DEFAULT_MODEL="small"
DEFAULT_LANG="en"
DEFAULT_HOTKEY="<ctrl>+<shift>+<alt>+v"
DEFAULT_AUTOSTART="yes"

# Functions
print_header() {
    echo -e "${BLUE}${BOLD}"
    echo "============================================================"
    echo "  Papagaio - Linux Installer"
    echo "  Version 1.1.0"
    echo "============================================================"
    echo -e "${NC}"
}

print_step() {
    echo -e "${CYAN}${BOLD}[$1/$2]${NC} $3"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

ask_question() {
    local question=$1
    local default=$2
    local response

    echo -e -n "${BOLD}$question${NC} [${GREEN}$default${NC}]: "
    read response
    echo "${response:-$default}"
}

detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$ID"
    elif [ -f /etc/lsb-release ]; then
        . /etc/lsb-release
        echo "$DISTRIB_ID" | tr '[:upper:]' '[:lower:]'
    else
        echo "unknown"
    fi
}

check_python_version() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        return 1
    fi

    local version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    local major=$(echo $version | cut -d. -f1)
    local minor=$(echo $version | cut -d. -f2)

    if [ "$major" -lt 3 ] || ([ "$major" -eq 3 ] && [ "$minor" -lt 8 ]); then
        print_error "Python 3.8+ required, found: $version"
        return 1
    fi

    print_success "Python $version detected"
    return 0
}

check_disk_space() {
    local available=$(df -BG "$HOME" | tail -1 | awk '{print $4}' | sed 's/G//')

    if [ "$available" -lt 2 ]; then
        print_warning "Less than 2GB available. Model download may fail."
        return 1
    fi

    print_success "Disk space: ${available}GB available"
    return 0
}

install_system_deps() {
    local distro=$(detect_distro)

    print_info "Detected distribution: $distro"

    case "$distro" in
        ubuntu|debian|linuxmint|pop)
            print_info "Installing system dependencies (requires sudo)..."
            sudo apt update
            sudo apt install -y python3-dev portaudio19-dev xdotool libportaudio2 || {
                print_error "Failed to install system dependencies"
                return 1
            }
            ;;
        fedora)
            print_info "Installing system dependencies (requires sudo)..."
            sudo dnf install -y python3-devel portaudio-devel xdotool portaudio || {
                print_error "Failed to install system dependencies"
                return 1
            }
            ;;
        arch|manjaro)
            print_info "Installing system dependencies (requires sudo)..."
            sudo pacman -S --noconfirm python portaudio xdotool || {
                print_error "Failed to install system dependencies"
                return 1
            }
            ;;
        opensuse*|suse)
            print_info "Installing system dependencies (requires sudo)..."
            sudo zypper install -y python3-devel portaudio-devel xdotool || {
                print_error "Failed to install system dependencies"
                return 1
            }
            ;;
        *)
            print_warning "Unknown distribution: $distro"
            print_info "Please manually install: python3-dev, portaudio-dev, xdotool"
            local response=$(ask_question "Continue anyway?" "no")
            if [ "$response" != "yes" ] && [ "$response" != "y" ]; then
                return 1
            fi
            ;;
    esac

    print_success "System dependencies installed"
    return 0
}

test_microphone() {
    print_info "Testing microphone access..."

    if ! command -v arecord &> /dev/null; then
        print_warning "Cannot test microphone (arecord not found)"
        return 0
    fi

    # Try to record 1 second of audio
    if timeout 1 arecord -d 1 -f cd /tmp/test-mic-$$.wav &> /dev/null; then
        rm -f /tmp/test-mic-$$.wav
        print_success "Microphone is working"
        return 0
    else
        rm -f /tmp/test-mic-$$.wav
        print_warning "Microphone test failed. You may need to configure audio permissions."
        return 0  # Don't fail installation
    fi
}

install_python_deps() {
    print_info "Installing Python dependencies..."

    # Check if pip is available
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 is not installed"
        print_info "Install it with: sudo apt install python3-pip"
        return 1
    fi

    # Install in user mode
    pip3 install --user --upgrade pip setuptools wheel 2>&1 | grep -v "Requirement already satisfied" || true
    pip3 install --user faster-whisper pynput pyaudio 2>&1 | grep -v "Requirement already satisfied" || true

    print_success "Python dependencies installed"
    return 0
}

interactive_config() {
    echo ""
    echo -e "${BOLD}${BLUE}Configuration${NC}"
    echo "─────────────────────────────────────────"

    # Language
    echo -e "${BOLD}Interface Language:${NC}"
    echo "  en - English"
    echo "  pt - Português"
    LANG_CONFIG=$(ask_question "Choose language" "$DEFAULT_LANG")

    # Model
    echo ""
    echo -e "${BOLD}Whisper Model:${NC}"
    echo "  tiny   - ~75MB  | Fast    | Basic accuracy"
    echo "  base   - ~140MB | Faster  | Good accuracy"
    echo "  small  - ~460MB | Balanced| Great accuracy (recommended)"
    echo "  medium - ~1.5GB | Slow    | Best accuracy"
    MODEL_CONFIG=$(ask_question "Choose model" "$DEFAULT_MODEL")

    # Hotkey
    echo ""
    echo -e "${BOLD}Hotkey:${NC}"
    echo "  Examples: <ctrl>+<alt>+v, <ctrl>+<shift>+v, <super>+v"
    HOTKEY_CONFIG=$(ask_question "Choose hotkey" "$DEFAULT_HOTKEY")

    # Auto-start
    echo ""
    AUTOSTART_CONFIG=$(ask_question "Auto-start on login?" "$DEFAULT_AUTOSTART")

    echo ""
    echo -e "${BOLD}${GREEN}Configuration Summary:${NC}"
    echo "  Language:   $LANG_CONFIG"
    echo "  Model:      $MODEL_CONFIG"
    echo "  Hotkey:     $HOTKEY_CONFIG"
    echo "  Auto-start: $AUTOSTART_CONFIG"
    echo ""
}

create_directories() {
    print_info "Creating installation directories..."

    mkdir -p "$INSTALL_DIR"
    mkdir -p "$BIN_DIR"
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$CACHE_DIR"
    mkdir -p "$SERVICE_DIR"

    print_success "Directories created"
}

install_files() {
    print_info "Installing files..."

    # Copy main daemon
    cp "$SCRIPT_DIR/papagaio.py" "$INSTALL_DIR/papagaio.py"
    chmod +x "$INSTALL_DIR/papagaio.py"

    # Copy control script
    cp "$SCRIPT_DIR/papagaio-ctl" "$INSTALL_DIR/papagaio-ctl"
    chmod +x "$INSTALL_DIR/papagaio-ctl"

    # Create symlink in PATH
    ln -sf "$INSTALL_DIR/papagaio-ctl" "$BIN_DIR/papagaio-ctl"

    # Copy requirements
    if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
        cp "$SCRIPT_DIR/requirements.txt" "$INSTALL_DIR/requirements.txt"
    fi

    print_success "Files installed to $INSTALL_DIR"
}

create_systemd_service() {
    print_info "Creating systemd service..."

    local service_file="$SERVICE_DIR/papagaio.service"

    cat > "$service_file" << EOF
[Unit]
Description=Papagaio - Voice-to-Text Input
Documentation=https://github.com/alexandrehsantos/papagaio
After=graphical-session.target

[Service]
Type=simple
Environment="DISPLAY=:0"
Environment="XAUTHORITY=$HOME/.Xauthority"
ExecStart=$INSTALL_DIR/papagaio.py -m $MODEL_CONFIG -l $LANG_CONFIG -k "$HOTKEY_CONFIG"
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF

    # Reload systemd
    systemctl --user daemon-reload

    # Enable if requested
    if [ "$AUTOSTART_CONFIG" = "yes" ] || [ "$AUTOSTART_CONFIG" = "y" ]; then
        systemctl --user enable papagaio
        print_success "Service created and enabled"
    else
        print_success "Service created (not enabled)"
    fi
}

add_to_path() {
    # Check if ~/.local/bin is in PATH
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        print_info "Adding ~/.local/bin to PATH..."

        # Determine shell config file
        if [ -n "$BASH_VERSION" ]; then
            shell_config="$HOME/.bashrc"
        elif [ -n "$ZSH_VERSION" ]; then
            shell_config="$HOME/.zshrc"
        else
            shell_config="$HOME/.profile"
        fi

        echo '' >> "$shell_config"
        echo '# Added by Papagaio installer' >> "$shell_config"
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$shell_config"

        print_success "Added to PATH in $shell_config"
        print_warning "Restart your terminal or run: source $shell_config"
    else
        print_success "~/.local/bin already in PATH"
    fi
}

create_config_file() {
    local config_file="$CONFIG_DIR/config.ini"

    cat > "$config_file" << EOF
# Papagaio Configuration
# Edit this file to customize settings

[General]
model = $MODEL_CONFIG
language = $LANG_CONFIG
hotkey = $HOTKEY_CONFIG
cache_dir = $CACHE_DIR

[Audio]
silence_threshold = 400
silence_duration = 5.0
max_recording_time = 3600

[Advanced]
use_ydotool = false
typing_delay = 0.3
EOF

    print_success "Configuration saved to $config_file"
}

print_final_info() {
    echo ""
    echo -e "${GREEN}${BOLD}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}${BOLD}║                 Installation Complete!                    ║${NC}"
    echo -e "${GREEN}${BOLD}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BOLD}Quick Start:${NC}"
    echo -e "  ${CYAN}papagaio-ctl start${NC}     - Start the daemon"
    echo -e "  ${CYAN}papagaio-ctl status${NC}    - Check status"
    echo -e "  ${CYAN}papagaio-ctl logs${NC}      - View logs"
    echo -e "  ${CYAN}papagaio-ctl help${NC}      - Show all commands"
    echo ""
    echo -e "${BOLD}Usage:${NC}"
    echo "  1. Start daemon: ${CYAN}papagaio-ctl start${NC}"
    echo "  2. Press hotkey: ${YELLOW}$HOTKEY_CONFIG${NC}"
    echo "  3. Speak clearly"
    echo "  4. Stop recording:"
    echo "     • Wait 5 seconds (auto-stop)"
    echo "     • Press $HOTKEY_CONFIG again (manual stop)"
    echo "     • Press ESC (cancel)"
    echo ""
    echo -e "${BOLD}Configuration:${NC}"
    echo "  Model:      $MODEL_CONFIG"
    echo "  Language:   $LANG_CONFIG"
    echo "  Hotkey:     $HOTKEY_CONFIG"
    echo "  Auto-start: $AUTOSTART_CONFIG"
    echo ""
    echo -e "${BOLD}Files:${NC}"
    echo "  Install:    $INSTALL_DIR"
    echo "  Config:     $CONFIG_DIR/config.ini"
    echo "  Cache:      $CACHE_DIR"
    echo ""
    echo -e "${BOLD}Documentation:${NC}"
    echo "  README:     ${SCRIPT_DIR}/README.md"
    echo "  GitHub:     https://github.com/alexandrehsantos/papagaio"
    echo ""
    echo -e "${BOLD}To uninstall:${NC}"
    echo "  Run: ${CYAN}./uninstall.sh${NC}"
    echo ""
}

cleanup_on_error() {
    print_error "Installation failed!"
    print_info "Cleaning up..."

    # Stop service if running
    systemctl --user stop papagaio 2>/dev/null || true
    systemctl --user disable papagaio 2>/dev/null || true

    # Remove files
    rm -rf "$INSTALL_DIR" 2>/dev/null || true
    rm -f "$BIN_DIR/papagaio-ctl" 2>/dev/null || true
    rm -f "$SERVICE_DIR/papagaio.service" 2>/dev/null || true

    exit 1
}

# Main installation flow
main() {
    trap cleanup_on_error ERR

    print_header

    # Step 1: Pre-flight checks
    print_step 1 10 "Running pre-flight checks..."
    check_python_version || exit 1
    check_disk_space

    # Step 2: Install system dependencies
    print_step 2 10 "Installing system dependencies..."
    install_system_deps || exit 1

    # Step 3: Test microphone
    print_step 3 10 "Testing hardware..."
    test_microphone

    # Step 4: Install Python dependencies
    print_step 4 10 "Installing Python dependencies..."
    install_python_deps || exit 1

    # Step 5: Interactive configuration
    print_step 5 10 "Configuration..."
    interactive_config

    # Step 6: Create directories
    print_step 6 10 "Creating directories..."
    create_directories

    # Step 7: Install files
    print_step 7 10 "Installing files..."
    install_files

    # Step 8: Create systemd service
    print_step 8 10 "Setting up systemd service..."
    create_systemd_service

    # Step 9: Add to PATH
    print_step 9 10 "Configuring environment..."
    add_to_path

    # Step 10: Create config file
    print_step 10 10 "Saving configuration..."
    create_config_file

    # Final info
    print_final_info

    # Offer to start now
    echo -n -e "${BOLD}Start daemon now?${NC} [${GREEN}yes${NC}/no]: "
    read start_now

    if [ "$start_now" = "yes" ] || [ "$start_now" = "y" ] || [ -z "$start_now" ]; then
        echo ""
        print_info "Starting daemon..."
        "$BIN_DIR/papagaio-ctl" start
    fi
}

# Run installer
main
