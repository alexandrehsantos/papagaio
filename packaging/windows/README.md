# Papagaio Windows Packaging

Build Windows MSI installer and portable ZIP using PyInstaller and WiX Toolset.

## Requirements

- Windows 10/11
- Python 3.8+
- PyInstaller (`pip install pyinstaller`)
- WiX Toolset 3.x (optional, for MSI creation)

## Quick Build

```powershell
# Build everything (executables + MSI)
.\build-msi.ps1

# Build only MSI (reuse existing PyInstaller output)
.\build-msi.ps1 -SkipPyInstaller

# Clean build
.\build-msi.ps1 -Clean
```

## Output

Files are created in the project's `dist/` directory:

- `papagaio-1.1.0-win64.msi` - Windows installer (if WiX is installed)
- `papagaio-1.1.0-win64-portable.zip` - Portable version (always created as fallback)

## Installation Methods

### MSI Installer (Recommended)

1. Double-click `papagaio-X.X.X-win64.msi`
2. Follow the installation wizard
3. Papagaio will auto-start on login

### Portable ZIP

1. Extract to any folder (e.g., `C:\Tools\Papagaio`)
2. Run `papagaio-tray.exe` to start the system tray
3. (Optional) Add a shortcut to Windows Startup folder

## Configuration

Configuration is stored in: `%APPDATA%\Papagaio\config.ini`

Default config is created on first run with these settings:

```ini
[General]
model = small
language = en
hotkey = <ctrl>+<shift>+<alt>+v
cache_dir = %LOCALAPPDATA%\Papagaio\models

[Audio]
silence_threshold = 400
silence_duration = 5.0
max_recording_time = 3600
```

## WiX Toolset Installation

Download from: https://wixtoolset.org/releases/

The build script automatically detects WiX in standard installation paths.

## Troubleshooting

### PyInstaller fails with "ModuleNotFoundError"

Install missing dependencies:
```powershell
pip install faster-whisper pynput pyaudio plyer pystray Pillow
```

### MSI creation fails

Ensure WiX Toolset is installed and in PATH, or the script will create a portable ZIP instead.

### Antivirus blocks the installer

PyInstaller executables may trigger false positives. Add an exception or sign the installer with a code signing certificate.

## Author

Alexandre Santos <alexandrehsantos@gmail.com>
Bulvee Company
