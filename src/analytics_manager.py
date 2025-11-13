"""
Analytics Manager for DarkCtrlKeeper
=====================================

Optional Google Analytics 4 integration for tracking application usage.
Designed with privacy and graceful degradation in mind.

Features:
- Non-blocking event tracking via background thread
- Automatic client ID generation and persistence
- Thread-safe event queue
- Silent failure mode (doesn't crash app if GA4 fails)
- Privacy-focused (no personal data collected)

Events Tracked:
- app_opened: Application launched
- app_closed: Application shut down
- ctrl_locked: CTRL key locked
- ctrl_released: CTRL key released
"""

import json
import queue
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: 'requests' library not available. Analytics will be disabled.")


class AnalyticsManager:
    """
    Manages Google Analytics 4 event tracking.
    
    Uses background thread to send events without blocking the main application.
    Generates and persists a unique client ID for user tracking (anonymous).
    
    Example:
        manager = AnalyticsManager(measurement_id, api_secret)
        manager.track_event('app_opened')
        manager.track_event('ctrl_locked', {'duration': 60})
        manager.shutdown()  # Flush remaining events
    """
    
    def __init__(self, measurement_id: Optional[str], api_secret: Optional[str]):
        """
        Initialize analytics manager.
        
        Args:
            measurement_id: GA4 Measurement ID (e.g., G-XXXXXXXXXX)
            api_secret: GA4 API Secret for Measurement Protocol
        """
        self.measurement_id = measurement_id
        self.api_secret = api_secret
        self.enabled = bool(measurement_id and api_secret and REQUESTS_AVAILABLE)
        
        if not self.enabled:
            print("ℹ Analytics disabled (missing credentials or requests library)")
            return
        
        # Load or create persistent client ID
        self.client_id = self._load_or_create_client_id()
        
        # Thread-safe event queue (max 100 events to prevent memory issues)
        self.event_queue: queue.Queue = queue.Queue(maxsize=100)
        
        # Background worker thread for sending events
        self.worker_thread = threading.Thread(
            target=self._worker_thread,
            daemon=True,
            name="AnalyticsWorker"
        )
        self.worker_running = True
        self.worker_thread.start()
        
        print(f"✓ Analytics initialized (Client ID: {self.client_id[:8]}...)")
    
    def track_event(self, event_name: str, params: Optional[Dict[str, Any]] = None) -> None:
        """
        Track an event asynchronously.
        
        Events are added to a queue and sent in a background thread.
        If queue is full, event is silently dropped (won't crash app).
        
        Args:
            event_name: Name of the event (e.g., 'app_opened', 'ctrl_locked')
            params: Optional dictionary of event parameters
        """
        if not self.enabled:
            return
        
        try:
            event_data = {
                'name': event_name,
                'params': params or {},
                'timestamp': datetime.utcnow().isoformat()
            }
            self.event_queue.put_nowait(event_data)
        except queue.Full:
            # Silently drop event if queue is full (prevents blocking)
            pass
        except Exception as e:
            # Never crash the app due to analytics
            print(f"Analytics warning: {e}")
    
    def _worker_thread(self) -> None:
        """
        Background worker thread that processes event queue.
        Runs continuously until shutdown() is called.
        """
        while self.worker_running:
            try:
                # Block for up to 1 second waiting for events
                event = self.event_queue.get(timeout=1.0)
                self._send_to_ga4(event)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Analytics worker error: {e}")
    
    def _send_to_ga4(self, event: Dict[str, Any]) -> None:
        """
        Send event to Google Analytics 4 via Measurement Protocol.
        
        Args:
            event: Event dictionary with 'name', 'params', and 'timestamp'
        """
        if not self.enabled or not REQUESTS_AVAILABLE:
            return
        
        url = "https://www.google-analytics.com/mp/collect"
        
        params = {
            'measurement_id': self.measurement_id,
            'api_secret': self.api_secret
        }
        
        body = {
            'client_id': self.client_id,
            'events': [{
                'name': event['name'],
                'params': {
                    **event['params'],
                    'engagement_time_msec': 100,
                    'session_id': int(datetime.utcnow().timestamp())
                }
            }]
        }
        
        try:
            response = requests.post(
                url,
                params=params,
                json=body,
                timeout=5
            )
            # GA4 Measurement Protocol returns 204 on success
            if response.status_code == 204:
                print(f"✓ Analytics: {event['name']}")
            else:
                print(f"⚠ Analytics response: {response.status_code}")
        except requests.exceptions.Timeout:
            print(f"⚠ Analytics timeout for event: {event['name']}")
        except Exception as e:
            # Silent failure - don't crash app
            print(f"Analytics send error: {e}")
    
    def _load_or_create_client_id(self) -> str:
        """
        Load existing client ID from user_config.json or create a new one.
        
        Client ID is a persistent anonymous identifier for tracking
        across sessions without identifying the user.
        
        Returns:
            UUID string representing the client ID
        """
        config_path = Path('user_config.json')
        
        # Try to load existing config
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'client_id' in data:
                        return data['client_id']
            except Exception as e:
                print(f"Warning: Could not load user_config.json: {e}")
        
        # Generate new client ID
        client_id = str(uuid.uuid4())
        
        # Save to config file
        try:
            config_data = {
                'client_id': client_id,
                'created_at': datetime.utcnow().isoformat(),
                'version': '1.0.0',
                'note': 'This file contains an anonymous identifier for analytics. Delete to reset.'
            }
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2)
            print(f"✓ Created new analytics client ID")
        except Exception as e:
            print(f"Warning: Could not save user_config.json: {e}")
        
        return client_id
    
    def shutdown(self, timeout: float = 5.0) -> None:
        """
        Gracefully shutdown analytics manager.
        
        Stops worker thread and attempts to flush remaining events
        in the queue before exiting.
        
        Args:
            timeout: Maximum time to wait for queue to flush (seconds)
        """
        if not self.enabled:
            return
        
        print("ℹ Shutting down analytics...")
        
        # Stop worker thread
        self.worker_running = False
        
        # Try to flush remaining events
        flushed = 0
        start_time = datetime.now()
        while not self.event_queue.empty():
            if (datetime.now() - start_time).total_seconds() > timeout:
                print(f"⚠ Analytics timeout - {self.event_queue.qsize()} events lost")
                break
            
            try:
                event = self.event_queue.get_nowait()
                self._send_to_ga4(event)
                flushed += 1
            except queue.Empty:
                break
            except Exception as e:
                print(f"Analytics flush error: {e}")
        
        if flushed > 0:
            print(f"✓ Flushed {flushed} analytics events")
        
        # Wait for worker thread to finish
        if self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2.0)


# Stub class for when analytics is disabled
class DisabledAnalyticsManager:
    """
    No-op analytics manager used when GA4 is not configured.
    Provides same interface but does nothing.
    """
    
    def __init__(self):
        self.enabled = False
    
    def track_event(self, event_name: str, params: Optional[Dict[str, Any]] = None) -> None:
        """No-op event tracking."""
        pass
    
    def shutdown(self, timeout: float = 5.0) -> None:
        """No-op shutdown."""
        pass


def create_analytics_manager(
    measurement_id: Optional[str],
    api_secret: Optional[str]
) -> AnalyticsManager:
    """
    Factory function to create analytics manager.
    
    Returns DisabledAnalyticsManager if credentials are not provided,
    otherwise returns fully functional AnalyticsManager.
    
    Args:
        measurement_id: GA4 Measurement ID
        api_secret: GA4 API Secret
    
    Returns:
        AnalyticsManager instance (or disabled stub)
    """
    if measurement_id and api_secret:
        return AnalyticsManager(measurement_id, api_secret)
    else:
        return DisabledAnalyticsManager()
