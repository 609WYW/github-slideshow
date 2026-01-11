from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass
class CacheManager:
    base_dir: Path

    def __post_init__(self) -> None:
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def read(self, key: str) -> pd.DataFrame | None:
        path = self.base_dir / f"{key}.csv"
        if not path.exists():
            return None
        return pd.read_csv(path)

    def write(self, key: str, data: pd.DataFrame) -> None:
        path = self.base_dir / f"{key}.csv"
        data.to_csv(path, index=False)
