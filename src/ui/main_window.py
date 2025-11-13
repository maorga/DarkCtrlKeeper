"""
Main Window
===========

The main application window that orchestrates all UI components and logic.
"""

import sys
import os
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QRadioButton, 
    QButtonGroup, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QPoint, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QMouseEvent, QIcon, QColor

from utils.resources import resource_path
from core.keyboard_manager import KeyboardManager
from core.timer_manager import TimerManager
from ui.styles import *
from ui.dialogs import show_info_dialog

# Optional analytics
try:
    from config.config_loader import Config
    from analytics_manager import create_analytics_manager
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    print("Warning: Config/Analytics modules not found. Running in basic mode.")


class DarkCtrlKeeperWindow(QWidget):
    """
    Main application window for DarkCtrlKeeper.
    
    Orchestrates UI components, keyboard control, timer logic,
    and optional analytics tracking.
    """
    
    # Qt signals for thread-safe operations
    reset_countdown_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # Initialize core managers
        self._init_config_and_analytics()
        self._init_managers()
        
        # Window setup
        self._setup_window()
        
        # UI setup
        self._setup_ui()
        
        # Connect signals
        self.reset_countdown_signal.connect(self._on_hotkey_reset)
        
        # State
        self.lock_is_active = True  # True = RELEASED, False = PRESSED
        self.drag_position = QPoint()
        
        # Start keyboard listener
        self.keyboard_mgr.start_listening()
        
        # Track app open
        if self.analytics:
            self.analytics.track_event('app_opened', {
                'version': '1.0.0',
                'platform': sys.platform
            })
        
        print("✓ DarkCtrlKeeper initialized successfully")
    
    def _init_config_and_analytics(self):
        """Initialize configuration and analytics."""
        self.config = None
        self.analytics = None
        
        if not CONFIG_AVAILABLE:
            return
        
        try:
            self.config = Config()
            print(self.config.get_config_summary())
            
            if self.config.is_analytics_enabled():
                ga4_config = self.config.get_ga4_config()
                self.analytics = create_analytics_manager(
                    ga4_config['measurement_id'],
                    ga4_config['api_secret']
                )
            else:
                self.analytics = create_analytics_manager(None, None)
        except Exception as e:
            print(f"Warning: Could not initialize config/analytics: {e}")
    
    def _init_managers(self):
        """Initialize core logic managers."""
        # Keyboard manager
        self.keyboard_mgr = KeyboardManager(
            on_hotkey_callback=lambda key: self.reset_countdown_signal.emit()
        )
        
        # Timer manager
        self.timer_mgr = TimerManager(
            on_tick_callback=self._on_timer_tick,
            on_alert_callback=self._on_timer_alert
        )
        
        # QTimer for UI updates
        self.qt_timer = QTimer(self)
        self.qt_timer.timeout.connect(lambda: self.timer_mgr.tick())
        
        # Alert pulse timer
        self.alert_pulse_timer = QTimer(self)
        self.alert_pulse_timer.timeout.connect(self._pulse_alert)
        self.alert_pulse_state = 0
    
    def _setup_window(self):
        """Setup window properties."""
        self.setWindowTitle("DarkCtrlKeeper")
        self.setFixedSize(356, 430)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Set icon
        icon_path = resource_path("assets/ICON.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
    
    def _setup_ui(self):
        """Setup all UI components."""
        self._setup_background()
        self._setup_watermark()
        self._setup_buttons()
        self._setup_status_text()
        self._setup_hotkey_selection()
        self._setup_countdown()
        self._setup_control_buttons()
        self._setup_window_buttons()
    
    def _setup_background(self):
        """Setup background image."""
        self.background_label = QLabel(self)
        bg_pixmap = QPixmap(resource_path("assets/base_background.png"))
        if bg_pixmap.isNull():
            print("ERROR: Could not load assets/base_background.png")
        self.background_label.setPixmap(bg_pixmap)
        self.background_label.setGeometry(0, 0, 356, 430)
    
    def _setup_watermark(self):
        """Setup watermark label."""
        self.watermark_label = QLabel("Created by MaorG", self)
        self.watermark_label.setGeometry(0, 68, 356, 20)
        self.watermark_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.watermark_label.setStyleSheet(WATERMARK_STYLE)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 2)
        self.watermark_label.setGraphicsEffect(shadow)
        self.watermark_label.raise_()
    
    def _setup_buttons(self):
        """Setup Lock and Release buttons."""
        # LOCK button
        self.lock_button = QPushButton(self)
        self.lock_active_pixmap = QPixmap(resource_path("assets/lock-button.png"))
        self.lock_gray_pixmap = QPixmap(resource_path("assets/lock-button-gray.png"))
        
        self.lock_button.setIcon(QIcon(self.lock_active_pixmap))
        self.lock_button.setIconSize(self.lock_active_pixmap.size())
        self.lock_button.setGeometry(45, 300, 
                                     self.lock_active_pixmap.width(), 
                                     self.lock_active_pixmap.height())
        self.lock_button.setFlat(True)
        self.lock_button.setStyleSheet("border: none; background: transparent;")
        self.lock_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lock_button.clicked.connect(self._on_lock_clicked)
        self.lock_button.setToolTip("Lock CTRL key")
        
        # RELEASE button
        self.release_button = QPushButton(self)
        self.release_active_pixmap = QPixmap(resource_path("assets/released-button.png"))
        self.release_gray_pixmap = QPixmap(resource_path("assets/released-button-gray.png"))
        
        self.release_button.setIcon(QIcon(self.release_gray_pixmap))
        self.release_button.setIconSize(self.release_active_pixmap.size())
        self.release_button.setGeometry(185, 300, 
                                        self.release_active_pixmap.width(), 
                                        self.release_active_pixmap.height())
        self.release_button.setFlat(True)
        self.release_button.setStyleSheet("border: none; background: transparent;")
        self.release_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.release_button.clicked.connect(self._on_release_clicked)
        self.release_button.setToolTip("Release CTRL key")
    
    def _setup_status_text(self):
        """Setup status text displays."""
        # Released text
        self.released_text = QLabel(self)
        released_pixmap = QPixmap(resource_path("assets/released_TEXT.png"))
        self.released_text.setPixmap(released_pixmap)
        self.released_text.setGeometry(120, 240, 
                                       released_pixmap.width(), 
                                       released_pixmap.height())
        self.released_text.setStyleSheet("background: transparent;")
        
        # Pressed text
        self.pressed_text = QLabel(self)
        pressed_pixmap = QPixmap(resource_path("assets/pressed_TEXT.png"))
        self.pressed_text.setPixmap(pressed_pixmap)
        self.pressed_text.setGeometry(120, 240, 
                                      pressed_pixmap.width(), 
                                      pressed_pixmap.height())
        self.pressed_text.setStyleSheet("background: transparent;")
        self.pressed_text.setVisible(False)
    
    def _setup_hotkey_selection(self):
        """Setup hotkey selection radio buttons."""
        # Label
        self.hotkey_label = QLabel("Greater Fortitude Hotkey:", self)
        self.hotkey_label.setGeometry(60, 266, 172, 26)
        self.hotkey_label.setStyleSheet(NUMBER_LABEL_STYLE)
        self.hotkey_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        
        # Radio buttons
        self.radio_4 = QRadioButton("4", self)
        self.radio_4.setGeometry(235, 266, 45, 26)
        self.radio_4.setCursor(Qt.CursorShape.PointingHandCursor)
        self.radio_4.setStyleSheet(RADIO_BUTTON_STYLE)
        
        self.radio_5 = QRadioButton("5", self)
        self.radio_5.setGeometry(280, 266, 45, 26)
        self.radio_5.setChecked(True)
        self.radio_5.setCursor(Qt.CursorShape.PointingHandCursor)
        self.radio_5.setStyleSheet(RADIO_BUTTON_STYLE)
        
        # Checkmarks
        self.check_4 = QLabel("✓", self)
        self.check_4.setGeometry(237, 270, 18, 18)
        self.check_4.setStyleSheet(CHECKMARK_STYLE)
        self.check_4.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.check_4.setVisible(False)
        
        self.check_5 = QLabel("✓", self)
        self.check_5.setGeometry(282, 270, 18, 18)
        self.check_5.setStyleSheet(CHECKMARK_STYLE)
        self.check_5.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.check_5.setVisible(True)
        
        # Button group
        self.hotkey_group = QButtonGroup(self)
        self.hotkey_group.addButton(self.radio_4)
        self.hotkey_group.addButton(self.radio_5)
        self.hotkey_group.buttonClicked.connect(self._on_hotkey_changed)
    
    def _setup_countdown(self):
        """Setup countdown timer display and alert."""
        # Countdown label
        self.countdown_label = QLabel("60.0", self)
        self.countdown_label.setGeometry(95, 358, 170, 60)
        self.countdown_label.setStyleSheet(COUNTDOWN_LABEL_STYLE)
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Glow effect
        self.countdown_glow = QGraphicsDropShadowEffect()
        self.countdown_glow.setBlurRadius(25)
        self.countdown_glow.setColor(QColor(0, 255, 0, 200))
        self.countdown_glow.setOffset(0, 0)
        self.countdown_label.setGraphicsEffect(self.countdown_glow)
        
        # Buff alert
        self.buff_alert = QLabel("BUFF", self)
        self.buff_alert.setGeometry(75, 140, 206, 80)
        self.buff_alert.setStyleSheet(BUFF_ALERT_STYLE)
        self.buff_alert.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.buff_alert.setVisible(False)
        
        # Alert glow
        self.buff_alert_glow = QGraphicsDropShadowEffect()
        self.buff_alert_glow.setBlurRadius(40)
        self.buff_alert_glow.setColor(QColor(255, 0, 0, 255))
        self.buff_alert_glow.setOffset(0, 0)
        self.buff_alert.setGraphicsEffect(self.buff_alert_glow)
    
    def _setup_control_buttons(self):
        """Setup timer control buttons."""
        # START/STOP button
        self.start_stop_btn = QPushButton("START", self)
        self.start_stop_btn.setGeometry(60, 380, 60, 20)
        self.start_stop_btn.setStyleSheet(START_STOP_BUTTON_STYLE)
        self.start_stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_stop_btn.clicked.connect(self._toggle_timer)
        
        # RESET button
        self.reset_btn = QPushButton("RESET", self)
        self.reset_btn.setGeometry(240, 380, 60, 20)
        self.reset_btn.setStyleSheet(RESET_BUTTON_STYLE)
        self.reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.reset_btn.clicked.connect(self._reset_timer)
    
    def _setup_window_buttons(self):
        """Setup window control buttons."""
        # Info button
        self.info_btn = QPushButton("ⓘ", self)
        self.info_btn.setGeometry(5, 5, 30, 30)
        self.info_btn.setStyleSheet(INFO_BUTTON_STYLE)
        self.info_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.info_btn.clicked.connect(lambda: show_info_dialog(self))
        self.info_btn.setToolTip("Application Information")
        
        # Minimize button
        self.minimize_btn = QPushButton("−", self)
        self.minimize_btn.setGeometry(285, 5, 30, 30)
        self.minimize_btn.setStyleSheet(MINIMIZE_BUTTON_STYLE)
        self.minimize_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.minimize_btn.clicked.connect(self.showMinimized)
        self.minimize_btn.setToolTip("Minimize")
        
        # Close button
        self.close_btn = QPushButton("×", self)
        self.close_btn.setGeometry(320, 5, 30, 30)
        self.close_btn.setStyleSheet(CLOSE_BUTTON_STYLE)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setToolTip("Close Application")
    
    # Event Handlers
    
    def _on_lock_clicked(self):
        """Handle Lock button click."""
        if self.lock_is_active:
            self.lock_is_active = False
            self.keyboard_mgr.press_ctrl()
            
            # Update UI
            self.lock_button.setIcon(QIcon(self.lock_gray_pixmap))
            self.release_button.setIcon(QIcon(self.release_active_pixmap))
            self.pressed_text.setVisible(True)
            self.released_text.setVisible(False)
            
            if self.analytics:
                self.analytics.track_event('ctrl_locked')
            
            print("✓ Lock button clicked - CTRL IS PRESSED")
    
    def _on_release_clicked(self):
        """Handle Release button click."""
        if not self.lock_is_active:
            self.lock_is_active = True
            self.keyboard_mgr.release_ctrl()
            
            # Update UI
            self.release_button.setIcon(QIcon(self.release_gray_pixmap))
            self.lock_button.setIcon(QIcon(self.lock_active_pixmap))
            self.pressed_text.setVisible(False)
            self.released_text.setVisible(True)
            
            if self.analytics:
                self.analytics.track_event('ctrl_released')
            
            print("✓ Release button clicked - CTRL RELEASED")
    
    def _on_hotkey_changed(self, button):
        """Handle hotkey selection change."""
        key = button.text()
        self.keyboard_mgr.set_hotkey(key)
        self.check_4.setVisible(self.radio_4.isChecked())
        self.check_5.setVisible(self.radio_5.isChecked())
    
    def _toggle_timer(self):
        """Toggle timer between running and stopped."""
        is_running = self.timer_mgr.toggle()
        
        if is_running:
            self.qt_timer.start(10)
            self.start_stop_btn.setText("STOP")
        else:
            self.qt_timer.stop()
            self.start_stop_btn.setText("START")
    
    def _reset_timer(self):
        """Reset timer manually."""
        self.timer_mgr.reset()
        self._update_countdown_display(60.0)
        self._hide_buff_alert()
        
        if not self.timer_mgr.is_running:
            self.qt_timer.start(10)
            self.timer_mgr.start()
            self.start_stop_btn.setText("STOP")
    
    def _on_hotkey_reset(self):
        """Handle hotkey triggered reset."""
        self.timer_mgr.reset()
        self._update_countdown_display(60.0)
        self._hide_buff_alert()
    
    def _on_timer_tick(self, seconds: float):
        """Handle timer tick callback."""
        self._update_countdown_display(seconds)
    
    def _on_timer_alert(self):
        """Handle timer alert callback."""
        self._show_buff_alert()
    
    def _update_countdown_display(self, seconds: float):
        """Update countdown label and color."""
        self.countdown_label.setText(f"{seconds:.1f}")
        
        # Update color based on time remaining
        zone = self.timer_mgr.get_color_zone()
        if zone == 'green':
            color, glow = COUNTDOWN_GREEN, QColor(0, 255, 0, 200)
        elif zone == 'yellow':
            color, glow = COUNTDOWN_YELLOW, QColor(255, 165, 0, 200)
        else:
            color, glow = COUNTDOWN_RED, QColor(255, 0, 0, 200)
        
        self.countdown_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font: bold 36pt "Cambria";
                background: transparent;
            }}
        """)
        self.countdown_glow.setColor(glow)
    
    def _show_buff_alert(self):
        """Show buff alert."""
        self.buff_alert.setVisible(True)
        self.buff_alert.raise_()
        self.alert_pulse_timer.start(100)
    
    def _hide_buff_alert(self):
        """Hide buff alert."""
        self.buff_alert.setVisible(False)
        self.alert_pulse_timer.stop()
        self.alert_pulse_state = 0
    
    def _pulse_alert(self):
        """Animate buff alert pulsing."""
        self.alert_pulse_state += 1
        if self.alert_pulse_state % 2 == 0:
            self.buff_alert_glow.setBlurRadius(40)
            self.buff_alert_glow.setColor(QColor(255, 0, 0, 255))
        else:
            self.buff_alert_glow.setBlurRadius(25)
            self.buff_alert_glow.setColor(QColor(255, 0, 0, 180))
    
    # Window Events
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press for window dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move for window dragging."""
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def closeEvent(self, event):
        """Handle application shutdown."""
        try:
            # Cleanup keyboard
            self.keyboard_mgr.cleanup()
            
            # Stop timers
            self.qt_timer.stop()
            self.alert_pulse_timer.stop()
            
            # Analytics
            if self.analytics:
                self.analytics.track_event('app_closed')
                self.analytics.shutdown()
                print("✓ Analytics shutdown complete")
        except Exception as e:
            print(f"Cleanup warning: {e}")
        
        event.accept()
