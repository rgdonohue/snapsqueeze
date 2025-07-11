# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SnapSqueeze is a macOS screenshot compression tool that captures screen regions and automatically compresses them before placing them on the clipboard. The app runs as a menu bar application and uses the hotkey `Cmd+Option+4` to trigger region capture.

## Architecture

This is a Python-based macOS application with the following key components:

- **Core Engine**: `core/image_compressor.py` - PIL-based image compression with configurable scaling and format support
- **System Integration**: `system/screenshot_handler.py` - macOS screenshot capture using Quartz/AppKit and clipboard integration via NSPasteboard
- **UI Layer**: `ui/menu_bar_app.py` - Menu bar application using the rumps library for simplicity

The app is designed to be stateless with local-only processing (no telemetry or cloud dependencies).

## Key Technical Decisions

- **Python + PyObjC**: Chosen for MVP speed over Swift
- **rumps library**: Simplifies menu bar app implementation
- **PIL (Pillow)**: Image processing and compression
- **NSPasteboard**: Direct clipboard integration without temp files
- **Default 50% scaling**: Balances compression with quality

## Development Commands

Since this is a new project, you'll need to set up the Python environment:

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux

# Install dependencies (to be created)
pip install -r requirements.txt

# Run the application
python -m ui.menu_bar_app

# For development/testing
python -m pytest tests/  # When tests are added
```

## Essential Dependencies

Based on the PRD, the following packages will be required:
- `Pillow` (PIL) - Image processing
- `rumps` - Menu bar app framework
- `pyobjc` - macOS system integration (Quartz, AppKit, Foundation)

## Core User Flow

1. User presses `Cmd+Option+4`
2. Transparent overlay appears for region selection
3. User selects region and clicks
4. Image is captured, compressed (50% scale), and copied to clipboard
5. User can immediately paste with `Cmd+V`

## Critical Implementation Areas

### Region Capture
- Use `CGDisplayCreateImageForRect` for precise region capture
- Implement transparent overlay for rubber band selection
- Handle multi-monitor setups and DPI differences

### Clipboard Integration
- Use `NSPasteboard.generalPasteboard()` for clipboard operations
- Handle RGBA to RGB conversion for non-PNG formats
- Implement race condition protection

### Error Handling
- Graceful fallbacks (return original data on compression failure)
- Handle large image sizes and memory constraints
- Manage clipboard conflicts

## macOS-Specific Considerations

- **Retina Display**: Handle high-DPI scaling correctly
- **Multiple Monitors**: Account for different DPI settings
- **Privacy**: Request screen recording permissions
- **Distribution**: Code signing and notarization required
- **Hotkey Registration**: Avoid conflicts with system shortcuts

## Testing Strategy

Focus on:
- Image compression ratios and quality
- Clipboard integration reliability
- Multi-monitor capture accuracy
- Error handling and edge cases
- Memory usage with large images

## Distribution

MVP targets GitHub releases with signed DMG files. Later phases may include Mac App Store distribution.