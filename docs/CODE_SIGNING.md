# Code Signing and Notarization Guide

This guide covers how to set up code signing and notarization for SnapSqueeze distribution.

## Prerequisites

### Apple Developer Account

1. **Enroll in Apple Developer Program**
   - Visit [developer.apple.com](https://developer.apple.com)
   - Cost: $99/year for individual developers
   - Required for code signing and App Store distribution

2. **Verify Account Status**
   ```bash
   # Check your developer account
   xcrun altool --list-providers -u "your-apple-id@example.com" -p "app-specific-password"
   ```

## Step 1: Generate Certificates

### 1.1 Create Certificate Signing Request (CSR)

1. **Open Keychain Access**
2. **Keychain Access → Certificate Assistant → Request a Certificate From a Certificate Authority**
3. **Fill in details:**
   - User Email Address: Your Apple ID email
   - Common Name: Your name or organization
   - Request is: Saved to disk
4. **Save CSR file** (e.g., `CertificateSigningRequest.certSigningRequest`)

### 1.2 Generate Developer ID Certificate

1. **Go to Apple Developer Portal**
   - [developer.apple.com/certificates](https://developer.apple.com/certificates)
2. **Create New Certificate**
   - Choose "Developer ID Application"
   - Upload your CSR file
   - Download the certificate
3. **Install Certificate**
   - Double-click to install in Keychain
   - Verify it appears in "My Certificates"

### 1.3 Verify Certificate Installation

```bash
# List available code signing identities
security find-identity -v -p codesigning

# Should show something like:
# 1) ABC123... "Developer ID Application: Your Name (TEAM_ID)"
```

## Step 2: Configure Build Environment

### 2.1 Set Environment Variables

Add to your shell profile (`.zshrc`, `.bash_profile`):

```bash
# Code signing configuration
export APPLE_ID="your-apple-id@example.com"
export TEAM_ID="YOUR_TEAM_ID"  # From developer portal
export CODESIGN_IDENTITY="Developer ID Application: Your Name (TEAM_ID)"

# App-specific password for notarization
export NOTARIZATION_PASSWORD="xxxx-xxxx-xxxx-xxxx"  # Generate in Apple ID settings
```

### 2.2 Create App-Specific Password

1. **Go to Apple ID Account Page**
   - [appleid.apple.com](https://appleid.apple.com)
2. **Sign In → Security → App-Specific Passwords**
3. **Generate Password** for "SnapSqueeze Notarization"
4. **Save the password** - you can't view it again

### 2.3 Configure GitHub Secrets (For CI/CD)

Add these secrets to your GitHub repository:

```
MACOS_CERTIFICATE          # Base64 encoded .p12 certificate
MACOS_CERTIFICATE_PWD       # Password for .p12 certificate  
MACOS_CERTIFICATE_NAME      # Certificate name (e.g., "Developer ID Application: ...")
NOTARIZATION_USERNAME       # Your Apple ID email
NOTARIZATION_PASSWORD       # App-specific password
TEAM_ID                     # Your team ID
```

## Step 3: Code Signing Process

### 3.1 Manual Code Signing

```bash
# Sign the app bundle
codesign --force --verify --verbose --sign "$CODESIGN_IDENTITY" \
  --options runtime \
  --entitlements SnapSqueeze.entitlements \
  "SnapSqueeze.app"

# Verify signing
codesign -vvv --deep --strict "SnapSqueeze.app"
spctl -a -vvv -t install "SnapSqueeze.app"
```

### 3.2 Create Entitlements File

Create `SnapSqueeze.entitlements`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.cs.allow-jit</key>
    <true/>
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <true/>
    <key>com.apple.security.cs.disable-library-validation</key>
    <true/>
    <key>com.apple.security.device.camera</key>
    <false/>
    <key>com.apple.security.device.microphone</key>
    <false/>
    <key>com.apple.security.network.client</key>
    <false/>
    <key>com.apple.security.network.server</key>
    <false/>
</dict>
</plist>
```

### 3.3 Sign DMG

```bash
# Create and sign DMG
hdiutil create -srcfolder "SnapSqueeze.app" \
  -volname "SnapSqueeze" \
  -format UDZO \
  "SnapSqueeze-v1.0.0.dmg"

# Sign the DMG
codesign --force --verify --verbose --sign "$CODESIGN_IDENTITY" \
  "SnapSqueeze-v1.0.0.dmg"
```

## Step 4: Notarization

### 4.1 Submit for Notarization

```bash
# Submit DMG for notarization
xcrun notarytool submit "SnapSqueeze-v1.0.0.dmg" \
  --apple-id "$APPLE_ID" \
  --password "$NOTARIZATION_PASSWORD" \
  --team-id "$TEAM_ID" \
  --wait

# Alternative: Submit app bundle
xcrun notarytool submit "SnapSqueeze.app" \
  --apple-id "$APPLE_ID" \
  --password "$NOTARIZATION_PASSWORD" \
  --team-id "$TEAM_ID" \
  --wait
```

### 4.2 Check Notarization Status

```bash
# Check status with submission ID
xcrun notarytool info SUBMISSION_ID \
  --apple-id "$APPLE_ID" \
  --password "$NOTARIZATION_PASSWORD" \
  --team-id "$TEAM_ID"

# Download logs if needed
xcrun notarytool log SUBMISSION_ID \
  --apple-id "$APPLE_ID" \
  --password "$NOTARIZATION_PASSWORD" \
  --team-id "$TEAM_ID"
```

### 4.3 Staple Notarization

```bash
# Staple notarization to DMG
xcrun stapler staple "SnapSqueeze-v1.0.0.dmg"

# Verify stapling
xcrun stapler validate "SnapSqueeze-v1.0.0.dmg"
spctl -a -vvv -t install "SnapSqueeze-v1.0.0.dmg"
```

## Step 5: Automated Signing Script

Create `scripts/sign_and_notarize.sh`:

```bash
#!/bin/bash

set -e

APP_NAME="SnapSqueeze"
VERSION="${1:-1.0.0}"
BUILD_DIR="build"
DIST_DIR="dist"

echo "🔐 Code signing and notarizing ${APP_NAME} v${VERSION}..."

# Ensure required env vars are set
if [[ -z "$CODESIGN_IDENTITY" || -z "$APPLE_ID" || -z "$NOTARIZATION_PASSWORD" || -z "$TEAM_ID" ]]; then
    echo "❌ Missing required environment variables"
    echo "Set: CODESIGN_IDENTITY, APPLE_ID, NOTARIZATION_PASSWORD, TEAM_ID"
    exit 1
fi

APP_BUNDLE="${BUILD_DIR}/${APP_NAME}.app"
DMG_FILE="${DIST_DIR}/${APP_NAME}-v${VERSION}.dmg"

# 1. Sign the app bundle
echo "🔏 Signing app bundle..."
codesign --force --verify --verbose --sign "$CODESIGN_IDENTITY" \
  --options runtime \
  --entitlements "${APP_NAME}.entitlements" \
  "$APP_BUNDLE"

# 2. Verify signing
echo "✅ Verifying app signature..."
codesign -vvv --deep --strict "$APP_BUNDLE"

# 3. Create and sign DMG
echo "📦 Creating signed DMG..."
hdiutil create -srcfolder "$APP_BUNDLE" \
  -volname "$APP_NAME" \
  -format UDZO \
  "$DMG_FILE"

codesign --force --verify --verbose --sign "$CODESIGN_IDENTITY" \
  "$DMG_FILE"

# 4. Submit for notarization
echo "📋 Submitting for notarization..."
SUBMISSION_ID=$(xcrun notarytool submit "$DMG_FILE" \
  --apple-id "$APPLE_ID" \
  --password "$NOTARIZATION_PASSWORD" \
  --team-id "$TEAM_ID" \
  --wait \
  --output-format json | jq -r '.id')

echo "📋 Submission ID: $SUBMISSION_ID"

# 5. Check notarization status
echo "🔍 Checking notarization status..."
xcrun notarytool info "$SUBMISSION_ID" \
  --apple-id "$APPLE_ID" \
  --password "$NOTARIZATION_PASSWORD" \
  --team-id "$TEAM_ID"

# 6. Staple notarization
echo "📎 Stapling notarization..."
xcrun stapler staple "$DMG_FILE"

# 7. Final verification
echo "✅ Final verification..."
xcrun stapler validate "$DMG_FILE"
spctl -a -vvv -t install "$DMG_FILE"

echo "🎉 Successfully signed and notarized: $DMG_FILE"
```

## Step 6: Testing

### 6.1 Test on Clean System

1. **Create test VM or use another Mac**
2. **Download the signed DMG**
3. **Install without admin privileges**
4. **Verify no security warnings appear**

### 6.2 Verify Gatekeeper Approval

```bash
# Check Gatekeeper status
spctl --status

# Test DMG approval
spctl -a -vvv -t install "SnapSqueeze-v1.0.0.dmg"

# Should show: "accepted" with no errors
```

## Common Issues

### Issue: "No identity found"

**Solution**: Install Developer ID certificate in Keychain

```bash
# Check keychain
security find-identity -v -p codesigning
```

### Issue: "Authentication failed"

**Solution**: Verify Apple ID and app-specific password

```bash
# Test authentication
xcrun notarytool store-credentials "SnapSqueeze-Profile" \
  --apple-id "$APPLE_ID" \
  --team-id "$TEAM_ID" \
  --password "$NOTARIZATION_PASSWORD"
```

### Issue: "Invalid binary"

**Solution**: Check entitlements and signing options

```bash
# Debug signing issues
codesign -dvvv "SnapSqueeze.app"
```

### Issue: Notarization rejected

**Solution**: Check notarization logs

```bash
# Download detailed logs
xcrun notarytool log SUBMISSION_ID \
  --apple-id "$APPLE_ID" \
  --password "$NOTARIZATION_PASSWORD" \
  --team-id "$TEAM_ID" \
  developer_log.json
```

## Security Best Practices

1. **Protect certificates**: Store in secure keychain
2. **Rotate passwords**: Change app-specific passwords regularly  
3. **Limit permissions**: Use minimal entitlements
4. **Audit builds**: Verify signatures before distribution
5. **Monitor certificates**: Check expiration dates

## Resources

- [Apple Code Signing Guide](https://developer.apple.com/library/archive/documentation/Security/Conceptual/CodeSigningGuide/)
- [Notarization Documentation](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)
- [Xcode Help: Signing](https://help.apple.com/xcode/mac/current/#/dev154b28f09)