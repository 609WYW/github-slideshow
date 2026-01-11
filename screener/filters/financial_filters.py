from __future__ import annotations

import pandas as pd


def latest_quarter_eps(financials: pd.DataFrame) -> tuple[float | None, float | None, float | None]:
    if financials.empty:
        return None, None, None
    df = financials.dropna(subset=["report_date"]).sort_values("report_date")
    if df.empty:
        return None, None, None
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) >= 2 else None
    eps_latest = latest.get("eps")
    eps_prev = prev.get("eps") if prev is not None else None
    return eps_latest, eps_prev, latest.get("net_profit")


def eps_filters(eps_latest: float | None, eps_prev: float | None) -> bool:
    if eps_latest is None:
        return False
    if eps_prev is None:
        return False
    return eps_latest > 0 and eps_latest > eps_prev
