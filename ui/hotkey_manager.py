import logging
from Quartz import (
    CGEventTapCreate, CGEventTapEnable, 
    CGEventGetFlags, CGEventGetIntegerValueField,
    kCGEventKeyDown, kCGEventFlagsChanged, kCGKeyboardEventKeycode,
    kCGEventFlagMaskCommand, kCGEventFlagMaskAlternate, kCGEventFlagMaskShift,
    kCGEventFlagMaskControl, CGEventPost, kCGHIDEventTap, CFRunLoopGetCurrent,
    CFRunLoopAddSource, CFRunLoopRemoveSource, kCGEventTapOptionListenOnly,
    CFRunLoopRun, CFRunLoopStop, CFMachPortCreateRunLoopSource,
    kCFRunLoopDefaultMode
)
from Cocoa import NSRunLoop, NSDefaultRunLoopMode
from Foundation import CFRunLoopGetMain
import threading

logger = logging.getLogger(__name__)


class HotkeyManager:
    """Manages global hotkey registration and handling."""
    
    def __init__(self):
        self.registered_hotkeys = {}
        self.event_tap = None
        self.run_loop_source = None
        self.is_monitoring = False
        self.modifier_flags = 0
        
        # Key code mappings
        self.key_codes = {
            '1': 18, '2': 19, '3': 20, '4': 21, '5': 23,
            '6': 22, '7': 26, '8': 28, '9': 25, '0': 29,
            'a': 0, 'b': 11, 'c': 8, 'd': 2, 'e': 14,
            'f': 3, 'g': 5, 'h': 4, 'i': 34, 'j': 38,
            'k': 40, 'l': 37, 'm': 46, 'n': 45, 'o': 31,
            'p': 35, 'q': 12, 'r': 15, 's': 1, 't': 17,
            'u': 32, 'v': 9, 'w': 13, 'x': 7, 'y': 16, 'z': 6,
            'space': 49, 'return': 36, 'tab': 48, 'escape': 53,
            'delete': 51, 'backspace': 51
        }
        
        # Modifier flag mappings
        self.modifier_flags_map = {
            'cmd': kCGEventFlagMaskCommand,
            'alt': kCGEventFlagMaskAlternate,
            'shift': kCGEventFlagMaskShift,
            'ctrl': kCGEventFlagMaskControl
        }
    
    def register_hotkey(self, key_code, modifiers, callback):
        """
        Register a global hotkey.
        
        Args:
            key_code (int or str): Key code or key name
            modifiers (list): List of modifier strings ('cmd', 'alt', 'shift', 'ctrl')
            callback (callable): Function to call when hotkey is pressed
        """
        try:
            # Convert key name to key code if needed
            if isinstance(key_code, str):
                if key_code in self.key_codes:
                    key_code = self.key_codes[key_code]
                else:
                    raise ValueError(f"Unknown key name: {key_code}")
            
            # Calculate modifier flags
            modifier_flags = 0
            for modifier in modifiers:
                if modifier in self.modifier_flags_map:
                    modifier_flags |= self.modifier_flags_map[modifier]
                else:
                    raise ValueError(f"Unknown modifier: {modifier}")
            
            # Create hotkey identifier
            hotkey_id = f"{key_code}_{modifier_flags}"
            
            # Store hotkey
            self.registered_hotkeys[hotkey_id] = {
                'key_code': key_code,
                'modifiers': modifier_flags,
                'callback': callback
            }
            
            # Start monitoring if not already started
            if not self.is_monitoring:
                self.start_monitoring()
            
            logger.info(f"Registered hotkey: {hotkey_id}")
            
        except Exception as e:
            logger.error(f"Error registering hotkey: {e}")
            raise
    
    def start_monitoring(self):
        """Start monitoring for hotkey events."""
        try:
            if self.is_monitoring:
                return
            
            # Create event tap
            self.event_tap = CGEventTapCreate(
                kCGHIDEventTap,  # Tap location
                0,  # Placement - use default
                kCGEventTapOptionListenOnly,  # Options - listen only, don't modify
                (1 << kCGEventKeyDown) | (1 << kCGEventFlagsChanged),  # Event mask
                self._event_callback,  # Callback
                None  # User info
            )
            
            if not self.event_tap:
                raise RuntimeError("Failed to create event tap")
            
            # Create run loop source
            self.run_loop_source = CFMachPortCreateRunLoopSource(
                None,  # Allocator
                self.event_tap,  # Port
                0  # Order
            )
            
            # Add to main run loop
            main_loop = CFRunLoopGetMain()
            CFRunLoopAddSource(main_loop, self.run_loop_source, kCFRunLoopDefaultMode)
            
            # Enable the event tap
            CGEventTapEnable(self.event_tap, True)
            
            self.is_monitoring = True
            logger.info("Hotkey monitoring started")
            
        except Exception as e:
            logger.error(f"Error starting hotkey monitoring: {e}")
            self.cleanup()
            raise
    
    def _event_callback(self, proxy, event_type, event, user_info):
        """
        Event callback for hotkey detection.
        
        Args:
            proxy: Event tap proxy
            event_type: Type of event
            event: The event
            user_info: User info (unused)
        """
        try:
            if event_type == kCGEventKeyDown:
                # Get key code and modifiers
                key_code = CGEventGetIntegerValueField(event, kCGKeyboardEventKeycode)
                flags = CGEventGetFlags(event)
                
                # Check if this matches any registered hotkey
                hotkey_id = f"{key_code}_{flags}"
                
                if hotkey_id in self.registered_hotkeys:
                    hotkey = self.registered_hotkeys[hotkey_id]
                    
                    # Execute callback in background thread
                    def execute_callback():
                        try:
                            hotkey['callback']()
                        except Exception as e:
                            logger.error(f"Error executing hotkey callback: {e}")
                    
                    threading.Thread(target=execute_callback, daemon=True).start()
                    
                    logger.debug(f"Hotkey triggered: {hotkey_id}")
            
            elif event_type == kCGEventFlagsChanged:
                # Track modifier flags
                self.modifier_flags = CGEventGetFlags(event)
            
            # Return the event unchanged (we're listening only)
            return event
            
        except Exception as e:
            logger.error(f"Error in hotkey event callback: {e}")
            return event
    
    def unregister_hotkey(self, key_code, modifiers):
        """
        Unregister a hotkey.
        
        Args:
            key_code (int or str): Key code or key name
            modifiers (list): List of modifier strings
        """
        try:
            # Convert key name to key code if needed
            if isinstance(key_code, str):
                if key_code in self.key_codes:
                    key_code = self.key_codes[key_code]
                else:
                    raise ValueError(f"Unknown key name: {key_code}")
            
            # Calculate modifier flags
            modifier_flags = 0
            for modifier in modifiers:
                if modifier in self.modifier_flags_map:
                    modifier_flags |= self.modifier_flags_map[modifier]
            
            # Remove hotkey
            hotkey_id = f"{key_code}_{modifier_flags}"
            if hotkey_id in self.registered_hotkeys:
                del self.registered_hotkeys[hotkey_id]
                logger.info(f"Unregistered hotkey: {hotkey_id}")
            
            # Stop monitoring if no hotkeys left
            if not self.registered_hotkeys and self.is_monitoring:
                self.stop_monitoring()
                
        except Exception as e:
            logger.error(f"Error unregistering hotkey: {e}")
    
    def stop_monitoring(self):
        """Stop monitoring for hotkey events."""
        try:
            if not self.is_monitoring:
                return
            
            # Disable event tap
            if self.event_tap:
                CGEventTapEnable(self.event_tap, False)
            
            # Remove from run loop
            if self.run_loop_source:
                main_loop = CFRunLoopGetMain()
                CFRunLoopRemoveSource(main_loop, self.run_loop_source, kCFRunLoopDefaultMode)
            
            self.is_monitoring = False
            logger.info("Hotkey monitoring stopped")
            
        except Exception as e:
            logger.error(f"Error stopping hotkey monitoring: {e}")
    
    def cleanup(self):
        """Clean up resources."""
        try:
            self.stop_monitoring()
            self.registered_hotkeys.clear()
            
            if self.event_tap:
                self.event_tap = None
            
            if self.run_loop_source:
                self.run_loop_source = None
            
            logger.info("Hotkey manager cleaned up")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def get_registered_hotkeys(self):
        """Get list of registered hotkeys."""
        hotkeys = []
        for hotkey_id, hotkey in self.registered_hotkeys.items():
            # Convert back to human-readable format
            modifiers = []
            for name, flag in self.modifier_flags_map.items():
                if hotkey['modifiers'] & flag:
                    modifiers.append(name)
            
            # Find key name
            key_name = str(hotkey['key_code'])
            for name, code in self.key_codes.items():
                if code == hotkey['key_code']:
                    key_name = name
                    break
            
            hotkeys.append({
                'key': key_name,
                'modifiers': modifiers,
                'id': hotkey_id
            })
        
        return hotkeys