# Papagaio

Voice-to-text daemon for Linux using OpenAI Whisper.

Papagaio runs as a background service and transcribes speech to text. Press a global hotkey anywhere on your system to dictate text into any application.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Features

- Global hotkey activation (default: Ctrl+Alt+V)
- Local processing only (no cloud services, privacy-first)
- Voice Activity Detection with automatic silence detection
- Manual stop (press hotkey again) or cancel (ESC)
- Multi-language transcription (auto-detected)
- Systemd integration with user-level service
- Multiple keyboard backends: xdotool (X11), ydotool (Wayland), xclip (fallback)

## Installation

### Requirements

- Linux (Ubuntu, Debian, Fedora, Arch, openSUSE)
- Python 3.8+
- Working microphone
- 2GB disk space for Whisper model

### PyPI (Recommended)

```bash
pip install papagaio
```

### From Source

```bash
git clone https://github.com/alexandrehsantos/papagaio.git
cd papagaio
./install.sh
```

### Distribution Packages

**Ubuntu/Debian:**
```bash
wget https://github.com/alexandrehsantos/papagaio/releases/latest/download/papagaio.deb
sudo dpkg -i papagaio.deb
sudo apt install -f
```

**Arch Linux (AUR):**
```bash
yay -S papagaio
```

## Usage

### Commands

```bash
papagaio-ctl start      # Start daemon
papagaio-ctl stop       # Stop daemon
papagaio-ctl status     # Check status
papagaio-ctl logs       # View logs
papagaio-ctl config     # Show configuration
papagaio-ctl edit       # Edit configuration
papagaio-ctl test       # Run in foreground (debug)
```

### Voice Input

1. Start the daemon: `papagaio-ctl start`
2. Press `Ctrl+Alt+V` in any application
3. Speak clearly
4. Stop recording:
   - Wait 5 seconds (auto-stop on silence)
   - Press `Ctrl+Alt+V` again (manual stop)
   - Press `ESC` (cancel)
5. Text is typed at cursor position

## Configuration

Configuration file: `~/.config/papagaio/config.ini`

```ini
[General]
model = small
language = en
hotkey = <ctrl>+<alt>+v
cache_dir = ~/.cache/whisper-models

[Audio]
silence_threshold = 400
silence_duration = 5.0
max_recording_time = 3600

[Advanced]
use_ydotool = false
typing_delay = 0.3
```

Edit with `papagaio-ctl edit`, then restart with `papagaio-ctl restart`.

### Whisper Models

| Model    | Size    | Speed  | Accuracy | Use Case              |
|----------|---------|--------|----------|-----------------------|
| tiny     | 75MB    | Fast   | Low      | Testing               |
| base     | 140MB   | Fast   | Medium   | Quick dictation       |
| small    | 460MB   | Medium | High     | Default (recommended) |
| medium   | 1.5GB   | Slow   | Highest  | Maximum accuracy      |

## Architecture

```
User presses Ctrl+Alt+V
         |
         v
  Hotkey Listener (pynput)
         |
         v
  Audio Recording (PyAudio)
  - Voice Activity Detection
  - Saves to temporary WAV
         |
         v
  Whisper Transcription
  - Auto language detection
  - VAD filter enabled
         |
         v
  Keyboard Simulation
  - xdotool (X11)
  - ydotool (Wayland)
  - xclip (fallback)
```

## Troubleshooting

**Service won't start:**
```bash
papagaio-ctl logs
python3 papagaio.py -m small  # Test manually
```

**Hotkey not working:**
```bash
which xdotool              # Verify installed
xdotool key Return         # Test manually
ps aux | grep papagaio     # Check for running instance
```

**Poor transcription:**
- Use a larger model (medium instead of small)
- Check microphone: `arecord -d 3 test.wav && aplay test.wav`
- Lower silence threshold in config

## Uninstallation

```bash
./uninstall.sh
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License. See [LICENSE](LICENSE).

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper)
- [Faster-Whisper](https://github.com/guillaumekln/faster-whisper)
- [pynput](https://github.com/moses-palmer/pynput)
