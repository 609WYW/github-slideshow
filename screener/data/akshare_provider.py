from __future__ import annotations

import logging

import pandas as pd

from screener.data.base import DataProvider

LOGGER = logging.getLogger(__name__)


class AkshareProvider(DataProvider):
    def __init__(self) -> None:
        try:
            import akshare as ak  # type: ignore
        except ImportError as exc:  # pragma: no cover - dependency runtime
            raise RuntimeError("AkShare is required. Please install akshare.") from exc
        self.ak = ak

    def list_stocks(self, markets: list[str]) -> pd.DataFrame:
        data = self.ak.stock_info_a_code_name()
        data = data.rename(columns={"code": "code", "name": "name"})
        data["market"] = data["code"].str[0].map({"6": "SH", "0": "SZ", "3": "SZ", "8": "BJ"})
        data = data[data["market"].isin(markets)].copy()
        data["symbol"] = data["code"]
        return data[["symbol", "code", "name", "market"]]

    def daily_history(self, symbol: str) -> pd.DataFrame:
        try:
            data = self.ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust="qfq")
        except Exception as exc:  # noqa: BLE001
            LOGGER.error("AkShare daily history failed for %s: %s", symbol, exc)
            return pd.DataFrame()
        if data.empty:
            return data
        data = data.rename(
            columns={
                "日期": "date",
                "开盘": "open",
                "收盘": "close",
                "最高": "high",
                "最低": "low",
                "成交量": "volume",
                "成交额": "amount",
            }
        )
        data["date"] = pd.to_datetime(data["date"])
        return data[["date", "open", "high", "low", "close", "volume", "amount"]]

    def market_caps(self) -> pd.DataFrame:
        try:
            data = self.ak.stock_zh_a_spot_em()
        except Exception as exc:  # noqa: BLE001
            LOGGER.error("AkShare spot failed: %s", exc)
            return pd.DataFrame()
        columns_map = {
            "代码": "code",
            "名称": "name",
            "总市值": "total_market_cap",
            "流通市值": "float_market_cap",
        }
        data = data.rename(columns=columns_map)
        data["total_market_cap"] = pd.to_numeric(data.get("total_market_cap"), errors="coerce")
        data["float_market_cap"] = pd.to_numeric(data.get("float_market_cap"), errors="coerce")
        return data[["code", "name", "total_market_cap", "float_market_cap"]]

    def quarterly_financials(self, symbol: str) -> pd.DataFrame:
        try:
            data = self.ak.stock_financial_analysis_indicator(symbol=symbol)
        except Exception as exc:  # noqa: BLE001
            LOGGER.error("AkShare financials failed for %s: %s", symbol, exc)
            return pd.DataFrame()
        if data.empty:
            return data
        data = data.rename(columns={"日期": "report_date"})
        data["report_date"] = pd.to_datetime(data["report_date"], errors="coerce")
        return data
