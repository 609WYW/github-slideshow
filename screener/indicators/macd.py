from __future__ import annotations

import pandas as pd


def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    dif = ema_fast - ema_slow
    dea = dif.ewm(span=signal, adjust=False).mean()
    hist = dif - dea
    return pd.DataFrame({"DIF": dif, "DEA": dea, "HIST": hist})


def detect_cross(macd_df: pd.DataFrame, lookback: int = 2) -> tuple[bool, int | None]:
    if macd_df.empty or len(macd_df) < 2:
        return False, None
    dif = macd_df["DIF"]
    dea = macd_df["DEA"]
    cross_points = (dif.shift(1) <= dea.shift(1)) & (dif > dea)
    recent_index = cross_points.tail(lookback)
    if recent_index.any():
        last_pos = recent_index[recent_index].index[-1]
        bars_ago = len(macd_df) - 1 - macd_df.index.get_loc(last_pos)
        return True, bars_ago
    return False, None
