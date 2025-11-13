"""
Dialogs
=======

Custom dialog windows for the application.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTextBrowser, 
    QDialogButtonBox, QApplication
)
from PyQt6.QtCore import Qt

from .styles import (
    DIALOG_STYLE, TEXT_BROWSER_STYLE, 
    DIALOG_BUTTON_STYLE
)


INFO_TEXT = """
<h2 style="color: #FFD700; text-align: center;">DarkCtrlKeeper</h2>
<p style="color: #E8D5B7;"><b>Version:</b> 1.0.0</p>
<p style="color: #E8D5B7;"><b>Author:</b> MaorG</p>
<p style="color: #E8D5B7;"><b>License:</b> MIT</p>

<hr style="border: 1px solid #8B4513;">

<h3 style="color: #FFD700;">Description</h3>
<p style="color: #E8D5B7;">Dark fantasy themed CTRL key locker designed for MU Online gamers. 
Maintains Greater Fortitude buff by virtually locking the CTRL key.</p>

<h3 style="color: #FFD700;">Features</h3>
<ul style="color: #E8D5B7;">
<li>Virtual CTRL key control (press and hold, then release)</li>
<li>Interactive button interface with visual feedback</li>
<li>Countdown timer with buff alert system</li>
<li>Customizable Greater Fortitude hotkey (4 or 5)</li>
<li>Always-on-top window for easy access</li>
</ul>

<h3 style="color: #FFD700;">How to Use</h3>
<ol style="color: #E8D5B7;">
<li>Click <b>LOCK CTRL</b> to hold CTRL key</li>
<li>Select your Greater Fortitude hotkey (4 or 5)</li>
<li>Press <b>START</b> to begin the 60-second countdown</li>
<li>When timer shows "BUFF", press your hotkey to refresh</li>
<li>Click <b>RELEASE CTRL</b> to release</li>
</ol>

<p style="color: #B8860B; font-style: italic; text-align: center;">Enjoy your gaming experience!</p>
"""


def show_info_dialog(parent):
    """
    Display information dialog about the application.
    
    Args:
        parent: Parent widget
    """
    dialog = QDialog(parent)
    dialog.setWindowTitle("DarkCtrlKeeper - Information")
    dialog.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
    
    # Create layout
    layout = QVBoxLayout(dialog)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(15)
    
    # Create text browser for scrollable content
    text_browser = QTextBrowser(dialog)
    text_browser.setOpenExternalLinks(False)
    text_browser.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    text_browser.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    text_browser.setHtml(INFO_TEXT)
    text_browser.setStyleSheet(TEXT_BROWSER_STYLE)
    
    layout.addWidget(text_browser)
    
    # Create OK button
    button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
    button_box.accepted.connect(dialog.accept)
    button_box.setStyleSheet(DIALOG_BUTTON_STYLE)
    
    layout.addWidget(button_box)
    
    # Style the dialog
    dialog.setStyleSheet(DIALOG_STYLE)
    
    # Calculate optimal size based on screen resolution
    screen = QApplication.primaryScreen().geometry()
    screen_width = screen.width()
    screen_height = screen.height()
    
    # Set dialog size as percentage of screen size (responsive)
    if screen_width < 1366:  # Small screens
        dialog_width = int(screen_width * 0.6)
        dialog_height = int(screen_height * 0.7)
    elif screen_width < 1920:  # Medium screens
        dialog_width = int(screen_width * 0.45)
        dialog_height = int(screen_height * 0.65)
    else:  # Large screens
        dialog_width = 650
        dialog_height = 600
    
    # Ensure minimum size
    dialog_width = max(dialog_width, 500)
    dialog_height = max(dialog_height, 450)
    
    dialog.resize(dialog_width, dialog_height)
    
    # Center the dialog on screen
    dialog_geometry = dialog.frameGeometry()
    center_point = screen.center()
    dialog_geometry.moveCenter(center_point)
    dialog.move(dialog_geometry.topLeft())
    
    # Show dialog
    dialog.exec()
