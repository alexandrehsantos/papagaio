.PHONY: help install uninstall test clean build-deb build-pypi build-all lint format

# Variables
PYTHON := python3
PIP := pip3
PROJECT := whisper-voice-daemon
VERSION := 1.0.1

# Default target
help:
	@echo "Whisper Voice Daemon - Build System"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Development:"
	@echo "  install       - Install locally using install.sh"
	@echo "  uninstall     - Uninstall using uninstall.sh"
	@echo "  test          - Run daemon in test mode"
	@echo "  lint          - Run code quality checks"
	@echo "  format        - Format code with black"
	@echo ""
	@echo "Packaging:"
	@echo "  build-deb     - Build Debian package (.deb)"
	@echo "  build-pypi    - Build Python package (PyPI)"
	@echo "  build-all     - Build all packages"
	@echo ""
	@echo "Cleanup:"
	@echo "  clean         - Remove build artifacts"
	@echo ""
	@echo "Release:"
	@echo "  release       - Create GitHub release"
	@echo ""

install:
	@echo "Installing Whisper Voice Daemon..."
	./install.sh

uninstall:
	@echo "Uninstalling Whisper Voice Daemon..."
	./uninstall.sh

test:
	@echo "Testing daemon in foreground mode..."
	$(PYTHON) voice-daemon.py -m small

lint:
	@echo "Running linters..."
	@which flake8 > /dev/null || $(PIP) install --user flake8
	flake8 voice-daemon.py --max-line-length=120 --ignore=E501,W503 || true
	@echo "✓ Lint complete"

format:
	@echo "Formatting code..."
	@which black > /dev/null || $(PIP) install --user black
	black voice-daemon.py --line-length=120
	@echo "✓ Format complete"

clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/ dist/ *.egg-info/
	rm -rf debian/whisper-voice-daemon
	rm -f ../*.deb ../*.build ../*.buildinfo ../*.changes ../*.dsc ../*.tar.xz
	rm -rf __pycache__/ .pytest_cache/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "*~" -delete
	@echo "✓ Clean complete"

build-deb:
	@echo "Building Debian package..."
	chmod +x packaging/build-deb.sh
	./packaging/build-deb.sh

build-pypi:
	@echo "Building PyPI package..."
	chmod +x packaging/build-pypi.sh
	./packaging/build-pypi.sh

build-all: clean
	@echo "Building all packages..."
	@make build-pypi
	@echo ""
	@echo "Note: build-deb requires debuild (run manually if needed)"
	@echo ""
	@echo "✓ All packages built"

release:
	@echo "Creating release v$(VERSION)..."
	@echo "This will:"
	@echo "  1. Commit current changes"
	@echo "  2. Create git tag v$(VERSION)"
	@echo "  3. Push to GitHub"
	@echo "  4. Create GitHub release"
	@echo ""
	@read -p "Continue? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
	git add .
	git commit -m "chore: prepare release v$(VERSION)" || true
	git tag -a "v$(VERSION)" -m "Release v$(VERSION)"
	git push origin main
	git push origin "v$(VERSION)"
	gh release create "v$(VERSION)" --generate-notes
	@echo "✓ Release complete"

.DEFAULT_GOAL := help
