import pytest
import time
import io
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import threading
import tempfile
import os

from core.image_compressor import ImageCompressor
from system.screenshot_handler import ScreenshotHandler
from system.permissions import PermissionManager
from ui.notifications import NotificationManager
from ui.hotkey_manager import HotkeyManager
from ui.menu_bar_app import SnapSqueezeApp
from core.error_handler import error_handler, ErrorCode
from core.performance_optimizer import performance_optimizer


class TestEndToEndIntegration:
    """End-to-end integration tests for SnapSqueeze."""
    
    def create_test_image(self, size=(500, 500), mode='RGB', color=(255, 0, 0)):
        """Create a test image."""
        image = Image.new(mode, size, color)
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        return buffer.getvalue()
    
    def test_image_compression_workflow(self):
        """Test complete image compression workflow."""
        # Create compressor
        compressor = ImageCompressor(target_scale=0.5, format='PNG')
        
        # Create test image
        image_data = self.create_test_image(size=(1000, 1000))
        
        # Compress image
        compressed_data = compressor.compress(image_data)
        
        # Verify compression
        assert compressed_data is not None
        assert len(compressed_data) > 0
        assert len(compressed_data) < len(image_data)  # Should be smaller
        
        # Verify compressed image is valid
        compressed_image = Image.open(io.BytesIO(compressed_data))
        assert compressed_image.size == (500, 500)  # 50% of original
        assert compressed_image.format == 'PNG'
    
    def test_screenshot_handler_integration(self):
        """Test screenshot handler integration."""
        handler = ScreenshotHandler()
        
        # Mock permission manager
        handler.permission_manager = Mock()
        handler.permission_manager.ensure_permissions.return_value = True
        
        # Mock clipboard write
        with patch.object(handler, 'write_to_clipboard') as mock_clipboard:
            mock_clipboard.return_value = True
            
            # Mock image capture
            with patch.object(handler, '_capture_screen_region') as mock_capture:
                test_image_data = self.create_test_image(size=(200, 200))
                mock_capture.return_value = test_image_data
                
                # Test region selection callback
                handler._on_region_selected((0, 0), (100, 100))
                
                # Verify capture was called
                mock_capture.assert_called_once_with(0, 0, 100, 100)
                
                # Verify clipboard was called
                mock_clipboard.assert_called_once()
    
    def test_permission_manager_integration(self):
        """Test permission manager integration."""
        manager = PermissionManager()
        
        # Test permission status
        status = manager.get_permission_status()
        assert 'screen_capture' in status
        assert 'all_granted' in status
        assert isinstance(status['screen_capture'], bool)
        assert isinstance(status['all_granted'], bool)
    
    def test_notification_manager_integration(self):
        """Test notification manager integration."""
        # Mock NSUserNotificationCenter
        with patch('ui.notifications.NSUserNotificationCenter') as mock_center_class:
            mock_center = Mock()
            mock_center_class.defaultUserNotificationCenter.return_value = mock_center
            
            # Create notification manager
            notification_manager = NotificationManager()
            
            # Test different types of notifications
            notification_manager.show_success("Test Success", "Success message")
            notification_manager.show_error("Test Error", "Error message")
            notification_manager.show_warning("Test Warning", "Warning message")
            notification_manager.show_info("Test Info", "Info message")
            
            # Verify notifications were delivered
            assert mock_center.deliverNotification_.call_count == 4
    
    def test_hotkey_manager_integration(self):
        """Test hotkey manager integration."""
        manager = HotkeyManager()
        
        # Test hotkey registration
        callback = Mock()
        
        # Mock system calls to avoid actual hotkey registration
        with patch('ui.hotkey_manager.CGEventTapCreate') as mock_create:
            with patch('ui.hotkey_manager.CFMachPortCreateRunLoopSource') as mock_source:
                with patch('ui.hotkey_manager.CFRunLoopGetMain') as mock_loop:
                    with patch('ui.hotkey_manager.CFRunLoopAddSource') as mock_add:
                        with patch('ui.hotkey_manager.CGEventTapEnable') as mock_enable:
                            mock_create.return_value = Mock()
                            mock_source.return_value = Mock()
                            mock_loop.return_value = Mock()
                            
                            # Register hotkey
                            manager.register_hotkey('4', ['cmd', 'alt'], callback)
                            
                            # Verify hotkey was registered
                            assert len(manager.registered_hotkeys) == 1
                            
                            # Get registered hotkeys
                            hotkeys = manager.get_registered_hotkeys()
                            assert len(hotkeys) == 1
                            assert hotkeys[0]['key'] == '4'
                            assert 'cmd' in hotkeys[0]['modifiers']
                            assert 'alt' in hotkeys[0]['modifiers']
    
    def test_error_handler_integration(self):
        """Test error handler integration."""
        # Set up notification manager
        notification_manager = NotificationManager()
        
        with patch('ui.notifications.NSUserNotificationCenter') as mock_center_class:
            mock_center = Mock()
            mock_center_class.defaultUserNotificationCenter.return_value = mock_center
            
            error_handler.set_notification_manager(notification_manager)
            
            # Test error handling
            test_error = ValueError("Test error")
            result = error_handler.handle_error(test_error, "test context")
            
            # Error should be handled
            assert isinstance(result, bool)
            
            # Check error statistics
            stats = error_handler.get_error_statistics()
            assert stats['total_errors'] > 0
    
    def test_performance_optimizer_integration(self):
        """Test performance optimizer integration."""
        # Create test image
        image_data = self.create_test_image(size=(800, 800))
        
        # Test optimization
        result = performance_optimizer.optimize_image_processing(
            image_data, 0.5, 'PNG'
        )
        
        assert result is not None
        assert len(result) > 0
        
        # Verify result is valid image
        result_image = Image.open(io.BytesIO(result))
        assert result_image.size == (400, 400)  # 50% of original
        
        # Check performance stats
        stats = performance_optimizer.get_performance_stats()
        assert stats['total_operations'] > 0
    
    def test_menu_bar_app_integration(self):
        """Test menu bar app integration."""
        # Mock rumps to avoid GUI
        with patch('ui.menu_bar_app.rumps') as mock_rumps:
            mock_app = Mock()
            mock_rumps.App.return_value = mock_app
            
            # Mock NSUserNotificationCenter
            with patch('ui.notifications.NSUserNotificationCenter') as mock_center_class:
                mock_center = Mock()
                mock_center_class.defaultUserNotificationCenter.return_value = mock_center
                
                # Create app
                app = SnapSqueezeApp()
                
                # Test app components
                assert app.screenshot_handler is not None
                assert app.permission_manager is not None
                assert app.notification_manager is not None
                assert app.hotkey_manager is not None
                
                # Test compression stats
                assert 'total_captures' in app.compression_stats
                assert 'total_saved_bytes' in app.compression_stats
                assert 'average_compression' in app.compression_stats


class TestErrorScenarios:
    """Test error scenarios and recovery."""
    
    def test_compression_with_invalid_data(self):
        """Test compression with invalid image data."""
        compressor = ImageCompressor()
        
        # Test with empty data
        result = compressor.compress(b'')
        assert result == b''  # Should return original (empty) data
        
        # Test with invalid image data
        result = compressor.compress(b'not an image')
        assert result == b'not an image'  # Should return original data
    
    def test_clipboard_error_handling(self):
        """Test clipboard error handling."""
        handler = ScreenshotHandler()
        
        # Mock clipboard failure
        with patch('system.screenshot_handler.NSPasteboard') as mock_pasteboard_class:
            mock_pasteboard = Mock()
            mock_pasteboard_class.generalPasteboard.return_value = mock_pasteboard
            mock_pasteboard.setData_forType_.return_value = False
            
            # Should raise ClipboardError
            with pytest.raises(Exception):  # Will be caught by error handler
                handler.write_to_clipboard(b'test data')
    
    def test_permission_denied_scenario(self):
        """Test permission denied scenario."""
        handler = ScreenshotHandler()
        
        # Mock permission denial
        handler.permission_manager = Mock()
        handler.permission_manager.ensure_permissions.return_value = False
        
        # Should raise ScreenshotError
        with pytest.raises(Exception):  # Will be caught by error handler
            handler.capture_region_and_compress()
    
    def test_memory_constraint_scenario(self):
        """Test memory constraint scenario."""
        compressor = ImageCompressor()
        
        # Mock low memory situation - fix numeric mock setup
        with patch('psutil.virtual_memory') as mock_memory:
            mock_memory_info = Mock()
            mock_memory_info.available = 50 * 1024 * 1024  # 50MB
            mock_memory_info.percent = 70.0  # Set numeric value for comparison
            mock_memory.return_value = mock_memory_info
            
            # Create large image data
            large_image_data = b'0' * (60 * 1024 * 1024)  # 60MB
            
            # Should handle memory constraint
            result = compressor.compress(large_image_data)
            assert result == large_image_data  # Should return original on validation failure


class TestPerformanceUnderLoad:
    """Test performance under various load conditions."""
    
    def create_test_image(self, size=(500, 500)):
        """Create a test image."""
        image = Image.new('RGB', size, color=(255, 0, 0))
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        return buffer.getvalue()
    
    def test_multiple_concurrent_compressions(self):
        """Test multiple concurrent compression operations."""
        compressor = ImageCompressor(target_scale=0.5)
        
        # Create test images
        images = [self.create_test_image(size=(300, 300)) for _ in range(5)]
        
        results = []
        start_time = time.time()
        
        # Compress all images
        for image_data in images:
            result = compressor.compress(image_data)
            results.append(result)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify all compressions succeeded
        assert len(results) == 5
        for result in results:
            assert result is not None
            assert len(result) > 0
        
        # Should complete within reasonable time
        assert total_time < 10.0  # 10 seconds max
        
        print(f"Processed {len(images)} images in {total_time:.2f} seconds")
    
    def test_compression_with_various_sizes(self):
        """Test compression with various image sizes."""
        compressor = ImageCompressor(target_scale=0.5)
        
        sizes = [(100, 100), (500, 500), (1000, 1000), (1500, 1500)]
        
        for size in sizes:
            image_data = self.create_test_image(size=size)
            
            start_time = time.time()
            result = compressor.compress(image_data)
            end_time = time.time()
            
            processing_time = end_time - start_time
            
            # Verify compression
            assert result is not None
            assert len(result) > 0
            
            # Verify result image
            result_image = Image.open(io.BytesIO(result))
            expected_size = (size[0] // 2, size[1] // 2)
            assert result_image.size == expected_size
            
            print(f"Size {size}: {processing_time:.3f}s, "
                  f"Compression ratio: {(1 - len(result) / len(image_data)) * 100:.1f}%")
    
    def test_memory_usage_stability(self):
        """Test memory usage stability over multiple operations."""
        compressor = ImageCompressor(target_scale=0.5)
        
        # Get initial memory usage
        import psutil
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Perform multiple compressions
        for i in range(10):
            image_data = self.create_test_image(size=(600, 600))
            result = compressor.compress(image_data)
            assert result is not None
            
            # Force garbage collection
            import gc
            gc.collect()
        
        # Check final memory usage
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        print(f"Memory increase: {memory_increase / 1024 / 1024:.2f} MB")
        
        # Memory increase should be minimal (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024  # 100MB


class TestFullApplicationWorkflow:
    """Test complete application workflow."""
    
    def create_test_image(self, size=(400, 400)):
        """Create a test image."""
        image = Image.new('RGB', size, color=(255, 0, 0))
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        return buffer.getvalue()
    
    def test_complete_capture_workflow(self):
        """Test complete capture workflow from trigger to clipboard."""
        # Mock all system dependencies
        with patch('ui.menu_bar_app.rumps') as mock_rumps:
            with patch('ui.notifications.NSUserNotificationCenter') as mock_notif:
                with patch('system.screenshot_handler.NSPasteboard') as mock_clipboard:
                    with patch('ui.hotkey_manager.CGEventTapCreate') as mock_hotkey:
                        # Setup mocks
                        mock_app = Mock()
                        mock_rumps.App.return_value = mock_app
                        
                        mock_notif_center = Mock()
                        mock_notif.defaultUserNotificationCenter.return_value = mock_notif_center
                        
                        mock_pasteboard = Mock()
                        mock_clipboard.generalPasteboard.return_value = mock_pasteboard
                        mock_pasteboard.setData_forType_.return_value = True
                        
                        mock_hotkey.return_value = Mock()
                        
                        # Create app
                        app = SnapSqueezeApp()
                        
                        # Mock permission success
                        app.permission_manager.ensure_permissions = Mock(return_value=True)
                        
                        # Mock screen capture
                        test_image_data = self.create_test_image(size=(200, 200))
                        app.screenshot_handler._capture_screen_region = Mock(return_value=test_image_data)
                        
                        # Mock overlay
                        app.screenshot_handler.overlay = Mock()
                        app.screenshot_handler.overlay.show_overlay = Mock()
                        
                        # Trigger capture
                        success = app.screenshot_handler.capture_region_and_compress()
                        assert success
                        
                        # Simulate region selection
                        app.screenshot_handler._on_region_selected((0, 0), (100, 100))
                        
                        # Verify workflow
                        app.screenshot_handler._capture_screen_region.assert_called_once()
                        mock_pasteboard.setData_forType_.assert_called_once()
    
    def test_app_error_recovery(self):
        """Test application error recovery."""
        # Mock system dependencies
        with patch('ui.menu_bar_app.rumps') as mock_rumps:
            with patch('ui.notifications.NSUserNotificationCenter') as mock_notif:
                # Setup mocks
                mock_app = Mock()
                mock_rumps.App.return_value = mock_app
                
                mock_notif_center = Mock()
                mock_notif.defaultUserNotificationCenter.return_value = mock_notif_center
                
                # Create app
                app = SnapSqueezeApp()
                
                # Test error recovery
                test_error = ValueError("Test error")
                recovery_success = error_handler.handle_error(test_error, "test context")
                
                # Should handle error gracefully
                assert isinstance(recovery_success, bool)
                
                # Check error statistics
                stats = error_handler.get_error_statistics()
                assert stats['total_errors'] > 0
    
    def test_performance_monitoring(self):
        """Test performance monitoring during operation."""
        # Test performance optimizer
        image_data = self.create_test_image(size=(600, 600))
        
        # Reset stats
        performance_optimizer.reset_stats()
        
        # Perform operation
        result = performance_optimizer.optimize_image_processing(
            image_data, 0.5, 'PNG'
        )
        
        # Verify result
        assert result is not None
        assert len(result) > 0
        
        # Check performance stats
        stats = performance_optimizer.get_performance_stats()
        assert stats['total_operations'] == 1
        assert stats['average_time'] > 0
        
        print(f"Performance stats: {stats}")


if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v"])