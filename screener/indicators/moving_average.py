from __future__ import annotations

import pandas as pd


def sma(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window=window, min_periods=window).mean()


def add_mas(df: pd.DataFrame, windows: list[int], price_col: str = "close") -> pd.DataFrame:
    result = df.copy()
    for window in windows:
        result[f"MA{window}"] = sma(result[price_col], window)
    return result
