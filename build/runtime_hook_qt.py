from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "QtAgg")

# Help Qt find bundled plugins on Windows one-dir bundle
base = Path(getattr(__import__("sys"), "_MEIPASS", Path(__file__).resolve().parents[1]))
qt_plugins = base / "PySide6" / "plugins"
if qt_plugins.exists():
    os.environ.setdefault("QT_PLUGIN_PATH", str(qt_plugins))
    os.environ.setdefault("QT_QPA_PLATFORM_PLUGIN_PATH", str(qt_plugins / "platforms"))
