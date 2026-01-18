#!/usr/bin/env python3
"""
Papagaio License Activation GUI
Shows trial status and allows license activation

Author: Alexandre Santos <alexandrehsantos@gmail.com>
Company: Bulvee Company
"""

import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from papagaio_license import (
    get_license_status,
    activate_license,
    get_trial_info,
    TRIAL_DAYS
)

# Purchase URL (Gumroad product page)
PURCHASE_URL = "https://bulvee.gumroad.com/l/papagaio"
SUPPORT_EMAIL = "support@bulvee.com"


class ActivationWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Papagaio - License Activation")
        self.root.geometry("450x380")
        self.root.resizable(False, False)

        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 450) // 2
        y = (self.root.winfo_screenheight() - 380) // 2
        self.root.geometry(f"+{x}+{y}")

        self.create_widgets()
        self.update_status()

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Logo/Title
        title_label = ttk.Label(
            main_frame,
            text="🎙️ Papagaio",
            font=("Helvetica", 24, "bold")
        )
        title_label.pack(pady=(0, 5))

        subtitle_label = ttk.Label(
            main_frame,
            text="Voice-to-Text Input",
            font=("Helvetica", 11)
        )
        subtitle_label.pack(pady=(0, 20))

        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="License Status", padding="15")
        status_frame.pack(fill=tk.X, pady=(0, 15))

        self.status_label = ttk.Label(
            status_frame,
            text="Checking...",
            font=("Helvetica", 12)
        )
        self.status_label.pack()

        self.detail_label = ttk.Label(
            status_frame,
            text="",
            font=("Helvetica", 10),
            foreground="gray"
        )
        self.detail_label.pack(pady=(5, 0))

        # License key frame
        key_frame = ttk.LabelFrame(main_frame, text="Enter License Key", padding="15")
        key_frame.pack(fill=tk.X, pady=(0, 15))

        self.key_entry = ttk.Entry(key_frame, width=40, font=("Courier", 11))
        self.key_entry.pack(pady=(0, 10))
        self.key_entry.bind("<Return>", lambda e: self.activate())

        self.activate_btn = ttk.Button(
            key_frame,
            text="Activate License",
            command=self.activate
        )
        self.activate_btn.pack()

        # Buttons frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))

        self.buy_btn = ttk.Button(
            btn_frame,
            text="🛒 Buy License ($29)",
            command=self.open_purchase
        )
        self.buy_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))

        self.continue_btn = ttk.Button(
            btn_frame,
            text="Continue Trial",
            command=self.continue_trial
        )
        self.continue_btn.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(5, 0))

        # Footer
        footer_label = ttk.Label(
            main_frame,
            text=f"Questions? Contact {SUPPORT_EMAIL}",
            font=("Helvetica", 9),
            foreground="gray"
        )
        footer_label.pack(side=tk.BOTTOM)

    def update_status(self):
        status = get_license_status()

        if status["status"] == "licensed":
            self.status_label.config(
                text="✅ License Active",
                foreground="green"
            )
            self.detail_label.config(text=f"Registered to: {status.get('email', 'N/A')}")
            self.continue_btn.config(text="Launch Papagaio", state="normal")
            self.activate_btn.config(state="disabled")
            self.key_entry.config(state="disabled")

        elif status["status"] == "trial":
            days = status["remaining_days"]
            if days > 3:
                color = "blue"
            elif days > 1:
                color = "orange"
            else:
                color = "red"

            self.status_label.config(
                text=f"⏱️ Trial: {days} days remaining",
                foreground=color
            )
            self.detail_label.config(text=f"Full version: Unlimited use")
            self.continue_btn.config(text="Continue Trial", state="normal")

        else:  # expired
            self.status_label.config(
                text="⛔ Trial Expired",
                foreground="red"
            )
            self.detail_label.config(text="Please purchase a license to continue")
            self.continue_btn.config(text="Trial Expired", state="disabled")

    def activate(self):
        key = self.key_entry.get().strip()

        if not key:
            messagebox.showwarning("Missing Key", "Please enter your license key.")
            return

        self.activate_btn.config(state="disabled", text="Validating...")
        self.root.update()

        result = activate_license(key)

        if result["valid"]:
            messagebox.showinfo("Success", "License activated successfully!\n\nThank you for purchasing Papagaio.")
            self.update_status()
        else:
            messagebox.showerror("Invalid License", result["message"])
            self.activate_btn.config(state="normal", text="Activate License")

    def open_purchase(self):
        webbrowser.open(PURCHASE_URL)

    def continue_trial(self):
        status = get_license_status()

        if status["status"] == "expired":
            messagebox.showwarning(
                "Trial Expired",
                "Your trial has expired.\n\nPlease purchase a license to continue using Papagaio."
            )
            return

        self.root.destroy()
        # Return success code
        sys.exit(0)

    def run(self):
        self.root.mainloop()

        # If window closed without continuing, check status
        status = get_license_status()
        if status["status"] == "expired":
            sys.exit(1)


def show_activation_if_needed():
    """Show activation window if trial expired or no license"""
    status = get_license_status()

    if status["status"] == "licensed":
        return True

    if status["status"] == "trial":
        # Show reminder on last 2 days
        if status["remaining_days"] <= 2:
            app = ActivationWindow()
            app.run()
        return True

    # Trial expired - must activate
    app = ActivationWindow()
    app.run()
    return False


if __name__ == "__main__":
    app = ActivationWindow()
    app.run()
