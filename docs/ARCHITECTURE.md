# Architecture Documentation

## Overview

Papagaio is a local voice-to-text service designed for Linux systems. It runs as a systemd user service and provides global hotkey-triggered speech recognition.

## System Components

### 1. Voice Daemon (`papagaio.py`)

**Purpose:** Main daemon process that handles voice input

**Responsibilities:**
- Initialize and manage Whisper model
- Listen for global hotkey events
- Record audio with Voice Activity Detection (VAD)
- Transcribe audio to text
- Simulate keyboard input

**Key Classes:**

```python
class VoiceDaemon:
    def __init__(self, model_size, hotkey, use_ydotool, model_cache_dir)
    def initialize_model()  # Load Whisper model
    def record_audio()      # Capture microphone input with VAD
    def transcribe(audio_file)  # Convert audio to text
    def type_text(text)     # Simulate keyboard input
    def start()             # Start daemon loop
```

### 2. Control Script (`papagaio-ctl`)

**Purpose:** Command-line interface for managing the daemon

**Commands:**
- `start` - Start the systemd service
- `stop` - Stop the service
- `restart` - Restart the service
- `status` - Show service status
- `logs` - View service logs
- `test` - Run daemon in foreground
- `enable` - Enable auto-start
- `disable` - Disable auto-start

### 3. Installer (`install.sh`)

**Purpose:** Professional multi-distro installation script

**Actions:**
1. Detect Linux distribution
2. Install system dependencies (xdotool, portaudio)
3. Check Python version (>=3.8)
4. Install Python dependencies
5. Interactive configuration (model, language, hotkey)
6. Create systemd user service
7. Add papagaio-ctl to PATH

## Data Flow

```
User Input (Hotkey Press)
    ↓
[1] Hotkey Detection (pynput.GlobalHotKeys)
    ↓
[2] Start Recording Thread
    ↓
[3] Audio Capture (PyAudio)
    │
    ├─→ Calculate RMS (volume detection)
    ├─→ Detect voice activity
    ├─→ Buffer audio frames
    └─→ Stop on silence (5s threshold)
    ↓
[4] Save to Temporary WAV file
    ↓
[5] Whisper Transcription
    │
    ├─→ Load model (if not cached)
    ├─→ Apply VAD filter
    ├─→ Beam search (size=5)
    └─→ Extract text segments
    ↓
[6] Keyboard Simulation
    │
    ├─→ Try xdotool (X11)
    ├─→ Fallback: ydotool (Wayland)
    └─→ Fallback: xclip (clipboard)
    ↓
[7] Desktop Notification
    ↓
Text appears in active application
```

## Threading Model

### Main Thread
- **Purpose:** Event loop for hotkey listener
- **Library:** pynput.GlobalHotKeys
- **Blocks on:** `listener.join()`

### Recording Thread
- **Purpose:** Non-blocking audio capture and transcription
- **Created:** When hotkey is pressed
- **Destroyed:** After transcription completes
- **Benefits:** UI remains responsive during processing

## Voice Activity Detection (VAD)

### Level 1: RMS-based VAD (Python)

**Location:** `papagaio.py:75-82`

```python
def get_rms(data):
    """Calculate Root Mean Square (volume) of audio"""
    # Convert bytes to shorts
    # Calculate sum of squares
    # Return sqrt(avg)
```

**Parameters:**
- `SILENCE_THRESHOLD_RMS = 400` - Volume threshold
- `SILENCE_DURATION_SECONDS = 5.0` - Silence timeout

**Logic:**
```
if RMS > threshold:
    started_speaking = True
    silence_chunks = 0
else if started_speaking:
    silence_chunks++

if silence_chunks > max_silence_chunks:
    stop_recording()
```

### Level 2: Whisper VAD (Model-based)

**Location:** `papagaio.py:168-174`

```python
vad_parameters = {
    "threshold": 0.3,           # Sensitivity (0-1)
    "min_speech_duration_ms": 200,  # Minimum speech
    "min_silence_duration_ms": 500, # End detection
    "speech_pad_ms": 400        # Padding
}
```

**Purpose:** Remove silence from transcription, improve accuracy

## Keyboard Simulation Strategy

### Primary: xdotool (X11)

```bash
xdotool type --delay 10 -- "transcribed text"
xdotool key Return
```

**Pros:** Reliable, widely available
**Cons:** X11 only

### Fallback 1: ydotool (Wayland)

```bash
ydotool type "transcribed text"
ydotool key 28:1 28:0  # Enter key
```

**Pros:** Works on Wayland
**Cons:** Requires ydotoold daemon

### Fallback 2: xclip (Clipboard)

```bash
echo "text" | xclip -selection clipboard
```

**Pros:** Always available
**Cons:** Requires manual paste (Ctrl+V)

## Model Management

### Model Storage

**Cache Directory:** `/mnt/development/.whisper-cache/`

**Structure:**
```
.whisper-cache/
├── models--guillaumekln--faster-whisper-small/
│   ├── model.bin
│   ├── vocabulary.json
│   └── config.json
└── ...
```

### Model Loading

**First Load:** Downloads from Hugging Face (~460MB for small)
**Subsequent Loads:** Read from cache (~2 seconds)

### Memory Usage

| Model | RAM | VRAM (GPU) |
|-------|-----|------------|
| tiny  | ~1GB | ~1GB |
| base  | ~1GB | ~1GB |
| small | ~2GB | ~2GB |
| medium| ~5GB | ~5GB |

## Configuration

### Compile-time Constants

**Location:** `papagaio.py:25-36`

```python
CHUNK_SIZE = 8192              # Audio buffer size
AUDIO_FORMAT = pyaudio.paInt16 # 16-bit audio
CHANNELS = 1                   # Mono
SAMPLE_RATE = 16000           # 16kHz
SILENCE_THRESHOLD_RMS = 400   # Volume threshold
SILENCE_DURATION_SECONDS = 5.0 # Stop timeout
MAX_RECORDING_DURATION_SECONDS = 3600  # Max 1 hour
```

### Runtime Arguments

```bash
python3 papagaio.py \
    -m small \                  # Model size
    -k "<ctrl>+<alt>+v" \      # Hotkey
    --ydotool                  # Force ydotool
```

### Systemd Configuration

**File:** `~/.config/systemd/user/papagaio.service`

```ini
[Unit]
Description=Voice Input Daemon
After=graphical-session.target

[Service]
Type=simple
Environment="DISPLAY=:0"
Environment="XAUTHORITY=/home/fns/.Xauthority"
ExecStart=/usr/bin/python3 /path/to/papagaio.py -m small
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
```

## Error Handling

### Graceful Degradation

1. **xdotool fails** → Try ydotool
2. **ydotool fails** → Copy to clipboard
3. **Clipboard fails** → Log error, notify user

### Signal Handling

```python
signal.signal(SIGINT, cleanup_handler)
signal.signal(SIGTERM, cleanup_handler)
```

**Cleanup Actions:**
- Release PID lock
- Close audio stream
- Unload model
- Remove temporary files

### PID Lock

**File:** `/tmp/papagaio.pid`

**Purpose:** Prevent multiple instances

```python
fcntl.flock(pid_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
# Raises BlockingIOError if already locked
```

## Performance Optimization

### Audio Buffering

**Chunk Size:** 8192 samples
- **Too small:** High CPU overhead
- **Too large:** Delayed response

**Optimal:** 8192 (512ms @ 16kHz)

### Model Quantization

```python
compute_type="int8"
```

**Benefits:**
- 4x smaller memory footprint
- 2-3x faster inference
- Minimal accuracy loss

### Beam Search

```python
beam_size=5
```

**Trade-off:**
- Larger = More accurate, slower
- Smaller = Faster, less accurate
- 5 = Good balance

## Security Considerations

### PID File Locking

Prevents race conditions and multiple instances

### Temporary File Handling

```python
with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
    output_file = f.name
```

**Cleanup:** File deleted after transcription

### Process Isolation

Runs as user service (not system-wide)

## Extensibility

### Adding New Keyboard Backends

```python
def type_text_new_backend(text):
    """New keyboard simulation method"""
    # Implementation
    return success
```

Add to fallback chain in `type_text()`

### Adding New Languages

```python
segments, info = self.model.transcribe(
    audio_file,
    language="en",  # Change here
    # ...
)
```

### Custom VAD Parameters

Modify `vad_parameters` dict in `transcribe()`

## Future Improvements

- [ ] Plugin system for custom actions
- [ ] Voice commands ("delete last word")
- [ ] Multiple simultaneous languages
- [ ] Cloud model support (API fallback)
- [ ] GUI configuration tool
