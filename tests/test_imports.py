from __future__ import annotations

import importlib

import pytest


def test_core_imports() -> None:
    import app.main  # noqa: F401
    import app.spec.ui_spec_loader  # noqa: F401
    import shared.core.io  # noqa: F401
    import src.tehl.solver.slipper_tehl  # noqa: F401
    import tools.validate_spec  # noqa: F401


def test_gui_imports_if_available() -> None:
    pytest.importorskip("PySide6")
    importlib.import_module("app.main_window")
    importlib.import_module("shared.ui.form_renderer")
    importlib.import_module("modules.tehl.ui.tehl_page")
