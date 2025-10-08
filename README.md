# Papagaio

Voice-to-text daemon for Linux - Like a parrot, it repeats what you say.

Papagaio runs as a background service and transcribes speech to text using OpenAI's Whisper model. Press a global hotkey anywhere on your system to dictate text into any application.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Features

- Global hotkey activation (default: Ctrl+Alt+V)
- Manual control: stop recording by pressing hotkey again, or cancel with ESC
- Local processing only (no cloud services)
- Voice Activity Detection (VAD) with automatic silence detection (5s threshold)
- Systemd integration with user-level service
- Desktop notifications for status feedback
- Works with any application (terminal, browser, IDE, text editor)
- Bilingual interface (English/Portuguese)
- Multi-language speech transcription (any language supported by Whisper)
- Multiple keyboard backends: xdotool (X11), ydotool (Wayland), xclip (fallback)

## Installation

### System Requirements

- Linux distribution (Ubuntu, Debian, Fedora, Arch, openSUSE, or similar)
- Python 3.8 or higher
- Working microphone
- 2GB free disk space (for Whisper model download)
- Internet connection (first-time setup only)

### Installation Methods

#### Method 1: PyPI

```bash
pip install papagaio
```

Recommended for most users. Works on all Linux distributions.

#### Method 2: From Source

```bash
git clone https://github.com/alexandrehsantos/papagaio.git
cd papagaio
./install.sh
```

The installer performs the following tasks:
- Detects Linux distribution
- Installs system dependencies (xdotool, portaudio, python3-dev)
- Installs Python dependencies
- Tests microphone access
- Prompts for configuration (language, model, hotkey)
- Creates systemd user service
- Adds papagaio-ctl to PATH

#### Method 3: Distribution Packages

**Ubuntu/Debian (.deb):**
```bash
wget https://github.com/alexandrehsantos/papagaio/releases/latest/download/papagaio.deb
sudo dpkg -i papagaio.deb
sudo apt install -f
```

**Arch Linux (AUR):**
```bash
yay -S papagaio
```

**Ubuntu PPA:**

After PPA publication, installation will be:
```bash
sudo add-apt-repository ppa:alexandrehsantos/papagaio
sudo apt update
sudo apt install papagaio
```

To publish to PPA, see: [docs/PPA-GUIDE.md](docs/PPA-GUIDE.md)

### Supported Distributions

- Ubuntu / Debian / Linux Mint / Pop!_OS
- Fedora / RHEL / CentOS
- Arch Linux / Manjaro
- openSUSE / SUSE
- Any Linux distribution with Python 3.8+

## Usage

### Basic Commands

```bash
# Start the service
papagaio-ctl start

# Stop the service
papagaio-ctl stop

# Restart the service
papagaio-ctl restart

# Check status
papagaio-ctl status

# View logs in real-time
papagaio-ctl logs

# Show configuration
papagaio-ctl config

# Edit configuration
papagaio-ctl edit

# Test in foreground (for debugging)
papagaio-ctl test

# Enable/disable auto-start
papagaio-ctl enable
papagaio-ctl disable

# Show help
papagaio-ctl help
```

### Using Voice Input

1. **Start the daemon:**
   ```bash
   papagaio-ctl start
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
papagaio-ctl start

# Terminal 2: Open your favorite editor
vim document.txt

# Press Ctrl+Alt+V, speak your text
# Text is automatically typed into vim!
```

## Uninstallation

To completely remove Whisper Voice Daemon:

```bash
cd papagaio
./uninstall.sh
```

The uninstaller will:
- Stop and remove the systemd service
- Remove installed files from `~/.local/bin/papagaio`
- Remove the `papagaio-ctl` command
- Ask if you want to remove configuration files
- Ask if you want to remove downloaded Whisper models
- Optionally remove PATH entry from shell config

## Configuration

### Easy Configuration

Edit your configuration file:

```bash
papagaio-ctl edit
```

Or view current settings:

```bash
papagaio-ctl config
```

**Configuration file location:** `~/.config/papagaio/config.ini`

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
papagaio-ctl restart
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
papagaio-ctl edit
# Change: model = small  →  model = medium
papagaio-ctl restart
```

## Architecture

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

## How It Works

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

## Troubleshooting

### Service Won't Start

```bash
# Check logs for errors
papagaio-ctl logs

# Test manually in foreground
python3 /path/to/papagaio.py -m small
```

### Hotkey Not Working

```bash
# Verify xdotool is installed
which xdotool

# Test xdotool manually
xdotool key Return

# Check if another instance is running
ps aux | grep papagaio
```

### Poor Transcription Quality

```bash
# 1. Use a better model
# Edit service file: -m small → -m medium

# 2. Check microphone
arecord -d 3 test.wav && aplay test.wav

# 3. Adjust silence threshold
# Edit papagaio.py: SILENCE_THRESHOLD_RMS = 300 (more sensitive)
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

## Contributing

Contributions are welcome. Please submit pull requests or open issues on GitHub.

### Development Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/papagaio.git
cd papagaio

# Install dev dependencies
pip3 install -r requirements.txt

# Run in debug mode
python3 papagaio.py -m small
```

### Code Style

- Follow PEP 8
- Use type hints where possible
- Write descriptive commit messages
- Add tests for new features

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition model
- [Faster-Whisper](https://github.com/guillaumekln/faster-whisper) - Optimized Whisper implementation
- [pynput](https://github.com/moses-palmer/pynput) - Global hotkey library

## Support

- Issues: [GitHub Issues](https://github.com/alexandrehsantos/papagaio/issues)
- Discussions: [GitHub Discussions](https://github.com/alexandrehsantos/papagaio/discussions)

## Roadmap

- GUI configuration tool
- Multiple language support via config
- Custom command triggers (e.g., "hey assistant")
- Integration with popular text editors
- macOS and Windows support
- Voice commands for system control
