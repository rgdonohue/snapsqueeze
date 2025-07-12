#!/bin/bash

# SnapSqueeze DMG Build Script
# Creates a distributable DMG file for SnapSqueeze

set -e

# Configuration
APP_NAME="SnapSqueeze"
VERSION="1.0.0"
BUILD_DIR="build"
DIST_DIR="dist"
DMG_NAME="${APP_NAME}-${VERSION}"
VOLUME_NAME="${APP_NAME}"

echo "🚀 Building ${APP_NAME} v${VERSION} DMG..."

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf "${BUILD_DIR}" "${DIST_DIR}"
mkdir -p "${BUILD_DIR}" "${DIST_DIR}"

# Create app bundle structure
echo "📦 Creating app bundle..."
APP_BUNDLE="${BUILD_DIR}/${APP_NAME}.app"
mkdir -p "${APP_BUNDLE}/Contents"
mkdir -p "${APP_BUNDLE}/Contents/MacOS"
mkdir -p "${APP_BUNDLE}/Contents/Resources"

# Copy Info.plist
cp Info.plist "${APP_BUNDLE}/Contents/"

# Copy app icon
if [ -f "assets/icon.icns" ]; then
    cp "assets/icon.icns" "${APP_BUNDLE}/Contents/Resources/"
else
    echo "⚠️  Warning: No icon.icns found, using default"
fi

# Create the executable wrapper script
cat > "${APP_BUNDLE}/Contents/MacOS/${APP_NAME}" << 'EOF'
#!/bin/bash
# Get the directory containing this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_DIR="$(dirname "$(dirname "$DIR")")"

# Set PYTHONPATH to include the app's Resources
export PYTHONPATH="${APP_DIR}/Contents/Resources:${PYTHONPATH}"

# Change to the Resources directory
cd "${APP_DIR}/Contents/Resources"

# Run the Python application
python3 -m ui.menu_bar_app
EOF

chmod +x "${APP_BUNDLE}/Contents/MacOS/${APP_NAME}"

# Copy Python source code to Resources
echo "📁 Copying source code..."
cp -r core/ "${APP_BUNDLE}/Contents/Resources/"
cp -r system/ "${APP_BUNDLE}/Contents/Resources/"
cp -r ui/ "${APP_BUNDLE}/Contents/Resources/"
cp main.py "${APP_BUNDLE}/Contents/Resources/"
cp requirements.txt "${APP_BUNDLE}/Contents/Resources/"

# Copy dependencies (if using a bundled Python environment)
echo "📚 Preparing dependencies..."
if [ -d "venv" ]; then
    echo "ℹ️  Virtual environment found, creating requirements install script"
    cat > "${APP_BUNDLE}/Contents/Resources/install_deps.py" << 'EOF'
#!/usr/bin/env python3
import subprocess
import sys
import os

def install_requirements():
    """Install requirements if not already installed."""
    try:
        # Check if we can import the main dependencies
        import PIL
        import rumps
        import psutil
        print("Dependencies already available")
        return True
    except ImportError:
        pass
    
    # Install requirements
    req_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(req_file):
        print("Installing dependencies...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', req_file, '--user'])
        return True
    return False

if __name__ == "__main__":
    install_requirements()
EOF
fi

# Create a temporary DMG directory
echo "🗂️  Preparing DMG contents..."
DMG_DIR="${BUILD_DIR}/dmg"
mkdir -p "${DMG_DIR}"

# Copy app bundle to DMG directory
cp -r "${APP_BUNDLE}" "${DMG_DIR}/"

# Create symlink to Applications folder
ln -s /Applications "${DMG_DIR}/Applications"

# Create a background image directory (optional)
mkdir -p "${DMG_DIR}/.background"

# Create DMG staging area with custom layout
echo "🎨 Setting up DMG layout..."
cat > "${BUILD_DIR}/dmg_setup.applescript" << EOF
tell application "Finder"
    tell disk "${VOLUME_NAME}"
        open
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set the bounds of container window to {100, 100, 650, 400}
        set theViewOptions to the icon view options of container window
        set arrangement of theViewOptions to not arranged
        set icon size of theViewOptions to 128
        set position of item "${APP_NAME}.app" of container window to {150, 150}
        set position of item "Applications" of container window to {400, 150}
        close
        open
        update without registering applications
        delay 5
    end tell
end tell
EOF

# Create the DMG
echo "💿 Creating DMG..."
hdiutil create -srcfolder "${DMG_DIR}" \
    -volname "${VOLUME_NAME}" \
    -fs HFS+ \
    -fsargs "-c c=64,a=16,e=16" \
    -format UDRW \
    -size 100m \
    "${BUILD_DIR}/${DMG_NAME}-tmp.dmg"

# Mount the DMG and apply custom layout
echo "🎯 Applying custom layout..."
hdiutil attach "${BUILD_DIR}/${DMG_NAME}-tmp.dmg" -mountpoint "${BUILD_DIR}/mount"

# Apply the layout script
if command -v osascript >/dev/null 2>&1; then
    osascript "${BUILD_DIR}/dmg_setup.applescript" || echo "⚠️  Could not apply custom layout"
fi

# Unmount the DMG
hdiutil detach "${BUILD_DIR}/mount"

# Convert to compressed, read-only DMG
echo "🗜️  Compressing DMG..."
hdiutil convert "${BUILD_DIR}/${DMG_NAME}-tmp.dmg" \
    -format UDZO \
    -imagekey zlib-level=9 \
    -o "${DIST_DIR}/${DMG_NAME}.dmg"

# Clean up temporary files
rm "${BUILD_DIR}/${DMG_NAME}-tmp.dmg"

echo "✅ DMG created successfully: ${DIST_DIR}/${DMG_NAME}.dmg"
echo "📊 File size: $(du -h "${DIST_DIR}/${DMG_NAME}.dmg" | cut -f1)"

# Generate checksums
echo "🔐 Generating checksums..."
cd "${DIST_DIR}"
shasum -a 256 "${DMG_NAME}.dmg" > "${DMG_NAME}.dmg.sha256"
echo "✅ SHA256: $(cat "${DMG_NAME}.dmg.sha256")"

echo "🎉 Build complete! Ready for distribution."
echo ""
echo "Next steps:"
echo "1. Test the DMG on a clean macOS system"
echo "2. Sign the app bundle with Apple Developer certificate"
echo "3. Notarize the DMG for Gatekeeper compatibility"
echo "4. Upload to GitHub releases"