# Ubuntu PPA Publishing Guide

Complete guide to publish Papagaio on Ubuntu PPA (Personal Package Archive).

After publication, users can install with:
```bash
sudo add-apt-repository ppa:your-username/papagaio
sudo apt update
sudo apt install papagaio
```

## Prerequisites

### 1. Create Launchpad Account

1. Go to https://launchpad.net/
2. Sign up with Ubuntu One account
3. Complete profile setup

### 2. Install Required Tools

```bash
sudo apt install devscripts debhelper dh-python dput gnupg
```

### 3. Generate GPG Key

```bash
# Generate key
gpg --full-generate-key

# Choose:
# - Key type: RSA and RSA
# - Key size: 4096
# - Expiration: 0 (no expiration) or 2y (2 years)
# - Real name: Your Name
# - Email: your-email@example.com (must match Launchpad email)
```

### 4. Upload GPG Key to Launchpad

```bash
# Get your key fingerprint
gpg --list-secret-keys --keyid-format LONG

# Example output:
# sec   rsa4096/1234ABCD5678EFGH 2025-10-08 [SC]
#       ABCD1234EFGH5678IJKL9012MNOP3456QRST7890
# uid   Your Name <your-email@example.com>

# Export public key (copy the entire output)
gpg --armor --export 1234ABCD5678EFGH
```

Upload to Launchpad:
1. Go to https://launchpad.net/~your-username/+editpgpkeys
2. Paste the exported key
3. Click "Import Key"
4. Check email and confirm

### 5. Create PPA

1. Go to https://launchpad.net/~your-username/+activate-ppa
2. Fill in:
   - **URL:** papagaio
   - **Display name:** Papagaio
   - **Description:**
     ```
     Voice-to-text daemon for Linux using Whisper speech recognition.

     Features:
     - Global hotkey support
     - Local processing (privacy-first)
     - Voice Activity Detection
     - Bilingual interface (English/Portuguese)
     ```
3. Click "Activate"

## Build and Upload

### Method 1: Using Build Script (Recommended)

```bash
cd /path/to/papagaio

# Build and upload
./packaging/build-ppa.sh ppa:your-username/papagaio
```

### Method 2: Manual Steps

#### Step 1: Update debian/changelog

Ensure version has ubuntu suffix:
```
papagaio (1.1.0-1ubuntu1) focal; urgency=medium
```

Supported Ubuntu releases:
- `focal` - Ubuntu 20.04 LTS
- `jammy` - Ubuntu 22.04 LTS
- `noble` - Ubuntu 24.04 LTS
- `mantic` - Ubuntu 23.10

#### Step 2: Build Source Package

```bash
cd /path/to/papagaio

# Clean previous builds
rm -f ../*.deb ../*.build ../*.changes ../*.dsc ../*.tar.*

# Build source package (will ask for GPG passphrase)
debuild -S -sa
```

Files generated in parent directory:
- `papagaio_1.1.0-1ubuntu1.dsc` - Package description
- `papagaio_1.1.0-1ubuntu1.debian.tar.xz` - Debian files
- `papagaio_1.1.0-1ubuntu1_source.changes` - Changes file
- `papagaio_1.1.0-1ubuntu1_source.build` - Build log

#### Step 3: Upload to PPA

```bash
# Upload
dput ppa:your-username/papagaio ../papagaio_1.1.0-1ubuntu1_source.changes
```

#### Step 4: Wait for Build

1. Go to https://launchpad.net/~your-username/+archive/ubuntu/papagaio/+packages
2. Wait 10-30 minutes for build to complete
3. Build will be done for: amd64, i386, arm64, armhf

Build status:
- **Building** - In progress
- **Successfully built** - Ready for installation
- **Failed to build** - Check build log for errors

## After Publication

### Users Install

```bash
# Add repository
sudo add-apt-repository ppa:your-username/papagaio
sudo apt update

# Install
sudo apt install papagaio
```

### Update README.md

Add PPA installation method:

```markdown
**Ubuntu PPA:**
```bash
sudo add-apt-repository ppa:your-username/papagaio
sudo apt update
sudo apt install papagaio
```
```

## Publishing Updates

When releasing a new version:

1. Update version in:
   - `debian/changelog` (add new entry at top)
   - `setup.py`
   - `Makefile`

2. Update changelog:
```bash
dch -v 1.2.0-1ubuntu1 -D focal
# This opens editor - add changes
```

3. Build and upload:
```bash
debuild -S -sa
dput ppa:your-username/papagaio ../papagaio_1.2.0-1ubuntu1_source.changes
```

## Troubleshooting

### GPG Key Issues

```bash
# List keys
gpg --list-secret-keys

# If no key:
gpg --full-generate-key

# Test signing
echo "test" | gpg --clearsign
```

### Build Fails

Check build log:
```
https://launchpad.net/~your-username/+archive/ubuntu/papagaio/+build/BUILD_ID
```

Common issues:
- Missing build dependencies in `debian/control`
- Wrong Python version
- debian/rules syntax errors

### Upload Rejected

Reasons:
- GPG key not uploaded to Launchpad
- Email mismatch (changelog vs GPG key vs Launchpad)
- Version already exists (increment version)

## Multiple Ubuntu Versions

To support multiple Ubuntu versions, create separate uploads:

```bash
# Ubuntu 20.04 (Focal)
dch -v 1.1.0-1ubuntu1~focal1 -D focal
debuild -S -sa
dput ppa:your-username/papagaio ../papagaio_1.1.0-1ubuntu1~focal1_source.changes

# Ubuntu 22.04 (Jammy)
dch -v 1.1.0-1ubuntu1~jammy1 -D jammy
debuild -S -sa
dput ppa:your-username/papagaio ../papagaio_1.1.0-1ubuntu1~jammy1_source.changes
```

## Resources

- Launchpad PPA Help: https://help.launchpad.net/Packaging/PPA
- Debian Policy: https://www.debian.org/doc/debian-policy/
- Ubuntu Packaging Guide: https://packaging.ubuntu.com/html/

## Summary

**One-time setup:**
1. Create Launchpad account
2. Generate and upload GPG key
3. Create PPA

**For each release:**
1. Update `debian/changelog`
2. Run `debuild -S -sa`
3. Run `dput ppa:your-username/papagaio ...`
4. Wait for build (10-30 min)
5. Users can `apt install`

**Users install:**
```bash
sudo add-apt-repository ppa:your-username/papagaio
sudo apt install papagaio
```
