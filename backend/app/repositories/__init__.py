"""Data access layer."""

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

__all__ = [
    "UserRepository",
    "ResumeRepository",
    "ResumeAnalysisRepository",
    "InterviewSessionRepository",
    "InterviewQuestionRepository",
    "InterviewAnswerRepository",
    "AnswerEvaluationRepository",
    "SpeechAnalysisRepository",
    "WeakAreaRepository",
    "RoadmapRepository",
]
