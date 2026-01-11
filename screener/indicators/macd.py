from __future__ import annotations

import pandas as pd


def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def macd(df: pd.DataFrame, price_col: str = "close", fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    prices = df[price_col]
    dif = ema(prices, fast) - ema(prices, slow)
    dea = ema(dif, signal)
    hist = dif - dea
    result = df.copy()
    result["DIF"] = dif
    result["DEA"] = dea
    result["HIST"] = hist
    return result


def cross_in_last_n(dif: pd.Series, dea: pd.Series, last_n: int) -> tuple[bool, int | None]:
    if len(dif) < 2:
        return False, None
    cross_indices = []
    for idx in range(1, len(dif)):
        if dif.iloc[idx - 1] <= dea.iloc[idx - 1] and dif.iloc[idx] > dea.iloc[idx]:
            cross_indices.append(idx)
    if not cross_indices:
        return False, None
    last_idx = cross_indices[-1]
    distance = len(dif) - 1 - last_idx
    return distance <= last_n - 1, distance
