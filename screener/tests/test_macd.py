import pandas as pd

from screener.indicators.macd import detect_cross, macd


def test_detect_cross_recent():
    series = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    macd_df = macd(series)
    crossed, bars_ago = detect_cross(macd_df, lookback=5)
    assert crossed is True
    assert bars_ago is not None


def test_detect_cross_none():
    series = pd.Series([10, 9, 8, 7, 6, 5, 4, 3, 2, 1])
    macd_df = macd(series)
    crossed, bars_ago = detect_cross(macd_df, lookback=2)
    assert crossed is False
    assert bars_ago is None
