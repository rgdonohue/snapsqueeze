import rumps
import logging
import threading
from system.screenshot_handler import ScreenshotHandler
from system.permissions import PermissionManager
from ui.notifications import NotificationManager
from ui.hotkey_manager import HotkeyManager

logger = logging.getLogger(__name__)


class SnapSqueezeApp(rumps.App):
    """Main menu bar application for SnapSqueeze."""
    
    def __init__(self):
        # Initialize with app name and icon
        super(SnapSqueezeApp, self).__init__(
            "SnapSqueeze",
            icon="assets/icon.png",
            quit_button=None  # We'll add a custom quit button
        )
        
        # Initialize components
        self.screenshot_handler = ScreenshotHandler()
        self.permission_manager = PermissionManager()
        self.notification_manager = NotificationManager()
        self.hotkey_manager = HotkeyManager()
        
        # App state
        self.is_capturing = False
        self.compression_stats = {
            'total_captures': 0,
            'total_saved_bytes': 0,
            'average_compression': 0.0
        }
        
        # Setup menu
        self.setup_menu()
        
        # Setup hotkeys
        self.setup_hotkeys()
        
        # Check permissions on startup
        self.check_permissions_on_startup()
        
        logger.info("SnapSqueeze application initialized")
    
    def setup_menu(self):
        """Setup the menu bar menu items."""
        self.menu = [
            "Capture & Compress",
            None,  # Separator
            "Preferences",
            "Statistics",
            None,  # Separator
            "About SnapSqueeze",
            "Check Permissions",
            None,  # Separator
            "Quit SnapSqueeze"
        ]
    
    def setup_hotkeys(self):
        """Setup global hotkeys."""
        try:
            # Register Cmd+Option+4 hotkey
            self.hotkey_manager.register_hotkey(
                key_code=21,  # Key code for '4'
                modifiers=['cmd', 'alt'],
                callback=self.hotkey_capture_triggered
            )
            logger.info("Global hotkey Cmd+Option+4 registered")
            
        except Exception as e:
            logger.error(f"Failed to register hotkey: {e}")
            self.notification_manager.show_error(
                "Hotkey Registration Failed",
                "Could not register Cmd+Option+4 hotkey. Use menu instead."
            )
    
    def check_permissions_on_startup(self):
        """Check and request permissions on startup."""
        def check_permissions():
            try:
                if not self.permission_manager.check_screen_capture_permission():
                    # Show notification about permission requirement
                    self.notification_manager.show_info(
                        "Permission Required",
                        "Please grant screen recording permission in System Preferences."
                    )
                    
                    # Request permission
                    self.permission_manager.request_screen_capture_permission()
                    
            except Exception as e:
                logger.error(f"Error checking permissions: {e}")
        
        # Run permission check in background thread
        threading.Thread(target=check_permissions, daemon=True).start()
    
    @rumps.clicked("Capture & Compress")
    def menu_capture_clicked(self, _):
        """Handle menu item click for capture."""
        self.trigger_capture()
    
    @rumps.clicked("Preferences")
    def menu_preferences_clicked(self, _):
        """Handle preferences menu click."""
        self.show_preferences()
    
    @rumps.clicked("Statistics")
    def menu_statistics_clicked(self, _):
        """Handle statistics menu click."""
        self.show_statistics()
    
    @rumps.clicked("About SnapSqueeze")
    def menu_about_clicked(self, _):
        """Handle about menu click."""
        self.show_about()
    
    @rumps.clicked("Check Permissions")
    def menu_check_permissions_clicked(self, _):
        """Handle check permissions menu click."""
        self.check_permissions()
    
    @rumps.clicked("Quit SnapSqueeze")
    def menu_quit_clicked(self, _):
        """Handle quit menu click."""
        self.quit_application()
    
    def hotkey_capture_triggered(self):
        """Handle hotkey triggered capture."""
        logger.info("Hotkey capture triggered")
        self.trigger_capture()
    
    def trigger_capture(self):
        """Trigger screenshot capture and compression."""
        if self.is_capturing:
            logger.info("Capture already in progress, ignoring request")
            return
        
        try:
            self.is_capturing = True
            
            # Update menu to show capture in progress
            self.menu["Capture & Compress"].title = "Capturing..."
            
            # Check permissions first
            if not self.permission_manager.check_screen_capture_permission():
                self.notification_manager.show_error(
                    "Permission Required",
                    "Screen recording permission is required for capturing screenshots."
                )
                return
            
            # Start capture in background thread
            def capture_thread():
                try:
                    success = self.screenshot_handler.capture_region_and_compress()
                    
                    if success:
                        # Update statistics
                        self.compression_stats['total_captures'] += 1
                        
                        # Show success notification
                        self.notification_manager.show_success(
                            "Screenshot Captured",
                            "Screenshot compressed and copied to clipboard"
                        )
                        
                        logger.info("Screenshot capture completed successfully")
                    else:
                        self.notification_manager.show_error(
                            "Capture Failed",
                            "Failed to capture screenshot. Please try again."
                        )
                        
                except Exception as e:
                    logger.error(f"Error during capture: {e}")
                    self.notification_manager.show_error(
                        "Capture Error",
                        f"An error occurred during capture: {str(e)}"
                    )
                finally:
                    # Reset capture state
                    self.is_capturing = False
                    self.menu["Capture & Compress"].title = "Capture & Compress"
            
            threading.Thread(target=capture_thread, daemon=True).start()
            
        except Exception as e:
            logger.error(f"Error triggering capture: {e}")
            self.is_capturing = False
            self.menu["Capture & Compress"].title = "Capture & Compress"
            self.notification_manager.show_error(
                "Capture Error",
                "Failed to start capture process"
            )
    
    def show_preferences(self):
        """Show preferences window."""
        try:
            # Create preferences window
            window = rumps.Window(
                title="SnapSqueeze Preferences",
                message="Configure SnapSqueeze settings:",
                default_text="",
                dimensions=(300, 200)
            )
            
            # Add compression scale options
            response = rumps.alert(
                title="Compression Settings",
                message="Choose compression level:",
                alert_style=rumps.AlertStyle.informational,
                other_button="50% (Default)",
                cancel_button="25% (High)",
                ok_button="75% (Low)"
            )
            
            # Handle response
            if response == 1:  # OK button (75%)
                self.screenshot_handler.compressor.target_scale = 0.75
                scale_text = "75% (Low compression)"
            elif response == 0:  # Cancel button (25%)
                self.screenshot_handler.compressor.target_scale = 0.25
                scale_text = "25% (High compression)"
            else:  # Other button (50%)
                self.screenshot_handler.compressor.target_scale = 0.5
                scale_text = "50% (Default)"
            
            self.notification_manager.show_info(
                "Settings Updated",
                f"Compression level set to {scale_text}"
            )
            
        except Exception as e:
            logger.error(f"Error showing preferences: {e}")
            self.notification_manager.show_error(
                "Preferences Error",
                "Failed to open preferences"
            )
    
    def show_statistics(self):
        """Show usage statistics."""
        try:
            stats = self.compression_stats
            
            # Calculate average compression if we have data
            if stats['total_captures'] > 0 and stats['total_saved_bytes'] > 0:
                avg_compression = (stats['total_saved_bytes'] / stats['total_captures']) / 1024  # KB
                avg_compression_text = f"{avg_compression:.1f} KB"
            else:
                avg_compression_text = "No data yet"
            
            message = (
                f"Total screenshots captured: {stats['total_captures']}\n"
                f"Total bytes saved: {stats['total_saved_bytes']:,}\n"
                f"Average compression: {avg_compression_text}\n"
                f"Current scale: {int(self.screenshot_handler.compressor.target_scale * 100)}%"
            )
            
            rumps.alert(
                title="SnapSqueeze Statistics",
                message=message,
                alert_style=rumps.AlertStyle.informational
            )
            
        except Exception as e:
            logger.error(f"Error showing statistics: {e}")
            self.notification_manager.show_error(
                "Statistics Error",
                "Failed to display statistics"
            )
    
    def show_about(self):
        """Show about dialog."""
        try:
            about_message = (
                "SnapSqueeze v1.0.0\n\n"
                "A clipboard-first screenshot compressor for macOS\n\n"
                "• Capture regions with Cmd+Option+4\n"
                "• Automatic compression and clipboard copy\n"
                "• Configurable compression levels\n\n"
                "Shrink Your Shots. Boost Your Flow."
            )
            
            rumps.alert(
                title="About SnapSqueeze",
                message=about_message,
                alert_style=rumps.AlertStyle.informational
            )
            
        except Exception as e:
            logger.error(f"Error showing about: {e}")
    
    def check_permissions(self):
        """Check and display current permissions."""
        try:
            status = self.permission_manager.get_permission_status()
            
            if status['all_granted']:
                message = "✓ All permissions granted\n✓ Screen recording: Enabled"
                title = "Permissions OK"
                alert_style = rumps.AlertStyle.informational
            else:
                message = "✗ Missing permissions\n✗ Screen recording: Disabled"
                title = "Permissions Required"
                alert_style = rumps.AlertStyle.warning
            
            response = rumps.alert(
                title=title,
                message=message,
                alert_style=alert_style,
                other_button="Request Permissions" if not status['all_granted'] else None
            )
            
            # If user clicked "Request Permissions"
            if response == 2:  # Other button
                self.permission_manager.request_screen_capture_permission()
                
        except Exception as e:
            logger.error(f"Error checking permissions: {e}")
            self.notification_manager.show_error(
                "Permission Check Error",
                "Failed to check permissions"
            )
    
    def quit_application(self):
        """Quit the application."""
        try:
            # Cleanup hotkeys
            self.hotkey_manager.cleanup()
            
            # Show goodbye message
            logger.info("SnapSqueeze application quitting")
            
            # Quit the app
            rumps.quit_application()
            
        except Exception as e:
            logger.error(f"Error during quit: {e}")
            # Force quit if there's an error
            rumps.quit_application()


def main():
    """Main entry point for the application."""
    try:
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Create and run the app
        app = SnapSqueezeApp()
        app.run()
        
    except Exception as e:
        logger.error(f"Fatal error starting application: {e}")
        print(f"Failed to start SnapSqueeze: {e}")


if __name__ == "__main__":
    main()