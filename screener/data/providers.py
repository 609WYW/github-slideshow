from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import pandas as pd


@dataclass
class SymbolInfo:
    code: str
    name: str
    market: str
    total_market_cap: float | None = None
    float_market_cap: float | None = None


class DataProvider(Protocol):
    def get_symbols(self) -> list[SymbolInfo]:
        raise NotImplementedError

    def get_daily(self, code: str) -> pd.DataFrame:
        raise NotImplementedError

    def get_financials(self, code: str) -> pd.DataFrame:
        raise NotImplementedError
