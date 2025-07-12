# SnapSqueeze Privacy Policy

**Last Updated**: December 2024  
**Version**: 1.0

## Our Commitment to Privacy

SnapSqueeze is designed with privacy as a fundamental principle. This document explains exactly what data is collected, processed, and shared (spoiler: almost nothing).

## Data Collection and Processing

### What We DON'T Collect

- **No screenshots are uploaded** - All image processing happens locally on your machine
- **No telemetry or analytics** - We don't track usage patterns, crashes, or performance
- **No personal information** - No names, emails, device IDs, or location data
- **No network requests** - SnapSqueeze works completely offline
- **No user accounts** - No registration, login, or cloud services required

### What We DO Process (Locally Only)

1. **Screenshot Images**
   - Captured when you press the hotkey or use manual capture
   - Processed entirely on your Mac using local CPU and memory
   - Compressed and placed on clipboard
   - **Never stored to disk** (except in temporary clipboard cache managed by macOS)
   - **Never transmitted** to any server or external service

2. **Application Preferences**
   - Compression settings (scale, format)
   - Hotkey configuration
   - UI preferences
   - **Stored locally** in macOS standard preference files (`~/Library/Preferences/`)
   - **Never synchronized** or backed up to external services

3. **System Information (For Functionality Only)**
   - Screen resolution and DPI for accurate capture
   - Available memory for performance optimization
   - Clipboard access for image placement
   - **Used immediately** and not retained

## Permissions Required

### Screen Recording Permission

**Why needed**: To capture screenshots of your selected regions  
**What it accesses**: Only the screen regions you explicitly select during capture  
**Limitations**: 
- Cannot access your screen when the app is not actively capturing
- Cannot record video or continuous monitoring
- Cannot access other applications' private data

### Clipboard Access

**Why needed**: To place compressed images on your clipboard for pasting  
**What it accesses**: Only writes compressed image data to clipboard  
**Limitations**:
- Does not read existing clipboard contents
- Only writes image data, never text or other formats
- Temporary storage only (cleared when you copy something else)

## Data Storage

### Local Storage Only

All SnapSqueeze data is stored locally on your Mac:

- **Preferences**: `~/Library/Preferences/com.snapsqueeze.*`
- **Temporary files**: `~/Library/Caches/SnapSqueeze/` (automatically cleaned)
- **Application files**: `/Applications/SnapSqueeze.app/`

### No Cloud Storage

- No data is synchronized to iCloud, Google Drive, or any cloud service
- No automatic backups to external servers
- Your data stays on your machine

## Third-Party Dependencies

SnapSqueeze uses these open-source libraries, all running locally:

- **Pillow (PIL)**: Image processing library - processes images locally
- **rumps**: Menu bar interface library - UI only, no network access
- **PyObjC**: macOS integration library - system interface only
- **psutil**: System resource monitoring - local system info only

**None of these libraries transmit data externally when used by SnapSqueeze.**

## Security Measures

### Local Processing Benefits

- **No data breaches possible** - Your images never leave your machine
- **No server vulnerabilities** - No external services to compromise
- **Network-independent** - Works without internet connection
- **Instant processing** - No upload/download delays

### Code Transparency

- **Open source** - Full source code available for audit
- **No obfuscation** - All code is readable and verifiable
- **Community reviewed** - Security experts can examine the codebase

## Compliance

### GDPR Compliance

SnapSqueeze is GDPR compliant by design:
- **No personal data processing** - Nothing to regulate
- **No consent required** - No data collection occurs
- **No data transfer** - All processing is local
- **No data retention** - Images are not stored

### CCPA Compliance

Under the California Consumer Privacy Act:
- **No personal information sale** - Nothing is collected to sell
- **No data sharing** - All processing is local
- **Full user control** - You own all your data

## Children's Privacy

SnapSqueeze does not knowingly collect any information from users under 13 years of age. Since no data is collected at all, this is inherently compliant with COPPA and similar regulations.

## Changes to Privacy Policy

If we ever change our privacy practices (though we don't anticipate needing to), we will:

1. **Update this document** with a new version number and date
2. **Provide notice** in the app and on GitHub
3. **Maintain backward compatibility** or provide clear migration instructions

## Verification

You can verify our privacy claims by:

### 1. Network Monitoring
```bash
# Monitor network activity while using SnapSqueeze
sudo lsof -i -P | grep -i snapsqueeze
# Should show no network connections
```

### 2. File System Monitoring
```bash
# Check what files SnapSqueeze accesses
sudo fs_usage -w -f filesys | grep -i snapsqueeze
# Should only show local preference and cache files
```

### 3. Source Code Audit
- Review the complete source code on GitHub
- All network-related code is absent (no `urllib`, `requests`, `socket` usage)
- Verify local-only processing in image compression modules

## Contact

If you have privacy questions or concerns:

- **GitHub Issues**: [Create a privacy-related issue](https://github.com/username/snapsqueeze/issues)
- **Email**: [maintainer@example.com] (if provided)
- **Code Review**: Submit pull requests for privacy improvements

## Summary

**SnapSqueeze is designed to be completely private by default:**

✅ **Zero data collection**  
✅ **100% local processing**  
✅ **No network connections**  
✅ **Open source and auditable**  
✅ **No accounts or registration**  
✅ **Complete user control**  

Your screenshots and data remain entirely under your control, on your machine, at all times.

---

*This privacy policy reflects our commitment to building software that respects user privacy by design. We believe the best way to protect your data is to never collect it in the first place.*