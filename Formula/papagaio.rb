# Papagaio Homebrew Formula
# Voice-to-text input daemon using Whisper AI
#
# Author: Alexandre Santos <alexandrehsantos@gmail.com>
# Company: Bulvee Company
#
# Installation:
#   brew tap alexandrehsantos/papagaio
#   brew install papagaio
#
# Or direct:
#   brew install alexandrehsantos/papagaio/papagaio

class Papagaio < Formula
  include Language::Python::Virtualenv

  desc "Voice-to-text input daemon using Whisper AI"
  homepage "https://github.com/alexandrehsantos/papagaio"
  url "https://github.com/alexandrehsantos/papagaio/archive/refs/tags/v1.1.0.tar.gz"
  sha256 "PLACEHOLDER_SHA256"
  license "MIT"
  head "https://github.com/alexandrehsantos/papagaio.git", branch: "main"

  depends_on "python@3.11"
  depends_on "portaudio"

  resource "faster-whisper" do
    url "https://files.pythonhosted.org/packages/source/f/faster-whisper/faster_whisper-1.0.0.tar.gz"
    sha256 "PLACEHOLDER_SHA256"
  end

  resource "pynput" do
    url "https://files.pythonhosted.org/packages/source/p/pynput/pynput-1.7.6.tar.gz"
    sha256 "PLACEHOLDER_SHA256"
  end

  resource "PyAudio" do
    url "https://files.pythonhosted.org/packages/source/P/PyAudio/PyAudio-0.2.14.tar.gz"
    sha256 "PLACEHOLDER_SHA256"
  end

  resource "plyer" do
    url "https://files.pythonhosted.org/packages/source/p/plyer/plyer-2.1.0.tar.gz"
    sha256 "PLACEHOLDER_SHA256"
  end

  resource "pystray" do
    url "https://files.pythonhosted.org/packages/source/p/pystray/pystray-0.19.5.tar.gz"
    sha256 "PLACEHOLDER_SHA256"
  end

  resource "Pillow" do
    url "https://files.pythonhosted.org/packages/source/P/Pillow/Pillow-10.2.0.tar.gz"
    sha256 "PLACEHOLDER_SHA256"
  end

  def install
    # Create virtual environment
    venv = virtualenv_create(libexec, "python3.11")

    # Install Python dependencies
    venv.pip_install resources

    # Install main scripts
    libexec.install "papagaio.py"
    libexec.install "papagaio-settings.py"
    libexec.install "papagaio-tray.py"

    # Create wrapper scripts
    (bin/"papagaio").write <<~EOS
      #!/bin/bash
      exec "#{libexec}/bin/python" "#{libexec}/papagaio.py" "$@"
    EOS

    (bin/"papagaio-settings").write <<~EOS
      #!/bin/bash
      exec "#{libexec}/bin/python" "#{libexec}/papagaio-settings.py" "$@"
    EOS

    (bin/"papagaio-tray").write <<~EOS
      #!/bin/bash
      exec "#{libexec}/bin/python" "#{libexec}/papagaio-tray.py" "$@"
    EOS

    # Install control script
    bin.install "macos/papagaio-ctl-macos" => "papagaio-ctl"

    # Install launchd plist
    prefix.install "macos/com.bulvee.papagaio.plist"

    # Create config directory
    (var/"papagaio").mkpath
  end

  def post_install
    # Create default config if not exists
    config_dir = Pathname.new(Dir.home) / ".config" / "papagaio"
    config_file = config_dir / "config.ini"

    unless config_file.exist?
      config_dir.mkpath
      config_file.write <<~EOS
        # Papagaio Configuration
        # Edit this file to customize settings

        [General]
        model = small
        language = en
        hotkey = <cmd>+<shift>+<alt>+v
        cache_dir = #{var}/papagaio/models

        [Audio]
        silence_threshold = 400
        silence_duration = 5.0
        max_recording_time = 3600

        [Advanced]
        typing_delay = 0.3
      EOS
    end
  end

  def caveats
    <<~EOS
      Papagaio has been installed!

      Quick start:
        papagaio-ctl start     # Start daemon
        papagaio-ctl status    # Check status
        papagaio-settings      # Open settings GUI

      Default hotkey: Cmd+Shift+Alt+V

      To start automatically on login:
        brew services start papagaio

      Or manually install the launchd service:
        cp #{prefix}/com.bulvee.papagaio.plist ~/Library/LaunchAgents/
        launchctl load ~/Library/LaunchAgents/com.bulvee.papagaio.plist

      Configuration file:
        ~/.config/papagaio/config.ini

      Note: On first run, Papagaio will download the Whisper model (~460MB for 'small').
      Models are cached in #{var}/papagaio/models

      For accessibility features (keyboard simulation), grant permissions:
        System Preferences > Security & Privacy > Privacy > Accessibility
    EOS
  end

  service do
    run [opt_bin/"papagaio"]
    keep_alive true
    log_path var/"log/papagaio.log"
    error_log_path var/"log/papagaio.error.log"
    environment_variables DISPLAY: ":0"
  end

  test do
    assert_match "Papagaio", shell_output("#{bin}/papagaio --help")
  end
end
