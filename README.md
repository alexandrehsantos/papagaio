# Whisper Voice Daemon

> 🎙️ **Professional voice-to-text daemon for Linux with global hotkey support**

A lightweight, privacy-focused voice input system that runs as a background service and transcribes speech to text using OpenAI's Whisper model. Press a hotkey anywhere on your system to dictate text directly into any application.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## ✨ Features

- 🎯 **Global Hotkey** - Press `Ctrl+Alt+V` from anywhere to start voice input
- 🔒 **100% Local Processing** - All transcription happens on your machine (privacy-first)
- 🎤 **Voice Activity Detection (VAD)** - Automatically stops recording after 5 seconds of silence
- ⚡ **Fast & Accurate** - Uses Faster-Whisper (optimized Whisper implementation)
- 🔄 **Systemd Integration** - Runs as a user service, auto-starts on login
- 💬 **Desktop Notifications** - Visual feedback during recording and transcription
- 🖥️ **Works Everywhere** - Terminal, browser, IDE, any application
- 🌍 **Multi-language** - Supports Portuguese (default) and other languages

## 📦 Installation

### Prerequisites

**System Requirements:**
- Linux (Ubuntu, Debian, Fedora, Arch, etc.)
- Python 3.8 or higher
- Working microphone
- `xdotool` or `ydotool` for keyboard simulation

**Install system dependencies:**

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3-dev portaudio19-dev xdotool

# Fedora
sudo dnf install python3-devel portaudio-devel xdotool

# Arch Linux
sudo pacman -S python portaudio xdotool
```

### Quick Install

```bash
# Clone the repository
cd /mnt/development/git/personal
git clone https://github.com/YOUR_USERNAME/whisper-voice-daemon.git
cd whisper-voice-daemon

# Install Python dependencies
pip3 install -r requirements.txt

# Install and start the service
./voice-service-install.sh
```

The installer will:
- ✅ Install Python dependencies
- ✅ Create systemd user service
- ✅ Enable auto-start on login
- ✅ Start the daemon immediately

## 🚀 Usage

### Basic Commands

```bash
# Start the service
voice-ctl start

# Stop the service
voice-ctl stop

# Check status
voice-ctl status

# View logs in real-time
voice-ctl logs

# Test in foreground (for debugging)
voice-ctl test
```

### Using Voice Input

1. **Start the daemon:**
   ```bash
   voice-ctl start
   ```

2. **Press the hotkey** (`Ctrl+Alt+V`) in any application

3. **Speak clearly** - The daemon will record until you stop talking (5s silence)

4. **Text is typed automatically** - The transcribed text appears where your cursor is

### Example Workflow

```bash
# Terminal 1: Start the daemon
voice-ctl start

# Terminal 2: Open your favorite editor
vim document.txt

# Press Ctrl+Alt+V, speak your text
# Text is automatically typed into vim!
```

## ⚙️ Configuration

### Change Hotkey

Edit the systemd service file:

```bash
nano ~/.config/systemd/user/voice-daemon.service
```

Modify the `ExecStart` line:

```ini
# Use Ctrl+Shift+V instead
ExecStart=/usr/bin/python3 /path/to/voice-daemon.py -m small -k "<ctrl>+<shift>+v"
```

Reload and restart:

```bash
systemctl --user daemon-reload
voice-ctl restart
```

### Change Whisper Model

Available models (speed vs accuracy):

| Model | Size | Speed | Accuracy | Recommended For |
|-------|------|-------|----------|----------------|
| `tiny` | ~75MB | ⚡⚡⚡ | ⭐⭐ | Testing |
| `base` | ~140MB | ⚡⚡ | ⭐⭐⭐ | Quick dictation |
| `small` | ~460MB | ⚡ | ⭐⭐⭐⭐ | **Default (recommended)** |
| `medium` | ~1.5GB | 🐌 | ⭐⭐⭐⭐⭐ | Maximum accuracy |

Edit the service file and change `-m small` to your preferred model:

```bash
nano ~/.config/systemd/user/voice-daemon.service
# Change: -m small  →  -m medium
systemctl --user daemon-reload
voice-ctl restart
```

### Advanced Settings

Edit `voice-daemon.py` directly to customize:

```python
# Audio configuration (lines 25-36)
SILENCE_THRESHOLD_RMS = 400  # Microphone sensitivity
SILENCE_DURATION_SECONDS = 5.0  # Stop after X seconds of silence
MAX_RECORDING_DURATION_SECONDS = 3600  # Max 1 hour recording
```

## 🏗️ Architecture

### System Design

```
┌─────────────────────────────────────────┐
│  User Presses Ctrl+Alt+V (Global)      │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  pynput GlobalHotKeys Listener          │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  Audio Recording (PyAudio)              │
│  • VAD: Detects silence                 │
│  • Saves to temporary WAV file          │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  Faster-Whisper Transcription           │
│  • Language: Portuguese                 │
│  • VAD Filter enabled                   │
│  • Beam search: 5                       │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  Keyboard Simulation                    │
│  • xdotool (X11)                        │
│  • ydotool (Wayland) - fallback         │
│  • xclip (clipboard) - final fallback   │
└─────────────────────────────────────────┘
```

### Threading Model

- **Main Thread:** Hotkey listener (pynput)
- **Worker Thread:** Audio recording + transcription
- **Non-blocking:** UI doesn't freeze during processing

## 📝 How It Works

1. **Daemon starts** and loads Whisper model into memory
2. **Hotkey listener** waits for `Ctrl+Alt+V`
3. **Recording begins** when hotkey is pressed
4. **VAD monitors** audio volume (RMS threshold)
5. **Stops automatically** after 5 seconds of silence
6. **Whisper transcribes** the audio file
7. **Text is typed** using xdotool/ydotool
8. **Notification shows** the transcribed text

## 🔧 Troubleshooting

### Service Won't Start

```bash
# Check logs for errors
voice-ctl logs

# Test manually in foreground
python3 /path/to/voice-daemon.py -m small
```

### Hotkey Not Working

```bash
# Verify xdotool is installed
which xdotool

# Test xdotool manually
xdotool key Return

# Check if another instance is running
ps aux | grep voice-daemon
```

### Poor Transcription Quality

```bash
# 1. Use a better model
# Edit service file: -m small → -m medium

# 2. Check microphone
arecord -d 3 test.wav && aplay test.wav

# 3. Adjust silence threshold
# Edit voice-daemon.py: SILENCE_THRESHOLD_RMS = 300 (more sensitive)
```

### Microphone Not Detected

```bash
# List audio devices
arecord -l

# Test recording
arecord -d 5 -f cd test.wav

# Check permissions
groups | grep audio
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/whisper-voice-daemon.git
cd whisper-voice-daemon

# Install dev dependencies
pip3 install -r requirements.txt

# Run in debug mode
python3 voice-daemon.py -m small
```

### Code Style

- Follow PEP 8
- Use type hints where possible
- Write descriptive commit messages
- Add tests for new features

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - Amazing speech recognition model
- [Faster-Whisper](https://github.com/guillaumekln/faster-whisper) - Optimized Whisper implementation
- [pynput](https://github.com/moses-palmer/pynput) - Global hotkey support

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/YOUR_USERNAME/whisper-voice-daemon/issues)
- **Discussions:** [GitHub Discussions](https://github.com/YOUR_USERNAME/whisper-voice-daemon/discussions)

## 🗺️ Roadmap

- [ ] GUI configuration tool
- [ ] Multiple language support via config
- [ ] Custom command triggers (e.g., "hey assistant")
- [ ] Integration with popular text editors
- [ ] macOS and Windows support
- [ ] Voice commands for system control

---

**Made with ❤️ for the Linux community**

⭐ Star this repo if you find it useful!
