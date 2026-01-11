from __future__ import annotations

from screener.app.config import ScoreWeights


def score_signal(quarter: dict, month: dict, week: dict, ma: dict, weights: ScoreWeights) -> float:
    score = 0.0
    if quarter.get("cross"):
        bars = quarter.get("cross_bars_ago", 0) or 0
        score += weights.quarter_cross * max(0.0, 1.0 - 0.3 * bars)
    if month.get("opening"):
        score += weights.month_opening * (1.0 + max(0.0, month.get("HIST", 0)))
    score += weights.week_strength * max(0.0, week.get("norm_dif", 0))
    if ma.get("pass"):
        score += weights.ma_strength
    return round(score, 4)
