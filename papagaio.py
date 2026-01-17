#!/usr/bin/env python3

import subprocess
import sys
import tempfile
import os
import signal
import threading
import time
import wave
import struct
import math
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
    from pynput.keyboard import Controller as KeyboardController, Key
    import pyaudio
except ImportError as e:
    print(f"Missing required dependency: {e.name}")
    print("Please install dependencies: pip install faster-whisper pynput pyaudio")
    sys.exit(1)

# Optional: cross-platform notifications
try:
    from plyer import notification as plyer_notification
    HAS_PLYER = True
except ImportError:
    HAS_PLYER = False


# Audio configuration constants
CHUNK_SIZE = 8192
AUDIO_FORMAT = pyaudio.paInt16
CHANNELS = 1
SAMPLE_RATE = 16000
SILENCE_THRESHOLD_RMS = 400
SILENCE_DURATION_SECONDS = 5.0
MAX_RECORDING_DURATION_SECONDS = 3600
MIN_VALID_TRANSCRIPTION_LENGTH = 3
TYPING_DELAY_SECONDS = 0.3
MIN_RECORDING_DURATION_SECONDS = 0.5

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
    def __init__(self, model_size="small", hotkey="<ctrl>+<shift>+<alt>+v", use_ydotool=False, model_cache_dir=None, lang="en"):
        self.model_size = model_size
        self.hotkey = hotkey
        self.use_ydotool = use_ydotool
        self.model_cache_dir = model_cache_dir or os.path.expanduser("~/.cache/whisper-models")
        self.lang = lang if lang in MESSAGES else "en"
        self.model = None
        self.is_recording = False
        self.stop_recording_flag = False  # For manual stop (hotkey pressed again)
        self.cancel_recording_flag = False  # For ESC key
        self.recording_thread = None
        self.esc_listener = None
        self.pid_file = os.path.join(tempfile.gettempdir(), "papagaio.pid")

        # Audio settings for VAD
        self.CHUNK = CHUNK_SIZE
        self.FORMAT = AUDIO_FORMAT
        self.CHANNELS = CHANNELS
        self.RATE = SAMPLE_RATE
        self.SILENCE_THRESHOLD = SILENCE_THRESHOLD_RMS
        self.SILENCE_DURATION = SILENCE_DURATION_SECONDS
        self.MAX_RECORDING_TIME = MAX_RECORDING_DURATION_SECONDS

    def msg(self, key):
        """Get translated message"""
        return MESSAGES[self.lang].get(key, MESSAGES["en"].get(key, key))

    def initialize_model(self):
        if self.model is None:
            # Create cache directory if it doesn't exist
            os.makedirs(self.model_cache_dir, exist_ok=True)

            print(f"[Papagaio] Loading Whisper {self.model_size} model...")
            print(f"[Papagaio] Cache dir: {self.model_cache_dir}")

            self.model = WhisperModel(
                self.model_size,
                device="cpu",
                compute_type="int8",
                num_workers=4,
                download_root=self.model_cache_dir
            )
            print(f"[Papagaio] ✓ Model loaded!")

    def get_rms(self, data):
        """Calculate RMS (volume) of audio chunk"""
        count = len(data) / 2
        format = "%dh" % (count)
        shorts = struct.unpack(format, data)
        sum_squares = sum([sample ** 2 for sample in shorts])
        rms = math.sqrt(sum_squares / count)
        return rms

    def record_audio(self):
        """Record audio until silence is detected"""
        audio = pyaudio.PyAudio()

        try:
            # Get sample width early before stream closes
            sample_width = audio.get_sample_size(self.FORMAT)

            stream = audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )

            print(f"[Papagaio] {self.msg('speak_now')}")
            print(f"[Papagaio] {self.msg('press_hotkey_manual')}")
            self.show_notification("Voice Input", self.msg("speak_now") + "\n" + self.msg("press_again_to_stop").format(hotkey=self.hotkey), "low")

            frames = []
            silence_chunks = 0
            max_silence_chunks = int(self.SILENCE_DURATION * self.RATE / self.CHUNK)
            started_speaking = False
            min_recording_chunks = int(MIN_RECORDING_DURATION_SECONDS * self.RATE / self.CHUNK)

            try:
                while True:
                    # Check for manual stop or cancel flags
                    if self.cancel_recording_flag:
                        print(f"\n[Papagaio] {self.msg('cancelled')}")
                        self.show_notification("Voice Input", self.msg("cancelled"), "normal")
                        return None

                    if self.stop_recording_flag:
                        print(f"\n[Papagaio] {self.msg('manually_stopped')}")
                        break

                    data = stream.read(self.CHUNK, exception_on_overflow=False)
                    frames.append(data)

                    rms = self.get_rms(data)

                    if rms > self.SILENCE_THRESHOLD:
                        started_speaking = True
                        silence_chunks = 0
                        print(".", end="", flush=True)
                    else:
                        if started_speaking:
                            silence_chunks += 1

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

        # Use secure temporary file creation
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            output_file = temp_file.name

        with wave.open(output_file, 'wb') as wf:
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(sample_width)
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(frames))

        duration = len(frames) * self.CHUNK / self.RATE
        print(f"[Papagaio] {self.msg('recorded')}: {duration:.1f}s")

        return output_file

    def transcribe(self, audio_file):
        """Transcribe audio file to text"""
        self.initialize_model()

        segments, info = self.model.transcribe(
            audio_file,
            beam_size=5,
            vad_filter=True,
            vad_parameters={
                "threshold": 0.3,  # Lower threshold - more sensitive
                "min_speech_duration_ms": 200,  # Minimum 200ms of speech
                "min_silence_duration_ms": 500,  # 500ms silence = end of speech
                "speech_pad_ms": 400  # Add padding around speech
            }
        )

        text = " ".join([segment.text.strip() for segment in segments])
        return text.strip()

    def type_text_pynput(self, text):
        """Type text using pynput (cross-platform)"""
        if not text:
            return False

        try:
            time.sleep(TYPING_DELAY_SECONDS)
            kb = KeyboardController()
            kb.type(text)
            kb.press(Key.enter)
            kb.release(Key.enter)
            print(f"[Papagaio] ✓ Typed (pynput): {text[:50]}...")
            return True
        except Exception as e:
            print(f"[Papagaio] pynput typing failed: {e}")
            return False

    def type_text_ydotool(self, text):
        """Type text using ydotool (works with Wayland and X11)"""
        if not text:
            return False

        try:
            # Check if ydotool is available
            if not shutil.which("ydotool"):
                return False

            time.sleep(TYPING_DELAY_SECONDS)

            subprocess.run(
                ["ydotool", "type", text],
                check=True
            )

            subprocess.run(["ydotool", "key", "28:1", "28:0"], check=True)

            print(f"[Papagaio] ✓ Typed (ydotool): {text[:50]}...")
            return True

        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def type_text_xdotool(self, text):
        """Type text using xdotool (X11 only)"""
        if not text:
            return False

        try:
            if not shutil.which("xdotool"):
                return False

            time.sleep(TYPING_DELAY_SECONDS)

            subprocess.run(
                ["xdotool", "type", "--delay", "10", "--", text],
                check=True
            )

            subprocess.run(["xdotool", "key", "Return"], check=True)

            print(f"[Papagaio] ✓ Typed (xdotool): {text[:50]}...")
            return True

        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def type_text_clipboard(self, text):
        """Copy text to clipboard as fallback"""
        if not text:
            return False

        try:
            if IS_WINDOWS:
                # Windows: use clip command
                subprocess.run("clip", input=text.encode('utf-16-le'), check=True, timeout=5)
            elif IS_MACOS:
                # macOS: use pbcopy
                subprocess.run(["pbcopy"], input=text.encode(), check=True, timeout=5)
            else:
                # Linux: use xclip
                subprocess.run(["xclip", "-selection", "clipboard"], input=text.encode(), check=True, timeout=5)
            print("[Papagaio] ✓ Copied to clipboard as fallback")
            return True
        except (subprocess.SubprocessError, FileNotFoundError, OSError) as e:
            print(f"[Papagaio] Clipboard fallback failed: {e}")
            return False

    def type_text(self, text):
        """Type text using available tool (cross-platform)"""
        if IS_WINDOWS or IS_MACOS:
            # On Windows and macOS, use pynput directly
            if not self.type_text_pynput(text):
                self.type_text_clipboard(text)
        else:
            # On Linux, try xdotool first (more reliable with special chars)
            if not self.type_text_xdotool(text):
                print("[Papagaio] ⚠️  xdotool failed, trying ydotool")
                if not self.type_text_ydotool(text):
                    print("[Papagaio] ⚠️  ydotool failed, trying pynput")
                    if not self.type_text_pynput(text):
                        self.type_text_clipboard(text)

    def show_notification(self, title, message, urgency="normal"):
        """Show desktop notification (cross-platform)"""
        try:
            if HAS_PLYER:
                # Use plyer for cross-platform notifications
                plyer_notification.notify(
                    title=title,
                    message=message,
                    app_name="Papagaio",
                    timeout=5
                )
            elif IS_LINUX:
                # Linux fallback: notify-send
                subprocess.run(
                    ["notify-send", "-u", urgency, title, message],
                    check=False,
                    timeout=5
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
        """Start ESC key listener for cancelling recording"""
        def on_press(key):
            try:
                if key == keyboard.Key.esc and self.is_recording:
                    self.cancel_recording_flag = True
                    return False  # Stop listener
            except AttributeError:
                pass

        self.esc_listener = keyboard.Listener(on_press=on_press)
        self.esc_listener.start()

    def stop_esc_listener(self):
        """Stop ESC key listener"""
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

        def record_and_transcribe():
            try:
                # Start ESC listener
                self.start_esc_listener()

                audio_file = self.record_audio()

                # Stop ESC listener
                self.stop_esc_listener()

                if audio_file:
                    print("[Papagaio] 🔄 Transcribing...")
                    self.show_notification("Voice Input", "🔄 Transcribing...", "low")

                    text = self.transcribe(audio_file)
                    os.unlink(audio_file)

                    if text and len(text) > MIN_VALID_TRANSCRIPTION_LENGTH:
                        print(f"[Papagaio] {self.msg('transcribed')}: {text}")
                        self.type_text(text)
                        self.show_notification("Voice Input", f"✓ {text[:50]}", "normal")
                    else:
                        print(f"[Papagaio] {self.msg('no_speech')}")
                        self.show_notification("Voice Input", self.msg("no_speech"), "normal")
                else:
                    print(f"[Papagaio] {self.msg('no_audio')}")
                    self.show_notification("Voice Input", self.msg("no_speech"), "normal")

            except Exception as e:
                print(f"[Papagaio] ✗ Error: {e}")
                self.show_notification("Voice Input", f"✗ Error: {str(e)}", "critical")
            finally:
                self.stop_esc_listener()
                self.is_recording = False
                # Reset flags
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
            if hasattr(self, 'pid_file_handle') and self.pid_file_handle:
                if IS_WINDOWS:
                    try:
                        msvcrt.locking(self.pid_file_handle.fileno(), msvcrt.LK_UNLCK, 1)
                    except OSError:
                        pass
                else:
                    fcntl.flock(self.pid_file_handle.fileno(), fcntl.LOCK_UN)
                self.pid_file_handle.close()
            os.unlink(self.pid_file)
        except OSError:
            # PID file may not exist, continue
            pass

    def start(self):
        """Start the daemon"""
        self.write_pid()

        # Detect which typing tool to use
        if IS_WINDOWS or IS_MACOS:
            tool_name = "pynput (native)"
        elif shutil.which("ydotool"):
            self.use_ydotool = True
            tool_name = "ydotool (Wayland/X11)"
        elif shutil.which("xdotool"):
            tool_name = "xdotool (X11)"
        else:
            tool_name = "pynput (fallback)"

        print("=" * 60)
        print(self.msg("started"))
        print("=" * 60)
        print(f"Hotkey: {self.hotkey}")
        print(f"Model: Whisper {self.model_size}")
        print(f"Language: {self.lang}")
        print(f"Typing tool: {tool_name}")
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

        # Set up hotkey listener
        try:
            with keyboard.GlobalHotKeys({
                self.hotkey: self.on_activate
            }) as listener:
                listener.join()
        except KeyboardInterrupt:
            print("\n[Papagaio] Stopping...")
        finally:
            self.remove_pid()
            self.show_notification("Papagaio", "Stopped", "low")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Voice Input Daemon (cross-platform)")
    parser.add_argument(
        "-m", "--model",
        default="small",
        choices=["tiny", "base", "small", "medium"],
        help="Whisper model size (default: small for better accuracy)"
    )
    parser.add_argument(
        "-k", "--hotkey",
        default="<ctrl>+<shift>+<alt>+v",
        help="Global hotkey (default: Ctrl+Shift+Alt+V)"
    )
    parser.add_argument(
        "--ydotool",
        action="store_true",
        help="Force use of ydotool instead of xdotool"
    )
    parser.add_argument(
        "-l", "--lang",
        default="en",
        choices=["en", "pt"],
        help="Interface language (default: en - English, pt - Portuguese)"
    )

    args = parser.parse_args()

    daemon = VoiceDaemon(model_size=args.model, hotkey=args.hotkey, use_ydotool=args.ydotool, lang=args.lang)

    # Handle signals
    def signal_handler(sig, frame):
        daemon.remove_pid()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    daemon.start()


if __name__ == "__main__":
    main()
