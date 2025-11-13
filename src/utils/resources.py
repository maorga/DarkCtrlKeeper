"""
Resource Path Utilities
========================

Helper functions for loading resources in both dev and PyInstaller modes.
"""

import os
import sys


def resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource, works for dev and for PyInstaller.
    
    When running as a script: uses current directory
    When running as PyInstaller exe: uses temporary _MEIPASS directory
    
    Args:
        relative_path: Relative path to resource
        
    Returns:
        Absolute path to resource
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Running as script - use current directory
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)
