from __future__ import annotations

from typing import Any


REQUIRED_TOP_KEYS = ["spec_version", "project", "module", "ui", "outputs"]


def validate_top_level(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in REQUIRED_TOP_KEYS:
        if key not in spec:
            errors.append(f"missing top key: {key}")
    return errors
