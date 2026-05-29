"""Helpers for Phase 12 speech analysis persistence."""

from __future__ import annotations

from typing import Any


def is_phase12_analysis_complete(metrics: dict[str, Any] | None) -> bool:
    """True when metrics were produced by the communication analyzer (not transcription-only)."""
    if not metrics:
        return False
    chart = metrics.get("chart_scores")
    if not isinstance(chart, dict):
        return False
    fluency = chart.get("fluency")
    return isinstance(fluency, (int, float)) and fluency > 0
