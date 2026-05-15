"""
Settings Manager
================

Persists user preferences to a local ``settings.json`` file.

The file is written alongside the executable when packaged with PyInstaller,
or in the project root when running from source.  All I/O is wrapped in
try/except so a missing or corrupt file never crashes the application.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any

# Keys and their default values — also act as the schema for validation.
_DEFAULTS: dict[str, Any] = {
    "hotkey": "5",          # "4" or "5"
    "window_width": 356,    # int ≥ minimum window width
    "window_height": 430,   # int (kept in sync with width via aspect ratio)
    "lock_active": True,    # True = CTRL released, False = CTRL held
}


class SettingsManager:
    """
    Read/write ``settings.json`` next to the executable (or project root).

    Usage::

        mgr = SettingsManager()
        data = mgr.load()        # always returns a complete dict
        mgr.save({"hotkey": "4", ...})
    """

    def __init__(self) -> None:
        self._path: Path = self._resolve_path()

    # ------------------------------------------------------------------
    # Path resolution
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_path() -> Path:
        """Return a writable path for ``settings.json``.

        - Packaged (PyInstaller): ``%APPDATA%\\DarkCtrlKeeper\\settings.json``
          so the file is always writable even when the .exe lives in a
          protected location such as ``C:\\Program Files``.
        - Development: project root (two levels above ``src/``).
        """
        if getattr(sys, "frozen", False):
            appdata = Path(os.environ.get("APPDATA", Path.home()))
            folder = appdata / "DarkCtrlKeeper"
            folder.mkdir(parents=True, exist_ok=True)
            return folder / "settings.json"
        # Development run — write in the project root.
        return Path(__file__).parent.parent.parent / "settings.json"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load(self) -> dict[str, Any]:
        """
        Return stored settings merged with defaults.

        Unknown keys and values with wrong types are silently ignored so
        that a partially-written or outdated file never causes issues.
        """
        data: dict[str, Any] = dict(_DEFAULTS)
        try:
            raw = self._path.read_text(encoding="utf-8")
            stored: dict = json.loads(raw)
            for key, default in _DEFAULTS.items():
                if key in stored and isinstance(stored[key], type(default)):
                    data[key] = stored[key]
        except (FileNotFoundError, json.JSONDecodeError, OSError, ValueError):
            pass  # absent or corrupt — caller receives pure defaults
        return data

    def save(self, data: dict[str, Any]) -> None:
        """Write *data* to disk; silently swallows I/O errors."""
        try:
            self._path.write_text(
                json.dumps(data, indent=2),
                encoding="utf-8",
            )
        except OSError:
            pass
