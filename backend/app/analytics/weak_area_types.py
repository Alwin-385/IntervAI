"""Canonical weak-area categories tracked across interview history."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

WeakAreaKind = Literal[
    "communication_issues",
    "confidence_problems",
    "weak_technical_explanations",
    "poor_behavioral_storytelling",
    "dsa_explanation_issues",
    "filler_word_overuse",
    "lack_of_structure",
]

PriorityLevel = Literal["high", "medium", "low"]
TrendDirection = Literal["improving", "declining", "stable", "insufficient_data"]


@dataclass(frozen=True)
class WeakAreaDefinition:
    kind: WeakAreaKind
    area_name: str
    category: str
    description: str


WEAK_AREA_DEFINITIONS: dict[WeakAreaKind, WeakAreaDefinition] = {
    "communication_issues": WeakAreaDefinition(
        kind="communication_issues",
        area_name="Communication clarity",
        category="Delivery",
        description="Answers or delivery lack clear, concise communication.",
    ),
    "confidence_problems": WeakAreaDefinition(
        kind="confidence_problems",
        area_name="Interview confidence",
        category="Delivery",
        description="Hesitant language or low confidence signals in speech.",
    ),
    "weak_technical_explanations": WeakAreaDefinition(
        kind="weak_technical_explanations",
        area_name="Technical depth",
        category="Technical",
        description="Technical answers miss depth, accuracy, or trade-off discussion.",
    ),
    "poor_behavioral_storytelling": WeakAreaDefinition(
        kind="poor_behavioral_storytelling",
        area_name="Behavioral storytelling (STAR)",
        category="Behavioral",
        description="Behavioral answers lack STAR structure or measurable outcomes.",
    ),
    "dsa_explanation_issues": WeakAreaDefinition(
        kind="dsa_explanation_issues",
        area_name="DSA & complexity",
        category="DSA",
        description="Algorithm answers omit complexity analysis or optimality reasoning.",
    ),
    "filler_word_overuse": WeakAreaDefinition(
        kind="filler_word_overuse",
        area_name="Filler words",
        category="Delivery",
        description="Frequent um/uh/like and hedging reduce perceived fluency.",
    ),
    "lack_of_structure": WeakAreaDefinition(
        kind="lack_of_structure",
        area_name="Answer structure",
        category="Communication",
        description="Responses jump around without context → approach → result flow.",
    ),
}
