from __future__ import annotations

import pandas as pd


AGG_MAP = {
    "open": "first",
    "high": "max",
    "low": "min",
    "close": "last",
    "volume": "sum",
    "amount": "sum",
}


def resample_ohlcv(data: pd.DataFrame, rule: str) -> pd.DataFrame:
    if data.empty:
        return data
    frame = data.copy()
    frame = frame.set_index("date").sort_index()
    resampled = frame.resample(rule).agg(AGG_MAP).dropna(subset=["close"])
    resampled = resampled.reset_index()
    return resampled
