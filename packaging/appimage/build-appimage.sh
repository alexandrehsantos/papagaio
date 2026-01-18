#!/bin/bash
#
# Papagaio AppImage Build Script
# Creates portable AppImage for Linux distributions
#
# Author: Alexandre Santos <alexandrehsantos@gmail.com>
# Company: Bulvee Company
#
# Requirements:
#   - Python 3.8+
#   - appimagetool (downloaded automatically)
#   - pip packages: python-appimage (optional)
#
# Usage:
#   ./build-appimage.sh
#   ./build-appimage.sh --clean

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
APP_DIR="$BUILD_DIR/Papagaio.AppDir"
OUTPUT_DIR="$PROJECT_ROOT/dist"

VERSION="1.1.0"
APP_NAME="Papagaio"
APP_ID="com.bulvee.papagaio"

print_header() {
    echo -e "${BLUE}${BOLD}"
    echo "============================================"
    echo "  Papagaio AppImage Builder"
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

# Clean previous builds
clean_build() {
    echo "Cleaning previous builds..."
    rm -rf "$BUILD_DIR"
    rm -f "$OUTPUT_DIR"/*.AppImage
}

# Download appimagetool if needed
get_appimagetool() {
    local tool="$BUILD_DIR/appimagetool"

    if [ -x "$tool" ]; then
        return 0
    fi

    echo "Downloading appimagetool..."
    mkdir -p "$BUILD_DIR"

    local arch=$(uname -m)
    local url="https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-${arch}.AppImage"

    curl -L -o "$tool" "$url"
    chmod +x "$tool"

    print_success "appimagetool downloaded"
}

# Create AppDir structure
create_appdir() {
    echo "Creating AppDir structure..."

    rm -rf "$APP_DIR"
    mkdir -p "$APP_DIR/usr/bin"
    mkdir -p "$APP_DIR/usr/lib/papagaio"
    mkdir -p "$APP_DIR/usr/share/applications"
    mkdir -p "$APP_DIR/usr/share/icons/hicolor/256x256/apps"
    mkdir -p "$APP_DIR/usr/share/metainfo"

    print_success "AppDir structure created"
}

# Copy application files
copy_files() {
    echo "Copying application files..."

    # Main scripts
    cp "$PROJECT_ROOT/papagaio.py" "$APP_DIR/usr/lib/papagaio/"
    cp "$PROJECT_ROOT/papagaio-settings.py" "$APP_DIR/usr/lib/papagaio/"
    cp "$PROJECT_ROOT/papagaio-tray.py" "$APP_DIR/usr/lib/papagaio/"

    # Make executable
    chmod +x "$APP_DIR/usr/lib/papagaio/"*.py

    print_success "Application files copied"
}

# Create AppRun script
create_apprun() {
    echo "Creating AppRun script..."

    cat > "$APP_DIR/AppRun" << 'APPRUN_EOF'
#!/bin/bash
# Papagaio AppImage launcher

SELF_DIR="$(dirname "$(readlink -f "$0")")"
export PATH="$SELF_DIR/usr/bin:$PATH"
export PYTHONPATH="$SELF_DIR/usr/lib/papagaio:$PYTHONPATH"

# Determine which component to run
case "$1" in
    --settings)
        shift
        exec python3 "$SELF_DIR/usr/lib/papagaio/papagaio-settings.py" "$@"
        ;;
    --tray)
        shift
        exec python3 "$SELF_DIR/usr/lib/papagaio/papagaio-tray.py" "$@"
        ;;
    --daemon)
        shift
        exec python3 "$SELF_DIR/usr/lib/papagaio/papagaio.py" "$@"
        ;;
    --help|-h)
        echo "Papagaio - Voice-to-Text Input"
        echo ""
        echo "Usage: $0 [OPTION]"
        echo ""
        echo "Options:"
        echo "  --daemon    Run the voice daemon (default)"
        echo "  --settings  Open settings GUI"
        echo "  --tray      Start system tray icon"
        echo "  --help      Show this help"
        echo ""
        echo "Daemon options (pass after --daemon):"
        exec python3 "$SELF_DIR/usr/lib/papagaio/papagaio.py" --help
        ;;
    *)
        # Default: run system tray
        exec python3 "$SELF_DIR/usr/lib/papagaio/papagaio-tray.py" "$@"
        ;;
esac
APPRUN_EOF

    chmod +x "$APP_DIR/AppRun"
    print_success "AppRun script created"
}

# Create desktop file
create_desktop_file() {
    echo "Creating desktop file..."

    cat > "$APP_DIR/usr/share/applications/${APP_ID}.desktop" << EOF
[Desktop Entry]
Name=Papagaio
GenericName=Voice Input
Comment=Voice-to-text input using Whisper AI
Exec=papagaio --tray
Icon=papagaio
Terminal=false
Type=Application
Categories=AudioVideo;Audio;Utility;
Keywords=voice;speech;whisper;dictation;
StartupNotify=false
X-AppImage-Version=$VERSION
EOF

    # Link to root of AppDir
    ln -sf "usr/share/applications/${APP_ID}.desktop" "$APP_DIR/${APP_ID}.desktop"

    print_success "Desktop file created"
}

# Create icon
create_icon() {
    echo "Creating icon..."

    # Create a simple SVG icon (microphone)
    cat > "$APP_DIR/usr/share/icons/hicolor/256x256/apps/papagaio.svg" << 'SVG_EOF'
<?xml version="1.0" encoding="UTF-8"?>
<svg width="256" height="256" viewBox="0 0 256 256" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#4CAF50;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#2E7D32;stop-opacity:1" />
    </linearGradient>
  </defs>
  <!-- Background circle -->
  <circle cx="128" cy="128" r="120" fill="url(#grad1)"/>
  <!-- Microphone body -->
  <rect x="96" y="48" width="64" height="96" rx="32" fill="white"/>
  <!-- Microphone stand -->
  <path d="M64 144 Q64 192 128 192 Q192 192 192 144" stroke="white" stroke-width="12" fill="none"/>
  <line x1="128" y1="192" x2="128" y2="224" stroke="white" stroke-width="12"/>
  <line x1="96" y1="224" x2="160" y2="224" stroke="white" stroke-width="12" stroke-linecap="round"/>
</svg>
SVG_EOF

    # Convert to PNG if ImageMagick is available
    if command -v convert &> /dev/null; then
        convert "$APP_DIR/usr/share/icons/hicolor/256x256/apps/papagaio.svg" \
                "$APP_DIR/usr/share/icons/hicolor/256x256/apps/papagaio.png"
        ln -sf "usr/share/icons/hicolor/256x256/apps/papagaio.png" "$APP_DIR/papagaio.png"
    else
        ln -sf "usr/share/icons/hicolor/256x256/apps/papagaio.svg" "$APP_DIR/papagaio.svg"
    fi

    print_success "Icon created"
}

# Create AppStream metadata
create_appstream() {
    echo "Creating AppStream metadata..."

    cat > "$APP_DIR/usr/share/metainfo/${APP_ID}.appdata.xml" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<component type="desktop-application">
  <id>${APP_ID}</id>
  <name>Papagaio</name>
  <summary>Voice-to-text input using Whisper AI</summary>
  <metadata_license>MIT</metadata_license>
  <project_license>MIT</project_license>

  <description>
    <p>
      Papagaio is a voice-to-text input daemon that uses OpenAI's Whisper AI
      for accurate speech recognition. Press a hotkey, speak, and the text
      is typed into any application.
    </p>
    <p>Features:</p>
    <ul>
      <li>High-quality speech recognition with Whisper AI</li>
      <li>Works with any application</li>
      <li>Configurable hotkey activation</li>
      <li>Multiple language support</li>
      <li>System tray integration</li>
    </ul>
  </description>

  <launchable type="desktop-id">${APP_ID}.desktop</launchable>

  <url type="homepage">https://github.com/alexandrehsantos/papagaio</url>
  <url type="bugtracker">https://github.com/alexandrehsantos/papagaio/issues</url>

  <developer_name>Bulvee Company</developer_name>

  <provides>
    <binary>papagaio</binary>
  </provides>

  <releases>
    <release version="$VERSION" date="$(date +%Y-%m-%d)">
      <description>
        <p>Initial AppImage release</p>
      </description>
    </release>
  </releases>

  <content_rating type="oars-1.1" />

  <categories>
    <category>AudioVideo</category>
    <category>Audio</category>
    <category>Utility</category>
  </categories>

  <keywords>
    <keyword>voice</keyword>
    <keyword>speech</keyword>
    <keyword>whisper</keyword>
    <keyword>dictation</keyword>
    <keyword>transcription</keyword>
  </keywords>
</component>
EOF

    print_success "AppStream metadata created"
}

# Build AppImage
build_appimage() {
    echo "Building AppImage..."

    mkdir -p "$OUTPUT_DIR"

    local arch=$(uname -m)
    local output_file="$OUTPUT_DIR/Papagaio-${VERSION}-${arch}.AppImage"

    # Set environment for appimagetool
    export ARCH="$arch"
    export VERSION="$VERSION"

    # Build
    "$BUILD_DIR/appimagetool" "$APP_DIR" "$output_file"

    if [ -f "$output_file" ]; then
        chmod +x "$output_file"
        print_success "AppImage created: $output_file"

        local size=$(du -h "$output_file" | cut -f1)
        echo ""
        echo -e "${GREEN}${BOLD}Build complete!${NC}"
        echo "  File: $output_file"
        echo "  Size: $size"
    else
        print_error "AppImage creation failed"
        exit 1
    fi
}

# Main
main() {
    print_header

    # Handle arguments
    if [ "$1" = "--clean" ] || [ "$1" = "-c" ]; then
        clean_build
        exit 0
    fi

    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required"
        exit 1
    fi

    print_step 1 7 "Getting appimagetool..."
    get_appimagetool

    print_step 2 7 "Creating AppDir structure..."
    create_appdir

    print_step 3 7 "Copying application files..."
    copy_files

    print_step 4 7 "Creating AppRun script..."
    create_apprun

    print_step 5 7 "Creating desktop file..."
    create_desktop_file

    print_step 6 7 "Creating icon and metadata..."
    create_icon
    create_appstream

    print_step 7 7 "Building AppImage..."
    build_appimage

    echo ""
    echo -e "${BOLD}Usage:${NC}"
    echo "  ./Papagaio-${VERSION}-$(uname -m).AppImage --tray    # Start system tray"
    echo "  ./Papagaio-${VERSION}-$(uname -m).AppImage --daemon  # Run daemon directly"
    echo "  ./Papagaio-${VERSION}-$(uname -m).AppImage --settings # Open settings"
    echo ""
}

main "$@"
