# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-08

### Initial Release

#### Added
- Global hotkey support (Ctrl+Alt+V)
- Voice Activity Detection (VAD) with automatic silence detection
- Faster-Whisper integration for speech recognition
- Systemd user service integration
- Desktop notifications for visual feedback
- Multi-backend keyboard simulation (xdotool, ydotool, xclip)
- Comprehensive documentation
- Installation script and control utility
- PID file locking to prevent multiple instances
- Non-blocking threaded recording and transcription
- Portuguese language support (configurable for others)
- Configurable Whisper models (tiny, base, small, medium)
- Real-time audio level monitoring (RMS-based VAD)
- Configurable silence threshold and duration
- Auto-start on login capability

#### Features
- Maximum recording duration: 1 hour
- Silence detection timeout: 5 seconds
- Audio sample rate: 16kHz mono
- Model caching for fast subsequent loads
- Graceful fallback for keyboard simulation
- Signal handling for clean shutdown
- Environment variable support for X11

#### Documentation
- README with installation and usage guide
- Architecture documentation
- Contributing guidelines
- MIT License
- Professional project structure

### Technical Details

**Dependencies:**
- faster-whisper >= 1.0.0
- pynput >= 1.7.6
- pyaudio >= 0.2.13

**System Requirements:**
- Linux (any distribution)
- Python 3.8+
- xdotool or ydotool
- Working microphone

**Performance:**
- Model: small (~460MB)
- Transcription time: 2-3 seconds
- Memory usage: ~2GB RAM
- CPU: int8 quantization for efficiency

---

## [Unreleased]

### Planned
- Ubuntu PPA publication
- Snap package
- Flatpak package

## [1.1.0] - 2025-10-08

### Added - Packaging & Distribution
- PyPI package support (`pip install whisper-voice-daemon`)
- Debian package (.deb) with full debian/ structure
- AUR PKGBUILD for Arch Linux
- Installer with distro detection
- Uninstaller script
- Configuration file support (~/.config/voice-daemon/config.ini)
- Enhanced voice-ctl with new commands (config, edit, version, help)
- Makefile for building
- Publishing guide (docs/PUBLISHING.md)

### Changed
- Installer now interactive with language/model/hotkey selection
- Installer auto-detects distribution (Ubuntu/Debian/Fedora/Arch/openSUSE)
- Installer auto-installs system dependencies
- Installation to ~/.local/bin/voice-daemon (proper location)
- voice-ctl now in PATH automatically
- Improved README with multiple installation methods

### Technical
- Created setup.py for PyPI
- Created debian/control, debian/rules, debian/changelog
- Build scripts for .deb and PyPI packages
- MANIFEST.in for package inclusion
- Proper Python package structure

## [1.0.1] - 2025-10-08

### Added
- Manual stop feature: Press hotkey again to stop recording immediately
- Cancel feature: Press ESC to cancel recording without transcription
- Bilingual support: English and Portuguese interface languages
- Language selection via `-l/--lang` command-line argument

### Technical Details
- Added state management flags for manual control
- Implemented ESC key listener during recording
- Enhanced hotkey handler to toggle between start/stop
- Thread-safe flag-based communication between listeners and recording thread

---

## [1.0.0] - 2025-10-08 (Previous Release)

### Planned Features
- [ ] GUI configuration tool
- [ ] Multiple language profiles
- [ ] Voice commands for system control
- [ ] Integration with popular text editors
- [ ] macOS support
- [ ] Windows support (WSL2)
- [ ] Custom wake word detection
- [ ] Punctuation commands
- [ ] Automated testing suite
- [ ] Docker container support

### Under Consideration
- Cloud API fallback (Google Speech, AWS Transcribe)
- Plugin system for extensibility
- Mobile app for remote dictation
- Real-time streaming transcription
- Speaker identification
- Noise cancellation filters

---

[1.0.0]: https://github.com/YOUR_USERNAME/whisper-voice-daemon/releases/tag/v1.0.0
