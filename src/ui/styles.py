"""
UI Styles and Constants
========================

Centralized styling for all UI components.
"""

# Radio button styling
RADIO_BUTTON_STYLE = """
    QRadioButton {
        color: #E8D5B7;
        font: bold 11pt "Georgia";
        spacing: 6px;
        background: transparent;
    }
    QRadioButton::indicator {
        width: 16px;
        height: 16px;
        border-radius: 8px;
        border: 2px solid rgba(160, 130, 75, 0.75);
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(48, 44, 62, 0.85),
            stop:1 rgba(28, 24, 42, 0.90));
    }
    QRadioButton::indicator:hover {
        border: 2px solid rgba(190, 155, 95, 0.90);
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(58, 54, 72, 0.90),
            stop:1 rgba(38, 34, 52, 0.95));
    }
    QRadioButton::indicator:checked {
        border: 2px solid rgba(255, 215, 0, 0.7);
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(255, 215, 0, 0.5),
            stop:1 rgba(218, 165, 32, 0.6));
    }
"""

# Watermark label styling
WATERMARK_STYLE = """
    QLabel {
        color: rgba(200, 180, 150, 0.7);
        font-family: "Georgia", "Times New Roman", serif;
        font-size: 8pt;
        font-style: italic;
        font-weight: normal;
        background: transparent;
        letter-spacing: 1px;
    }
"""

# Number label styling
NUMBER_LABEL_STYLE = """
    QLabel {
        color: #E8D5B7;
        font: bold 9pt "Georgia";
        background: transparent;
    }
"""

# Checkmark styling
CHECKMARK_STYLE = """
    QLabel {
        color: #00FF00;
        font: bold 15pt Arial;
        background: transparent;
    }
"""

# Countdown label styling
COUNTDOWN_LABEL_STYLE = """
    QLabel {
        color: #00FF00;
        font: bold 36pt "Cambria";
        background: transparent;
    }
"""

# Buff alert styling
BUFF_ALERT_STYLE = """
    QLabel {
        color: #FF0000;
        font: bold 48pt "Impact";
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(139, 0, 0, 0.95),
            stop:1 rgba(80, 0, 0, 0.98));
        border: 4px solid #FF0000;
        border-radius: 10px;
        padding: 10px;
    }
"""

# Start/Stop button styling
START_STOP_BUTTON_STYLE = """
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(139, 0, 0, 0.8),
            stop:1 rgba(100, 0, 0, 0.9));
        color: #FFD700;
        font: bold 9pt "Georgia";
        border: 2px solid rgba(139, 0, 0, 0.9);
        border-radius: 4px;
    }
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(180, 0, 0, 0.9),
            stop:1 rgba(139, 0, 0, 1.0));
        border: 2px solid rgba(180, 0, 0, 1.0);
    }
    QPushButton:pressed {
        background: rgba(80, 0, 0, 0.95);
    }
"""

# Reset button styling
RESET_BUTTON_STYLE = """
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(34, 139, 34, 0.8),
            stop:1 rgba(0, 100, 0, 0.9));
        color: #FFD700;
        font: bold 9pt "Georgia";
        border: 2px solid rgba(34, 139, 34, 0.9);
        border-radius: 4px;
    }
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(50, 205, 50, 0.9),
            stop:1 rgba(34, 139, 34, 1.0));
        border: 2px solid rgba(50, 205, 50, 1.0);
    }
    QPushButton:pressed {
        background: rgba(0, 80, 0, 0.95);
    }
"""

# Minimize button styling
MINIMIZE_BUTTON_STYLE = """
    QPushButton {
        background: rgba(139, 139, 0, 0.7);
        color: white;
        font: bold 20pt Arial;
        border-radius: 15px;
        border: 2px solid rgba(255, 255, 0, 0.5);
    }
    QPushButton:hover {
        background: rgba(218, 165, 32, 0.9);
        border: 2px solid rgba(255, 215, 0, 0.8);
    }
"""

# Close button styling
CLOSE_BUTTON_STYLE = """
    QPushButton {
        background: rgba(139, 0, 0, 0.7);
        color: white;
        font: bold 20pt Arial;
        border-radius: 15px;
        border: 2px solid rgba(255, 0, 0, 0.5);
    }
    QPushButton:hover {
        background: rgba(220, 20, 60, 0.9);
        border: 2px solid rgba(255, 0, 0, 0.8);
    }
"""

# Info button styling
INFO_BUTTON_STYLE = """
    QPushButton {
        background: rgba(70, 130, 180, 0.6);
        color: white;
        font: bold 18pt Arial;
        border-radius: 15px;
        border: 2px solid rgba(100, 149, 237, 0.5);
    }
    QPushButton:hover {
        background: rgba(100, 149, 237, 0.8);
        border: 2px solid rgba(135, 206, 250, 0.8);
    }
"""

# Dialog styling
DIALOG_STYLE = """
    QDialog {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(25, 25, 40, 0.98),
            stop:1 rgba(15, 15, 25, 0.99));
    }
"""

TEXT_BROWSER_STYLE = """
    QTextBrowser {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(25, 25, 40, 0.98),
            stop:1 rgba(15, 15, 25, 0.99));
        color: #E8D5B7;
        border: 2px solid rgba(100, 149, 237, 0.5);
        border-radius: 8px;
        padding: 15px;
        font-family: "Georgia", serif;
        font-size: 10pt;
    }
    QScrollBar:vertical {
        background: rgba(25, 25, 40, 0.9);
        width: 12px;
        border-radius: 6px;
        margin: 0;
    }
    QScrollBar::handle:vertical {
        background: rgba(100, 149, 237, 0.7);
        border-radius: 6px;
        min-height: 20px;
    }
    QScrollBar::handle:vertical:hover {
        background: rgba(135, 206, 250, 0.8);
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
"""

DIALOG_BUTTON_STYLE = """
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(70, 130, 180, 0.8),
            stop:1 rgba(50, 100, 150, 0.9));
        color: #FFD700;
        font: bold 10pt "Georgia";
        border: 2px solid rgba(100, 149, 237, 0.9);
        border-radius: 4px;
        padding: 8px 25px;
        min-width: 80px;
    }
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(100, 149, 237, 0.9),
            stop:1 rgba(70, 130, 180, 1.0));
        border: 2px solid rgba(135, 206, 250, 1.0);
    }
"""

# Color constants for countdown timer
COUNTDOWN_GREEN = "#00FF00"
COUNTDOWN_YELLOW = "#FFd900"
COUNTDOWN_RED = "#FF0000"
