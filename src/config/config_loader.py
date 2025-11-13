"""
Configuration Loader for DarkCtrlKeeper
========================================

Loads environment variables from .env file and provides
configuration for optional Google Analytics 4 integration.

Features:
- Loads .env file if present
- Provides GA4 configuration
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
        if config.is_analytics_enabled():
            ga4_config = config.get_ga4_config()
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
            print(f"ℹ No .env file found at {self.env_path} - analytics disabled")
    
    def get_ga4_config(self) -> Dict[str, Optional[str]]:
        """
        Get Google Analytics 4 configuration.
        
        Returns:
            Dictionary with 'measurement_id' and 'api_secret' keys.
            Values may be None if not configured.
        """
        return {
            'measurement_id': os.getenv('GA4_MEASUREMENT_ID'),
            'api_secret': os.getenv('GA4_API_SECRET')
        }
    
    def is_analytics_enabled(self) -> bool:
        """
        Check if analytics is properly configured.
        
        Returns:
            True if both GA4_MEASUREMENT_ID and GA4_API_SECRET are set.
        """
        config = self.get_ga4_config()
        return all(config.values())
    
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
            f"Analytics Enabled: {self.is_analytics_enabled()}",
        ]
        
        if self.is_analytics_enabled():
            ga4_config = self.get_ga4_config()
            lines.append(f"GA4 Measurement ID: {ga4_config['measurement_id']}")
            lines.append("GA4 API Secret: [CONFIGURED]")
        else:
            lines.append("Analytics: Not configured (optional)")
        
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
