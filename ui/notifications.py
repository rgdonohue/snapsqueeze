import logging
from Cocoa import (
    NSUserNotificationCenter, NSUserNotification, NSUserNotificationDefaultSoundName,
    NSAlert, NSAlertFirstButtonReturn, NSAlertSecondButtonReturn, NSAlertThirdButtonReturn,
    NSAlertStyle, NSApplication, NSApp
)
from Foundation import NSTimer, NSRunLoop, NSDefaultRunLoopMode
import threading
import time

logger = logging.getLogger(__name__)


class NotificationManager:
    """Manages user notifications and feedback."""
    
    def __init__(self):
        self.notification_center = NSUserNotificationCenter.defaultUserNotificationCenter()
        self.notification_queue = []
        self.current_notification = None
        
        # Set up notification center delegate if needed
        # self.notification_center.setDelegate_(self)
        
        logger.info("Notification manager initialized")
    
    def show_success(self, title, message, sound=True):
        """
        Show success notification.
        
        Args:
            title (str): Notification title
            message (str): Notification message
            sound (bool): Whether to play sound
        """
        self._show_notification(title, message, "success", sound)
    
    def show_error(self, title, message, sound=True):
        """
        Show error notification.
        
        Args:
            title (str): Notification title
            message (str): Notification message
            sound (bool): Whether to play sound
        """
        self._show_notification(title, message, "error", sound)
    
    def show_warning(self, title, message, sound=True):
        """
        Show warning notification.
        
        Args:
            title (str): Notification title
            message (str): Notification message
            sound (bool): Whether to play sound
        """
        self._show_notification(title, message, "warning", sound)
    
    def show_info(self, title, message, sound=False):
        """
        Show info notification.
        
        Args:
            title (str): Notification title
            message (str): Notification message
            sound (bool): Whether to play sound
        """
        self._show_notification(title, message, "info", sound)
    
    def _show_notification(self, title, message, notification_type="info", sound=True):
        """
        Show a notification.
        
        Args:
            title (str): Notification title
            message (str): Notification message
            notification_type (str): Type of notification
            sound (bool): Whether to play sound
        """
        try:
            # Create notification
            notification = NSUserNotification.alloc().init()
            notification.setTitle_(title)
            notification.setInformativeText_(message)
            notification.setIdentifier_(f"snapsqueeze_{notification_type}_{int(time.time())}")
            
            # Set sound
            if sound:
                notification.setSoundName_(NSUserNotificationDefaultSoundName)
            
            # Add emoji based on type
            emoji_map = {
                "success": "✅",
                "error": "❌",
                "warning": "⚠️",
                "info": "ℹ️"
            }
            
            if notification_type in emoji_map:
                notification.setTitle_(f"{emoji_map[notification_type]} {title}")
            
            # Deliver notification
            self.notification_center.deliverNotification_(notification)
            
            # Store current notification
            self.current_notification = notification
            
            logger.info(f"Notification shown: {notification_type} - {title}")
            
        except Exception as e:
            logger.error(f"Error showing notification: {e}")
    
    def show_compression_stats(self, original_size, compressed_size, compression_ratio):
        """
        Show compression statistics notification.
        
        Args:
            original_size (int): Original file size in bytes
            compressed_size (int): Compressed file size in bytes
            compression_ratio (float): Compression ratio percentage
        """
        try:
            # Format sizes
            def format_size(size):
                if size < 1024:
                    return f"{size} B"
                elif size < 1024 * 1024:
                    return f"{size / 1024:.1f} KB"
                else:
                    return f"{size / (1024 * 1024):.1f} MB"
            
            original_str = format_size(original_size)
            compressed_str = format_size(compressed_size)
            
            title = "Screenshot Compressed"
            message = f"Size: {original_str} → {compressed_str} ({compression_ratio:.1f}% reduction)"
            
            self.show_success(title, message)
            
        except Exception as e:
            logger.error(f"Error showing compression stats: {e}")
    
    def show_toast(self, message, duration=2.0):
        """
        Show a simple toast notification.
        
        Args:
            message (str): Toast message
            duration (float): Duration in seconds
        """
        try:
            # For simplicity, use regular notification
            # In a full implementation, you might create a custom overlay
            self.show_info("SnapSqueeze", message, sound=False)
            
        except Exception as e:
            logger.error(f"Error showing toast: {e}")
    
    def show_alert(self, title, message, alert_type="info", buttons=None):
        """
        Show an alert dialog.
        
        Args:
            title (str): Alert title
            message (str): Alert message
            alert_type (str): Type of alert ("info", "warning", "error")
            buttons (list): List of button titles
        
        Returns:
            int: Button index pressed (0-based)
        """
        try:
            # Create alert
            alert = NSAlert.alloc().init()
            alert.setMessageText_(title)
            alert.setInformativeText_(message)
            
            # Set alert style
            if alert_type == "warning":
                alert.setAlertStyle_(NSAlertStyle.warning)
            elif alert_type == "error":
                alert.setAlertStyle_(NSAlertStyle.critical)
            else:
                alert.setAlertStyle_(NSAlertStyle.informational)
            
            # Add buttons
            if buttons:
                for button_title in buttons:
                    alert.addButtonWithTitle_(button_title)
            else:
                alert.addButtonWithTitle_("OK")
            
            # Run modal
            response = alert.runModal()
            
            # Convert response to button index
            if response == NSAlertFirstButtonReturn:
                return 0
            elif response == NSAlertSecondButtonReturn:
                return 1
            elif response == NSAlertThirdButtonReturn:
                return 2
            else:
                return response - NSAlertFirstButtonReturn
            
        except Exception as e:
            logger.error(f"Error showing alert: {e}")
            return 0
    
    def show_permission_request(self, title, message):
        """
        Show permission request dialog.
        
        Args:
            title (str): Dialog title
            message (str): Dialog message
        
        Returns:
            bool: True if user granted permission, False otherwise
        """
        try:
            response = self.show_alert(
                title,
                message,
                alert_type="warning",
                buttons=["Grant Permission", "Cancel"]
            )
            
            return response == 0  # First button (Grant Permission)
            
        except Exception as e:
            logger.error(f"Error showing permission request: {e}")
            return False
    
    def clear_notifications(self):
        """Clear all delivered notifications."""
        try:
            self.notification_center.removeAllDeliveredNotifications()
            logger.info("All notifications cleared")
            
        except Exception as e:
            logger.error(f"Error clearing notifications: {e}")
    
    def remove_notification(self, notification):
        """
        Remove a specific notification.
        
        Args:
            notification: The notification to remove
        """
        try:
            self.notification_center.removeDeliveredNotification_(notification)
            
        except Exception as e:
            logger.error(f"Error removing notification: {e}")
    
    def show_capture_status(self, status):
        """
        Show capture status notification.
        
        Args:
            status (str): Status message ("starting", "capturing", "compressing", "complete", "error")
        """
        try:
            status_messages = {
                "starting": ("Starting Capture", "Preparing to capture screen region..."),
                "capturing": ("Capturing", "Select region to capture..."),
                "compressing": ("Compressing", "Optimizing image size..."),
                "complete": ("Complete", "Image copied to clipboard!"),
                "error": ("Error", "Failed to capture screenshot")
            }
            
            if status in status_messages:
                title, message = status_messages[status]
                
                if status == "complete":
                    self.show_success(title, message)
                elif status == "error":
                    self.show_error(title, message)
                else:
                    self.show_info(title, message, sound=False)
            
        except Exception as e:
            logger.error(f"Error showing capture status: {e}")
    
    def show_settings_changed(self, setting_name, new_value):
        """
        Show settings changed notification.
        
        Args:
            setting_name (str): Name of the setting
            new_value (str): New value
        """
        try:
            title = "Settings Updated"
            message = f"{setting_name}: {new_value}"
            self.show_info(title, message, sound=False)
            
        except Exception as e:
            logger.error(f"Error showing settings notification: {e}")
    
    def show_hotkey_conflict(self, hotkey):
        """
        Show hotkey conflict notification.
        
        Args:
            hotkey (str): Conflicting hotkey
        """
        try:
            title = "Hotkey Conflict"
            message = f"Hotkey {hotkey} is already in use by another application."
            self.show_warning(title, message)
            
        except Exception as e:
            logger.error(f"Error showing hotkey conflict: {e}")


class VisualFeedback:
    """Provides visual feedback for user actions."""
    
    def __init__(self):
        self.feedback_windows = []
        
    def show_capture_feedback(self, x, y, width, height):
        """
        Show visual feedback for capture area.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            width (int): Width
            height (int): Height
        """
        try:
            # Create a brief visual indicator
            # This could be a colored border or flash effect
            # For now, we'll use a simple notification
            
            feedback_msg = f"Captured {width}x{height} region"
            NotificationManager().show_toast(feedback_msg)
            
        except Exception as e:
            logger.error(f"Error showing capture feedback: {e}")
    
    def show_compression_feedback(self, compression_ratio):
        """
        Show visual feedback for compression.
        
        Args:
            compression_ratio (float): Compression ratio percentage
        """
        try:
            if compression_ratio > 50:
                emoji = "🚀"
                quality = "Excellent"
            elif compression_ratio > 30:
                emoji = "✨"
                quality = "Good"
            else:
                emoji = "📦"
                quality = "Moderate"
            
            feedback_msg = f"{emoji} {quality} compression: {compression_ratio:.1f}%"
            NotificationManager().show_toast(feedback_msg)
            
        except Exception as e:
            logger.error(f"Error showing compression feedback: {e}")
    
    def cleanup(self):
        """Clean up visual feedback resources."""
        try:
            # Close any open feedback windows
            for window in self.feedback_windows:
                if window:
                    window.close()
            
            self.feedback_windows.clear()
            
        except Exception as e:
            logger.error(f"Error cleaning up visual feedback: {e}")