from pathlib import Path

from app.domain.io_project import load_project, save_project
from app.domain.project_model import LoadPoint, ProjectModel, SCHEMA_VERSION


def test_project_save_and_load_roundtrip(tmp_path: Path) -> None:
    project = ProjectModel(
        load_spectrum=[LoadPoint(max_pressure_mpa=31.5, freq_per_hour=120.0)],
        rated_pressure_mpa=28.0,
        active_module="load_spectrum",
    )
    out = tmp_path / "demo.apdd.json"
    save_project(out, project)

    loaded = load_project(out)
    assert loaded.schema_version == SCHEMA_VERSION
    assert loaded.rated_pressure_mpa == 28.0
    assert loaded.active_module == "load_spectrum"
    assert len(loaded.load_spectrum) == 1
    assert loaded.load_spectrum[0].max_pressure_mpa == 31.5
    assert loaded.load_spectrum[0].freq_per_hour == 120.0


def test_schema_version_and_reserved_modules_exist(tmp_path: Path) -> None:
    out = tmp_path / "blank.apdd.json"
    save_project(out, ProjectModel())
    loaded = load_project(out)

    assert loaded.schema_version == SCHEMA_VERSION
    for key in (
        "tehl",
        "contamination",
        "servo_valve",
        "cycloid_pump",
        "gear_pump",
        "hydraulic_cylinder",
    ):
        assert key in loaded.modules_reserved
