from __future__ import annotations

import math


def solve_thermal(
    total_pressure: list[list[float]],
    inlet_temp_c: float,
    speed_rpm: float,
) -> dict[str, list[list[float]] | dict[str, list[float]]]:
    ny = len(total_pressure)
    nx = len(total_pressure[0]) if ny else 0
    t0 = inlet_temp_c if inlet_temp_c != 0 else 60.0
    temp = [[0.0 for _ in range(nx)] for _ in range(ny)]
    heat_flux = [[0.0 for _ in range(nx)] for _ in range(ny)]

    for j in range(ny):
        for i in range(nx):
            p = total_pressure[j][i]
            t = t0 + 18.0 * (p / 1.0e7) + 0.002 * speed_rpm
            q = 0.12 * p / 1.0e6
            temp[j][i] = t
            heat_flux[j][i] = q

    xs = [20 + k * 5 for k in range(15)]
    ys = [0.11 * math.exp(-0.028 * (x - 20)) for x in xs]
    return {"thermal": temp, "heat_flux": heat_flux, "viscosity_temp": {"x": xs, "y": ys}}
