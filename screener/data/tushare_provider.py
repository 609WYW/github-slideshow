from __future__ import annotations

import logging

import pandas as pd

from screener.data.base import DataProvider

LOGGER = logging.getLogger(__name__)


class TushareProvider(DataProvider):
    def __init__(self, token: str) -> None:
        try:
            import tushare as ts  # type: ignore
        except ImportError as exc:  # pragma: no cover - dependency runtime
            raise RuntimeError("Tushare is required. Please install tushare.") from exc
        ts.set_token(token)
        self.pro = ts.pro_api()

    def list_stocks(self, markets: list[str]) -> pd.DataFrame:
        data = self.pro.stock_basic(exchange="", list_status="L", fields="ts_code,symbol,name,market")
        data = data.rename(columns={"ts_code": "symbol", "symbol": "code", "name": "name"})
        data["market"] = data["symbol"].str.split(".").str[1]
        data = data[data["market"].isin(markets)].copy()
        return data[["symbol", "code", "name", "market"]]

    def daily_history(self, symbol: str) -> pd.DataFrame:
        try:
            data = self.pro.daily(ts_code=f"{symbol}.SH" if symbol.startswith("6") else f"{symbol}.SZ")
        except Exception as exc:  # noqa: BLE001
            LOGGER.error("Tushare daily failed for %s: %s", symbol, exc)
            return pd.DataFrame()
        if data.empty:
            return data
        data = data.rename(
            columns={
                "trade_date": "date",
                "open": "open",
                "close": "close",
                "high": "high",
                "low": "low",
                "vol": "volume",
                "amount": "amount",
            }
        )
        data["date"] = pd.to_datetime(data["date"], format="%Y%m%d")
        return data[["date", "open", "high", "low", "close", "volume", "amount"]]

    def market_caps(self) -> pd.DataFrame:
        try:
            data = self.pro.daily_basic(ts_code="", fields="ts_code,total_mv,circ_mv")
        except Exception as exc:  # noqa: BLE001
            LOGGER.error("Tushare market cap failed: %s", exc)
            return pd.DataFrame()
        data = data.rename(columns={"ts_code": "symbol", "total_mv": "total_market_cap", "circ_mv": "float_market_cap"})
        data["code"] = data["symbol"].str.split(".").str[0]
        data["total_market_cap"] = pd.to_numeric(data["total_market_cap"], errors="coerce") * 1e4
        data["float_market_cap"] = pd.to_numeric(data["float_market_cap"], errors="coerce") * 1e4
        return data[["code", "total_market_cap", "float_market_cap"]]

    def quarterly_financials(self, symbol: str) -> pd.DataFrame:
        try:
            data = self.pro.fina_indicator(ts_code=f"{symbol}.SH" if symbol.startswith("6") else f"{symbol}.SZ", fields="end_date,eps,netprofit_margin")
        except Exception as exc:  # noqa: BLE001
            LOGGER.error("Tushare financials failed for %s: %s", symbol, exc)
            return pd.DataFrame()
        if data.empty:
            return data
        data = data.rename(columns={"end_date": "report_date", "eps": "EPS", "netprofit_margin": "net_profit"})
        data["report_date"] = pd.to_datetime(data["report_date"], format="%Y%m%d")
        return data
