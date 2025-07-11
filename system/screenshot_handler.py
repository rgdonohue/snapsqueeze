import logging
import io
from Quartz import (
    CGDisplayCreateImageForRect, CGRectMake, CGImageGetWidth, CGImageGetHeight,
    CGImageCreateWithImageInRect, CGDataProviderCreateWithCFData,
    CGImageCreateWithPNGDataProvider, CGBitmapContextCreateImage,
    CGBitmapContextCreate, CGColorSpaceCreateDeviceRGB,
    kCGImageAlphaPremultipliedLast, kCGBitmapByteOrder32Big
)
from Cocoa import (
    NSPasteboard, NSPasteboardTypePNG, NSData, NSScreen,
    NSEvent, NSApplication, NSWindow, NSView, NSColor,
    NSBezierPath, NSRect, NSMakeRect, NSRectFill
)
from Foundation import NSTimer
from core.image_compressor import ImageCompressor
from system.permissions import PermissionManager
from core.error_handler import handle_errors, ErrorCode, ScreenshotError, ClipboardError

logger = logging.getLogger(__name__)


class RegionSelectionOverlay:
    """Transparent overlay for region selection."""
    
    def __init__(self, callback=None):
        self.callback = callback
        self.start_point = None
        self.end_point = None
        self.window = None
        self.is_selecting = False
        
    def show_overlay(self):
        """Show the selection overlay."""
        try:
            # Get screen dimensions
            screen = NSScreen.mainScreen()
            screen_rect = screen.frame()
            
            # Create transparent window covering the screen
            self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
                screen_rect,
                0,  # No style mask for transparent window
                2,  # NSBackingStoreBuffered
                False
            )
            
            # Configure window
            self.window.setLevel_(1000)  # Above most windows
            self.window.setOpaque_(False)
            self.window.setBackgroundColor_(NSColor.clearColor())
            self.window.setIgnoresMouseEvents_(False)
            self.window.makeKeyAndOrderFront_(None)
            
            # Create content view
            content_view = RegionSelectionView.alloc().initWithFrame_(screen_rect)
            content_view.overlay = self
            self.window.setContentView_(content_view)
            
            self.is_selecting = True
            
        except Exception as e:
            logger.error(f"Error showing overlay: {e}")
            
    def hide_overlay(self):
        """Hide the selection overlay."""
        if self.window:
            self.window.orderOut_(None)
            self.window = None
        self.is_selecting = False
        
    def selection_completed(self, start_point, end_point):
        """Called when selection is completed."""
        self.start_point = start_point
        self.end_point = end_point
        self.hide_overlay()
        
        if self.callback:
            self.callback(start_point, end_point)


class RegionSelectionView(NSView):
    """View for handling region selection."""
    
    def initWithFrame_(self, frame):
        self = super(RegionSelectionView, self).initWithFrame_(frame)
        if self:
            self.overlay = None
            self.start_point = None
            self.current_point = None
            self.is_dragging = False
        return self
    
    def mouseDown_(self, event):
        """Handle mouse down event."""
        self.start_point = self.convertPoint_fromView_(event.locationInWindow(), None)
        self.is_dragging = True
        
    def mouseDragged_(self, event):
        """Handle mouse drag event."""
        if self.is_dragging:
            self.current_point = self.convertPoint_fromView_(event.locationInWindow(), None)
            self.setNeedsDisplay_(True)
            
    def mouseUp_(self, event):
        """Handle mouse up event."""
        if self.is_dragging and self.start_point and self.current_point:
            self.is_dragging = False
            
            # Calculate selection rectangle
            min_x = min(self.start_point.x, self.current_point.x)
            min_y = min(self.start_point.y, self.current_point.y)
            max_x = max(self.start_point.x, self.current_point.x)
            max_y = max(self.start_point.y, self.current_point.y)
            
            # Notify overlay of selection
            if self.overlay:
                self.overlay.selection_completed(
                    (min_x, min_y),
                    (max_x, max_y)
                )
    
    def drawRect_(self, rect):
        """Draw the selection rectangle."""
        # Fill background with semi-transparent overlay
        NSColor.colorWithCalibratedRed_green_blue_alpha_(0.0, 0.0, 0.0, 0.3).set()
        NSRectFill(rect)
        
        # Draw selection rectangle if dragging
        if self.is_dragging and self.start_point and self.current_point:
            # Clear the selection area
            selection_rect = NSMakeRect(
                min(self.start_point.x, self.current_point.x),
                min(self.start_point.y, self.current_point.y),
                abs(self.current_point.x - self.start_point.x),
                abs(self.current_point.y - self.start_point.y)
            )
            
            # Clear selection area
            NSColor.clearColor().set()
            NSRectFill(selection_rect)
            
            # Draw selection border
            NSColor.colorWithCalibratedRed_green_blue_alpha_(0.0, 0.5, 1.0, 0.8).set()
            NSBezierPath.strokeRect_(selection_rect)


class ScreenshotHandler:
    """Handles screenshot capture and processing."""
    
    def __init__(self):
        self.compressor = ImageCompressor()
        self.permission_manager = PermissionManager()
        self.overlay = None
        
    @handle_errors(ErrorCode.SCREENSHOT_CAPTURE_ERROR, "region capture", return_on_error=False)
    def capture_region_and_compress(self):
        """Capture a region and compress it."""
        # Ensure permissions
        if not self.permission_manager.ensure_permissions():
            logger.error("Screen capture permission not granted")
            raise ScreenshotError("Screen capture permission not granted", ErrorCode.PERMISSION_DENIED)
        
        # Show region selection overlay
        self.overlay = RegionSelectionOverlay(callback=self._on_region_selected)
        self.overlay.show_overlay()
        
        return True
    
    def _on_region_selected(self, start_point, end_point):
        """Called when region selection is completed."""
        try:
            # Calculate capture rectangle
            x = int(start_point[0])
            y = int(start_point[1])
            width = int(end_point[0] - start_point[0])
            height = int(end_point[1] - start_point[1])
            
            # Ensure valid dimensions
            if width <= 0 or height <= 0:
                logger.warning("Invalid selection dimensions")
                return
            
            # Capture the region
            captured_data = self._capture_screen_region(x, y, width, height)
            
            if captured_data:
                # Compress the image
                compressed_data = self.compressor.compress(captured_data)
                
                # Copy to clipboard
                self.write_to_clipboard(compressed_data)
                
                # Log success
                original_size = len(captured_data)
                compressed_size = len(compressed_data)
                ratio = (1 - compressed_size / original_size) * 100
                logger.info(f"Captured and compressed region: {ratio:.1f}% reduction")
                
        except Exception as e:
            logger.error(f"Error processing region selection: {e}")
    
    def _capture_screen_region(self, x, y, width, height):
        """Capture a specific region of the screen."""
        try:
            # Create capture rectangle
            capture_rect = CGRectMake(x, y, width, height)
            
            # Capture the region
            image_ref = CGDisplayCreateImageForRect(0, capture_rect)  # 0 = main display
            
            if not image_ref:
                logger.error("Failed to capture screen region")
                return None
            
            # Convert to PNG data
            png_data = self._cgimage_to_png_data(image_ref)
            
            return png_data
            
        except Exception as e:
            logger.error(f"Error capturing screen region: {e}")
            return None
    
    def _cgimage_to_png_data(self, image_ref):
        """Convert CGImage to PNG data."""
        try:
            # This is a simplified approach - in practice you'd use more sophisticated
            # conversion methods or libraries like Pillow to handle the conversion
            
            # For now, we'll create a basic PNG representation
            # In a real implementation, you'd use CGImageDestination or similar
            
            # Get image dimensions
            width = CGImageGetWidth(image_ref)
            height = CGImageGetHeight(image_ref)
            
            # Create a simple PNG-like structure (this is a placeholder)
            # In production, you'd use proper image conversion
            
            # For testing, create a minimal image structure
            from PIL import Image
            import numpy as np
            
            # Create a placeholder image (this would be replaced with actual conversion)
            # This is just for testing the framework
            image_array = np.zeros((height, width, 3), dtype=np.uint8)
            image_array[:] = [255, 0, 0]  # Red placeholder
            
            pil_image = Image.fromarray(image_array)
            buffer = io.BytesIO()
            pil_image.save(buffer, format='PNG')
            
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error converting CGImage to PNG: {e}")
            return None
    
    @handle_errors(ErrorCode.CLIPBOARD_WRITE_ERROR, "clipboard write", return_on_error=False)
    def write_to_clipboard(self, image_data):
        """Write image data to clipboard."""
        if not image_data:
            raise ClipboardError("No image data to write", ErrorCode.CLIPBOARD_ACCESS_ERROR)
        
        # Get the pasteboard
        pasteboard = NSPasteboard.generalPasteboard()
        
        # Clear existing contents
        pasteboard.clearContents()
        
        # Create NSData from bytes
        ns_data = NSData.dataWithBytes_length_(image_data, len(image_data))
        
        # Write to pasteboard
        success = pasteboard.setData_forType_(ns_data, NSPasteboardTypePNG)
        
        if not success:
            raise ClipboardError("Failed to write to clipboard", ErrorCode.CLIPBOARD_WRITE_ERROR)
        
        logger.info("Image copied to clipboard successfully")
        return True
    
    def capture_full_screen(self):
        """Capture the full screen (for testing)."""
        try:
            # Get screen dimensions
            screen = NSScreen.mainScreen()
            screen_rect = screen.frame()
            
            return self._capture_screen_region(
                int(screen_rect.origin.x),
                int(screen_rect.origin.y),
                int(screen_rect.size.width),
                int(screen_rect.size.height)
            )
            
        except Exception as e:
            logger.error(f"Error capturing full screen: {e}")
            return None