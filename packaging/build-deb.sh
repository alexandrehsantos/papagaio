#!/bin/bash
#
# Build Debian Package (.deb)
# Usage: ./build-deb.sh
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VERSION="1.0.1"
PKG_NAME="papagaio"

echo "============================================"
echo "Building Debian Package for $PKG_NAME v$VERSION"
echo "============================================"
echo ""

# Check if debuild is installed
if ! command -v debuild &> /dev/null; then
    echo "ERROR: debuild not found"
    echo "Install with: sudo apt install devscripts debhelper"
    exit 1
fi

# Go to project directory
cd "$PROJECT_DIR"

echo "[1/4] Cleaning previous builds..."
rm -rf debian/papagaio
rm -f ../*.deb ../*.build ../*.buildinfo ../*.changes ../*.dsc ../*.tar.xz

echo "[2/4] Building package..."
debuild -us -uc -b

echo "[3/4] Checking package..."
if [ -f "../${PKG_NAME}_${VERSION}-1_all.deb" ]; then
    echo "✓ Package built successfully!"
    echo ""
    echo "Package: ../${PKG_NAME}_${VERSION}-1_all.deb"
    echo ""

    # Show package info
    dpkg-deb --info "../${PKG_NAME}_${VERSION}-1_all.deb"
    echo ""

    echo "[4/4] Package contents:"
    dpkg-deb --contents "../${PKG_NAME}_${VERSION}-1_all.deb"

    echo ""
    echo "============================================"
    echo "✓ Build Complete!"
    echo "============================================"
    echo ""
    echo "Install with:"
    echo "  sudo dpkg -i ../${PKG_NAME}_${VERSION}-1_all.deb"
    echo "  sudo apt install -f  # Fix dependencies if needed"
    echo ""
else
    echo "✗ Package build failed!"
    exit 1
fi
