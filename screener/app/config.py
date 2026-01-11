from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class DataConfig:
    provider: str = "akshare"
    tushare_token: str | None = None
    cache_dir: str = ".cache"
    use_cache: bool = True
    markets: list[str] = field(default_factory=lambda: ["SH", "SZ", "BJ"])


@dataclass
class MacdConfig:
    fast: int = 12
    slow: int = 26
    signal: int = 9


@dataclass
class ZeroBandConfig:
    quarter: float = 0.01
    month: float = 0.0
    week: float = 0.015
    daily: float = 0.0


@dataclass
class MacdFilterConfig:
    last_n_q_bars: int = 2
    enable_daily_filter: bool = False
    daily_rule: str = "dif_gt_dea_and_hist_gt_0"


@dataclass
class MarketCapConfig:
    max_total_market_cap: float = 1e11
    field: str = "total_market_cap"


@dataclass
class FinancialConfig:
    eps_field_candidates: list[str] = field(
        default_factory=lambda: [
            "基本每股收益(元)",
            "基本每股收益",
            "每股收益",  # fallback
        ]
    )
    net_profit_field_candidates: list[str] = field(
        default_factory=lambda: [
            "归属于母公司股东的净利润(元)",
            "归母净利润",
            "归属母公司股东的净利润",
        ]
    )
    require_net_profit_positive: bool = True


@dataclass
class MovingAverageConfig:
    enabled: bool = True
    price_above: list[int] = field(default_factory=lambda: [20])
    ma_order: list[int] = field(default_factory=lambda: [20, 60])


@dataclass
class ScoreWeights:
    quarter_cross: float = 2.0
    month_opening: float = 1.5
    week_strength: float = 1.0
    ma_strength: float = 1.0


@dataclass
class OutputConfig:
    export: list[str] = field(default_factory=lambda: ["csv"])
    output_dir: str = "output"
    html_report: bool = True


@dataclass
class AppConfig:
    data: DataConfig = field(default_factory=DataConfig)
    macd: MacdConfig = field(default_factory=MacdConfig)
    zero_band: ZeroBandConfig = field(default_factory=ZeroBandConfig)
    macd_filters: MacdFilterConfig = field(default_factory=MacdFilterConfig)
    market_cap: MarketCapConfig = field(default_factory=MarketCapConfig)
    financial: FinancialConfig = field(default_factory=FinancialConfig)
    moving_average: MovingAverageConfig = field(default_factory=MovingAverageConfig)
    score_weights: ScoreWeights = field(default_factory=ScoreWeights)
    output: OutputConfig = field(default_factory=OutputConfig)
    max_workers: int = 8
    log_level: str = "INFO"


def _deep_update(target: dict[str, Any], source: dict[str, Any]) -> dict[str, Any]:
    for key, value in source.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            target[key] = _deep_update(target[key], value)
        else:
            target[key] = value
    return target


def load_config(path: str | Path) -> AppConfig:
    with open(path, "r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}
    data = _deep_update(AppConfig().__dict__, raw)

    return AppConfig(
        data=DataConfig(**data.get("data", {})),
        macd=MacdConfig(**data.get("macd", {})),
        zero_band=ZeroBandConfig(**data.get("zero_band", {})),
        macd_filters=MacdFilterConfig(**data.get("macd_filters", {})),
        market_cap=MarketCapConfig(**data.get("market_cap", {})),
        financial=FinancialConfig(**data.get("financial", {})),
        moving_average=MovingAverageConfig(**data.get("moving_average", {})),
        score_weights=ScoreWeights(**data.get("score_weights", {})),
        output=OutputConfig(**data.get("output", {})),
        max_workers=data.get("max_workers", 8),
        log_level=data.get("log_level", "INFO"),
    )
