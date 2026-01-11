from __future__ import annotations

import pandas as pd

from screener.app.config import FinancialConfig


def _first_existing(columns: list[str], candidates: list[str]) -> str | None:
    for name in candidates:
        if name in columns:
            return name
    return None


def latest_quarter_eps(financials: pd.DataFrame, config: FinancialConfig) -> dict:
    if financials.empty:
        return {"pass": False, "reason": "no_financials"}
    frame = financials.copy()
    frame = frame.sort_values("report_date", ascending=False)
    eps_col = _first_existing(frame.columns.tolist(), config.eps_field_candidates + ["EPS", "eps"])
    profit_col = _first_existing(frame.columns.tolist(), config.net_profit_field_candidates + ["net_profit"])
    if eps_col is None:
        return {"pass": False, "reason": "no_eps"}
    latest = frame.iloc[0]
    prev = frame.iloc[1] if len(frame) > 1 else None
    eps_latest = pd.to_numeric(latest[eps_col], errors="coerce")
    eps_prev = pd.to_numeric(prev[eps_col], errors="coerce") if prev is not None else None
    if pd.isna(eps_latest) or eps_prev is None or pd.isna(eps_prev):
        return {"pass": False, "reason": "eps_missing"}
    pass_eps = eps_latest > eps_prev and eps_latest > 0
    net_profit_latest = None
    if profit_col is not None:
        net_profit_latest = pd.to_numeric(latest[profit_col], errors="coerce")
        if config.require_net_profit_positive and pd.notna(net_profit_latest):
            pass_eps = pass_eps and net_profit_latest > 0
    return {
        "pass": pass_eps,
        "eps_latest": float(eps_latest),
        "eps_prev": float(eps_prev),
        "net_profit_latest": float(net_profit_latest) if net_profit_latest is not None and pd.notna(net_profit_latest) else None,
        "reason": "ok" if pass_eps else "eps_or_profit_failed",
    }
