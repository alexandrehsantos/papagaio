#!/bin/bash
#
# Papagaio Settings - Build Script
# Creates professional installers for Linux, Windows, and macOS
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║           Papagaio Settings - Build System                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check dependencies
check_deps() {
    echo -e "${BLUE}Checking dependencies...${NC}"

    if ! command -v node &> /dev/null; then
        echo -e "${RED}Error: Node.js is not installed${NC}"
        exit 1
    fi

    if ! command -v npm &> /dev/null; then
        echo -e "${RED}Error: npm is not installed${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓ Node.js $(node --version)${NC}"
    echo -e "${GREEN}✓ npm $(npm --version)${NC}"
}

# Install dependencies
install_deps() {
    echo -e "${BLUE}Installing dependencies...${NC}"
    npm install

    # Ensure electron binary is installed
    if [ ! -f "node_modules/electron/dist/electron" ]; then
        node node_modules/electron/install.js
    fi
}

# Run tests
run_tests() {
    echo -e "${BLUE}Running tests...${NC}"
    npm test || {
        echo -e "${YELLOW}Warning: Some tests failed${NC}"
    }
}

# Build for specific platform
build_platform() {
    local platform=$1
    echo -e "${BLUE}Building for ${platform}...${NC}"

    case $platform in
        linux)
            npm run build:linux
            ;;
        windows|win)
            npm run build:win
            ;;
        macos|mac)
            npm run build:mac
            ;;
        all)
            npm run build:all
            ;;
        *)
            echo -e "${RED}Unknown platform: ${platform}${NC}"
            echo "Usage: $0 [linux|windows|macos|all]"
            exit 1
            ;;
    esac
}

# Show build results
show_results() {
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗"
    echo -e "║                    Build Complete!                         ║"
    echo -e "╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Output files:${NC}"
    echo ""

    if [ -d "dist" ]; then
        ls -lh dist/ 2>/dev/null | grep -E "\.(deb|rpm|AppImage|exe|dmg|zip|tar\.gz)$" | while read line; do
            echo "  $line"
        done
    fi

    echo ""
    echo -e "${YELLOW}Distribution packages are in: ${PROJECT_DIR}/dist/${NC}"
}

# Main
main() {
    local platform=${1:-linux}

    check_deps
    install_deps

    if [ "$2" != "--skip-tests" ]; then
        run_tests
    fi

    build_platform "$platform"
    show_results
}

# Help
if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    echo "Usage: $0 [platform] [--skip-tests]"
    echo ""
    echo "Platforms:"
    echo "  linux    - Build AppImage, .deb, .rpm, .tar.gz"
    echo "  windows  - Build NSIS installer and portable .exe"
    echo "  macos    - Build .dmg and .zip"
    echo "  all      - Build for all platforms"
    echo ""
    echo "Options:"
    echo "  --skip-tests  Skip running tests before build"
    echo ""
    echo "Examples:"
    echo "  $0 linux              # Build Linux packages"
    echo "  $0 windows            # Build Windows installer"
    echo "  $0 all --skip-tests   # Build all without tests"
    exit 0
fi

main "$@"
