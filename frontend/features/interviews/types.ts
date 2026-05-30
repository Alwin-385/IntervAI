export type InterviewCategory =
  | "hr"
  | "technical"
  | "behavioral"
  | "dsa"
  | "resume_based"
  | "mixed";

export type InterviewDifficulty = "beginner" | "intermediate" | "advanced";

export type AnswerMode = "text" | "voice";

export type InterviewSessionStatus = "scheduled" | "in_progress" | "completed" | "cancelled";

export interface InterviewCreateRequest {
  target_role: string;
  category: InterviewCategory;
  difficulty: InterviewDifficulty;
  answer_mode: AnswerMode;
  question_count: number;
  resume_id?: string | null;
  title?: string | null;
  notes?: string | null;
}

export interface InterviewSetupResponse {
  id: string;
  user_id: string;
  resume_id: string | null;
  title: string;
  target_role: string;
  status: InterviewSessionStatus;
  category: InterviewCategory;
  difficulty: InterviewDifficulty;
  answer_mode: AnswerMode;
  question_count: number;
  notes: string | null;
  scheduled_at: string | null;
  started_at: string | null;
  completed_at: string | null;
  current_question_index: number;
  created_at: string;
  updated_at: string;
}

export interface InterviewWizardState {
  target_role: string;
  category: InterviewCategory | null;
  difficulty: InterviewDifficulty | null;
  question_count: number;
  answer_mode: AnswerMode | null;
  resume_id: string | null;
  custom_role: boolean;
}

export interface InterviewQuestionDetail {
  id: string;
  session_id: string;
  question_text: string;
  question_type: string;
  order_index: number;
  time_limit_seconds: number | null;
  category: InterviewCategory;
  difficulty: InterviewDifficulty;
  expected_answer_points: string[];
  evaluation_criteria: string[];
  source_hint?: string | null;
  created_at: string;
  updated_at: string;
}

export interface GenerateQuestionsResponse {
  session_id: string;
  count: number;
  questions: InterviewQuestionDetail[];
  generation: {
    version: string;
    session_id: string;
    target_role: string;
    session_category: InterviewCategory;
    rag_chunks_used: number;
    weak_areas_targeted: string[];
  };
  job_id?: string | null;
  status?: string;
}

export interface InterviewAnswer {
  id: string;
  question_id: string;
  answer_text: string | null;
  audio_storage_path: string | null;
  duration_seconds: number | null;
  word_count: number | null;
  created_at: string;
  updated_at: string;
}

export interface InterviewProgress {
  total_questions: number;
  answered_count: number;
  current_question_index: number;
  percent_complete: number;
}

export interface QuestionAnswerState {
  question: InterviewQuestionDetail;
  answer: InterviewAnswer | null;
}

export interface InterviewSessionStateResponse {
  session_id: string;
  title: string;
  target_role: string;
  status: InterviewSessionStatus;
  started_at: string | null;
  completed_at: string | null;
  progress: InterviewProgress;
  questions: QuestionAnswerState[];
  seconds_per_question: number;
  total_duration_seconds: number;
  answer_mode: AnswerMode;
}

export interface SubmitAnswerRequest {
  question_id: string;
  answer_text?: string | null;
  audio_storage_path?: string | null;
  duration_seconds?: number | null;
  autosave?: boolean;
  advance?: boolean;
  resume_question_index?: number | null;
}

/** 2 minutes per question for the full-interview timer. */
export const INTERVIEW_SECONDS_PER_QUESTION = 120;

export interface SubmitAnswerResponse {
  answer: InterviewAnswer;
  progress: InterviewProgress;
  saved_at: string;
}

export interface CompleteInterviewResponse {
  session_id: string;
  status: InterviewSessionStatus;
  completed_at: string;
  progress: InterviewProgress;
  total_time_seconds: number | null;
}

export const DEFAULT_WIZARD_STATE: InterviewWizardState = {
  target_role: "",
  category: null,
  difficulty: null,
  question_count: 8,
  answer_mode: null,
  resume_id: null,
  custom_role: false,
};
