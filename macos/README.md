# Papagaio macOS Installation

Voice-to-text input daemon using Whisper AI for macOS.

## Installation via Homebrew (Recommended)

```bash
# Add the tap
brew tap alexandrehsantos/papagaio

# Install
brew install papagaio

# Start the service
brew services start papagaio
```

## Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/alexandrehsantos/papagaio.git
cd papagaio
```

2. Install dependencies:
```bash
brew install python@3.11 portaudio
pip3 install faster-whisper pynput pyaudio plyer pystray Pillow
```

3. Install the daemon:
```bash
# Copy scripts
mkdir -p ~/.local/bin
cp papagaio.py papagaio-settings.py papagaio-tray.py ~/.local/bin/
cp macos/papagaio-ctl-macos ~/.local/bin/papagaio-ctl
chmod +x ~/.local/bin/papagaio-ctl

# Install launchd service
cp macos/com.bulvee.papagaio.plist ~/Library/LaunchAgents/
```

4. Start the service:
```bash
launchctl load ~/Library/LaunchAgents/com.bulvee.papagaio.plist
```

## Usage

```bash
papagaio-ctl start     # Start daemon
papagaio-ctl stop      # Stop daemon
papagaio-ctl status    # Check status
papagaio-ctl logs      # View logs
papagaio-settings      # Open settings GUI
papagaio-tray          # Start system tray
```

Default hotkey: **Cmd+Shift+Alt+V**

## Permissions

macOS requires accessibility permissions for keyboard simulation:

1. Open **System Preferences** > **Security & Privacy** > **Privacy**
2. Select **Accessibility** in the sidebar
3. Click the lock icon to make changes
4. Add Terminal (or your terminal emulator) to the list
5. If using Homebrew, also add the Papagaio executable

## Configuration

Configuration file: `~/.config/papagaio/config.ini`

```ini
[General]
model = small
language = en
hotkey = <cmd>+<shift>+<alt>+v
cache_dir = ~/.cache/whisper-models

[Audio]
silence_threshold = 400
silence_duration = 5.0

[Advanced]
typing_delay = 0.3
```

## Uninstall

### Homebrew
```bash
brew services stop papagaio
brew uninstall papagaio
```

### Manual
```bash
launchctl unload ~/Library/LaunchAgents/com.bulvee.papagaio.plist
rm ~/Library/LaunchAgents/com.bulvee.papagaio.plist
rm -rf ~/.local/bin/papagaio*
rm -rf ~/.config/papagaio
rm -rf ~/.cache/whisper-models
```

## Troubleshooting

### Daemon not starting
Check logs: `papagaio-ctl logs`

### Hotkey not working
Ensure accessibility permissions are granted.

### Text not being typed
Some applications may block simulated keyboard input. Try a different application.

## Author

Alexandre Santos <alexandrehsantos@gmail.com>
Bulvee Company
