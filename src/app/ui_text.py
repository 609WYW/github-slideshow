from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class UIText:
    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @classmethod
    def from_yaml_compatible_json(cls, file_path: Path) -> "UIText":
        # YAML 1.2 is a superset of JSON; this keeps runtime dependency-free in Stage 1/2/3.
        with file_path.open("r", encoding="utf-8") as handle:
            content = json.load(handle)
        return cls(content)

    def get_any(self, key: str) -> Any:
        current: Any = self._data
        for part in key.split("."):
            if not isinstance(current, dict) or part not in current:
                raise KeyError(f"Missing UI text key: {key}")
            current = current[part]
        return current

    def get(self, key: str) -> str:
        value = self.get_any(key)
        if not isinstance(value, str):
            raise TypeError(f"UI key does not map to string: {key}")
        return value
