#!/bin/bash
#
# Papagaio - Linux Installer
# Voice-to-text input daemon using Whisper AI
# Supports: Ubuntu, Debian, Fedora, Arch Linux, openSUSE
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

# Installation directories
INSTALL_DIR="$HOME/.local/bin/papagaio"
BIN_DIR="$HOME/.local/bin"
CONFIG_DIR="$HOME/.config/papagaio"
CACHE_DIR="$HOME/.cache/whisper-models"
SERVICE_DIR="$HOME/.config/systemd/user"

# Script directory (where installer is run from)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Defaults
DEFAULT_MODEL="small"
DEFAULT_LANG="en"
DEFAULT_TRANSCRIPTION_LANG="auto"
DEFAULT_HOTKEY="<ctrl>+<alt>+v"
DEFAULT_AUTOSTART="yes"

# ─── Helpers ────────────────────────────────────────────────

print_header() {
    echo ""
    echo -e "${BLUE}${BOLD}============================================${NC}"
    echo -e "${BLUE}${BOLD}  Papagaio Installer${NC}"
    echo -e "${BLUE}${BOLD}============================================${NC}"
    echo ""
}

print_step() {
    echo -e "\n${CYAN}${BOLD}[$1/$2]${NC} $3"
}

print_success() { echo -e "  ${GREEN}✓${NC} $1"; }
print_error()   { echo -e "  ${RED}✗${NC} $1"; }
print_warning() { echo -e "  ${YELLOW}⚠${NC} $1"; }
print_info()    { echo -e "  ${BLUE}ℹ${NC} $1"; }

ask_question() {
    local question=$1
    local default=$2
    local response
    echo -e -n "  ${BOLD}$question${NC} [${GREEN}$default${NC}]: "
    read response
    echo "${response:-$default}"
}

die() {
    print_error "$1"
    exit 1
}

# ─── Pre-flight checks ─────────────────────────────────────

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

check_python() {
    command -v python3 &>/dev/null || die "Python 3 not found. Install it first."

    local version
    version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    local major minor
    major=$(echo "$version" | cut -d. -f1)
    minor=$(echo "$version" | cut -d. -f2)

    if [ "$major" -lt 3 ] || { [ "$major" -eq 3 ] && [ "$minor" -lt 8 ]; }; then
        die "Python 3.8+ required (found $version)"
    fi

    print_success "Python $version"
}

check_disk_space() {
    local available
    available=$(df -BG "$HOME" | tail -1 | awk '{print $4}' | sed 's/G//')

    if [ "$available" -lt 2 ]; then
        print_warning "Less than 2 GB free - model download may fail"
    else
        print_success "Disk space: ${available} GB available"
    fi
}

check_source_files() {
    [ -f "$SCRIPT_DIR/papagaio.py" ]  || die "papagaio.py not found in $SCRIPT_DIR"
    [ -f "$SCRIPT_DIR/papagaio-ctl" ] || die "papagaio-ctl not found in $SCRIPT_DIR"
    print_success "Source files found"
}

# ─── System dependencies ───────────────────────────────────

install_system_deps() {
    local distro
    distro=$(detect_distro)
    print_info "Distribution: $distro"

    case "$distro" in
        ubuntu|debian|linuxmint|pop)
            sudo apt update -qq
            sudo apt install -y -qq python3-dev python3-pip portaudio19-dev libportaudio2 xdotool xclip
            ;;
        fedora)
            sudo dnf install -y python3-devel python3-pip portaudio-devel portaudio xdotool xclip
            ;;
        arch|manjaro)
            sudo pacman -S --noconfirm --needed python python-pip portaudio xdotool xclip
            ;;
        opensuse*|suse)
            sudo zypper install -y python3-devel python3-pip portaudio-devel xdotool xclip
            ;;
        *)
            print_warning "Unknown distro: $distro"
            print_info "Please manually install: python3-dev, python3-pip, portaudio-dev, xdotool, xclip"
            local resp
            resp=$(ask_question "Continue anyway?" "no")
            [[ "$resp" =~ ^(yes|y)$ ]] || exit 1
            ;;
    esac

    print_success "System dependencies installed"
}

# ─── Python dependencies ───────────────────────────────────

install_python_deps() {
    command -v pip3 &>/dev/null || die "pip3 not found. Install python3-pip."

    pip3 install --user --upgrade pip setuptools wheel 2>&1 | tail -1
    pip3 install --user faster-whisper pynput pyaudio 2>&1 | tail -1

    print_success "Python dependencies installed"
}

# ─── Microphone test ───────────────────────────────────────

test_microphone() {
    if ! command -v arecord &>/dev/null; then
        print_warning "Cannot test microphone (arecord not found)"
        return 0
    fi

    local tmp="/tmp/papagaio-mic-test-$$.wav"
    if timeout 2 arecord -d 1 -f cd "$tmp" &>/dev/null; then
        rm -f "$tmp"
        print_success "Microphone working"
    else
        rm -f "$tmp"
        print_warning "Microphone test failed - check audio permissions"
    fi
}

# ─── Interactive configuration ──────────────────────────────

interactive_config() {
    echo ""
    echo -e "  ${BOLD}${BLUE}Configuration${NC}"
    echo -e "  ─────────────────────────────────────"

    # Language
    echo ""
    echo -e "  ${BOLD}Interface language:${NC}"
    echo "    en - English"
    echo "    pt - Portugues"
    LANG_CONFIG=$(ask_question "Language" "$DEFAULT_LANG")

    # Model
    echo ""
    echo -e "  ${BOLD}Whisper model:${NC}"
    echo "    tiny   -  ~75 MB  | Fast   | Basic accuracy"
    echo "    base   - ~140 MB  | Fast   | Good accuracy"
    echo "    small  - ~460 MB  | Medium | Great accuracy (recommended)"
    echo "    medium - ~1.5 GB  | Slow   | Best accuracy"
    MODEL_CONFIG=$(ask_question "Model" "$DEFAULT_MODEL")

    # Transcription language
    echo ""
    echo -e "  ${BOLD}Transcription language:${NC}"
    echo "    auto - Auto-detect spoken language"
    echo "    en   - English only"
    echo "    pt   - Portuguese only"
    echo "    (or any Whisper-supported language code)"
    TRANSCRIPTION_LANG_CONFIG=$(ask_question "Transcription language" "$DEFAULT_TRANSCRIPTION_LANG")

    # Hotkey
    echo ""
    echo -e "  ${BOLD}Hotkey:${NC}"
    echo "    Examples: <ctrl>+<alt>+v, <ctrl>+<shift>+v, <super>+v"
    HOTKEY_CONFIG=$(ask_question "Hotkey" "$DEFAULT_HOTKEY")

    # Autostart
    echo ""
    AUTOSTART_CONFIG=$(ask_question "Auto-start on login?" "$DEFAULT_AUTOSTART")

    # Summary
    echo ""
    echo -e "  ${BOLD}${GREEN}Summary:${NC}"
    echo "    Interface:     $LANG_CONFIG"
    echo "    Model:         $MODEL_CONFIG"
    echo "    Transcription: $TRANSCRIPTION_LANG_CONFIG"
    echo "    Hotkey:        $HOTKEY_CONFIG"
    echo "    Auto-start:    $AUTOSTART_CONFIG"
    echo ""
}

# ─── Install files ──────────────────────────────────────────

create_directories() {
    mkdir -p "$INSTALL_DIR" "$BIN_DIR" "$CONFIG_DIR" "$CACHE_DIR" "$SERVICE_DIR"
    print_success "Directories created"
}

install_files() {
    # Core files
    cp "$SCRIPT_DIR/papagaio.py" "$INSTALL_DIR/papagaio.py"
    chmod +x "$INSTALL_DIR/papagaio.py"

    cp "$SCRIPT_DIR/papagaio-ctl" "$INSTALL_DIR/papagaio-ctl"
    chmod +x "$INSTALL_DIR/papagaio-ctl"

    if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
        cp "$SCRIPT_DIR/requirements.txt" "$INSTALL_DIR/requirements.txt"
    fi

    # Symlink papagaio-ctl into PATH
    ln -sf "$INSTALL_DIR/papagaio-ctl" "$BIN_DIR/papagaio-ctl"

    print_success "Files installed to $INSTALL_DIR"
}

# ─── Systemd service ───────────────────────────────────────

create_systemd_service() {
    local service_file="$SERVICE_DIR/papagaio.service"

    cat > "$service_file" << EOF
[Unit]
Description=Papagaio - Voice-to-Text Input
Documentation=https://github.com/alexandrehsantos/papagaio
After=graphical-session.target

[Service]
Type=simple
Environment="DISPLAY=:0"
Environment="XAUTHORITY=%h/.Xauthority"
ExecStart=%h/.local/bin/papagaio/papagaio.py -m ${MODEL_CONFIG} -l ${LANG_CONFIG} -t ${TRANSCRIPTION_LANG_CONFIG} -k "${HOTKEY_CONFIG}"
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF

    systemctl --user daemon-reload

    if [[ "$AUTOSTART_CONFIG" =~ ^(yes|y)$ ]]; then
        systemctl --user enable papagaio
        print_success "Service created and enabled"
    else
        print_success "Service created (not enabled)"
    fi
}

# ─── Config file ────────────────────────────────────────────

create_config_file() {
    local config_file="$CONFIG_DIR/config.ini"

    # Don't overwrite existing config
    if [ -f "$config_file" ]; then
        print_warning "Config already exists: $config_file (preserved)"
        return 0
    fi

    cat > "$config_file" << EOF
# Papagaio Configuration
# Edit this file to customize settings

[General]
model = ${MODEL_CONFIG}
language = ${LANG_CONFIG}
hotkey = ${HOTKEY_CONFIG}
cache_dir = ${CACHE_DIR}

[Audio]
silence_threshold = 400
silence_duration = 5.0
max_recording_time = 3600

[Advanced]
use_ydotool = false
typing_delay = 0.3
EOF

    print_success "Config saved to $config_file"
}

# ─── PATH setup ─────────────────────────────────────────────

add_to_path() {
    if [[ ":$PATH:" == *":$HOME/.local/bin:"* ]]; then
        print_success "~/.local/bin already in PATH"
        return 0
    fi

    # Determine shell config
    local shell_config="$HOME/.profile"
    if [ -n "$BASH_VERSION" ]; then
        shell_config="$HOME/.bashrc"
    elif [ -n "$ZSH_VERSION" ]; then
        shell_config="$HOME/.zshrc"
    fi

    echo '' >> "$shell_config"
    echo '# Added by Papagaio installer' >> "$shell_config"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$shell_config"

    print_success "Added ~/.local/bin to PATH in $shell_config"
    print_warning "Restart your terminal or: source $shell_config"
}

# ─── Cleanup on failure ────────────────────────────────────

cleanup_on_error() {
    echo ""
    print_error "Installation failed!"
    print_info "Cleaning up..."

    systemctl --user stop papagaio 2>/dev/null || true
    systemctl --user disable papagaio 2>/dev/null || true
    rm -rf "$INSTALL_DIR" 2>/dev/null || true
    rm -f "$BIN_DIR/papagaio-ctl" 2>/dev/null || true
    rm -f "$SERVICE_DIR/papagaio.service" 2>/dev/null || true

    exit 1
}

# ─── Final output ───────────────────────────────────────────

print_done() {
    echo ""
    echo -e "${GREEN}${BOLD}============================================${NC}"
    echo -e "${GREEN}${BOLD}  Installation complete!${NC}"
    echo -e "${GREEN}${BOLD}============================================${NC}"
    echo ""
    echo -e "  ${BOLD}Quick start:${NC}"
    echo -e "    ${CYAN}papagaio-ctl start${NC}    Start the daemon"
    echo -e "    ${CYAN}papagaio-ctl status${NC}   Check status"
    echo -e "    ${CYAN}papagaio-ctl logs${NC}     View logs"
    echo -e "    ${CYAN}papagaio-ctl test${NC}     Run in foreground (debug)"
    echo -e "    ${CYAN}papagaio-ctl help${NC}     All commands"
    echo ""
    echo -e "  ${BOLD}How to use:${NC}"
    echo "    1. Start:  papagaio-ctl start"
    echo -e "    2. Press:  ${YELLOW}${HOTKEY_CONFIG}${NC}"
    echo "    3. Speak clearly"
    echo "    4. Stop: wait 5s (auto) / press hotkey again / ESC"
    echo ""
    echo -e "  ${BOLD}Files:${NC}"
    echo "    Install: $INSTALL_DIR"
    echo "    Config:  $CONFIG_DIR/config.ini"
    echo "    Cache:   $CACHE_DIR"
    echo ""
    echo -e "  ${BOLD}Uninstall:${NC} ${CYAN}./uninstall.sh${NC}"
    echo ""
}

# ─── Main ───────────────────────────────────────────────────

main() {
    trap cleanup_on_error ERR

    print_header

    local total=8

    print_step 1 $total "Pre-flight checks..."
    check_python
    check_disk_space
    check_source_files

    print_step 2 $total "Installing system dependencies..."
    install_system_deps

    print_step 3 $total "Testing microphone..."
    test_microphone

    print_step 4 $total "Installing Python dependencies..."
    install_python_deps

    print_step 5 $total "Configuration..."
    interactive_config

    print_step 6 $total "Installing files..."
    create_directories
    install_files

    print_step 7 $total "Setting up systemd service..."
    create_systemd_service
    create_config_file
    add_to_path

    print_step 8 $total "Done!"
    print_done

    # Offer to start now
    echo -e -n "  ${BOLD}Start daemon now?${NC} [${GREEN}yes${NC}/no]: "
    read start_now
    if [[ "${start_now:-yes}" =~ ^(yes|y|)$ ]]; then
        echo ""
        "$BIN_DIR/papagaio-ctl" start
    fi
}

main
