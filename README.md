# Whisper Voice Daemon

> 🎙️ **Professional voice-to-text daemon for Linux with global hotkey support**

A lightweight, privacy-focused voice input system that runs as a background service and transcribes speech to text using OpenAI's Whisper model. Press a hotkey anywhere on your system to dictate text directly into any application.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## ✨ Features

- 🎯 **Global Hotkey** - Press `Ctrl+Alt+V` from anywhere to start voice input
- 🛑 **Manual Control** - Press hotkey again to stop recording immediately, or ESC to cancel
- 🔒 **100% Local Processing** - All transcription happens on your machine (privacy-first)
- 🎤 **Voice Activity Detection (VAD)** - Automatically stops recording after 5 seconds of silence
- ⚡ **Fast & Accurate** - Uses Faster-Whisper (optimized Whisper implementation)
- 🔄 **Systemd Integration** - Runs as a user service, auto-starts on login
- 💬 **Desktop Notifications** - Visual feedback during recording and transcription
- 🖥️ **Works Everywhere** - Terminal, browser, IDE, any application
- 🌍 **Bilingual Interface** - English and Portuguese UI support
- 🗣️ **Multi-language Speech** - Transcribe in any language Whisper supports

## 📦 Installation

### System Requirements
- Linux (Ubuntu, Debian, Fedora, Arch, openSUSE, etc.)
- Python 3.8 or higher
- Working microphone
- 2GB+ free disk space (for Whisper model)
- Internet connection (for first-time model download)

---

### Installation Methods

#### 🐍 Method 1: PyPI (Recommended - Works on ALL distros)

```bash
pip install whisper-voice-daemon
```

#### 📥 Method 2: From Source (Interactive Installer)

```bash
git clone https://github.com/alexandrehsantos/whisper-voice-daemon.git
cd whisper-voice-daemon
./install.sh
```

**The installer will:**
- ✅ Auto-detect your Linux distribution
- ✅ Install system dependencies (xdotool, portaudio, python3-dev)
- ✅ Install Python dependencies
- ✅ Test your microphone
- ✅ Interactive configuration (language, model, hotkey)
- ✅ Setup systemd service
- ✅ Add `voice-ctl` to PATH

#### 🏗️ Method 3: Distribution Packages

**Ubuntu/Debian (.deb):**
```bash
# Download from releases
wget https://github.com/alexandrehsantos/whisper-voice-daemon/releases/latest/download/whisper-voice-daemon_1.0.1-1_all.deb
sudo dpkg -i whisper-voice-daemon_1.0.1-1_all.deb
sudo apt install -f
```

**Arch Linux (AUR):**
```bash
yay -S whisper-voice-daemon
# or
paru -S whisper-voice-daemon
```

**Ubuntu PPA** *(coming soon)*:
```bash
sudo add-apt-repository ppa:alexandrehsantos/whisper-voice-daemon
sudo apt update
sudo apt install whisper-voice-daemon
```

---

### Supported Distributions

✅ Ubuntu / Debian / Linux Mint / Pop!_OS
✅ Fedora / RHEL / CentOS
✅ Arch Linux / Manjaro
✅ openSUSE / SUSE
✅ Any Linux with Python 3.8+

## 🚀 Usage

### Basic Commands

```bash
# Start the service
voice-ctl start

# Stop the service
voice-ctl stop

# Restart the service
voice-ctl restart

# Check status
voice-ctl status

# View logs in real-time
voice-ctl logs

# Show configuration
voice-ctl config

# Edit configuration
voice-ctl edit

# Test in foreground (for debugging)
voice-ctl test

# Enable/disable auto-start
voice-ctl enable
voice-ctl disable

# Show help
voice-ctl help
```

### Using Voice Input

1. **Start the daemon:**
   ```bash
   voice-ctl start
   ```

2. **Press the hotkey** (`Ctrl+Alt+V`) in any application

3. **Speak clearly** - You have three ways to stop recording:
   - **Automatic:** Stop talking for 5 seconds (VAD auto-stop)
   - **Manual:** Press `Ctrl+Alt+V` again to stop immediately
   - **Cancel:** Press `ESC` to cancel (no transcription)

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

## 🗑️ Uninstallation

To completely remove Whisper Voice Daemon:

```bash
cd whisper-voice-daemon
./uninstall.sh
```

The uninstaller will:
- Stop and remove the systemd service
- Remove installed files from `~/.local/bin/voice-daemon`
- Remove the `voice-ctl` command
- Ask if you want to remove configuration files
- Ask if you want to remove downloaded Whisper models
- Optionally remove PATH entry from shell config

## ⚙️ Configuration

### Easy Configuration

Edit your configuration file:

```bash
voice-ctl edit
```

Or view current settings:

```bash
voice-ctl config
```

**Configuration file location:** `~/.config/voice-daemon/config.ini`

### Configuration Options

```ini
[General]
model = small              # Whisper model: tiny, base, small, medium
language = en              # Interface language: en, pt
hotkey = <ctrl>+<alt>+v   # Global hotkey
cache_dir = ~/.cache/whisper-models

[Audio]
silence_threshold = 400         # Microphone sensitivity (lower = more sensitive)
silence_duration = 5.0          # Silence timeout in seconds
max_recording_time = 3600       # Maximum recording duration (1 hour)

[Advanced]
use_ydotool = false            # Force ydotool instead of xdotool
typing_delay = 0.3             # Delay before typing (seconds)
```

After editing, restart the daemon:

```bash
voice-ctl restart
```

### Available Whisper Models

| Model | Size | Speed | Accuracy | Recommended For |
|-------|------|-------|----------|----------------|
| `tiny` | ~75MB | ⚡⚡⚡ | ⭐⭐ | Testing |
| `base` | ~140MB | ⚡⚡ | ⭐⭐⭐ | Quick dictation |
| `small` | ~460MB | ⚡ | ⭐⭐⭐⭐ | **Default (recommended)** |
| `medium` | ~1.5GB | 🐌 | ⭐⭐⭐⭐⭐ | Maximum accuracy |

Change model in config file:

```bash
voice-ctl edit
# Change: model = small  →  model = medium
voice-ctl restart
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
5. **Stops recording** when:
   - 5 seconds of silence detected (automatic)
   - Hotkey pressed again (manual stop)
   - ESC key pressed (cancel - no transcription)
6. **Whisper transcribes** the audio file (if not cancelled)
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
