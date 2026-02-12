from __future__ import annotations

from pathlib import Path

from app.spec.ui_spec_loader import load_ui_spec


def test_tehl_subpages_exist() -> None:
    spec = load_ui_spec(Path("modules/tehl/spec/ui_spec.yaml"))
    ids = [p["id"] for p in spec["ui"]["subpages"]]
    assert ids == ["inputs", "solver", "outputs"]
