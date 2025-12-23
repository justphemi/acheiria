#!/usr/bin/env python3
"""
Acheiria - acheiria: nuturing laziness in youths
"""

import flet as ft
import sys
import logging
import time
import threading
from pathlib import Path

# Get user's home directory for logs (writable in bundled apps)
if getattr(sys, 'frozen', False):
    # Running as bundled app
    log_dir = Path.home() / '.acheiria'
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / 'acheiria.log'
else:
    # Running as script
    log_file = Path('acheiria.log')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(str(log_file)),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logger.info("="*50)
logger.info("acheiria acheiria: nuturing laziness in youths is starting")
logger.info(f"Log file: {log_file}")
logger.info("="*50)

# Import our app module
try:
    from app.ui import AcheiriaApp
    from app.config import ConfigManager
except ImportError as e:
    logger.error(f"Import error: {e}")
    logger.error("Make sure app/ui.py and app/config.py exist")
    # Create a simple error UI
    def main(page: ft.Page):
        page.add(ft.Text(f"Import Error: {e}", color="red"))
    ft.app(target=main)
    sys.exit(1)

def main(page: ft.Page):
    """
    Main function that initializes the Flet application
    """
    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Configure the main window
        page.title = "acheiria: nuturing laziness in youths"
        page.window.resizable = True
        page.window.minimizable = True
        page.window.maximizable = True
        page.padding = 0
        page.spacing = 0
        page.bgcolor = "#000000"
        page.window.title_bar_hidden = False
        page.window.frameless = False
        
        # Set window constraints
        page.window.min_width = 500
        page.window.max_width = 900
        page.window.min_height = 350
        page.window.max_height = 900
        
        # Set initial window size
        page.window.width = 600
        page.window.height = 480
        
        # Set window position and always on top from config
        if not config.get('first_run', False):
            pos = config.get('window_position', {})
            page.window.left = pos.get('x', 100)
            page.window.top = pos.get('y', 100)
        
        page.window.always_on_top = config.get('always_on_top', True)
        
        # Initialize and add the main app UI
        app = AcheiriaApp(page, config_manager)
        page.add(app)
        
        # Save window position on move
        def handle_window_move():
            try:
                config = config_manager.load_config()
                config['window_position'] = {
                    'x': page.window.left or 100,
                    'y': page.window.top or 100
                }
                config_manager.save_config(config)
            except Exception as e:
                logger.debug(f"Window move save error: {e}")
        
        # Monitor window position
        def monitor_window():
            last_pos = None
            while True:
                try:
                    current_pos = (page.window.left, page.window.top)
                    if current_pos != last_pos and all(current_pos):
                        last_pos = current_pos
                        handle_window_move()
                    time.sleep(1)
                except:
                    time.sleep(1)
        
        monitor_thread = threading.Thread(target=monitor_window, daemon=True)
        monitor_thread.start()
        
        # Update the page (use regular update, not update_async)
        page.update()
        
        logger.info("Acheiria acheiria: nuturing laziness in youths started successfully")
        
    except Exception as e:
        logger.error(f"Error starting application: {e}", exc_info=True)
        # Simple error display
        page.add(ft.Text(f"Error: {str(e)}", color="red"))
        page.update()

if __name__ == "__main__":
    try:
        ft.app(target=main)
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)