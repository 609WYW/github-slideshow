import pandas as pd

from screener.indicators.macd import cross_in_last_n


def test_cross_in_last_n_detects_recent_cross():
    dif = pd.Series([0.1, 0.2, 0.5])
    dea = pd.Series([0.2, 0.2, 0.3])
    ok, distance = cross_in_last_n(dif, dea, last_n=2)
    assert ok is True
    assert distance == 0
