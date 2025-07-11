import logging
from Quartz import CGRequestScreenCaptureAccess, CGPreflightScreenCaptureAccess
from Cocoa import NSAlert, NSAlertFirstButtonReturn, NSAlertSecondButtonReturn

logger = logging.getLogger(__name__)


class PermissionManager:
    """Manages macOS permissions for screen capture."""
    
    def __init__(self):
        self.screen_capture_granted = False
    
    def check_screen_capture_permission(self):
        """
        Check if screen capture permission is granted.
        
        Returns:
            bool: True if permission is granted, False otherwise
        """
        try:
            # Check if we already have screen capture access
            has_access = CGPreflightScreenCaptureAccess()
            self.screen_capture_granted = has_access
            
            logger.info(f"Screen capture permission status: {has_access}")
            return has_access
            
        except Exception as e:
            logger.error(f"Error checking screen capture permission: {e}")
            return False
    
    def request_screen_capture_permission(self):
        """
        Request screen capture permission from the user.
        
        Returns:
            bool: True if permission was granted, False otherwise
        """
        try:
            # First check if we already have permission
            if self.check_screen_capture_permission():
                return True
            
            # Show user alert about permission requirement
            alert = NSAlert.alloc().init()
            alert.setMessageText_("Screen Recording Permission Required")
            alert.setInformativeText_(
                "SnapSqueeze needs screen recording permission to capture screenshots. "
                "Please click 'Request Permission' to open System Preferences, "
                "then enable screen recording for SnapSqueeze."
            )
            alert.addButtonWithTitle_("Request Permission")
            alert.addButtonWithTitle_("Cancel")
            
            response = alert.runModal()
            
            if response == NSAlertFirstButtonReturn:
                # Request permission - this will open System Preferences
                permission_granted = CGRequestScreenCaptureAccess()
                
                if permission_granted:
                    self.screen_capture_granted = True
                    logger.info("Screen capture permission granted")
                    return True
                else:
                    logger.warning("Screen capture permission denied")
                    self._show_permission_denied_alert()
                    return False
            else:
                logger.info("User cancelled permission request")
                return False
                
        except Exception as e:
            logger.error(f"Error requesting screen capture permission: {e}")
            return False
    
    def _show_permission_denied_alert(self):
        """Show alert when permission is denied."""
        alert = NSAlert.alloc().init()
        alert.setMessageText_("Permission Required")
        alert.setInformativeText_(
            "SnapSqueeze cannot function without screen recording permission. "
            "Please enable it in System Preferences > Security & Privacy > Privacy > Screen Recording."
        )
        alert.addButtonWithTitle_("OK")
        alert.runModal()
    
    def ensure_permissions(self):
        """
        Ensure all required permissions are granted.
        
        Returns:
            bool: True if all permissions are granted, False otherwise
        """
        if not self.check_screen_capture_permission():
            return self.request_screen_capture_permission()
        
        return True
    
    def get_permission_status(self):
        """
        Get current permission status.
        
        Returns:
            dict: Dictionary with permission status
        """
        return {
            'screen_capture': self.screen_capture_granted,
            'all_granted': self.screen_capture_granted
        }