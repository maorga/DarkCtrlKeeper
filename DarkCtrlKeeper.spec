# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src\\main.py'],
    pathex=['src'],
    binaries=[],
    datas=[('assets', 'assets')],
    hiddenimports=['PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets', 'pynput.keyboard', 'pynput.keyboard._win32'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'pandas', 'scipy', 'PIL', 'pytest', 'unittest', 'email', 'xml', 'requests', 'urllib3', 'dotenv', 'certifi', 'charset_normalizer', 'PyQt6.QtNetwork', 'PyQt6.QtOpenGL', 'PyQt6.QtQml', 'PyQt6.QtQuick', 'PyQt6.QtSql', 'PyQt6.QtWebEngine', 'PyQt6.QtMultimedia', 'PyQt6.QtWebEngineCore', 'PyQt6.QtWebEngineWidgets', 'PyQt6.QtWebSockets', 'PyQt6.Qt3D', 'PyQt6.QtBluetooth', 'PyQt6.QtDBus', 'PyQt6.QtDesigner', 'PyQt6.QtHelp', 'PyQt6.QtMultimediaWidgets', 'PyQt6.QtNfc', 'PyQt6.QtPositioning', 'PyQt6.QtPrintSupport', 'PyQt6.QtRemoteObjects', 'PyQt6.QtSensors', 'PyQt6.QtSerialPort', 'PyQt6.QtSvg', 'PyQt6.QtSvgWidgets', 'PyQt6.QtXml', 'PyQt6.QtTest', 'PyQt6.QtWebChannel', 'sqlite3', 'bz2', 'lzma', '_decimal', '_hashlib', '_ssl', 'readline', 'grp', 'pwd', 'resource', 'termios'],
    noarchive=False,
    optimize=2,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='DarkCtrlKeeper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=True,
    icon=['assets\\ICON.ico'],
    manifest='scripts\\admin.manifest',
)
