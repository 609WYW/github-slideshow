from __future__ import annotations

import pandas as pd

from screener.indicators.macd import cross_in_last_n


def compute_norm(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result["norm_dif"] = result["DIF"] / result["close"]
    result["norm_dea"] = result["DEA"] / result["close"]
    return result


def quarter_cross_ok(df: pd.DataFrame, last_n: int, zero_band_q: float) -> tuple[bool, dict[str, float | bool | None]]:
    if df.empty:
        return False, {"cross_in_last_n": False, "distance": None}
    dif = df["DIF"]
    dea = df["DEA"]
    cross_ok, distance = cross_in_last_n(dif, dea, last_n)
    latest = df.iloc[-1]
    norm_dif = latest["norm_dif"]
    norm_dea = latest["norm_dea"]
    zero_near = (abs(norm_dif) <= zero_band_q and abs(norm_dea) <= zero_band_q) or (
        norm_dif >= -zero_band_q and norm_dea >= -zero_band_q
    )
    return cross_ok and zero_near, {
        "cross_in_last_n": cross_ok,
        "distance": distance,
        "norm_dif": norm_dif,
        "norm_dea": norm_dea,
    }


def month_opening_ok(df: pd.DataFrame, min_opening_growth: float) -> tuple[bool, dict[str, float | bool]]:
    if len(df) < 2:
        return False, {"opening_flag": False, "opening_growth": 0.0}
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    dif = latest["DIF"]
    dea = latest["DEA"]
    opening_growth = (latest["HIST"] - prev["HIST"]) if "HIST" in df.columns else (dif - dea) - (prev["DIF"] - prev["DEA"])
    opening_flag = dif > 0 and dea > 0 and opening_growth > min_opening_growth
    return opening_flag, {"opening_flag": opening_flag, "opening_growth": float(opening_growth)}


def week_strength_ok(df: pd.DataFrame, zero_band_w: float) -> tuple[bool, dict[str, float]]:
    if df.empty:
        return False, {"norm_dif": 0.0, "norm_dea": 0.0}
    latest = df.iloc[-1]
    norm_dif = latest["norm_dif"]
    norm_dea = latest["norm_dea"]
    ok = norm_dif >= -zero_band_w and norm_dea >= -zero_band_w
    return ok, {"norm_dif": norm_dif, "norm_dea": norm_dea}


def daily_filter_ok(df: pd.DataFrame) -> bool:
    if df.empty:
        return False
    latest = df.iloc[-1]
    return (latest["DIF"] > latest["DEA"] and latest["HIST"] > 0) or (latest["close"] > latest.get("MA20", latest["close"]))
