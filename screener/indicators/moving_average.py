from __future__ import annotations

import pandas as pd


def moving_averages(series: pd.Series, windows: list[int]) -> pd.DataFrame:
    data = {}
    for window in windows:
        data[f"MA{window}"] = series.rolling(window=window).mean()
    return pd.DataFrame(data)
