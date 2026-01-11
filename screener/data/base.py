from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class DataProvider(ABC):
    @abstractmethod
    def list_stocks(self, markets: list[str]) -> pd.DataFrame:
        raise NotImplementedError

    @abstractmethod
    def daily_history(self, symbol: str) -> pd.DataFrame:
        raise NotImplementedError

    @abstractmethod
    def market_caps(self) -> pd.DataFrame:
        raise NotImplementedError

    @abstractmethod
    def quarterly_financials(self, symbol: str) -> pd.DataFrame:
        raise NotImplementedError
