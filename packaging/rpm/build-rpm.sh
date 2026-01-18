#!/bin/bash
#
# Papagaio RPM Build Script
# Creates RPM package for Fedora/RHEL/CentOS
#
# Author: Alexandre Santos <alexandrehsantos@gmail.com>
# Company: Bulvee Company
#
# Requirements:
#   - rpmbuild (rpm-build package)
#   - rpmdevtools (optional, for rpmdev-setuptree)
#
# Usage:
#   ./build-rpm.sh
#   ./build-rpm.sh --clean

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
VERSION="1.1.0"
NAME="papagaio"

# RPM build directories
RPMBUILD_DIR="$HOME/rpmbuild"
SOURCES_DIR="$RPMBUILD_DIR/SOURCES"
SPECS_DIR="$RPMBUILD_DIR/SPECS"
RPMS_DIR="$RPMBUILD_DIR/RPMS"
OUTPUT_DIR="$PROJECT_ROOT/dist"

print_header() {
    echo -e "${BLUE}${BOLD}"
    echo "============================================"
    echo "  Papagaio RPM Builder"
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
    if ! command -v rpmbuild &> /dev/null; then
        print_error "rpmbuild not found"
        echo "Install with: sudo dnf install rpm-build"
        exit 1
    fi
    print_success "rpmbuild found"
}

# Setup RPM build tree
setup_tree() {
    echo "Setting up RPM build tree..."

    # Create directories
    mkdir -p "$SOURCES_DIR"
    mkdir -p "$SPECS_DIR"
    mkdir -p "$RPMBUILD_DIR/BUILD"
    mkdir -p "$RPMBUILD_DIR/BUILDROOT"
    mkdir -p "$RPMS_DIR/noarch"
    mkdir -p "$RPMBUILD_DIR/SRPMS"

    print_success "RPM build tree created"
}

# Create source tarball
create_tarball() {
    echo "Creating source tarball..."

    local tarball="$SOURCES_DIR/${NAME}-${VERSION}.tar.gz"
    local tmpdir=$(mktemp -d)
    local srcdir="$tmpdir/${NAME}-${VERSION}"

    # Create source directory
    mkdir -p "$srcdir"

    # Copy source files
    cp "$PROJECT_ROOT/papagaio.py" "$srcdir/"
    cp "$PROJECT_ROOT/papagaio-settings.py" "$srcdir/"
    cp "$PROJECT_ROOT/papagaio-tray.py" "$srcdir/"
    cp "$PROJECT_ROOT/papagaio-ctl" "$srcdir/"
    cp "$PROJECT_ROOT/papagaio-settings.desktop" "$srcdir/"
    cp "$PROJECT_ROOT/papagaio-tray.desktop" "$srcdir/"
    cp "$PROJECT_ROOT/requirements.txt" "$srcdir/"

    # Copy LICENSE if exists, or create one
    if [ -f "$PROJECT_ROOT/LICENSE" ]; then
        cp "$PROJECT_ROOT/LICENSE" "$srcdir/"
    else
        cat > "$srcdir/LICENSE" << 'EOF'
MIT License

Copyright (c) 2024 Alexandre Santos / Bulvee Company

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
    fi

    # Copy README if exists
    if [ -f "$PROJECT_ROOT/README.md" ]; then
        cp "$PROJECT_ROOT/README.md" "$srcdir/"
    fi

    # Create tarball
    tar -czf "$tarball" -C "$tmpdir" "${NAME}-${VERSION}"

    # Cleanup
    rm -rf "$tmpdir"

    print_success "Source tarball created: $tarball"
}

# Copy spec file
copy_spec() {
    echo "Copying spec file..."
    cp "$SCRIPT_DIR/papagaio.spec" "$SPECS_DIR/"
    print_success "Spec file copied"
}

# Build RPM
build_rpm() {
    echo "Building RPM..."

    cd "$SPECS_DIR"
    rpmbuild -ba papagaio.spec

    if [ $? -eq 0 ]; then
        print_success "RPM built successfully"
    else
        print_error "RPM build failed"
        exit 1
    fi
}

# Copy output
copy_output() {
    echo "Copying RPM to dist directory..."

    mkdir -p "$OUTPUT_DIR"

    # Find and copy RPMs
    find "$RPMS_DIR" -name "${NAME}-*.rpm" -exec cp {} "$OUTPUT_DIR/" \;
    find "$RPMBUILD_DIR/SRPMS" -name "${NAME}-*.src.rpm" -exec cp {} "$OUTPUT_DIR/" \;

    print_success "RPM copied to $OUTPUT_DIR"

    # List output files
    echo ""
    echo "Output files:"
    ls -la "$OUTPUT_DIR"/${NAME}*.rpm 2>/dev/null || echo "  (no RPM files found)"
}

# Clean build
clean_build() {
    echo "Cleaning build artifacts..."
    rm -rf "$RPMBUILD_DIR/BUILD/${NAME}-${VERSION}"
    rm -rf "$RPMBUILD_DIR/BUILDROOT/${NAME}-${VERSION}*"
    rm -f "$SOURCES_DIR/${NAME}-${VERSION}.tar.gz"
    rm -f "$SPECS_DIR/papagaio.spec"
    print_success "Build artifacts cleaned"
}

# Main
main() {
    print_header

    if [ "$1" = "--clean" ] || [ "$1" = "-c" ]; then
        clean_build
        exit 0
    fi

    print_step 1 6 "Checking dependencies..."
    check_deps

    print_step 2 6 "Setting up RPM build tree..."
    setup_tree

    print_step 3 6 "Creating source tarball..."
    create_tarball

    print_step 4 6 "Copying spec file..."
    copy_spec

    print_step 5 6 "Building RPM..."
    build_rpm

    print_step 6 6 "Copying output..."
    copy_output

    echo ""
    echo -e "${GREEN}${BOLD}Build complete!${NC}"
    echo ""
    echo "To install:"
    echo "  sudo dnf install $OUTPUT_DIR/${NAME}-${VERSION}-*.noarch.rpm"
    echo ""
    echo "Or on RHEL/CentOS:"
    echo "  sudo yum install $OUTPUT_DIR/${NAME}-${VERSION}-*.noarch.rpm"
    echo ""
}

main "$@"
