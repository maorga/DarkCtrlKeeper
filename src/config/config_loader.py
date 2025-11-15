"""
Configuration Loader for DarkCtrlKeeper
========================================

Loads environment variables from .env file and provides
configuration settings for the application.

Features:
- Loads .env file if present
- Graceful degradation if .env is missing
- Type-safe configuration access
"""

import os
from pathlib import Path
from typing import Dict, Optional

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    print("Warning: python-dotenv not installed. Environment variables from .env will not be loaded.")


class Config:
    """
    Configuration manager for DarkCtrlKeeper.
    
    Loads environment variables from .env file and provides
    access to configuration settings.
    
    Example:
        config = Config()
        version = config.get_app_version()
    """
    
    def __init__(self, env_path: Optional[Path] = None):
        """
        Initialize configuration loader.
        
        Args:
            env_path: Optional path to .env file. If None, looks for .env in project root.
        """
        if env_path is None:
            # Look for .env in project root (parent of src/)
            env_path = Path(__file__).parent.parent.parent / '.env'
        
        self.env_path = env_path
        self._load_environment()
    
    def _load_environment(self) -> None:
        """
        Load environment variables from .env file if it exists.
        Fails silently if file doesn't exist or dotenv is not available.
        """
        if not DOTENV_AVAILABLE:
            return
        
        if self.env_path.exists():
            load_dotenv(self.env_path)
            print(f"✓ Loaded environment from {self.env_path}")
        else:
            print(f"ℹ No .env file found at {self.env_path}")
    
    def get_app_version(self) -> str:
        """
        Get application version from environment or default.
        
        Returns:
            Application version string.
        """
        return os.getenv('APP_VERSION', '1.0.0')
    
    def is_debug_mode(self) -> bool:
        """
        Check if debug mode is enabled.
        
        Returns:
            True if DEBUG environment variable is set to 'true'.
        """
        return os.getenv('DEBUG', 'false').lower() == 'true'
    
    def get_config_summary(self) -> str:
        """
        Get human-readable configuration summary.
        
        Returns:
            Multi-line string describing current configuration.
        """
        lines = [
            "DarkCtrlKeeper Configuration",
            "=" * 30,
            f"App Version: {self.get_app_version()}",
            f"Debug Mode: {self.is_debug_mode()}",
        ]
        
        return "\n".join(lines)


# Singleton instance for easy access
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """
    Get singleton configuration instance.
    
    Returns:
        Global Config instance.
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
