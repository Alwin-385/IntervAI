"""Structured AI resume analysis output (validated JSON)."""

from pydantic import Field

from app.schemas.common import SchemaBase


class AnalysisScores(SchemaBase):
    ats_score: float = Field(ge=0, le=100)
    resume_quality_score: float = Field(ge=0, le=100)
    technical_skill_score: float = Field(ge=0, le=100)
    project_strength_score: float = Field(ge=0, le=100)
    communication_score: float = Field(ge=0, le=100)
    role_readiness_score: float = Field(ge=0, le=100)


class ATSBreakdown(SchemaBase):
    keyword_match: float = Field(ge=0, le=100)
    formatting: float = Field(ge=0, le=100)
    section_completeness: float = Field(ge=0, le=100)
    contact_info: float = Field(ge=0, le=100)


class AnalysisProgress(SchemaBase):
    step: str
    percent: int = Field(ge=0, le=100)
    message: str | None = None


class StructuredResumeAnalysis(SchemaBase):
    """Full analyzer payload stored in resume_analyses.raw_analysis."""

    version: str = "1"
    role_target: str | None = None
    scores: AnalysisScores
    ats_breakdown: ATSBreakdown
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    missing_technologies: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    interview_topics: list[str] = Field(default_factory=list)
    recruiter_feedback: str = ""
    formatting_issues: list[str] = Field(default_factory=list)
    extracted_skills: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    projects_summary: list[str] = Field(default_factory=list)
    experience_summary: list[str] = Field(default_factory=list)
    skill_radar: dict[str, float] = Field(default_factory=dict)
    embeddings_indexed: int = 0
    progress: AnalysisProgress | None = None


class ResumeAnalyzeRequest(SchemaBase):
    target_role: str | None = Field(
        default=None,
        max_length=120,
        description="Optional role to evaluate readiness against, e.g. Frontend Developer",
    )


class ResumeAnalysisDetailResponse(SchemaBase):
    """API response with flattened scores for the UI."""

    id: str
    resume_id: str
    status: str
    overall_score: float | None
    summary: str | None
    created_at: str
    updated_at: str
    progress: AnalysisProgress | None = None
    analysis: StructuredResumeAnalysis | None = None
    error_message: str | None = None
    job_id: str | None = None
