"""
Main Window
===========

The main application window that orchestrates all UI components and logic.
"""

import sys
import os
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QRadioButton,
    QButtonGroup, QGraphicsDropShadowEffect, QSizeGrip
)
from PyQt6.QtCore import Qt, QPoint, QSize, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QMouseEvent, QIcon, QColor, QPainter, QPen

from utils.resources import resource_path
from core.keyboard_manager import KeyboardManager
from core.timer_manager import TimerManager
from ui.styles import *
from ui.dialogs import show_info_dialog
from config.settings_manager import SettingsManager


class GothicSizeGrip(QSizeGrip):
    """
    Frameless-window resize grip with a dark-fantasy aesthetic.

    Draws three diagonal strokes (golden-amber + soft glow) toward the
    bottom-right corner entirely via paintEvent — no external image needed.
    The native QSizeGrip resize logic handles the actual window geometry.
    """

    def __init__(self, parent):
        super().__init__(parent)
        # SizeFDiagCursor (↘) is correct for a bottom-right resize handle
        self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        self.setToolTip("Drag to resize")
        self.setStyleSheet("background: transparent;")

    def paintEvent(self, event):  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        step = max(w // 4, 3)   # spacing between the three strokes

        # Pass 1 — soft amber glow halo
        glow_pen = QPen(
            QColor(210, 172, 72, 65), 8.5,
            Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
        )
        painter.setPen(glow_pen)
        for i in range(1, 4):
            offset = i * step
            painter.drawLine(
                max(0, w - offset), h - 1,
                w - 1, max(0, h - offset),
            )

        # Pass 2 — golden-amber metallic strokes
        main_pen = QPen(
            QColor(185, 152, 70, 225), 1.5,
            Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
        )
        painter.setPen(main_pen)
        for i in range(1, 4):
            offset = i * step
            painter.drawLine(
                max(0, w - offset), h - 1,
                w - 1, max(0, h - offset),
            )


class DarkCtrlKeeperWindow(QWidget):
    """
    Main application window for DarkCtrlKeeper.
    
    Orchestrates UI components, keyboard control, and timer logic.
    """
    
    # Base design dimensions (pixels at 100 % scale)
    BASE_W = 356
    BASE_H = 430

    # Qt signals for thread-safe operations
    reset_countdown_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()

        # Settings manager (created early so load/save can be called anywhere)
        self._settings_mgr = SettingsManager()

        # Initialize core managers
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
        self._current_sf = 1.0  # current scale factor

        # Restore persisted settings (hotkey, window size, lock state)
        self._load_settings()

        # Start keyboard listener
        self.keyboard_mgr.start_listening()
        
        print("✓ DarkCtrlKeeper initialized successfully")
    
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
        self.resize(self.BASE_W, self.BASE_H)
        self.setMinimumSize(180, 218)
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
        self._setup_resize_grip()

    def _setup_background(self):
        """Setup background image."""
        self.background_label = QLabel(self)
        self._bg_base_pixmap = QPixmap(resource_path("assets/base_background.png"))
        if self._bg_base_pixmap.isNull():
            print("ERROR: Could not load assets/base_background.png")
        self.background_label.setPixmap(self._bg_base_pixmap)
        self.background_label.setScaledContents(True)
        self.background_label.setGeometry(0, 0, self.BASE_W, self.BASE_H)
    
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
        
        self._lock_base_size = self.lock_active_pixmap.size()
        self.lock_button.setIcon(QIcon(self.lock_active_pixmap))
        self.lock_button.setIconSize(self._lock_base_size)
        self.lock_button.setGeometry(45, 300,
                                     self._lock_base_size.width(),
                                     self._lock_base_size.height())
        self.lock_button.setFlat(True)
        self.lock_button.setStyleSheet("border: none; background: transparent;")
        self.lock_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lock_button.clicked.connect(self._on_lock_clicked)
        self.lock_button.setToolTip("Lock CTRL key")
        
        # RELEASE button
        self.release_button = QPushButton(self)
        self.release_active_pixmap = QPixmap(resource_path("assets/released-button.png"))
        self.release_gray_pixmap = QPixmap(resource_path("assets/released-button-gray.png"))
        
        self._release_base_size = self.release_active_pixmap.size()
        self.release_button.setIcon(QIcon(self.release_gray_pixmap))
        self.release_button.setIconSize(self._release_base_size)
        self.release_button.setGeometry(185, 300,
                                        self._release_base_size.width(),
                                        self._release_base_size.height())
        self.release_button.setFlat(True)
        self.release_button.setStyleSheet("border: none; background: transparent;")
        self.release_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.release_button.clicked.connect(self._on_release_clicked)
        self.release_button.setToolTip("Release CTRL key")
    
    def _setup_status_text(self):
        """Setup status text displays."""
        # Released text
        self.released_text = QLabel(self)
        self._released_base_pixmap = QPixmap(resource_path("assets/released_TEXT.png"))
        self.released_text.setPixmap(self._released_base_pixmap)
        self.released_text.setGeometry(120, 240,
                                       self._released_base_pixmap.width(),
                                       self._released_base_pixmap.height())
        self.released_text.setStyleSheet("background: transparent;")

        # Pressed text
        self.pressed_text = QLabel(self)
        self._pressed_base_pixmap = QPixmap(resource_path("assets/pressed_TEXT.png"))
        self.pressed_text.setPixmap(self._pressed_base_pixmap)
        self.pressed_text.setGeometry(120, 240,
                                      self._pressed_base_pixmap.width(),
                                      self._pressed_base_pixmap.height())
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
    
    def _setup_resize_grip(self):
        """Add a gothic-themed resize grip to the bottom-right corner."""
        self.size_grip = GothicSizeGrip(self)
        self.size_grip.resize(20, 20)
        self.size_grip.move(self.BASE_W - 20, self.BASE_H - 20)
        self.size_grip.raise_()

    # ------------------------------------------------------------------ #
    #  Settings persistence                                                #
    # ------------------------------------------------------------------ #

    def _load_settings(self):
        """Apply persisted settings to the UI; falls back to defaults silently."""
        s = self._settings_mgr.load()

        # --- Hotkey radio selection ---
        hotkey = s["hotkey"]
        if hotkey == "4":
            self.radio_4.setChecked(True)
            self.check_4.setVisible(True)
            self.check_5.setVisible(False)
            self.keyboard_mgr.set_hotkey("4")
        else:
            self.radio_5.setChecked(True)
            self.check_4.setVisible(False)
            self.check_5.setVisible(True)
            self.keyboard_mgr.set_hotkey("5")

        # --- Window geometry ---
        saved_w = max(s["window_width"], self.minimumWidth())
        self.resize(saved_w, int(round(saved_w * self.BASE_H / self.BASE_W)))

        # --- Lock / Release state ---
        # lock_active == True  → CTRL is released (safe default on first run)
        # lock_active == False → CTRL was being held; restore that state
        if not s["lock_active"]:
            self._on_lock_clicked()

    def _save_settings(self):
        """Persist hotkey selection and window geometry to disk.

        lock_active is always saved as True (released) so CTRL is never
        automatically re-pressed on the next launch.
        """
        self._settings_mgr.save({
            "hotkey": "4" if self.radio_4.isChecked() else "5",
            "window_width": self.width(),
            "window_height": self.height(),
            "lock_active": True,
        })

    # ------------------------------------------------------------------ #
    #  Responsive resize                                                   #
    # ------------------------------------------------------------------ #

    def resizeEvent(self, event):
        """Enforce aspect ratio and proportionally reposition all widgets."""
        new_w = event.size().width()
        new_h = int(round(new_w * self.BASE_H / self.BASE_W))
        if abs(event.size().height() - new_h) > 1:
            self.resize(new_w, new_h)
            return
        super().resizeEvent(event)
        if hasattr(self, "background_label"):
            self._reposition_widgets(new_w, event.size().height())

    def _reposition_widgets(self, w, h):
        """Reposition and resize every widget proportionally to (w, h)."""
        sf = w / self.BASE_W
        self._current_sf = sf

        # Background fills the whole window
        self.background_label.setGeometry(0, 0, w, h)

        # Watermark
        self.watermark_label.setGeometry(0, int(68 * sf), w, max(int(20 * sf), 10))

        # Window control buttons (top corners)
        btn = max(int(30 * sf), 14)
        self.info_btn.setGeometry(int(5 * sf), int(5 * sf), btn, btn)
        self.minimize_btn.setGeometry(int(285 * sf), int(5 * sf), btn, btn)
        self.close_btn.setGeometry(int(320 * sf), int(5 * sf), btn, btn)

        # Status text (scale pixmaps smoothly)
        rel_w = max(int(self._released_base_pixmap.width() * sf), 10)
        rel_h = max(int(self._released_base_pixmap.height() * sf), 10)
        sx, sy = int(120 * sf), int(240 * sf)
        for lbl, base_px in (
            (self.released_text, self._released_base_pixmap),
            (self.pressed_text,  self._pressed_base_pixmap),
        ):
            lbl.setGeometry(sx, sy, rel_w, rel_h)
            lbl.setPixmap(base_px.scaled(
                rel_w, rel_h,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            ))

        # Hotkey row
        self.hotkey_label.setGeometry(
            int(60 * sf), int(266 * sf),
            max(int(172 * sf), 60), max(int(26 * sf), 14),
        )
        rb_h = max(int(26 * sf), 14)
        self.radio_4.setGeometry(int(235 * sf), int(266 * sf), max(int(45 * sf), 20), rb_h)
        self.radio_5.setGeometry(int(280 * sf), int(266 * sf), max(int(45 * sf), 20), rb_h)
        ck = max(int(18 * sf), 10)
        self.check_4.setGeometry(int(237 * sf), int(270 * sf), ck, ck)
        self.check_5.setGeometry(int(282 * sf), int(270 * sf), ck, ck)

        # Lock / Release icon-buttons
        lk_w = max(int(self._lock_base_size.width() * sf), 20)
        lk_h = max(int(self._lock_base_size.height() * sf), 20)
        self.lock_button.setGeometry(int(45 * sf), int(300 * sf), lk_w, lk_h)
        self.lock_button.setIconSize(QSize(lk_w, lk_h))

        rl_w = max(int(self._release_base_size.width() * sf), 20)
        rl_h = max(int(self._release_base_size.height() * sf), 20)
        self.release_button.setGeometry(int(185 * sf), int(300 * sf), rl_w, rl_h)
        self.release_button.setIconSize(QSize(rl_w, rl_h))

        # Countdown label
        self.countdown_label.setGeometry(
            int(95 * sf), int(358 * sf),
            max(int(170 * sf), 60), max(int(60 * sf), 30),
        )

        # Buff alert overlay
        self.buff_alert.setGeometry(
            int(75 * sf), int(140 * sf),
            max(int(206 * sf), 60), max(int(80 * sf), 30),
        )

        # Control buttons (START/STOP · RESET)
        cb_w = max(int(60 * sf), 28)
        cb_h = max(int(20 * sf), 12)
        self.start_stop_btn.setGeometry(int(60 * sf), int(380 * sf), cb_w, cb_h)
        self.reset_btn.setGeometry(int(240 * sf), int(380 * sf), cb_w, cb_h)

        # Size grip stays at bottom-right; scale with window
        gs = max(int(20 * sf), 12)
        self.size_grip.setGeometry(w - gs, h - gs, gs, gs)
        self.size_grip.raise_()

        # Refresh all font-based styles
        self._apply_scaled_styles(sf)

    # ------------------------------------------------------------------ #
    #  Dynamic style generation                                            #
    # ------------------------------------------------------------------ #

    def _apply_scaled_styles(self, sf):
        """Regenerate all QSS with font sizes and radii scaled by sf."""
        # Watermark
        wm_pt = max(int(8 * sf), 5)
        self.watermark_label.setStyleSheet(f"""
            QLabel {{
                color: rgba(200, 180, 150, 0.7);
                font-family: "Georgia", "Times New Roman", serif;
                font-size: {wm_pt}pt;
                font-style: italic;
                background: transparent;
                letter-spacing: 1px;
            }}
        """)

        # Window control buttons
        wb_pt = max(int(14 * sf), 7)
        wb_br = max(int(15 * sf), 5)
        wb_bw = max(int(2 * sf), 1)
        self.info_btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(70, 130, 180, 0.6);
                color: white;
                font: bold {wb_pt}pt Arial;
                border-radius: {wb_br}px;
                border: {wb_bw}px solid rgba(100, 149, 237, 0.5);
            }}
            QPushButton:hover {{
                background: rgba(100, 149, 237, 0.8);
                border: {wb_bw}px solid rgba(135, 206, 250, 0.8);
            }}
        """)
        self.minimize_btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(139, 139, 0, 0.7);
                color: white;
                font: bold {wb_pt}pt Arial;
                border-radius: {wb_br}px;
                border: {wb_bw}px solid rgba(255, 255, 0, 0.5);
            }}
            QPushButton:hover {{
                background: rgba(218, 165, 32, 0.9);
                border: {wb_bw}px solid rgba(255, 215, 0, 0.8);
            }}
        """)
        self.close_btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(139, 0, 0, 0.7);
                color: white;
                font: bold {wb_pt}pt Arial;
                border-radius: {wb_br}px;
                border: {wb_bw}px solid rgba(255, 0, 0, 0.5);
            }}
            QPushButton:hover {{
                background: rgba(220, 20, 60, 0.9);
                border: {wb_bw}px solid rgba(255, 0, 0, 0.8);
            }}
        """)

        # Hotkey label
        hl_pt = max(int(9 * sf), 5)
        self.hotkey_label.setStyleSheet(f"""
            QLabel {{
                color: #E8D5B7;
                font: bold {hl_pt}pt "Georgia";
                background: transparent;
            }}
        """)

        # Radio buttons
        rb_pt  = max(int(11 * sf), 5)
        rb_ind = max(int(16 * sf), 8)
        rb_bw  = max(int(2 * sf), 1)
        rb_sp  = max(int(6 * sf), 3)
        rb_style = f"""
            QRadioButton {{
                color: #E8D5B7;
                font: bold {rb_pt}pt "Georgia";
                spacing: {rb_sp}px;
                background: transparent;
            }}
            QRadioButton::indicator {{
                width: {rb_ind}px;
                height: {rb_ind}px;
                border-radius: {rb_ind // 2}px;
                border: {rb_bw}px solid rgba(160, 130, 75, 0.75);
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(48, 44, 62, 0.85),
                    stop:1 rgba(28, 24, 42, 0.90));
            }}
            QRadioButton::indicator:hover {{
                border: {rb_bw}px solid rgba(190, 155, 95, 0.90);
            }}
            QRadioButton::indicator:checked {{
                border: {rb_bw}px solid rgba(255, 215, 0, 0.7);
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 215, 0, 0.5),
                    stop:1 rgba(218, 165, 32, 0.6));
            }}
        """
        self.radio_4.setStyleSheet(rb_style)
        self.radio_5.setStyleSheet(rb_style)

        # Checkmarks
        ck_pt = max(int(15 * sf), 7)
        ck_style = f"""
            QLabel {{
                color: #00FF00;
                font: bold {ck_pt}pt Arial;
                background: transparent;
            }}
        """
        self.check_4.setStyleSheet(ck_style)
        self.check_5.setStyleSheet(ck_style)

        # Countdown (colour is managed separately by _update_countdown_display)
        cd_pt = max(int(36 * sf), 10)
        zone = self.timer_mgr.get_color_zone()
        color = {"green": COUNTDOWN_GREEN, "yellow": COUNTDOWN_YELLOW}.get(
            zone, COUNTDOWN_RED
        )
        self.countdown_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font: bold {cd_pt}pt "Cambria";
                background: transparent;
            }}
        """)

        # Buff alert overlay
        ba_pt  = max(int(48 * sf), 10)
        ba_bw  = max(int(4 * sf), 1)
        ba_br  = max(int(10 * sf), 3)
        ba_pad = max(int(10 * sf), 3)
        self.buff_alert.setStyleSheet(f"""
            QLabel {{
                color: #FF0000;
                font: bold {ba_pt}pt "Impact";
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(139, 0, 0, 0.95),
                    stop:1 rgba(80, 0, 0, 0.98));
                border: {ba_bw}px solid #FF0000;
                border-radius: {ba_br}px;
                padding: {ba_pad}px;
            }}
        """)

        # START/STOP and RESET buttons
        cb_pt = max(int(9 * sf), 5)
        cb_bw = max(int(2 * sf), 1)
        cb_br = max(int(4 * sf), 2)
        self.start_stop_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(139, 0, 0, 0.8),
                    stop:1 rgba(100, 0, 0, 0.9));
                color: #FFD700;
                font: bold {cb_pt}pt "Georgia";
                border: {cb_bw}px solid rgba(139, 0, 0, 0.9);
                border-radius: {cb_br}px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(180, 0, 0, 0.9),
                    stop:1 rgba(139, 0, 0, 1.0));
                border: {cb_bw}px solid rgba(180, 0, 0, 1.0);
            }}
            QPushButton:pressed {{ background: rgba(80, 0, 0, 0.95); }}
        """)
        self.reset_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(34, 139, 34, 0.8),
                    stop:1 rgba(0, 100, 0, 0.9));
                color: #FFD700;
                font: bold {cb_pt}pt "Georgia";
                border: {cb_bw}px solid rgba(34, 139, 34, 0.9);
                border-radius: {cb_br}px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(50, 205, 50, 0.9),
                    stop:1 rgba(34, 139, 34, 1.0));
                border: {cb_bw}px solid rgba(50, 205, 50, 1.0);
            }}
            QPushButton:pressed {{ background: rgba(0, 80, 0, 0.95); }}
        """)

    # ------------------------------------------------------------------ #
    #  Event Handlers                                                      #
    # ------------------------------------------------------------------ #

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

            print("✓ Lock button clicked - CTRL IS PRESSED")
            self._save_settings()
    
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

            print("✓ Release button clicked - CTRL RELEASED")
            self._save_settings()
    
    def _on_hotkey_changed(self, button):
        """Handle hotkey selection change."""
        key = button.text()
        self.keyboard_mgr.set_hotkey(key)
        self.check_4.setVisible(self.radio_4.isChecked())
        self.check_5.setVisible(self.radio_5.isChecked())
        self._save_settings()
    
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
                font: bold {max(int(36 * self._current_sf), 10)}pt "Cambria";
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
        self._save_settings()  # flush final geometry and state before exit
        try:
            # Cleanup keyboard
            self.keyboard_mgr.cleanup()
            
            # Stop timers
            self.qt_timer.stop()
            self.alert_pulse_timer.stop()
        except Exception as e:
            print(f"Cleanup warning: {e}")
        
        event.accept()
