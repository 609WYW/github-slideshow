from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class AppConfig:
    output_dir: Path = Path("output")
    export: list[str] = field(default_factory=lambda: ["csv", "xlsx"])
    max_workers: int = 8
    use_cache: bool = True
    cache_dir: Path = Path(".cache")
    limit: int | None = None
    log_level: str = "INFO"


@dataclass
class ProviderConfig:
    name: str = "akshare"
    tushare_token: str = ""


@dataclass
class FiltersConfig:
    st_keywords: list[str] = field(default_factory=lambda: ["ST", "*ST", "退"])
    market_cap: dict[str, Any] = field(
        default_factory=lambda: {"enabled": True, "field": "total_market_cap", "max_cny": 1.0e11}
    )
    macd: dict[str, Any] = field(
        default_factory=lambda: {
            "last_n_quarter": 2,
            "zero_band_q": 0.01,
            "zero_band_w": 0.015,
            "min_opening_growth": 0.0,
            "enable_daily_filter": False,
        }
    )
    financial: dict[str, Any] = field(
        default_factory=lambda: {"require_net_profit_positive": True}
    )
    ma: dict[str, Any] = field(
        default_factory=lambda: {
            "windows": [5, 10, 20],
            "converge_pct": 0.02,
            "enable_converge": True,
            "enable_bullish": True,
        }
    )


@dataclass
class ScoringConfig:
    weights: dict[str, float] = field(
        default_factory=lambda: {
            "quarter_cross_recency": 4.0,
            "month_opening_growth": 2.0,
            "week_strength": 1.5,
            "ma_bullish_bonus": 1.0,
            "ma_converge_bonus": 0.5,
        }
    )


@dataclass
class Config:
    app: AppConfig = field(default_factory=AppConfig)
    provider: ProviderConfig = field(default_factory=ProviderConfig)
    filters: FiltersConfig = field(default_factory=FiltersConfig)
    scoring: ScoringConfig = field(default_factory=ScoringConfig)


def _merge_dataclass(instance: Any, values: dict[str, Any]) -> Any:
    for key, value in values.items():
        if hasattr(instance, key):
            current = getattr(instance, key)
            if isinstance(current, (AppConfig, ProviderConfig, FiltersConfig, ScoringConfig)):
                _merge_dataclass(current, value)
            else:
                setattr(instance, key, value)
    return instance


def load_config(path: Path) -> Config:
    config = Config()
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if "app" in payload:
        _merge_dataclass(config.app, payload["app"])
    if "provider" in payload:
        _merge_dataclass(config.provider, payload["provider"])
    if "filters" in payload:
        _merge_dataclass(config.filters, payload["filters"])
    if "scoring" in payload:
        _merge_dataclass(config.scoring, payload["scoring"])
    return config
