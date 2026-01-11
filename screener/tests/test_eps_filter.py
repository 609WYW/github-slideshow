import pandas as pd

from screener.filters.financial_filters import eps_filters, latest_quarter_eps


def test_eps_filter_requires_positive_growth():
    df = pd.DataFrame(
        {
            "report_date": pd.to_datetime(["2024-06-30", "2024-09-30"]),
            "eps": [-0.1, 0.2],
            "net_profit": [10, 20],
        }
    )
    eps_latest, eps_prev, _ = latest_quarter_eps(df)
    assert eps_filters(eps_latest, eps_prev) is True
