# SnapSqueeze

<div align="center">
  <img src="assets/icon_128x128.png" alt="SnapSqueeze Icon" width="128" height="128">
  
  **A clipboard-first screenshot compressor for macOS**
  
  *Shrink Your Shots. Boost Your Flow.*

  [![macOS](https://img.shields.io/badge/macOS-10.15+-blue.svg)](https://www.apple.com/macos/)
  [![Python](https://img.shields.io/badge/Python-3.9+-green.svg)](https://www.python.org/)
  [![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
  [![GitHub Release](https://img.shields.io/github/v/release/username/snapsqueeze.svg)](https://github.com/username/snapsqueeze/releases)
</div>

## 🚀 What is SnapSqueeze?

SnapSqueeze revolutionizes your screenshot workflow by **automatically compressing and copying screenshots to your clipboard**. No more manually resizing images in Preview before sharing them in Slack, Jira, or GitHub!

### The Problem
- Default macOS screenshots are **huge** (often 2-10MB)
- Sharing large screenshots slows down team communication
- Manual resizing in Preview/Photoshop breaks your flow
- File attachments clutter your desktop

### The Solution
- **One hotkey** (`Cmd+Option+4`) captures, compresses, and copies to clipboard
- **Instant sharing** - just paste anywhere with `Cmd+V`
- **Smart compression** - 50-80% size reduction while maintaining quality
- **No files** - everything goes straight to clipboard

## ✨ Features

### 🎯 **Core Functionality**
- **Region Capture**: Select any area of your screen with precision
- **Smart Compression**: Automatic 50% scaling with quality optimization
- **Instant Clipboard**: No temp files - straight to clipboard
- **Menu Bar App**: Lightweight, always-accessible interface

### ⚡ **Power User Features**
- **Global Hotkey**: `Cmd+Option+4` for lightning-fast capture
- **Configurable Compression**: 25%, 50%, or 75% scaling options
- **Multiple Formats**: PNG (default), JPEG, WebP support
- **Memory Efficient**: Advanced optimization for large screenshots

### 🛡️ **Privacy & Performance**
- **100% Local Processing**: No cloud uploads, no telemetry
- **Lightning Fast**: Sub-second compression for typical screenshots
- **Error Recovery**: Graceful handling of edge cases
- **Resource Conscious**: Minimal system impact

## 📸 Perfect For

| Use Case | Before | After |
|----------|--------|--------|
| **Slack Messages** | 3MB screenshot → manual resize → upload | `Cmd+Option+4` → `Cmd+V` → done! |
| **Jira Bug Reports** | Multiple steps, large files | One hotkey, perfect size |
| **GitHub Issues** | Desktop clutter, slow uploads | Instant paste, fast loading |
| **Design Feedback** | Email attachments, file sharing | Direct paste in tools |
| **Documentation** | Heavy images in wikis | Optimized screenshots |

## 🚀 Quick Start

### Installation

1. **Download** the latest release from [GitHub Releases](https://github.com/username/snapsqueeze/releases)
2. **Open** the downloaded DMG file
3. **Drag** SnapSqueeze to your Applications folder
4. **Launch** SnapSqueeze from Applications or Spotlight
5. **Grant** screen recording permission when prompted

### First Capture

1. **Press** `Cmd+Option+4` (or click the menu bar icon → "Capture & Compress")
2. **Select** the region you want to capture by dragging
3. **Release** to capture - your compressed screenshot is now in clipboard!
4. **Paste** anywhere with `Cmd+V`

That's it! Your screenshot is automatically compressed and ready to share.

## 🎛️ Usage

### Hotkey Capture
```
Cmd+Option+4 → Select region → Release → Paste with Cmd+V
```

### Menu Bar Options
- **Capture & Compress**: Manual trigger for screenshot capture
- **Preferences**: Adjust compression level (25%, 50%, 75%)
- **Statistics**: View your compression savings
- **About**: Version and app information

### Compression Settings
- **25% (High Compression)**: Maximum size reduction, good for simple UI
- **50% (Default)**: Perfect balance of size and quality
- **75% (High Quality)**: Minimal compression, preserves detail

## 📊 Performance

### Compression Results
- **UI Screenshots**: 40-60% size reduction
- **Text Documents**: 70-85% size reduction  
- **Mixed Content**: 50-70% size reduction
- **Processing Speed**: < 1 second for typical screenshots

### System Requirements
- **macOS**: 10.15 (Catalina) or later
- **Architecture**: Intel and Apple Silicon supported
- **Memory**: 100MB available recommended
- **Permissions**: Screen Recording access required

## 🔧 Advanced Usage

### Custom Formats
```python
# Change output format in Preferences
PNG (default) - Best for UI screenshots with transparency
JPEG - Smaller files, good for photos
WebP - Modern format with excellent compression
```

### Workflow Integration
- **Slack**: Paste directly in messages
- **Jira**: Add to issue descriptions instantly  
- **Notion**: Embed in pages without file uploads
- **GitHub**: Include in issue comments
- **Email**: Attach compressed images

### Keyboard Shortcuts
| Action | Shortcut |
|--------|----------|
| Capture Region | `Cmd+Option+4` |
| Open Preferences | Menu Bar → Preferences |
| View Statistics | Menu Bar → Statistics |
| Quit Application | Menu Bar → Quit |

## 🛠️ Development

### Building from Source

```bash
# Clone the repository
git clone https://github.com/username/snapsqueeze.git
cd snapsqueeze

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_compressor.py -v
python -m pytest tests/test_integration.py -v
python -m pytest tests/test_performance.py -v
```

### Project Structure
```
snapsqueeze/
├── core/               # Image compression engine
├── system/             # macOS system integration
├── ui/                 # Menu bar app and interface
├── tests/              # Comprehensive test suite
├── assets/             # App icons and resources
└── main.py            # Application entry point
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Quick Contributions
- 🐛 **Report bugs** via [GitHub Issues](https://github.com/username/snapsqueeze/issues)
- 💡 **Suggest features** for future releases
- 📖 **Improve documentation** and examples
- 🌟 **Star the repository** to show support

### Development Contributions
1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines
- Follow existing code style and patterns
- Add tests for new functionality
- Update documentation for user-facing changes
- Ensure all tests pass before submitting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

### Built With
- **[Pillow](https://python-pillow.org/)** - Image processing engine
- **[rumps](https://github.com/jaredks/rumps)** - Menu bar application framework
- **[PyObjC](https://pythonhosted.org/pyobjc/)** - macOS system integration
- **[psutil](https://github.com/giampaolo/psutil)** - System monitoring

### Inspiration
- **macOS Screenshot Tools** - Building on the excellent foundation
- **Compression Tools** - Learning from the best in image optimization
- **Menu Bar Apps** - Following macOS design principles

## 📈 Roadmap

### v1.1 - Enhanced Features
- [ ] Window capture mode
- [ ] Annotation tools (arrows, text)
- [ ] Custom hotkey configuration
- [ ] Batch processing

### v1.2 - Advanced Compression
- [ ] Smart format selection
- [ ] Progressive compression
- [ ] Quality presets for different use cases
- [ ] Real-time compression preview

### v2.0 - Professional Features
- [ ] Team sharing workflows
- [ ] Cloud storage integration
- [ ] Advanced editing tools
- [ ] Workflow automation

## 💬 Support

### Getting Help
- 📖 **Documentation**: Check this README and [Wiki](https://github.com/username/snapsqueeze/wiki)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/username/snapsqueeze/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/username/snapsqueeze/discussions)
- 📧 **Contact**: [hello@snapsqueeze.app](mailto:hello@snapsqueeze.app)

### FAQ

**Q: Why does macOS ask for screen recording permission?**
A: SnapSqueeze needs this permission to capture screenshots. This is standard for all screenshot apps on macOS.

**Q: Is my data sent to any servers?**
A: No! SnapSqueeze processes everything locally on your Mac. No data is ever sent to external servers.

**Q: Can I change the compression level?**
A: Yes! Use the Preferences menu to choose between 25%, 50%, or 75% scaling.

**Q: Does it work with multiple monitors?**
A: Yes! SnapSqueeze supports multi-monitor setups with different resolutions.

**Q: How do I uninstall SnapSqueeze?**
A: Simply drag the app from Applications to Trash, then restart to clear the menu bar icon.

---

<div align="center">
  
**Made with ❤️ for the macOS community**

[Download](https://github.com/username/snapsqueeze/releases) • [Documentation](https://github.com/username/snapsqueeze/wiki) • [Support](https://github.com/username/snapsqueeze/issues)

*Shrink Your Shots. Boost Your Flow.*

</div>