from __future__ import annotations


def _grid_max(grid: list[list[float]]) -> float:
    return max((max(row) for row in grid), default=0.0)


def build_kpi(results: dict[str, object]) -> dict[str, float]:
    p_film = results.get("pressure", [])
    p_contact = results.get("p_contact", [])
    p_total = results.get("pressure_components", [])
    thermal = results.get("thermal", [])

    return {
        "max_p_film_pa": _grid_max(p_film),
        "max_p_contact_pa": _grid_max(p_contact),
        "max_p_total_pa": _grid_max(p_total),
        "max_temp_c": _grid_max(thermal),
    }
