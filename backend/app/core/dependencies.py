"""FastAPI dependency injection for repositories and services."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.repositories.analytics_queries import AnalyticsQueryRepository
from app.repositories.background_job import BackgroundJobRepository
from app.repositories.answer_evaluation import AnswerEvaluationRepository
from app.repositories.interview_answer import InterviewAnswerRepository
from app.repositories.interview_question import InterviewQuestionRepository
from app.repositories.interview_session import InterviewSessionRepository
from app.repositories.resume import ResumeRepository
from app.repositories.resume_analysis import ResumeAnalysisRepository
from app.repositories.roadmap import RoadmapRepository
from app.repositories.speech_analysis import SpeechAnalysisRepository
from app.repositories.user import UserRepository
from app.repositories.weak_area import WeakAreaRepository
from app.schemas.common import PaginationQuery
from app.services.answer_evaluation import AnswerEvaluationService
from app.services.background_job_dispatch import BackgroundJobDispatcher
from app.services.background_job_service import BackgroundJobService
from app.services.analytics_dashboard_engine import AnalyticsDashboardEngineService
from app.services.answer_evaluator_engine import AnswerEvaluatorEngineService
from app.services.dashboard import DashboardService
from app.services.interview_answer import InterviewAnswerService
from app.services.interview_question import InterviewQuestionService
from app.services.interview_question_generator import InterviewQuestionGeneratorService
from app.services.interview_runtime import InterviewRuntimeService
from app.services.interview_session import InterviewSessionService
from app.services.interview_setup import InterviewSetupService
from app.services.resume import ResumeService
from app.services.resume_analysis import ResumeAnalysisService
from app.services.resume_analysis_orchestrator import ResumeAnalysisOrchestrator
from app.services.resume_extraction_status import ResumeExtractionStatusService
from app.services.resume_upload import ResumeUploadService
from app.services.roadmap import RoadmapService
from app.services.roadmap_engine import RoadmapEngineService
from app.services.speech_analysis import SpeechAnalysisService
from app.services.speech_analyzer_engine import SpeechAnalyzerEngineService
from app.services.speech_transcription import SpeechTranscriptionService
from app.services.user import UserService
from app.services.weak_area import WeakAreaService
from app.services.weak_area_detection_engine import WeakAreaDetectionEngineService


async def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserRepository:
    return UserRepository(session)


async def get_resume_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ResumeRepository:
    return ResumeRepository(session)


async def get_resume_analysis_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ResumeAnalysisRepository:
    return ResumeAnalysisRepository(session)


async def get_interview_session_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> InterviewSessionRepository:
    return InterviewSessionRepository(session)


async def get_interview_question_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> InterviewQuestionRepository:
    return InterviewQuestionRepository(session)


async def get_interview_answer_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> InterviewAnswerRepository:
    return InterviewAnswerRepository(session)


async def get_answer_evaluation_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> AnswerEvaluationRepository:
    return AnswerEvaluationRepository(session)


async def get_speech_analysis_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> SpeechAnalysisRepository:
    return SpeechAnalysisRepository(session)


async def get_weak_area_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> WeakAreaRepository:
    return WeakAreaRepository(session)


async def get_analytics_query_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> AnalyticsQueryRepository:
    return AnalyticsQueryRepository(session)


async def get_roadmap_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> RoadmapRepository:
    return RoadmapRepository(session)


async def get_user_service(
    repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    return UserService(repo)


async def get_resume_service(
    resume_repo: Annotated[ResumeRepository, Depends(get_resume_repository)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> ResumeService:
    return ResumeService(resume_repo, user_repo)


async def get_resume_upload_service(
    resume_repo: Annotated[ResumeRepository, Depends(get_resume_repository)],
) -> ResumeUploadService:
    return ResumeUploadService(resume_repo)


async def get_resume_extraction_status_service(
    resume_repo: Annotated[ResumeRepository, Depends(get_resume_repository)],
) -> ResumeExtractionStatusService:
    return ResumeExtractionStatusService(resume_repo)


async def get_resume_analysis_orchestrator(
    analysis_repo: Annotated[ResumeAnalysisRepository, Depends(get_resume_analysis_repository)],
    resume_repo: Annotated[ResumeRepository, Depends(get_resume_repository)],
) -> ResumeAnalysisOrchestrator:
    return ResumeAnalysisOrchestrator(analysis_repo, resume_repo)


async def get_dashboard_service(
    resume_repo: Annotated[ResumeRepository, Depends(get_resume_repository)],
    session_repo: Annotated[InterviewSessionRepository, Depends(get_interview_session_repository)],
) -> DashboardService:
    return DashboardService(resume_repo, session_repo)


async def get_resume_analysis_service(
    analysis_repo: Annotated[ResumeAnalysisRepository, Depends(get_resume_analysis_repository)],
    resume_repo: Annotated[ResumeRepository, Depends(get_resume_repository)],
) -> ResumeAnalysisService:
    return ResumeAnalysisService(analysis_repo, resume_repo)


async def get_interview_session_service(
    session_repo: Annotated[InterviewSessionRepository, Depends(get_interview_session_repository)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    resume_repo: Annotated[ResumeRepository, Depends(get_resume_repository)],
) -> InterviewSessionService:
    return InterviewSessionService(session_repo, user_repo, resume_repo)


async def get_interview_setup_service(
    session_repo: Annotated[InterviewSessionRepository, Depends(get_interview_session_repository)],
    resume_repo: Annotated[ResumeRepository, Depends(get_resume_repository)],
) -> InterviewSetupService:
    return InterviewSetupService(session_repo, resume_repo)


async def get_interview_question_generator_service(
    session_repo: Annotated[InterviewSessionRepository, Depends(get_interview_session_repository)],
    question_repo: Annotated[
        InterviewQuestionRepository,
        Depends(get_interview_question_repository),
    ],
) -> InterviewQuestionGeneratorService:
    return InterviewQuestionGeneratorService(session_repo, question_repo)


async def get_interview_question_service(
    question_repo: Annotated[
        InterviewQuestionRepository,
        Depends(get_interview_question_repository),
    ],
    session_repo: Annotated[InterviewSessionRepository, Depends(get_interview_session_repository)],
) -> InterviewQuestionService:
    return InterviewQuestionService(question_repo, session_repo)


async def get_interview_answer_service(
    answer_repo: Annotated[InterviewAnswerRepository, Depends(get_interview_answer_repository)],
    question_repo: Annotated[
        InterviewQuestionRepository,
        Depends(get_interview_question_repository),
    ],
) -> InterviewAnswerService:
    return InterviewAnswerService(answer_repo, question_repo)


async def get_interview_runtime_service(
    session_repo: Annotated[InterviewSessionRepository, Depends(get_interview_session_repository)],
    question_repo: Annotated[
        InterviewQuestionRepository,
        Depends(get_interview_question_repository),
    ],
    answer_repo: Annotated[InterviewAnswerRepository, Depends(get_interview_answer_repository)],
) -> InterviewRuntimeService:
    return InterviewRuntimeService(session_repo, question_repo, answer_repo)


async def get_answer_evaluation_service(
    eval_repo: Annotated[AnswerEvaluationRepository, Depends(get_answer_evaluation_repository)],
    answer_repo: Annotated[InterviewAnswerRepository, Depends(get_interview_answer_repository)],
) -> AnswerEvaluationService:
    return AnswerEvaluationService(eval_repo, answer_repo)


async def get_speech_analysis_service(
    repo: Annotated[SpeechAnalysisRepository, Depends(get_speech_analysis_repository)],
) -> SpeechAnalysisService:
    return SpeechAnalysisService(repo)


async def get_speech_transcription_service(
    session_repo: Annotated[InterviewSessionRepository, Depends(get_interview_session_repository)],
    question_repo: Annotated[
        InterviewQuestionRepository,
        Depends(get_interview_question_repository),
    ],
    answer_repo: Annotated[InterviewAnswerRepository, Depends(get_interview_answer_repository)],
    speech_repo: Annotated[SpeechAnalysisRepository, Depends(get_speech_analysis_repository)],
) -> SpeechTranscriptionService:
    return SpeechTranscriptionService(session_repo, question_repo, answer_repo, speech_repo)


async def get_speech_analyzer_engine_service(
    session_repo: Annotated[InterviewSessionRepository, Depends(get_interview_session_repository)],
    question_repo: Annotated[
        InterviewQuestionRepository,
        Depends(get_interview_question_repository),
    ],
    answer_repo: Annotated[InterviewAnswerRepository, Depends(get_interview_answer_repository)],
    speech_repo: Annotated[SpeechAnalysisRepository, Depends(get_speech_analysis_repository)],
) -> SpeechAnalyzerEngineService:
    return SpeechAnalyzerEngineService(session_repo, question_repo, answer_repo, speech_repo)


async def get_answer_evaluator_engine_service(
    session_repo: Annotated[InterviewSessionRepository, Depends(get_interview_session_repository)],
    question_repo: Annotated[
        InterviewQuestionRepository,
        Depends(get_interview_question_repository),
    ],
    answer_repo: Annotated[InterviewAnswerRepository, Depends(get_interview_answer_repository)],
    eval_repo: Annotated[AnswerEvaluationRepository, Depends(get_answer_evaluation_repository)],
    speech_repo: Annotated[SpeechAnalysisRepository, Depends(get_speech_analysis_repository)],
) -> AnswerEvaluatorEngineService:
    return AnswerEvaluatorEngineService(session_repo, question_repo, answer_repo, eval_repo, speech_repo)


async def get_weak_area_service(
    area_repo: Annotated[WeakAreaRepository, Depends(get_weak_area_repository)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> WeakAreaService:
    return WeakAreaService(area_repo, user_repo)


async def get_weak_area_detection_engine_service(
    analytics_repo: Annotated[AnalyticsQueryRepository, Depends(get_analytics_query_repository)],
    session_repo: Annotated[InterviewSessionRepository, Depends(get_interview_session_repository)],
    weak_area_repo: Annotated[WeakAreaRepository, Depends(get_weak_area_repository)],
) -> WeakAreaDetectionEngineService:
    return WeakAreaDetectionEngineService(analytics_repo, session_repo, weak_area_repo)


async def get_background_job_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> BackgroundJobRepository:
    return BackgroundJobRepository(session)


async def get_background_job_service(
    job_repo: Annotated[BackgroundJobRepository, Depends(get_background_job_repository)],
) -> BackgroundJobService:
    return BackgroundJobService(job_repo)


async def get_background_job_dispatcher(
    job_repo: Annotated[BackgroundJobRepository, Depends(get_background_job_repository)],
    job_service: Annotated[BackgroundJobService, Depends(get_background_job_service)],
) -> BackgroundJobDispatcher:
    return BackgroundJobDispatcher(job_service, job_repo)


async def get_analytics_dashboard_engine_service(
    analytics_repo: Annotated[AnalyticsQueryRepository, Depends(get_analytics_query_repository)],
    session_repo: Annotated[InterviewSessionRepository, Depends(get_interview_session_repository)],
    roadmap_repo: Annotated[RoadmapRepository, Depends(get_roadmap_repository)],
) -> AnalyticsDashboardEngineService:
    return AnalyticsDashboardEngineService(analytics_repo, session_repo, roadmap_repo)


async def get_roadmap_service(
    roadmap_repo: Annotated[RoadmapRepository, Depends(get_roadmap_repository)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> RoadmapService:
    return RoadmapService(roadmap_repo, user_repo)


async def get_roadmap_engine_service(
    roadmap_repo: Annotated[RoadmapRepository, Depends(get_roadmap_repository)],
    analytics_repo: Annotated[AnalyticsQueryRepository, Depends(get_analytics_query_repository)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> RoadmapEngineService:
    return RoadmapEngineService(roadmap_repo, analytics_repo, user_repo)


def get_pagination(
    page: int = 1,
    page_size: int = 20,
) -> PaginationQuery:
    return PaginationQuery(page=page, page_size=page_size)
