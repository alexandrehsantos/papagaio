#!/usr/bin/env python3
"""
Papagaio Settings - Graphical Configuration Tool
"""

import tkinter as tk
from tkinter import ttk, messagebox
import configparser
import os
import subprocess

CONFIG_DIR = os.path.expanduser("~/.config/papagaio")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.ini")

MODELS = [
    ("tiny", "Tiny - 75MB (Fast, Low Accuracy)"),
    ("base", "Base - 140MB (Fast, Medium Accuracy)"),
    ("small", "Small - 460MB (Balanced, Recommended)"),
    ("medium", "Medium - 1.5GB (Slow, Best Accuracy)")
]

LANGUAGES = [
    ("en", "English"),
    ("pt", "Portuguese")
]

HOTKEY_PRESETS = [
    "<ctrl>+<shift>+<alt>+v",
    "<ctrl>+<alt>+v",
    "<ctrl>+<shift>+v",
    "<super>+v"
]


class PapagaioSettings:
    def __init__(self, root):
        self.root = root
        self.root.title("Papagaio Settings")
        self.root.geometry("500x450")
        self.root.resizable(False, False)

        self.config = configparser.ConfigParser()
        self.load_config()

        self.create_widgets()

    def load_config(self):
        """Load configuration from file or create defaults"""
        if os.path.exists(CONFIG_FILE):
            self.config.read(CONFIG_FILE)

        if 'General' not in self.config:
            self.config['General'] = {}
        if 'Audio' not in self.config:
            self.config['Audio'] = {}
        if 'Advanced' not in self.config:
            self.config['Advanced'] = {}

        defaults = {
            'General': {
                'model': 'small',
                'language': 'en',
                'hotkey': '<ctrl>+<shift>+<alt>+v',
                'cache_dir': '~/.cache/whisper-models'
            },
            'Audio': {
                'silence_threshold': '400',
                'silence_duration': '3600.0',
                'max_recording_time': '3600'
            },
            'Advanced': {
                'use_ydotool': 'false',
                'typing_delay': '0.3'
            }
        }

        for section, values in defaults.items():
            for key, value in values.items():
                if key not in self.config[section]:
                    self.config[section][key] = value

    def create_widgets(self):
        """Create the GUI widgets"""
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # General Tab
        general_frame = ttk.Frame(notebook, padding=20)
        notebook.add(general_frame, text="General")

        # Model
        ttk.Label(general_frame, text="Whisper Model:", font=('', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=(0, 5))
        self.model_var = tk.StringVar(value=self.config['General']['model'])
        for i, (value, text) in enumerate(MODELS):
            ttk.Radiobutton(general_frame, text=text, variable=self.model_var, value=value).grid(row=i+1, column=0, sticky='w', padx=(20, 0))

        # Language
        ttk.Label(general_frame, text="Interface Language:", font=('', 10, 'bold')).grid(row=6, column=0, sticky='w', pady=(20, 5))
        self.lang_var = tk.StringVar(value=self.config['General']['language'])
        lang_frame = ttk.Frame(general_frame)
        lang_frame.grid(row=7, column=0, sticky='w', padx=(20, 0))
        for value, text in LANGUAGES:
            ttk.Radiobutton(lang_frame, text=text, variable=self.lang_var, value=value).pack(side='left', padx=(0, 20))

        # Hotkey
        ttk.Label(general_frame, text="Hotkey:", font=('', 10, 'bold')).grid(row=8, column=0, sticky='w', pady=(20, 5))
        self.hotkey_var = tk.StringVar(value=self.config['General']['hotkey'])
        hotkey_combo = ttk.Combobox(general_frame, textvariable=self.hotkey_var, values=HOTKEY_PRESETS, width=30)
        hotkey_combo.grid(row=9, column=0, sticky='w', padx=(20, 0))
        ttk.Label(general_frame, text="Format: <ctrl>+<shift>+<alt>+key", foreground='gray').grid(row=10, column=0, sticky='w', padx=(20, 0))

        # Audio Tab
        audio_frame = ttk.Frame(notebook, padding=20)
        notebook.add(audio_frame, text="Audio")

        # Silence Threshold
        ttk.Label(audio_frame, text="Silence Threshold (RMS):", font=('', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=(0, 5))
        self.threshold_var = tk.StringVar(value=self.config['Audio']['silence_threshold'])
        threshold_spin = ttk.Spinbox(audio_frame, from_=100, to=1000, textvariable=self.threshold_var, width=10)
        threshold_spin.grid(row=1, column=0, sticky='w', padx=(20, 0))
        ttk.Label(audio_frame, text="Lower = more sensitive (default: 400)", foreground='gray').grid(row=2, column=0, sticky='w', padx=(20, 0))

        # Silence Duration
        ttk.Label(audio_frame, text="Silence Duration (seconds):", font=('', 10, 'bold')).grid(row=3, column=0, sticky='w', pady=(20, 5))
        self.duration_var = tk.StringVar(value=self.config['Audio']['silence_duration'])
        duration_spin = ttk.Spinbox(audio_frame, from_=5.0, to=3600.0, increment=60, textvariable=self.duration_var, width=10)
        duration_spin.grid(row=4, column=0, sticky='w', padx=(20, 0))
        ttk.Label(audio_frame, text="Wait time before auto-stop (default: 3600 = 60 min)", foreground='gray').grid(row=5, column=0, sticky='w', padx=(20, 0))

        # Max Recording Time
        ttk.Label(audio_frame, text="Max Recording Time (seconds):", font=('', 10, 'bold')).grid(row=6, column=0, sticky='w', pady=(20, 5))
        self.max_time_var = tk.StringVar(value=self.config['Audio']['max_recording_time'])
        max_time_spin = ttk.Spinbox(audio_frame, from_=60, to=7200, increment=60, textvariable=self.max_time_var, width=10)
        max_time_spin.grid(row=7, column=0, sticky='w', padx=(20, 0))
        ttk.Label(audio_frame, text="Maximum recording length (default: 3600 = 1 hour)", foreground='gray').grid(row=8, column=0, sticky='w', padx=(20, 0))

        # Advanced Tab
        advanced_frame = ttk.Frame(notebook, padding=20)
        notebook.add(advanced_frame, text="Advanced")

        # Use ydotool
        ttk.Label(advanced_frame, text="Keyboard Backend:", font=('', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=(0, 5))
        self.ydotool_var = tk.BooleanVar(value=self.config['Advanced']['use_ydotool'].lower() == 'true')
        ttk.Checkbutton(advanced_frame, text="Force ydotool (for Wayland)", variable=self.ydotool_var).grid(row=1, column=0, sticky='w', padx=(20, 0))
        ttk.Label(advanced_frame, text="Leave unchecked for auto-detect", foreground='gray').grid(row=2, column=0, sticky='w', padx=(20, 0))

        # Typing Delay
        ttk.Label(advanced_frame, text="Typing Delay (seconds):", font=('', 10, 'bold')).grid(row=3, column=0, sticky='w', pady=(20, 5))
        self.delay_var = tk.StringVar(value=self.config['Advanced']['typing_delay'])
        delay_spin = ttk.Spinbox(advanced_frame, from_=0.0, to=2.0, increment=0.1, textvariable=self.delay_var, width=10)
        delay_spin.grid(row=4, column=0, sticky='w', padx=(20, 0))
        ttk.Label(advanced_frame, text="Delay before typing (default: 0.3)", foreground='gray').grid(row=5, column=0, sticky='w', padx=(20, 0))

        # Buttons
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill='x', padx=10, pady=(0, 10))

        ttk.Button(button_frame, text="Save", command=self.save_config).pack(side='right', padx=(5, 0))
        ttk.Button(button_frame, text="Save & Restart", command=self.save_and_restart).pack(side='right', padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self.root.quit).pack(side='right')

        # Status
        self.status_var = tk.StringVar(value="")
        ttk.Label(button_frame, textvariable=self.status_var, foreground='green').pack(side='left')

    def save_config(self):
        """Save configuration to file"""
        os.makedirs(CONFIG_DIR, exist_ok=True)

        self.config['General']['model'] = self.model_var.get()
        self.config['General']['language'] = self.lang_var.get()
        self.config['General']['hotkey'] = self.hotkey_var.get()

        self.config['Audio']['silence_threshold'] = self.threshold_var.get()
        self.config['Audio']['silence_duration'] = self.duration_var.get()
        self.config['Audio']['max_recording_time'] = self.max_time_var.get()

        self.config['Advanced']['use_ydotool'] = str(self.ydotool_var.get()).lower()
        self.config['Advanced']['typing_delay'] = self.delay_var.get()

        with open(CONFIG_FILE, 'w') as f:
            self.config.write(f)

        self.status_var.set("Saved!")
        self.root.after(2000, lambda: self.status_var.set(""))

    def save_and_restart(self):
        """Save configuration and restart the daemon"""
        self.save_config()

        try:
            subprocess.run(["systemctl", "--user", "restart", "papagaio"], check=True)
            messagebox.showinfo("Success", "Configuration saved and daemon restarted!")
        except subprocess.CalledProcessError:
            messagebox.showwarning("Warning", "Configuration saved but failed to restart daemon.\n\nRun: papagaio-ctl restart")
        except FileNotFoundError:
            messagebox.showwarning("Warning", "Configuration saved but systemctl not found.\n\nRun: papagaio-ctl restart")


def main():
    root = tk.Tk()
    app = PapagaioSettings(root)
    root.mainloop()


if __name__ == "__main__":
    main()
