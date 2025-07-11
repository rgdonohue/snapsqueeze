# SnapSqueeze MVP Execution Plan (Revised)
*A Clipboard-First Screenshot Compressor for macOS*

## ✅ Architecture

```python
# core/image_compressor.py
from PIL import Image
import io

class ImageCompressor:
    def __init__(self, target_scale=0.5, format='PNG'):
        self.target_scale = target_scale
        self.format = format
    
    def compress(self, image_data):
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Handle RGBA for PNG, convert to RGB for other formats
            if self.format != 'PNG' and image.mode == 'RGBA':
                image = image.convert('RGB')
            
            new_size = (int(image.width * self.target_scale), 
                       int(image.height * self.target_scale))
            resized = image.resize(new_size, Image.LANCZOS)
            
            output = io.BytesIO()
            save_kwargs = {'format': self.format, 'optimize': True}
            if self.format == 'PNG':
                save_kwargs['compress_level'] = 6  # Balance speed/size
            
            resized.save(output, **save_kwargs)
            return output.getvalue()
        except Exception as e:
            # Log error, return original data as fallback
            return image_data
```

```python
# system/screenshot_handler.py
import Quartz
import AppKit
from Foundation import NSPasteboard, NSPasteboardTypePNG
from core.image_compressor import ImageCompressor

class ScreenshotHandler:
    def __init__(self):
        self.compressor = ImageCompressor()
    
    def capture_region_and_compress(self):
        # Use CGDisplayCreateImageForRect for region capture
        # Requires a selection overlay implementation
        pass
    
    def write_to_clipboard(self, image_data):
        pasteboard = NSPasteboard.generalPasteboard()
        pasteboard.clearContents()
        pasteboard.setData_forType_(image_data, NSPasteboardTypePNG)
```

```python
# ui/menu_bar_app.py
from AppKit import NSApplication, NSStatusBar, NSMenu, NSMenuItem
import rumps  # Consider this for simpler menu bar apps

class SnapSqueezeApp(rumps.App):
    def __init__(self):
        super().__init__("SnapSqueeze", icon="icon.png")
        self.menu = ["Capture & Compress", "Preferences", "Quit"]
        self.screenshot_handler = ScreenshotHandler()
    
    @rumps.clicked("Capture & Compress")
    def capture_clicked(self, _):
        self.screenshot_handler.capture_region_and_compress()
```

* Use **Python + pyobjc** for MVP speed and simplicity.
* Introduce Swift **only if**: UI becomes complex or performance bottlenecks arise.

## 🌟 MVP Feature Scope

| Feature | Status | Notes |
|---------|--------|-------|
| Region capture | ✅ Must-have | Transparent overlay with rubber band selection |
| PNG compression | ✅ Must-have | Default format, handles RGBA properly |
| Fixed 50% resize | ✅ Must-have | Configurable via constructor |
| Clipboard output | ✅ Must-have | NSPasteboard integration |
| Menu bar toggle (minimal) | ✅ Must-have | Using rumps library for simplicity |
| Visual feedback | ✅ Must-have | Brief notification on completion |
| Window capture | ❌ Nice-to-have | Post-MVP validation |
| Preferences UI | ❌ Nice-to-have | Quick settings via right-click menu |
| Temp file output | ❌ Nice-to-have | Undo mechanism (1-hour retention) |
| JPEG/WebP toggle | ❌ Post-validation | Focus on PNG optimization first |
| Redaction tools | ❌ Post-validation | Advanced feature for Pro version |

## 🧪 Core User Flow

**SnapSqueeze vs. Standard macOS:**

*Current macOS Flow:*
1. `Cmd+Shift+4` → Select region → Click
2. Screenshot saved to desktop (full resolution)
3. `Cmd+V` pastes full-res image (if copied)

*SnapSqueeze Flow:*
1. `Cmd+Option+4` → Select region → Click  
2. SnapSqueeze automatically compresses and copies to clipboard
3. `Cmd+V` immediately pastes compressed image

**Key benefit**: Eliminates the manual resize step that users currently do in Preview/Photoshop before pasting.

## 🧪 Core Validation Use Cases

* **Slack pasting** (primary use case)
* **Jira/GitHub bug reporting**
* **Documentation and Notion embeds**
* **Design + PM feedback loops**

## ⚠️ Edge Cases to Handle

* **Retina (high-DPI) vs. standard display scaling**
* **Multiple monitors** (incl. DPI mismatch)
* **Large image sizes** (e.g., 4K or ultra-wide captures)
* **Clipboard conflict** (race conditions, type coercion)
* **RGBA to RGB conversion** for non-PNG formats
* **Error handling** with graceful fallbacks

## 🚀 Distribution Strategy

**Phase 1**: Signed DMG via GitHub
* Fast iteration
* Skip Mac App Store gatekeeping
* Basic auto-launch option (via LaunchAgent or plist)
* Feedback via GitHub Issues

**Phase 1 GitHub Release Checklist:**
- [ ] Code signing certificate
- [ ] Notarization for Gatekeeper
- [ ] Basic installer (shell script or .pkg)
- [ ] Clear README + install instructions
- [ ] GitHub issue templates for feedback

**Phase 2**: Harden UX and release to Mac App Store
* Once product-market fit is validated

## 🧠 Strategic Notes

* **Hotkey Strategy**: Use `Cmd+Option+4` to build on existing screenshot muscle memory while avoiding conflicts. Related to `Cmd+Shift+4` but clearly distinct for compression workflow.
* **Region Selection**: Implement transparent overlay for rubber band selection; use `CGDisplayCreateImageForRect` to capture selected region.

* **Privacy First**: All processing is local; no telemetry unless user opts in

* **User Control**: MVP stays stateless, with optional Pro upgrades

* **Freemium Path**: Advanced features (e.g., blur, batch, format presets) gated behind a one-time unlock or donationware model

## 📊 MVP Validation Metrics

Track these locally (with user consent):
- **Usage frequency**: Screenshots per day/week
- **Compression ratios**: Original vs compressed file sizes
- **Workflow completion**: Capture → paste success rate
- **Error scenarios**: Failed captures, clipboard conflicts

## 🚀 Quick Wins for User Feedback

* **Visual confirmation**: Toast or menu bar notification when compression completes
* **Undo/restore**: Keep last original in temp folder for 1 hour
* **Quick settings**: Right-click menu for 25%/50%/75% scale options
* **Status visibility**: Show compression ratio in notification

## 🚀 Early User Acquisition

- **ProductHunt launch**
- **Hacker News (Show HN)**
- **Mac productivity forums** (Reddit, Discord)
- **Developer Twitter/X**

## 🔗 Implementation Priority

1. **Core compression engine** (ImageCompressor class)
2. **Basic region capture** (selection overlay)
3. **Clipboard integration** (NSPasteboard)
4. **Menu bar app** (rumps-based)
5. **Visual feedback** (notifications)
6. **Error handling** (graceful degradation)
7. **Distribution setup** (signing, notarization)

---

**SnapSqueeze: Shrink Your Shots. Boost Your Flow.**

*Focus: Compress the workflow, not just the image*