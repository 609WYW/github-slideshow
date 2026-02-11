from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class MeshConfig:
    nx: int = 48
    ny: int = 36
    length_mm: float = 12.0
    width_mm: float = 10.0


def mm_to_m(value_mm: float) -> float:
    return value_mm * 1e-3


def build_mesh(config: MeshConfig) -> dict[str, list[float]]:
    nx = max(8, int(config.nx))
    ny = max(8, int(config.ny))
    lx = mm_to_m(config.length_mm)
    ly = mm_to_m(config.width_mm)
    xs = [i * lx / (nx - 1) for i in range(nx)]
    ys = [j * ly / (ny - 1) for j in range(ny)]
    return {"x": xs, "y": ys, "nx": nx, "ny": ny, "lx": lx, "ly": ly}
