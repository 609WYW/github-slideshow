from __future__ import annotations

import pytest

np = pytest.importorskip("numpy")

from src.tehl.solver.slipper_tehl import SlipperTEHL


def test_slipper_tehl_run_returns_nonzero_fields() -> None:
    solver = SlipperTEHL(
        {
            "nr": 41,
            "nth": 61,
            "high_pressure_ph": 35e6,
            "case_pressure_pc": 1e5,
            "initial_film_thickness_h0": 5e-6,
        }
    )
    out = solver.run()

    for key in ["p_film", "p_contact", "p_total"]:
        assert key in out
        arr = out[key]
        assert arr.shape == (41, 61)
        assert np.isfinite(arr).all()

    assert np.nanmax(out["p_film"]) > 0.0
    assert np.nanmax(out["p_total"]) > 0.0
    assert float(np.nanstd(out["p_total"])) > 0.0
