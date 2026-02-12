from __future__ import annotations


def format_with_unit(value: object, unit: str) -> str:
    return f"{value} {unit}".strip()
