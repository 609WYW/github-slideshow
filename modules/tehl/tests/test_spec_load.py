from __future__ import annotations

from pathlib import Path

from app.spec.ui_spec_loader import load_ui_spec
from tools.validate_spec import validate_spec


def test_spec_load_and_validate() -> None:
    path = Path("modules/tehl/spec/ui_spec.yaml")
    spec = load_ui_spec(path)
    errors = validate_spec(spec)
    assert errors == []
    assert spec["module"]["id"] == "tehl"


def test_stage5_inputs_groups_order_and_defaults() -> None:
    spec = load_ui_spec(Path("modules/tehl/spec/ui_spec.yaml"))
    inputs_tab = next(t for t in spec["ui"]["tabs"] if t["id"] == "inputs")
    group_titles = [g["title"] for g in inputs_tab["groups"]]
    assert group_titles == [
        "Solve Parameters",
        "Fluid",
        "Geometry",
        "Materials",
        "Boundary",
        "TEHL Models",
        "TEHL Parameters",
        "Tilt Options",
    ]

    lookup = {f["id"]: f for g in inputs_tab["groups"] for f in g["fields"]}
    assert lookup["revolutions"]["default"] == 5
    assert lookup["density_rho"]["default"] == 850.0
    assert lookup["pressure_model"]["default"] == "Reynolds"
    assert lookup["max_iterations"]["default"] == 300
    assert lookup["enable_tilt_x"]["default"] is False
