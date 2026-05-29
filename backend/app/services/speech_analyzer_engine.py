"""Run speech analysis and persist results (Phase 12)."""

from __future__ import annotations

from uuid import UUID

from app.core.exceptions import NotFoundError, UnauthorizedError, ValidationAppError
from app.repositories.interview_answer import InterviewAnswerRepository
from app.repositories.interview_question import InterviewQuestionRepository
from app.repositories.interview_session import InterviewSessionRepository
from app.repositories.speech_analysis import SpeechAnalysisRepository
from app.schemas.speech_analyze import (
    FillerWordStat,
    QuestionSpeechAnalysis,
    SessionSpeechSummary,
    SpeechAnalyzeRequest,
    SpeechAnalyzeResponse,
    SpeechAnalyzeSessionRequest,
    SpeechSessionResultsResponse,
)
from app.core.config import get_settings
from app.orchestration import AgentName, get_orchestration_service
from app.speech.analysis_utils import is_phase12_analysis_complete
from app.speech.analyzer import SpeechAnalysisResult, analyze_speech


class SpeechAnalyzerEngineService:
    def __init__(
        self,
        session_repo: InterviewSessionRepository,
        question_repo: InterviewQuestionRepository,
        answer_repo: InterviewAnswerRepository,
        speech_repo: SpeechAnalysisRepository,
    ) -> None:
        self.session_repo = session_repo
        self.question_repo = question_repo
        self.answer_repo = answer_repo
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
        return answer, session

    async def analyze(
        self,
        user_id: UUID,
        payload: SpeechAnalyzeRequest,
    ) -> SpeechAnalyzeResponse:
        answer, session = await self._verify_answer_access(user_id, payload.answer_id)

        transcript = (payload.transcript or answer.answer_text or "").strip()
        if not transcript:
            raise ValidationAppError(
                "No transcript to analyze. Record or type an answer first.",
            )

        duration = payload.duration_seconds
        if duration is None:
            duration = _effective_duration(answer)

        from app.speech.transcript_cleanup import collapse_repeated_phrases

        transcript = collapse_repeated_phrases(transcript)
        result = _run_speech_analysis(transcript, duration_seconds=duration)

        metrics = dict(result.metrics)
        metrics["analysis_version"] = "phase12"
        metrics["weak_patterns"] = result.weak_patterns
        metrics["communication_tips"] = result.communication_tips
        metrics["pause_count"] = result.pause_count
        metrics["hesitation_count"] = result.hesitation_count

        entity_payload = {
            "words_per_minute": result.words_per_minute,
            "filler_word_count": result.filler_word_count,
            "clarity_score": result.communication_score,
            "confidence_score": result.confidence_score,
            "metrics": metrics,
        }

        existing = await self.speech_repo.get_latest_by_answer(answer.id)
        if existing:
            entity = await self.speech_repo.update(existing, entity_payload)
        else:
            entity = await self.speech_repo.create(
                {
                    "answer_id": answer.id,
                    "session_id": session.id,
                    **entity_payload,
                },
            )

        return self._to_response(entity, result)

    async def get_by_answer(self, user_id: UUID, answer_id: UUID) -> SpeechAnalyzeResponse:
        await self._verify_answer_access(user_id, answer_id)
        entity = await self.speech_repo.get_latest_by_answer(answer_id)
        if entity is None or not is_phase12_analysis_complete(entity.metrics):
            raise NotFoundError("SpeechAnalysis", str(answer_id))

        metrics = entity.metrics or {}
        filler_stats = [
            FillerWordStat(**item)
            for item in metrics.get("filler_breakdown", [])
            if isinstance(item, dict)
        ]

        return SpeechAnalyzeResponse(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            answer_id=entity.answer_id,
            session_id=entity.session_id,
            fluency_score=float(metrics.get("chart_scores", {}).get("fluency", 0)),
            communication_score=float(entity.clarity_score or 0),
            confidence_score=float(entity.confidence_score or 0),
            speaking_speed_score=float(metrics.get("chart_scores", {}).get("speaking_speed", 0)),
            pause_score=float(metrics.get("chart_scores", {}).get("pauses", 0)),
            words_per_minute=float(entity.words_per_minute or 0),
            filler_word_count=int(entity.filler_word_count or 0),
            filler_word_stats=filler_stats,
            pause_count=int(metrics.get("pause_count", 0)),
            hesitation_count=int(metrics.get("hesitation_count", 0)),
            weak_patterns=list(metrics.get("weak_patterns", [])),
            communication_tips=list(metrics.get("communication_tips", [])),
            confidence_indicators=dict(metrics.get("confidence_indicators", {})),
            metrics=metrics,
            clarity_score=entity.clarity_score,
        )

    async def analyze_session(
        self,
        user_id: UUID,
        payload: SpeechAnalyzeSessionRequest,
    ) -> SpeechSessionResultsResponse:
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
        for answer in answers:
            prev = latest_by_question.get(answer.question_id)
            if prev is None or answer.updated_at > prev.updated_at:
                latest_by_question[answer.question_id] = answer

        results: list[QuestionSpeechAnalysis] = []
        analyzed = 0
        skipped = 0
        analyses_for_summary: list[SpeechAnalyzeResponse] = []

        for question in questions:
            answer = latest_by_question.get(question.id)
            analysis_response: SpeechAnalyzeResponse | None = None
            preview = ""

            if answer and (answer.answer_text or "").strip():
                preview = (answer.answer_text or "").strip()[:200]
                existing = await self.speech_repo.get_latest_by_answer(answer.id)
                needs_run = payload.force or not is_phase12_analysis_complete(
                    existing.metrics if existing else None,
                )
                if needs_run:
                    analysis_response = await self.analyze(
                        user_id,
                        SpeechAnalyzeRequest(
                            answer_id=answer.id,
                            duration_seconds=_effective_duration(answer),
                        ),
                    )
                    analyzed += 1
                elif existing:
                    analysis_response = await self.get_by_answer(user_id, answer.id)
                    skipped += 1

                if analysis_response:
                    analyses_for_summary.append(analysis_response)
            else:
                skipped += 1

            results.append(
                QuestionSpeechAnalysis(
                    question_id=question.id,
                    question_text=question.question_text,
                    order_index=question.order_index,
                    answer_id=answer.id if answer else None,
                    answer_preview=preview,
                    analysis=analysis_response,
                ),
            )

        summary = _build_session_summary(analyses_for_summary, analyzed, skipped)
        return SpeechSessionResultsResponse(
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
    ) -> SpeechSessionResultsResponse:
        return await self.analyze_session(
            user_id,
            SpeechAnalyzeSessionRequest(session_id=session_id, force=False),
        )

    @staticmethod
    def _to_response(entity, result) -> SpeechAnalyzeResponse:
        metrics = dict(entity.metrics or {})
        metrics["pause_count"] = result.pause_count
        metrics["hesitation_count"] = result.hesitation_count

        return SpeechAnalyzeResponse(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            answer_id=entity.answer_id,
            session_id=entity.session_id,
            fluency_score=result.fluency_score,
            communication_score=result.communication_score,
            confidence_score=result.confidence_score,
            speaking_speed_score=result.speaking_speed_score,
            pause_score=result.pause_score,
            words_per_minute=result.words_per_minute,
            filler_word_count=result.filler_word_count,
            filler_word_stats=[
                FillerWordStat(word=s.word, count=s.count) for s in result.filler_word_stats
            ],
            pause_count=result.pause_count,
            hesitation_count=result.hesitation_count,
            weak_patterns=result.weak_patterns,
            communication_tips=result.communication_tips,
            confidence_indicators=result.confidence_indicators,
            metrics=metrics,
            clarity_score=result.communication_score,
        )


def _effective_duration(answer) -> float | None:
    """Use recording duration only; avoid question-timer values that skew WPM."""
    raw = answer.duration_seconds
    if raw is None or raw <= 0:
        return None
    if raw > 600:
        return None
    return float(raw)


def _build_session_summary(
    analyses: list[SpeechAnalyzeResponse],
    analyzed_count: int,
    skipped_count: int,
) -> SessionSpeechSummary:
    if not analyses:
        return SessionSpeechSummary(
            analyzed_count=analyzed_count,
            skipped_count=skipped_count,
            avg_communication_score=0,
            avg_fluency_score=0,
            avg_confidence_score=0,
            avg_speaking_speed_score=0,
            avg_words_per_minute=0,
            total_filler_words=0,
            highlight_weak_patterns=[],
            highlight_tips=[],
        )

    n = len(analyses)
    weak_seen: list[str] = []
    tips_seen: list[str] = []
    for item in analyses:
        for w in item.weak_patterns:
            if w not in weak_seen:
                weak_seen.append(w)
        for t in item.communication_tips:
            if t not in tips_seen:
                tips_seen.append(t)

    return SessionSpeechSummary(
        analyzed_count=analyzed_count,
        skipped_count=skipped_count,
        avg_communication_score=round(sum(a.communication_score for a in analyses) / n, 1),
        avg_fluency_score=round(sum(a.fluency_score for a in analyses) / n, 1),
        avg_confidence_score=round(sum(a.confidence_score for a in analyses) / n, 1),
        avg_speaking_speed_score=round(sum(a.speaking_speed_score for a in analyses) / n, 1),
        avg_words_per_minute=round(sum(a.words_per_minute for a in analyses) / n, 1),
        total_filler_words=sum(a.filler_word_count for a in analyses),
        highlight_weak_patterns=weak_seen[:5],
        highlight_tips=tips_seen[:5],
    )


def _run_speech_analysis(
    transcript: str,
    *,
    duration_seconds: float | None,
) -> SpeechAnalysisResult:
    settings = get_settings()
    if settings.orchestration_enabled:
        run = get_orchestration_service().run_agent(
            AgentName.SPEECH_ANALYSIS,
            {"transcript": transcript, "duration_seconds": duration_seconds},
        )
        if run.status == "completed":
            return _speech_result_from_output(run.output, transcript, duration_seconds)
    return analyze_speech(transcript, duration_seconds=duration_seconds)


def _speech_result_from_output(
    output: dict,
    transcript: str,
    duration_seconds: float | None,
) -> SpeechAnalysisResult:
    from app.speech.analyzer import FillerStat

    scores = output.get("scores") or {}
    fillers = [
        FillerStat(word=f["word"], count=int(f["count"]))
        for f in output.get("filler_breakdown") or []
    ]
    metrics = dict(output.get("metrics") or {})
    return SpeechAnalysisResult(
        transcript=transcript,
        word_count=int(output.get("word_count") or len(transcript.split())),
        words_per_minute=float(output.get("words_per_minute") or 0),
        duration_seconds=float(output.get("duration_seconds") or duration_seconds or 0),
        filler_word_count=int(output.get("filler_word_count") or 0),
        filler_word_stats=fillers,
        pause_count=int(output.get("pause_count") or 0),
        hesitation_count=int(output.get("hesitation_count") or 0),
        fluency_score=float(scores.get("fluency_score", 0)),
        communication_score=float(scores.get("communication_score", 0)),
        confidence_score=float(scores.get("confidence_score", 0)),
        speaking_speed_score=float(scores.get("speaking_speed_score", 0)),
        pause_score=float(scores.get("pause_score", 0)),
        weak_patterns=list(output.get("weak_patterns") or []),
        communication_tips=list(output.get("communication_tips") or []),
        confidence_indicators=dict(output.get("confidence_indicators") or {}),
        metrics=metrics,
    )
