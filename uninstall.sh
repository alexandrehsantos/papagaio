#!/bin/bash
#
# Papagaio - Uninstaller
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
    echo ""
    echo -e "${RED}${BOLD}============================================${NC}"
    echo -e "${RED}${BOLD}  Papagaio Uninstaller${NC}"
    echo -e "${RED}${BOLD}============================================${NC}"
    echo ""
}

print_success() { echo -e "  ${GREEN}✓${NC} $1"; }
print_error()   { echo -e "  ${RED}✗${NC} $1"; }
print_info()    { echo -e "  ${BLUE}ℹ${NC} $1"; }
print_warning() { echo -e "  ${YELLOW}⚠${NC} $1"; }

ask_yes_no() {
    local prompt=$1
    local response
    echo -e -n "  ${YELLOW}${BOLD}$prompt${NC} [yes/NO]: "
    read response
    [[ "$response" == "yes" ]]
}

# ─── Stop and remove service ──────────────────────────────

stop_service() {
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
    local service_file="$SERVICE_DIR/papagaio.service"

    if [ -f "$service_file" ]; then
        rm -f "$service_file"
        systemctl --user daemon-reload
        print_success "Service file removed"
    else
        print_info "Service file not found (already removed)"
    fi
}

# ─── Remove files ─────────────────────────────────────────

remove_files() {
    # Remove symlink
    if [ -L "$BIN_DIR/papagaio-ctl" ]; then
        rm -f "$BIN_DIR/papagaio-ctl"
        print_success "Removed papagaio-ctl symlink"
    fi

    # Remove installation directory
    if [ -d "$INSTALL_DIR" ]; then
        rm -rf "$INSTALL_DIR"
        print_success "Removed $INSTALL_DIR"
    fi
}

# ─── Remove config ────────────────────────────────────────

remove_config() {
    if [ -d "$CONFIG_DIR" ]; then
        rm -rf "$CONFIG_DIR"
        print_success "Removed configuration"
    fi
}

# ─── Remove cache ─────────────────────────────────────────

remove_cache() {
    if [ -d "$CACHE_DIR" ]; then
        rm -rf "$CACHE_DIR"
        print_success "Removed model cache"
    fi
}

# ─── Clean PATH entry ─────────────────────────────────────

clean_path_entry() {
    local shell_configs=("$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile")

    for config in "${shell_configs[@]}"; do
        if [ -f "$config" ] && grep -q "Added by Papagaio installer" "$config"; then
            print_info "Found PATH entry in $config"
            if ask_yes_no "Remove PATH entry?"; then
                sed -i '/Added by Papagaio installer/,+1d' "$config"
                print_success "Removed PATH entry from $config"
            fi
        fi
    done
}

# ─── Main ─────────────────────────────────────────────────

main() {
    print_header

    # Confirm
    if ! ask_yes_no "Are you sure you want to uninstall Papagaio?"; then
        echo "  Cancelled."
        exit 0
    fi

    echo ""

    # Stop and remove service
    print_info "Stopping service..."
    stop_service
    remove_service

    # Remove installed files
    print_info "Removing files..."
    remove_files

    # Ask about config
    echo ""
    if [ -d "$CONFIG_DIR" ]; then
        if ask_yes_no "Remove configuration ($CONFIG_DIR)?"; then
            remove_config
        else
            print_info "Configuration preserved at $CONFIG_DIR"
        fi
    fi

    # Ask about cache
    if [ -d "$CACHE_DIR" ]; then
        local size
        size=$(du -sh "$CACHE_DIR" 2>/dev/null | cut -f1 || echo "unknown")
        echo ""
        print_info "Model cache: $CACHE_DIR ($size)"
        if ask_yes_no "Remove downloaded models?"; then
            remove_cache
        else
            print_info "Models preserved at $CACHE_DIR"
        fi
    fi

    # Clean PATH
    echo ""
    clean_path_entry

    # Done
    echo ""
    echo -e "${GREEN}${BOLD}============================================${NC}"
    echo -e "${GREEN}${BOLD}  Uninstall complete${NC}"
    echo -e "${GREEN}${BOLD}============================================${NC}"
    echo ""
    print_info "To reinstall: ${CYAN}./install.sh${NC}"
    echo ""
}

main
