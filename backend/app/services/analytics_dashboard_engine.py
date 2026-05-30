"""Phase 16 — Analytics dashboard aggregation engine."""

from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime, timedelta
from statistics import mean
from uuid import UUID

from app.analytics.weak_area_detector import (
    AnswerHistoryItem,
    SpeechHistoryItem,
    detect_weak_areas,
)
from app.models.enums import InterviewCategory
from app.repositories.analytics_queries import AnalyticsQueryRepository
from app.repositories.interview_session import InterviewSessionRepository
from app.repositories.roadmap import RoadmapRepository
from app.schemas.analytics_dashboard import (
    AnalyticsDashboardResponse,
    AnalyticsFiltersApplied,
    AnalyticsProgressResponse,
    AnalyticsSummary,
    ImprovementProgressSnapshot,
    InterviewHistoryItem,
    MetricTrendPoint,
    RoleReadinessItem,
    ScoreTrendPoint,
    WeakAreaFrequencyItem,
)
from app.services.weak_area_detection_engine import (
    _build_summary as build_weak_summary,
)
from app.services.weak_area_detection_engine import (
    _map_answer_row,
    _map_speech_row,
    _to_api_item,
)


class AnalyticsDashboardEngineService:
    def __init__(
        self,
        analytics_repo: AnalyticsQueryRepository,
        session_repo: InterviewSessionRepository,
        roadmap_repo: RoadmapRepository,
    ) -> None:
        self.analytics_repo = analytics_repo
        self.session_repo = session_repo
        self.roadmap_repo = roadmap_repo

    async def get_dashboard(
        self,
        user_id: UUID,
        *,
        page: int = 1,
        page_size: int = 10,
        target_role: str | None = None,
        category: str | None = None,
        days: int | None = None,
    ) -> AnalyticsDashboardResponse:
        filters = AnalyticsFiltersApplied(
            target_role=target_role,
            category=category,
            days=days,
        )
        ctx = await self._load_context(user_id, filters)
        weak_items = [_to_api_item(d) for d in ctx["detected"]]
        weak_summary = build_weak_summary(
            interviews=len(ctx["session_ids"]),
            answers=len(ctx["answers"]),
            speeches=len(ctx["speeches"]),
            items=weak_items,
        )

        cat_enum = InterviewCategory(category) if category else None
        history_page = await self.session_repo.list_by_user(
            user_id,
            page=page,
            page_size=page_size,
            target_role=target_role,
            category=cat_enum,
        )
        history_items = [
            _session_to_history(s, ctx["session_metrics"].get(s.id, {}))
            for s in history_page.items
            if _within_days(s.completed_at or s.created_at, days)
        ]

        improvement = _build_improvement_progress(
            ctx["roadmap_milestones"],
            weak_summary.overall_improvement_score,
            weak_items,
        )

        return AnalyticsDashboardResponse(
            generated_at=datetime.now(UTC),
            filters_applied=filters,
            available_roles=ctx["available_roles"],
            available_categories=ctx["available_categories"],
            summary=_build_summary(ctx),
            score_over_time=_score_over_time(ctx),
            communication_trend=_metric_series(ctx, "communication"),
            confidence_trend=_metric_series(ctx, "confidence"),
            technical_trend=_metric_series(ctx, "technical"),
            interview_history=history_items,
            interview_history_total=history_page.total,
            interview_history_page=history_page.page,
            interview_history_page_size=history_page.page_size,
            interview_history_pages=history_page.pages,
            weak_area_frequency=[
                WeakAreaFrequencyItem(
                    kind=i.kind,
                    area_name=i.area_name,
                    frequency=i.frequency,
                    frequency_rate=min(1.0, i.frequency_rate),
                    priority=i.priority,
                )
                for i in weak_items
            ],
            role_readiness=_role_readiness(ctx),
            improvement_progress=improvement,
        )

    async def get_progress(
        self,
        user_id: UUID,
        *,
        target_role: str | None = None,
        category: str | None = None,
        days: int | None = None,
    ) -> AnalyticsProgressResponse:
        filters = AnalyticsFiltersApplied(
            target_role=target_role,
            category=category,
            days=days,
        )
        ctx = await self._load_context(user_id, filters)
        weak_items = [_to_api_item(d) for d in ctx["detected"]]
        weak_summary = build_weak_summary(
            interviews=len(ctx["session_ids"]),
            answers=len(ctx["answers"]),
            speeches=len(ctx["speeches"]),
            items=weak_items,
        )
        improvement = _build_improvement_progress(
            ctx["roadmap_milestones"],
            weak_summary.overall_improvement_score,
            weak_items,
        )

        return AnalyticsProgressResponse(
            generated_at=datetime.now(UTC),
            filters_applied=filters,
            improvement_score_over_time=_bucket_metric(
                ctx["answers"],
                lambda a: a.rubric_score,
                days,
            ),
            correctness_over_time=_bucket_correctness(ctx["answers"], days),
            roadmap_completion_over_time=_roadmap_completion_series(
                ctx["roadmap_snapshots"],
                days,
            ),
            improvement_progress=improvement,
        )

    async def _load_context(
        self,
        user_id: UUID,
        filters: AnalyticsFiltersApplied,
    ) -> dict:
        answer_rows = await self.analytics_repo.list_answer_evaluations_for_user(user_id)
        speech_rows = await self.analytics_repo.list_speech_analyses_for_user(user_id)

        if filters.target_role:
            answer_rows = [r for r in answer_rows if r[3].target_role == filters.target_role]
            speech_rows = [r for r in speech_rows if r[1].target_role == filters.target_role]
        if filters.category:
            answer_rows = [r for r in answer_rows if r[3].category.value == filters.category]
            speech_rows = [r for r in speech_rows if r[1].category.value == filters.category]

        answers: list[AnswerHistoryItem] = []
        for row in answer_rows:
            item = _map_answer_row(row)
            if item is not None and _within_days(item.recorded_at, filters.days):
                answers.append(item)

        speeches = [
            _map_speech_row(row)
            for row in speech_rows
            if _within_days(_map_speech_row(row).recorded_at, filters.days)
        ]

        session_ids = {a.session_id for a in answers} | {s.session_id for s in speeches}
        session_metrics = _aggregate_session_metrics(answers, speeches, answer_rows)
        session_role_map: dict[UUID, str] = {}
        session_category_map: dict[UUID, str] = {}
        for _ev, _ans, _q, session in answer_rows:
            session_role_map[session.id] = session.target_role
            session_category_map[session.id] = session.category.value
        for _speech, session in speech_rows:
            session_role_map.setdefault(session.id, session.target_role)
            session_category_map.setdefault(session.id, session.category.value)

        all_sessions_page = await self.session_repo.list_by_user(user_id, page=1, page_size=500)
        available_roles = sorted({s.target_role for s in all_sessions_page.items if s.target_role})
        available_categories = sorted({s.category.value for s in all_sessions_page.items})

        min_freq = 1 if len(answers) + len(speeches) < 6 else 2
        detected = detect_weak_areas(answers, speeches, min_frequency=min_freq)

        roadmap_page = await self.roadmap_repo.list_by_user(user_id, page=1, page_size=20)
        milestones: list[dict] = []
        roadmap_snapshots: list[tuple[datetime, float]] = []
        for rm in roadmap_page.items:
            if filters.target_role and rm.target_role != filters.target_role:
                continue
            ms = rm.milestones or []
            if rm.status.value == "active" and not milestones:
                milestones = ms
            rate = _roadmap_completion_rate(ms)
            roadmap_snapshots.append((rm.updated_at, rate))

        return {
            "answers": answers,
            "speeches": speeches,
            "session_ids": session_ids,
            "session_metrics": session_metrics,
            "detected": detected,
            "available_roles": available_roles,
            "available_categories": available_categories,
            "roadmap_milestones": milestones,
            "roadmap_snapshots": roadmap_snapshots,
            "session_role_map": session_role_map,
            "session_category_map": session_category_map,
        }


def _within_days(dt: datetime | None, days: int | None) -> bool:
    if days is None or dt is None:
        return days is None
    cutoff = datetime.now(UTC) - timedelta(days=days)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt >= cutoff


def _aggregate_session_metrics(
    answers: list[AnswerHistoryItem],
    speeches: list[SpeechHistoryItem],
    answer_rows: list,
) -> dict[UUID, dict]:
    by_session: dict[UUID, dict] = defaultdict(
        lambda: {
            "scores": [],
            "communication": [],
            "technical": [],
            "confidence": [],
            "correct": 0,
            "total": 0,
        }
    )
    for a in answers:
        m = by_session[a.session_id]
        scores = a.rubric_score if a.rubric_score else 0
        m["scores"].append(scores)
        m["communication"].append(a.communication_score)
        m["technical"].append(a.technical_score)
        m["total"] += 1
        if a.correctness_verdict == "correct":
            m["correct"] += 1
    for s in speeches:
        m = by_session[s.session_id]
        m["confidence"].append(s.confidence_score)
        if not m["communication"]:
            m["communication"].append(s.communication_score)

    # answered count from rows
    session_answered: dict[UUID, int] = defaultdict(int)
    for _ev, _ans, _q, session in answer_rows:
        session_answered[session.id] += 1
    for sid, count in session_answered.items():
        by_session[sid]["answered_count"] = count

    return dict(by_session)


def _session_to_history(session, metrics: dict) -> InterviewHistoryItem:
    scores = metrics.get("scores", [])
    comm = metrics.get("communication", [])
    tech = metrics.get("technical", [])
    conf = metrics.get("confidence", [])
    total = metrics.get("total", 0)
    correct = metrics.get("correct", 0)
    return InterviewHistoryItem(
        session_id=session.id,
        title=session.title,
        target_role=session.target_role,
        category=session.category.value,
        status=session.status.value,
        difficulty=session.difficulty.value,
        completed_at=session.completed_at,
        created_at=session.created_at,
        question_count=session.question_count,
        answered_count=metrics.get("answered_count", total),
        average_score=round(mean(scores), 1) if scores else None,
        communication_score=round(mean(comm), 1) if comm else None,
        confidence_score=round(mean(conf), 1) if conf else None,
        technical_score=round(mean(tech), 1) if tech else None,
        correctness_rate=round(correct / total, 2) if total else None,
    )


def _build_summary(ctx: dict) -> AnalyticsSummary:
    answers: list[AnswerHistoryItem] = ctx["answers"]
    speeches: list[SpeechHistoryItem] = ctx["speeches"]
    if not answers and not speeches:
        return AnalyticsSummary()

    all_scores = [a.rubric_score for a in answers if a.rubric_score is not None]
    comm = [a.communication_score for a in answers] + [s.communication_score for s in speeches]
    conf = [s.confidence_score for s in speeches]
    tech = [a.technical_score for a in answers]

    trend, delta = _compute_trend([a.rubric_score for a in answers], lambda x: x)

    weak_items = [_to_api_item(d) for d in ctx["detected"]]
    weak_summary = build_weak_summary(
        interviews=len(ctx["session_ids"]),
        answers=len(answers),
        speeches=len(speeches),
        items=weak_items,
    )

    completed = sum(1 for sid, m in ctx["session_metrics"].items() if m.get("scores"))

    return AnalyticsSummary(
        total_interviews=len(ctx["session_ids"]),
        completed_interviews=completed,
        total_answers_evaluated=len(answers),
        average_score=round(mean(all_scores), 1) if all_scores else None,
        average_communication=round(mean(comm), 1) if comm else None,
        average_confidence=round(mean(conf), 1) if conf else None,
        average_technical=round(mean(tech), 1) if tech else None,
        improvement_score=weak_summary.overall_improvement_score,
        score_trend=trend,
        score_trend_delta=round(delta, 1),
    )


def _score_over_time(ctx: dict) -> list[ScoreTrendPoint]:
    role_map = ctx["session_role_map"]
    cat_map = ctx["session_category_map"]
    by_session: dict[UUID, list[AnswerHistoryItem]] = defaultdict(list)
    for a in ctx["answers"]:
        by_session[a.session_id].append(a)

    points: list[ScoreTrendPoint] = []
    for session_id, items in sorted(
        by_session.items(),
        key=lambda kv: min(i.recorded_at for i in kv[1]),
    ):
        scores = [i.rubric_score for i in items]
        if not scores:
            continue
        dt = min(i.recorded_at for i in items)
        points.append(
            ScoreTrendPoint(
                label=dt.strftime("%b %d"),
                date=dt,
                session_id=session_id,
                average_score=round(mean(scores), 1),
                target_role=role_map.get(session_id),
                category=cat_map.get(session_id),
            )
        )
    return points[-24:]


def _metric_series(ctx: dict, metric: str) -> list[MetricTrendPoint]:
    answers: list[AnswerHistoryItem] = ctx["answers"]
    speeches: list[SpeechHistoryItem] = ctx["speeches"]

    if metric == "communication":
        entries = sorted(
            [(a.recorded_at, a.communication_score) for a in answers]
            + [(s.recorded_at, s.communication_score) for s in speeches],
            key=lambda x: x[0],
        )
    elif metric == "confidence":
        entries = sorted(
            [(s.recorded_at, s.confidence_score) for s in speeches],
            key=lambda x: x[0],
        )
    else:
        entries = sorted(
            [(a.recorded_at, a.technical_score) for a in answers],
            key=lambda x: x[0],
        )

    return _entries_to_trend_points(entries)[-24:]


def _entries_to_trend_points(
    entries: list[tuple[datetime, float]],
) -> list[MetricTrendPoint]:
    if not entries:
        return []
    # bucket by day
    buckets: dict[str, list[float]] = defaultdict(list)
    dates: dict[str, datetime] = {}
    for dt, val in entries:
        key = dt.strftime("%Y-%m-%d")
        buckets[key].append(val)
        dates[key] = dt
    points: list[MetricTrendPoint] = []
    for key in sorted(buckets.keys()):
        dt = dates[key]
        points.append(
            MetricTrendPoint(
                label=dt.strftime("%b %d"),
                date=dt,
                value=round(mean(buckets[key]), 1),
            )
        )
    return points


def _role_readiness(ctx: dict) -> list[RoleReadinessItem]:
    role_map = ctx["session_role_map"]
    by_role: dict[str, list[float]] = defaultdict(list)
    by_role_sessions: dict[str, set[UUID]] = defaultdict(set)

    for a in ctx["answers"]:
        role = role_map.get(a.session_id) or "General"
        by_role[role].append(a.rubric_score)
        by_role_sessions[role].add(a.session_id)

    items: list[RoleReadinessItem] = []
    for role, scores in by_role.items():
        avg = mean(scores) if scores else 0
        readiness = min(100.0, max(0.0, avg * 0.7 + len(by_role_sessions[role]) * 3))
        trend, _ = _compute_trend(scores, lambda x: x)
        items.append(
            RoleReadinessItem(
                target_role=role,
                readiness_score=round(readiness, 1),
                interviews_completed=len(by_role_sessions[role]),
                average_score=round(avg, 1) if scores else None,
                trend=trend,
            )
        )
    return sorted(items, key=lambda x: x.readiness_score, reverse=True)


def _compute_trend(values: list[float], accessor) -> tuple[str, float]:
    if len(values) < 4:
        return "insufficient_data", 0.0
    mid = len(values) // 2
    older = [accessor(v) for v in values[:mid]]
    recent = [accessor(v) for v in values[mid:]]
    if not older or not recent:
        return "insufficient_data", 0.0
    old_avg = mean(older)
    new_avg = mean(recent)
    delta = new_avg - old_avg
    if abs(delta) < 2:
        return "stable", delta
    return ("improving" if delta > 0 else "declining"), delta


def _build_improvement_progress(
    milestones: list[dict],
    improvement_score: float | None,
    weak_items,
) -> ImprovementProgressSnapshot:
    completed, total = _roadmap_item_counts(milestones)
    rate = (completed / total * 100) if total else 0.0
    return ImprovementProgressSnapshot(
        roadmap_completion_rate=round(rate, 1),
        roadmap_items_completed=completed,
        roadmap_items_total=total,
        weak_areas_high_priority=sum(1 for i in weak_items if i.priority == "high"),
        weak_areas_improving=sum(1 for i in weak_items if i.trend == "improving"),
        weak_areas_declining=sum(1 for i in weak_items if i.trend == "declining"),
        overall_improvement_score=improvement_score,
    )


def _roadmap_item_counts(milestones: list[dict]) -> tuple[int, int]:
    completed = 0
    total = 0
    for phase in milestones:
        for item in phase.get("items", []):
            total += 1
            if item.get("completed"):
                completed += 1
    return completed, total


def _roadmap_completion_rate(milestones: list[dict]) -> float:
    completed, total = _roadmap_item_counts(milestones)
    return (completed / total * 100) if total else 0.0


def _bucket_metric(
    answers: list[AnswerHistoryItem],
    accessor,
    days: int | None,
) -> list[MetricTrendPoint]:
    entries = sorted(
        [(a.recorded_at, accessor(a)) for a in answers],
        key=lambda x: x[0],
    )
    return _entries_to_trend_points(entries)[-24:]


def _bucket_correctness(
    answers: list[AnswerHistoryItem],
    days: int | None,
) -> list[MetricTrendPoint]:
    entries = sorted(
        [
            (
                a.recorded_at,
                100.0
                if a.correctness_verdict == "correct"
                else (50.0 if a.correctness_verdict == "partially_correct" else 0.0),
            )
            for a in answers
        ],
        key=lambda x: x[0],
    )
    return _entries_to_trend_points(entries)[-24:]


def _roadmap_completion_series(
    snapshots: list[tuple[datetime, float]],
    days: int | None,
) -> list[MetricTrendPoint]:
    filtered = [(dt, rate) for dt, rate in snapshots if _within_days(dt, days)]
    filtered.sort(key=lambda x: x[0])
    return [
        MetricTrendPoint(
            label=dt.strftime("%b %d"),
            date=dt,
            value=round(rate, 1),
        )
        for dt, rate in filtered[-24:]
    ]
