#!/usr/bin/env python3
"""
Whisper Voice Daemon - Setup Script
"""

from setuptools import setup, find_packages
import os

# Read long description from README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="whisper-voice-daemon",
    version="1.0.1",
    author="Alexandre Santos",
    author_email="alexandrehsantos@example.com",
    description="Voice-to-text daemon for Linux using Whisper speech recognition",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alexandrehsantos/whisper-voice-daemon",
    project_urls={
        "Bug Tracker": "https://github.com/alexandrehsantos/whisper-voice-daemon/issues",
        "Documentation": "https://github.com/alexandrehsantos/whisper-voice-daemon#readme",
        "Source Code": "https://github.com/alexandrehsantos/whisper-voice-daemon",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Environment :: Console",
        "Natural Language :: English",
        "Natural Language :: Portuguese",
    ],
    keywords="whisper voice speech-to-text voice-input transcription linux daemon",
    packages=find_packages(where="src") if os.path.exists("src") else [],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
        ],
    },
    scripts=[
        "voice-daemon.py",
        "voice-ctl",
        "install.sh",
        "uninstall.sh",
    ],
    data_files=[
        ("share/doc/whisper-voice-daemon", ["README.md", "CHANGELOG.md", "LICENSE", "CONTRIBUTING.md"]),
        ("share/whisper-voice-daemon", ["requirements.txt"]),
    ],
    entry_points={
        "console_scripts": [
            "voice-daemon=voice-daemon:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    platforms=["Linux"],
)
