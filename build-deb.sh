#!/bin/bash
#
# Papagaio - Debian Package Builder
# Compiles binary with PyInstaller, then builds .deb
#
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION=$(grep '__version__' "$SCRIPT_DIR/papagaio.py" | head -1 | cut -d'"' -f2)

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

echo -e "${GREEN}${BOLD}Papagaio Debian Package Builder v${VERSION}${NC}"
echo "============================================"

# ─── Step 1: Check build tools ──────────────────────────────

echo -e "\n${YELLOW}[1/5]${NC} Checking build dependencies..."

command -v python3 >/dev/null || { echo -e "${RED}Error: python3 required${NC}"; exit 1; }
command -v dpkg-buildpackage >/dev/null || {
    echo "Installing debhelper..."
    sudo apt-get update -qq && sudo apt-get install -y -qq debhelper
}

# ─── Step 2: Create build virtualenv ────────────────────────

echo -e "${YELLOW}[2/5]${NC} Setting up build environment..."

BUILD_VENV="/tmp/papagaio-build-venv-$$"
rm -rf "$BUILD_VENV" 2>/dev/null || true
python3 -m venv "$BUILD_VENV"
# shellcheck disable=SC1091
source "$BUILD_VENV/bin/activate"
pip install --upgrade pip setuptools wheel -q
pip install pyinstaller -q
pip install -r "$SCRIPT_DIR/requirements.txt" -q
echo -e "  ${GREEN}✓${NC} Build virtualenv ready"

# ─── Step 3: Compile with PyInstaller ───────────────────────

echo -e "${YELLOW}[3/5]${NC} Compiling binary with PyInstaller..."

pyinstaller "$SCRIPT_DIR/papagaio.spec" \
    --distpath "$SCRIPT_DIR/dist" \
    --workpath "$SCRIPT_DIR/.build-pyinstaller" \
    --clean \
    --noconfirm \
    2>&1 | tail -5

deactivate

if [ ! -f "$SCRIPT_DIR/dist/papagaio" ]; then
    echo -e "${RED}Error: PyInstaller failed to produce binary${NC}"
    exit 1
fi

BINARY_SIZE=$(du -h "$SCRIPT_DIR/dist/papagaio" | cut -f1)
echo -e "  ${GREEN}✓${NC} Binary compiled: dist/papagaio (${BINARY_SIZE})"

# ─── Step 4: Build .deb ─────────────────────────────────────

echo -e "${YELLOW}[4/5]${NC} Building .deb package..."

cd "$SCRIPT_DIR"
dpkg-buildpackage -us -uc -b 2>&1 | tail -3

# ─── Step 5: Report ─────────────────────────────────────────

echo -e "\n${YELLOW}[5/5]${NC} Done!"

DEB_FILE=$(ls -t ../papagaio_*.deb 2>/dev/null | head -1)
if [ -n "$DEB_FILE" ]; then
    DEB_SIZE=$(du -h "$DEB_FILE" | cut -f1)
    echo ""
    echo -e "${GREEN}${BOLD}============================================${NC}"
    echo -e "${GREEN}${BOLD}  Package built successfully!${NC}"
    echo -e "${GREEN}${BOLD}============================================${NC}"
    echo -e "  File:    ${CYAN}$DEB_FILE${NC}"
    echo -e "  Size:    ${DEB_SIZE}"
    echo -e "  Install: ${CYAN}sudo dpkg -i $DEB_FILE && sudo apt-get install -f${NC}"
    echo ""
else
    echo -e "${RED}Error: .deb file not found${NC}"
    exit 1
fi

# Cleanup build artifacts
rm -rf "$BUILD_VENV" "$SCRIPT_DIR/.build-pyinstaller" 2>/dev/null || true
