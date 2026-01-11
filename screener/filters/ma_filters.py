from __future__ import annotations


def converge(ma5: float, ma10: float, ma20: float, close: float, converge_pct: float) -> bool:
    max_ma = max(ma5, ma10, ma20)
    min_ma = min(ma5, ma10, ma20)
    return (max_ma - min_ma) <= converge_pct * close


def bullish(ma5: float, ma10: float, ma20: float, close: float) -> bool:
    return ma5 > ma10 > ma20 and close > ma20
