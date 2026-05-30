"""Aggregate historical interview analyses into recurring weak areas."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from statistics import mean
from uuid import UUID

from app.analytics.weak_area_types import (
    WEAK_AREA_DEFINITIONS,
    PriorityLevel,
    TrendDirection,
    WeakAreaKind,
)
from app.models.enums import WeakAreaSeverity


@dataclass
class SpeechHistoryItem:
    session_id: UUID
    answer_id: UUID
    recorded_at: datetime
    communication_score: float
    confidence_score: float
    fluency_score: float
    filler_word_count: int
    words_per_minute: float
    weak_patterns: list[str]


@dataclass
class AnswerHistoryItem:
    session_id: UUID
    answer_id: UUID
    recorded_at: datetime
    interview_category: str
    correctness_verdict: str
    rubric_score: float
    communication_score: float
    technical_score: float
    clarity_score: float
    completeness_score: float
    technical_accuracy_score: float
    star_overall: float | None
    dsa_optimality: float | None
    rubric_points_missed: list[str]
    weaknesses: list[str]
    missing_concepts: list[str]


@dataclass
class WeakAreaSignal:
    kind: WeakAreaKind
    hit: bool
    weight: float = 1.0


@dataclass
class DetectedWeakArea:
    kind: WeakAreaKind
    area_name: str
    category: str
    priority: PriorityLevel
    severity: WeakAreaSeverity
    frequency: int
    total_opportunities: int
    frequency_rate: float
    trend: TrendDirection
    trend_delta: float
    description: str
    improvement_suggestions: list[str]
    practice_recommendations: list[str]
    evidence: list[str] = field(default_factory=list)
    last_seen_at: datetime | None = None


def _priority_from_rate(rate: float, avg_severity: float) -> PriorityLevel:
    if rate >= 0.55 or avg_severity >= 75:
        return "high"
    if rate >= 0.3 or avg_severity >= 50:
        return "medium"
    return "low"


def _severity_enum(priority: PriorityLevel) -> WeakAreaSeverity:
    if priority == "high":
        return WeakAreaSeverity.HIGH
    if priority == "medium":
        return WeakAreaSeverity.MEDIUM
    return WeakAreaSeverity.LOW


def _trend(
    recent_hits: int, recent_n: int, older_hits: int, older_n: int
) -> tuple[TrendDirection, float]:
    if recent_n < 1 and older_n < 1:
        return "insufficient_data", 0.0
    recent_rate = recent_hits / recent_n if recent_n else 0.0
    older_rate = older_hits / older_n if older_n else recent_rate
    delta = recent_rate - older_rate
    if abs(delta) < 0.08:
        return "stable", round(delta, 3)
    if delta < 0:
        return "improving", round(delta, 3)
    return "declining", round(delta, 3)


def _split_recent(
    items: list[tuple[datetime, bool]],
) -> tuple[list[tuple[datetime, bool]], list[tuple[datetime, bool]]]:
    ordered = sorted(items, key=lambda x: x[0])
    if len(ordered) <= 4:
        return ordered, []
    mid = max(1, len(ordered) // 2)
    return ordered[mid:], ordered[:mid]


def _signals_for_answer(item: AnswerHistoryItem) -> list[WeakAreaSignal]:
    signals: list[WeakAreaSignal] = []
    cat = item.interview_category.lower()

    if item.communication_score < 62 or item.clarity_score < 58:
        signals.append(WeakAreaSignal("communication_issues", True, 1.0))

    if item.clarity_score < 55 or any(
        "structure" in m.lower() or "context" in m.lower() for m in item.rubric_points_missed
    ):
        signals.append(WeakAreaSignal("lack_of_structure", True, 1.0))

    if cat in ("technical", "dsa", "mixed", "resume_based") and (
        item.technical_score < 58 or item.technical_accuracy_score < 55 or item.rubric_score < 55
    ):
        signals.append(WeakAreaSignal("weak_technical_explanations", True, 1.0))

    if cat == "behavioral" and (
        (item.star_overall is not None and item.star_overall < 62)
        or item.correctness_verdict in ("incorrect", "partially_correct")
    ):
        signals.append(WeakAreaSignal("poor_behavioral_storytelling", True, 1.0))

    if cat == "dsa" and (
        (item.dsa_optimality is not None and item.dsa_optimality < 60)
        or any("complexity" in m.lower() for m in item.missing_concepts)
    ):
        signals.append(WeakAreaSignal("dsa_explanation_issues", True, 1.0))

    if item.correctness_verdict == "incorrect" and item.completeness_score < 50:
        signals.append(WeakAreaSignal("lack_of_structure", True, 0.6))

    return signals


def _signals_for_speech(item: SpeechHistoryItem) -> list[WeakAreaSignal]:
    signals: list[WeakAreaSignal] = []
    if item.communication_score < 62:
        signals.append(WeakAreaSignal("communication_issues", True, 0.9))
    if item.confidence_score < 58:
        signals.append(WeakAreaSignal("confidence_problems", True, 1.0))
    if item.filler_word_count >= 6:
        signals.append(WeakAreaSignal("filler_word_overuse", True, 1.0))
    elif item.filler_word_count >= 3:
        signals.append(WeakAreaSignal("filler_word_overuse", True, 0.5))
    if any("filler" in p.lower() for p in item.weak_patterns):
        signals.append(WeakAreaSignal("filler_word_overuse", True, 1.0))
    if any(
        "pace" in p.lower() or "slow" in p.lower() or "fast" in p.lower()
        for p in item.weak_patterns
    ):
        signals.append(WeakAreaSignal("communication_issues", True, 0.5))
    if item.fluency_score < 60:
        signals.append(WeakAreaSignal("communication_issues", True, 0.6))
    return signals


_SUGGESTIONS: dict[WeakAreaKind, tuple[list[str], list[str]]] = {
    "communication_issues": (
        [
            "Open with one sentence that directly answers the question.",
            "Use short paragraphs: context → your approach → outcome.",
            "Record practice answers and listen for clarity at 1.25× speed.",
        ],
        [
            "Do 3 mock answers daily focusing only on clarity (no jargon first).",
            "Use the post-interview speech results to track communication score.",
        ],
    ),
    "confidence_problems": (
        [
            'Replace hedging ("I think", "maybe") with definitive statements.',
            "Practice power poses + 60s outline before each recorded answer.",
            "End answers with a clear takeaway tied to the role.",
        ],
        [
            "Re-record weak answers until confidence score ≥ 70.",
            "Read answers aloud standing up to project energy.",
        ],
    ),
    "weak_technical_explanations": (
        [
            "State assumptions, approach, trade-offs, and validation for each technical question.",
            "Name concrete tools/metrics from your experience.",
            "Compare at least two alternatives and when each fails.",
        ],
        [
            "Run 2 technical mock interviews per week with rubric self-check.",
            "Study expected answer points shown on each question card before answering.",
        ],
    ),
    "poor_behavioral_storytelling": (
        [
            "Use STAR: Situation, Task, Action, Result with one metric in Result.",
            'Use "I" for your actions, not only "we".',
            "Keep stories under 2 minutes with one clear conflict.",
        ],
        [
            "Prepare 5 STAR stories mapped to common behavioral prompts.",
            "Review STAR scores on the results page after each interview.",
        ],
    ),
    "dsa_explanation_issues": (
        [
            "Always state brute-force then optimal time/space complexity.",
            "Walk through a small example and one edge case.",
            "Explain why your chosen structure fits the constraints.",
        ],
        [
            "Practice 1 DSA question daily out loud with complexity first.",
            "Use NeetCode/leetcode patterns but explain trade-offs verbally.",
        ],
    ),
    "filler_word_overuse": (
        [
            "Pause silently instead of saying um/uh — silence reads as thoughtful.",
            "Slow to ~130–150 WPM; fillers spike when rushing.",
            "Drill answers without filler words for 5 minutes daily.",
        ],
        [
            "Use browser live captions to catch fillers while recording.",
            "Target filler count under 3 per answer on speech results.",
        ],
    ),
    "lack_of_structure": (
        [
            'Template: "Short answer → context → steps you took → measurable result."',
            "Signpost with First / Then / Finally.",
            "Hit each expected rubric bullet explicitly.",
        ],
        [
            "Outline answers in 15 seconds before recording.",
            "Compare your transcript to the model answer on incorrect items.",
        ],
    ),
}


def rate_threshold(hits: int, total: int) -> float:
    return hits / total if total else 0.0


def _dedupe_signals(signals: list[WeakAreaSignal]) -> list[WeakAreaSignal]:
    seen: set[WeakAreaKind] = set()
    out: list[WeakAreaSignal] = []
    for sig in signals:
        if sig.kind in seen:
            continue
        seen.add(sig.kind)
        out.append(sig)
    return out


def detect_weak_areas(
    answers: list[AnswerHistoryItem],
    speeches: list[SpeechHistoryItem],
    *,
    min_frequency: int = 2,
) -> list[DetectedWeakArea]:
    """Aggregate signals across all historical analyses for a user."""
    hit_sources: dict[WeakAreaKind, set[str]] = {k: set() for k in WEAK_AREA_DEFINITIONS}
    hit_severities: dict[WeakAreaKind, list[float]] = {k: [] for k in WEAK_AREA_DEFINITIONS}
    hit_times: dict[WeakAreaKind, list[datetime]] = {k: [] for k in WEAK_AREA_DEFINITIONS}
    evidence_by_kind: dict[WeakAreaKind, list[str]] = {k: [] for k in WEAK_AREA_DEFINITIONS}
    last_seen: dict[WeakAreaKind, datetime] = {}

    def record(
        kind: WeakAreaKind,
        when: datetime,
        source_key: str,
        severity: float,
        note: str | None = None,
    ) -> None:
        if source_key in hit_sources[kind]:
            return
        hit_sources[kind].add(source_key)
        hit_severities[kind].append(severity)
        hit_times[kind].append(when)
        last_seen[kind] = max(last_seen.get(kind, when), when)
        if note and len(evidence_by_kind[kind]) < 4:
            evidence_by_kind[kind].append(note)

    for a in answers:
        for sig in _dedupe_signals(_signals_for_answer(a)):
            if sig.hit:
                note = f"Answer rubric {a.rubric_score:.0f}% · {a.correctness_verdict}"
                record(sig.kind, a.recorded_at, f"answer:{a.answer_id}", 100 - a.rubric_score, note)

    for s in speeches:
        for sig in _dedupe_signals(_signals_for_speech(s)):
            if sig.hit:
                note = f"Speech: {s.filler_word_count} fillers · conf {s.confidence_score:.0f}%"
                record(
                    sig.kind,
                    s.recorded_at,
                    f"speech:{s.answer_id}",
                    100 - s.communication_score,
                    note,
                )

    opportunities = max(len(answers) + len(speeches), 1)

    detected: list[DetectedWeakArea] = []
    for kind, definition in WEAK_AREA_DEFINITIONS.items():
        frequency = len(hit_sources[kind])
        if frequency < 1:
            continue
        rate = min(1.0, frequency / opportunities)
        if frequency < min_frequency and rate < 0.2:
            continue
        severities = hit_severities[kind]
        avg_sev = mean(severities) if severities else 0
        priority = _priority_from_rate(rate, avg_sev)

        all_dates = sorted({a.recorded_at for a in answers} | {s.recorded_at for s in speeches})
        times = hit_times[kind]
        if len(all_dates) >= 2:
            mid_idx = len(all_dates) // 2
            mid_date = all_dates[mid_idx]
            recent_n = sum(1 for d in all_dates if d >= mid_date)
            older_n = len(all_dates) - recent_n
            recent_hits = sum(1 for t in times if t >= mid_date)
            older_hits = len(times) - recent_hits
            trend, delta = _trend(recent_hits, recent_n, older_hits, older_n)
        else:
            trend, delta = "insufficient_data", 0.0

        tips, practice = _SUGGESTIONS[kind]
        detected.append(
            DetectedWeakArea(
                kind=kind,
                area_name=definition.area_name,
                category=definition.category,
                priority=priority,
                severity=_severity_enum(priority),
                frequency=frequency,
                total_opportunities=opportunities,
                frequency_rate=round(rate, 3),
                trend=trend,
                trend_delta=delta,
                description=definition.description,
                improvement_suggestions=tips,
                practice_recommendations=practice,
                evidence=evidence_by_kind[kind][:4],
                last_seen_at=last_seen.get(kind),
            ),
        )

    detected.sort(
        key=lambda w: (
            {"high": 0, "medium": 1, "low": 2}[w.priority],
            -w.frequency,
            -w.frequency_rate,
        ),
    )
    return detected
