from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd


class CacheManager:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        safe_key = key.replace("/", "_")
        return self.base_dir / f"{safe_key}.csv"

    def load(self, key: str) -> Optional[pd.DataFrame]:
        path = self._path(key)
        if not path.exists():
            return None
        return pd.read_csv(path)

    def save(self, key: str, df: pd.DataFrame) -> None:
        path = self._path(key)
        df.to_csv(path, index=False)
