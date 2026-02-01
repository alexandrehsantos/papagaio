#!/usr/bin/env python3
"""Papagaio - Configurações"""

import tkinter as tk
from tkinter import messagebox
import configparser
import os
import subprocess
import locale

try:
    import customtkinter as ctk
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    USE_CTK = True
except ImportError:
    USE_CTK = False

CONFIG_DIR = os.path.expanduser("~/.config/papagaio")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.ini")


def detect_language():
    try:
        lang = locale.getdefaultlocale()[0]
        if lang:
            return lang.split('_')[0].lower()
    except:
        pass
    return 'pt'


class App:
    def __init__(self):
        if USE_CTK:
            self.root = ctk.CTk()
        else:
            self.root = tk.Tk()

        self.root.title("Papagaio - Configurações")
        self.root.geometry("500x650")
        self.root.resizable(False, False)

        # Centralizar
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 500) // 2
        y = (self.root.winfo_screenheight() - 650) // 2
        self.root.geometry(f"+{x}+{y}")

        self.load_config()
        self.build_ui()

    def load_config(self):
        self.model = 'small'
        self.language = detect_language()
        self.hotkey_display = 'Ctrl + Shift + Alt + V'
        self.hotkey_internal = '<ctrl>+<shift>+<alt>+v'

        if os.path.exists(CONFIG_FILE):
            try:
                cfg = configparser.ConfigParser()
                cfg.read(CONFIG_FILE)
                if 'General' in cfg:
                    self.model = cfg['General'].get('model', 'small')
                    self.language = cfg['General'].get('language', self.language)
                    hk = cfg['General'].get('hotkey', self.hotkey_internal)
                    self.hotkey_internal = hk
                    self.hotkey_display = hk.replace('<ctrl>', 'Ctrl').replace('<alt>', 'Alt').replace('<shift>', 'Shift').replace('<cmd>', 'Win').replace('+', ' + ')
            except:
                pass

    def build_ui(self):
        if not USE_CTK:
            self.build_tk_ui()
            return

        # Container principal
        main = ctk.CTkFrame(self.root, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=30, pady=25)

        # === TÍTULO ===
        ctk.CTkLabel(main, text="🎙️ Papagaio", font=("", 28, "bold")).pack(anchor="w")
        ctk.CTkLabel(main, text="Transforme sua voz em texto em qualquer programa!",
                    font=("", 14), text_color="gray").pack(anchor="w", pady=(5,20))

        # === ATALHO ===
        box1 = ctk.CTkFrame(main, corner_radius=10)
        box1.pack(fill="x", pady=(0,15))

        inner1 = ctk.CTkFrame(box1, fg_color="transparent")
        inner1.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(inner1, text="🎹 Atalho do teclado", font=("", 14, "bold")).pack(anchor="w")
        ctk.CTkLabel(inner1, text="Pressione estas teclas para começar a ditar:",
                    font=("", 12), text_color="gray").pack(anchor="w", pady=(3,0))

        row1 = ctk.CTkFrame(inner1, fg_color="transparent")
        row1.pack(fill="x", pady=(10,0))

        self.hotkey_var = tk.StringVar(value=self.hotkey_display)
        ctk.CTkLabel(row1, textvariable=self.hotkey_var, font=("", 20, "bold"),
                    text_color="#3b8ed0").pack(side="left")
        ctk.CTkButton(row1, text="Mudar", width=80, height=32,
                     command=self.change_hotkey).pack(side="right")

        # === QUALIDADE ===
        box2 = ctk.CTkFrame(main, corner_radius=10)
        box2.pack(fill="x", pady=(0,15))

        inner2 = ctk.CTkFrame(box2, fg_color="transparent")
        inner2.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(inner2, text="⚙️ Qualidade da transcrição", font=("", 14, "bold")).pack(anchor="w")

        self.quality_var = tk.StringVar(value=self.model)

        options = [
            ("tiny", "⚡ Rápido", "Bom para frases curtas e comandos"),
            ("small", "⭐ Recomendado", "Ideal para uso no dia a dia"),
            ("medium", "🎯 Alta precisão", "Melhor para textos longos"),
        ]

        for val, label, desc in options:
            row = ctk.CTkFrame(inner2, fg_color="transparent")
            row.pack(fill="x", pady=5)
            ctk.CTkRadioButton(row, text=f"{label}", variable=self.quality_var,
                              value=val, font=("", 14, "bold")).pack(side="left")
            ctk.CTkLabel(row, text=f"  →  {desc}", font=("", 12),
                        text_color="gray").pack(side="left")

        # === COMO USAR ===
        box3 = ctk.CTkFrame(main, corner_radius=10)
        box3.pack(fill="x", pady=(0,15))

        inner3 = ctk.CTkFrame(box3, fg_color="transparent")
        inner3.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(inner3, text="📖 Como usar o Papagaio", font=("", 14, "bold")).pack(anchor="w")

        steps = [
            "1️⃣  Abra qualquer programa (Word, email, navegador)",
            "2️⃣  Clique onde você quer que o texto apareça",
            "3️⃣  Pressione o atalho do teclado e comece a falar",
            "4️⃣  Quando parar de falar, o texto aparece automaticamente!"
        ]
        for step in steps:
            ctk.CTkLabel(inner3, text=step, font=("", 13),
                        text_color="#cccccc").pack(anchor="w", pady=2)

        # === BOTÕES ===
        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(15,0))

        ctk.CTkButton(btn_frame, text="Cancelar", width=120, height=45,
                     fg_color="#555", hover_color="#666", font=("", 14),
                     command=self.root.destroy).pack(side="left")

        ctk.CTkButton(btn_frame, text="✓ Salvar", width=150, height=45,
                     font=("", 16, "bold"), command=self.save).pack(side="right")

    def build_tk_ui(self):
        tk.Label(self.root, text="Papagaio", font=("", 20, "bold")).pack(pady=20)
        tk.Label(self.root, text="Instale customtkinter para melhor interface:").pack()
        tk.Label(self.root, text="pip install customtkinter", fg="blue").pack(pady=10)

        self.hotkey_var = tk.StringVar(value=self.hotkey_display)
        tk.Label(self.root, text="Atalho atual:", font=("", 12)).pack(pady=(20,5))
        tk.Label(self.root, textvariable=self.hotkey_var, font=("", 16, "bold")).pack()
        tk.Button(self.root, text="Mudar Atalho", command=self.change_hotkey).pack(pady=10)

        tk.Label(self.root, text="Qualidade:", font=("", 12)).pack(pady=(20,5))
        self.quality_var = tk.StringVar(value=self.model)
        for val, label in [("tiny", "Rápido"), ("small", "Recomendado"), ("medium", "Alta precisão")]:
            tk.Radiobutton(self.root, text=label, variable=self.quality_var, value=val, font=("", 12)).pack()

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=30)
        tk.Button(btn_frame, text="Cancelar", font=("", 12), command=self.root.destroy).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Salvar", font=("", 14, "bold"), command=self.save).pack(side="left", padx=10)

    def change_hotkey(self):
        dialog = HotkeyDialog(self.root)
        self.root.wait_window(dialog)
        if dialog.result:
            self.hotkey_display = dialog.result[0]
            self.hotkey_internal = dialog.result[1]
            self.hotkey_var.set(self.hotkey_display)

    def save(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)

        cfg = configparser.ConfigParser()
        cfg['General'] = {
            'model': self.quality_var.get(),
            'language': self.language,
            'hotkey': self.hotkey_internal
        }
        cfg['Audio'] = {'silence_threshold': '400', 'silence_duration': '5.0'}

        with open(CONFIG_FILE, 'w') as f:
            cfg.write(f)

        try:
            subprocess.run(["systemctl", "--user", "restart", "papagaio"], capture_output=True, timeout=5)
        except:
            pass

        messagebox.showinfo("Papagaio",
            f"✓ Configurações salvas!\n\n"
            f"Seu atalho: {self.hotkey_var.get()}\n\n"
            f"Agora você pode usar o atalho para ditar em qualquer programa!")
        self.root.destroy()

    def run(self):
        self.root.mainloop()


class HotkeyDialog(ctk.CTkToplevel if USE_CTK else tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.result = None
        self.keys = set()
        self.combo = ""

        self.title("Escolher Atalho")
        self.geometry("400x200")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - 400) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - 200) // 2
        self.geometry(f"+{x}+{y}")

        if USE_CTK:
            ctk.CTkLabel(self, text="Pressione as teclas juntas",
                        font=("", 16, "bold")).pack(pady=(25,5))
            ctk.CTkLabel(self, text="Exemplo: Ctrl + Shift + V",
                        font=("", 13), text_color="gray").pack()
            self.lbl = ctk.CTkLabel(self, text="aguardando...",
                        font=("", 24, "bold"), text_color="#3b8ed0")
            self.lbl.pack(pady=20)

            btn_row = ctk.CTkFrame(self, fg_color="transparent")
            btn_row.pack()
            ctk.CTkButton(btn_row, text="Cancelar", width=100, height=36,
                         fg_color="#555", command=self.destroy).pack(side="left", padx=5)
            ctk.CTkButton(btn_row, text="Usar este", width=100, height=36,
                         command=self.ok).pack(side="left", padx=5)
        else:
            tk.Label(self, text="Pressione as teclas", font=("", 14)).pack(pady=20)
            self.lbl = tk.Label(self, text="aguardando...", font=("", 18, "bold"))
            self.lbl.pack(pady=15)
            btn_row = tk.Frame(self)
            btn_row.pack(pady=10)
            tk.Button(btn_row, text="Cancelar", font=("", 12), command=self.destroy).pack(side="left", padx=5)
            tk.Button(btn_row, text="OK", font=("", 12), command=self.ok).pack(side="left", padx=5)

        self.bind("<KeyPress>", self.on_press)
        self.bind("<KeyRelease>", self.on_release)
        self.after(100, self.focus_force)

    def on_press(self, e):
        names = {"Control_L": "Ctrl", "Control_R": "Ctrl", "Alt_L": "Alt", "Alt_R": "Alt",
                 "Shift_L": "Shift", "Shift_R": "Shift", "Super_L": "Win", "Super_R": "Win"}
        name = names.get(e.keysym, e.keysym.upper() if len(e.keysym) == 1 else e.keysym)
        self.keys.add(name)

        order = {"Ctrl": 0, "Alt": 1, "Shift": 2, "Win": 3}
        self.combo = " + ".join(sorted(self.keys, key=lambda k: order.get(k, 9)))

        if USE_CTK:
            self.lbl.configure(text=self.combo)
            # Mudar cor se tem modificador + tecla
            mods = {"Ctrl", "Alt", "Shift", "Win"}
            if self.keys & mods and self.keys - mods:
                self.lbl.configure(text_color="#22bb33")
        else:
            self.lbl.config(text=self.combo)

    def on_release(self, e):
        names = {"Control_L": "Ctrl", "Control_R": "Ctrl", "Alt_L": "Alt", "Alt_R": "Alt",
                 "Shift_L": "Shift", "Shift_R": "Shift", "Super_L": "Win", "Super_R": "Win"}
        name = names.get(e.keysym, e.keysym.upper() if len(e.keysym) == 1 else e.keysym)
        self.keys.discard(name)

    def ok(self):
        if self.combo:
            internal = self.combo.lower().replace(" + ", "+")
            internal = internal.replace("ctrl", "<ctrl>").replace("alt", "<alt>")
            internal = internal.replace("shift", "<shift>").replace("win", "<cmd>")
            self.result = (self.combo, internal)
        self.destroy()


if __name__ == "__main__":
    App().run()
