from __future__ import annotations

from dataclasses import dataclass
from math import cos, pi, sin
from typing import Any

try:
    import numpy as np
except ModuleNotFoundError:  # pragma: no cover
    np = None


@dataclass(slots=True)
class SlipperTEHL:
    """Simplified Python port shell of MATLAB SlipperTEHL core flow for Stage 6/7."""

    params: dict[str, Any]

    def run(self) -> dict[str, Any]:
        nr = int(self.params.get("nr", 61))
        nth = int(self.params.get("nth", 121))

        ri = float(self.params.get("inner_radius_rin", 0.0035))
        ro = float(self.params.get("outer_radius_rout", 0.009))
        p_high = float(self.params.get("high_pressure_ph", 35e6))
        p_case = float(self.params.get("case_pressure_pc", 1e5))
        h0 = float(self.params.get("initial_film_thickness_h0", 5e-6))
        pressure_relax = float(self.params.get("pressure_relax", 0.8))

        if np is None:
            return self._run_pure_python(nr, nth, ri, ro, p_high, p_case, h0, pressure_relax)

        r = np.linspace(ri, ro, nr)
        th = np.linspace(0.0, 2.0 * np.pi, nth, endpoint=False)
        rr, tt = np.meshgrid(r, th, indexing="ij")

        r_norm = (rr - ri) / max(ro - ri, 1e-12)
        wedge = 1.0 + 0.25 * np.cos(tt - np.deg2rad(20.0))
        radial = 1.0 - 0.35 * r_norm
        p_film = p_case + (p_high - p_case) * np.clip(radial * wedge, 0.0, None)
        p_film *= max(min(pressure_relax, 1.0), 0.05)

        h_shape = h0 * (1.0 + 0.12 * np.sin(tt) + 0.08 * (r_norm - 0.5))
        h_contact = float(self.params.get("h_contact", 0.3)) * 1e-6
        deficit = np.maximum(h_contact - h_shape, 0.0)
        k_contact = float(self.params.get("k_contact", 8.0e14))
        p_contact = k_contact * deficit

        if bool(self.params.get("clamp_pressure", True)):
            p_contact = np.clip(p_contact, 0.0, p_high)
            p_film = np.clip(p_film, p_case, p_high)

        p_total = p_film + p_contact
        return {"r": r, "theta": th, "p_film": p_film, "p_contact": p_contact, "p_total": p_total}

    def _run_pure_python(
        self,
        nr: int,
        nth: int,
        ri: float,
        ro: float,
        p_high: float,
        p_case: float,
        h0: float,
        pressure_relax: float,
    ) -> dict[str, Any]:
        r = [ri + (ro - ri) * i / (nr - 1 or 1) for i in range(nr)]
        th = [2.0 * pi * j / nth for j in range(nth)]

        p_film: list[list[float]] = []
        p_contact: list[list[float]] = []
        p_total: list[list[float]] = []
        h_contact = float(self.params.get("h_contact", 0.3)) * 1e-6
        k_contact = float(self.params.get("k_contact", 8.0e14))

        relax = max(min(pressure_relax, 1.0), 0.05)
        for i, rv in enumerate(r):
            rn = (rv - ri) / max(ro - ri, 1e-12)
            row_f: list[float] = []
            row_c: list[float] = []
            row_t: list[float] = []
            for tv in th:
                wedge = 1.0 + 0.25 * cos(tv - (20.0 * pi / 180.0))
                radial = 1.0 - 0.35 * rn
                pf = p_case + (p_high - p_case) * max(radial * wedge, 0.0)
                pf *= relax
                h_shape = h0 * (1.0 + 0.12 * sin(tv) + 0.08 * (rn - 0.5))
                deficit = max(h_contact - h_shape, 0.0)
                pc = k_contact * deficit
                if bool(self.params.get("clamp_pressure", True)):
                    pc = max(0.0, min(pc, p_high))
                    pf = max(p_case, min(pf, p_high))
                pt = pf + pc
                row_f.append(pf)
                row_c.append(pc)
                row_t.append(pt)
            p_film.append(row_f)
            p_contact.append(row_c)
            p_total.append(row_t)

        return {"r": r, "theta": th, "p_film": p_film, "p_contact": p_contact, "p_total": p_total}
