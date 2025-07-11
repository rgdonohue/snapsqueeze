import pytest
import threading
import time
from unittest.mock import Mock, patch, MagicMock
from ui.notifications import NotificationManager, VisualFeedback
from ui.hotkey_manager import HotkeyManager


class TestNotificationManager:
    """Test notification manager functionality."""
    
    def test_init(self):
        """Test notification manager initialization."""
        manager = NotificationManager()
        
        assert manager.notification_center is not None
        assert manager.notification_queue == []
        assert manager.current_notification is None
    
    @patch('ui.notifications.NSUserNotificationCenter')
    def test_show_success(self, mock_center_class):
        """Test showing success notification."""
        mock_center = Mock()
        mock_center_class.defaultUserNotificationCenter.return_value = mock_center
        
        manager = NotificationManager()
        manager.show_success("Test Title", "Test Message")
        
        # Verify notification was delivered
        mock_center.deliverNotification_.assert_called_once()
    
    @patch('ui.notifications.NSUserNotificationCenter')
    def test_show_error(self, mock_center_class):
        """Test showing error notification."""
        mock_center = Mock()
        mock_center_class.defaultUserNotificationCenter.return_value = mock_center
        
        manager = NotificationManager()
        manager.show_error("Error Title", "Error Message")
        
        mock_center.deliverNotification_.assert_called_once()
    
    @patch('ui.notifications.NSUserNotificationCenter')
    def test_show_warning(self, mock_center_class):
        """Test showing warning notification."""
        mock_center = Mock()
        mock_center_class.defaultUserNotificationCenter.return_value = mock_center
        
        manager = NotificationManager()
        manager.show_warning("Warning Title", "Warning Message")
        
        mock_center.deliverNotification_.assert_called_once()
    
    @patch('ui.notifications.NSUserNotificationCenter')
    def test_show_info(self, mock_center_class):
        """Test showing info notification."""
        mock_center = Mock()
        mock_center_class.defaultUserNotificationCenter.return_value = mock_center
        
        manager = NotificationManager()
        manager.show_info("Info Title", "Info Message")
        
        mock_center.deliverNotification_.assert_called_once()
    
    @patch('ui.notifications.NSUserNotificationCenter')
    def test_show_compression_stats(self, mock_center_class):
        """Test showing compression statistics."""
        mock_center = Mock()
        mock_center_class.defaultUserNotificationCenter.return_value = mock_center
        
        manager = NotificationManager()
        manager.show_compression_stats(1000, 500, 50.0)
        
        mock_center.deliverNotification_.assert_called_once()
    
    @patch('ui.notifications.NSUserNotificationCenter')
    def test_show_toast(self, mock_center_class):
        """Test showing toast notification."""
        mock_center = Mock()
        mock_center_class.defaultUserNotificationCenter.return_value = mock_center
        
        manager = NotificationManager()
        manager.show_toast("Toast Message")
        
        mock_center.deliverNotification_.assert_called_once()
    
    @patch('ui.notifications.NSAlert')
    def test_show_alert(self, mock_alert_class):
        """Test showing alert dialog."""
        mock_alert = Mock()
        mock_alert_class.alloc.return_value.init.return_value = mock_alert
        mock_alert.runModal.return_value = 1000  # NSAlertFirstButtonReturn
        
        manager = NotificationManager()
        result = manager.show_alert("Test Title", "Test Message")
        
        assert result == 0  # First button
        mock_alert.setMessageText_.assert_called_once_with("Test Title")
        mock_alert.setInformativeText_.assert_called_once_with("Test Message")
        mock_alert.runModal.assert_called_once()
    
    @patch('ui.notifications.NSAlert')
    def test_show_permission_request(self, mock_alert_class):
        """Test showing permission request dialog."""
        mock_alert = Mock()
        mock_alert_class.alloc.return_value.init.return_value = mock_alert
        mock_alert.runModal.return_value = 1000  # NSAlertFirstButtonReturn
        
        manager = NotificationManager()
        result = manager.show_permission_request("Permission Title", "Permission Message")
        
        assert result is True  # Permission granted
        mock_alert.runModal.assert_called_once()
    
    @patch('ui.notifications.NSUserNotificationCenter')
    def test_clear_notifications(self, mock_center_class):
        """Test clearing all notifications."""
        mock_center = Mock()
        mock_center_class.defaultUserNotificationCenter.return_value = mock_center
        
        manager = NotificationManager()
        manager.clear_notifications()
        
        mock_center.removeAllDeliveredNotifications.assert_called_once()
    
    @patch('ui.notifications.NSUserNotificationCenter')
    def test_show_capture_status(self, mock_center_class):
        """Test showing capture status notifications."""
        mock_center = Mock()
        mock_center_class.defaultUserNotificationCenter.return_value = mock_center
        
        manager = NotificationManager()
        
        # Test different statuses
        statuses = ["starting", "capturing", "compressing", "complete", "error"]
        for status in statuses:
            manager.show_capture_status(status)
        
        # Should have called deliverNotification for each status
        assert mock_center.deliverNotification_.call_count == len(statuses)
    
    @patch('ui.notifications.NSUserNotificationCenter')
    def test_show_settings_changed(self, mock_center_class):
        """Test showing settings changed notification."""
        mock_center = Mock()
        mock_center_class.defaultUserNotificationCenter.return_value = mock_center
        
        manager = NotificationManager()
        manager.show_settings_changed("Compression Level", "50%")
        
        mock_center.deliverNotification_.assert_called_once()
    
    @patch('ui.notifications.NSUserNotificationCenter')
    def test_show_hotkey_conflict(self, mock_center_class):
        """Test showing hotkey conflict notification."""
        mock_center = Mock()
        mock_center_class.defaultUserNotificationCenter.return_value = mock_center
        
        manager = NotificationManager()
        manager.show_hotkey_conflict("Cmd+Option+4")
        
        mock_center.deliverNotification_.assert_called_once()


class TestVisualFeedback:
    """Test visual feedback functionality."""
    
    def test_init(self):
        """Test visual feedback initialization."""
        feedback = VisualFeedback()
        
        assert feedback.feedback_windows == []
    
    @patch('ui.notifications.NotificationManager')
    def test_show_capture_feedback(self, mock_manager_class):
        """Test showing capture feedback."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        
        feedback = VisualFeedback()
        feedback.show_capture_feedback(100, 100, 300, 200)
        
        # Should create a notification manager and show toast
        mock_manager.show_toast.assert_called_once()
    
    @patch('ui.notifications.NotificationManager')
    def test_show_compression_feedback(self, mock_manager_class):
        """Test showing compression feedback."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        
        feedback = VisualFeedback()
        
        # Test different compression ratios
        feedback.show_compression_feedback(60.0)  # Excellent
        feedback.show_compression_feedback(40.0)  # Good
        feedback.show_compression_feedback(20.0)  # Moderate
        
        # Should show toast for each
        assert mock_manager.show_toast.call_count == 3
    
    def test_cleanup(self):
        """Test cleanup of visual feedback."""
        feedback = VisualFeedback()
        
        # Add mock windows
        mock_window = Mock()
        feedback.feedback_windows.append(mock_window)
        
        feedback.cleanup()
        
        # Should close windows and clear list
        mock_window.close.assert_called_once()
        assert feedback.feedback_windows == []


class TestHotkeyManager:
    """Test hotkey manager functionality."""
    
    def test_init(self):
        """Test hotkey manager initialization."""
        manager = HotkeyManager()
        
        assert manager.registered_hotkeys == {}
        assert manager.event_tap is None
        assert manager.run_loop_source is None
        assert manager.is_monitoring is False
        assert manager.modifier_flags == 0
    
    def test_key_code_mapping(self):
        """Test key code mapping."""
        manager = HotkeyManager()
        
        # Test some key mappings
        assert manager.key_codes['4'] == 21
        assert manager.key_codes['a'] == 0
        assert manager.key_codes['space'] == 49
    
    def test_modifier_flags_mapping(self):
        """Test modifier flags mapping."""
        manager = HotkeyManager()
        
        # Test modifier mappings
        assert 'cmd' in manager.modifier_flags_map
        assert 'alt' in manager.modifier_flags_map
        assert 'shift' in manager.modifier_flags_map
        assert 'ctrl' in manager.modifier_flags_map
    
    def test_register_hotkey_with_key_name(self):
        """Test registering hotkey with key name."""
        manager = HotkeyManager()
        callback = Mock()
        
        # Mock the start_monitoring method to avoid system calls
        with patch.object(manager, 'start_monitoring'):
            manager.register_hotkey('4', ['cmd', 'alt'], callback)
        
        # Should have registered the hotkey
        assert len(manager.registered_hotkeys) == 1
        
        # Check hotkey details
        hotkey_id = list(manager.registered_hotkeys.keys())[0]
        hotkey = manager.registered_hotkeys[hotkey_id]
        
        assert hotkey['key_code'] == 21  # Key code for '4'
        assert hotkey['callback'] == callback
    
    def test_register_hotkey_with_key_code(self):
        """Test registering hotkey with key code."""
        manager = HotkeyManager()
        callback = Mock()
        
        with patch.object(manager, 'start_monitoring'):
            manager.register_hotkey(21, ['cmd', 'alt'], callback)
        
        assert len(manager.registered_hotkeys) == 1
    
    def test_register_hotkey_invalid_key_name(self):
        """Test registering hotkey with invalid key name."""
        manager = HotkeyManager()
        callback = Mock()
        
        with pytest.raises(ValueError, match="Unknown key name"):
            manager.register_hotkey('invalid_key', ['cmd'], callback)
    
    def test_register_hotkey_invalid_modifier(self):
        """Test registering hotkey with invalid modifier."""
        manager = HotkeyManager()
        callback = Mock()
        
        with pytest.raises(ValueError, match="Unknown modifier"):
            manager.register_hotkey('4', ['invalid_modifier'], callback)
    
    def test_unregister_hotkey(self):
        """Test unregistering hotkey."""
        manager = HotkeyManager()
        callback = Mock()
        
        with patch.object(manager, 'start_monitoring'):
            manager.register_hotkey('4', ['cmd', 'alt'], callback)
        
        # Should have one hotkey
        assert len(manager.registered_hotkeys) == 1
        
        with patch.object(manager, 'stop_monitoring'):
            manager.unregister_hotkey('4', ['cmd', 'alt'])
        
        # Should have no hotkeys
        assert len(manager.registered_hotkeys) == 0
    
    def test_get_registered_hotkeys(self):
        """Test getting registered hotkeys."""
        manager = HotkeyManager()
        callback = Mock()
        
        with patch.object(manager, 'start_monitoring'):
            manager.register_hotkey('4', ['cmd', 'alt'], callback)
        
        hotkeys = manager.get_registered_hotkeys()
        
        assert len(hotkeys) == 1
        assert hotkeys[0]['key'] == '4'
        assert 'cmd' in hotkeys[0]['modifiers']
        assert 'alt' in hotkeys[0]['modifiers']
    
    def test_cleanup(self):
        """Test cleanup of hotkey manager."""
        manager = HotkeyManager()
        callback = Mock()
        
        with patch.object(manager, 'start_monitoring'):
            manager.register_hotkey('4', ['cmd', 'alt'], callback)
        
        with patch.object(manager, 'stop_monitoring'):
            manager.cleanup()
        
        # Should have cleared all hotkeys
        assert len(manager.registered_hotkeys) == 0
        assert manager.event_tap is None
        assert manager.run_loop_source is None
    
    @patch('ui.hotkey_manager.CGEventTapCreate')
    @patch('ui.hotkey_manager.CFMachPortCreateRunLoopSource')
    @patch('ui.hotkey_manager.CFRunLoopGetMain')
    @patch('ui.hotkey_manager.CFRunLoopAddSource')
    @patch('ui.hotkey_manager.CGEventTapEnable')
    def test_start_monitoring(self, mock_enable, mock_add_source, mock_get_main, 
                            mock_create_source, mock_create_tap):
        """Test starting hotkey monitoring."""
        # Mock successful event tap creation
        mock_create_tap.return_value = Mock()
        mock_create_source.return_value = Mock()
        mock_get_main.return_value = Mock()
        
        manager = HotkeyManager()
        manager.start_monitoring()
        
        # Should have called the necessary functions
        mock_create_tap.assert_called_once()
        mock_create_source.assert_called_once()
        mock_enable.assert_called_once()
        
        assert manager.is_monitoring is True
    
    @patch('ui.hotkey_manager.CGEventTapCreate')
    def test_start_monitoring_failure(self, mock_create_tap):
        """Test starting hotkey monitoring with failure."""
        # Mock failed event tap creation
        mock_create_tap.return_value = None
        
        manager = HotkeyManager()
        
        with pytest.raises(RuntimeError, match="Failed to create event tap"):
            manager.start_monitoring()
    
    @patch('ui.hotkey_manager.CGEventTapEnable')
    def test_stop_monitoring(self, mock_enable):
        """Test stopping hotkey monitoring."""
        manager = HotkeyManager()
        manager.is_monitoring = True
        manager.event_tap = Mock()
        manager.run_loop_source = Mock()
        
        with patch('ui.hotkey_manager.CFRunLoopGetMain') as mock_get_main:
            with patch('ui.hotkey_manager.CFRunLoopRemoveSource') as mock_remove:
                mock_get_main.return_value = Mock()
                
                manager.stop_monitoring()
                
                # Should have disabled tap and removed from run loop
                mock_enable.assert_called_once_with(manager.event_tap, False)
                mock_remove.assert_called_once()
        
        assert manager.is_monitoring is False


class TestHotkeyManagerIntegration:
    """Integration tests for hotkey manager."""
    
    def test_register_and_unregister_workflow(self):
        """Test complete register and unregister workflow."""
        manager = HotkeyManager()
        callback = Mock()
        
        with patch.object(manager, 'start_monitoring'):
            with patch.object(manager, 'stop_monitoring'):
                # Register hotkey
                manager.register_hotkey('4', ['cmd', 'alt'], callback)
                assert len(manager.registered_hotkeys) == 1
                
                # Get registered hotkeys
                hotkeys = manager.get_registered_hotkeys()
                assert len(hotkeys) == 1
                
                # Unregister hotkey
                manager.unregister_hotkey('4', ['cmd', 'alt'])
                assert len(manager.registered_hotkeys) == 0
                
                # Cleanup
                manager.cleanup()
                assert len(manager.registered_hotkeys) == 0