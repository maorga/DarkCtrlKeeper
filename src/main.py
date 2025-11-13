"""
DarkCtrlKeeper - Main Application Entry Point
==============================================

Dark fantasy themed CTRL key locker for MU Online gamers.
Maintains Greater Fortitude buff by locking CTRL key.

Version: 1.0.0
Author: MaorG
License: MIT
"""

import sys
from PyQt6.QtWidgets import QApplication

from ui.main_window import DarkCtrlKeeperWindow


def main():
    """
    Main application entry point.
    
    Creates the QApplication, shows the DarkCtrlKeeper window,
    and runs the event loop.
    """
    app = QApplication(sys.argv)
    app.setApplicationName("DarkCtrlKeeper")
    app.setApplicationVersion("1.0.0")
    
    # Create and show main window
    window = DarkCtrlKeeperWindow()
    window.show()
    
    # Center window on screen
    screen_geometry = app.primaryScreen().geometry()
    window_geometry = window.frameGeometry()
    center_point = screen_geometry.center()
    window_geometry.moveCenter(center_point)
    window.move(window_geometry.topLeft())
    
    print("=" * 50)
    print("DarkCtrlKeeper is running")
    print("Control: Use on-screen buttons to Lock or Release CTRL")
    print("Close: Click X or press Alt+F4")
    print("=" * 50)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
