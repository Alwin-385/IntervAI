export type AnalysisStatus = "pending" | "processing" | "completed" | "failed";

export interface AnalysisScores {
  ats_score: number;
  resume_quality_score: number;
  technical_skill_score: number;
  project_strength_score: number;
  communication_score: number;
  role_readiness_score: number;
}

export interface ATSBreakdown {
  keyword_match: number;
  formatting: number;
  section_completeness: number;
  contact_info: number;
}

export interface AnalysisProgress {
  step: string;
  percent: number;
  message?: string | null;
}

export interface StructuredResumeAnalysis {
  version?: string;
  role_target?: string | null;
  scores: AnalysisScores;
  ats_breakdown: ATSBreakdown;
  strengths: string[];
  weaknesses: string[];
  missing_keywords: string[];
  missing_technologies: string[];
  recommendations: string[];
  interview_topics: string[];
  recruiter_feedback: string;
  formatting_issues: string[];
  extracted_skills: string[];
  technologies: string[];
  projects_summary: string[];
  experience_summary: string[];
  skill_radar: Record<string, number>;
  embeddings_indexed?: number;
}

export interface ResumeAnalysisDetail {
  id: string;
  resume_id: string;
  status: AnalysisStatus;
  overall_score: number | null;
  summary: string | null;
  created_at: string;
  updated_at: string;
  progress: AnalysisProgress | null;
  analysis: StructuredResumeAnalysis | null;
  error_message: string | null;
  job_id?: string | null;
}

export interface ResumeAnalyzeRequest {
  target_role?: string | null;
}
