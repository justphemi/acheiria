"""
Configuration Manager - Fixed for bundled apps
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages application configuration and settings"""
    
    def __init__(self, config_file: str = "config.json"):
        # Get user's home directory for config (writable in bundled apps)
        if getattr(sys, 'frozen', False):
            # Running as bundled app
            config_dir = Path.home() / '.acheiria'
            config_dir.mkdir(exist_ok=True)
            self.config_file = config_dir / config_file
        else:
            # Running as script
            self.config_file = Path(config_file)
        
        logger.info(f"Config file: {self.config_file}")
        
        self.default_config = {
            "typing_speed": 60,
            "countdown_duration": 4,
            "always_on_top": True,
            "window_position": {"x": 100, "y": 100},
            "first_run": False,
        }
    
    def load_config(self) -> Dict[str, Any]:
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    merged_config = self.default_config.copy()
                    merged_config.update(config)
                    logger.info("Configuration loaded successfully")
                    return merged_config
            else:
                logger.info("Config file not found, creating default")
                self.save_config(self.default_config)
                return self.default_config.copy()
        except Exception as e:
            logger.error(f"Error loading config: {e}", exc_info=True)
            return self.default_config.copy()
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info("Configuration saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving config: {e}", exc_info=True)
            return False