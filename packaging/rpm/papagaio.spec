# Papagaio RPM Spec File
# Voice-to-text input daemon using Whisper AI
#
# Author: Alexandre Santos <alexandrehsantos@gmail.com>
# Company: Bulvee Company
#
# Build:
#   rpmbuild -ba papagaio.spec
#   or use build-rpm.sh script

Name:           papagaio
Version:        1.1.0
Release:        1%{?dist}
Summary:        Voice-to-text input daemon using Whisper AI

License:        MIT
URL:            https://github.com/alexandrehsantos/papagaio
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools

Requires:       python3 >= 3.8
Requires:       python3-pip
Requires:       portaudio
Requires:       xdotool

# Python dependencies (installed via pip post-install)
# faster-whisper, pynput, pyaudio, plyer, pystray, Pillow

%description
Papagaio is a voice-to-text input daemon that uses OpenAI's Whisper AI
for accurate speech recognition. Press a configurable hotkey, speak,
and the transcribed text is automatically typed into any application.

Features:
- High-quality speech recognition with Whisper AI (faster-whisper)
- Works with any application via xdotool/ydotool
- Configurable hotkey activation
- Multiple Whisper model sizes (tiny, base, small, medium)
- System tray integration for easy control
- Graphical settings interface

%prep
%autosetup -n %{name}-%{version}

%build
# Nothing to build - pure Python

%install
# Create directories
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_libexecdir}/%{name}
mkdir -p %{buildroot}%{_datadir}/applications
mkdir -p %{buildroot}%{_sysconfdir}/xdg/autostart
mkdir -p %{buildroot}%{_userunitdir}

# Install main scripts
install -m 755 papagaio.py %{buildroot}%{_libexecdir}/%{name}/
install -m 755 papagaio-settings.py %{buildroot}%{_libexecdir}/%{name}/
install -m 755 papagaio-tray.py %{buildroot}%{_libexecdir}/%{name}/
install -m 755 papagaio-ctl %{buildroot}%{_libexecdir}/%{name}/

# Create wrapper scripts
cat > %{buildroot}%{_bindir}/papagaio << 'EOF'
#!/bin/bash
exec python3 %{_libexecdir}/%{name}/papagaio.py "$@"
EOF
chmod 755 %{buildroot}%{_bindir}/papagaio

cat > %{buildroot}%{_bindir}/papagaio-ctl << 'EOF'
#!/bin/bash
exec %{_libexecdir}/%{name}/papagaio-ctl "$@"
EOF
chmod 755 %{buildroot}%{_bindir}/papagaio-ctl

cat > %{buildroot}%{_bindir}/papagaio-settings << 'EOF'
#!/bin/bash
exec python3 %{_libexecdir}/%{name}/papagaio-settings.py "$@"
EOF
chmod 755 %{buildroot}%{_bindir}/papagaio-settings

cat > %{buildroot}%{_bindir}/papagaio-tray << 'EOF'
#!/bin/bash
exec python3 %{_libexecdir}/%{name}/papagaio-tray.py "$@"
EOF
chmod 755 %{buildroot}%{_bindir}/papagaio-tray

# Install desktop files
install -m 644 papagaio-settings.desktop %{buildroot}%{_datadir}/applications/
install -m 644 papagaio-tray.desktop %{buildroot}%{_datadir}/applications/

# Install autostart
install -m 644 papagaio-tray.desktop %{buildroot}%{_sysconfdir}/xdg/autostart/

# Install systemd user service
cat > %{buildroot}%{_userunitdir}/%{name}.service << 'EOF'
[Unit]
Description=Papagaio - Voice-to-Text Input Daemon
Documentation=https://github.com/alexandrehsantos/papagaio
After=graphical-session.target

[Service]
Type=simple
ExecStart=%{_bindir}/papagaio
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF

%post
# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --user faster-whisper pynput pyaudio plyer pystray Pillow 2>/dev/null || \
    pip3 install faster-whisper pynput pyaudio plyer pystray Pillow 2>/dev/null || \
    echo "Warning: Could not install Python dependencies automatically."
    echo "Please run: pip3 install faster-whisper pynput pyaudio plyer pystray Pillow"

# Reload systemd user daemon
systemctl --user daemon-reload 2>/dev/null || true

echo ""
echo "Papagaio installed successfully!"
echo ""
echo "Quick start:"
echo "  papagaio-ctl start     # Start daemon"
echo "  papagaio-ctl status    # Check status"
echo "  papagaio-settings      # Open settings"
echo ""

%preun
# Stop service before uninstall
systemctl --user stop %{name} 2>/dev/null || true
systemctl --user disable %{name} 2>/dev/null || true

%postun
# Reload systemd
systemctl --user daemon-reload 2>/dev/null || true

%files
%license LICENSE
%doc README.md
%{_bindir}/papagaio
%{_bindir}/papagaio-ctl
%{_bindir}/papagaio-settings
%{_bindir}/papagaio-tray
%{_libexecdir}/%{name}/
%{_datadir}/applications/papagaio-settings.desktop
%{_datadir}/applications/papagaio-tray.desktop
%{_sysconfdir}/xdg/autostart/papagaio-tray.desktop
%{_userunitdir}/%{name}.service

%changelog
* %(date "+%a %b %d %Y") Alexandre Santos <alexandrehsantos@gmail.com> - 1.1.0-1
- Initial RPM release
- Voice-to-text daemon with Whisper AI
- System tray GUI
- Settings GUI
- Cross-platform support
