"""Weak-area detection from historical interview + speech + answer analysis."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from app.analytics.weak_area_detector import (
    AnswerHistoryItem,
    SpeechHistoryItem,
    detect_weak_areas,
)
from app.repositories.analytics_queries import AnalyticsQueryRepository
from app.repositories.interview_session import InterviewSessionRepository
from app.repositories.weak_area import WeakAreaRepository
from app.schemas.weak_area import WeakAreaCreate
from app.schemas.weak_area_analytics import (
    DetectedWeakAreaItem,
    WeakAreaProgressSummary,
    WeakAreasAnalyticsResponse,
)


class WeakAreaDetectionEngineService:
    def __init__(
        self,
        analytics_repo: AnalyticsQueryRepository,
        session_repo: InterviewSessionRepository,
        weak_area_repo: WeakAreaRepository,
    ) -> None:
        self.analytics_repo = analytics_repo
        self.session_repo = session_repo
        self.weak_area_repo = weak_area_repo

    async def get_weak_areas_analytics(
        self,
        user_id: UUID,
        *,
        sync_to_profile: bool = True,
    ) -> WeakAreasAnalyticsResponse:
        answer_rows = await self.analytics_repo.list_answer_evaluations_for_user(user_id)
        speech_rows = await self.analytics_repo.list_speech_analyses_for_user(user_id)

        answers = []
        for row in answer_rows:
            item = _map_answer_row(row)
            if item is not None:
                answers.append(item)
        speeches = [_map_speech_row(row) for row in speech_rows]

        min_freq = 1 if len(answers) + len(speeches) < 6 else 2
        detected = detect_weak_areas(answers, speeches, min_frequency=min_freq)

        if sync_to_profile and detected:
            try:
                await self._sync_weak_areas(user_id, detected)
            except Exception:
                pass

        session_ids = {a.session_id for a in answers} | {s.session_id for s in speeches}
        items = [_to_api_item(d) for d in detected]
        summary = _build_summary(
            interviews=len(session_ids),
            answers=len(answers),
            speeches=len(speeches),
            items=items,
        )
        recommendations = _personalized_recommendations(items)
        trend_overview = _trend_overview(answers, speeches)

        return WeakAreasAnalyticsResponse(
            generated_at=datetime.now(UTC),
            weak_areas=items,
            summary=summary,
            personalized_recommendations=recommendations,
            trend_overview=trend_overview,
        )

    async def _sync_weak_areas(self, user_id: UUID, detected) -> None:
        existing_page = await self.weak_area_repo.list_by_user(user_id, page=1, page_size=200)
        by_name = {e.area_name.lower(): e for e in existing_page.items}

        for item in detected:
            desc = (
                item.description
                + "\n\nTop tips:\n- "
                + "\n- ".join(
                    item.improvement_suggestions[:3],
                )
            )
            payload = WeakAreaCreate(
                area_name=item.area_name,
                category=item.category,
                severity=item.severity,
                description=desc[:4000],
            )
            key = item.area_name.lower()
            if key in by_name:
                await self.weak_area_repo.update(
                    by_name[key],
                    {
                        "severity": item.severity,
                        "description": payload.description,
                        "category": item.category,
                    },
                )
            else:
                await self.weak_area_repo.create(
                    {**payload.model_dump(), "user_id": user_id},
                )


def _map_answer_row(row) -> AnswerHistoryItem | None:
    ev, ans, question, session = row
    breakdown = ev.criteria_breakdown or {}
    version = str(breakdown.get("version", ""))
    if not version.startswith("phase13"):
        return None
    scores = breakdown.get("scores") or {}
    star = breakdown.get("star_feedback") or {}
    dsa = breakdown.get("dsa_feedback") or {}
    return AnswerHistoryItem(
        session_id=session.id,
        answer_id=ans.id,
        recorded_at=ev.updated_at,
        interview_category=str(breakdown.get("interview_category", session.category.value)),
        correctness_verdict=str(breakdown.get("correctness_verdict", "incorrect")),
        rubric_score=float(breakdown.get("rubric_score", ev.overall_score)),
        communication_score=float(scores.get("communication_score", 0)),
        technical_score=float(scores.get("technical_score", ev.depth_score or 0)),
        clarity_score=float(scores.get("clarity_score", ev.clarity_score or 0)),
        completeness_score=float(scores.get("completeness_score", 0)),
        technical_accuracy_score=float(scores.get("technical_accuracy_score", 0)),
        star_overall=float(star.get("overall_star_score")) if star else None,
        dsa_optimality=float(dsa.get("optimality_score")) if dsa else None,
        rubric_points_missed=list(breakdown.get("rubric_points_missed") or []),
        weaknesses=list(breakdown.get("weaknesses") or []),
        missing_concepts=list(breakdown.get("missing_concepts") or []),
    )


def _map_speech_row(row) -> SpeechHistoryItem:
    speech, session = row
    metrics = speech.metrics or {}
    chart = metrics.get("chart_scores") or {}
    return SpeechHistoryItem(
        session_id=session.id,
        answer_id=speech.answer_id,
        recorded_at=speech.updated_at,
        communication_score=float(speech.clarity_score or 0),
        confidence_score=float(speech.confidence_score or 0),
        fluency_score=float(chart.get("fluency", 0)),
        filler_word_count=int(speech.filler_word_count or 0),
        words_per_minute=float(speech.words_per_minute or 0),
        weak_patterns=list(metrics.get("weak_patterns") or []),
    )


def _to_api_item(d) -> DetectedWeakAreaItem:
    return DetectedWeakAreaItem(
        kind=d.kind,
        area_name=d.area_name,
        category=d.category,
        priority=d.priority,
        severity=d.severity,
        frequency=d.frequency,
        total_opportunities=d.total_opportunities,
        frequency_rate=min(1.0, d.frequency_rate),
        frequency_label=f"{d.frequency} of {d.total_opportunities} analyzed responses",
        trend=d.trend,
        trend_delta=d.trend_delta,
        description=d.description,
        improvement_suggestions=d.improvement_suggestions,
        practice_recommendations=d.practice_recommendations,
        evidence=d.evidence,
        last_seen_at=d.last_seen_at,
    )


def _build_summary(
    *,
    interviews: int,
    answers: int,
    speeches: int,
    items: list[DetectedWeakAreaItem],
) -> WeakAreaProgressSummary:
    high = sum(1 for i in items if i.priority == "high")
    med = sum(1 for i in items if i.priority == "medium")
    low = sum(1 for i in items if i.priority == "low")
    improving = sum(1 for i in items if i.trend == "improving")
    declining = sum(1 for i in items if i.trend == "declining")
    base = 85.0
    base -= high * 12
    base -= med * 6
    base -= declining * 5
    base += improving * 4
    score = max(0.0, min(100.0, base))
    return WeakAreaProgressSummary(
        interviews_analyzed=interviews,
        answers_analyzed=answers,
        speech_analyses_analyzed=speeches,
        overall_improvement_score=round(score, 1),
        high_priority_count=high,
        medium_priority_count=med,
        low_priority_count=low,
    )


def _personalized_recommendations(items: list[DetectedWeakAreaItem]) -> list[str]:
    if not items:
        return [
            "Complete more mock interviews with voice or text answers to unlock weak-area tracking.",
            "Review answer quality and speech results after each session.",
        ]
    recs: list[str] = []
    for item in items[:3]:
        if item.practice_recommendations:
            recs.append(f"{item.area_name}: {item.practice_recommendations[0]}")
    high = [i for i in items if i.priority == "high"]
    if high:
        recs.insert(
            0,
            f"Focus this week on {high[0].area_name} ({high[0].frequency_label}) — highest impact.",
        )
    return recs[:6]


def _trend_overview(answers: list[AnswerHistoryItem], speeches: list[SpeechHistoryItem]):
    from app.schemas.weak_area_analytics import WeakAreaTrendPoint

    dates = sorted({a.recorded_at for a in answers} | {s.recorded_at for s in speeches})
    if len(dates) < 2:
        return []
    mid = len(dates) // 2
    mid_date = dates[mid]
    recent_ans = [a for a in answers if a.recorded_at >= mid_date]
    older_ans = [a for a in answers if a.recorded_at < mid_date]
    recent_correct = sum(1 for a in recent_ans if a.correctness_verdict == "correct")
    older_correct = sum(1 for a in older_ans if a.correctness_verdict == "correct")

    points = [
        WeakAreaTrendPoint(
            period_label="Earlier",
            hit_count=len(older_ans) - older_correct,
            opportunity_count=max(len(older_ans), 1),
            rate=round((len(older_ans) - older_correct) / max(len(older_ans), 1), 3),
        ),
        WeakAreaTrendPoint(
            period_label="Recent",
            hit_count=len(recent_ans) - recent_correct,
            opportunity_count=max(len(recent_ans), 1),
            rate=round((len(recent_ans) - recent_correct) / max(len(recent_ans), 1), 3),
        ),
    ]
    return points
