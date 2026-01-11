from __future__ import annotations

import argparse
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from screener.app.config import AppConfig, load_config
from screener.data import AkshareProvider, TushareProvider
from screener.data.cache import CacheManager
from screener.filters import (
    daily_filter,
    latest_quarter_eps,
    month_filter,
    moving_average_filter,
    quarter_filter,
    score_signal,
    week_filter,
)
from screener.indicators.macd import macd
from screener.indicators.moving_average import moving_averages
from screener.indicators.resample import resample_ohlcv
from screener.utils.logging import setup_logging

LOGGER = logging.getLogger(__name__)


def _select_provider(config: AppConfig):
    if config.data.provider == "tushare" and config.data.tushare_token:
        return TushareProvider(config.data.tushare_token)
    if config.data.provider == "auto" and config.data.tushare_token:
        return TushareProvider(config.data.tushare_token)
    return AkshareProvider()


def _export_results(df: pd.DataFrame, config: AppConfig) -> None:
    output_dir = Path(config.output.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if "csv" in config.output.export:
        df.to_csv(output_dir / "screener_results.csv", index=False)
    if "xlsx" in config.output.export:
        df.to_excel(output_dir / "screener_results.xlsx", index=False)
    if config.output.html_report:
        html = df.to_html(index=False)
        (output_dir / "screener_results.html").write_text(html, encoding="utf-8")


def _load_cached(cache: CacheManager, key: str, use_cache: bool) -> pd.DataFrame | None:
    if not use_cache:
        return None
    return cache.read(key)


def _store_cached(cache: CacheManager, key: str, data: pd.DataFrame, use_cache: bool) -> None:
    if use_cache:
        cache.write(key, data)


def _process_symbol(
    symbol_row: pd.Series,
    config: AppConfig,
    provider,
    cache: CacheManager,
    market_caps: dict,
) -> dict | None:
    symbol = symbol_row["code"]
    name = symbol_row["name"]
    market = symbol_row["market"]

    daily_key = f"daily_{symbol}"
    daily_data = _load_cached(cache, daily_key, config.data.use_cache)
    if daily_data is None:
        daily_data = provider.daily_history(symbol)
        _store_cached(cache, daily_key, daily_data, config.data.use_cache)
    if daily_data is None or daily_data.empty:
        return None

    daily_data = daily_data.sort_values("date")
    weekly = resample_ohlcv(daily_data, "W-FRI")
    monthly = resample_ohlcv(daily_data, "M")
    quarterly = resample_ohlcv(daily_data, "Q")

    if len(quarterly) < 3 or len(monthly) < 3 or len(weekly) < 3:
        return None

    quarter_macd = macd(quarterly["close"], config.macd.fast, config.macd.slow, config.macd.signal)
    month_macd = macd(monthly["close"], config.macd.fast, config.macd.slow, config.macd.signal)
    week_macd = macd(weekly["close"], config.macd.fast, config.macd.slow, config.macd.signal)
    daily_macd = macd(daily_data["close"], config.macd.fast, config.macd.slow, config.macd.signal)

    quarter_result = quarter_filter(quarter_macd, quarterly["close"], config.zero_band, config.macd_filters)
    if not quarter_result["pass"]:
        return None
    month_result = month_filter(month_macd, monthly["close"], config.zero_band)
    if not month_result["pass"]:
        return None
    week_result = week_filter(week_macd, weekly["close"], config.zero_band)
    if not week_result["pass"]:
        return None
    if config.macd_filters.enable_daily_filter:
        daily_result = daily_filter(daily_macd, daily_data["close"], config.zero_band, config.macd_filters)
        if not daily_result["pass"]:
            return None
    else:
        daily_result = daily_filter(daily_macd, daily_data["close"], config.zero_band, config.macd_filters)

    ma_windows = sorted(set(config.moving_average.price_above + config.moving_average.ma_order))
    ma_data = moving_averages(daily_data["close"], ma_windows)
    ma_result = moving_average_filter(daily_data["close"], ma_data, config.moving_average)
    if not ma_result["pass"]:
        return None

    cap_value = market_caps.get(symbol)
    if cap_value is None or cap_value >= config.market_cap.max_total_market_cap:
        return None

    fin_key = f"fin_{symbol}"
    fin_data = _load_cached(cache, fin_key, config.data.use_cache)
    if fin_data is None:
        fin_data = provider.quarterly_financials(symbol)
        _store_cached(cache, fin_key, fin_data, config.data.use_cache)
    fin_result = latest_quarter_eps(fin_data, config.financial)
    if not fin_result.get("pass"):
        return None

    score = score_signal(quarter_result, month_result, week_result, ma_result, config.score_weights)

    return {
        "code": symbol,
        "name": name,
        "market": market,
        "total_market_cap": cap_value,
        "quarter_DIF": quarter_result["DIF"],
        "quarter_DEA": quarter_result["DEA"],
        "quarter_HIST": quarter_result["HIST"],
        "quarter_norm_dif": quarter_result["norm_dif"],
        "quarter_norm_dea": quarter_result["norm_dea"],
        "quarter_cross": quarter_result["cross"],
        "quarter_cross_bars_ago": quarter_result["cross_bars_ago"],
        "month_DIF": month_result["DIF"],
        "month_DEA": month_result["DEA"],
        "month_HIST": month_result["HIST"],
        "month_norm_dif": month_result["norm_dif"],
        "month_norm_dea": month_result["norm_dea"],
        "month_opening": month_result["opening"],
        "week_DIF": week_result["DIF"],
        "week_DEA": week_result["DEA"],
        "week_HIST": week_result["HIST"],
        "week_norm_dif": week_result["norm_dif"],
        "week_norm_dea": week_result["norm_dea"],
        "daily_DIF": daily_result["DIF"],
        "daily_DEA": daily_result["DEA"],
        "daily_HIST": daily_result["HIST"],
        "eps_latest": fin_result.get("eps_latest"),
        "eps_prev": fin_result.get("eps_prev"),
        "net_profit_latest": fin_result.get("net_profit_latest"),
        "score": score,
        **ma_result,
    }


def run(config: AppConfig) -> pd.DataFrame:
    setup_logging(config.log_level)
    provider = _select_provider(config)
    cache = CacheManager(Path(config.data.cache_dir))

    LOGGER.info("Loading stock universe...")
    universe = provider.list_stocks(config.data.markets)
    if universe.empty:
        raise RuntimeError("No stocks returned from provider")

    LOGGER.info("Loading market caps...")
    market_caps_df = provider.market_caps()
    market_caps = {}
    if not market_caps_df.empty:
        cap_field = config.market_cap.field
        if cap_field not in market_caps_df.columns:
            cap_field = "total_market_cap"
        market_caps = market_caps_df.set_index("code")[cap_field].dropna().to_dict()

    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
        futures = [
            executor.submit(_process_symbol, row, config, provider, cache, market_caps)
            for _, row in universe.iterrows()
        ]
        for future in tqdm(as_completed(futures), total=len(futures)):
            try:
                result = future.result()
            except Exception as exc:  # noqa: BLE001
                LOGGER.error("Processing failed: %s", exc)
                continue
            if result:
                results.append(result)

    if not results:
        return pd.DataFrame()

    df = pd.DataFrame(results).sort_values("score", ascending=False)
    _export_results(df, config)
    return df


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="A-share stock screener")
    parser.add_argument("run", nargs="?", default="run")
    parser.add_argument("--config", required=True, help="Path to config yaml")
    parser.add_argument("--max-workers", type=int)
    parser.add_argument("--use-cache", type=str)
    parser.add_argument("--export", type=str)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    config = load_config(args.config)
    if args.max_workers is not None:
        config.max_workers = args.max_workers
    if args.use_cache is not None:
        config.data.use_cache = args.use_cache.lower() == "true"
    if args.export is not None:
        config.output.export = [item.strip() for item in args.export.split(",") if item.strip()]
    run(config)


if __name__ == "__main__":
    main()
