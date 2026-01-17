#!/usr/bin/env python3
"""
Papagaio System Tray - Graphical Control Interface
Provides system tray icon with menu for controlling the daemon
"""

import subprocess
import sys
import os

# Check for pystray availability
try:
    import pystray
    from PIL import Image, ImageDraw
except ImportError:
    print("Required packages not found. Installing...")
    subprocess.run([sys.executable, "-m", "pip", "install", "--user", "pystray", "Pillow"])
    import pystray
    from PIL import Image, ImageDraw

INSTALL_DIR = os.path.expanduser("~/.local/bin/papagaio")
SERVICE_NAME = "papagaio"


def create_icon_image(color="gray"):
    """Create a simple microphone icon"""
    size = 64
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    colors = {
        "gray": "#808080",
        "green": "#4CAF50",
        "red": "#F44336",
        "orange": "#FF9800"
    }
    fill_color = colors.get(color, "#808080")

    # Microphone body (rounded rectangle)
    draw.rounded_rectangle([20, 8, 44, 38], radius=8, fill=fill_color)

    # Microphone stand (arc + line)
    draw.arc([14, 20, 50, 48], start=0, end=180, fill=fill_color, width=3)
    draw.line([32, 48, 32, 56], fill=fill_color, width=3)
    draw.line([22, 56, 42, 56], fill=fill_color, width=3)

    return image


def is_daemon_running():
    """Check if the daemon is running"""
    try:
        result = subprocess.run(
            ["systemctl", "--user", "is-active", SERVICE_NAME],
            capture_output=True, text=True
        )
        return result.stdout.strip() == "active"
    except Exception:
        return False


def start_daemon(icon, item):
    """Start the daemon"""
    try:
        subprocess.run(["systemctl", "--user", "start", SERVICE_NAME], check=True)
        update_icon(icon)
        show_notification("Papagaio", "Daemon started")
    except subprocess.CalledProcessError:
        show_notification("Papagaio", "Failed to start daemon", error=True)


def stop_daemon(icon, item):
    """Stop the daemon"""
    try:
        subprocess.run(["systemctl", "--user", "stop", SERVICE_NAME], check=True)
        update_icon(icon)
        show_notification("Papagaio", "Daemon stopped")
    except subprocess.CalledProcessError:
        show_notification("Papagaio", "Failed to stop daemon", error=True)


def restart_daemon(icon, item):
    """Restart the daemon"""
    try:
        subprocess.run(["systemctl", "--user", "restart", SERVICE_NAME], check=True)
        update_icon(icon)
        show_notification("Papagaio", "Daemon restarted")
    except subprocess.CalledProcessError:
        show_notification("Papagaio", "Failed to restart daemon", error=True)


def open_settings(icon, item):
    """Open settings GUI"""
    settings_script = os.path.join(INSTALL_DIR, "papagaio-settings.py")
    if not os.path.exists(settings_script):
        settings_script = os.path.join(os.path.dirname(__file__), "papagaio-settings.py")

    if os.path.exists(settings_script):
        subprocess.Popen([sys.executable, settings_script])
    else:
        show_notification("Papagaio", "Settings not found", error=True)


def open_logs(icon, item):
    """Open logs in terminal"""
    try:
        # Try different terminal emulators
        terminals = [
            ["gnome-terminal", "--", "journalctl", "--user", "-u", SERVICE_NAME, "-f"],
            ["xfce4-terminal", "-e", "journalctl --user -u papagaio -f"],
            ["konsole", "-e", "journalctl", "--user", "-u", SERVICE_NAME, "-f"],
            ["xterm", "-e", "journalctl --user -u papagaio -f"]
        ]

        for term_cmd in terminals:
            try:
                subprocess.Popen(term_cmd)
                return
            except FileNotFoundError:
                continue

        show_notification("Papagaio", "No terminal found", error=True)
    except Exception as e:
        show_notification("Papagaio", f"Error: {e}", error=True)


def show_notification(title, message, error=False):
    """Show desktop notification"""
    try:
        urgency = "critical" if error else "normal"
        subprocess.run(["notify-send", "-u", urgency, title, message], check=False)
    except Exception:
        pass


def update_icon(icon):
    """Update icon based on daemon status"""
    if is_daemon_running():
        icon.icon = create_icon_image("green")
        icon.title = "Papagaio - Running"
    else:
        icon.icon = create_icon_image("gray")
        icon.title = "Papagaio - Stopped"


def get_status_text(item):
    """Get current status for menu"""
    if is_daemon_running():
        return "Status: Running"
    return "Status: Stopped"


def quit_app(icon, item):
    """Quit the tray application"""
    icon.stop()


def create_menu():
    """Create the system tray menu"""
    return pystray.Menu(
        pystray.MenuItem(
            get_status_text,
            None,
            enabled=False
        ),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(
            "Start",
            start_daemon,
            visible=lambda item: not is_daemon_running()
        ),
        pystray.MenuItem(
            "Stop",
            stop_daemon,
            visible=lambda item: is_daemon_running()
        ),
        pystray.MenuItem(
            "Restart",
            restart_daemon,
            visible=lambda item: is_daemon_running()
        ),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Settings", open_settings),
        pystray.MenuItem("View Logs", open_logs),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit Tray", quit_app)
    )


def main():
    """Main entry point"""
    # Determine initial icon color
    color = "green" if is_daemon_running() else "gray"
    title = "Papagaio - Running" if is_daemon_running() else "Papagaio - Stopped"

    icon = pystray.Icon(
        name="papagaio",
        icon=create_icon_image(color),
        title=title,
        menu=create_menu()
    )

    # Update icon periodically
    def setup(icon):
        icon.visible = True

    icon.run(setup)


if __name__ == "__main__":
    main()
