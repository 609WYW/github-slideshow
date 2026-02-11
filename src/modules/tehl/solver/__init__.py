from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .contact import compute_contact_pressure
from .kpi import build_kpi
from .mesh import MeshConfig, build_mesh
from .reynolds import solve_reynolds
from .thermal import solve_thermal
from .wear import estimate_wear


@dataclass(slots=True)
class CancelToken:
    cancelled: bool = False

    def cancel(self) -> None:
        self.cancelled = True


def run_tehl_case(config: dict[str, Any], cancel_token: CancelToken | None = None) -> dict[str, Any]:
    token = cancel_token or CancelToken()

    mesh = build_mesh(
        MeshConfig(
            nx=int(config.get("nx", 48)),
            ny=int(config.get("ny", 36)),
            length_mm=float(config.get("length_mm", 12.0)),
            width_mm=float(config.get("width_mm", 10.0)),
        )
    )

    pressure = solve_reynolds(
        mesh=mesh,
        method=str(config.get("solver_method", "CTDMA")),
        rated_pressure_mpa=float(config.get("rated_pressure_mpa", 21.0)),
        speed_rpm=float(config.get("speed_rpm", 1500.0)),
        cancel_check=lambda: token.cancelled,
    )

    contact = compute_contact_pressure(pressure)
    thermal = solve_thermal(contact["p_total"], float(config.get("inlet_temp_c", 60.0)), float(config.get("speed_rpm", 1500.0)))
    wear = estimate_wear(contact["p_total"], float(config.get("duration_h", 100.0)))

    merged: dict[str, Any] = {
        "pressure": pressure,
        "pressure_components": contact["p_total"],
        "p_contact": contact["p_contact"],
        "p_total": contact["p_total"],
        "film": [[max(1e-7, 8e-6 - cell * 1e-13) for cell in row] for row in contact["p_total"]],
        "deformation": [[cell * 1e-9 for cell in row] for row in contact["p_total"]],
        "thermal": thermal["thermal"],
        "heat_flux": thermal["heat_flux"],
        "viscosity_temp": thermal["viscosity_temp"],
        "wear": wear,
        "cancelled": token.cancelled,
    }
    merged["kpi"] = build_kpi(merged)
    return merged


__all__ = ["CancelToken", "run_tehl_case"]
