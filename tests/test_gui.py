"""
Unit Tests for DarkCtrlKeeper GUI
==================================

Tests the main application window and UI components.

To run tests:
    pytest tests/test_gui.py
    pytest tests/test_gui.py -v  # Verbose output
    pytest tests/test_gui.py --cov=src  # With coverage
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for all tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit()


@pytest.fixture
def app_window(qapp):
    """Create DarkCtrlKeeper app instance for testing."""
    # Mock pynput to avoid keyboard control in tests
    with patch('main.keyboard'):
        with patch('main.CONFIG_AVAILABLE', False):  # Disable config/analytics
            from main import DarkCtrlKeeperApp
            window = DarkCtrlKeeperApp()
            yield window
            window.close()


class TestWindowCreation:
    """Test window initialization and properties."""
    
    def test_window_dimensions(self, app_window):
        """Test window has correct fixed size."""
        assert app_window.width() == 356
        assert app_window.height() == 430
    
    def test_window_title(self, app_window):
        """Test window title is set correctly."""
        assert app_window.windowTitle() == "DarkCtrlKeeper"
    
    def test_window_frameless(self, app_window):
        """Test window is frameless."""
        flags = app_window.windowFlags()
        assert Qt.WindowType.FramelessWindowHint in flags
    
    def test_window_always_on_top(self, app_window):
        """Test window stays on top."""
        flags = app_window.windowFlags()
        assert Qt.WindowType.WindowStaysOnTopHint in flags


class TestButtonState:
    """Test button state changes and interactions."""
    
    def test_initial_state_released(self, app_window):
        """Test initial state is RELEASED (lock active, release inactive)."""
        assert app_window.lock_is_active is True
        assert app_window.pressed_text.isVisible() is False
        assert app_window.released_text.isVisible() is True
    
    def test_lock_button_click(self, app_window):
        """Test clicking lock button changes state to PRESSED."""
        app_window.on_lock_button_clicked()
        
        assert app_window.lock_is_active is False
        assert app_window.pressed_text.isVisible() is True
        assert app_window.released_text.isVisible() is False
    
    def test_release_button_click(self, app_window):
        """Test clicking release button changes state to RELEASED."""
        # First lock
        app_window.on_lock_button_clicked()
        assert app_window.lock_is_active is False
        
        # Then release
        app_window.on_release_button_clicked()
        assert app_window.lock_is_active is True
        assert app_window.pressed_text.isVisible() is False
        assert app_window.released_text.isVisible() is True
    
    def test_lock_button_idempotent(self, app_window):
        """Test clicking lock button when already locked has no effect."""
        app_window.on_lock_button_clicked()
        state_before = app_window.lock_is_active
        
        # Click again - should have no effect
        app_window.on_lock_button_clicked()
        assert app_window.lock_is_active == state_before
    
    def test_release_button_idempotent(self, app_window):
        """Test clicking release button when already released has no effect."""
        # Ensure we start in released state
        if not app_window.lock_is_active:
            app_window.on_release_button_clicked()
        
        state_before = app_window.lock_is_active
        
        # Click again - should have no effect
        app_window.on_release_button_clicked()
        assert app_window.lock_is_active == state_before


class TestCountdownTimer:
    """Test countdown timer functionality."""
    
    def test_initial_countdown_value(self, app_window):
        """Test countdown starts at 60.0 seconds."""
        assert app_window.countdown_milliseconds == 60000
        assert app_window.countdown_label.text() == "60.0"
    
    def test_countdown_timer_running(self, app_window):
        """Test countdown timer is running by default."""
        assert app_window.timer_running is True
        assert app_window.countdown_timer.isActive() is True
    
    def test_reset_countdown(self, app_window):
        """Test countdown reset to 60.0."""
        # Change countdown value
        app_window.countdown_milliseconds = 30000
        app_window.countdown_label.setText("30.0")
        
        # Reset
        app_window.reset_countdown()
        
        assert app_window.countdown_milliseconds == 60000
        assert app_window.countdown_label.text() == "60.0"
    
    def test_toggle_timer_stop(self, app_window):
        """Test stopping timer."""
        assert app_window.timer_running is True
        
        app_window.toggle_timer()
        
        assert app_window.timer_running is False
        assert app_window.countdown_timer.isActive() is False
        assert app_window.stop_button.text() == "RESUME"
    
    def test_toggle_timer_resume(self, app_window):
        """Test resuming timer."""
        # First stop
        app_window.toggle_timer()
        assert app_window.timer_running is False
        
        # Then resume
        app_window.toggle_timer()
        
        assert app_window.timer_running is True
        assert app_window.countdown_timer.isActive() is True
        assert app_window.stop_button.text() == "STOP"
    
    def test_manual_reset_resumes_timer(self, app_window):
        """Test manual reset also resumes stopped timer."""
        # Stop timer
        app_window.toggle_timer()
        assert app_window.timer_running is False
        
        # Manual reset
        app_window.manual_reset_countdown()
        
        assert app_window.timer_running is True
        assert app_window.countdown_milliseconds == 60000


class TestNumberSelection:
    """Test Greater Fortitude hotkey selection."""
    
    def test_initial_selection(self, app_window):
        """Test default selection is '4'."""
        assert app_window.selected_number == '4'
        assert app_window.radio_4.isChecked() is True
        assert app_window.radio_5.isChecked() is False
    
    def test_select_radio_5(self, app_window):
        """Test selecting radio button 5."""
        app_window.radio_5.setChecked(True)
        app_window.on_number_selected(app_window.radio_5)
        
        assert app_window.selected_number == '5'
        assert app_window.radio_4.isChecked() is False
        assert app_window.radio_5.isChecked() is True
    
    def test_mutual_exclusivity(self, app_window):
        """Test only one radio button can be selected."""
        app_window.radio_5.setChecked(True)
        
        # Only one should be checked
        checked_count = sum([
            app_window.radio_4.isChecked(),
            app_window.radio_5.isChecked()
        ])
        assert checked_count == 1


class TestCleanup:
    """Test proper cleanup on application exit."""
    
    def test_close_event_releases_ctrl(self, app_window):
        """Test CTRL key is released on close."""
        # Simulate CTRL being held
        app_window.simulated_ctrl_held = True
        
        # Mock the controller
        app_window.ctrl_controller = Mock()
        
        # Trigger close
        from PyQt6.QtGui import QCloseEvent
        event = QCloseEvent()
        app_window.closeEvent(event)
        
        # Verify CTRL was released
        app_window.ctrl_controller.release.assert_called_once()
    
    def test_close_event_stops_listeners(self, app_window):
        """Test keyboard listener is stopped on close."""
        app_window.keyboard_listener = Mock()
        
        from PyQt6.QtGui import QCloseEvent
        event = QCloseEvent()
        app_window.closeEvent(event)
        
        # Verify listener was stopped
        app_window.keyboard_listener.stop.assert_called_once()


class TestUIComponents:
    """Test UI component presence and properties."""
    
    def test_background_label_exists(self, app_window):
        """Test background label is created."""
        assert hasattr(app_window, 'background_label')
        assert app_window.background_label.width() == 356
        assert app_window.background_label.height() == 430
    
    def test_buttons_exist(self, app_window):
        """Test all buttons are created."""
        assert hasattr(app_window, 'lock_button')
        assert hasattr(app_window, 'release_button')
        assert hasattr(app_window, 'close_button')
        assert hasattr(app_window, 'stop_button')
        assert hasattr(app_window, 'reset_button')
    
    def test_status_text_exists(self, app_window):
        """Test status text labels exist."""
        assert hasattr(app_window, 'pressed_text')
        assert hasattr(app_window, 'released_text')
    
    def test_countdown_label_exists(self, app_window):
        """Test countdown label exists."""
        assert hasattr(app_window, 'countdown_label')
    
    def test_buff_alert_exists(self, app_window):
        """Test buff alert exists and is hidden initially."""
        assert hasattr(app_window, 'buff_alert')
        assert app_window.buff_alert.isVisible() is False


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
