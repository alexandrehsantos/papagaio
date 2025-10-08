#!/bin/bash
#
# Build and Upload to PyPI
# Usage: ./build-pypi.sh [test|prod]
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
MODE="${1:-test}"

echo "============================================"
echo "Building Python Package for PyPI"
echo "Mode: $MODE"
echo "============================================"
echo ""

# Check if build tools are installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found"
    exit 1
fi

# Go to project directory
cd "$PROJECT_DIR"

echo "[1/5] Installing build tools..."
pip3 install --user --upgrade build twine

echo "[2/5] Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info/

echo "[3/5] Building package..."
python3 -m build

echo "[4/5] Checking package..."
python3 -m twine check dist/*

echo ""
echo "✓ Package built successfully!"
echo ""
ls -lh dist/

if [ "$MODE" = "test" ]; then
    echo ""
    echo "[5/5] Uploading to TestPyPI..."
    echo ""
    echo "This will upload to TestPyPI (test.pypi.org)"
    echo "You need an account at: https://test.pypi.org/account/register/"
    echo ""
    read -p "Press Enter to continue or Ctrl+C to cancel..."

    python3 -m twine upload --repository testpypi dist/*

    echo ""
    echo "============================================"
    echo "✓ Upload Complete!"
    echo "============================================"
    echo ""
    echo "Test installation:"
    echo "  pip install --index-url https://test.pypi.org/simple/ papagaio"
    echo ""

elif [ "$MODE" = "prod" ]; then
    echo ""
    echo "[5/5] Uploading to PyPI..."
    echo ""
    echo "⚠️  WARNING: This will upload to PRODUCTION PyPI!"
    echo "You need an account at: https://pypi.org/account/register/"
    echo ""
    read -p "Are you sure? Type 'yes' to continue: " confirm

    if [ "$confirm" = "yes" ]; then
        python3 -m twine upload dist/*

        echo ""
        echo "============================================"
        echo "✓ Upload Complete!"
        echo "============================================"
        echo ""
        echo "Users can now install with:"
        echo "  pip install papagaio"
        echo ""
    else
        echo "Upload cancelled."
        exit 1
    fi
else
    echo ""
    echo "[5/5] Skipping upload (local build only)"
    echo ""
    echo "To upload to TestPyPI: ./build-pypi.sh test"
    echo "To upload to PyPI:     ./build-pypi.sh prod"
    echo ""
fi
