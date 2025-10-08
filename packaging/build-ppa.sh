#!/bin/bash
#
# Build and Upload to Ubuntu PPA
# Usage: ./build-ppa.sh [ppa-name]
#
# Example: ./build-ppa.sh ppa:alexandrehsantos/whisper-voice-daemon
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PPA_NAME="${1}"
VERSION="1.1.0"

echo "============================================"
echo "Building Source Package for Ubuntu PPA"
echo "============================================"
echo ""

if [ -z "$PPA_NAME" ]; then
    echo "ERROR: PPA name required"
    echo ""
    echo "Usage: $0 ppa:username/ppa-name"
    echo ""
    echo "Example:"
    echo "  $0 ppa:alexandrehsantos/whisper-voice-daemon"
    echo ""
    exit 1
fi

# Check if tools are installed
if ! command -v debuild &> /dev/null; then
    echo "ERROR: debuild not found"
    echo "Install with: sudo apt install devscripts debhelper dh-python"
    exit 1
fi

if ! command -v dput &> /dev/null; then
    echo "ERROR: dput not found"
    echo "Install with: sudo apt install dput"
    exit 1
fi

# Go to project directory
cd "$PROJECT_DIR"

echo "[1/6] Checking GPG key..."
if ! gpg --list-secret-keys | grep -q "@"; then
    echo "ERROR: No GPG key found"
    echo ""
    echo "Create GPG key:"
    echo "  gpg --full-generate-key"
    echo "  # Choose: RSA and RSA, 4096 bits"
    echo ""
    echo "Upload to Launchpad:"
    echo "  gpg --armor --export YOUR_KEY_ID"
    echo "  # Paste at: https://launchpad.net/~your-username/+editpgpkeys"
    echo ""
    exit 1
fi

GPG_KEY=$(gpg --list-secret-keys --keyid-format LONG | grep "sec" | head -1 | awk '{print $2}' | cut -d'/' -f2)
echo "Using GPG key: $GPG_KEY"

echo ""
echo "[2/6] Cleaning previous builds..."
rm -f ../*.deb ../*.build ../*.buildinfo ../*.changes ../*.dsc ../*.tar.* ../*.upload

echo "[3/6] Building source package..."
debuild -S -sa -k$GPG_KEY

echo ""
echo "[4/6] Verifying package..."
CHANGES_FILE="../whisper-voice-daemon_${VERSION}-1ubuntu1_source.changes"

if [ ! -f "$CHANGES_FILE" ]; then
    echo "ERROR: Changes file not found: $CHANGES_FILE"
    exit 1
fi

echo "Changes file: $CHANGES_FILE"
cat "$CHANGES_FILE"

echo ""
echo "[5/6] Uploading to PPA..."
echo "PPA: $PPA_NAME"
echo ""
read -p "Upload to PPA? [yes/NO]: " confirm

if [ "$confirm" != "yes" ]; then
    echo "Upload cancelled."
    echo ""
    echo "To upload manually:"
    echo "  dput $PPA_NAME $CHANGES_FILE"
    exit 0
fi

dput "$PPA_NAME" "$CHANGES_FILE"

echo ""
echo "============================================"
echo "Upload Complete!"
echo "============================================"
echo ""
echo "Check build status at:"
echo "  https://launchpad.net/~your-username/+archive/ubuntu/ppa-name/+packages"
echo ""
echo "Build usually takes 10-30 minutes."
echo ""
echo "After build succeeds, users can install with:"
echo "  sudo add-apt-repository $PPA_NAME"
echo "  sudo apt update"
echo "  sudo apt install whisper-voice-daemon"
echo ""
