# SnapSqueeze Troubleshooting Guide

## Quick Diagnostics

### Health Check Script

Run this command to check your SnapSqueeze installation:

```bash
python3 -c "
import sys
print(f'Python version: {sys.version}')

try:
    from PIL import Image
    print('✅ PIL/Pillow: Available')
except ImportError:
    print('❌ PIL/Pillow: Missing')

try:
    import rumps
    print('✅ rumps: Available')
except ImportError:
    print('❌ rumps: Missing')

try:
    import psutil
    memory = psutil.virtual_memory()
    print(f'✅ psutil: Available (Memory: {memory.available // 1024 // 1024} MB free)')
except ImportError:
    print('❌ psutil: Missing')

import os
if os.path.exists('/Applications/SnapSqueeze.app'):
    print('✅ App: Installed in Applications')
else:
    print('❌ App: Not found in Applications')
"
```

## Common Problems & Solutions

### 1. Permission Issues

#### Problem: "SnapSqueeze requires screen recording permission"

**Symptoms:**
- Permission dialog keeps appearing
- Screenshots are black/empty
- Error notifications about permissions

**Solution:**
1. **Manual permission grant:**
   ```
   System Preferences → Security & Privacy → Privacy → Screen Recording
   ```
   - Unlock with admin password
   - Check the box next to SnapSqueeze
   - Restart SnapSqueeze

2. **Force permission reset:**
   ```bash
   sudo tccutil reset ScreenCapture com.snapsqueeze.app
   ```
   - Restart SnapSqueeze
   - Grant permission when prompted

3. **Check for multiple entries:**
   - Remove duplicate SnapSqueeze entries in Screen Recording
   - Keep only the one from /Applications/

#### Problem: "Can't open SnapSqueeze - unidentified developer"

**Solution A (Recommended):**
1. Right-click SnapSqueeze.app
2. Select "Open"
3. Click "Open" in the security dialog

**Solution B (Command line):**
```bash
sudo xattr -r -d com.apple.quarantine /Applications/SnapSqueeze.app
```

**Solution C (System wide):**
```bash
sudo spctl --master-disable  # Disables Gatekeeper (not recommended)
```

### 2. Hotkey Problems

#### Problem: Hotkey `Cmd+Option+4` doesn't work

**Check for conflicts:**
```bash
# List all global hotkeys
defaults read com.apple.symbolichotkeys AppleSymbolicHotKeys
```

**Solutions:**
1. **Change SnapSqueeze hotkey:**
   - Menu bar icon → Preferences → Hotkey
   - Try `Cmd+Shift+4` or `Cmd+Option+3`

2. **Check conflicting apps:**
   - CleanMyMac, Alfred, Raycast, etc.
   - Disable their screenshot hotkeys

3. **System screenshot shortcuts:**
   ```
   System Preferences → Keyboard → Shortcuts → Screenshots
   ```
   - Disable conflicting system shortcuts

4. **Reset hotkey system:**
   ```bash
   killall SystemUIServer
   ```

#### Problem: Hotkey works but nothing happens

**Diagnostics:**
```bash
# Check if SnapSqueeze is running
ps aux | grep -i snapsqueeze

# Check logs
tail -f ~/Library/Logs/SnapSqueeze/app.log
```

**Solutions:**
1. **Restart SnapSqueeze:**
   - Menu bar icon → Quit
   - Relaunch from Applications

2. **Check permissions again:**
   - Screen Recording permission might have been revoked
   - Accessibility permission might be needed

### 3. Compression Issues

#### Problem: Images aren't getting compressed

**Symptoms:**
- File sizes remain the same
- No compression notification
- Images paste at original size

**Diagnostics:**
```bash
# Test compression manually
python3 -c "
from core.image_compressor import ImageCompressor
import os

# Create test data
test_data = b'test image data'
compressor = ImageCompressor()

try:
    result = compressor.compress(test_data)
    print('✅ Compression working')
except Exception as e:
    print(f'❌ Compression failed: {e}')
"
```

**Solutions:**
1. **Check image formats:**
   - JPEG files may already be compressed
   - PNG files with few colors won't compress much
   - Try with larger, more complex images

2. **Memory issues:**
   ```bash
   # Check available memory
   vm_stat | head -n 10
   ```
   - Close other applications
   - Restart if memory is low

3. **Reset compression settings:**
   ```bash
   rm ~/Library/Preferences/com.snapsqueeze.compression.plist
   ```

#### Problem: "Memory constraint" errors

**Symptoms:**
- Error notifications about memory
- Large images fail to process
- System becomes slow during compression

**Solutions:**
1. **Increase available memory:**
   - Close unnecessary applications
   - Restart macOS to clear caches

2. **Reduce image size:**
   - Use smaller capture regions
   - Lower resolution displays if possible

3. **Adjust compression settings:**
   - Menu bar → Preferences → Compression
   - Lower quality setting (50% → 25%)
   - Change format (PNG → JPEG)

### 4. Clipboard Issues

#### Problem: Compressed images don't paste

**Symptoms:**
- Nothing pastes after capture
- Old clipboard content remains
- Applications don't see the image

**Diagnostics:**
```bash
# Check clipboard contents
osascript -e 'the clipboard as string'
osascript -e 'clipboard info'
```

**Solutions:**
1. **Check clipboard format:**
   - Some apps only accept specific formats
   - Try pasting in Preview or TextEdit first

2. **Clipboard conflicts:**
   - Quit clipboard managers (Paste, Copied, etc.)
   - Wait a few seconds after capture before pasting

3. **Reset clipboard:**
   ```bash
   pbcopy < /dev/null  # Clear clipboard
   ```

### 5. Performance Issues

#### Problem: Slow compression/capture

**Symptoms:**
- Long delay between capture and completion
- High CPU usage
- System becomes unresponsive

**Diagnostics:**
```bash
# Monitor SnapSqueeze performance
top -pid $(pgrep -f snapsqueeze)

# Check system load
uptime
```

**Solutions:**
1. **Optimize capture size:**
   - Use smaller regions when possible
   - Avoid capturing entire 4K/5K displays

2. **System optimization:**
   ```bash
   # Clear system caches
   sudo purge
   
   # Reset launch services
   /System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -kill -r -domain local -domain system -domain user
   ```

3. **Reduce quality settings:**
   - Menu bar → Preferences → Compression
   - Lower scale factor (50% → 25%)

### 6. Menu Bar Issues

#### Problem: Menu bar icon missing

**Symptoms:**
- SnapSqueeze appears to be running but no icon
- Can't access preferences
- Hotkey might still work

**Solutions:**
1. **Reset menu bar:**
   ```bash
   killall SystemUIServer
   ```

2. **Check hidden icons:**
   - Click and drag the menu bar to reveal hidden icons
   - Some menu bar managers hide icons

3. **Restart with clean preferences:**
   ```bash
   rm ~/Library/Preferences/com.snapsqueeze.menubar.plist
   ```

4. **Force restart:**
   ```bash
   killall python3
   # Then relaunch SnapSqueeze
   ```

### 7. Installation Issues

#### Problem: DMG won't open or mount

**Symptoms:**
- "Image not recognized" error
- DMG appears corrupted
- macOS won't mount the file

**Solutions:**
1. **Verify download integrity:**
   ```bash
   shasum -a 256 SnapSqueeze-v1.0.0.dmg
   # Compare with published SHA256 hash
   ```

2. **Re-download:**
   - Download may have been corrupted
   - Try different browser or network

3. **Manual extraction:**
   ```bash
   hdiutil attach SnapSqueeze-v1.0.0.dmg -readonly
   ```

#### Problem: App won't launch after installation

**Check installation location:**
```bash
ls -la /Applications/SnapSqueeze.app
```

**Check permissions:**
```bash
ls -la /Applications/SnapSqueeze.app/Contents/MacOS/SnapSqueeze
chmod +x /Applications/SnapSqueeze.app/Contents/MacOS/SnapSqueeze
```

**Check dependencies:**
```bash
/Applications/SnapSqueeze.app/Contents/MacOS/SnapSqueeze
# Look for Python import errors
```

## Advanced Diagnostics

### Log Analysis

**Enable verbose logging:**
```bash
mkdir -p ~/Library/Application\ Support/SnapSqueeze
echo "LOG_LEVEL=DEBUG" > ~/Library/Application\ Support/SnapSqueeze/.env
```

**View real-time logs:**
```bash
tail -f ~/Library/Logs/SnapSqueeze/app.log
```

**Common log patterns:**
- `Permission denied`: Permission issues
- `Memory error`: Insufficient RAM
- `Import error`: Missing Python packages
- `Hotkey conflict`: Another app using same key

### System Information

**Collect system info for bug reports:**
```bash
echo "=== System Information ===" > snapsqueeze-debug.txt
sw_vers >> snapsqueeze-debug.txt
echo "" >> snapsqueeze-debug.txt

echo "=== Python Information ===" >> snapsqueeze-debug.txt
python3 --version >> snapsqueeze-debug.txt
python3 -c "import sys; print(sys.path)" >> snapsqueeze-debug.txt
echo "" >> snapsqueeze-debug.txt

echo "=== Memory Information ===" >> snapsqueeze-debug.txt
vm_stat >> snapsqueeze-debug.txt
echo "" >> snapsqueeze-debug.txt

echo "=== SnapSqueeze Process ===" >> snapsqueeze-debug.txt
ps aux | grep -i snapsqueeze >> snapsqueeze-debug.txt
```

### Clean Reinstall

If all else fails, perform a clean reinstall:

1. **Complete removal:**
   ```bash
   # Quit SnapSqueeze
   killall python3
   
   # Remove app
   rm -rf /Applications/SnapSqueeze.app
   
   # Remove preferences
   rm -rf ~/Library/Preferences/com.snapsqueeze.*
   rm -rf ~/Library/Application\ Support/SnapSqueeze/
   rm -rf ~/Library/Logs/SnapSqueeze/
   
   # Reset permissions
   sudo tccutil reset ScreenCapture
   sudo tccutil reset Accessibility
   ```

2. **Fresh installation:**
   - Download latest DMG
   - Install normally
   - Grant permissions when prompted

## Getting Additional Help

### Before Reporting Issues

1. **Search existing issues:** [GitHub Issues](https://github.com/username/snapsqueeze/issues)
2. **Try solutions above:** Most problems have known fixes
3. **Collect debug information:** Use system info script above

### Bug Report Checklist

Include the following in bug reports:

- [ ] macOS version (`sw_vers`)
- [ ] Python version (`python3 --version`)
- [ ] SnapSqueeze version (About dialog)
- [ ] Specific steps to reproduce
- [ ] Expected vs actual behavior
- [ ] Error messages or logs
- [ ] Screenshots (if applicable)
- [ ] System information (use script above)

### Performance Reports

For performance issues, include:

- [ ] Activity Monitor screenshot during issue
- [ ] Memory usage (`vm_stat`)
- [ ] CPU usage (`top`)
- [ ] Disk space (`df -h`)
- [ ] Image sizes being processed
- [ ] Time measurements

### Emergency Recovery

If SnapSqueeze is completely broken:

```bash
# Nuclear option - remove everything
sudo rm -rf /Applications/SnapSqueeze.app
rm -rf ~/Library/Preferences/com.snapsqueeze.*
rm -rf ~/Library/Application\ Support/SnapSqueeze/
sudo tccutil reset All
```

Then reinstall from scratch.

Remember: SnapSqueeze processes everything locally, so no data is lost when reinstalling.