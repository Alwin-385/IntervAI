"""SQLAlchemy ORM models — import all models for Alembic metadata discovery."""

from app.core.database import Base
from app.models.answer_evaluation import AnswerEvaluation
from app.models.interview_answer import InterviewAnswer
from app.models.interview_question import InterviewQuestion
from app.models.interview_session import InterviewSession
from app.models.resume import Resume
from app.models.resume_analysis import ResumeAnalysis
from app.models.roadmap import Roadmap
from app.models.speech_analysis import SpeechAnalysis
from app.models.user import User
from app.models.weak_area import WeakArea

__all__ = [
    "Base",
    "User",
    "Resume",
    "ResumeAnalysis",
    "InterviewSession",
    "InterviewQuestion",
    "InterviewAnswer",
    "AnswerEvaluation",
    "SpeechAnalysis",
    "WeakArea",
    "Roadmap",
]
