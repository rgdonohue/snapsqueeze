# SnapSqueeze Installation Guide

## System Requirements

- **macOS**: 12.0 (Monterey) or later
- **Python**: 3.8+ (automatically detected)
- **Architecture**: Intel and Apple Silicon supported
- **Permissions**: Screen Recording access required

## Quick Installation

### Option 1: Download Release (Recommended)

1. **Download the latest release**
   - Go to [Releases](https://github.com/username/snapsqueeze/releases)
   - Download `SnapSqueeze-v1.0.0.dmg`

2. **Install the application**
   ```bash
   # Verify download integrity (optional)
   shasum -a 256 SnapSqueeze-v1.0.0.dmg
   ```
   - Double-click the DMG file
   - Drag SnapSqueeze.app to Applications folder
   - Eject the DMG

3. **First launch**
   - Open SnapSqueeze from Applications
   - Grant screen recording permissions when prompted
   - Look for the SnapSqueeze icon in your menu bar

### Option 2: Build from Source

1. **Clone the repository**
   ```bash
   git clone https://github.com/username/snapsqueeze.git
   cd snapsqueeze
   ```

2. **Set up Python environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python -m ui.menu_bar_app
   ```

## Initial Setup

### 1. Grant Permissions

SnapSqueeze requires screen recording permissions to capture screenshots:

1. **When prompted**: Click "Grant Permission" in the dialog
2. **Manual setup**: 
   - Open System Preferences → Security & Privacy → Privacy
   - Select "Screen Recording" from the left sidebar
   - Click the lock icon and enter your password
   - Check the box next to SnapSqueeze

### 2. Configure Hotkey

The default hotkey is `Cmd+Option+4`. To customize:

1. Click the SnapSqueeze menu bar icon
2. Select "Preferences"
3. Choose your preferred key combination
4. Click "Save"

### 3. Test Installation

1. Press `Cmd+Option+4` (or your custom hotkey)
2. Select a region of your screen
3. Check that the compressed image is in your clipboard
4. Paste into any application with `Cmd+V`

## Uninstallation

### Complete Removal

1. **Quit SnapSqueeze**
   - Click menu bar icon → Quit
   - Or force quit if unresponsive

2. **Remove application**
   ```bash
   # Move to Trash
   mv /Applications/SnapSqueeze.app ~/.Trash/
   
   # Or use Finder
   # Drag SnapSqueeze.app from Applications to Trash
   ```

3. **Remove preferences** (optional)
   ```bash
   rm -rf ~/Library/Preferences/com.snapsqueeze.*
   rm -rf ~/Library/Application\ Support/SnapSqueeze/
   ```

4. **Revoke permissions** (optional)
   - System Preferences → Security & Privacy → Privacy → Screen Recording
   - Uncheck SnapSqueeze

## Troubleshooting

### Common Issues

#### 1. "SnapSqueeze can't be opened because it's from an unidentified developer"

**Solution A: Allow in System Preferences**
1. Right-click SnapSqueeze.app → Open
2. Click "Open" in the security dialog
3. Enter admin password if prompted

**Solution B: Command Line**
```bash
sudo xattr -r -d com.apple.quarantine /Applications/SnapSqueeze.app
```

#### 2. Hotkey doesn't work

**Possible causes:**
- Another app is using the same hotkey
- SnapSqueeze doesn't have screen recording permissions
- The app crashed silently

**Solutions:**
1. **Check permissions**: System Preferences → Security & Privacy → Privacy → Screen Recording
2. **Change hotkey**: SnapSqueeze menu → Preferences → Hotkey
3. **Restart app**: Quit and relaunch SnapSqueeze
4. **Check Activity Monitor**: Ensure SnapSqueeze is running

#### 3. Screenshots aren't being compressed

**Symptoms:**
- Images are same size as before
- No compression notification appears

**Solutions:**
1. **Check image format**: PNG files may not compress much
2. **Try larger images**: Small images have minimal compression benefit
3. **Check logs**: 
   ```bash
   tail -f ~/Library/Logs/SnapSqueeze/app.log
   ```

#### 4. Python/dependency errors

**Error**: `ModuleNotFoundError: No module named 'PIL'`

**Solution**: Reinstall dependencies
```bash
cd /Applications/SnapSqueeze.app/Contents/Resources
pip3 install -r requirements.txt --user
```

#### 5. Menu bar icon missing

**Possible causes:**
- App crashed during startup
- Menu bar is hidden
- Multiple instances running

**Solutions:**
1. **Restart**: Force quit and relaunch
2. **Check Activity Monitor**: Kill duplicate processes
3. **Reset preferences**:
   ```bash
   rm ~/Library/Preferences/com.snapsqueeze.plist
   ```

### Advanced Troubleshooting

#### Enable Debug Logging

1. **Create debug configuration**
   ```bash
   mkdir -p ~/Library/Application\ Support/SnapSqueeze
   echo "DEBUG=true" > ~/Library/Application\ Support/SnapSqueeze/config
   ```

2. **View logs**
   ```bash
   tail -f ~/Library/Logs/SnapSqueeze/debug.log
   ```

#### Performance Issues

**Symptoms**: Slow compression, high CPU usage

**Solutions**:
1. **Check available memory**: Activity Monitor → Memory
2. **Reduce image quality**: Preferences → Compression → Quality
3. **Close other apps**: Free up system resources
4. **Restart macOS**: Clear system caches

#### Network/Firewall Issues

SnapSqueeze works entirely offline, but some firewalls may block Python:

1. **Allow Python in firewall**: System Preferences → Security & Privacy → Firewall → Options
2. **Add SnapSqueeze exception**: Firewall settings → Allow SnapSqueeze

## Development Setup

### For Contributors

1. **Clone and setup**
   ```bash
   git clone https://github.com/username/snapsqueeze.git
   cd snapsqueeze
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

2. **Run tests**
   ```bash
   python -m pytest tests/ -v
   ```

3. **Run from source**
   ```bash
   python -m ui.menu_bar_app
   ```

### Building Distribution

```bash
# Build DMG
./scripts/build_dmg.sh

# Test the built DMG
open dist/SnapSqueeze-1.0.0.dmg
```

## Support

### Getting Help

1. **Check this documentation**: Common issues are covered above
2. **Search existing issues**: [GitHub Issues](https://github.com/username/snapsqueeze/issues)
3. **Create new issue**: Use issue templates for bug reports or feature requests

### Reporting Bugs

When reporting bugs, please include:

- macOS version (`sw_vers`)
- Python version (`python3 --version`)
- SnapSqueeze version (menu bar → About)
- Steps to reproduce
- Error messages or logs
- Screenshots (if applicable)

### Privacy

SnapSqueeze processes all images locally on your machine:
- No data is transmitted to external servers
- No analytics or telemetry collected
- Open source code available for audit
- Screen recording permission used only for screenshot capture

## Version History

- **v1.0.0**: Initial release
  - Basic screenshot compression
  - Menu bar interface
  - Configurable hotkeys
  - DMG distribution