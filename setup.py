#!/usr/bin/env python3
"""
Papagaio - Voice-to-text daemon for Linux
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
    name="papagaio",
    version="1.1.0",
    author="Alexandre Santos",
    author_email="alexandrehsantos@example.com",
    description="Voice-to-text daemon for Linux - Papagaio repeats what you say",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alexandrehsantos/papagaio",
    project_urls={
        "Bug Tracker": "https://github.com/alexandrehsantos/papagaio/issues",
        "Documentation": "https://github.com/alexandrehsantos/papagaio#readme",
        "Source Code": "https://github.com/alexandrehsantos/papagaio",
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
    keywords="papagaio voice speech-to-text voice-input transcription linux daemon whisper",
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
        "papagaio.py",
        "papagaioctl",
        "install.sh",
        "uninstall.sh",
    ],
    data_files=[
        ("share/doc/papagaio", ["README.md", "CHANGELOG.md", "LICENSE", "CONTRIBUTING.md"]),
        ("share/papagaio", ["requirements.txt"]),
    ],
    entry_points={
        "console_scripts": [
            "papagaio=papagaio:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    platforms=["Linux"],
)
