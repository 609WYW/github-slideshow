from __future__ import annotations

from typing import Any


def compute_score(data: dict[str, Any], weights: dict[str, float]) -> float:
    score = 0.0
    distance = data.get("quarter_cross_distance")
    if distance is not None:
        score += weights.get("quarter_cross_recency", 0.0) * (1.0 / (1.0 + distance))
    score += weights.get("month_opening_growth", 0.0) * max(data.get("month_opening_growth", 0.0), 0.0)
    week_strength = (data.get("week_norm_dif", 0.0) + data.get("week_norm_dea", 0.0)) / 2
    score += weights.get("week_strength", 0.0) * week_strength
    if data.get("ma_bullish"):
        score += weights.get("ma_bullish_bonus", 0.0)
    if data.get("ma_converge"):
        score += weights.get("ma_converge_bonus", 0.0)
    return float(score)
