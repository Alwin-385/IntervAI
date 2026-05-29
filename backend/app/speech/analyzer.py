"""Transcript-based speech communication analysis (Phase 12)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# Longer phrases first for non-overlapping counts
FILLER_PHRASES: tuple[tuple[str, str], ...] = (
    ("you know", r"\byou\s+know\b"),
    ("i mean", r"\bi\s+mean\b"),
    ("kind of", r"\bkind\s+of\b"),
    ("sort of", r"\bsort\s+of\b"),
    ("basically", r"\bbasically\b"),
    ("actually", r"\bactually\b"),
    ("literally", r"\bliterally\b"),
)

FILLER_STANDALONE: tuple[tuple[str, str], ...] = (
    ("um", r"\bum+m?\b"),
    ("uh", r"\buh+h?\b"),
    ("erm", r"\berm+\b"),
    ("hmm", r"\bhmm+\b"),
    ("like", r"\blike\b"),
    ("so", r"\bso+\b"),
    ("well", r"\bwell+\b"),
    ("right", r"\bright\b"),
    ("okay", r"\bok(?:ay)?\b"),
)

HEDGING_PHRASES: tuple[tuple[str, str], ...] = (
    ("i think", r"\bi\s+think\b"),
    ("maybe", r"\bmaybe\b"),
    ("probably", r"\bprobably\b"),
    ("not sure", r"\bnot\s+sure\b"),
    ("i guess", r"\bi\s+guess\b"),
    ("sort of", r"\bsort\s+of\b"),
    ("kind of", r"\bkind\s+of\b"),
)

IDEAL_WPM = 140.0
WPM_MIN = 90.0
WPM_MAX = 180.0


@dataclass
class FillerStat:
    word: str
    count: int


@dataclass
class SpeechAnalysisResult:
    transcript: str
    word_count: int
    words_per_minute: float
    duration_seconds: float
    filler_word_count: int
    filler_word_stats: list[FillerStat]
    pause_count: int
    hesitation_count: int
    fluency_score: float
    communication_score: float
    confidence_score: float
    speaking_speed_score: float
    pause_score: float
    weak_patterns: list[str] = field(default_factory=list)
    communication_tips: list[str] = field(default_factory=list)
    confidence_indicators: dict[str, float] = field(default_factory=dict)
    metrics: dict[str, object] = field(default_factory=dict)


def _clamp_score(value: float) -> float:
    return round(max(0.0, min(100.0, value)), 1)


def _tokenize_words(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z']+", text.lower())


def _count_regex(pattern: str, text: str) -> int:
    return len(re.findall(pattern, text, flags=re.IGNORECASE))


def _count_fillers(text: str) -> tuple[int, list[FillerStat]]:
    """Count filler phrases and standalone fillers (case-insensitive)."""
    working = f" {text.lower()} "
    stats: list[FillerStat] = []
    total = 0

    for label, pattern in FILLER_PHRASES:
        matches = list(re.finditer(pattern, working, flags=re.IGNORECASE))
        if matches:
            count = len(matches)
            stats.append(FillerStat(word=label, count=count))
            total += count
            for match in reversed(matches):
                span = match.end() - match.start()
                working = working[: match.start()] + (" " * span) + working[match.end() :]

    for label, pattern in FILLER_STANDALONE:
        count = _count_regex(pattern, working)
        if count:
            stats.append(FillerStat(word=label, count=count))
            total += count

    stats.sort(key=lambda s: (-s.count, s.word))
    return total, stats


def _count_hedging(text: str) -> int:
    lower = text.lower()
    return sum(_count_regex(pattern, lower) for _, pattern in HEDGING_PHRASES)


def _count_pauses(text: str) -> int:
    ellipsis = len(re.findall(r"\.{3,}|…", text))
    em_dash_breaks = len(re.findall(r"\s—\s|--", text))
    comma_heavy = len(re.findall(r",\s+\w", text)) // 3
    return ellipsis + em_dash_breaks + comma_heavy


def _count_hesitations(text: str, filler_count: int) -> int:
    repeated = len(re.findall(r"\b(\w+)\s+\1\b", text, flags=re.IGNORECASE))
    restarts = len(
        re.findall(
            r"\b(i mean|wait|sorry|let me|you know)\b",
            text,
            flags=re.IGNORECASE,
        ),
    )
    return filler_count + repeated + restarts


def _sentence_count(text: str) -> int:
    parts = re.split(r"[.!?]+", text)
    return max(1, len([p for p in parts if p.strip()]))


def _speaking_speed_score(wpm: float) -> float:
    if wpm <= 0:
        return 40.0
    if WPM_MIN <= wpm <= WPM_MAX:
        distance = abs(wpm - IDEAL_WPM)
        span = (WPM_MAX - WPM_MIN) / 2
        return _clamp_score(100 - (distance / span) * 35)
    if wpm < WPM_MIN:
        return _clamp_score(55 + (wpm / WPM_MIN) * 35)
    overshoot = wpm - WPM_MAX
    return _clamp_score(max(35.0, 85 - overshoot * 1.2))


def _filler_penalty(filler_count: int, word_count: int) -> float:
    if word_count == 0:
        return 0.0
    rate = filler_count / word_count
    return min(55.0, 15.0 + rate * 900)


def _pause_penalty(pause_count: int, sentence_count: int) -> float:
    if sentence_count == 0:
        return 0.0
    rate = pause_count / sentence_count
    return min(40.0, rate * 45)


def _hesitation_penalty(hesitation_count: int, word_count: int) -> float:
    if word_count == 0:
        return 0.0
    rate = hesitation_count / max(word_count, 1)
    return min(35.0, rate * 320)


def _confidence_indicators(text: str, word_count: int, hedging_count: int) -> dict[str, float]:
    lower = text.lower()
    assertive = sum(
        1
        for phrase in (
            "i led",
            "i built",
            "i delivered",
            "i implemented",
            "i achieved",
            "i designed",
            "i managed",
            "i created",
            "i improved",
        )
        if phrase in lower
    )
    questions = text.count("?")
    return {
        "assertiveness": _clamp_score(min(100.0, 40 + assertive * 14)),
        "hedging_control": _clamp_score(max(20.0, 100 - hedging_count * 12)),
        "answer_depth": _clamp_score(min(100.0, (word_count / 60) * 100)),
        "certainty": _clamp_score(max(25.0, 100 - questions * 10)),
    }


def _confidence_score(indicators: dict[str, float], hedging_count: int) -> float:
    base = sum(indicators.values()) / max(len(indicators), 1)
    return _clamp_score(base - hedging_count * 4)


def _weak_patterns(
    *,
    filler_stats: list[FillerStat],
    wpm: float,
    pause_count: int,
    hesitation_count: int,
    hedging_count: int,
    word_count: int,
    filler_count: int,
) -> list[str]:
    patterns: list[str] = []
    if word_count < 25:
        patterns.append("Very short answer — expand with a concrete example (STAR format).")
    if filler_count >= 1 and word_count > 0:
        rate = round((filler_count / word_count) * 100, 1)
        if rate >= 4 or filler_count >= 2:
            top = filler_stats[0] if filler_stats else None
            if top:
                patterns.append(
                    f'Filler words detected ({filler_count} total, {rate}% of words) — '
                    f'"{top.word}" used {top.count} times.',
                )
    top_filler = filler_stats[0] if filler_stats else None
    if top_filler and top_filler.count >= 2:
        patterns.append(f'Reduce "{top_filler.word}" — it appeared {top_filler.count} times.')
    if wpm > 0 and wpm < WPM_MIN:
        patterns.append("Speaking pace is slow — tighten phrasing and reduce long pauses.")
    if wpm > WPM_MAX:
        patterns.append("Speaking pace is fast — pause briefly between key points.")
    if pause_count >= 2:
        patterns.append("Frequent pauses or trailing off — outline the point before speaking.")
    if hesitation_count >= 3:
        patterns.append("Hesitation markers detected — practice the opening sentence.")
    if hedging_count >= 1:
        patterns.append("Uncertainty language (e.g. “I think”, “maybe”) weakens impact.")
    return patterns


def _communication_tips(
    *,
    weak_patterns: list[str],
    filler_stats: list[FillerStat],
    wpm: float,
    fluency_score: float,
    confidence_score: float,
    filler_count: int,
) -> list[str]:
    tips: list[str] = []
    if filler_count > 0:
        tips.append("Replace filler words with a silent pause — it sounds more confident.")
    if fluency_score < 75:
        tips.append("Pause for one beat between ideas instead of using filler sounds.")
    if confidence_score < 75:
        tips.append('Replace hedging with specifics: numbers, outcomes, and “I” statements.')
    if wpm > 0 and wpm < WPM_MIN:
        tips.append(
            "Aim for ~130–150 words per minute — rehearse a 60-second version of your answer.",
        )
    elif wpm > WPM_MAX:
        tips.append("Slow down on the first sentence; interviewers need time to follow.")
    if filler_stats:
        top = filler_stats[0].word
        tips.append(f'When you feel "{top}" coming, pause silently instead.')
    if not tips:
        tips.append("Strong delivery — keep answers structured: situation, action, result.")
    if weak_patterns:
        tips.append("Review highlighted weak patterns before your next mock question.")
    return tips[:6]


def analyze_speech(
    transcript: str,
    *,
    duration_seconds: float | None = None,
) -> SpeechAnalysisResult:
    text = (transcript or "").strip()
    words = _tokenize_words(text)
    word_count = len(words)

    duration = duration_seconds if duration_seconds and duration_seconds > 0 else None
    if duration is None and word_count > 0:
        duration = max(word_count / (IDEAL_WPM / 60.0), 5.0)
    duration_seconds = duration or 0.0

    minutes = duration_seconds / 60.0 if duration_seconds > 0 else 0.0
    wpm = round(word_count / minutes, 1) if minutes > 0 else 0.0

    filler_count, filler_stats = _count_fillers(text)
    pause_count = _count_pauses(text)
    hesitation_count = _count_hesitations(text, filler_count)
    hedging_count = _count_hedging(text)
    sentence_count = _sentence_count(text)

    speaking_speed_score = _speaking_speed_score(wpm)
    pause_score = _clamp_score(100 - _pause_penalty(pause_count, sentence_count) * 2)
    fluency_raw = (
        100
        - _filler_penalty(filler_count, word_count)
        - _pause_penalty(pause_count, sentence_count)
        - _hesitation_penalty(hesitation_count, word_count)
    )
    avg_sentence_len = word_count / sentence_count if sentence_count else 0
    if avg_sentence_len > 35:
        fluency_raw -= 8
    elif 8 <= avg_sentence_len <= 28:
        fluency_raw += 4
    fluency_score = _clamp_score(fluency_raw)

    confidence_indicators = _confidence_indicators(text, word_count, hedging_count)
    confidence_score = _confidence_score(confidence_indicators, hedging_count)

    clarity_raw = _clamp_score(
        100
        - (filler_count / max(word_count, 1)) * 120
        - hedging_count * 5,
    )
    communication_score = _clamp_score(
        fluency_score * 0.35
        + confidence_score * 0.3
        + speaking_speed_score * 0.2
        + clarity_raw * 0.15,
    )

    weak = _weak_patterns(
        filler_stats=filler_stats,
        wpm=wpm,
        pause_count=pause_count,
        hesitation_count=hesitation_count,
        hedging_count=hedging_count,
        word_count=word_count,
        filler_count=filler_count,
    )
    tips = _communication_tips(
        weak_patterns=weak,
        filler_stats=filler_stats,
        wpm=wpm,
        fluency_score=fluency_score,
        confidence_score=confidence_score,
        filler_count=filler_count,
    )

    metrics: dict[str, object] = {
        "transcript_preview": text[:500] if text else "",
        "word_count": word_count,
        "sentence_count": sentence_count,
        "avg_sentence_length": round(avg_sentence_len, 1),
        "hedging_count": hedging_count,
        "filler_rate_per_100_words": (
            round((filler_count / word_count) * 100, 2) if word_count else 0
        ),
        "pause_density": round(pause_count / sentence_count, 2) if sentence_count else 0,
        "hesitation_density": round(hesitation_count / max(word_count, 1), 3),
        "chart_scores": {
            "fluency": fluency_score,
            "communication": communication_score,
            "confidence": confidence_score,
            "speaking_speed": speaking_speed_score,
            "pauses": pause_score,
        },
        "filler_breakdown": [{"word": s.word, "count": s.count} for s in filler_stats],
        "confidence_indicators": confidence_indicators,
    }

    return SpeechAnalysisResult(
        transcript=text,
        word_count=word_count,
        words_per_minute=wpm,
        duration_seconds=duration_seconds,
        filler_word_count=filler_count,
        filler_word_stats=filler_stats,
        pause_count=pause_count,
        hesitation_count=hesitation_count,
        fluency_score=fluency_score,
        communication_score=communication_score,
        confidence_score=confidence_score,
        speaking_speed_score=speaking_speed_score,
        pause_score=pause_score,
        weak_patterns=weak,
        communication_tips=tips,
        confidence_indicators=confidence_indicators,
        metrics=metrics,
    )
