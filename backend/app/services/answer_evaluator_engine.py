"""Run AI answer evaluation and persist results (Phase 13)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from app.agents.answer_evaluator.graph import run_answer_evaluator
from app.core.config import get_settings
from app.orchestration import AgentName, get_orchestration_service
from app.core.exceptions import NotFoundError, UnauthorizedError, ValidationAppError
from app.models.answer_evaluation import AnswerEvaluation
from app.repositories.answer_evaluation import AnswerEvaluationRepository
from app.repositories.interview_answer import InterviewAnswerRepository
from app.repositories.interview_question import InterviewQuestionRepository
from app.repositories.interview_session import InterviewSessionRepository
from app.repositories.speech_analysis import SpeechAnalysisRepository
from app.schemas.answer_evaluator import (
    AnswerEvaluationContext,
    AnswerEvaluationDetailResponse,
    AnswerScoreBreakdown,
    DsaComplexityFeedback,
    EvaluateAnswerRequest,
    EvaluateSessionRequest,
    QuestionAnswerEvaluation,
    SessionAnswerEvaluationResponse,
    SessionEvaluationSummary,
    SpeechContextSnapshot,
    StarMethodFeedback,
    StructuredAnswerEvaluation,
)
from app.services.interview_question_mapper import to_question_detail
from app.speech.analysis_utils import is_phase12_analysis_complete


def _is_phase13_complete(criteria_breakdown: dict[str, Any] | None) -> bool:
    if not criteria_breakdown:
        return False
    return (
        criteria_breakdown.get("version") == "phase13_v3"
        and criteria_breakdown.get("correctness_verdict") is not None
    )


class AnswerEvaluatorEngineService:
    def __init__(
        self,
        session_repo: InterviewSessionRepository,
        question_repo: InterviewQuestionRepository,
        answer_repo: InterviewAnswerRepository,
        eval_repo: AnswerEvaluationRepository,
        speech_repo: SpeechAnalysisRepository,
    ) -> None:
        self.session_repo = session_repo
        self.question_repo = question_repo
        self.answer_repo = answer_repo
        self.eval_repo = eval_repo
        self.speech_repo = speech_repo

    async def _verify_answer_access(self, user_id: UUID, answer_id: UUID):
        answer = await self.answer_repo.get_by_id(answer_id)
        if answer is None:
            raise NotFoundError("InterviewAnswer", str(answer_id))
        question = await self.question_repo.get_by_id(answer.question_id)
        if question is None:
            raise NotFoundError("InterviewQuestion", str(answer.question_id))
        session = await self.session_repo.get_by_id(question.session_id)
        if session is None:
            raise NotFoundError("InterviewSession", str(question.session_id))
        if session.user_id != user_id:
            raise UnauthorizedError("You do not have access to this answer")
        return answer, question, session

    async def _load_speech_context(self, answer_id: UUID) -> SpeechContextSnapshot | None:
        entity = await self.speech_repo.get_latest_by_answer(answer_id)
        if entity is None or not is_phase12_analysis_complete(entity.metrics):
            return None
        metrics = entity.metrics or {}
        chart = metrics.get("chart_scores") or {}
        return SpeechContextSnapshot(
            communication_score=float(entity.clarity_score or 0),
            confidence_score=float(entity.confidence_score or 0),
            fluency_score=float(chart.get("fluency") or 0),
            words_per_minute=float(entity.words_per_minute or 0),
        )

    async def _build_context(
        self,
        answer,
        question,
        session,
    ) -> AnswerEvaluationContext:
        detail = to_question_detail(question)
        meta = question.question_metadata or {}
        speech = await self._load_speech_context(answer.id)
        return AnswerEvaluationContext(
            answer_id=answer.id,
            question_id=question.id,
            session_id=session.id,
            question_text=question.question_text,
            answer_text=(answer.answer_text or "").strip(),
            target_role=session.target_role or "Software Engineer",
            interview_category=(
                meta.get("category") or session.category.value
            ),
            difficulty=meta.get("difficulty") or session.difficulty.value,
            question_type=question.question_type.value,
            evaluation_criteria=list(detail.evaluation_criteria or meta.get("evaluation_criteria") or []),
            expected_answer_points=list(
                detail.expected_answer_points or meta.get("expected_answer_points") or [],
            ),
            speech_context=speech,
        )

    async def evaluate(
        self,
        user_id: UUID,
        answer_id: UUID,
        *,
        force: bool = False,
    ) -> AnswerEvaluationDetailResponse:
        answer, question, session = await self._verify_answer_access(user_id, answer_id)
        text = (answer.answer_text or "").strip()
        if not text:
            raise ValidationAppError(
                "No answer text to evaluate. Record or type your response first.",
            )

        existing = await self.eval_repo.get_by_answer_id(answer.id)
        if existing and not force and _is_phase13_complete(existing.criteria_breakdown):
            return self._to_detail(existing, question, session)

        ctx = await self._build_context(answer, question, session)
        result = _run_evaluation(ctx)
        preview = text[:200]
        entity = await self._upsert_evaluation(answer.id, result, answer_preview=preview)
        return self._to_detail(entity, question, session)

    async def get_evaluation(
        self,
        user_id: UUID,
        answer_id: UUID,
    ) -> AnswerEvaluationDetailResponse:
        answer, question, session = await self._verify_answer_access(user_id, answer_id)
        entity = await self.eval_repo.get_by_answer_id(answer.id)
        if entity is None or not _is_phase13_complete(entity.criteria_breakdown):
            raise NotFoundError("AnswerEvaluation", str(answer_id))
        return self._to_detail(entity, question, session)

    async def evaluate_session(
        self,
        user_id: UUID,
        payload: EvaluateSessionRequest,
    ) -> SessionAnswerEvaluationResponse:
        session = await self.session_repo.get_by_id_or_raise(
            payload.session_id,
            resource="InterviewSession",
        )
        if session.user_id != user_id:
            raise UnauthorizedError("You do not have access to this interview session")

        questions = await self.question_repo.list_by_session(session.id)
        questions.sort(key=lambda q: q.order_index)
        answers = await self.answer_repo.list_by_session(session.id)
        latest_by_question: dict = {}
        for ans in answers:
            prev = latest_by_question.get(ans.question_id)
            if prev is None or ans.updated_at > prev.updated_at:
                latest_by_question[ans.question_id] = ans

        results: list[QuestionAnswerEvaluation] = []
        evaluated = 0
        skipped = 0
        details: list[AnswerEvaluationDetailResponse] = []

        for question in questions:
            answer = latest_by_question.get(question.id)
            preview = ""
            detail: AnswerEvaluationDetailResponse | None = None

            if answer and (answer.answer_text or "").strip():
                preview = (answer.answer_text or "").strip()[:200]
                existing = await self.eval_repo.get_by_answer_id(answer.id)
                needs_run = payload.force or not _is_phase13_complete(
                    existing.criteria_breakdown if existing else None,
                )
                if needs_run:
                    detail = await self.evaluate(user_id, answer.id, force=payload.force)
                    evaluated += 1
                elif existing:
                    detail = self._to_detail(existing, question, session)
                    skipped += 1
                if detail:
                    details.append(detail)
            else:
                skipped += 1

            results.append(
                QuestionAnswerEvaluation(
                    question_id=question.id,
                    question_text=question.question_text,
                    order_index=question.order_index,
                    answer_id=answer.id if answer else None,
                    answer_preview=preview,
                    evaluation=detail,
                ),
            )

        answered = sum(1 for q in questions if latest_by_question.get(q.id) and (latest_by_question[q.id].answer_text or "").strip())
        summary = _build_session_summary(
            details,
            evaluated,
            skipped,
            total_questions=len(questions),
            answered_count=answered,
        )
        return SessionAnswerEvaluationResponse(
            session_id=session.id,
            session_title=session.title,
            target_role=session.target_role,
            questions=results,
            summary=summary,
        )

    async def get_session_results(
        self,
        user_id: UUID,
        session_id: UUID,
    ) -> SessionAnswerEvaluationResponse:
        return await self.evaluate_session(
            user_id,
            EvaluateSessionRequest(session_id=session_id, force=False),
        )

    async def _upsert_evaluation(
        self,
        answer_id: UUID,
        result: StructuredAnswerEvaluation,
        *,
        answer_preview: str = "",
    ) -> AnswerEvaluation:
        payload = _structured_to_entity_payload(result, answer_preview=answer_preview)
        existing = await self.eval_repo.get_by_answer_id(answer_id)
        if existing:
            return await self.eval_repo.update(existing, payload)
        return await self.eval_repo.create({"answer_id": answer_id, **payload})

    @staticmethod
    def _to_detail(
        entity: AnswerEvaluation,
        question,
        session,
    ) -> AnswerEvaluationDetailResponse:
        breakdown = entity.criteria_breakdown or {}
        scores_raw = breakdown.get("scores") or {}
        scores = AnswerScoreBreakdown(
            overall_score=float(entity.overall_score),
            communication_score=float(
                scores_raw.get("communication_score") or breakdown.get("communication_score") or 0,
            ),
            technical_score=float(
                scores_raw.get("technical_score") or entity.depth_score or 0,
            ),
            completeness_score=float(
                scores_raw.get("completeness_score") or breakdown.get("completeness_score") or 0,
            ),
            confidence_score=float(scores_raw.get("confidence_score") or 0),
            relevance_score=float(entity.relevance_score or scores_raw.get("relevance_score") or 0),
            clarity_score=float(entity.clarity_score or scores_raw.get("clarity_score") or 0),
            technical_accuracy_score=float(scores_raw.get("technical_accuracy_score") or 0),
            professionalism_score=float(scores_raw.get("professionalism_score") or 0),
            role_alignment_score=float(scores_raw.get("role_alignment_score") or 0),
        )

        star = breakdown.get("star_feedback")
        dsa = breakdown.get("dsa_feedback")
        return AnswerEvaluationDetailResponse(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            answer_id=entity.answer_id,
            question_id=question.id,
            session_id=session.id,
            question_text=question.question_text,
            answer_preview=str(breakdown.get("answer_preview") or "")[:200],
            interview_category=breakdown.get("interview_category", session.category.value),
            scores=scores,
            correctness_verdict=breakdown.get("correctness_verdict", "incorrect"),
            is_correct=bool(breakdown.get("is_correct", False)),
            rubric_score=float(breakdown.get("rubric_score", 0)),
            rubric_points_matched=list(breakdown.get("rubric_points_matched") or []),
            rubric_points_missed=list(breakdown.get("rubric_points_missed") or []),
            reference_answer=str(breakdown.get("reference_answer") or ""),
            correct_answer=str(breakdown.get("correct_answer") or ""),
            correctness_explanation=str(breakdown.get("correctness_explanation") or ""),
            summary_feedback=entity.feedback,
            strengths=list(entity.strengths or []),
            weaknesses=list(breakdown.get("weaknesses") or []),
            missing_concepts=list(breakdown.get("missing_concepts") or []),
            improved_answer=breakdown.get("improved_answer") or "",
            improvement_suggestions=list(entity.improvements or []),
            technical_feedback=breakdown.get("technical_feedback"),
            star_feedback=StarMethodFeedback.model_validate(star) if star else None,
            dsa_feedback=DsaComplexityFeedback.model_validate(dsa) if dsa else None,
            criteria_breakdown=breakdown,
        )


def _structured_to_entity_payload(
    result: StructuredAnswerEvaluation,
    *,
    answer_preview: str = "",
) -> dict[str, Any]:
    s = result.scores
    breakdown: dict[str, Any] = result.model_dump()
    breakdown["scores"] = s.model_dump()
    if answer_preview:
        breakdown["answer_preview"] = answer_preview
    return {
        "overall_score": s.overall_score,
        "relevance_score": s.relevance_score,
        "depth_score": s.technical_score,
        "clarity_score": s.clarity_score,
        "feedback": result.summary_feedback,
        "criteria_breakdown": breakdown,
        "strengths": result.strengths,
        "improvements": result.improvement_suggestions,
    }


def _build_session_summary(
    details: list[AnswerEvaluationDetailResponse],
    evaluated_count: int,
    skipped_count: int,
    *,
    total_questions: int,
    answered_count: int,
) -> SessionEvaluationSummary:
    correct = sum(1 for d in details if d.is_correct)
    partial = sum(1 for d in details if d.correctness_verdict == "partially_correct")
    incorrect = sum(1 for d in details if d.correctness_verdict == "incorrect")
    marks_obtained = float(correct) + 0.5 * float(partial)
    denom = answered_count if answered_count > 0 else total_questions
    marks_display = f"{correct}/{denom} correct"

    if not details:
        return SessionEvaluationSummary(
            total_questions=total_questions,
            answered_count=answered_count,
            evaluated_count=evaluated_count,
            skipped_count=skipped_count,
            correct_count=0,
            partially_correct_count=0,
            incorrect_count=0,
            marks_obtained=0,
            marks_display=marks_display,
        )

    n = len(details)
    strengths: list[str] = []
    weaknesses: list[str] = []
    for item in details:
        for s in item.strengths:
            if s not in strengths:
                strengths.append(s)
        for w in item.weaknesses:
            if w not in weaknesses:
                weaknesses.append(w)

    return SessionEvaluationSummary(
        total_questions=total_questions,
        answered_count=answered_count,
        evaluated_count=evaluated_count,
        skipped_count=skipped_count,
        correct_count=correct,
        partially_correct_count=partial,
        incorrect_count=incorrect,
        marks_obtained=round(marks_obtained, 1),
        marks_display=marks_display,
        avg_overall_score=round(sum(d.scores.overall_score for d in details) / n, 1),
        avg_communication_score=round(sum(d.scores.communication_score for d in details) / n, 1),
        avg_technical_score=round(sum(d.scores.technical_score for d in details) / n, 1),
        avg_completeness_score=round(sum(d.scores.completeness_score for d in details) / n, 1),
        avg_confidence_score=round(sum(d.scores.confidence_score for d in details) / n, 1),
        highlight_strengths=strengths[:5],
        highlight_weaknesses=weaknesses[:5],
    )


def _run_evaluation(ctx: AnswerEvaluationContext) -> StructuredAnswerEvaluation:
    settings = get_settings()
    if settings.orchestration_enabled:
        run = get_orchestration_service().run_agent(
            AgentName.INTERVIEW_EVALUATION,
            ctx.model_dump(mode="json"),
        )
        if run.status == "completed":
            return StructuredAnswerEvaluation.model_validate(run.output)
    return run_answer_evaluator(ctx)
