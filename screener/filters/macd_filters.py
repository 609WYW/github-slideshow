from __future__ import annotations

import pandas as pd

from screener.app.config import MacdFilterConfig, ZeroBandConfig
from screener.indicators.macd import detect_cross


def normalize_macd(macd_df: pd.DataFrame, close: pd.Series) -> pd.DataFrame:
    data = macd_df.copy()
    data["norm_dif"] = data["DIF"] / close
    data["norm_dea"] = data["DEA"] / close
    return data


def quarter_filter(macd_df: pd.DataFrame, close: pd.Series, zero_band: ZeroBandConfig, settings: MacdFilterConfig) -> dict:
    normalized = normalize_macd(macd_df, close)
    last_row = normalized.iloc[-1]
    cross, bars_ago = detect_cross(macd_df, lookback=settings.last_n_q_bars)
    condition = (
        last_row["norm_dif"] >= -zero_band.quarter
        and last_row["norm_dea"] >= -zero_band.quarter
        and cross
    )
    return {
        "pass": condition,
        "norm_dif": last_row["norm_dif"],
        "norm_dea": last_row["norm_dea"],
        "cross": cross,
        "cross_bars_ago": bars_ago,
        "DIF": last_row["DIF"],
        "DEA": last_row["DEA"],
        "HIST": last_row["HIST"],
    }


def month_filter(macd_df: pd.DataFrame, close: pd.Series, zero_band: ZeroBandConfig) -> dict:
    normalized = normalize_macd(macd_df, close)
    last_row = normalized.iloc[-1]
    prev_row = normalized.iloc[-2] if len(normalized) > 1 else last_row
    hist_expand = last_row["HIST"] > prev_row["HIST"]
    condition = (
        last_row["norm_dif"] > 0
        and last_row["norm_dea"] > 0
        and last_row["HIST"] > 0
        and hist_expand
    )
    return {
        "pass": condition,
        "norm_dif": last_row["norm_dif"],
        "norm_dea": last_row["norm_dea"],
        "opening": hist_expand,
        "DIF": last_row["DIF"],
        "DEA": last_row["DEA"],
        "HIST": last_row["HIST"],
    }


def week_filter(macd_df: pd.DataFrame, close: pd.Series, zero_band: ZeroBandConfig) -> dict:
    normalized = normalize_macd(macd_df, close)
    last_row = normalized.iloc[-1]
    condition = (
        last_row["norm_dif"] >= -zero_band.week and last_row["norm_dea"] >= -zero_band.week
    )
    return {
        "pass": condition,
        "norm_dif": last_row["norm_dif"],
        "norm_dea": last_row["norm_dea"],
        "DIF": last_row["DIF"],
        "DEA": last_row["DEA"],
        "HIST": last_row["HIST"],
    }


def daily_filter(macd_df: pd.DataFrame, close: pd.Series, zero_band: ZeroBandConfig, settings: MacdFilterConfig) -> dict:
    normalized = normalize_macd(macd_df, close)
    last_row = normalized.iloc[-1]
    condition = True
    if settings.daily_rule == "dif_gt_dea_and_hist_gt_0":
        condition = last_row["DIF"] > last_row["DEA"] and last_row["HIST"] > 0
    return {
        "pass": condition,
        "norm_dif": last_row["norm_dif"],
        "norm_dea": last_row["norm_dea"],
        "DIF": last_row["DIF"],
        "DEA": last_row["DEA"],
        "HIST": last_row["HIST"],
    }
