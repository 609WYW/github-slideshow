from __future__ import annotations

import pandas as pd

from screener.app.config import MovingAverageConfig


def moving_average_filter(close: pd.Series, ma_df: pd.DataFrame, config: MovingAverageConfig) -> dict:
    if not config.enabled:
        return {"pass": True, "reason": "disabled"}
    last_close = close.iloc[-1]
    pass_price = True
    for window in config.price_above:
        key = f"MA{window}"
        if key in ma_df.columns and pd.notna(ma_df[key].iloc[-1]):
            pass_price = pass_price and last_close > ma_df[key].iloc[-1]
    pass_order = True
    if len(config.ma_order) >= 2:
        for left, right in zip(config.ma_order, config.ma_order[1:]):
            left_key = f"MA{left}"
            right_key = f"MA{right}"
            if left_key in ma_df.columns and right_key in ma_df.columns:
                pass_order = pass_order and ma_df[left_key].iloc[-1] > ma_df[right_key].iloc[-1]
    return {
        "pass": pass_price and pass_order,
        "last_close": float(last_close),
        **{k: float(v.iloc[-1]) for k, v in ma_df.items()},
    }
