import pytest
import io
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
from system.screenshot_handler import ScreenshotHandler, RegionSelectionOverlay, PermissionManager
from system.permissions import PermissionManager as PermissionManagerClass


class TestPermissionManager:
    """Test permission management functionality."""
    
    @patch('system.permissions.CGPreflightScreenCaptureAccess')
    def test_check_screen_capture_permission_granted(self, mock_preflight):
        """Test checking screen capture permission when granted."""
        mock_preflight.return_value = True
        
        manager = PermissionManagerClass()
        result = manager.check_screen_capture_permission()
        
        assert result is True
        assert manager.screen_capture_granted is True
        mock_preflight.assert_called_once()
    
    @patch('system.permissions.CGPreflightScreenCaptureAccess')
    def test_check_screen_capture_permission_denied(self, mock_preflight):
        """Test checking screen capture permission when denied."""
        mock_preflight.return_value = False
        
        manager = PermissionManagerClass()
        result = manager.check_screen_capture_permission()
        
        assert result is False
        assert manager.screen_capture_granted is False
        mock_preflight.assert_called_once()
    
    @patch('system.permissions.CGPreflightScreenCaptureAccess')
    def test_check_screen_capture_permission_error(self, mock_preflight):
        """Test checking screen capture permission with error."""
        mock_preflight.side_effect = Exception("Permission check failed")
        
        manager = PermissionManagerClass()
        result = manager.check_screen_capture_permission()
        
        assert result is False
        assert manager.screen_capture_granted is False
    
    def test_get_permission_status(self):
        """Test getting permission status."""
        manager = PermissionManagerClass()
        manager.screen_capture_granted = True
        
        status = manager.get_permission_status()
        
        assert status['screen_capture'] is True
        assert status['all_granted'] is True
    
    @patch('system.permissions.CGPreflightScreenCaptureAccess')
    def test_ensure_permissions_already_granted(self, mock_preflight):
        """Test ensuring permissions when already granted."""
        mock_preflight.return_value = True
        
        manager = PermissionManagerClass()
        result = manager.ensure_permissions()
        
        assert result is True


class TestRegionSelectionOverlay:
    """Test region selection overlay functionality."""
    
    def test_init_default_values(self):
        """Test overlay initialization with default values."""
        overlay = RegionSelectionOverlay()
        
        assert overlay.callback is None
        assert overlay.start_point is None
        assert overlay.end_point is None
        assert overlay.window is None
        assert overlay.is_selecting is False
    
    def test_init_with_callback(self):
        """Test overlay initialization with callback."""
        callback = Mock()
        overlay = RegionSelectionOverlay(callback=callback)
        
        assert overlay.callback == callback
    
    def test_selection_completed(self):
        """Test selection completion."""
        callback = Mock()
        overlay = RegionSelectionOverlay(callback=callback)
        
        start_point = (10, 10)
        end_point = (100, 100)
        
        overlay.selection_completed(start_point, end_point)
        
        assert overlay.start_point == start_point
        assert overlay.end_point == end_point
        assert overlay.is_selecting is False
        callback.assert_called_once_with(start_point, end_point)
    
    def test_hide_overlay(self):
        """Test hiding overlay."""
        overlay = RegionSelectionOverlay()
        overlay.window = Mock()
        overlay.is_selecting = True
        
        overlay.hide_overlay()
        
        assert overlay.window is None
        assert overlay.is_selecting is False


class TestScreenshotHandler:
    """Test screenshot handler functionality."""
    
    def test_init(self):
        """Test screenshot handler initialization."""
        handler = ScreenshotHandler()
        
        assert handler.compressor is not None
        assert handler.permission_manager is not None
        assert handler.overlay is None
    
    @patch('system.screenshot_handler.NSPasteboard')
    def test_write_to_clipboard_success(self, mock_pasteboard_class):
        """Test writing to clipboard successfully."""
        # Mock pasteboard
        mock_pasteboard = Mock()
        mock_pasteboard_class.generalPasteboard.return_value = mock_pasteboard
        mock_pasteboard.setData_forType_.return_value = True
        
        handler = ScreenshotHandler()
        test_data = b"test image data"
        
        result = handler.write_to_clipboard(test_data)
        
        assert result is True
        mock_pasteboard.clearContents.assert_called_once()
        mock_pasteboard.setData_forType_.assert_called_once()
    
    @patch('system.screenshot_handler.NSPasteboard')
    def test_write_to_clipboard_failure(self, mock_pasteboard_class):
        """Test writing to clipboard failure."""
        # Mock pasteboard
        mock_pasteboard = Mock()
        mock_pasteboard_class.generalPasteboard.return_value = mock_pasteboard
        mock_pasteboard.setData_forType_.return_value = False
        
        handler = ScreenshotHandler()
        test_data = b"test image data"
        
        result = handler.write_to_clipboard(test_data)
        
        assert result is False
    
    @patch('system.screenshot_handler.NSPasteboard')
    def test_write_to_clipboard_exception(self, mock_pasteboard_class):
        """Test writing to clipboard with exception."""
        mock_pasteboard_class.generalPasteboard.side_effect = Exception("Pasteboard error")
        
        handler = ScreenshotHandler()
        test_data = b"test image data"
        
        result = handler.write_to_clipboard(test_data)
        
        assert result is False
    
    def test_on_region_selected_invalid_dimensions(self):
        """Test region selection with invalid dimensions."""
        handler = ScreenshotHandler()
        
        # Test with zero width
        handler._on_region_selected((10, 10), (10, 50))
        
        # Test with zero height
        handler._on_region_selected((10, 10), (50, 10))
        
        # Test with negative dimensions
        handler._on_region_selected((50, 50), (10, 10))
        
        # Should not crash and should log warnings
        assert True  # Test passes if no exceptions are raised
    
    @patch('system.screenshot_handler.CGDisplayCreateImageForRect')
    def test_capture_screen_region_failure(self, mock_capture):
        """Test screen region capture failure."""
        mock_capture.return_value = None
        
        handler = ScreenshotHandler()
        result = handler._capture_screen_region(0, 0, 100, 100)
        
        assert result is None
        mock_capture.assert_called_once()
    
    @patch('system.screenshot_handler.CGDisplayCreateImageForRect')
    def test_capture_screen_region_exception(self, mock_capture):
        """Test screen region capture with exception."""
        mock_capture.side_effect = Exception("Capture failed")
        
        handler = ScreenshotHandler()
        result = handler._capture_screen_region(0, 0, 100, 100)
        
        assert result is None
    
    def test_cgimage_to_png_data_creates_placeholder(self):
        """Test CGImage to PNG conversion creates placeholder."""
        handler = ScreenshotHandler()
        
        # Mock CGImage reference
        mock_image_ref = Mock()
        
        # Mock the width and height functions
        with patch('system.screenshot_handler.CGImageGetWidth', return_value=100):
            with patch('system.screenshot_handler.CGImageGetHeight', return_value=100):
                result = handler._cgimage_to_png_data(mock_image_ref)
        
        assert result is not None
        assert len(result) > 0
        
        # Verify it's valid PNG data by loading with PIL
        image = Image.open(io.BytesIO(result))
        assert image.size == (100, 100)
        assert image.format == 'PNG'
    
    def test_cgimage_to_png_data_exception(self):
        """Test CGImage to PNG conversion with exception."""
        handler = ScreenshotHandler()
        
        # Mock image ref that causes exception
        mock_image_ref = Mock()
        
        with patch('system.screenshot_handler.CGImageGetWidth', side_effect=Exception("Conversion error")):
            result = handler._cgimage_to_png_data(mock_image_ref)
        
        assert result is None
    
    @patch.object(ScreenshotHandler, '_capture_screen_region')
    @patch.object(ScreenshotHandler, 'write_to_clipboard')
    def test_on_region_selected_success(self, mock_write_clipboard, mock_capture):
        """Test successful region selection processing."""
        # Mock capture returning test data
        test_image_data = b"test image data"
        mock_capture.return_value = test_image_data
        mock_write_clipboard.return_value = True
        
        handler = ScreenshotHandler()
        
        # Mock compressor
        handler.compressor = Mock()
        compressed_data = b"compressed data"
        handler.compressor.compress.return_value = compressed_data
        
        # Test region selection
        start_point = (10, 10)
        end_point = (110, 110)
        
        handler._on_region_selected(start_point, end_point)
        
        # Verify calls
        mock_capture.assert_called_once_with(10, 10, 100, 100)
        handler.compressor.compress.assert_called_once_with(test_image_data)
        mock_write_clipboard.assert_called_once_with(compressed_data)
    
    @patch.object(ScreenshotHandler, '_capture_screen_region')
    def test_on_region_selected_capture_failure(self, mock_capture):
        """Test region selection with capture failure."""
        mock_capture.return_value = None
        
        handler = ScreenshotHandler()
        
        # Should not crash when capture fails
        handler._on_region_selected((10, 10), (110, 110))
        
        mock_capture.assert_called_once()
    
    def test_capture_region_and_compress_permission_denied(self):
        """Test capture when permission is denied."""
        handler = ScreenshotHandler()
        
        # Mock permission manager to deny permission
        handler.permission_manager = Mock()
        handler.permission_manager.ensure_permissions.return_value = False
        
        result = handler.capture_region_and_compress()
        
        assert result is False
        handler.permission_manager.ensure_permissions.assert_called_once()
    
    def test_capture_region_and_compress_exception(self):
        """Test capture with exception."""
        handler = ScreenshotHandler()
        
        # Mock permission manager to raise exception
        handler.permission_manager = Mock()
        handler.permission_manager.ensure_permissions.side_effect = Exception("Permission error")
        
        result = handler.capture_region_and_compress()
        
        assert result is False


class TestScreenshotHandlerIntegration:
    """Integration tests for screenshot handler."""
    
    def test_end_to_end_mock_workflow(self):
        """Test end-to-end workflow with mocked components."""
        handler = ScreenshotHandler()
        
        # Mock all external dependencies
        handler.permission_manager = Mock()
        handler.permission_manager.ensure_permissions.return_value = True
        
        # Mock clipboard
        with patch('system.screenshot_handler.NSPasteboard') as mock_pasteboard_class:
            mock_pasteboard = Mock()
            mock_pasteboard_class.generalPasteboard.return_value = mock_pasteboard
            mock_pasteboard.setData_forType_.return_value = True
            
            # Mock screen capture
            with patch('system.screenshot_handler.CGDisplayCreateImageForRect') as mock_capture:
                mock_capture.return_value = Mock()  # Mock CGImage
                
                # Mock image conversion
                with patch.object(handler, '_cgimage_to_png_data') as mock_convert:
                    test_data = b"test image data"
                    mock_convert.return_value = test_data
                    
                    # Test the workflow
                    handler._on_region_selected((0, 0), (100, 100))
                    
                    # Verify the flow
                    mock_capture.assert_called_once()
                    mock_convert.assert_called_once()
                    mock_pasteboard.setData_forType_.assert_called_once()