# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-08

### Initial Release

#### Added
- 🎯 Global hotkey support (Ctrl+Alt+V)
- 🎤 Voice Activity Detection (VAD) with automatic silence detection
- ⚡ Faster-Whisper integration for speech recognition
- 🔄 Systemd user service integration
- 💬 Desktop notifications for visual feedback
- 🖥️ Multi-backend keyboard simulation (xdotool, ydotool, xclip)
- 📝 Comprehensive documentation
- 🛠️ Installation script and control utility
- 🔒 PID file locking to prevent multiple instances
- 🧵 Non-blocking threaded recording and transcription
- 🌍 Portuguese language support (configurable for others)
- ⚙️ Configurable Whisper models (tiny, base, small, medium)
- 📊 Real-time audio level monitoring (RMS-based VAD)
- ⏱️ Configurable silence threshold and duration
- 🚀 Auto-start on login capability

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

### Added
- 🛑 Manual stop: Press hotkey again during recording to stop immediately
- ❌ Cancel recording: Press ESC key to cancel recording without transcription
- 🌍 Bilingual interface: Full English and Portuguese UI support
- 🔤 Configurable language: Command-line argument to choose interface language

### Changed
- Improved user feedback during recording with manual control instructions
- Enhanced notification messages to show available control options

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
