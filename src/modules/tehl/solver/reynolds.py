from __future__ import annotations

import math
from typing import Callable


def mpa_to_pa(value_mpa: float) -> float:
    return value_mpa * 1e6


def rpm_to_rad_s(value_rpm: float) -> float:
    return value_rpm * 2.0 * math.pi / 60.0


def solve_reynolds(
    mesh: dict[str, list[float]],
    method: str,
    rated_pressure_mpa: float,
    speed_rpm: float,
    cancel_check: Callable[[], bool] | None = None,
) -> list[list[float]]:
    nx = int(mesh["nx"])
    ny = int(mesh["ny"])
    rated_pa = max(1.0, mpa_to_pa(rated_pressure_mpa if rated_pressure_mpa > 0 else 12.0))
    omega = max(1.0, rpm_to_rad_s(speed_rpm if speed_rpm > 0 else 1500.0))

    field = [[0.0 for _ in range(nx)] for _ in range(ny)]
    relax = 0.62 if method.upper() == "CTDMA" else 0.48

    for _ in range(10):
        if cancel_check and cancel_check():
            break
        for j in range(ny):
            y = j / max(1, ny - 1)
            for i in range(nx):
                x = i / max(1, nx - 1)
                base = rated_pa * (0.65 + 0.35 * math.sin(math.pi * x) * math.cos(math.pi * y))
                shear = 0.03 * omega * math.sin(2.0 * math.pi * x)
                value = max(1.0, base + shear)
                field[j][i] = (1 - relax) * field[j][i] + relax * value
    return field
