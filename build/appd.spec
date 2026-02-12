# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

project_root = Path.cwd()

pyside_hidden = collect_submodules("PySide6")
matplotlib_hidden = collect_submodules("matplotlib.backends")

datas = []
# Required runtime configs
datas += [(str(project_root / "modules" / "tehl" / "spec" / "ui_spec.yaml"), "modules/tehl/spec")]
datas += [(str(project_root / "assets" / "i18n" / "ui_text_zh_CN.yaml"), "assets/i18n")]

# Optional refs (pack if present)
for pattern, target in [
    ("ref/docs/*.pdf", "ref/docs"),
    ("ref/appd_screenshots/*.jpg", "ref/appd_screenshots"),
]:
    for file in project_root.glob(pattern):
        datas.append((str(file), target))

# ensure matplotlib data and Qt plugin metadata are included
for item in collect_data_files("matplotlib"):
    datas.append(item)
for item in collect_data_files("PySide6"):
    datas.append(item)

hiddenimports = pyside_hidden + matplotlib_hidden + [
    "matplotlib.backends.backend_qtagg",
    "tools.smoke_run",
]

a = Analysis(
    ["app/main.py"],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=["build/runtime_hook_qt.py"],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="APPD",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="APPD",
)
