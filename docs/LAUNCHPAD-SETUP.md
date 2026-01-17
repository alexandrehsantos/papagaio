# Launchpad Setup Guide

Complete guide to register Papagaio on Launchpad for PPA publishing.

## Step 1: Create Launchpad Account

1. Go to https://launchpad.net/
2. Click "Log in / Register"
3. Click "I am a new Ubuntu One user"
4. Fill in:
   - Email address
   - Full name
   - Password
   - Accept terms
5. Check email and verify account
6. Complete profile setup

## Step 2: Register Project on Launchpad

### Option A: Register as New Project

1. Go to https://launchpad.net/projects/+new
2. Fill in the form:

**Project Details:**
- **URL:** `papagaio`
  - This will be: https://launchpad.net/papagaio
- **Display Name:** `Papagaio`
- **Summary (one line):**
  ```
  Voice-to-text daemon for Linux using Whisper speech recognition
  ```

**Description:**
```
Voice-to-text daemon for Linux with global hotkey support.

Features:
- Global hotkey activation (Ctrl+Alt+V)
- Local processing only (privacy-first)
- Voice Activity Detection (VAD) with automatic silence detection
- Manual control (stop with hotkey, cancel with ESC)
- Bilingual interface (English/Portuguese)
- Systemd integration
- Works with any application

Technical:
- Uses OpenAI Whisper via Faster-Whisper
- Python 3.8+
- Multiple keyboard backends (xdotool, ydotool)
- Configurable models (tiny, base, small, medium)

Installation methods:
- pip install papagaio
- Ubuntu PPA (apt install)
- Debian package (.deb)
- Arch AUR
- Source installation

Project repository: https://github.com/alexandrehsantos/papagaio
```

**Additional Information:**
- **Maintainer:** Your Name
- **Driver:** Yourself (you'll be added as project owner)
- **Licenses:** MIT / X / Expat License
- **Source:** https://github.com/alexandrehsantos/papagaio

3. Click "Register"

### Option B: Import from GitHub (Recommended)

Launchpad can import code from GitHub:

1. Go to https://launchpad.net/projects/+new
2. Select "Import a project hosted somewhere else"
3. Choose "Git"
4. Enter:
   - **Git repository URL:** `https://github.com/alexandrehsantos/papagaio.git`
   - **Project name:** `papagaio`
5. Fill in project details (same as above)
6. Click "Create Project"

## Step 3: Configure GPG Key

### Generate GPG Key

```bash
# Generate key (if you don't have one)
gpg --full-generate-key

# Choose:
# 1. RSA and RSA
# 2. 4096 bits
# 3. 0 = key does not expire (or 2y for 2 years)
# 4. Your real name
# 5. Email (MUST match Launchpad email)
# 6. Comment (optional): "Launchpad PPA signing key"
# 7. Passphrase (remember this!)
```

### Upload to Launchpad

```bash
# List your keys
gpg --list-secret-keys --keyid-format LONG

# Example output:
# sec   rsa4096/1234ABCD5678EFGH 2025-10-08 [SC]
#       ABCD1234EFGH5678IJKL9012MNOP3456QRST7890
# uid   Your Name <your-email@example.com>
# ssb   rsa4096/9876ZYXW5432VUTR 2025-10-08 [E]

# Export public key (use the long key ID)
gpg --armor --export 1234ABCD5678EFGH

# Copy the entire output (including BEGIN/END lines)
```

Upload to Launchpad:
1. Go to https://launchpad.net/~your-username/+editpgpkeys
2. Paste the entire GPG public key
3. Click "Import Key"
4. Check your email for confirmation
5. Click confirmation link in email

### Verify GPG Key

```bash
# After confirmation, verify on Launchpad:
# Go to: https://launchpad.net/~your-username

# Should show your GPG key fingerprint
```

## Step 4: Create PPA

1. Go to https://launchpad.net/~your-username/+activate-ppa
2. Fill in:

**PPA Details:**
- **URL:** `papagaio`
  - Final PPA: `ppa:your-username/papagaio`
- **Display name:** `Papagaio`
- **Description:**
  ```
  Voice-to-text daemon for Linux using Whisper speech recognition.

  Install:
    sudo add-apt-repository ppa:your-username/papagaio
    sudo apt update
    sudo apt install papagaio

  Features:
  - Global hotkey support (Ctrl+Alt+V)
  - 100% local processing (privacy-first)
  - Voice Activity Detection
  - Bilingual interface (English/Portuguese)
  - Manual control (stop/cancel)

  Project: https://launchpad.net/papagaio
  GitHub: https://github.com/alexandrehsantos/papagaio
  ```

3. Click "Activate"

## Step 5: Configure dput

Create/edit `~/.dput.cf`:

```ini
[ppa:your-username/papagaio]
fqdn = ppa.launchpad.net
method = ftp
incoming = ~your-username/ubuntu/papagaio/
login = anonymous
allow_unsigned_uploads = 0
```

## Step 6: Build and Upload First Package

```bash
cd /path/to/papagaio

# Build source package
debuild -S -sa

# Upload to PPA
dput ppa:your-username/papagaio ../papagaio_1.1.0-1ubuntu1_source.changes
```

Or use the automated script:

```bash
./packaging/build-ppa.sh ppa:your-username/papagaio
```

## Step 7: Monitor Build

1. Go to https://launchpad.net/~your-username/+archive/ubuntu/papagaio/+packages
2. Wait for build to complete (10-30 minutes)
3. Builds for: amd64, i386, arm64, armhf

Build status:
- **Pending** - Waiting in queue
- **Building** - Currently building
- **Successfully built** - Ready for use
- **Failed to build** - Check build log

## Step 8: Test Installation

After build succeeds:

```bash
# Add PPA
sudo add-apt-repository ppa:your-username/papagaio
sudo apt update

# Install
sudo apt install papagaio

# Test
papagaio-ctl help
```

## Quick Reference

**Your URLs after setup:**
- Project: `https://launchpad.net/papagaio`
- PPA: `https://launchpad.net/~your-username/+archive/ubuntu/papagaio`
- Profile: `https://launchpad.net/~your-username`

**Installation command for users:**
```bash
sudo add-apt-repository ppa:your-username/papagaio
sudo apt install papagaio
```

## Troubleshooting

### Email Not Verified
- Check spam folder
- Resend verification: https://launchpad.net/~/+editemails

### GPG Key Not Accepted
- Email in GPG key must match Launchpad email
- Regenerate key with correct email if needed

### Upload Rejected
Common reasons:
- GPG key not uploaded/confirmed
- Version already exists (increment version)
- Missing fields in debian/changelog

### Build Failed
- Check build log on Launchpad
- Common issues: missing dependencies, Python errors
- Update debian/control with correct dependencies

## Next Steps

After successful PPA setup:

1. Update README.md with your PPA:
   ```bash
   sudo add-apt-repository ppa:your-username/papagaio
   ```

2. Announce on:
   - GitHub releases
   - Project website
   - Social media

3. For updates:
   - Update debian/changelog
   - Rebuild and upload
   - Launchpad auto-updates users

## Resources

- Launchpad Help: https://help.launchpad.net/
- PPA Guide: https://help.launchpad.net/Packaging/PPA
- Ubuntu Packaging: https://packaging.ubuntu.com/
- GPG Guide: https://help.ubuntu.com/community/GnuPrivacyGuardHowto
