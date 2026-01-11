from __future__ import annotations

import pandas as pd


def resample_ohlcv(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.sort_values("date").set_index("date")
    agg = {
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
        "amount": "sum",
    }
    resampled = df.resample(rule).agg(agg).dropna(subset=["open", "close"])
    resampled = resampled.reset_index()
    return resampled
