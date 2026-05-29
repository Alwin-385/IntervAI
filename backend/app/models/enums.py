"""Domain enumerations shared across models and schemas."""

import enum


class UserRole(str, enum.Enum):
    CANDIDATE = "candidate"
    ADMIN = "admin"


class ResumeStatus(str, enum.Enum):
    QUEUED = "queued"
    EXTRACTING_RESUME = "extracting_resume"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalysisStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class InterviewSessionStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class QuestionType(str, enum.Enum):
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    SITUATIONAL = "situational"
    SYSTEM_DESIGN = "system_design"
    OPEN_ENDED = "open_ended"


class RoadmapStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class WeakAreaSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class InterviewCategory(str, enum.Enum):
    HR = "hr"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    DSA = "dsa"
    RESUME_BASED = "resume_based"
    MIXED = "mixed"


class InterviewDifficulty(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class AnswerMode(str, enum.Enum):
    TEXT = "text"
    VOICE = "voice"


class BackgroundJobType(str, enum.Enum):
    RESUME_EXTRACTION = "resume_extraction"
    RESUME_ANALYSIS = "resume_analysis"
    QUESTION_GENERATION = "question_generation"
    TRANSCRIPTION = "transcription"
    ANSWER_EVALUATION = "answer_evaluation"
    ROADMAP_GENERATION = "roadmap_generation"


class BackgroundJobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    RETRYING = "retrying"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
