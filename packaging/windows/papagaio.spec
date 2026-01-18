# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Papagaio Windows build
Creates standalone Windows executables from Python source
"""

import os
import sys

block_cipher = None

# Get the project root directory
project_root = os.path.abspath(os.path.join(SPECPATH, '..', '..'))

# Main daemon application
daemon_a = Analysis(
    [os.path.join(project_root, 'papagaio.py')],
    pathex=[project_root],
    binaries=[],
    datas=[],
    hiddenimports=[
        'faster_whisper',
        'pynput',
        'pynput.keyboard',
        'pynput.keyboard._win32',
        'pyaudio',
        'plyer',
        'plyer.platforms.win',
        'plyer.platforms.win.notification',
        'ctypes',
        'ctypes.wintypes',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

daemon_pyz = PYZ(daemon_a.pure, daemon_a.zipped_data, cipher=block_cipher)

daemon_exe = EXE(
    daemon_pyz,
    daemon_a.scripts,
    [],
    exclude_binaries=True,
    name='papagaio',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(project_root, 'packaging', 'windows', 'papagaio.ico') if os.path.exists(os.path.join(project_root, 'packaging', 'windows', 'papagaio.ico')) else None,
)

# Settings GUI application
settings_a = Analysis(
    [os.path.join(project_root, 'papagaio-settings.py')],
    pathex=[project_root],
    binaries=[],
    datas=[],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'configparser',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

settings_pyz = PYZ(settings_a.pure, settings_a.zipped_data, cipher=block_cipher)

settings_exe = EXE(
    settings_pyz,
    settings_a.scripts,
    [],
    exclude_binaries=True,
    name='papagaio-settings',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(project_root, 'packaging', 'windows', 'papagaio.ico') if os.path.exists(os.path.join(project_root, 'packaging', 'windows', 'papagaio.ico')) else None,
)

# System tray application
tray_a = Analysis(
    [os.path.join(project_root, 'papagaio-tray.py')],
    pathex=[project_root],
    binaries=[],
    datas=[],
    hiddenimports=[
        'pystray',
        'pystray._win32',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

tray_pyz = PYZ(tray_a.pure, tray_a.zipped_data, cipher=block_cipher)

tray_exe = EXE(
    tray_pyz,
    tray_a.scripts,
    [],
    exclude_binaries=True,
    name='papagaio-tray',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(project_root, 'packaging', 'windows', 'papagaio.ico') if os.path.exists(os.path.join(project_root, 'packaging', 'windows', 'papagaio.ico')) else None,
)

# Collect all executables
coll = COLLECT(
    daemon_exe,
    daemon_a.binaries,
    daemon_a.zipfiles,
    daemon_a.datas,
    settings_exe,
    settings_a.binaries,
    settings_a.zipfiles,
    settings_a.datas,
    tray_exe,
    tray_a.binaries,
    tray_a.zipfiles,
    tray_a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='papagaio',
)
