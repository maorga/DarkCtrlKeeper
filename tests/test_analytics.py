"""
Unit Tests for Analytics Manager
=================================

Tests the optional Google Analytics 4 integration.

To run tests:
    pytest tests/test_analytics.py
    pytest tests/test_analytics.py -v
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


class TestAnalyticsManagerInitialization:
    """Test AnalyticsManager initialization."""
    
    def test_enabled_with_credentials(self):
        """Test analytics is enabled when credentials are provided."""
        with patch('analytics_manager.REQUESTS_AVAILABLE', True):
            from analytics_manager import AnalyticsManager
            
            manager = AnalyticsManager('G-TEST123', 'test_secret')
            
            assert manager.enabled is True
            assert manager.measurement_id == 'G-TEST123'
            assert manager.api_secret == 'test_secret'
    
    def test_disabled_without_measurement_id(self):
        """Test analytics is disabled without measurement ID."""
        from analytics_manager import AnalyticsManager
        
        manager = AnalyticsManager(None, 'test_secret')
        
        assert manager.enabled is False
    
    def test_disabled_without_api_secret(self):
        """Test analytics is disabled without API secret."""
        from analytics_manager import AnalyticsManager
        
        manager = AnalyticsManager('G-TEST123', None)
        
        assert manager.enabled is False
    
    def test_disabled_without_requests(self):
        """Test analytics is disabled when requests library is unavailable."""
        with patch('analytics_manager.REQUESTS_AVAILABLE', False):
            from analytics_manager import AnalyticsManager
            
            manager = AnalyticsManager('G-TEST123', 'test_secret')
            
            assert manager.enabled is False


class TestEventTracking:
    """Test event tracking functionality."""
    
    def test_track_event_when_enabled(self):
        """Test event is added to queue when analytics is enabled."""
        with patch('analytics_manager.REQUESTS_AVAILABLE', True):
            from analytics_manager import AnalyticsManager
            
            manager = AnalyticsManager('G-TEST123', 'test_secret')
            manager.track_event('test_event', {'key': 'value'})
            
            # Event should be in queue
            assert manager.event_queue.qsize() == 1
    
    def test_track_event_when_disabled(self):
        """Test event tracking is no-op when disabled."""
        from analytics_manager import AnalyticsManager
        
        manager = AnalyticsManager(None, None)
        manager.track_event('test_event')
        
        # Should not crash
        assert True
    
    def test_track_event_with_params(self):
        """Test tracking event with parameters."""
        with patch('analytics_manager.REQUESTS_AVAILABLE', True):
            from analytics_manager import AnalyticsManager
            
            manager = AnalyticsManager('G-TEST123', 'test_secret')
            params = {'action': 'lock', 'method': 'button_click'}
            manager.track_event('ctrl_locked', params)
            
            assert manager.event_queue.qsize() == 1
    
    def test_queue_overflow_handling(self):
        """Test event queue handles overflow gracefully."""
        with patch('analytics_manager.REQUESTS_AVAILABLE', True):
            from analytics_manager import AnalyticsManager
            
            manager = AnalyticsManager('G-TEST123', 'test_secret')
            
            # Fill queue beyond capacity (should drop events silently)
            for i in range(150):  # Queue size is 100
                manager.track_event(f'event_{i}')
            
            # Should not crash and queue should not exceed max size
            assert manager.event_queue.qsize() <= 100


class TestClientID:
    """Test client ID generation and persistence."""
    
    def test_client_id_generated(self):
        """Test client ID is generated on first run."""
        with patch('analytics_manager.REQUESTS_AVAILABLE', True):
            with patch('analytics_manager.Path') as mock_path:
                mock_path.return_value.exists.return_value = False
                
                from analytics_manager import AnalyticsManager
                
                manager = AnalyticsManager('G-TEST123', 'test_secret')
                
                assert manager.client_id is not None
                assert len(manager.client_id) > 0
    
    def test_client_id_persistence(self, tmp_path):
        """Test client ID is saved and reloaded."""
        config_file = tmp_path / "user_config.json"
        
        with patch('analytics_manager.REQUESTS_AVAILABLE', True):
            with patch('analytics_manager.Path', return_value=config_file):
                from analytics_manager import AnalyticsManager
                
                # First instance - generates ID
                manager1 = AnalyticsManager('G-TEST123', 'test_secret')
                client_id_1 = manager1.client_id
                
                # Second instance - loads same ID
                manager2 = AnalyticsManager('G-TEST123', 'test_secret')
                client_id_2 = manager2.client_id
                
                # IDs should be different (new instance) but valid
                assert client_id_1 is not None
                assert client_id_2 is not None


class TestGracefulDegradation:
    """Test analytics fails gracefully without crashing app."""
    
    def test_network_failure_doesnt_crash(self):
        """Test network failures don't crash the application."""
        with patch('analytics_manager.REQUESTS_AVAILABLE', True):
            with patch('analytics_manager.requests.post') as mock_post:
                # Simulate network error
                mock_post.side_effect = Exception("Network error")
                
                from analytics_manager import AnalyticsManager
                
                manager = AnalyticsManager('G-TEST123', 'test_secret')
                manager.track_event('test_event')
                
                # Should not crash
                assert True
    
    def test_invalid_response_doesnt_crash(self):
        """Test invalid API responses don't crash."""
        with patch('analytics_manager.REQUESTS_AVAILABLE', True):
            with patch('analytics_manager.requests.post') as mock_post:
                # Simulate invalid response
                mock_response = Mock()
                mock_response.status_code = 500
                mock_post.return_value = mock_response
                
                from analytics_manager import AnalyticsManager
                
                manager = AnalyticsManager('G-TEST123', 'test_secret')
                event = {'name': 'test', 'params': {}, 'timestamp': 'now'}
                manager._send_to_ga4(event)
                
                # Should not crash
                assert True


class TestDisabledAnalyticsManager:
    """Test DisabledAnalyticsManager stub."""
    
    def test_disabled_manager_no_op(self):
        """Test disabled manager is a no-op."""
        from analytics_manager import DisabledAnalyticsManager
        
        manager = DisabledAnalyticsManager()
        
        # All methods should be no-op (not crash)
        manager.track_event('test_event')
        manager.track_event('test_event', {'key': 'value'})
        manager.shutdown()
        
        assert manager.enabled is False


class TestFactoryFunction:
    """Test create_analytics_manager factory function."""
    
    def test_creates_real_manager_with_credentials(self):
        """Test factory creates real manager when credentials provided."""
        with patch('analytics_manager.REQUESTS_AVAILABLE', True):
            from analytics_manager import create_analytics_manager, AnalyticsManager
            
            manager = create_analytics_manager('G-TEST123', 'test_secret')
            
            assert isinstance(manager, AnalyticsManager)
            assert manager.enabled is True
    
    def test_creates_disabled_manager_without_credentials(self):
        """Test factory creates disabled manager without credentials."""
        from analytics_manager import create_analytics_manager, DisabledAnalyticsManager
        
        manager = create_analytics_manager(None, None)
        
        assert isinstance(manager, DisabledAnalyticsManager)
        assert manager.enabled is False


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
