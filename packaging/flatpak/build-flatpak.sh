#!/bin/bash
#
# Papagaio Flatpak Build Script
# Creates Flatpak package for universal Linux distribution
#
# Author: Alexandre Santos <alexandrehsantos@gmail.com>
# Company: Bulvee Company
#
# Requirements:
#   - flatpak
#   - flatpak-builder
#   - org.freedesktop.Platform//23.08 runtime
#   - org.freedesktop.Sdk//23.08 SDK
#
# Usage:
#   ./build-flatpak.sh           # Build and install locally
#   ./build-flatpak.sh --bundle  # Create distributable bundle
#   ./build-flatpak.sh --clean   # Clean build artifacts

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BUILD_DIR="$SCRIPT_DIR/build"
REPO_DIR="$SCRIPT_DIR/repo"
OUTPUT_DIR="$PROJECT_ROOT/dist"

VERSION="1.1.0"
APP_ID="com.bulvee.papagaio"

print_header() {
    echo -e "${BLUE}${BOLD}"
    echo "============================================"
    echo "  Papagaio Flatpak Builder"
    echo "  Version: $VERSION"
    echo "============================================"
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

# Check dependencies
check_deps() {
    local missing=0

    if ! command -v flatpak &> /dev/null; then
        print_error "flatpak not found"
        echo "  Install with: sudo apt install flatpak  (Debian/Ubuntu)"
        echo "                sudo dnf install flatpak  (Fedora)"
        missing=1
    else
        print_success "flatpak found"
    fi

    if ! command -v flatpak-builder &> /dev/null; then
        print_error "flatpak-builder not found"
        echo "  Install with: sudo apt install flatpak-builder  (Debian/Ubuntu)"
        echo "                sudo dnf install flatpak-builder  (Fedora)"
        missing=1
    else
        print_success "flatpak-builder found"
    fi

    if [ $missing -eq 1 ]; then
        exit 1
    fi
}

# Install required runtimes
install_runtimes() {
    echo "Checking Flatpak runtimes..."

    # Check if runtime is installed
    if ! flatpak list --runtime | grep -q "org.freedesktop.Platform.*23.08"; then
        echo "Installing Freedesktop Platform 23.08..."
        flatpak install -y flathub org.freedesktop.Platform//23.08
    fi
    print_success "org.freedesktop.Platform//23.08 available"

    if ! flatpak list --runtime | grep -q "org.freedesktop.Sdk.*23.08"; then
        echo "Installing Freedesktop SDK 23.08..."
        flatpak install -y flathub org.freedesktop.Sdk//23.08
    fi
    print_success "org.freedesktop.Sdk//23.08 available"
}

# Clean build
clean_build() {
    echo "Cleaning build artifacts..."
    rm -rf "$BUILD_DIR"
    rm -rf "$REPO_DIR"
    rm -rf "$SCRIPT_DIR/.flatpak-builder"
    print_success "Build artifacts cleaned"
}

# Build Flatpak
build_flatpak() {
    echo "Building Flatpak..."

    mkdir -p "$REPO_DIR"

    # Build
    flatpak-builder \
        --force-clean \
        --user \
        --repo="$REPO_DIR" \
        "$BUILD_DIR" \
        "$SCRIPT_DIR/com.bulvee.papagaio.yml"

    if [ $? -eq 0 ]; then
        print_success "Flatpak built successfully"
    else
        print_error "Flatpak build failed"
        exit 1
    fi
}

# Install locally
install_local() {
    echo "Installing Flatpak locally..."

    flatpak --user remote-add --no-gpg-verify --if-not-exists \
        papagaio-local "$REPO_DIR"

    flatpak --user install -y papagaio-local "$APP_ID"

    print_success "Flatpak installed locally"
    echo ""
    echo "Run with: flatpak run $APP_ID"
}

# Create distributable bundle
create_bundle() {
    echo "Creating distributable bundle..."

    mkdir -p "$OUTPUT_DIR"

    local bundle_file="$OUTPUT_DIR/papagaio-${VERSION}.flatpak"

    flatpak build-bundle \
        "$REPO_DIR" \
        "$bundle_file" \
        "$APP_ID"

    if [ -f "$bundle_file" ]; then
        print_success "Bundle created: $bundle_file"

        local size=$(du -h "$bundle_file" | cut -f1)
        echo "  Size: $size"
    else
        print_error "Bundle creation failed"
        exit 1
    fi
}

# Main
main() {
    print_header

    case "$1" in
        --clean|-c)
            clean_build
            exit 0
            ;;
        --bundle|-b)
            CREATE_BUNDLE=1
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --bundle, -b   Create distributable bundle"
            echo "  --clean, -c    Clean build artifacts"
            echo "  --help, -h     Show this help"
            echo ""
            exit 0
            ;;
    esac

    print_step 1 5 "Checking dependencies..."
    check_deps

    print_step 2 5 "Installing runtimes..."
    install_runtimes

    print_step 3 5 "Building Flatpak..."
    build_flatpak

    print_step 4 5 "Installing locally..."
    install_local

    if [ "$CREATE_BUNDLE" = "1" ]; then
        print_step 5 5 "Creating bundle..."
        create_bundle
    else
        print_step 5 5 "Skipping bundle creation (use --bundle to create)"
    fi

    echo ""
    echo -e "${GREEN}${BOLD}Build complete!${NC}"
    echo ""
    echo "Usage:"
    echo "  flatpak run $APP_ID              # Run system tray"
    echo "  flatpak run $APP_ID --daemon     # Run daemon directly"
    echo "  flatpak run $APP_ID --settings   # Open settings"
    echo ""

    if [ "$CREATE_BUNDLE" = "1" ]; then
        echo "Distribution:"
        echo "  Share: $OUTPUT_DIR/papagaio-${VERSION}.flatpak"
        echo "  Install: flatpak install papagaio-${VERSION}.flatpak"
        echo ""
    fi
}

main "$@"
