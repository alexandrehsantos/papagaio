# Contributing to Whisper Voice Daemon

Thank you for considering contributing to Whisper Voice Daemon! This document provides guidelines and instructions for contributing.

## 🤝 Code of Conduct

- Be respectful and constructive
- Welcome newcomers and beginners
- Focus on what is best for the community
- Show empathy towards other community members

## 🐛 Reporting Bugs

Before submitting a bug report:

1. **Check existing issues** - Your bug might already be reported
2. **Test with latest version** - Make sure you're using the latest code
3. **Isolate the problem** - Try to reproduce with minimal steps

When submitting a bug:

```markdown
**Description:** Clear description of the bug

**Steps to Reproduce:**
1. Step one
2. Step two
3. ...

**Expected Behavior:** What should happen

**Actual Behavior:** What actually happened

**Environment:**
- OS: Ubuntu 22.04
- Python version: 3.10
- Whisper model: small
- Installation method: pip / git clone

**Logs:**
```
Paste relevant logs from `papagaio-ctl logs`
```
```

## 💡 Suggesting Features

Feature suggestions are welcome! Please:

1. **Check existing feature requests** first
2. **Describe the problem** your feature would solve
3. **Explain your proposed solution**
4. **Consider alternatives** you've thought about

## 🔧 Development Setup

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/papagaio.git
cd papagaio

# Install dependencies
pip3 install -r requirements.txt

# Run in debug mode
python3 papagaio.py -m small
```

## 📝 Code Guidelines

### Python Style

- Follow **PEP 8** style guide
- Use **type hints** for function signatures
- Write **docstrings** for classes and functions
- Keep functions **focused** (single responsibility)

### Example

```python
def transcribe(self, audio_file: str) -> str:
    """
    Transcribe audio file to text using Whisper.

    Args:
        audio_file: Path to WAV audio file

    Returns:
        Transcribed text as string

    Raises:
        FileNotFoundError: If audio file doesn't exist
    """
    # Implementation
```

### Code Structure

- **One class per file** when possible
- **Descriptive names** that reveal intent
- **No magic numbers** - use named constants
- **Handle errors gracefully** with try/except

### Clean Code Principles

This project follows:

- **SOLID Principles**
- **Object Calisthenics** (one level of indentation, small methods)
- **Self-documenting code** (minimize comments, use clear names)

## 🧪 Testing

Before submitting:

1. **Test manually** - Run the daemon and verify functionality
2. **Test edge cases** - Empty input, long recordings, etc.
3. **Test on clean install** - Ensure dependencies are correct

Future: We plan to add automated tests

## 📤 Submitting Changes

### Pull Request Process

1. **Create a branch** for your feature/fix
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, documented code
   - Follow style guidelines
   - Keep commits atomic and focused

3. **Commit with clear messages**
   ```bash
   git commit -m "feat: Add support for custom silence threshold"
   git commit -m "fix: Handle missing xdotool gracefully"
   ```

4. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Open a Pull Request**
   - Describe what your PR does
   - Reference any related issues
   - Include screenshots/demos if relevant

### Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): subject

body (optional)

footer (optional)
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `perf:` Performance improvements
- `test:` Adding tests
- `chore:` Maintenance tasks

**Examples:**
```
feat: Add VAD sensitivity configuration option
fix: Prevent daemon crash on missing audio device
docs: Update installation instructions for Fedora
refactor: Extract audio recording to separate class
```

## 🎯 Good First Issues

Looking to contribute but not sure where to start? Look for issues tagged:

- `good first issue` - Easy tasks for beginners
- `help wanted` - Community help appreciated
- `documentation` - Improve docs

## 💬 Questions?

- **GitHub Discussions** - Ask questions and discuss ideas
- **Issues** - Report bugs and request features

## 🙏 Thank You!

Every contribution matters, whether it's:

- 🐛 Reporting a bug
- 📝 Improving documentation
- 💡 Suggesting a feature
- 🔧 Submitting code
- ⭐ Starring the repo
- 📢 Spreading the word

Your time and effort make this project better for everyone!
