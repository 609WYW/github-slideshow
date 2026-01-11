from screener.filters.ma_filters import bullish, converge


def test_ma_converge():
    assert converge(10, 10.1, 10.2, close=10.5, converge_pct=0.05) is True


def test_ma_bullish():
    assert bullish(11, 10, 9, close=11.5) is True
