"""Phase 15 — AI improvement roadmap generation engine."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from app.analytics.weak_area_detector import (
    AnswerHistoryItem,
    SpeechHistoryItem,
    detect_weak_areas,
)
from app.models.enums import RoadmapStatus
from app.repositories.analytics_queries import AnalyticsQueryRepository
from app.repositories.roadmap import RoadmapRepository
from app.repositories.user import UserRepository
from app.schemas.roadmap_engine import (
    GeneratedRoadmapResponse,
    GenerateRoadmapRequest,
    RoadmapItem,
    RoadmapItemPriority,
    RoadmapPhase,
    RoadmapPhaseKind,
)

# ---------------------------------------------------------------------------
# Per-weakness item templates
# ---------------------------------------------------------------------------

_PHASE_TITLES = {
    "immediate": ("Immediate fixes", "High-impact changes this week", "1 week"),
    "short_term": ("Build the habit", "Consistent improvement over 2–4 weeks", "2–4 weeks"),
    "advanced": ("Master the skill", "Deep refinement and edge-case fluency", "1–3 months"),
}

_ITEM_TEMPLATES: dict[str, list[dict[str, Any]]] = {
    "communication_issues": [
        {
            "phase": "immediate",
            "title": "Answer structure drill",
            "description": (
                "Record 3 practice answers using the format: "
                "one-sentence thesis → context → your approach → outcome. "
                "Listen back and flag any spots where the thread breaks."
            ),
            "estimated_time": "20 min / day × 3 days",
            "practice_recommendation": "Record on voice recorder; transcribe and annotate weak sentences.",
            "resources": ["IntervAI voice recorder", "Speech results page"],
        },
        {
            "phase": "short_term",
            "title": "Clarity score to 75+",
            "description": (
                "Run a full mock interview each week. Target communication score ≥ 75 "
                "on the speech results page. Focus on sentence length and signposting."
            ),
            "estimated_time": "1 mock interview / week",
            "practice_recommendation": "Review the 'Delivery metrics' card after each session.",
            "resources": ["IntervAI interview results", "Speech analysis"],
        },
        {
            "phase": "advanced",
            "title": "Storytelling under pressure",
            "description": (
                "Practice answering cold questions (no prep) in 90 seconds or less. "
                "Aim for zero vague sentences — every claim must have a specific detail."
            ),
            "estimated_time": "2 × 30 min sessions / week",
            "practice_recommendation": "Use a timer; replay and self-grade on clarity.",
            "resources": ["IntervAI mock interviews"],
        },
    ],
    "confidence_problems": [
        {
            "phase": "immediate",
            "title": "Eliminate hedging language",
            "description": (
                "Replace 'I think', 'maybe', 'sort of', 'I guess' with definitive statements. "
                "Rewrite your 3 weakest answers removing every hedge."
            ),
            "estimated_time": "15 min tonight",
            "practice_recommendation": "Use the transcript viewer — highlight every hedge word.",
            "resources": ["IntervAI transcript editor"],
        },
        {
            "phase": "short_term",
            "title": "Own your examples",
            "description": (
                "For every answer, ensure 'I' appears at least 3 times with concrete actions. "
                "Avoid 'we did…' without specifying your personal contribution."
            ),
            "estimated_time": "5 min review per session",
            "practice_recommendation": "Score confidence on the results page — target 70+.",
            "resources": ["IntervAI answer evaluations"],
        },
        {
            "phase": "advanced",
            "title": "Cold-start confidence",
            "description": (
                "Answer questions with zero preparation time. The goal is to deliver a "
                "structured, confident response within 5 seconds of reading the question."
            ),
            "estimated_time": "10 min rapid-fire drills × 3 / week",
            "practice_recommendation": "Record video; note body language and voice projection.",
            "resources": ["IntervAI mock interviews"],
        },
    ],
    "weak_technical_explanations": [
        {
            "phase": "immediate",
            "title": "Review expected answer rubrics",
            "description": (
                "Open each incorrect/partial answer in results. Read the 'Correct answer' "
                "section. Write your own version hitting all expected bullet points."
            ),
            "estimated_time": "30 min",
            "practice_recommendation": "Check rubric match % on each answer evaluation card.",
            "resources": ["IntervAI answer evaluation results"],
        },
        {
            "phase": "short_term",
            "title": "Trade-off templates",
            "description": (
                "For every technical question, practice the pattern: "
                "approach → time/space complexity → alternative → when each fails. "
                "Run 2 technical sessions per week."
            ),
            "estimated_time": "2 sessions / week × 30 min",
            "practice_recommendation": "Target technical score ≥ 70 on answer evaluation.",
            "resources": ["IntervAI technical interviews", "Answer evaluation"],
        },
        {
            "phase": "advanced",
            "title": "System design fluency",
            "description": (
                "Practice end-to-end system design walkthroughs (5–10 min): "
                "requirements → scale estimates → component design → trade-offs → failure modes."
            ),
            "estimated_time": "1 design session / week",
            "practice_recommendation": "Draw on paper; explain aloud; record and review.",
            "resources": ["IntervAI DSA/Technical interviews"],
        },
    ],
    "poor_behavioral_storytelling": [
        {
            "phase": "immediate",
            "title": "Write 5 STAR stories",
            "description": (
                "Prepare 5 go-to STAR stories covering: a challenge, a failure, a conflict, "
                "a success, and a time you influenced stakeholders. Each story needs a metric in Result."
            ),
            "estimated_time": "45 min",
            "practice_recommendation": "Review STAR scores on behavioral interview results.",
            "resources": ["IntervAI behavioral interviews", "STAR feedback card"],
        },
        {
            "phase": "short_term",
            "title": "Hit STAR overall score 70+",
            "description": (
                "Run 1 behavioral interview per week. Review the STAR breakdown. "
                "Focus on whichever of S/T/A/R scored lowest that week."
            ),
            "estimated_time": "1 interview / week + 10 min review",
            "practice_recommendation": "Check 'STAR method analysis' on evaluation results.",
            "resources": ["IntervAI behavioral evaluation"],
        },
        {
            "phase": "advanced",
            "title": "Quantified impact library",
            "description": (
                "Build a personal 'impact library': 10+ work achievements with metrics. "
                "Practice mapping any behavioral question to the best matching story in under 3 seconds."
            ),
            "estimated_time": "1 hr setup + 5 min / week refresh",
            "practice_recommendation": "Keep a note with each story's metrics ready.",
            "resources": ["IntervAI mock interviews"],
        },
    ],
    "dsa_explanation_issues": [
        {
            "phase": "immediate",
            "title": "Always lead with complexity",
            "description": (
                "Before describing your algorithm, state: "
                "'Brute force is O(…), my optimized approach is O(…) time / O(…) space'. "
                "Practice this on your last 3 DSA answers."
            ),
            "estimated_time": "20 min",
            "practice_recommendation": "Check time/space complexity on DSA evaluation cards.",
            "resources": ["IntervAI DSA interview results"],
        },
        {
            "phase": "short_term",
            "title": "Edge-case habit",
            "description": (
                "After each algorithm explanation, explicitly say: "
                "'Edge cases I'd handle: empty input, duplicates, overflow, negative numbers.' "
                "Drill this in every DSA session."
            ),
            "estimated_time": "1 DSA session / week",
            "practice_recommendation": "Target correctness score ≥ 70 on DSA evaluation.",
            "resources": ["IntervAI DSA interviews"],
        },
        {
            "phase": "advanced",
            "title": "Pattern mastery",
            "description": (
                "Practice 20 LeetCode patterns (sliding window, two pointers, BFS, DP, etc.). "
                "For each, practice verbal explanation with complexity + edge cases."
            ),
            "estimated_time": "3 problems / week",
            "practice_recommendation": "Explain aloud as if interviewing; use IntervAI to record.",
            "resources": ["NeetCode patterns", "IntervAI DSA sessions"],
        },
    ],
    "filler_word_overuse": [
        {
            "phase": "immediate",
            "title": "Filler detox — 3 days",
            "description": (
                "Record every voice answer for 3 days. After each, count fillers on "
                "the speech results page. Stop recording when you hit 0–2 fillers per answer."
            ),
            "estimated_time": "10 min / day × 3",
            "practice_recommendation": "Target filler count under 3 on speech results.",
            "resources": ["IntervAI speech analysis"],
        },
        {
            "phase": "short_term",
            "title": "Silent pause practice",
            "description": (
                "Replace every 'um/uh' with a 1-second silent pause. "
                "Record answers and replay — silence sounds confident, fillers sound nervous."
            ),
            "estimated_time": "5 min drill before each session",
            "practice_recommendation": "Monitor filler trend on speech results across sessions.",
            "resources": ["IntervAI speech delivery"],
        },
        {
            "phase": "advanced",
            "title": "Fluency under pressure",
            "description": (
                "Under timed conditions (30 seconds to think, 90 seconds to answer), "
                "target zero fillers and fluency score ≥ 80 consistently."
            ),
            "estimated_time": "5 rapid-fire answers × 2 / week",
            "practice_recommendation": "Compare fluency trend across last 5 sessions.",
            "resources": ["IntervAI speech analysis", "Fluency score trend"],
        },
    ],
    "lack_of_structure": [
        {
            "phase": "immediate",
            "title": "The 4-part template",
            "description": (
                "Memorize: 'Direct answer → Context → Steps I took → Measurable result.' "
                "Apply this template to your 5 most recent incorrect answers."
            ),
            "estimated_time": "30 min",
            "practice_recommendation": "Compare to model answer on evaluation page — hit each bullet.",
            "resources": ["IntervAI answer evaluation", "Correct answer cards"],
        },
        {
            "phase": "short_term",
            "title": "Outline before answering",
            "description": (
                "Spend 10–15 seconds forming a mental outline before each recorded answer. "
                "Signpost out loud: 'First… then… finally…'."
            ),
            "estimated_time": "Applied to every session",
            "practice_recommendation": "Check completeness score — target 65+.",
            "resources": ["IntervAI answer completeness score"],
        },
        {
            "phase": "advanced",
            "title": "Rubric point coverage",
            "description": (
                "Study the expected answer points on the question card before each mock. "
                "After answering, verify every bullet appears in your transcript."
            ),
            "estimated_time": "5 min post-answer review",
            "practice_recommendation": "Target rubric match ≥ 70% on answer evaluation.",
            "resources": ["IntervAI answer rubric scores"],
        },
    ],
}

# General items added for users with no/few weak areas or as closing advanced items
_GENERAL_ADVANCED_ITEMS = [
    {
        "title": "Full mock — simulate real interview conditions",
        "description": (
            "Take a timed interview with all question types. No pausing, no replaying. "
            "Treat it exactly like a real loop. Review results in full afterward."
        ),
        "category": "General",
        "estimated_time": "45–60 min",
        "practice_recommendation": "Do one per week once other weak areas score green.",
        "resources": ["IntervAI full mock interviews"],
    },
    {
        "title": "Role-specific vocabulary",
        "description": (
            "Study the exact terminology used in job descriptions for your target role. "
            "Use these words naturally in answers — interviewers notice domain fluency."
        ),
        "category": "Role Alignment",
        "estimated_time": "20 min research",
        "practice_recommendation": "Compare role-alignment score before and after.",
        "resources": ["Job descriptions", "IntervAI role alignment score"],
    },
]


def _priority_for_weak(area_priority: str) -> RoadmapItemPriority:
    if area_priority == "high":
        return "high"
    if area_priority == "medium":
        return "medium"
    return "low"


def _phase_for_priority(area_priority: str, item_phase: RoadmapPhaseKind) -> RoadmapPhaseKind:
    """High-priority weak areas pull their short-term item up to immediate."""
    if area_priority == "high" and item_phase == "short_term":
        return "immediate"
    return item_phase


def _build_roadmap_phases(
    weak_areas: list[Any],
    target_role: str | None,
) -> tuple[list[RoadmapPhase], list[str]]:
    buckets: dict[RoadmapPhaseKind, list[RoadmapItem]] = {
        "immediate": [],
        "short_term": [],
        "advanced": [],
    }
    addressed: list[str] = []

    for area in weak_areas:
        templates = _ITEM_TEMPLATES.get(area.kind, [])
        if not templates:
            continue
        addressed.append(area.area_name)
        for tmpl in templates:
            raw_phase: RoadmapPhaseKind = tmpl["phase"]
            phase = _phase_for_priority(area.priority, raw_phase)
            item = RoadmapItem(
                id=str(uuid.uuid4()),
                title=tmpl["title"],
                description=tmpl["description"],
                priority=_priority_for_weak(area.priority),
                phase=phase,
                category=area.category,
                estimated_time=tmpl["estimated_time"],
                practice_recommendation=tmpl["practice_recommendation"],
                resources=tmpl.get("resources", []),
                weak_area_kind=area.kind,
            )
            buckets[phase].append(item)

    # Add general advanced items if advanced bucket is thin
    if len(buckets["advanced"]) < 2:
        for i, g in enumerate(_GENERAL_ADVANCED_ITEMS):
            priority: RoadmapItemPriority = "medium" if i == 0 else "low"
            buckets["advanced"].append(
                RoadmapItem(
                    id=str(uuid.uuid4()),
                    title=g["title"],
                    description=g["description"],
                    priority=priority,
                    phase="advanced",
                    category=g["category"],
                    estimated_time=g["estimated_time"],
                    practice_recommendation=g["practice_recommendation"],
                    resources=g.get("resources", []),
                    weak_area_kind=None,
                )
            )

    # Sort each bucket by priority
    _order = {"high": 0, "medium": 1, "low": 2}
    for phase_items in buckets.values():
        phase_items.sort(key=lambda x: _order[x.priority])

    phases: list[RoadmapPhase] = []
    for kind in ("immediate", "short_term", "advanced"):
        phase_kind: RoadmapPhaseKind = kind  # type: ignore[assignment]
        title, subtitle, duration = _PHASE_TITLES[kind]
        items = buckets[phase_kind]
        if not items:
            continue
        phases.append(
            RoadmapPhase(
                phase=phase_kind,
                title=title,
                subtitle=subtitle,
                estimated_duration=duration,
                items=items,
            )
        )

    return phases, addressed


def _build_summary(
    weak_areas: list[Any],
    target_role: str | None,
    phases: list[RoadmapPhase],
) -> str:
    total = sum(len(p.items) for p in phases)
    high_count = sum(1 for wa in weak_areas if wa.priority == "high")
    role_str = f" for {target_role}" if target_role else ""
    if not weak_areas:
        return (
            f"Your personalized roadmap{role_str} is ready. "
            "Complete more mock interviews to unlock targeted weak-area improvements."
        )
    return (
        f"Your AI roadmap{role_str} has {total} improvement tasks across "
        f"{len(phases)} phases, targeting {len(weak_areas)} recurring weak area(s)"
        + (f" including {high_count} high-priority item(s)" if high_count else "")
        + ". Work through Immediate tasks first for the fastest score gains."
    )


class RoadmapEngineService:
    def __init__(
        self,
        roadmap_repo: RoadmapRepository,
        analytics_repo: AnalyticsQueryRepository,
        user_repo: UserRepository,
    ) -> None:
        self.roadmap_repo = roadmap_repo
        self.analytics_repo = analytics_repo
        self.user_repo = user_repo

    async def generate_roadmap(
        self,
        user_id: UUID,
        request: GenerateRoadmapRequest,
    ) -> GeneratedRoadmapResponse:
        # Pull historical data
        answer_rows = await self.analytics_repo.list_answer_evaluations_for_user(user_id)
        speech_rows = await self.analytics_repo.list_speech_analyses_for_user(user_id)

        # Determine target role from request or latest session
        target_role = request.target_role
        if not target_role:
            for row in answer_rows:
                _ev, _ans, _q, session = row
                if session.target_role:
                    target_role = session.target_role
                    break

        # Scope generation to selected role if provided
        if target_role:
            answer_rows = [row for row in answer_rows if row[3].target_role == target_role]
            speech_rows = [row for row in speech_rows if row[1].target_role == target_role]

        answers: list[AnswerHistoryItem] = []
        for row in answer_rows:
            item = _map_answer_row(row)
            if item is not None:
                answers.append(item)
        speeches = [_map_speech_row(row) for row in speech_rows]

        min_freq = 1 if len(answers) + len(speeches) < 6 else 2
        weak_areas = detect_weak_areas(answers, speeches, min_frequency=min_freq)

        phases, addressed = _build_roadmap_phases(weak_areas, target_role)
        summary = _build_summary(weak_areas, target_role, phases)

        title = f"Interview prep roadmap{f' — {target_role}' if target_role else ''}"
        milestones = _phases_to_milestones(phases)

        # Upsert for same role scope only
        if target_role:
            existing_page = await self.roadmap_repo.list_by_user_and_target_role(
                user_id, target_role, page=1, page_size=50
            )
        else:
            existing_page = await self.roadmap_repo.list_by_user(user_id, page=1, page_size=50)
        for old in existing_page.items:
            if old.status == RoadmapStatus.ACTIVE:
                await self.roadmap_repo.update(old, {"status": RoadmapStatus.ARCHIVED})

        entity = await self.roadmap_repo.create({
            "user_id": user_id,
            "title": title,
            "description": summary,
            "status": RoadmapStatus.ACTIVE,
            "target_role": target_role,
            "milestones": milestones,
        })

        return _entity_to_response(entity, phases, summary)

    async def get_latest_roadmap(
        self,
        user_id: UUID,
        target_role: str | None = None,
    ) -> GeneratedRoadmapResponse | None:
        if target_role:
            page = await self.roadmap_repo.list_by_user_and_target_role(
                user_id, target_role, page=1, page_size=1
            )
        else:
            page = await self.roadmap_repo.list_by_user(user_id, page=1, page_size=1)
        if not page.items:
            return None
        entity = page.items[0]
        phases = _milestones_to_phases(entity.milestones or [])
        return _entity_to_response(entity, phases, entity.description or "")

    async def update_item_completion(
        self,
        user_id: UUID,
        roadmap_id: UUID,
        item_id: str,
        completed: bool,
    ) -> GeneratedRoadmapResponse:
        from app.core.exceptions import NotFoundError, UnauthorizedError

        entity = await self.roadmap_repo.get_by_id_or_raise(roadmap_id, resource="Roadmap")
        if entity.user_id != user_id:
            raise UnauthorizedError("You do not have access to this roadmap")

        milestones: list[dict] = list(entity.milestones or [])
        now = datetime.now(UTC).isoformat()
        for phase in milestones:
            for item in phase.get("items", []):
                if item.get("id") == item_id:
                    item["completed"] = completed
                    item["completed_at"] = now if completed else None
        updated = await self.roadmap_repo.update(entity, {"milestones": milestones})
        phases = _milestones_to_phases(updated.milestones or [])
        return _entity_to_response(updated, phases, updated.description or "")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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


def _phases_to_milestones(phases: list[RoadmapPhase]) -> list[dict]:
    return [p.model_dump() for p in phases]


def _milestones_to_phases(milestones: list[dict]) -> list[RoadmapPhase]:
    phases: list[RoadmapPhase] = []
    for m in milestones:
        try:
            phases.append(RoadmapPhase.model_validate(m))
        except Exception:
            continue
    return phases


def _entity_to_response(entity, phases: list[RoadmapPhase], summary: str) -> GeneratedRoadmapResponse:
    total = sum(len(p.items) for p in phases)
    addressed = list({item.weak_area_kind for p in phases for item in p.items if item.weak_area_kind})
    return GeneratedRoadmapResponse(
        id=entity.id,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
        title=entity.title,
        description=entity.description,
        target_role=entity.target_role,
        status=entity.status.value,
        phases=phases,
        summary=summary,
        total_items=total,
        weak_areas_addressed=addressed,
        generated_at=entity.created_at,
    )
