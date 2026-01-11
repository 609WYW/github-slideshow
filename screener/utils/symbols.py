from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StockSymbol:
    code: str
    name: str
    market: str


def normalize_symbol(code: str) -> str:
    return code.strip().upper()


def is_a_share(code: str) -> bool:
    upper = normalize_symbol(code)
    return upper.endswith(".SH") or upper.endswith(".SZ") or upper.endswith(".BJ")
