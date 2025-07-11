import logging
import traceback
import sys
from enum import Enum
from typing import Optional, Dict, Any, Callable
from functools import wraps
import psutil
import os

logger = logging.getLogger(__name__)


class ErrorCode(Enum):
    """Error codes for different types of failures."""
    
    # General errors
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    SYSTEM_ERROR = "SYSTEM_ERROR"
    
    # Image processing errors
    IMAGE_LOAD_ERROR = "IMAGE_LOAD_ERROR"
    IMAGE_SAVE_ERROR = "IMAGE_SAVE_ERROR"
    IMAGE_COMPRESS_ERROR = "IMAGE_COMPRESS_ERROR"
    IMAGE_TOO_LARGE = "IMAGE_TOO_LARGE"
    INVALID_IMAGE_FORMAT = "INVALID_IMAGE_FORMAT"
    
    # Screenshot errors
    SCREENSHOT_CAPTURE_ERROR = "SCREENSHOT_CAPTURE_ERROR"
    REGION_SELECTION_ERROR = "REGION_SELECTION_ERROR"
    DISPLAY_ACCESS_ERROR = "DISPLAY_ACCESS_ERROR"
    
    # Clipboard errors
    CLIPBOARD_ACCESS_ERROR = "CLIPBOARD_ACCESS_ERROR"
    CLIPBOARD_WRITE_ERROR = "CLIPBOARD_WRITE_ERROR"
    
    # UI errors
    UI_INITIALIZATION_ERROR = "UI_INITIALIZATION_ERROR"
    HOTKEY_REGISTRATION_ERROR = "HOTKEY_REGISTRATION_ERROR"
    NOTIFICATION_ERROR = "NOTIFICATION_ERROR"
    
    # Memory errors
    OUT_OF_MEMORY = "OUT_OF_MEMORY"
    MEMORY_ALLOCATION_ERROR = "MEMORY_ALLOCATION_ERROR"
    
    # Performance errors
    OPERATION_TIMEOUT = "OPERATION_TIMEOUT"
    RESOURCE_EXHAUSTED = "RESOURCE_EXHAUSTED"


class SnapSqueezeError(Exception):
    """Base exception for SnapSqueeze errors."""
    
    def __init__(self, message: str, error_code: ErrorCode, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = None
        
        # Log the error
        logger.error(f"SnapSqueezeError: {error_code.value} - {message}")
        if details:
            logger.error(f"Error details: {details}")


class ImageProcessingError(SnapSqueezeError):
    """Exception for image processing related errors."""
    pass


class ScreenshotError(SnapSqueezeError):
    """Exception for screenshot capture related errors."""
    pass


class ClipboardError(SnapSqueezeError):
    """Exception for clipboard operation errors."""
    pass


class UIError(SnapSqueezeError):
    """Exception for UI related errors."""
    pass


class MemoryError(SnapSqueezeError):
    """Exception for memory related errors."""
    pass


class ErrorHandler:
    """Centralized error handling and recovery."""
    
    def __init__(self):
        self.error_stats = {
            'total_errors': 0,
            'error_counts': {},
            'last_errors': []
        }
        self.recovery_strategies = {}
        self.notification_manager = None
        
    def set_notification_manager(self, notification_manager):
        """Set the notification manager for user feedback."""
        self.notification_manager = notification_manager
    
    def handle_error(self, error: Exception, context: str = "", notify_user: bool = True) -> bool:
        """
        Handle an error with appropriate recovery strategy.
        
        Args:
            error: The exception that occurred
            context: Additional context about where the error occurred
            notify_user: Whether to notify the user about the error
            
        Returns:
            bool: True if error was handled and recovery was successful
        """
        try:
            # Update error statistics
            self._update_error_stats(error)
            
            # Log the error
            logger.error(f"Error in {context}: {str(error)}")
            logger.error(f"Error traceback: {traceback.format_exc()}")
            
            # Determine error type and code
            error_code = self._classify_error(error)
            
            # Try recovery strategy
            recovery_success = self._attempt_recovery(error, error_code, context)
            
            # Notify user if requested
            if notify_user:
                self._notify_user_of_error(error, error_code, context, recovery_success)
            
            return recovery_success
            
        except Exception as e:
            logger.critical(f"Error in error handler: {e}")
            return False
    
    def _update_error_stats(self, error: Exception):
        """Update error statistics."""
        self.error_stats['total_errors'] += 1
        
        error_type = type(error).__name__
        if error_type not in self.error_stats['error_counts']:
            self.error_stats['error_counts'][error_type] = 0
        self.error_stats['error_counts'][error_type] += 1
        
        # Keep track of last 10 errors
        self.error_stats['last_errors'].append({
            'type': error_type,
            'message': str(error),
            'timestamp': logger.getEffectiveLevel()
        })
        
        if len(self.error_stats['last_errors']) > 10:
            self.error_stats['last_errors'].pop(0)
    
    def _classify_error(self, error: Exception) -> ErrorCode:
        """Classify error and return appropriate error code."""
        error_type = type(error).__name__
        error_message = str(error).lower()
        
        # Classification based on error type
        if isinstance(error, SnapSqueezeError):
            return error.error_code
        elif isinstance(error, PermissionError):
            return ErrorCode.PERMISSION_DENIED
        elif isinstance(error, OSError):
            return ErrorCode.SYSTEM_ERROR
        elif isinstance(error, MemoryError):
            return ErrorCode.OUT_OF_MEMORY
        elif isinstance(error, TimeoutError):
            return ErrorCode.OPERATION_TIMEOUT
        
        # Classification based on error message
        if 'memory' in error_message or 'allocation' in error_message:
            return ErrorCode.MEMORY_ALLOCATION_ERROR
        elif 'clipboard' in error_message:
            return ErrorCode.CLIPBOARD_ACCESS_ERROR
        elif 'image' in error_message or 'pil' in error_message:
            return ErrorCode.IMAGE_LOAD_ERROR
        elif 'screenshot' in error_message or 'capture' in error_message:
            return ErrorCode.SCREENSHOT_CAPTURE_ERROR
        elif 'hotkey' in error_message:
            return ErrorCode.HOTKEY_REGISTRATION_ERROR
        elif 'notification' in error_message:
            return ErrorCode.NOTIFICATION_ERROR
        
        return ErrorCode.UNKNOWN_ERROR
    
    def _attempt_recovery(self, error: Exception, error_code: ErrorCode, context: str) -> bool:
        """Attempt to recover from the error."""
        recovery_strategy = self.recovery_strategies.get(error_code)
        
        if recovery_strategy:
            try:
                return recovery_strategy(error, context)
            except Exception as e:
                logger.error(f"Recovery strategy failed: {e}")
                return False
        
        # Default recovery strategies
        if error_code == ErrorCode.OUT_OF_MEMORY:
            return self._recover_from_memory_error()
        elif error_code == ErrorCode.PERMISSION_DENIED:
            return self._recover_from_permission_error()
        elif error_code in [ErrorCode.IMAGE_LOAD_ERROR, ErrorCode.IMAGE_COMPRESS_ERROR]:
            return self._recover_from_image_error()
        elif error_code == ErrorCode.CLIPBOARD_ACCESS_ERROR:
            return self._recover_from_clipboard_error()
        
        return False
    
    def _recover_from_memory_error(self) -> bool:
        """Attempt to recover from memory errors."""
        try:
            # Force garbage collection
            import gc
            gc.collect()
            
            # Check available memory
            memory_info = psutil.virtual_memory()
            available_memory_mb = memory_info.available / (1024 * 1024)
            
            if available_memory_mb < 100:  # Less than 100MB available
                logger.warning("Low memory detected, recovery may not be possible")
                return False
            
            logger.info("Memory cleanup completed")
            return True
            
        except Exception as e:
            logger.error(f"Memory recovery failed: {e}")
            return False
    
    def _recover_from_permission_error(self) -> bool:
        """Attempt to recover from permission errors."""
        try:
            # For permission errors, we can't automatically recover
            # but we can provide guidance to the user
            logger.info("Permission error detected, user intervention required")
            return False
            
        except Exception as e:
            logger.error(f"Permission recovery failed: {e}")
            return False
    
    def _recover_from_image_error(self) -> bool:
        """Attempt to recover from image processing errors."""
        try:
            # For image errors, we can try to clear any cached images
            # and reset the image compressor
            logger.info("Attempting image processing recovery")
            
            # Force garbage collection to clear image buffers
            import gc
            gc.collect()
            
            return True
            
        except Exception as e:
            logger.error(f"Image processing recovery failed: {e}")
            return False
    
    def _recover_from_clipboard_error(self) -> bool:
        """Attempt to recover from clipboard errors."""
        try:
            # For clipboard errors, we can try to clear the clipboard
            # and reset the pasteboard
            logger.info("Attempting clipboard recovery")
            
            # Try to clear clipboard
            from Cocoa import NSPasteboard
            pasteboard = NSPasteboard.generalPasteboard()
            pasteboard.clearContents()
            
            return True
            
        except Exception as e:
            logger.error(f"Clipboard recovery failed: {e}")
            return False
    
    def _notify_user_of_error(self, error: Exception, error_code: ErrorCode, context: str, recovery_success: bool):
        """Notify user about the error."""
        if not self.notification_manager:
            return
        
        try:
            # Create user-friendly error messages
            error_messages = {
                ErrorCode.PERMISSION_DENIED: ("Permission Required", "Please grant required permissions in System Preferences"),
                ErrorCode.IMAGE_TOO_LARGE: ("Image Too Large", "The selected image is too large to process"),
                ErrorCode.OUT_OF_MEMORY: ("Memory Error", "Not enough memory to complete the operation"),
                ErrorCode.SCREENSHOT_CAPTURE_ERROR: ("Capture Failed", "Failed to capture screenshot. Please try again"),
                ErrorCode.CLIPBOARD_ACCESS_ERROR: ("Clipboard Error", "Failed to copy image to clipboard"),
                ErrorCode.HOTKEY_REGISTRATION_ERROR: ("Hotkey Error", "Failed to register hotkey. Use menu instead"),
                ErrorCode.UNKNOWN_ERROR: ("Unexpected Error", "An unexpected error occurred")
            }
            
            title, message = error_messages.get(error_code, ("Error", "An error occurred"))
            
            if recovery_success:
                message += " (Automatically recovered)"
                self.notification_manager.show_warning(title, message)
            else:
                self.notification_manager.show_error(title, message)
                
        except Exception as e:
            logger.error(f"Failed to notify user of error: {e}")
    
    def register_recovery_strategy(self, error_code: ErrorCode, strategy: Callable):
        """Register a custom recovery strategy for an error code."""
        self.recovery_strategies[error_code] = strategy
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics."""
        return self.error_stats.copy()
    
    def reset_error_statistics(self):
        """Reset error statistics."""
        self.error_stats = {
            'total_errors': 0,
            'error_counts': {},
            'last_errors': []
        }


# Global error handler instance
error_handler = ErrorHandler()


def handle_errors(error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR, 
                 context: str = "", 
                 notify_user: bool = True,
                 return_on_error: Any = None):
    """
    Decorator to handle errors in functions.
    
    Args:
        error_code: Default error code if not determinable
        context: Context description for logging
        notify_user: Whether to notify user of errors
        return_on_error: Value to return if error occurs
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Handle the error
                recovery_success = error_handler.handle_error(
                    e, context or func.__name__, notify_user
                )
                
                if not recovery_success:
                    if return_on_error is not None:
                        return return_on_error
                    else:
                        raise
                
                # If recovery was successful, try the function again
                try:
                    return func(*args, **kwargs)
                except Exception as retry_error:
                    logger.error(f"Retry after recovery failed: {retry_error}")
                    if return_on_error is not None:
                        return return_on_error
                    else:
                        raise
        
        return wrapper
    return decorator


def check_system_resources() -> Dict[str, Any]:
    """Check system resource availability."""
    try:
        # Memory info
        memory = psutil.virtual_memory()
        
        # Disk space info
        disk = psutil.disk_usage('/')
        
        # CPU info
        cpu_percent = psutil.cpu_percent(interval=1)
        
        return {
            'memory': {
                'total': memory.total,
                'available': memory.available,
                'percent': memory.percent,
                'free_mb': memory.available / (1024 * 1024)
            },
            'disk': {
                'total': disk.total,
                'free': disk.free,
                'percent': (disk.used / disk.total) * 100,
                'free_gb': disk.free / (1024 * 1024 * 1024)
            },
            'cpu': {
                'percent': cpu_percent
            }
        }
    except Exception as e:
        logger.error(f"Error checking system resources: {e}")
        return {}