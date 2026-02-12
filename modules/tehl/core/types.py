from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class TEHLRunInput:
    values: dict[str, Any]


@dataclass(slots=True)
class TEHLRunOutput:
    status: str
    kpis: dict[str, float]
