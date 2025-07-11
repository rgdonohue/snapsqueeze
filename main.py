#!/usr/bin/env python3
"""
SnapSqueeze - A clipboard-first screenshot compressor for macOS
Main entry point for the application.
"""

import sys
import os
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ui.menu_bar_app import SnapSqueezeApp


def setup_logging():
    """Setup application logging."""
    # Create logs directory if it doesn't exist
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "snapsqueeze.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set some loggers to WARNING to reduce noise
    logging.getLogger('rumps').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)


def check_macos_version():
    """Check if running on supported macOS version."""
    import platform
    
    if platform.system() != 'Darwin':
        print("SnapSqueeze is only supported on macOS")
        sys.exit(1)
    
    # Check macOS version (require 10.15+)
    version = platform.mac_ver()[0]
    major, minor = map(int, version.split('.')[:2])
    
    if major < 10 or (major == 10 and minor < 15):
        print("SnapSqueeze requires macOS 10.15 (Catalina) or later")
        sys.exit(1)


def main():
    """Main entry point."""
    try:
        # Check system requirements
        check_macos_version()
        
        # Setup logging
        setup_logging()
        
        logger = logging.getLogger(__name__)
        logger.info("Starting SnapSqueeze application")
        
        # Create and run the app
        app = SnapSqueezeApp()
        
        # Log startup success
        logger.info("SnapSqueeze initialized successfully")
        
        # Run the application
        app.run()
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error starting SnapSqueeze: {e}")
        print(f"Failed to start SnapSqueeze: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()