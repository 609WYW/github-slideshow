from __future__ import annotations

from dataclasses import dataclass


@dataclass
class STFilterResult:
    is_filtered: bool
    reason: str


def check_st(name: str, tags: list[str], keywords: list[str]) -> STFilterResult:
    name_upper = name.upper()
    for key in keywords:
        if key.upper() in name_upper:
            return STFilterResult(True, f"name contains {key}")
    for tag in tags:
        if tag.upper() == "ST":
            return STFilterResult(True, "risk tag ST")
    return STFilterResult(False, "")
