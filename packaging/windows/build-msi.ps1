# Papagaio Windows MSI Build Script
# Builds standalone Windows installer using PyInstaller and WiX Toolset
#
# Author: Alexandre Santos <alexandrehsantos@gmail.com>
# Company: Bulvee Company
#
# Requirements:
#   - Python 3.8+
#   - PyInstaller: pip install pyinstaller
#   - WiX Toolset 3.x: https://wixtoolset.org/releases/
#   - Visual C++ Build Tools (for some dependencies)
#
# Usage:
#   .\build-msi.ps1
#   .\build-msi.ps1 -SkipPyInstaller  # Only rebuild MSI

param(
    [switch]$SkipPyInstaller,
    [switch]$Clean
)

$ErrorActionPreference = "Stop"

# Configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = (Get-Item "$ScriptDir\..\..").FullName
$BuildDir = Join-Path $ScriptDir "build"
$DistDir = Join-Path $ScriptDir "dist"
$OutputDir = Join-Path $ProjectRoot "dist"

$Version = "1.1.0"
$ProductName = "Papagaio"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Papagaio Windows MSI Builder" -ForegroundColor Cyan
Write-Host "  Version: $Version" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Clean previous builds
if ($Clean) {
    Write-Host "[1/6] Cleaning previous builds..." -ForegroundColor Yellow
    Remove-Item -Path $BuildDir -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path $DistDir -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path (Join-Path $OutputDir "*.msi") -Force -ErrorAction SilentlyContinue
}

# Create directories
New-Item -ItemType Directory -Path $BuildDir -Force | Out-Null
New-Item -ItemType Directory -Path $DistDir -Force | Out-Null
New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null

# Step 1: Check dependencies
Write-Host "[1/6] Checking dependencies..." -ForegroundColor Yellow

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Check PyInstaller
try {
    $pyinstallerVersion = pyinstaller --version 2>&1
    Write-Host "  PyInstaller: $pyinstallerVersion" -ForegroundColor Green
} catch {
    Write-Host "  PyInstaller not found. Installing..." -ForegroundColor Yellow
    pip install pyinstaller
}

# Check WiX
$wixPath = $null
$wixPaths = @(
    "${env:ProgramFiles(x86)}\WiX Toolset v3.11\bin",
    "${env:ProgramFiles}\WiX Toolset v3.11\bin",
    "${env:ProgramFiles(x86)}\WiX Toolset v3.14\bin",
    "${env:ProgramFiles}\WiX Toolset v3.14\bin"
)

foreach ($path in $wixPaths) {
    if (Test-Path (Join-Path $path "candle.exe")) {
        $wixPath = $path
        break
    }
}

if (-not $wixPath) {
    Write-Host "  WARNING: WiX Toolset not found. MSI creation will be skipped." -ForegroundColor Yellow
    Write-Host "  Download from: https://wixtoolset.org/releases/" -ForegroundColor Yellow
    $skipWix = $true
} else {
    Write-Host "  WiX Toolset: $wixPath" -ForegroundColor Green
    $env:PATH = "$wixPath;$env:PATH"
}

# Step 2: Install Python dependencies
Write-Host ""
Write-Host "[2/6] Installing Python dependencies..." -ForegroundColor Yellow
pip install faster-whisper pynput pyaudio plyer pystray Pillow --quiet

# Step 3: Build with PyInstaller
if (-not $SkipPyInstaller) {
    Write-Host ""
    Write-Host "[3/6] Building executables with PyInstaller..." -ForegroundColor Yellow

    Push-Location $ScriptDir
    try {
        pyinstaller --clean --noconfirm papagaio.spec
        if ($LASTEXITCODE -ne 0) {
            throw "PyInstaller build failed"
        }
        Write-Host "  Executables built successfully" -ForegroundColor Green
    } finally {
        Pop-Location
    }
} else {
    Write-Host ""
    Write-Host "[3/6] Skipping PyInstaller (using existing build)..." -ForegroundColor Yellow
}

# Check PyInstaller output
$pyinstallerOutput = Join-Path $ScriptDir "dist\papagaio"
if (-not (Test-Path $pyinstallerOutput)) {
    Write-Host "  ERROR: PyInstaller output not found at $pyinstallerOutput" -ForegroundColor Red
    exit 1
}

# Step 4: Create default config file
Write-Host ""
Write-Host "[4/6] Creating default configuration..." -ForegroundColor Yellow

$configContent = @"
# Papagaio Configuration
# Edit this file to customize settings

[General]
model = small
language = en
hotkey = <ctrl>+<shift>+<alt>+v
cache_dir = %LOCALAPPDATA%\Papagaio\models

[Audio]
silence_threshold = 400
silence_duration = 5.0
max_recording_time = 3600

[Advanced]
typing_delay = 0.3
"@

$configFile = Join-Path $pyinstallerOutput "config.ini.default"
$configContent | Out-File -FilePath $configFile -Encoding UTF8
Write-Host "  Default config created" -ForegroundColor Green

# Step 5: Build MSI with WiX
if (-not $skipWix) {
    Write-Host ""
    Write-Host "[5/6] Building MSI installer..." -ForegroundColor Yellow

    # Create license file if not exists
    $licenseFile = Join-Path $ScriptDir "license.rtf"
    if (-not (Test-Path $licenseFile)) {
        $licenseContent = @"
{\rtf1\ansi\deff0
{\fonttbl{\f0 Arial;}}
\f0\fs20
MIT License\par
\par
Copyright (c) 2024 Alexandre Santos / Bulvee Company\par
\par
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:\par
\par
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.\par
\par
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
}
"@
        $licenseContent | Out-File -FilePath $licenseFile -Encoding ASCII
    }

    # Harvest files from PyInstaller output
    Write-Host "  Harvesting files..." -ForegroundColor Gray
    $wxsFragment = Join-Path $BuildDir "files.wxs"

    & heat.exe dir $pyinstallerOutput `
        -cg ProductComponents `
        -dr BinFolder `
        -srd `
        -ag `
        -sfrag `
        -var var.SourceDir `
        -out $wxsFragment

    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ERROR: heat.exe failed" -ForegroundColor Red
        exit 1
    }

    # Compile WiX sources
    Write-Host "  Compiling installer..." -ForegroundColor Gray
    $mainWxs = Join-Path $ScriptDir "papagaio.wxs"
    $mainWixobj = Join-Path $BuildDir "papagaio.wixobj"
    $filesWixobj = Join-Path $BuildDir "files.wixobj"

    & candle.exe -dSourceDir="$pyinstallerOutput" -out $mainWixobj $mainWxs
    & candle.exe -dSourceDir="$pyinstallerOutput" -out $filesWixobj $wxsFragment

    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ERROR: candle.exe failed" -ForegroundColor Red
        exit 1
    }

    # Link MSI
    Write-Host "  Linking MSI..." -ForegroundColor Gray
    $msiFile = Join-Path $OutputDir "papagaio-$Version-win64.msi"

    & light.exe `
        -ext WixUIExtension `
        -ext WixUtilExtension `
        -out $msiFile `
        $mainWixobj $filesWixobj

    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ERROR: light.exe failed" -ForegroundColor Red
        exit 1
    }

    Write-Host "  MSI created: $msiFile" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "[5/6] Skipping MSI creation (WiX not installed)..." -ForegroundColor Yellow

    # Create portable ZIP instead
    Write-Host "  Creating portable ZIP..." -ForegroundColor Gray
    $zipFile = Join-Path $OutputDir "papagaio-$Version-win64-portable.zip"
    Compress-Archive -Path "$pyinstallerOutput\*" -DestinationPath $zipFile -Force
    Write-Host "  Portable ZIP created: $zipFile" -ForegroundColor Green
}

# Step 6: Summary
Write-Host ""
Write-Host "[6/6] Build complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Output files:" -ForegroundColor Cyan

Get-ChildItem $OutputDir -Filter "papagaio-*" | ForEach-Object {
    $size = [math]::Round($_.Length / 1MB, 2)
    Write-Host "  $($_.Name) ($size MB)" -ForegroundColor White
}

Write-Host ""
Write-Host "To install:" -ForegroundColor Cyan
Write-Host "  - MSI: Double-click the .msi file" -ForegroundColor White
Write-Host "  - Portable: Extract ZIP to any folder and run papagaio-tray.exe" -ForegroundColor White
Write-Host ""
