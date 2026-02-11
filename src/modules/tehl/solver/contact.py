from __future__ import annotations


def compute_contact_pressure(film_pressure: list[list[float]]) -> dict[str, list[list[float]]]:
    ny = len(film_pressure)
    nx = len(film_pressure[0]) if ny else 0
    contact = [[0.0 for _ in range(nx)] for _ in range(ny)]
    total = [[0.0 for _ in range(nx)] for _ in range(ny)]

    for j in range(ny):
        for i in range(nx):
            pf = film_pressure[j][i]
            pc = max(0.0, (pf - 7.5e6) * 0.42)
            pt = pf + pc
            contact[j][i] = pc
            total[j][i] = pt

    return {"p_contact": contact, "p_total": total}
