"""
Unit Tests for Configuration Loader
====================================

Tests the configuration loading and environment variable management.

To run tests:
    pytest tests/test_config.py
    pytest tests/test_config.py -v
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import patch, mock_open

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


class TestConfigInitialization:
    """Test Config class initialization."""
    
    def test_config_creation(self):
        """Test Config object can be created."""
        from config.config_loader import Config
        
        config = Config()
        
        assert config is not None
    
    def test_env_path_default(self):
        """Test default .env path is set correctly."""
        from config.config_loader import Config
        
        config = Config()
        
        assert config.env_path.name == '.env'
    
    def test_env_path_custom(self, tmp_path):
        """Test custom .env path can be specified."""
        from config.config_loader import Config
        
        custom_path = tmp_path / 'custom.env'
        config = Config(env_path=custom_path)
        
        assert config.env_path == custom_path


class TestGA4Configuration:
    """Test Google Analytics 4 configuration."""
    
    def test_get_ga4_config_empty(self):
        """Test GA4 config returns None values when not set."""
        from config.config_loader import Config
        
        with patch.dict(os.environ, {}, clear=True):
            config = Config()
            ga4_config = config.get_ga4_config()
            
            assert ga4_config['measurement_id'] is None
            assert ga4_config['api_secret'] is None
    
    def test_get_ga4_config_with_values(self):
        """Test GA4 config returns values from environment."""
        from config.config_loader import Config
        
        test_env = {
            'GA4_MEASUREMENT_ID': 'G-TEST123',
            'GA4_API_SECRET': 'test_secret_456'
        }
        
        with patch.dict(os.environ, test_env):
            config = Config()
            ga4_config = config.get_ga4_config()
            
            assert ga4_config['measurement_id'] == 'G-TEST123'
            assert ga4_config['api_secret'] == 'test_secret_456'
    
    def test_is_analytics_enabled_true(self):
        """Test analytics is enabled when both values are set."""
        from config.config_loader import Config
        
        test_env = {
            'GA4_MEASUREMENT_ID': 'G-TEST123',
            'GA4_API_SECRET': 'test_secret'
        }
        
        with patch.dict(os.environ, test_env):
            config = Config()
            
            assert config.is_analytics_enabled() is True
    
    def test_is_analytics_enabled_false_missing_id(self):
        """Test analytics is disabled when measurement ID is missing."""
        from config.config_loader import Config
        
        test_env = {
            'GA4_API_SECRET': 'test_secret'
        }
        
        with patch.dict(os.environ, test_env, clear=True):
            config = Config()
            
            assert config.is_analytics_enabled() is False
    
    def test_is_analytics_enabled_false_missing_secret(self):
        """Test analytics is disabled when API secret is missing."""
        from config.config_loader import Config
        
        test_env = {
            'GA4_MEASUREMENT_ID': 'G-TEST123'
        }
        
        with patch.dict(os.environ, test_env, clear=True):
            config = Config()
            
            assert config.is_analytics_enabled() is False
    
    def test_is_analytics_enabled_false_both_missing(self):
        """Test analytics is disabled when both values are missing."""
        from config.config_loader import Config
        
        with patch.dict(os.environ, {}, clear=True):
            config = Config()
            
            assert config.is_analytics_enabled() is False


class TestAppConfiguration:
    """Test application configuration settings."""
    
    def test_get_app_version_default(self):
        """Test default app version."""
        from config.config_loader import Config
        
        with patch.dict(os.environ, {}, clear=True):
            config = Config()
            
            assert config.get_app_version() == '1.0.0'
    
    def test_get_app_version_from_env(self):
        """Test app version from environment."""
        from config.config_loader import Config
        
        test_env = {'APP_VERSION': '2.5.1'}
        
        with patch.dict(os.environ, test_env):
            config = Config()
            
            assert config.get_app_version() == '2.5.1'
    
    def test_is_debug_mode_false_default(self):
        """Test debug mode is false by default."""
        from config.config_loader import Config
        
        with patch.dict(os.environ, {}, clear=True):
            config = Config()
            
            assert config.is_debug_mode() is False
    
    def test_is_debug_mode_true(self):
        """Test debug mode can be enabled."""
        from config.config_loader import Config
        
        test_env = {'DEBUG': 'true'}
        
        with patch.dict(os.environ, test_env):
            config = Config()
            
            assert config.is_debug_mode() is True
    
    def test_is_debug_mode_false_explicitly(self):
        """Test debug mode can be explicitly disabled."""
        from config.config_loader import Config
        
        test_env = {'DEBUG': 'false'}
        
        with patch.dict(os.environ, test_env):
            config = Config()
            
            assert config.is_debug_mode() is False
    
    def test_is_debug_mode_case_insensitive(self):
        """Test debug mode setting is case insensitive."""
        from config.config_loader import Config
        
        test_env = {'DEBUG': 'TRUE'}
        
        with patch.dict(os.environ, test_env):
            config = Config()
            
            assert config.is_debug_mode() is True


class TestConfigSummary:
    """Test configuration summary generation."""
    
    def test_get_config_summary_analytics_disabled(self):
        """Test config summary when analytics is disabled."""
        from config.config_loader import Config
        
        with patch.dict(os.environ, {}, clear=True):
            config = Config()
            summary = config.get_config_summary()
            
            assert 'DarkCtrlKeeper Configuration' in summary
            assert 'Analytics Enabled: False' in summary
            assert 'Not configured (optional)' in summary
    
    def test_get_config_summary_analytics_enabled(self):
        """Test config summary when analytics is enabled."""
        from config.config_loader import Config
        
        test_env = {
            'GA4_MEASUREMENT_ID': 'G-TEST123',
            'GA4_API_SECRET': 'test_secret'
        }
        
        with patch.dict(os.environ, test_env):
            config = Config()
            summary = config.get_config_summary()
            
            assert 'DarkCtrlKeeper Configuration' in summary
            assert 'Analytics Enabled: True' in summary
            assert 'G-TEST123' in summary
            assert '[CONFIGURED]' in summary
            # Secret value should NOT appear
            assert 'test_secret' not in summary


class TestSingletonPattern:
    """Test singleton configuration instance."""
    
    def test_get_config_returns_instance(self):
        """Test get_config returns Config instance."""
        from config.config_loader import get_config
        
        config = get_config()
        
        assert config is not None
    
    def test_get_config_returns_same_instance(self):
        """Test get_config returns same instance (singleton)."""
        from config.config_loader import get_config, _config_instance
        
        # Reset singleton
        import config.config_loader as config_module
        config_module._config_instance = None
        
        config1 = get_config()
        config2 = get_config()
        
        assert config1 is config2


class TestDotenvIntegration:
    """Test python-dotenv integration."""
    
    def test_dotenv_unavailable_warning(self):
        """Test warning is shown when python-dotenv is unavailable."""
        with patch('config.config_loader.DOTENV_AVAILABLE', False):
            from config.config_loader import Config
            
            # Should create config without crashing
            config = Config()
            assert config is not None
    
    def test_missing_env_file_handled(self, tmp_path):
        """Test missing .env file is handled gracefully."""
        from config.config_loader import Config
        
        non_existent_path = tmp_path / 'nonexistent.env'
        
        # Should not crash
        config = Config(env_path=non_existent_path)
        assert config is not None


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
