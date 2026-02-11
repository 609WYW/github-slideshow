from __future__ import annotations


def estimate_wear(total_pressure: list[list[float]], duration_h: float) -> list[list[float]]:
    ny = len(total_pressure)
    nx = len(total_pressure[0]) if ny else 0
    wear = [[0.0 for _ in range(nx)] for _ in range(ny)]
    scale = max(1.0, duration_h) * 1e-12

    for j in range(ny):
        for i in range(nx):
            wear[j][i] = total_pressure[j][i] * scale
    return wear
