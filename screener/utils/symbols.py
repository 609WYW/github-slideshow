from __future__ import annotations


def is_a_share_market(market: str) -> bool:
    return market in {"SH", "SZ", "BJ"}
