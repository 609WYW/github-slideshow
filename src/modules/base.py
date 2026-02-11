from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True, slots=True)
class ModuleDefinition:
    key: str
    nav_text_key: str
    title_text_key: str
    page_factory: Callable[[], Any]
