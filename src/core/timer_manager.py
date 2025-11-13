"""
Timer Manager
=============

Manages countdown timer logic and state.
"""

from typing import Callable, Optional


class TimerManager:
    """Manages countdown timer state and logic."""
    
    def __init__(
        self,
        on_tick_callback: Optional[Callable[[float], None]] = None,
        on_alert_callback: Optional[Callable[[], None]] = None
    ):
        """
        Initialize timer manager.
        
        Args:
            on_tick_callback: Called on each timer tick with seconds remaining
            on_alert_callback: Called when timer reaches alert threshold
        """
        self.milliseconds = 60000  # 60 seconds
        self.is_running = False
        self.alert_shown = False
        self.on_tick_callback = on_tick_callback
        self.on_alert_callback = on_alert_callback
        
        # Timer thresholds
        self.alert_threshold = 5.0  # Show alert at 5 seconds
    
    def start(self) -> None:
        """Start the timer."""
        self.is_running = True
        print(f"▶ Timer started from {self.get_seconds():.1f}")
    
    def stop(self) -> None:
        """Stop the timer."""
        self.is_running = False
        print(f"⏸ Timer stopped at {self.get_seconds():.1f}")
    
    def reset(self) -> None:
        """Reset timer to initial value."""
        self.milliseconds = 60000
        self.alert_shown = False
        print("✓ Countdown reset to 60.0")
    
    def toggle(self) -> bool:
        """
        Toggle timer between running and stopped.
        
        Returns:
            True if now running, False if now stopped
        """
        if self.is_running:
            self.stop()
        else:
            self.start()
        return self.is_running
    
    def tick(self) -> None:
        """Process one timer tick (10ms)."""
        if not self.is_running:
            return
        
        if self.milliseconds > 0:
            self.milliseconds -= 10
            seconds = self.get_seconds()
            
            # Trigger tick callback
            if self.on_tick_callback:
                self.on_tick_callback(seconds)
            
            # Check for alert threshold
            if seconds <= self.alert_threshold and not self.alert_shown:
                self.alert_shown = True
                if self.on_alert_callback:
                    self.on_alert_callback()
                print("🚨 BUFF ALERT: Countdown reached threshold!")
        else:
            if self.on_tick_callback:
                self.on_tick_callback(0.0)
    
    def get_seconds(self) -> float:
        """Get remaining time in seconds."""
        return self.milliseconds / 1000.0
    
    def get_color_zone(self) -> str:
        """
        Get current color zone based on remaining time.
        
        Returns:
            'green', 'yellow', or 'red'
        """
        seconds = self.get_seconds()
        if seconds > 30.0:
            return 'green'
        elif seconds > 10.0:
            return 'yellow'
        else:
            return 'red'
