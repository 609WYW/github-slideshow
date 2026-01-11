from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
from tqdm import tqdm

from screener.app.config import Config
from screener.data.akshare_provider import AkshareProvider
from screener.data.cache import CacheManager
from screener.data.providers import SymbolInfo
from screener.data.tushare_provider import TushareProvider
from screener.filters.financial_filters import eps_filters, latest_quarter_eps
from screener.filters.ma_filters import bullish, converge
from screener.filters.macd_filters import (
    compute_norm,
    daily_filter_ok,
    month_opening_ok,
    quarter_cross_ok,
    week_strength_ok,
)
from screener.filters.market_cap_filters import within_market_cap
from screener.filters.score import compute_score
from screener.filters.st_filters import check_st
from screener.indicators.macd import macd
from screener.indicators.moving_average import add_mas
from screener.indicators.resample import resample_ohlcv
from screener.utils.symbols import is_a_share_market

LOGGER = logging.getLogger(__name__)


def run_screen(config: Config) -> None:
    provider = _select_provider(config)
    cache = CacheManager(Path(config.app.cache_dir))

    symbols = [symbol for symbol in provider.get_symbols() if is_a_share_market(symbol.market)]
    if config.app.limit:
        symbols = symbols[: config.app.limit]

    results: list[dict[str, Any]] = []

    with ThreadPoolExecutor(max_workers=config.app.max_workers) as executor:
        futures = {
            executor.submit(process_symbol, symbol, provider, config, cache): symbol.code for symbol in symbols
        }
        for future in tqdm(as_completed(futures), total=len(futures), desc="Screening"):
            try:
                payload = future.result()
            except Exception as exc:  # noqa: BLE001
                LOGGER.warning("Failed processing %s: %s", futures[future], exc)
                continue
            if payload is None:
                continue
            results.append(payload)

    if not results:
        LOGGER.warning("No results matched the filters.")
        return

    df = pd.DataFrame(results)
    df = df.sort_values("score", ascending=False)

    output_dir = Path(config.app.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if "csv" in config.app.export:
        df.to_csv(output_dir / f"screen_result_{stamp}.csv", index=False)
    if "xlsx" in config.app.export:
        df.to_excel(output_dir / f"screen_result_{stamp}.xlsx", index=False)
    if "html" in config.app.export:
        df.to_html(output_dir / f"screen_result_{stamp}.html", index=False)

    LOGGER.info("Saved %d results to %s", len(df), output_dir)


def _select_provider(config: Config):
    if config.provider.name.lower() == "tushare" and config.provider.tushare_token:
        return TushareProvider(config.provider.tushare_token)
    return AkshareProvider()


def process_symbol(
    symbol: SymbolInfo, provider: Any, config: Config, cache: CacheManager
) -> dict[str, Any] | None:
    st_result = check_st(symbol.name, [], config.filters.st_keywords)
    if st_result.is_filtered:
        return None

    daily = _load_cached(cache, provider, symbol.code, "daily", config.app.use_cache)
    if daily is None or daily.empty or len(daily) < 250:
        LOGGER.info("Insufficient daily data for %s", symbol.code)
        return None

    daily = daily.sort_values("date")
    daily = add_mas(daily, config.filters.ma["windows"])

    week = resample_ohlcv(daily, "W-FRI")
    month = resample_ohlcv(daily, "M")
    quarter = resample_ohlcv(daily, "Q")

    quarter_macd = compute_norm(macd(quarter))
    month_macd = macd(month)
    week_macd = compute_norm(macd(week))

    quarter_ok, quarter_meta = quarter_cross_ok(
        quarter_macd, config.filters.macd["last_n_quarter"], config.filters.macd["zero_band_q"]
    )
    month_ok, month_meta = month_opening_ok(month_macd, config.filters.macd["min_opening_growth"])
    week_ok, week_meta = week_strength_ok(week_macd, config.filters.macd["zero_band_w"])

    if not (quarter_ok and month_ok and week_ok):
        return None

    if config.filters.macd["enable_daily_filter"]:
        daily_macd = macd(daily)
        if not daily_filter_ok(daily_macd):
            return None

    ma5 = float(daily.iloc[-1]["MA5"])
    ma10 = float(daily.iloc[-1]["MA10"])
    ma20 = float(daily.iloc[-1]["MA20"])
    close = float(daily.iloc[-1]["close"])

    ma_converge = converge(ma5, ma10, ma20, close, config.filters.ma["converge_pct"])
    ma_bullish = bullish(ma5, ma10, ma20, close)
    if config.filters.ma["enable_converge"] and config.filters.ma["enable_bullish"]:
        ma_ok = ma_converge or ma_bullish
    elif config.filters.ma["enable_converge"]:
        ma_ok = ma_converge
    elif config.filters.ma["enable_bullish"]:
        ma_ok = ma_bullish
    else:
        ma_ok = True

    if not ma_ok:
        return None

    market_cap_value = symbol.total_market_cap
    if config.filters.market_cap["field"] == "float_market_cap":
        market_cap_value = symbol.float_market_cap

    if config.filters.market_cap.get("enabled", True):
        if not within_market_cap(market_cap_value, config.filters.market_cap["max_cny"]):
            return None

    financials = _load_cached(cache, provider, symbol.code, "financials", config.app.use_cache)
    if financials is None or financials.empty:
        LOGGER.info("Missing financials for %s", symbol.code)
        return None

    eps_latest, eps_prev, net_profit_latest = latest_quarter_eps(financials)
    if not eps_filters(eps_latest, eps_prev):
        return None
    if config.filters.financial.get("require_net_profit_positive", True) and net_profit_latest is not None:
        if net_profit_latest <= 0:
            return None

    score_data = {
        "quarter_cross_distance": quarter_meta.get("distance"),
        "month_opening_growth": month_meta.get("opening_growth", 0.0),
        "week_norm_dif": week_meta.get("norm_dif", 0.0),
        "week_norm_dea": week_meta.get("norm_dea", 0.0),
        "ma_bullish": ma_bullish,
        "ma_converge": ma_converge,
    }

    score = compute_score(score_data, config.scoring.weights)

    return {
        "code": symbol.code,
        "name": symbol.name,
        "market": symbol.market,
        "is_st_filtered": False,
        "total_market_cap": market_cap_value,
        "quarter_dif": quarter_macd.iloc[-1]["DIF"],
        "quarter_dea": quarter_macd.iloc[-1]["DEA"],
        "quarter_hist": quarter_macd.iloc[-1]["HIST"],
        "quarter_norm_dif": quarter_meta.get("norm_dif"),
        "quarter_norm_dea": quarter_meta.get("norm_dea"),
        "cross_in_last_n": quarter_meta.get("cross_in_last_n"),
        "month_dif": month_macd.iloc[-1]["DIF"],
        "month_dea": month_macd.iloc[-1]["DEA"],
        "month_hist": month_macd.iloc[-1]["HIST"],
        "month_opening_flag": month_meta.get("opening_flag"),
        "month_opening_growth": month_meta.get("opening_growth"),
        "week_norm_dif": week_meta.get("norm_dif"),
        "week_norm_dea": week_meta.get("norm_dea"),
        "eps_latest": eps_latest,
        "eps_prev": eps_prev,
        "eps_qoq_delta": (eps_latest - eps_prev) if eps_latest is not None and eps_prev is not None else None,
        "net_profit_latest": net_profit_latest,
        "MA5": ma5,
        "MA10": ma10,
        "MA20": ma20,
        "ma_mode_matched": "bullish" if ma_bullish else "converge" if ma_converge else "none",
        "score": score,
    }


def _load_cached(cache: CacheManager, provider: Any, code: str, key: str, use_cache: bool) -> pd.DataFrame | None:
    cache_key = f"{key}_{code}"
    if use_cache:
        cached = cache.load(cache_key)
        if cached is not None:
            if "date" in cached.columns:
                cached["date"] = pd.to_datetime(cached["date"])
            if "report_date" in cached.columns:
                cached["report_date"] = pd.to_datetime(cached["report_date"])
            return cached
    try:
        if key == "daily":
            df = provider.get_daily(code)
        else:
            df = provider.get_financials(code)
    except Exception as exc:  # noqa: BLE001
        LOGGER.warning("Fetch failed for %s %s: %s", key, code, exc)
        return None
    if df is not None and not df.empty:
        cache.save(cache_key, df)
    return df
