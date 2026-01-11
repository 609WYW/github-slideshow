import pandas as pd

from screener.indicators.resample import resample_ohlcv


def test_resample_weekly():
    dates = pd.date_range("2024-01-01", periods=10, freq="D")
    data = pd.DataFrame(
        {
            "date": dates,
            "open": range(10),
            "high": range(1, 11),
            "low": range(10),
            "close": range(10),
            "volume": range(10),
            "amount": range(10),
        }
    )
    weekly = resample_ohlcv(data, "W-FRI")
    assert not weekly.empty
    assert "close" in weekly.columns
