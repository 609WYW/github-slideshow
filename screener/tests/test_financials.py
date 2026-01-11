import pandas as pd

from screener.app.config import FinancialConfig
from screener.filters.financial_filters import latest_quarter_eps


def test_eps_growth_positive():
    data = pd.DataFrame(
        {
            "report_date": pd.to_datetime(["2024-06-30", "2024-03-31"]),
            "基本每股收益(元)": [0.5, 0.2],
            "归属于母公司股东的净利润(元)": [10.0, 5.0],
        }
    )
    result = latest_quarter_eps(data, FinancialConfig())
    assert result["pass"] is True
    assert result["eps_latest"] == 0.5


def test_eps_growth_fail():
    data = pd.DataFrame(
        {
            "report_date": pd.to_datetime(["2024-06-30", "2024-03-31"]),
            "基本每股收益(元)": [0.1, 0.2],
        }
    )
    result = latest_quarter_eps(data, FinancialConfig())
    assert result["pass"] is False
