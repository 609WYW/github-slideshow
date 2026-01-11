from __future__ import annotations


def within_market_cap(value: float | None, max_cny: float) -> bool:
    if value is None:
        return False
    return value < max_cny
