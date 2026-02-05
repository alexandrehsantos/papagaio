.PHONY: help install uninstall test clean build-deb build-appimage build-all lint format release

PROJECT := papagaio
VERSION := 1.2.0

help:
	@echo "Papagaio v$(VERSION) - Build System"
	@echo ""
	@echo "Usage: make <target>"
	@echo ""
	@echo "Development:"
	@echo "  install       Install locally (./install.sh)"
	@echo "  uninstall     Uninstall (./uninstall.sh)"
	@echo "  test          Run daemon in foreground"
	@echo "  lint          Run flake8"
	@echo "  format        Format with black"
	@echo ""
	@echo "Packaging:"
	@echo "  build-deb     Build .deb (PyInstaller + dpkg)"
	@echo "  build-appimage Build AppImage"
	@echo "  build-all     Build all packages"
	@echo ""
	@echo "Cleanup:"
	@echo "  clean         Remove all build artifacts"
	@echo ""

install:
	./install.sh

uninstall:
	./uninstall.sh

test:
	@echo "Running daemon in foreground..."
	python3 papagaio.py -m small

lint:
	flake8 papagaio.py --max-line-length=120 --ignore=E501,W503 || true

format:
	black papagaio.py --line-length=120

build-deb:
	chmod +x build-deb.sh
	./build-deb.sh

build-appimage:
	chmod +x build-appimage.sh
	./build-appimage.sh

build-all: clean build-deb build-appimage
	@echo "All packages built."

clean:
	@echo "Cleaning..."
	rm -rf build/ dist/ *.egg-info/
	rm -rf .build-venv .build-pyinstaller .build-appimage
	rm -rf debian/papagaio debian/.debhelper .pybuild/
	rm -f debian/debhelper-build-stamp debian/papagaio.substvars debian/files
	rm -f ../*.deb ../*.build ../*.buildinfo ../*.changes ../*.dsc ../*.tar.xz
	rm -rf __pycache__/
	find . -name "*.pyc" -delete
	@echo "Done."

release:
	@echo "Creating release v$(VERSION)..."
	@read -p "Continue? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
	git tag -a "v$(VERSION)" -m "Release v$(VERSION)"
	git push origin main
	git push origin "v$(VERSION)"
	gh release create "v$(VERSION)" \
		dist/Papagaio-$(VERSION)-$$(uname -m).AppImage \
		../papagaio_$(VERSION)-2_amd64.deb \
		--generate-notes
	@echo "Done."

.DEFAULT_GOAL := help
