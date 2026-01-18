#!/bin/bash
#
# Papagaio Release Publisher
# Builds packages and creates GitHub release
#
# Usage:
#   ./scripts/publish-release.sh 1.1.0
#

set -e

VERSION="${1:-1.1.0}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

echo -e "${BOLD}${CYAN}Papagaio Release Publisher${NC}"
echo "Version: $VERSION"
echo ""

cd "$PROJECT_ROOT"
mkdir -p dist

# Step 1: Build DEB
echo -e "${YELLOW}[1/4]${NC} Building DEB package..."
if command -v dpkg-buildpackage &> /dev/null; then
    ./build-deb.sh || echo "DEB build failed (may need: sudo apt install debhelper dh-python)"
else
    echo "  Skipping DEB (dpkg-buildpackage not found)"
fi

# Step 2: Build AppImage
echo -e "${YELLOW}[2/4]${NC} Building AppImage..."
./packaging/appimage/build-appimage.sh || echo "AppImage build failed"

# Step 3: Build RPM (if on Fedora/RHEL)
echo -e "${YELLOW}[3/4]${NC} Building RPM..."
if command -v rpmbuild &> /dev/null; then
    ./packaging/rpm/build-rpm.sh || echo "RPM build failed"
else
    echo "  Skipping RPM (rpmbuild not found)"
fi

# Step 4: Create GitHub Release
echo -e "${YELLOW}[4/4]${NC} Creating GitHub Release..."

# Check for gh CLI
if ! command -v gh &> /dev/null; then
    echo "GitHub CLI (gh) not found. Install with:"
    echo "  sudo apt install gh  # or brew install gh"
    echo ""
    echo "Then run:"
    echo "  gh auth login"
    exit 1
fi

# List built packages
echo ""
echo "Built packages:"
ls -la dist/

# Create release
echo ""
echo "Creating GitHub release v$VERSION..."

RELEASE_NOTES="## Papagaio v$VERSION

Voice-to-text input daemon using Whisper AI.

### Installation

**Linux (DEB - Ubuntu/Debian):**
\`\`\`bash
sudo dpkg -i papagaio_${VERSION}_all.deb
sudo apt-get install -f
\`\`\`

**Linux (AppImage - Universal):**
\`\`\`bash
chmod +x Papagaio-${VERSION}-x86_64.AppImage
./Papagaio-${VERSION}-x86_64.AppImage
\`\`\`

**Linux (RPM - Fedora/RHEL):**
\`\`\`bash
sudo dnf install papagaio-${VERSION}-1.noarch.rpm
\`\`\`

**macOS (Homebrew):**
\`\`\`bash
brew tap alexandrehsantos/papagaio
brew install papagaio
\`\`\`

### Quick Start

1. Start daemon: \`papagaio-ctl start\`
2. Press hotkey: **Ctrl+Shift+Alt+V**
3. Speak clearly
4. Text appears where your cursor is

### What's New

- Cross-platform installers (Windows, Linux, macOS)
- System tray GUI
- Graphical settings interface
- Improved configuration handling
"

# Find all packages in dist/
PACKAGES=$(find dist/ -type f \( -name "*.deb" -o -name "*.rpm" -o -name "*.AppImage" -o -name "*.flatpak" -o -name "*.msi" -o -name "*.zip" \) 2>/dev/null)

if [ -n "$PACKAGES" ]; then
    gh release create "v$VERSION" $PACKAGES \
        --title "Papagaio v$VERSION" \
        --notes "$RELEASE_NOTES"

    echo -e "${GREEN}✓${NC} Release created: https://github.com/alexandrehsantos/papagaio/releases/tag/v$VERSION"
else
    echo "No packages found in dist/"
    echo "Creating release without assets..."

    gh release create "v$VERSION" \
        --title "Papagaio v$VERSION" \
        --notes "$RELEASE_NOTES"
fi

echo ""
echo -e "${GREEN}Done!${NC}"
