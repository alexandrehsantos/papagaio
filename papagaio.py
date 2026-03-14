#!/usr/bin/env python3

__version__ = "1.3.0"

import subprocess
import sys
import tempfile
import os
import signal
import threading
import time
import platform
import shutil

# Platform detection
IS_WINDOWS = platform.system() == 'Windows'
IS_LINUX = platform.system() == 'Linux'
IS_MACOS = platform.system() == 'Darwin'

# Platform-specific imports for file locking
if IS_WINDOWS:
    import msvcrt
else:
    import fcntl

try:
    from faster_whisper import WhisperModel
    from pynput import keyboard
    from pynput.keyboard import Controller as KeyboardController, Key, KeyCode
    import pyaudio
    import numpy as np
except ImportError as e:
    print(f"Missing required dependency: {e.name}")
    print("Please install dependencies: pip install faster-whisper pynput pyaudio numpy")
    sys.exit(1)

HAS_EVDEV = False
try:
    import evdev
    import select as _select_mod
    HAS_EVDEV = True
except ImportError:
    pass

# Optional: GPU acceleration
HAS_CUDA = False
try:
    import torch
    HAS_CUDA = torch.cuda.is_available()
except ImportError:
    pass

# Hallucination patterns - common Whisper artifacts to filter out
_HALLUCINATION_PATTERNS = {
    # English artifacts
    "thanks for watching", "thank you for watching",
    "please subscribe", "like and subscribe",
    "thanks for listening", "thank you for listening",
    "see you next time", "see you in the next video",
    "continue watching", "don't forget to subscribe",
    "you", "bye", "hello",
    # Portuguese artifacts
    "obrigado por assistir", "obrigada por assistir",
    "legendas por", "legendado por", "tradução por",
    "inscreva-se", "se inscreva", "curta e inscreva",
    "obrigado por ouvir", "obrigada por ouvir",
    "até a próxima", "até o próximo vídeo",
    "tchau", "olá",
    # Spanish artifacts
    "gracias por ver", "suscribete",
    # Common noise transcriptions
    "...", "…", "hm", "hmm", "uh", "um", "ah",
}


def _is_hallucination(text):
    """Detect Whisper hallucinations and stutters."""
    if not text:
        return True

    lower = text.strip().lower().rstrip(".!?,")

    # Empty after cleanup
    if not lower:
        return True

    # Known hallucination patterns
    if lower in _HALLUCINATION_PATTERNS:
        return True

    # Detect repeated words/stutters (e.g., "as as as as")
    words = lower.split()
    if len(words) >= 3:
        # Check if same word repeated 3+ times
        for i in range(len(words) - 2):
            if words[i] == words[i+1] == words[i+2]:
                return True

    # Very short single-word responses are often noise
    if len(words) == 1 and len(lower) <= 3:
        return True

    return False


# Optional: cross-platform notifications
try:
    from plyer import notification as plyer_notification
    HAS_PLYER = True
except ImportError:
    HAS_PLYER = False

# Optional: GTK for edit dialog
HAS_GTK = False
if IS_LINUX:
    try:
        import gi
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk, GLib
        HAS_GTK = True
    except (ImportError, ValueError):
        pass


# Audio configuration constants
CHUNK_SIZE = 1024  # Smaller chunks = faster detection (~64ms at 16kHz)
AUDIO_FORMAT = pyaudio.paInt16
CHANNELS = 1
SAMPLE_RATE = 16000
SILENCE_THRESHOLD_RMS = 200  # Lower threshold for better detection
SILENCE_DURATION_SECONDS = 2.0  # 2 seconds of silence to stop (was 60 min!)
MAX_RECORDING_DURATION_SECONDS = 3600
MIN_VALID_TRANSCRIPTION_LENGTH = 3
TYPING_DELAY_SECONDS = 0.03  # Minimal delay before typing
MIN_RECORDING_DURATION_SECONDS = 0.3  # Shorter minimum
CALIBRATION_DURATION_SECONDS = 0.5  # Time to calibrate ambient noise

# Multilingual messages
MESSAGES = {
    "en": {
        "speak_now": "🎤 Speak now...",
        "press_again_to_stop": "Press {hotkey} again to stop, or ESC to cancel",
        "manually_stopped": "🛑 Manually stopped",
        "cancelled": "❌ Recording cancelled",
        "silence_detected": "Silence detected after",
        "max_time_reached": "Maximum time reached",
        "recorded": "Recorded",
        "transcribed": "📝 Transcribed",
        "no_speech": "⚠️  No speech detected",
        "no_audio": "⚠️  No audio recorded",
        "started": "🎙️  Voice Input Daemon Started (VAD Mode)",
        "mode": "Mode: Silence detection (stops when you stop talking)",
        "silence_threshold": "Silence threshold: 5.0 seconds",
        "max_duration": "Maximum duration: 1 HOUR continuous recording",
        "buffer": "Buffer: 8192 chunks (optimized for 64GB RAM)",
        "press_hotkey": "Press hotkey and SPEAK - stops automatically after 5s silence",
        "press_hotkey_manual": "Press hotkey again to stop manually, or ESC to cancel",
        "speak_duration": "You can speak for up to 1 HOUR continuously!",
        "press_ctrl_c": "Press Ctrl+C to stop the daemon",
        "notification_ready": "Press {hotkey} and speak - stops when you stop talking"
    },
    "pt": {
        "speak_now": "🎤 Fale agora...",
        "press_again_to_stop": "Pressione {hotkey} novamente para parar, ou ESC para cancelar",
        "manually_stopped": "🛑 Parado manualmente",
        "cancelled": "❌ Gravação cancelada",
        "silence_detected": "Silêncio detectado após",
        "max_time_reached": "Tempo máximo atingido",
        "recorded": "Gravado",
        "transcribed": "📝 Transcrito",
        "no_speech": "⚠️  Nenhuma fala detectada",
        "no_audio": "⚠️  Sem áudio gravado",
        "started": "🎙️  Daemon de Voz Iniciado (Modo VAD)",
        "mode": "Modo: Detecção de silêncio (para quando você parar de falar)",
        "silence_threshold": "Limite de silêncio: 5.0 segundos",
        "max_duration": "Duração máxima: 1 HORA de gravação contínua",
        "buffer": "Buffer: 8192 chunks (otimizado para 64GB RAM)",
        "press_hotkey": "Pressione o atalho e FALE - para automaticamente após 5s de silêncio",
        "press_hotkey_manual": "Pressione o atalho novamente para parar manualmente, ou ESC para cancelar",
        "speak_duration": "Você pode falar por até 1 HORA continuamente!",
        "press_ctrl_c": "Pressione Ctrl+C para parar o daemon",
        "notification_ready": "Pressione {hotkey} e fale - para quando você parar de falar"
    }
}


class VoiceDaemon:
    def __init__(self, model_size="small", hotkey="<ctrl>+<shift>+<alt>+v", secondary_hotkey="", auto_enter=False, use_ydotool=False, model_cache_dir=None, lang="en", silence_threshold=None, silence_duration=None, transcription_language="auto", edit_before_send=False):
        self.model_size = model_size
        self.hotkey = hotkey
        self.secondary_hotkey = secondary_hotkey
        self.auto_enter = auto_enter
        self.use_ydotool = use_ydotool
        self.model_cache_dir = model_cache_dir or os.path.expanduser("~/.cache/whisper-models")
        self.lang = lang if lang in MESSAGES else "en"
        self.transcription_language = transcription_language if transcription_language != "auto" else None
        self.edit_before_send = edit_before_send
        self.model = None
        self.is_recording = False
        self.stop_recording_flag = False  # For manual stop (hotkey pressed again)
        self.cancel_recording_flag = False  # For ESC key
        self.recording_thread = None
        self.esc_listener = None
        self.pid_file = os.path.join(tempfile.gettempdir(), "papagaio.pid")
        self._hotkey_cooldown = 0
        self._stop_listener = False
        self._target_window_id = None
        self._typing_in_progress = False

        # Cache tool availability (avoids repeated PATH lookups)
        self._has_xdotool = bool(shutil.which("xdotool"))
        self._has_xclip = bool(shutil.which("xclip"))
        self._has_wl_copy = bool(shutil.which("wl-copy"))
        self._has_ydotool = bool(shutil.which("ydotool"))
        self._has_notify_send = bool(shutil.which("notify-send"))

        # Audio settings for VAD
        self.CHUNK = CHUNK_SIZE
        self.FORMAT = AUDIO_FORMAT
        self.CHANNELS = CHANNELS
        self.RATE = SAMPLE_RATE
        self.SILENCE_THRESHOLD = silence_threshold if silence_threshold is not None else SILENCE_THRESHOLD_RMS
        self.SILENCE_DURATION = silence_duration if silence_duration is not None else SILENCE_DURATION_SECONDS
        self.MAX_RECORDING_TIME = MAX_RECORDING_DURATION_SECONDS

    _EVDEV_KEY_MAP = {
        '<ctrl>': {evdev.ecodes.KEY_LEFTCTRL, evdev.ecodes.KEY_RIGHTCTRL} if HAS_EVDEV else set(),
        '<shift>': {evdev.ecodes.KEY_LEFTSHIFT, evdev.ecodes.KEY_RIGHTSHIFT} if HAS_EVDEV else set(),
        '<alt>': {evdev.ecodes.KEY_LEFTALT, evdev.ecodes.KEY_RIGHTALT} if HAS_EVDEV else set(),
        '<super>': {evdev.ecodes.KEY_LEFTMETA, evdev.ecodes.KEY_RIGHTMETA} if HAS_EVDEV else set(),
        '<cmd>': {evdev.ecodes.KEY_LEFTMETA, evdev.ecodes.KEY_RIGHTMETA} if HAS_EVDEV else set(),
        '<esc>': {evdev.ecodes.KEY_ESC} if HAS_EVDEV else set(),
    }

    _EVDEV_CHAR_MAP = {
        'a': 'KEY_A', 'b': 'KEY_B', 'c': 'KEY_C', 'd': 'KEY_D', 'e': 'KEY_E',
        'f': 'KEY_F', 'g': 'KEY_G', 'h': 'KEY_H', 'i': 'KEY_I', 'j': 'KEY_J',
        'k': 'KEY_K', 'l': 'KEY_L', 'm': 'KEY_M', 'n': 'KEY_N', 'o': 'KEY_O',
        'p': 'KEY_P', 'q': 'KEY_Q', 'r': 'KEY_R', 's': 'KEY_S', 't': 'KEY_T',
        'u': 'KEY_U', 'v': 'KEY_V', 'w': 'KEY_W', 'x': 'KEY_X', 'y': 'KEY_Y',
        'z': 'KEY_Z',
    }

    def _parse_hotkey_evdev(self, hotkey_str):
        modifier_groups = []
        trigger_key = None
        for part in hotkey_str.lower().split('+'):
            part = part.strip()
            if part in self._EVDEV_KEY_MAP:
                modifier_groups.append(self._EVDEV_KEY_MAP[part])
            elif part.strip('<>') in self._EVDEV_CHAR_MAP:
                char = part.strip('<>')
                trigger_key = getattr(evdev.ecodes, self._EVDEV_CHAR_MAP[char])
            elif len(part) == 1 and part in self._EVDEV_CHAR_MAP:
                trigger_key = getattr(evdev.ecodes, self._EVDEV_CHAR_MAP[part])
        return modifier_groups, trigger_key

    def _get_evdev_keyboards(self):
        devices = []
        for path in evdev.list_devices():
            try:
                dev = evdev.InputDevice(path)
                caps = dev.capabilities()
                if evdev.ecodes.EV_KEY in caps:
                    key_caps = caps[evdev.ecodes.EV_KEY]
                    if evdev.ecodes.KEY_A in key_caps or evdev.ecodes.KEY_ENTER in key_caps:
                        devices.append(dev)
            except PermissionError:
                continue
        return devices

    def _evdev_listener_loop(self):
        keyboards = self._get_evdev_keyboards()
        if not keyboards:
            return False

        kb_names = [k.name for k in keyboards]
        print(f"[Papagaio] evdev keyboards: {kb_names}", flush=True)

        modifier_groups, trigger_key = self._parse_hotkey_evdev(self.hotkey)
        print(f"[Papagaio] evdev hotkey: modifiers={modifier_groups} trigger={trigger_key}", flush=True)
        pressed = set()
        heartbeat = 0
        while not self._stop_listener:
            heartbeat += 1
            if heartbeat <= 3:
                print(f"[Papagaio] evdev loop tick {heartbeat}", flush=True)
            r, _, _ = _select_mod.select(keyboards, [], [], 0.5)
            for dev in r:
                try:
                    for event in dev.read():
                        if event.type != evdev.ecodes.EV_KEY:
                            continue
                        if event.value == 1:  # key down
                            pressed.add(event.code)
                            if event.code in (29, 97, 42, 54, 56, 100, trigger_key):
                                key_name = evdev.ecodes.KEY.get(event.code, event.code)
                                print(f"[Papagaio] MOD key={key_name} pressed={pressed}", flush=True)
                            if event.code == trigger_key:
                                modifiers_held = all(
                                    any(k in pressed for k in group)
                                    for group in modifier_groups
                                )
                                now = time.monotonic()
                                if modifiers_held and now - self._hotkey_cooldown > 2.0:
                                    self._hotkey_cooldown = now
                                    self.on_activate()
                            if event.code == evdev.ecodes.KEY_ESC and self.is_recording:
                                self.cancel_recording_flag = True
                        elif event.value == 0:  # key up
                            pressed.discard(event.code)
                except OSError:
                    pass
        return True

    # X11 keysym values for modifier keys
    _MODIFIER_KEYSYMS = {
        '<ctrl>': {65507, 65508},      # Control_L, Control_R
        '<shift>': {65505, 65506},     # Shift_L, Shift_R
        '<alt>': {65513, 65514, 65511, 65027},  # Alt_L, Alt_R, Meta_L, ISO_Level3_Shift
        '<super>': {65515, 65516},     # Super_L, Super_R
        '<cmd>': {65515, 65516},       # Super_L, Super_R
    }

    @staticmethod
    def _key_to_keysym(key):
        """Extract X11 keysym from any pynput key object"""
        if hasattr(key, 'vk') and key.vk is not None:
            return key.vk
        if hasattr(key, 'value') and key.value is not None:
            v = key.value
            if isinstance(v, int):
                return v
            if hasattr(v, 'vk') and v.vk is not None:
                return v.vk
            try:
                return int(v)
            except (TypeError, ValueError):
                pass
        return None

    def _parse_hotkey_pynput(self, hotkey_str):
        modifier_keysym_sets = []
        trigger_char = None
        for part in hotkey_str.lower().split('+'):
            part = part.strip()
            if part in self._MODIFIER_KEYSYMS:
                modifier_keysym_sets.append(self._MODIFIER_KEYSYMS[part])
            elif len(part) == 1:
                trigger_char = part
            elif part.startswith('<') and part.endswith('>'):
                trigger_char = part.strip('<>')
        return modifier_keysym_sets, trigger_char

    def _release_modifiers(self):
        """Release all modifier keys to prevent stuck keys after hotkey activation"""
        if IS_LINUX and self._has_xdotool:
            try:
                subprocess.run(
                    ["xdotool", "keyup", "ctrl", "shift", "alt", "super"],
                    timeout=2, stderr=subprocess.DEVNULL
                )
            except Exception:
                pass

    def _resolve_xbindkeys_combo(self, hotkey_str):
        """Convert a hotkey string to xbindkeys format"""
        hotkey_lower = hotkey_str.lower().strip()
        mouse_map = {"mouse_middle": "b:2", "mouse_right": "b:3",
                     "mouse_back": "b:8", "mouse_forward": "b:9"}
        if hotkey_lower in mouse_map:
            return mouse_map[hotkey_lower]

        hotkey_parts = hotkey_lower.split('+')
        xbk_parts = []
        for part in hotkey_parts:
            part = part.strip().strip('<>')
            mapping = {"ctrl": "control", "alt": "alt", "shift": "shift",
                       "super": "mod4", "cmd": "mod4"}
            xbk_parts.append(mapping.get(part, part))
        return "+".join(xbk_parts)

    def _xbindkeys_listener_loop(self):
        """Hotkey listener using xbindkeys (most reliable X11 hotkey method)"""
        if not shutil.which("xbindkeys"):
            return False

        pid = os.getpid()
        rc_path = os.path.join(tempfile.gettempdir(), f"papagaio_{pid}.xbindkeysrc")

        combos = []
        xbk_primary = self._resolve_xbindkeys_combo(self.hotkey)
        combos.append(xbk_primary)

        if self.secondary_hotkey:
            xbk_secondary = self._resolve_xbindkeys_combo(self.secondary_hotkey)
            if xbk_secondary != xbk_primary:
                combos.append(xbk_secondary)

        with open(rc_path, "w") as f:
            for combo in combos:
                f.write(f'"kill -USR1 {pid}"\n')
                f.write(f"  {combo}\n\n")

        self._xbindkeys_proc = proc = subprocess.Popen(
            ["xbindkeys", "-f", rc_path, "-n"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

        signal.signal(signal.SIGUSR1, self._on_hotkey_signal)

        combo_str = " + ".join(combos) if len(combos) > 1 else combos[0]
        print(f"[Papagaio] xbindkeys listener started (combos={combo_str})", flush=True)

        try:
            while proc.poll() is None:
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass
        finally:
            signal.signal(signal.SIGUSR1, signal.SIG_DFL)
            proc.terminate()
            proc.wait()
            try:
                os.unlink(rc_path)
            except OSError:
                pass
        return True

    def _on_hotkey_signal(self, signum, frame):
        """Handle SIGUSR1 from xbindkeys"""
        if self._typing_in_progress:
            return
        if self.is_recording:
            self.stop_recording_flag = True
            return

        now = time.monotonic()
        if now - self._hotkey_cooldown > 2.0:
            self._hotkey_cooldown = now
            print("[Papagaio] Hotkey detected via xbindkeys", flush=True)
            threading.Thread(target=self._hotkey_thread, daemon=True).start()

    def _hotkey_thread(self):
        """Run hotkey activation in a separate thread (signal handlers must be fast)"""
        try:
            time.sleep(0.02)
            self._release_modifiers()
            self.on_activate()
        except Exception as e:
            print(f"[Papagaio] Hotkey thread error: {e}", flush=True)
            import traceback
            traceback.print_exc()

    def _pynput_listener_loop(self):
        modifier_keysym_sets, trigger_char = self._parse_hotkey_pynput(self.hotkey)
        pressed_keysyms = set()

        def on_press(key):
            keysym = self._key_to_keysym(key)
            if keysym is not None:
                pressed_keysyms.add(keysym)

            char = None
            if hasattr(key, 'char') and key.char:
                char = key.char.lower()
            elif hasattr(key, 'vk') and key.vk and 65 <= key.vk <= 90:
                char = chr(key.vk + 32)

            if char == trigger_char:
                all_held = all(
                    bool(pressed_keysyms & keysym_set)
                    for keysym_set in modifier_keysym_sets
                )
                now = time.monotonic()
                if all_held and now - self._hotkey_cooldown > 2.0:
                    self._hotkey_cooldown = now
                    pressed_keysyms.clear()
                    time.sleep(0.1)
                    self._release_modifiers()
                    self.on_activate()

            esc_keysym = 65307
            if keysym == esc_keysym and self.is_recording:
                self.cancel_recording_flag = True

        def on_release(key):
            keysym = self._key_to_keysym(key)
            if keysym is not None:
                pressed_keysyms.discard(keysym)

        with keyboard.Listener(on_press=on_press, on_release=on_release, suppress=False) as listener:
            listener.join()

    def msg(self, key):
        """Get translated message"""
        return MESSAGES[self.lang].get(key, MESSAGES["en"].get(key, key))

    def initialize_model(self):
        if self.model is None:
            import multiprocessing

            os.makedirs(self.model_cache_dir, exist_ok=True)

            # Auto-detect optimal device and compute type
            if HAS_CUDA:
                device = "cuda"
                compute_type = "float16"  # GPU: use float16 for speed
                print(f"[Papagaio] 🚀 Using GPU (CUDA) for transcription")
            else:
                device = "cpu"
                compute_type = "int8"  # CPU: use int8 quantization
                print(f"[Papagaio] Using CPU for transcription")

            # Use optimal worker count (CPU cores - 1, max 8)
            optimal_workers = min(max(multiprocessing.cpu_count() - 1, 1), 8)

            print(f"[Papagaio] Loading Whisper {self.model_size} model...")
            print(f"[Papagaio] Device: {device}, Compute: {compute_type}, Workers: {optimal_workers}")
            print(f"[Papagaio] Cache dir: {self.model_cache_dir}")

            self.model = WhisperModel(
                self.model_size,
                device=device,
                compute_type=compute_type,
                num_workers=optimal_workers,
                download_root=self.model_cache_dir
            )
            print(f"[Papagaio] ✓ Model loaded!")

    def get_rms(self, data):
        """Calculate RMS (volume) of audio chunk - optimized with NumPy"""
        # Convert bytes directly to int16 array (zero-copy view)
        audio_data = np.frombuffer(data, dtype=np.int16)
        # Vectorized RMS calculation (5-10x faster than Python loop)
        return np.sqrt(np.mean(audio_data.astype(np.float32) ** 2))

    _THRESHOLD_CACHE_TTL = 60  # Reuse calibration for 60 seconds

    def calibrate_noise_floor(self, stream, duration=0.5):
        """Measure ambient noise level for adaptive threshold (cached)"""
        now = time.monotonic()
        if (hasattr(self, '_cached_threshold') and
                now - self._threshold_timestamp < self._THRESHOLD_CACHE_TTL):
            print(f"[Papagaio] Threshold: {self._cached_threshold} (cached)")
            return self._cached_threshold

        samples = int(duration * self.RATE / self.CHUNK)
        rms_values = []

        for _ in range(samples):
            data = stream.read(self.CHUNK, exception_on_overflow=False)
            rms_values.append(self.get_rms(data))

        if rms_values:
            avg_noise = sum(rms_values) / len(rms_values)
            threshold = max(100, int(avg_noise * 2.5))
        else:
            threshold = self.SILENCE_THRESHOLD

        self._cached_threshold = threshold
        self._threshold_timestamp = now
        return threshold

    def record_audio(self):
        """Record audio until silence is detected"""
        audio = pyaudio.PyAudio()

        try:
            stream = audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )

            # Auto-calibrate noise floor
            print(f"[Papagaio] 🎚️  Calibrating...")
            adaptive_threshold = self.calibrate_noise_floor(stream)
            print(f"[Papagaio] Threshold: {adaptive_threshold} (auto)")

            print(f"[Papagaio] {self.msg('speak_now')}")
            print(f"[Papagaio] {self.msg('press_hotkey_manual')}")
            self.show_notification("Papagaio", self.msg("speak_now") + "\n" + self.msg("press_again_to_stop").format(hotkey=self.hotkey), "low")

            frames = []
            silence_chunks = 0
            max_silence_chunks = int(self.SILENCE_DURATION * self.RATE / self.CHUNK)
            started_speaking = False
            min_recording_chunks = int(MIN_RECORDING_DURATION_SECONDS * self.RATE / self.CHUNK)
            speech_threshold = adaptive_threshold  # Use calibrated threshold

            try:
                while True:
                    # Check for manual stop or cancel flags
                    if self.cancel_recording_flag:
                        print(f"\n[Papagaio] {self.msg('cancelled')}")
                        self.show_notification("Papagaio", self.msg("cancelled"), "normal")
                        return None

                    if self.stop_recording_flag:
                        print(f"\n[Papagaio] {self.msg('manually_stopped')}")
                        break

                    data = stream.read(self.CHUNK, exception_on_overflow=False)
                    frames.append(data)

                    rms = self.get_rms(data)

                    if rms > speech_threshold:
                        started_speaking = True
                        silence_chunks = 0
                        # Visual feedback: show audio level
                        level = min(10, int(rms / speech_threshold * 3))
                        print("█" * level, end="", flush=True)
                    else:
                        if started_speaking:
                            silence_chunks += 1
                            print("·", end="", flush=True)

                    if started_speaking and silence_chunks > max_silence_chunks:
                        if len(frames) > min_recording_chunks:
                            print(f"\n[Papagaio] {self.msg('silence_detected')} {self.SILENCE_DURATION}s")
                            break

                    # Check max recording time
                    if len(frames) > int(self.MAX_RECORDING_TIME * self.RATE / self.CHUNK):
                        print(f"\n[Papagaio] {self.msg('max_time_reached')} ({self.MAX_RECORDING_TIME}s)")
                        break

            except KeyboardInterrupt:
                pass
            finally:
                stream.stop_stream()
                stream.close()
        finally:
            audio.terminate()

        if not started_speaking:
            return None

        duration = len(frames) * self.CHUNK / self.RATE
        print(f"[Papagaio] {self.msg('recorded')}: {duration:.1f}s")

        # Convert raw bytes to float32 numpy array (faster-whisper native format)
        audio_array = np.frombuffer(b"".join(frames), dtype=np.int16).astype(np.float32) / 32768.0
        return audio_array

    def transcribe(self, audio_data):
        """Transcribe audio data to text (accepts numpy array or file path)"""
        self.initialize_model()

        if HAS_CUDA:
            beam_size = 2
            best_of = 1
        else:
            beam_size = 1
            best_of = 1

        segments, info = self.model.transcribe(
            audio_data,
            language=self.transcription_language,
            beam_size=beam_size,
            best_of=best_of,
            vad_filter=True,
            vad_parameters={
                "threshold": 0.35,
                "min_speech_duration_ms": 100,
                "min_silence_duration_ms": 250,
                "speech_pad_ms": 250
            },
            without_timestamps=True,
            word_timestamps=False,
            condition_on_previous_text=False
        )

        detected_lang = info.language
        confidence = info.language_probability
        print(f"[Papagaio] Language: {detected_lang} ({confidence:.0%} confidence)")

        # More efficient string joining with generator
        text = " ".join(segment.text.strip() for segment in segments)
        text = text.strip()

        # Filter hallucinations and stutters
        if _is_hallucination(text):
            print(f"[Papagaio] ⚠ Filtered hallucination: {text[:50]}")
            return ""

        return text

    def type_text_pynput(self, text):
        """Type text using pynput (cross-platform)"""
        if not text:
            return False

        try:
            time.sleep(TYPING_DELAY_SECONDS)
            kb = KeyboardController()
            kb.type(text)
            # Don't press Enter - let user decide
            print(f"[Papagaio] ✓ Typed (pynput): {text[:50]}...")
            return True
        except Exception as e:
            print(f"[Papagaio] pynput typing failed: {e}")
            return False

    def type_text_ydotool(self, text):
        """Type text using ydotool (kernel-level, bypasses IBus/X11)"""
        if not text:
            return False

        try:
            if not self._has_ydotool:
                return False

            time.sleep(TYPING_DELAY_SECONDS)

            subprocess.run(
                ["ydotool", "type", "--", text],
                check=True, timeout=10
            )

            print(f"[Papagaio] Typed (ydotool): {text[:50]}...")
            return True

        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def type_text_clipboard_paste(self, text):
        """Copy to clipboard and paste with Ctrl+V (most reliable on Linux)"""
        if not text:
            return False

        try:
            clipboard_tool = None
            if IS_LINUX and self._has_xclip:
                clipboard_tool = "xclip"
            elif IS_LINUX and self._has_wl_copy:
                clipboard_tool = "wl-copy"

            if not clipboard_tool:
                return False

            time.sleep(TYPING_DELAY_SECONDS)

            if clipboard_tool == "xclip":
                subprocess.run(
                    ["xclip", "-selection", "clipboard"],
                    input=text.encode(), check=True, timeout=5
                )
            else:
                subprocess.run(
                    ["wl-copy", text],
                    check=True, timeout=5
                )

            if self._has_xdotool:
                subprocess.run(
                    ["xdotool", "key", "ctrl+v"],
                    check=True, timeout=5
                )
            elif self._has_ydotool:
                subprocess.run(["ydotool", "key", "29:1", "47:1", "47:0", "29:0"], check=True, timeout=5)
            else:
                print("[Papagaio] Copied to clipboard, paste manually with Ctrl+V")
                return True

            print(f"[Papagaio] Typed (clipboard paste): {text[:50]}...")
            return True

        except (subprocess.SubprocessError, FileNotFoundError, OSError) as e:
            print(f"[Papagaio] Clipboard paste failed: {e}")
            return False

    def type_text_xdotool(self, text):
        """Type text using xdotool (X11 only)"""
        if not text:
            return False

        try:
            if not self._has_xdotool:
                return False

            time.sleep(TYPING_DELAY_SECONDS)

            cmd = ["xdotool", "type", "--delay", "2", "--", text]
            subprocess.run(cmd, check=True, timeout=30)

            print(f"[Papagaio] Typed (xdotool type): {text[:50]}...")
            return True

        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def type_text_clipboard(self, text):
        """Copy text to clipboard as fallback"""
        if not text:
            return False

        try:
            if IS_WINDOWS:
                subprocess.run("clip", input=text.encode('utf-16-le'), check=True, timeout=5)
            elif IS_MACOS:
                subprocess.run(["pbcopy"], input=text.encode(), check=True, timeout=5)
            else:
                subprocess.run(["xclip", "-selection", "clipboard"], input=text.encode(), check=True, timeout=5)
            print("[Papagaio] Copied to clipboard, paste with Ctrl+V")
            return True
        except (subprocess.SubprocessError, FileNotFoundError, OSError) as e:
            print(f"[Papagaio] Clipboard fallback failed: {e}")
            return False

    def _refocus_target_window(self):
        """Refocus the window that was active when hotkey was pressed"""
        if self._target_window_id and IS_LINUX and self._has_xdotool:
            try:
                subprocess.run(
                    ["xdotool", "windowactivate", self._target_window_id],
                    check=True, timeout=2
                )
                time.sleep(0.05)
                print(f"[Papagaio] Refocused window {self._target_window_id}")
            except Exception as e:
                print(f"[Papagaio] Window refocus failed: {e}")

    def _press_enter(self):
        """Press Enter key after typing"""
        if IS_LINUX and self._has_xdotool:
            subprocess.run(["xdotool", "key", "Return"], check=False, timeout=5)
        elif IS_LINUX and self.use_ydotool and self._has_ydotool:
            subprocess.run(["ydotool", "key", "28:1", "28:0"], check=False, timeout=5)
        else:
            kb = KeyboardController()
            kb.press(Key.enter)
            kb.release(Key.enter)

    def type_text(self, text):
        """Type text using available tool (cross-platform)"""
        self._typing_in_progress = True
        try:
            self._refocus_target_window()
            result = self._type_text_impl(text)
            if self.auto_enter:
                time.sleep(0.03)
                self._press_enter()
                print("[Papagaio] Auto-enter: pressed Enter", flush=True)
            return result
        finally:
            self._typing_in_progress = False
            self._hotkey_cooldown = time.monotonic()

    def _type_text_impl(self, text):
        if IS_WINDOWS or IS_MACOS:
            if not self.type_text_pynput(text):
                self.type_text_clipboard(text)
        elif self.use_ydotool:
            if not self.type_text_ydotool(text):
                if not self.type_text_clipboard_paste(text):
                    if not self.type_text_xdotool(text):
                        self.type_text_clipboard(text)
        else:
            if not self.type_text_xdotool(text):
                if not self.type_text_clipboard_paste(text):
                    if not self.type_text_pynput(text):
                        self.type_text_clipboard(text)

    def show_edit_dialog(self, text):
        """Show GTK dialog to edit text before sending"""
        if not HAS_GTK:
            return text

        result = [text]  # Use list to allow modification in nested function

        def create_dialog():
            dialog = Gtk.Dialog(
                title="Papagaio - Editar",
                flags=Gtk.DialogFlags.MODAL
            )
            dialog.set_default_size(500, 150)
            dialog.add_button("Cancelar", Gtk.ResponseType.CANCEL)
            dialog.add_button("Enviar", Gtk.ResponseType.OK)
            dialog.set_default_response(Gtk.ResponseType.OK)

            box = dialog.get_content_area()
            box.set_margin_start(10)
            box.set_margin_end(10)
            box.set_margin_top(10)
            box.set_margin_bottom(10)

            label = Gtk.Label(label="Edite o texto transcrito:")
            label.set_halign(Gtk.Align.START)
            box.pack_start(label, False, False, 5)

            # Text view with scroll
            scrolled = Gtk.ScrolledWindow()
            scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            scrolled.set_min_content_height(80)

            text_view = Gtk.TextView()
            text_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
            text_view.get_buffer().set_text(text)
            scrolled.add(text_view)
            box.pack_start(scrolled, True, True, 5)

            dialog.show_all()

            # Focus the text view and select all
            text_view.grab_focus()
            buffer = text_view.get_buffer()
            buffer.select_range(buffer.get_start_iter(), buffer.get_end_iter())

            response = dialog.run()

            if response == Gtk.ResponseType.OK:
                buffer = text_view.get_buffer()
                start, end = buffer.get_bounds()
                result[0] = buffer.get_text(start, end, False).strip()
            else:
                result[0] = None  # Cancelled

            dialog.destroy()

            # Process pending GTK events
            while Gtk.events_pending():
                Gtk.main_iteration()

        # Run on main thread
        GLib.idle_add(create_dialog)

        # Wait for dialog (simple approach)
        time.sleep(0.2)
        while Gtk.events_pending():
            Gtk.main_iteration()
            time.sleep(0.05)

        return result[0]

    def show_notification(self, title, message, urgency="normal"):
        """Show desktop notification (non-blocking, cross-platform)"""
        try:
            if IS_LINUX and self._has_notify_send:
                subprocess.Popen(
                    ["notify-send", "-u", urgency,
                     "-t", "3000",
                     "-h", "string:x-canonical-private-synchronous:papagaio",
                     title, message],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            elif HAS_PLYER:
                plyer_notification.notify(
                    title=title,
                    message=message,
                    app_name="Papagaio",
                    timeout=3
                )
            elif IS_MACOS:
                # macOS fallback: osascript
                script = f'display notification "{message}" with title "{title}"'
                subprocess.run(["osascript", "-e", script], check=False, timeout=5)
            # Windows without plyer: notifications silently skipped
        except Exception:
            # Notifications are non-critical, silently continue
            pass

    def start_esc_listener(self):
        if HAS_EVDEV:
            return
        def on_press(key):
            try:
                if key == keyboard.Key.esc and self.is_recording:
                    self.cancel_recording_flag = True
                    return False
            except AttributeError:
                pass

        self.esc_listener = keyboard.Listener(on_press=on_press)
        self.esc_listener.start()

    def stop_esc_listener(self):
        if HAS_EVDEV:
            return
        if self.esc_listener:
            self.esc_listener.stop()
            self.esc_listener = None

    def process_voice_input(self):
        """Process voice input in a separate thread"""
        if self.is_recording:
            return

        self.is_recording = True
        # Reset flags for new recording session
        self.stop_recording_flag = False
        self.cancel_recording_flag = False

        if IS_LINUX and self._has_xdotool:
            try:
                result = subprocess.run(
                    ["xdotool", "getactivewindow"],
                    capture_output=True, text=True, timeout=2
                )
                if result.returncode == 0 and result.stdout.strip():
                    self._target_window_id = result.stdout.strip()
                    print(f"[Papagaio] Saved target window: {self._target_window_id}")
            except Exception:
                self._target_window_id = None

        def record_and_transcribe():
            try:
                # Start ESC listener
                self.start_esc_listener()

                audio_data = self.record_audio()

                # Stop ESC listener
                self.stop_esc_listener()

                if audio_data is not None:
                    print("[Papagaio] 🔄 Transcribing...", flush=True)

                    text = self.transcribe(audio_data)

                    if text and len(text) > MIN_VALID_TRANSCRIPTION_LENGTH:
                        print(f"[Papagaio] {self.msg('transcribed')}: {text}", flush=True)

                        # Allow editing before sending if enabled
                        if self.edit_before_send and HAS_GTK:
                            print("[Papagaio] ✏️  Opening edit dialog...")
                            edited_text = self.show_edit_dialog(text)
                            if edited_text is None:
                                print(f"[Papagaio] {self.msg('cancelled')}")
                                self.show_notification("Papagaio", self.msg("cancelled"), "normal")
                                return
                            text = edited_text

                        self.type_text(text)
                        self.show_notification("Papagaio", f"✓ {text[:50]}", "normal")
                    else:
                        print(f"[Papagaio] {self.msg('no_speech')}")
                        self.show_notification("Papagaio", self.msg("no_speech"), "normal")
                else:
                    print(f"[Papagaio] {self.msg('no_audio')}")
                    self.show_notification("Papagaio", self.msg("no_speech"), "normal")

            except Exception as e:
                print(f"[Papagaio] ✗ Error: {e}")
                self.show_notification("Papagaio", f"✗ Error: {str(e)}", "critical")
            finally:
                self.stop_esc_listener()
                self.is_recording = False
                self.stop_recording_flag = False
                self.cancel_recording_flag = False

        self.recording_thread = threading.Thread(target=record_and_transcribe)
        self.recording_thread.start()

    def on_activate(self):
        """Called when hotkey is pressed"""
        if self.is_recording:
            # Hotkey pressed again while recording - stop manually
            print(f"[Papagaio] Hotkey pressed again - stopping recording...")
            self.stop_recording_flag = True
        else:
            # Start new recording
            print(f"[Papagaio] Hotkey triggered!")
            self.process_voice_input()

    def write_pid(self):
        """Write PID to file with exclusive lock to prevent multiple instances"""
        try:
            self.pid_file_handle = open(self.pid_file, 'w')
            if IS_WINDOWS:
                # Windows file locking using msvcrt
                msvcrt.locking(self.pid_file_handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                # Unix file locking using fcntl
                fcntl.flock(self.pid_file_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.pid_file_handle.write(str(os.getpid()))
            self.pid_file_handle.flush()
        except (BlockingIOError, OSError) as e:
            if isinstance(e, BlockingIOError) or (IS_WINDOWS and e.errno == 36):
                print(f"[Papagaio] Another instance is already running (PID file locked)")
            else:
                print(f"[Papagaio] Failed to create PID file: {e}")
            sys.exit(1)

    def remove_pid(self):
        """Remove PID file and release lock"""
        try:
            if hasattr(self, 'pid_file_handle') and self.pid_file_handle and not self.pid_file_handle.closed:
                if IS_WINDOWS:
                    try:
                        msvcrt.locking(self.pid_file_handle.fileno(), msvcrt.LK_UNLCK, 1)
                    except OSError:
                        pass
                else:
                    fcntl.flock(self.pid_file_handle.fileno(), fcntl.LOCK_UN)
                self.pid_file_handle.close()
            os.unlink(self.pid_file)
        except (OSError, ValueError):
            pass

    def start(self):
        """Start the daemon"""
        self.write_pid()

        # Detect which typing tool to use
        if IS_WINDOWS or IS_MACOS:
            tool_name = "pynput (native)"
        elif self.use_ydotool and self._has_ydotool:
            tool_name = "ydotool (Wayland/X11)"
        elif self._has_xdotool:
            self.use_ydotool = False
            tool_name = "xdotool (X11)"
        elif self._has_ydotool:
            self.use_ydotool = True
            tool_name = "ydotool (Wayland/X11)"
        else:
            tool_name = "pynput (fallback)"

        print("=" * 60)
        print(self.msg("started"))
        print("=" * 60)
        print(f"Hotkey: {self.hotkey}")
        print(f"Model: Whisper {self.model_size}")
        print(f"Interface: {self.lang}")
        print(f"Transcription: {self.transcription_language or 'auto'}")
        print(f"Typing tool: {tool_name}")
        edit_status = "✓ ON (GTK)" if self.edit_before_send and HAS_GTK else "OFF"
        print(f"Edit mode: {edit_status}")
        print(self.msg("mode"))
        print(self.msg("silence_threshold"))
        print(self.msg("max_duration"))
        print(self.msg("buffer"))
        print(f"PID: {os.getpid()}")
        print("=" * 60)
        print(f"\n{self.msg('press_hotkey')}")
        print(self.msg("speak_duration"))
        print(f"{self.msg('press_ctrl_c')}\n")

        # Initialize model on startup
        self.initialize_model()

        self.show_notification(
            "Papagaio (VAD)",
            f"✓ {self.msg('notification_ready').format(hotkey=self.hotkey)}",
            "normal"
        )

        try:
            listener_started = False
            if HAS_EVDEV:
                print("[Papagaio] Trying evdev for hotkey detection...", flush=True)
                if self._evdev_listener_loop() is not False:
                    listener_started = True
                else:
                    print("[Papagaio] evdev unavailable (no permission or no keyboards)", flush=True)
            if not listener_started and IS_LINUX:
                print("[Papagaio] Trying xbindkeys for hotkey detection...", flush=True)
                result = self._xbindkeys_listener_loop()
                if result is not False:
                    listener_started = True
                else:
                    print("[Papagaio] xbindkeys unavailable", flush=True)
            if not listener_started:
                print("[Papagaio] Using pynput for hotkey detection", flush=True)
                self._pynput_listener_loop()
        except KeyboardInterrupt:
            print("\n[Papagaio] Stopping...")
        finally:
            self._stop_listener = True
            self.remove_pid()
            self.show_notification("Papagaio", "Stopped", "low")


def load_config():
    """Load configuration from config file"""
    import configparser
    config_file = os.path.expanduser("~/.config/papagaio/config.ini")

    defaults = {
        'model': 'small',
        'language': 'en',
        'hotkey': '<super>+v',
        'secondary_hotkey': '',
        'auto_enter': False,
        'use_ydotool': False,
        'cache_dir': os.path.expanduser("~/.cache/whisper-models"),
        'silence_threshold': 200,  # Lower for better detection
        'silence_duration': 2.0,   # 2 seconds silence to stop
        'transcription_language': 'auto',
        'edit_before_send': False
    }

    if os.path.exists(config_file):
        config = configparser.ConfigParser()
        config.read(config_file)

        if 'General' in config:
            defaults['model'] = config['General'].get('model', defaults['model'])
            defaults['language'] = config['General'].get('language', defaults['language'])
            defaults['hotkey'] = config['General'].get('hotkey', defaults['hotkey'])
            defaults['secondary_hotkey'] = config['General'].get('secondary_hotkey', defaults['secondary_hotkey'])
            defaults['cache_dir'] = config['General'].get('cache_dir', defaults['cache_dir'])
            defaults['edit_before_send'] = config['General'].get('edit_before_send', 'false').lower() == 'true'
            defaults['auto_enter'] = config['General'].get('auto_enter', 'false').lower() == 'true'

        if 'Audio' in config:
            defaults['silence_threshold'] = int(config['Audio'].get('silence_threshold', '200'))
            defaults['silence_duration'] = float(config['Audio'].get('silence_duration', '2.0'))
            defaults['transcription_language'] = config['Audio'].get('transcription_language', 'auto')

        if 'Advanced' in config:
            defaults['use_ydotool'] = config['Advanced'].get('use_ydotool', 'false').lower() == 'true'

    return defaults


def main():
    import argparse

    # License check disabled for development

    # Load config file defaults
    config = load_config()

    parser = argparse.ArgumentParser(description="Voice Input Daemon (cross-platform)")
    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "-m", "--model",
        default=config['model'],
        choices=["tiny", "base", "small", "medium"],
        help="Whisper model size (default: from config or small)"
    )
    parser.add_argument(
        "-k", "--hotkey",
        default=config['hotkey'],
        help="Global hotkey (default: from config or Ctrl+Shift+Alt+V)"
    )
    parser.add_argument(
        "--ydotool",
        action="store_true",
        default=config['use_ydotool'],
        help="Force use of ydotool instead of xdotool"
    )
    parser.add_argument(
        "-l", "--lang",
        default=config['language'],
        choices=["en", "pt"],
        help="Interface language (default: from config or en)"
    )
    parser.add_argument(
        "-t", "--transcription-language",
        default=config['transcription_language'],
        help="Transcription language: auto, en, pt, es, fr, de, etc. (default: auto)"
    )
    parser.add_argument(
        "-e", "--edit",
        action="store_true",
        default=config['edit_before_send'],
        help="Show edit dialog before sending text (requires GTK)"
    )

    args = parser.parse_args()

    daemon = VoiceDaemon(
        model_size=args.model,
        hotkey=args.hotkey,
        secondary_hotkey=config.get('secondary_hotkey', ''),
        auto_enter=config.get('auto_enter', False),
        use_ydotool=args.ydotool,
        model_cache_dir=config['cache_dir'],
        lang=args.lang,
        silence_threshold=config['silence_threshold'],
        silence_duration=config['silence_duration'],
        transcription_language=args.transcription_language,
        edit_before_send=args.edit
    )

    # Handle signals
    def signal_handler(sig, frame):
        daemon.remove_pid()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    daemon.start()


if __name__ == "__main__":
    main()
