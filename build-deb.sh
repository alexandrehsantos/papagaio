#!/bin/bash
#
# Papagaio - Debian Package Builder
# Installs build dependencies and creates .deb package
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${GREEN}Papagaio - Debian Package Builder${NC}"
echo "========================================"

# Detect distro
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$ID"
    else
        echo "unknown"
    fi
}

DISTRO=$(detect_distro)

if [[ "$DISTRO" != "ubuntu" && "$DISTRO" != "debian" && "$DISTRO" != "linuxmint" && "$DISTRO" != "pop" ]]; then
    echo -e "${RED}Error: This script is for Debian-based systems only${NC}"
    echo "Detected: $DISTRO"
    exit 1
fi

echo -e "${YELLOW}[1/3]${NC} Installing build dependencies..."
sudo apt-get update
sudo apt-get install -y debhelper dh-python python3-all python3-setuptools

echo -e "${YELLOW}[2/3]${NC} Building .deb package..."
cd "$SCRIPT_DIR"
dpkg-buildpackage -us -uc -b

echo -e "${YELLOW}[3/3]${NC} Package built successfully!"
echo ""

# Find the created .deb
DEB_FILE=$(ls -t ../papagaio_*.deb 2>/dev/null | head -1)

if [ -n "$DEB_FILE" ]; then
    echo -e "${GREEN}Package created:${NC} $DEB_FILE"
    echo ""
    echo "To install:"
    echo -e "  ${GREEN}sudo dpkg -i $DEB_FILE${NC}"
    echo ""

    read -p "Install now? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo dpkg -i "$DEB_FILE" || sudo apt-get install -f -y
        echo -e "${GREEN}Installed!${NC} Run: papagaio-ctl start"
    fi
else
    echo -e "${RED}Error: .deb file not found${NC}"
    exit 1
fi
