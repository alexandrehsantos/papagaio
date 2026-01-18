# Papagaio Packaging Guide

This document describes how to build installation packages for all supported platforms.

## Package Types

| Platform | Package Type | Build Script | Output |
|----------|-------------|--------------|--------|
| Windows | MSI + Portable ZIP | `packaging/windows/build-msi.ps1` | `dist/papagaio-*.msi` |
| Linux | DEB | `build-deb.sh` | `dist/papagaio_*.deb` |
| Linux | RPM | `packaging/rpm/build-rpm.sh` | `dist/papagaio-*.rpm` |
| Linux | AppImage | `packaging/appimage/build-appimage.sh` | `dist/Papagaio-*.AppImage` |
| Linux | Flatpak | `packaging/flatpak/build-flatpak.sh` | `dist/papagaio-*.flatpak` |
| macOS | Homebrew | `Formula/papagaio.rb` | Homebrew tap |

## Quick Build Commands

### Linux (on the target platform)

```bash
# Debian/Ubuntu (.deb)
./build-deb.sh

# Fedora/RHEL (.rpm)
./packaging/rpm/build-rpm.sh

# Universal (AppImage)
./packaging/appimage/build-appimage.sh

# Universal (Flatpak)
./packaging/flatpak/build-flatpak.sh
```

### Windows (PowerShell)

```powershell
cd packaging\windows
.\build-msi.ps1
```

### macOS (via Homebrew)

```bash
# For users
brew tap alexandrehsantos/papagaio
brew install papagaio

# For maintainers: update Formula/papagaio.rb
```

## Build Requirements

### All Platforms
- Python 3.8+
- pip

### Linux DEB
- `debhelper`
- `dh-python`
- `python3-all`

### Linux RPM
- `rpm-build`
- `rpmdevtools`

### Linux AppImage
- `curl` (for downloading appimagetool)
- `fuse` (for running AppImages)

### Linux Flatpak
- `flatpak`
- `flatpak-builder`
- `org.freedesktop.Platform//23.08`
- `org.freedesktop.Sdk//23.08`

### Windows
- Python 3.8+ (from python.org)
- PyInstaller (`pip install pyinstaller`)
- WiX Toolset 3.x (optional, for MSI)

### macOS
- Homebrew
- Python 3.11+ (`brew install python@3.11`)
- PortAudio (`brew install portaudio`)

## Output Directory

All build scripts output packages to the `dist/` directory:

```
dist/
├── papagaio_1.1.0_all.deb              # Debian package
├── papagaio-1.1.0-1.noarch.rpm         # RPM package
├── Papagaio-1.1.0-x86_64.AppImage      # AppImage
├── papagaio-1.1.0.flatpak              # Flatpak bundle
└── papagaio-1.1.0-win64.msi            # Windows MSI
```

## Directory Structure

```
papagaio/
├── packaging/
│   ├── windows/
│   │   ├── papagaio.spec           # PyInstaller spec
│   │   ├── papagaio.wxs            # WiX installer config
│   │   ├── build-msi.ps1           # Build script
│   │   └── README.md
│   ├── appimage/
│   │   └── build-appimage.sh       # AppImage builder
│   ├── rpm/
│   │   ├── papagaio.spec           # RPM spec file
│   │   └── build-rpm.sh            # Build script
│   └── flatpak/
│       ├── com.bulvee.papagaio.yml # Flatpak manifest
│       ├── com.bulvee.papagaio.metainfo.xml
│       ├── papagaio.svg            # App icon
│       └── build-flatpak.sh        # Build script
├── debian/                          # Debian packaging
│   ├── control
│   ├── rules
│   └── ...
├── Formula/
│   └── papagaio.rb                 # Homebrew formula
├── macos/
│   ├── com.bulvee.papagaio.plist   # launchd service
│   ├── papagaio-ctl-macos          # macOS control script
│   └── README.md
├── build-deb.sh                    # DEB builder
└── PACKAGING.md                    # This file
```

## Versioning

Update version in these files before release:
- `install.sh` (VERSION variable)
- `packaging/windows/papagaio.wxs` (ProductVersion)
- `packaging/rpm/papagaio.spec` (Version)
- `packaging/appimage/build-appimage.sh` (VERSION)
- `packaging/flatpak/com.bulvee.papagaio.yml` (tag/branch)
- `packaging/flatpak/com.bulvee.papagaio.metainfo.xml` (release version)
- `Formula/papagaio.rb` (url, sha256)
- `macos/papagaio-ctl-macos` (version command)

## Release Checklist

1. Update version numbers in all files
2. Update CHANGELOG.md
3. Create git tag: `git tag -a v1.1.0 -m "Release 1.1.0"`
4. Push tag: `git push origin v1.1.0`
5. Build packages for each platform
6. Create GitHub release with packages
7. Update Homebrew formula with new SHA256

## Author

Alexandre Santos <alexandrehsantos@gmail.com>
Bulvee Company <support@bulvee.com>
