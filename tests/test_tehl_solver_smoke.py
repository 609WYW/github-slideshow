from modules.tehl.solver import CancelToken, run_tehl_case
from modules.tehl.solver.reynolds import mpa_to_pa, rpm_to_rad_s


def _grid_sum(grid: list[list[float]]) -> float:
    return sum(sum(row) for row in grid)


def test_unit_conversions() -> None:
    assert abs(mpa_to_pa(1.0) - 1_000_000.0) < 1e-6
    assert abs(rpm_to_rad_s(60.0) - 6.283185307179586) < 1e-9


def test_solver_smoke_for_ctdma_and_tdma() -> None:
    for method in ("CTDMA", "TDMA"):
        results = run_tehl_case(
            {
                "solver_method": method,
                "rated_pressure_mpa": 21.0,
                "speed_rpm": 1500.0,
                "inlet_temp_c": 60.0,
                "length_mm": 12.0,
                "width_mm": 10.0,
                "nx": 24,
                "ny": 18,
            }
        )
        assert _grid_sum(results["pressure"]) > 0.0
        assert _grid_sum(results["p_contact"]) > 0.0
        assert _grid_sum(results["p_total"]) > _grid_sum(results["pressure"])
        assert _grid_sum(results["thermal"]) > 0.0
        assert _grid_sum(results["heat_flux"]) > 0.0


def test_solver_cancel_token() -> None:
    token = CancelToken()
    token.cancel()
    results = run_tehl_case({"solver_method": "CTDMA", "nx": 16, "ny": 12}, token)
    assert results["cancelled"] is True
    assert _grid_sum(results["pressure"]) >= 0.0
