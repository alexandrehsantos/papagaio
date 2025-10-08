# Publishing Guide

This guide explains how to publish Whisper Voice Daemon to various package repositories.

## Package Distribution Methods

### 1. PyPI (Python Package Index)

Recommended as the first distribution method.

- Works on all Linux distributions
- Installation: `pip install whisper-voice-daemon`
- Automatic dependency management
- No approval required

1. **Create PyPI account:**
   - Production: https://pypi.org/account/register/
   - Test: https://test.pypi.org/account/register/

2. **Build package:**
   ```bash
   make build-pypi
   # or
   ./packaging/build-pypi.sh
   ```

3. **Test upload (TestPyPI):**
   ```bash
   ./packaging/build-pypi.sh test
   ```

4. **Test installation:**
   ```bash
   pip install --index-url https://test.pypi.org/simple/ whisper-voice-daemon
   ```

5. **Production upload:**
   ```bash
   ./packaging/build-pypi.sh prod
   ```

**Users can install:**
```bash
pip install whisper-voice-daemon
```

---

### 2. AUR (Arch User Repository)

- Popular among Arch/Manjaro users
- Community-maintained after initial upload
- Easy updates


1. **Create AUR account:**
   - https://aur.archlinux.org/register/

2. **Setup SSH key:**
   ```bash
   ssh-keygen -t ed25519 -C "your-email@example.com"
   # Upload public key to AUR account
   ```

3. **Clone AUR repository:**
   ```bash
   git clone ssh://aur@aur.archlinux.org/whisper-voice-daemon.git aur-repo
   cd aur-repo
   ```

4. **Copy PKGBUILD:**
   ```bash
   cp ../packaging/PKGBUILD .
   ```

5. **Generate checksums:**
   ```bash
   updpkgsums
   makepkg --printsrcinfo > .SRCINFO
   ```

6. **Push to AUR:**
   ```bash
   git add PKGBUILD .SRCINFO
   git commit -m "Initial upload: whisper-voice-daemon 1.0.1"
   git push
   ```

**Users can install:**
```bash
yay -S whisper-voice-daemon
# or
paru -S whisper-voice-daemon
```

---

### 3. Ubuntu PPA (Personal Package Archive)

- Native `apt install` support
- Automatic updates via apt
- Popular among Ubuntu/Debian users


1. **Create Launchpad account:**
   - https://launchpad.net/

2. **Create PPA:**
   - Go to: https://launchpad.net/~your-username/+activate-ppa
   - Name: whisper-voice-daemon
   - Description: Voice-to-text daemon for Linux

3. **Setup GPG key:**
   ```bash
   gpg --full-generate-key
   gpg --list-secret-keys --keyid-format LONG
   gpg --armor --export YOUR_KEY_ID | pbcopy
   # Upload to: https://launchpad.net/~your-username/+editpgpkeys
   ```

4. **Build source package:**
   ```bash
   debuild -S -sa
   ```

5. **Upload to PPA:**
   ```bash
   dput ppa:your-username/whisper-voice-daemon ../whisper-voice-daemon_1.0.1-1_source.changes
   ```

6. **Wait for build** (usually 10-30 minutes)

**Users can install:**
```bash
sudo add-apt-repository ppa:your-username/whisper-voice-daemon
sudo apt update
sudo apt install whisper-voice-daemon
```

---

### 4. Debian Package (.deb) - Direct Download

- Works on Debian/Ubuntu without PPA
- Can be hosted on GitHub Releases


1. **Build package:**
   ```bash
   make build-deb
   # or
   ./packaging/build-deb.sh
   ```

2. **Package will be in parent directory:**
   ```
   ../whisper-voice-daemon_1.0.1-1_all.deb
   ```

3. **Upload to GitHub Release:**
   ```bash
   gh release upload v1.0.1 ../whisper-voice-daemon_1.0.1-1_all.deb
   ```

**Users can install:**
```bash
wget https://github.com/alexandrehsantos/whisper-voice-daemon/releases/download/v1.0.1/whisper-voice-daemon_1.0.1-1_all.deb
sudo dpkg -i whisper-voice-daemon_1.0.1-1_all.deb
sudo apt install -f  # Fix dependencies
```

---

### 5. Snapcraft (Universal Package)

- Works on all Linux distributions
- Automatic updates
- Sandboxed


1. **Create snapcraft.yaml:**
   ```yaml
   name: whisper-voice-daemon
   version: '1.0.1'
   summary: Voice-to-text daemon
   description: |
     Voice input system for Linux
   ```

2. **Build and publish:**
   ```bash
   snapcraft
   snapcraft upload whisper-voice-daemon_1.0.1_amd64.snap
   ```

**Users can install:**
```bash
snap install whisper-voice-daemon
```

---

### 6. Flatpak (Universal Package)

- Works on all Linux distributions
- Sandboxed applications


1. **Create Flatpak manifest**
2. **Submit to Flathub**

**Users can install:**
```bash
flatpak install flathub com.github.alexandrehsantos.whisper-voice-daemon
```

---

## 🎯 Recommended Distribution Strategy

**Phase 1: Quick Start (Week 1)**
1. ✅ **PyPI** - Easiest, works everywhere
2. ✅ **GitHub Releases** with .deb file

**Phase 2: Community (Week 2-4)**
3. ✅ **AUR** - Popular with Arch users
4. ✅ **Ubuntu PPA** - Native apt support

**Phase 3: Universal (Month 2+)**
5. ⏳ **Snapcraft** - Universal package
6. ⏳ **Flatpak** - Flathub submission

---

## 📊 Comparison

| Method | Effort | Reach | Auto-Updates | Approval |
|--------|--------|-------|--------------|----------|
| PyPI | ⭐ Easy | 🌍 All | ✅ Yes | ❌ None |
| GitHub .deb | ⭐ Easy | 🐧 Debian/Ubuntu | ❌ Manual | ❌ None |
| AUR | ⭐⭐ Medium | 🎯 Arch | ✅ Yes | ❌ None |
| PPA | ⭐⭐⭐ Hard | 🐧 Ubuntu | ✅ Yes | ⏳ Build time |
| Snap | ⭐⭐ Medium | 🌍 All | ✅ Yes | ✅ Required |
| Flatpak | ⭐⭐⭐ Hard | 🌍 All | ✅ Yes | ✅ Required |

---

## 🚀 Quick Commands

```bash
# Build all packages locally
make build-all

# Test PyPI upload
./packaging/build-pypi.sh test

# Production PyPI upload
./packaging/build-pypi.sh prod

# Build Debian package
make build-deb

# Create GitHub release
make release
```

---

## 📝 Maintenance

**For each new release:**

1. Update version in:
   - `setup.py`
   - `debian/changelog`
   - `packaging/PKGBUILD`
   - `Makefile`

2. Update CHANGELOG.md

3. Build and upload:
   ```bash
   make release
   ./packaging/build-pypi.sh prod
   ```

4. Update AUR:
   ```bash
   cd aur-repo
   # Update PKGBUILD version
   updpkgsums
   makepkg --printsrcinfo > .SRCINFO
   git commit -am "Update to 1.0.2"
   git push
   ```

---

## 🆘 Help

- **PyPI Issues:** https://pypi.org/help/
- **AUR Guidelines:** https://wiki.archlinux.org/title/AUR_submission_guidelines
- **Debian Packaging:** https://www.debian.org/doc/manuals/maint-guide/
- **Launchpad PPA:** https://help.launchpad.net/Packaging/PPA
