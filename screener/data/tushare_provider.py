from __future__ import annotations

import logging
from typing import Any

import pandas as pd
import tushare as ts

from screener.data.providers import DataProvider, SymbolInfo

LOGGER = logging.getLogger(__name__)


class TushareProvider(DataProvider):
    def __init__(self, token: str) -> None:
        self._token = token
        ts.set_token(token)
        self._pro = ts.pro_api()

    def get_symbols(self) -> list[SymbolInfo]:
        df = self._pro.stock_basic(exchange="", list_status="L", fields="ts_code,symbol,name,market")
        market_cap = self._pro.daily_basic(ts_code="", fields="ts_code,total_mv,float_mv")
        merged = df.merge(market_cap, on="ts_code", how="left")
        symbols: list[SymbolInfo] = []
        for _, row in merged.iterrows():
            ts_code = str(row.get("ts_code", ""))
            code = str(row.get("symbol", "")).zfill(6)
            market = self._map_market(ts_code)
            total_mc = self._to_cny(row.get("total_mv"))
            float_mc = self._to_cny(row.get("float_mv"))
            name = str(row.get("name", ""))
            symbols.append(SymbolInfo(code=code, name=name, market=market, total_market_cap=total_mc, float_market_cap=float_mc))
        return symbols

    def get_daily(self, code: str) -> pd.DataFrame:
        ts_code = self._to_ts_code(code)
        df = self._pro.daily(ts_code=ts_code, start_date="20170101")
        if df.empty:
            return df
        df = df.rename(columns={"trade_date": "date"})
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
        return df[["date", "open", "high", "low", "close", "vol", "amount"]].rename(columns={"vol": "volume"})

    def get_financials(self, code: str) -> pd.DataFrame:
        ts_code = self._to_ts_code(code)
        try:
            df = self._pro.fina_indicator(ts_code=ts_code, fields="ts_code,end_date,eps,netprofit_yoy,netprofit")
        except Exception as exc:  # noqa: BLE001
            LOGGER.warning("Failed to load financials for %s: %s", code, exc)
            return pd.DataFrame()
        if df.empty:
            return df
        df = df.rename(columns={"end_date": "report_date", "netprofit": "net_profit"})
        df["report_date"] = pd.to_datetime(df["report_date"])
        return df[["report_date", "eps", "net_profit"]]

    def _map_market(self, ts_code: str) -> str:
        if ts_code.endswith(".SH"):
            return "SH"
        if ts_code.endswith(".BJ"):
            return "BJ"
        return "SZ"

    def _to_ts_code(self, code: str) -> str:
        if code.startswith("6"):
            return f"{code}.SH"
        if code.startswith("8") or code.startswith("4"):
            return f"{code}.BJ"
        return f"{code}.SZ"

    def _to_cny(self, value: Any) -> float | None:
        try:
            if value is None:
                return None
            return float(value) * 1e6
        except (TypeError, ValueError):
            return None
