import pytest

pytest.importorskip("PySide6")

from app.framework.pages.load_spectrum_page import create_default_row, create_load_spectrum_model


def test_default_row_values() -> None:
    row = create_default_row()
    assert row.index == 1
    assert row.max_pressure_mpa == 0.0
    assert row.frequency_per_hour == 100.0


def test_default_model_first_row() -> None:
    model = create_load_spectrum_model()
    assert model.rowCount() == 1
    assert model.columnCount() == 3
    assert model.item(0, 0).text() == "1"
    assert model.item(0, 1).text() == "0"
    assert model.item(0, 2).text() == "100"
