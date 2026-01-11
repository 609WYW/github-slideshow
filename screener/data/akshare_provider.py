from __future__ import annotations

import logging
from typing import Any

import akshare as ak
import pandas as pd

from screener.data.providers import DataProvider, SymbolInfo

LOGGER = logging.getLogger(__name__)


class AkshareProvider(DataProvider):
    def __init__(self) -> None:
        self._spot_cache: pd.DataFrame | None = None

    def get_symbols(self) -> list[SymbolInfo]:
        if self._spot_cache is None:
            self._spot_cache = ak.stock_zh_a_spot_em()
        df = self._spot_cache
        symbols: list[SymbolInfo] = []
        for _, row in df.iterrows():
            code = str(row.get("代码", "")).zfill(6)
            name = str(row.get("名称", ""))
            market = self._infer_market(code)
            total_mc = self._to_cny(row.get("总市值"))
            float_mc = self._to_cny(row.get("流通市值"))
            symbols.append(SymbolInfo(code=code, name=name, market=market, total_market_cap=total_mc, float_market_cap=float_mc))
        return symbols

    def get_daily(self, code: str) -> pd.DataFrame:
        df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date="20170101", adjust="")
        mapping = {
            "日期": "date",
            "开盘": "open",
            "收盘": "close",
            "最高": "high",
            "最低": "low",
            "成交量": "volume",
            "成交额": "amount",
        }
        df = df.rename(columns=mapping)
        df["date"] = pd.to_datetime(df["date"])
        return df[["date", "open", "high", "low", "close", "volume", "amount"]]

    def get_financials(self, code: str) -> pd.DataFrame:
        try:
            df = ak.stock_financial_analysis_indicator(symbol=code)
        except Exception as exc:  # noqa: BLE001
            LOGGER.warning("Failed to load financials for %s: %s", code, exc)
            return pd.DataFrame()
        mapping = {
            "日期": "report_date",
            "每股收益": "eps",
            "归母净利润": "net_profit",
            "净利润": "net_profit",
        }
        df = df.rename(columns=mapping)
        if "report_date" in df.columns:
            df["report_date"] = pd.to_datetime(df["report_date"])
        return df[[col for col in ["report_date", "eps", "net_profit"] if col in df.columns]]

    def _infer_market(self, code: str) -> str:
        if code.startswith("6"):
            return "SH"
        if code.startswith("8") or code.startswith("4"):
            return "BJ"
        return "SZ"

    def _to_cny(self, value: Any) -> float | None:
        try:
            if value is None:
                return None
            return float(value)
        except (TypeError, ValueError):
            return None
