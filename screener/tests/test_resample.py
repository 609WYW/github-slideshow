import pandas as pd

from screener.indicators.resample import resample_ohlcv


def test_resample_weekly():
    df = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=10, freq="D"),
            "open": range(10),
            "high": range(10),
            "low": range(10),
            "close": range(10),
            "volume": [1] * 10,
            "amount": [1] * 10,
        }
    )
    weekly = resample_ohlcv(df, "W-FRI")
    assert len(weekly) >= 1
    assert {"open", "high", "low", "close"}.issubset(weekly.columns)
