#!/bin/bash
#
# Whisper Voice Daemon - Uninstaller
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

print_header() {
    echo -e "${RED}${BOLD}"
    echo "============================================================"
    echo "  Whisper Voice Daemon - Uninstaller"
    echo "============================================================"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

ask_confirmation() {
    echo -e -n "${YELLOW}${BOLD}Are you sure you want to uninstall?${NC} [yes/NO]: "
    read response
    if [ "$response" != "yes" ]; then
        echo "Uninstall cancelled."
        exit 0
    fi
}

ask_remove_cache() {
    echo ""
    echo -e "${BOLD}Remove downloaded Whisper models?${NC}"
    print_info "Location: $CACHE_DIR"
    local size=$(du -sh "$CACHE_DIR" 2>/dev/null | cut -f1 || echo "unknown")
    print_info "Size: $size"
    echo -e -n "${YELLOW}Remove models?${NC} [yes/NO]: "
    read response
    echo "$response"
}

ask_remove_config() {
    echo ""
    echo -e "${BOLD}Remove configuration files?${NC}"
    print_info "Location: $CONFIG_DIR"
    echo -e -n "${YELLOW}Remove config?${NC} [yes/NO]: "
    read response
    echo "$response"
}

stop_service() {
    print_info "Stopping service..."

    if systemctl --user is-active papagaio &>/dev/null; then
        systemctl --user stop papagaio
        print_success "Service stopped"
    fi

    if systemctl --user is-enabled papagaio &>/dev/null; then
        systemctl --user disable papagaio
        print_success "Auto-start disabled"
    fi
}

remove_service() {
    print_info "Removing systemd service..."

    local service_file="$SERVICE_DIR/papagaio.service"

    if [ -f "$service_file" ]; then
        rm -f "$service_file"
        systemctl --user daemon-reload
        print_success "Service removed"
    else
        print_info "Service file not found (already removed?)"
    fi
}

remove_files() {
    print_info "Removing installation files..."

    # Remove symlink
    if [ -L "$BIN_DIR/papagaio-ctl" ]; then
        rm -f "$BIN_DIR/papagaio-ctl"
        print_success "Removed papagaio-ctl command"
    fi

    # Remove installation directory
    if [ -d "$INSTALL_DIR" ]; then
        rm -rf "$INSTALL_DIR"
        print_success "Removed $INSTALL_DIR"
    fi
}

remove_config() {
    if [ -d "$CONFIG_DIR" ]; then
        rm -rf "$CONFIG_DIR"
        print_success "Removed configuration"
    fi
}

remove_cache() {
    if [ -d "$CACHE_DIR" ]; then
        rm -rf "$CACHE_DIR"
        print_success "Removed model cache"
    fi
}

check_path_entry() {
    # Check if we added PATH entry
    local shell_configs=("$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile")

    for config in "${shell_configs[@]}"; do
        if [ -f "$config" ] && grep -q "Added by Whisper Voice Daemon installer" "$config"; then
            print_info "Found PATH entry in $config"
            echo -e -n "${YELLOW}Remove PATH entry?${NC} [yes/NO]: "
            read response

            if [ "$response" = "yes" ]; then
                # Remove the lines
                sed -i '/Added by Whisper Voice Daemon installer/,+1d' "$config"
                print_success "Removed PATH entry from $config"
                print_info "Restart terminal for changes to take effect"
            fi
        fi
    done
}

print_final_info() {
    echo ""
    echo -e "${GREEN}${BOLD}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}${BOLD}║              Uninstallation Complete!                      ║${NC}"
    echo -e "${GREEN}${BOLD}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BOLD}Removed:${NC}"
    echo "  ✓ Voice daemon service"
    echo "  ✓ Installation files"
    echo "  ✓ Command-line tools"
    echo ""
    print_info "Thank you for using Whisper Voice Daemon!"
    echo ""
    print_info "To reinstall: ./install.sh"
    echo ""
}

main() {
    print_header

    # Confirmation
    ask_confirmation

    echo ""
    echo -e "${BOLD}Uninstalling...${NC}"
    echo ""

    # Stop and remove service
    stop_service
    remove_service

    # Remove files
    remove_files

    # Ask about config
    local remove_cfg=$(ask_remove_config)
    if [ "$remove_cfg" = "yes" ]; then
        remove_config
    else
        print_info "Configuration preserved at $CONFIG_DIR"
    fi

    # Ask about cache
    if [ -d "$CACHE_DIR" ]; then
        local remove_mdl=$(ask_remove_cache)
        if [ "$remove_mdl" = "yes" ]; then
            remove_cache
        else
            print_info "Models preserved at $CACHE_DIR"
        fi
    fi

    # Check PATH entry
    echo ""
    check_path_entry

    # Final info
    print_final_info
}

main
