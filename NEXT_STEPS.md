# Next Steps - Papagaio Publication

## Priority 1: Register on Launchpad

**Action:** Register project on Launchpad for PPA distribution

**Link:** https://launchpad.net/projects/+new

**Steps:**
1. Go to https://launchpad.net/projects/+new
2. Fill in:
   - **URL:** `papagaio`
   - **Display Name:** `Papagaio`
   - **Summary:** `Voice-to-text daemon for Linux - Papagaio repeats what you say`
   - **Description:** See docs/LAUNCHPAD-SETUP.md
3. Register project

**Documentation:** docs/LAUNCHPAD-SETUP.md

## Priority 2: Publish to PyPI

**Action:** Make package available via `pip install papagaio`

**Command:**
```bash
cd /path/to/papagaio
./packaging/build-pypi.sh prod
```

**Prerequisites:**
- Create account: https://pypi.org/account/register/
- Test first: `./packaging/build-pypi.sh test`

**Documentation:** docs/PUBLISHING.md

## Priority 3: Create Ubuntu PPA

**Action:** Enable `sudo apt install papagaio`

**Prerequisites:**
1. Launchpad account (Priority 1)
2. GPG key configured
3. PPA created

**Command:**
```bash
./packaging/build-ppa.sh ppa:alexandrehsantos/papagaio
```

**Documentation:** docs/PPA-GUIDE.md

## Priority 4: Publish to AUR (Arch Linux)

**Action:** Enable `yay -S papagaio` for Arch users

**Steps:**
1. Create AUR account: https://aur.archlinux.org/register/
2. Clone AUR repo:
   ```bash
   git clone ssh://aur@aur.archlinux.org/papagaio.git aur-papagaio
   ```
3. Copy and update PKGBUILD:
   ```bash
   cp packaging/PKGBUILD aur-papagaio/
   cd aur-papagaio
   updpkgsums
   makepkg --printsrcinfo > .SRCINFO
   git add PKGBUILD .SRCINFO
   git commit -m "Initial upload: papagaio 1.1.0"
   git push
   ```

**Documentation:** docs/PUBLISHING.md

## Priority 5: Update Release Notes

**Action:** Create v1.2.0 release with new name

**Command:**
```bash
gh release create v1.2.0 --title "v1.2.0 - Renamed to Papagaio" --notes "
# Papagaio v1.2.0

Project renamed from whisper-voice-daemon to **Papagaio** (Portuguese for parrot).

## What's New
- New name: Papagaio - Like a parrot, repeats what you say
- Shorter installation: \`pip install papagaio\`
- Brazilian identity
- All features maintained

## Installation
\`\`\`bash
pip install papagaio
sudo apt install papagaio  # After PPA
\`\`\`

## Usage
\`\`\`bash
papagaio-ctl start
\`\`\`
"
```

## Checklist

- [ ] Register on Launchpad: https://launchpad.net/projects/+new
- [ ] Configure GPG key for PPA
- [ ] Create PyPI account
- [ ] Publish to PyPI: `./packaging/build-pypi.sh prod`
- [ ] Create PPA on Launchpad
- [ ] Upload to PPA: `./packaging/build-ppa.sh`
- [ ] Create AUR account
- [ ] Publish to AUR
- [ ] Create GitHub release v1.2.0
- [ ] Update badges in README.md
- [ ] Announce on social media

## Quick Links

- **Launchpad Register:** https://launchpad.net/projects/+new
- **PyPI Register:** https://pypi.org/account/register/
- **AUR Register:** https://aur.archlinux.org/register/
- **Documentation:** docs/PUBLISHING.md
- **PPA Guide:** docs/PPA-GUIDE.md
- **Launchpad Setup:** docs/LAUNCHPAD-SETUP.md
